# Research Group subset-b-001370

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/cwsr_trap_handler_gfx10.asm -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/cwsr_trap_handler_gfx10.asm

## Purpose

`cwsr_trap_handler_gfx10.asm` is the first-level AMD KFD CWSR trap handler for gfx10/gfx11-era compute waves. It is assembled with `cpp` and `sp3` for Navi1x, Sienna Cichlid, and Plum Bonito families, selected through `ASIC_FAMILY`. Its job is to distinguish ordinary traps/exceptions from save-context requests, delegate non-CWSR events to a second-level debugger trap handler when one exists, and serialize the complete wave context into the SPI-provided save area so the scheduler can preempt and later resume the wave.

The file also implements the inverse restore path, entered through `L_JUMP_TO_RESTORE`, that rebuilds LDS, VGPR, shared VGPR, SGPR, selected HWREGs, trap temporaries, replay state, EXEC/VCC-derived status flags, and PC before returning with `s_rfe_b64` or ending with `s_endpgm_saved`.

## Important APIs, Macros, And Register Contracts

This assembly is not a C API, but it exposes a strict binary contract to KFD, SPI, and the hardware trap ABI:

- Entry labels: `main`, `L_SKIP_RESTORE`, `L_SAVE`, `L_RESTORE`, `L_END_PGM`.
- Trap routing labels: `L_HALTED`, `L_NOT_HALTED`, `L_FETCH_2ND_TRAP`, `L_NO_NEXT_TRAP`, `L_TRAP_CASE`, `L_EXIT_TRAP`.
- State-save labels: `L_SAVE_HWREG`, `L_SAVE_SGPR_LOOP`, `L_SAVE_LDS`, `L_SAVE_VGPR`, `L_SAVE_SHARED_VGPR`.
- State-restore labels: `L_RESTORE_LDS`, `L_RESTORE_VGPR`, `L_RESTORE_SHARED_VGPR`, `L_RESTORE_SGPR`, `L_RESTORE_HWREG`.
- Helper functions/macros: `write_hwreg_to_mem`, `write_16sgpr_to_mem`, `write_12sgpr_to_mem`, `read_*_from_mem`, `get_vgpr_size_bytes`, `get_svgpr_size_bytes`, `get_wave_size2`, `save_and_clear_ib_sts`, `restore_ib_sts`, and the SQC fallback VGPR writers.

The handler depends on the trap temporary ABI: PC in `ttmp0/ttmp1`, original EXEC in `ttmp2/ttmp3`, status/trap fields in `ttmp12/ttmp15`, save-area base address in `exec_lo/exec_hi` after the SPI message, and debug/SPI metadata packed into `ttmp11`. It also consumes hardware registers such as `HW_REG_STATUS`, `HW_REG_TRAPSTS`, `HW_REG_IB_STS`, `HW_REG_IB_STS2`, `HW_REG_GPR_ALLOC`, `HW_REG_LDS_ALLOC`, `HW_REG_MODE`, and flat scratch registers.

## Control Flow

The handler starts by branching over restore. The restore entry is available at `L_JUMP_TO_RESTORE`, while the normal trap entry runs `L_SKIP_RESTORE`. It snapshots `STATUS`, clears `SPI_PRIO` and `ECC_ERR`, reads `TRAPSTS`, and then separates halted and non-halted waves.

For halted waves, a nonzero trap ID goes to the second-level trap path. If no host trap or save-context bit is present, the code sleeps and polls `TRAPSTS` to avoid an interrupt storm caused by instruction-fetch memory violations. For non-halted waves, it checks non-maskable exceptions, maskable exceptions enabled in `MODE.EXCP_EN`, trap IDs, and the single-step workaround before deciding between `L_FETCH_2ND_TRAP` and `L_SAVE`.

`L_FETCH_2ND_TRAP` preserves scalar replay state when XNACK is supported, obtains the second-level TMA either through `MSG_RTN_GET_TMA` or shader TMA registers, sign-extends the pointer, loads debugger metadata plus second-level TBA/TMA from the trap memory area, and jumps if a second-level handler is installed. If none is present, the handler advances past `s_trap` instructions, halts non-trap exceptions to prevent re-entry, rewinds from `S_ENDPGM` hazards, restores `STATUS`, and returns from exception.

`L_SAVE` clears the save-context bit, saves or clears XNACK/IB replay state, sends `MSG_SAVEWAVE` or `MSG_RTN_SAVE_WAVE`, waits for SPI to provide the save address, and then writes the save area in a fixed order: VGPR block, shared VGPR block when present, SGPR block, HWREG block, LDS block, and a TTMP side area. The first four VGPRs are saved early because they are reused as staging registers for SGPR and helper operations. The save path handles wave32 and wave64 sizes separately and, for later ASICs where scalar stores are not available or not safe, routes TTMP/HWREG/SGPR writes through VGPR lane staging and TCP global stores.

`L_RESTORE` reverses the layout. It restores LDS only for the first wave in the thread group, then restores VGPRs with v0-v3 delayed until the end of the VGPR phase, restores shared VGPRs for wave64 shared VGPR allocation, restores SGPRs from high indices down to zero using `s_movreld`, uses a barrier before re-exposing LDS, restores HWREGs, TTMPs, XNACK/IB state, PC, EXEC, mode, and status, and finally returns to the shader. Plum Bonito-specific software-assisted trap behavior can return with PRIV cleared when traps are enabled.

## State And Persistence Behavior

The persisted save area is source-of-truth for preempted wave state. Offsets are computed, not hard-coded globally:

- VGPR state starts at offset 0 and is sized by `GPR_ALLOC.VGPR_SIZE` and wave size.
- Shared VGPR state is appended on gfx10 wave64 paths using `LDS_ALLOC.VGPR_SHARED_SIZE`.
- SGPR state follows VGPR plus shared VGPR state and is fixed to `get_sgpr_size_bytes() == 512`, with `s_sgpr_save_num = 108` restored.
- HWREG state follows SGPR state and occupies 128 bytes.
- LDS follows VGPR plus shared VGPR plus SGPR plus HWREG and is written only by the first wave.
- TTMP spill storage is placed after VGPR/shared VGPR/SGPR with offsets for `ttmp4` through `ttmp11` and `ttmp13`.

The code deliberately avoids restoring volatile bits that may have changed concurrently. It does not blindly rewrite `TRAPSTS.SAVE_CONTEXT` and host-trap state. It restores EXECZ and VCCZ via `s_and_b64 exec, exec, exec` and `s_and_b64 vcc, vcc, vcc`, because those status bits are not directly writable. Replay state is packed into unused bits of `ttmp11` and restored through `IB_STS` for XNACK-capable ASICs.

## Dependencies And Integration Points

This file integrates with:

- KFD CWSR firmware loading and per-ASIC trap handler selection.
- SPI save/restore handshakes through `MSG_SAVEWAVE`, `MSG_RTN_SAVE_WAVE`, and, on supported ASICs, `MSG_RTN_GET_TMA`.
- The debugger second-level trap ABI, where first-level TMA points at second-level TBA/TMA and a debug-trap-enabled flag.
- AMDGPU code that allocates and interprets the save area layout.
- Hardware generation feature gates for XNACK, SQC-store availability, sendmsg return, buffer LDS load, software-assisted traps, and wave32/wave64 support.

## Risks

The highest-risk behavior is layout compatibility. Any change to `get_vgpr_size_bytes`, `get_svgpr_size_bytes`, SGPR count, HWREG size, or TTMP offsets must be mirrored by restore code and by host-side save-area consumers. Trap routing is also delicate: incorrect exception masking can either hide debugger traps or spin in the first-level handler. XNACK and TCP-store workarounds are correctness-critical; choosing the wrong SQC/TCP path after an XNACK error can produce incomplete saves. Wave32/wave64 divergence affects offsets by a factor of two, so tests must cover both. The Plum Bonito `SW_SA_TRAP` path adds barrier and PRIV-return behavior that can regress save-after-trap ordering.

## Test Signals

Useful signals include successful assembly for each advertised `ASIC_FAMILY`, CWSR preemption/resume tests for wave32 and wave64 queues, debugger single-step and host-trap tests, XNACK fault and replay tests, LDS save/restore validation for first-wave and non-first-wave workgroups, shared VGPR context validation on gfx10, and negative tests where no second-level trap handler is installed. Kernel logs, GPU reset counters, KFD queue eviction/resume success, and shader-visible register/LDS checksum tests are the most direct runtime indicators.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/cwsr_trap_handler_gfx10.asm -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/cwsr_trap_handler_gfx12.asm -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/cwsr_trap_handler_gfx12.asm

## Purpose

`cwsr_trap_handler_gfx12.asm` is the gfx12/gfx12.5 CWSR trap handler. It performs the same first-level trap routing, context-save, and context-restore duties as older handlers, but it is adapted to gfx12 register names and semantics: `WAVE_STATE_PRIV`, `WAVE_EXCP_FLAG_PRIV`, `WAVE_TRAP_CTRL`, `WAVE_STATUS`, `WAVE_XNACK_STATE_PRIV`, global `*_addtid` memory operations, optional 57-bit addresses, banked VGPR state, named barriers, cluster barriers, relaxed scheduling mode, and instruction fixup for newer VALU encodings.

The file supports `CHIP_GFX12` and `CHIP_GC_12_0_3`, with multiple feature gates: XNACK, 57-bit addresses, banked VGPRs, wave32-only operation, named barriers, cluster barriers, trap scheduling mode, and instruction fixup.

## Important APIs, Macros, And Register Contracts

Key labels are `L_SAVE`, `L_RESTORE`, `L_FETCH_2ND_TRAP`, `L_SAVE_HWREG`, `L_RESTORE_HWREG`, `L_RESTORE_NAMED_BARRIER_LOOP`, `L_BARRIER_RESTORE_LOOP`, and the instruction-fixup labels under `fixup_instruction`.

Important helper functions are:

- `write_hwreg_to_v2`, `write_16sgpr_to_v2`, `write_12sgpr_to_v2`: stage scalar state through `v2` and then write via global addtid stores.
- `get_vgpr_size_bytes`, `get_sgpr_size_bytes`, `get_hwreg_size_bytes`, `get_wave_size2`: compute save-area sizes from live allocation registers.
- `save_and_clear_xnack_state_priv` and `restore_xnack_state_priv`: preserve `FIRST_REPLAY`, `REPLAY_W64H`, and `FXPTR` in `ttmp11`.
- `wait_trap_barriers`, `restore_barrier_signal_count`, and `restore_sched_mode`: coordinate trap entry/exit with group and cluster barrier state and scheduling mode.
- `fixup_instruction`: decodes instruction length and following `S_SET_VGPR_MSB` patterns so banked VGPR mode can be restored correctly after traps.

The handler treats `exec_lo/exec_hi` as SPI-provided save base address, masks high address bits with `ADDRESS_HI32_MASK`, and preserves selected metadata in `s_save_pc_hi`, including first-wave and banked VGPR mode bits.

## Control Flow

The normal entry saves and sanitizes scheduling and private wave state. On base gfx12, relaxed scheduling mode is saved into `ttmp11` and reset before the trap handler proceeds. It reads `WAVE_STATE_PRIV`, clears system priority and poison error fields that should not be re-applied blindly, reads `WAVE_EXCP_FLAG_PRIV`, and branches according to halted state.

Halted waves go to `L_FETCH_2ND_TRAP` for host traps, to `L_SAVE` for save-context requests, or into a sleep/poll loop for instruction-fetch memory violations. Non-halted waves check non-maskable private exception flags, user exception flags masked by `WAVE_TRAP_CTRL`, trap ID bits, the trap-after-instruction single-step workaround, and then save-context.

`L_FETCH_2ND_TRAP` preserves XNACK state, obtains second-level TMA through `MSG_RTN_GET_TMA`, sign-extends according to the active address width, loads the debug flag and second-level TBA/TMA, and dispatches to the debugger trap handler if available. Without a second-level handler it advances trap PCs, halts non-trap exceptions, optionally runs `fixup_instruction`, restores XNACK and scheduling state, partially restores `WAVE_STATE_PRIV`, and returns from exception.

`L_SAVE` validates that VGPRs are still allocated, clears `SAVE_CONTEXT`, optionally preserves XNACK and fixes banked-VGPR instruction state, handshakes with SPI via `MSG_RTN_SAVE_WAVE`, saves first-wave and bank-selection bits, spills `v0` and TTMPs through global addtid stores, saves VGPRs, HWREGs, SGPRs, LDS, and barrier state. Before writing final HWREG state it calls `wait_trap_barriers` and rereads barrier-complete bits so persisted `STATE_PRIV` reflects the settled trap barrier state.

`L_RESTORE` restores LDS for the first wave, then VGPRs, SGPRs, HWREGs, group/named/cluster barriers, XNACK state, TTMPs, scheduling mode, state-private fields, and returns with `s_rfe_b64`. `L_END_PGM` also waits for trap barriers before `s_endpgm_saved`, preventing a wave from exiting before group or cluster barrier state is saved.

## State And Persistence Behavior

The save layout keeps VGPRs at the front, followed by SGPRs, HWREGs, LDS, and TTMP storage. Compared with gfx10, gfx12 removes the separate shared-VGPR block and uses fixed `get_sgpr_size_bytes() == 512`. `get_hwreg_size_bytes()` is 128 bytes on `CHIP_GFX12` and 512 bytes on `CHIP_GC_12_0_3`, because gfx12.5 stores additional named barrier and scheduler state.

Persisted HWREG fields include PC, EXEC, `WAVE_STATE_PRIV`, `WAVE_EXCP_FLAG_PRIV`, XNACK mask or zero, `WAVE_MODE`, scratch base, user exception flags, trap control, wave status, group barrier state, optional cluster barrier state, and optional scheduling mode. Named barriers are stored at `NAMED_BARRIERS_SR_OFFSET_FROM_HWREG`. For `SAVE_TTMPS_IN_SGPR_BLOCK`, TTMP spill offsets move relative to HWREG storage, so save and restore use `TTMP_SR_OFFSET_FROM_HWREG`.

The code avoids clobbering asynchronous state. It restores `EXCP_FLAG_PRIV` in parts so `SAVE_CONTEXT` and host trap bits are not overwritten. It handles barrier-complete bits specially because they can change after initial trap entry. XNACK replay state is persisted in `ttmp11` fields and hardware `WAVE_XNACK_STATE_PRIV` is cleared while the handler performs memory operations.

## Dependencies And Integration Points

The file depends on gfx12 assembler support for instructions such as `s_sendmsg_rtn_b64`, `s_get_barrier_state`, `s_barrier_signal_isfirst`, `global_store_addtid_b32`, `global_load_addtid_b32`, `s_load_b128`, `s_load_b256`, and `s_load_b512`. It integrates with KFD save-area allocation, SPI save-wave messages, second-level debugger traps, trap barrier protocol, named and cluster barrier hardware, XNACK replay machinery, banked VGPR mode, and host-side code that knows the gfx12 HWREG block layout.

## Risks

This is the most feature-dense handler in the group. Barrier serialization is a major risk: saving or restoring barrier counters too early can corrupt user group or cluster barriers. Address-width masking must match the ASIC, otherwise second-level TMA and save-area pointers can be truncated or incorrectly sign-extended. Instruction fixup is opcode-sensitive; missing a new encoding can restore banked VGPR state incorrectly. `WAVE32_ONLY`, `SAVE_TTMPS_IN_SGPR_BLOCK`, and `get_hwreg_size_bytes()` are tightly coupled to the save-area layout. The relaxed scheduling path assumes the trap handler can temporarily force normal dependency mode and later restore it.

## Test Signals

Test coverage should include assembly for both gfx12 feature sets, CWSR preemption/resume with 48-bit and 57-bit addresses, wave32-only execution, XNACK replay state, banked VGPR instructions near trap boundaries, named barrier and cluster barrier kernels, debugger host traps, single-step/trap-after-instruction, and no-second-level-handler fallback. Runtime signals include successful queue eviction/resume, absence of GPU hangs in barrier-heavy kernels, preserved scratch base and EXEC masks, and shader checksums across VGPR, SGPR, LDS, and barrier-dependent data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/cwsr_trap_handler_gfx12.asm -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/cwsr_trap_handler_gfx8.asm -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/cwsr_trap_handler_gfx8.asm

## Purpose

`cwsr_trap_handler_gfx8.asm` is the older VI/gfx8 CWSR trap handler. It implements a first-level compute shader trap program that either saves a wave for CWSR preemption, restores a previously saved wave, delegates ordinary traps to a next-level handler, or returns directly to the shader when no next-level trap handler is installed.

Compared with newer handlers, this file is simpler and assumes wave64-style save sizing. It still persists the full execution context needed for resume: VGPRs, SGPRs, selected HWREGs, XNACK masks, TBA/TMA, LDS for the first wave, EXEC, PC, STATUS, TRAPSTS, MODE, and M0.

## Important APIs, Macros, And Register Contracts

The externally meaningful labels are `main`, `L_JUMP_TO_RESTORE`, `L_SKIP_RESTORE`, `L_SAVE`, `L_RESTORE`, and `L_END_PGM`. Save and restore sublabels include `L_SAVE_HWREG`, `L_SAVE_SGPR_LOOP`, `L_SAVE_LDS`, `L_SAVE_VGPR`, `L_RESTORE_LDS`, `L_RESTORE_VGPR`, `L_RESTORE_SGPR_LOOP`, and `L_RESTORE_HWREG`.

Helper functions define the storage contract:

- `write_hwreg_to_mem` and `read_hwreg_from_mem` serialize scalar hardware state via scalar buffer memory operations.
- `write_16sgpr_to_mem` and `read_16sgpr_from_mem` move SGPR blocks in 16-register chunks.
- `get_vgpr_size_bytes`, `get_sgpr_size_bytes`, `get_lds_size_bytes`, and `get_hwreg_size_bytes` compute layout offsets from allocation registers.
- `set_status_without_spi_prio` restores status fields while intentionally preserving scheduler-controlled `SPI_PRIO`.

The handler relies on `tma_lo/tma_hi` for the first-level trap memory pointer, `ttmp0/ttmp1` for PC, `ttmp2/ttmp3` for EXEC, `ttmp4/ttmp5` for STATUS/TRAPSTS, `ttmp6/ttmp7` for XNACK masks, and `exec_lo/exec_hi` for SPI-provided save-area state.

## Control Flow

Normal trap entry reads `STATUS`, clears `SPI_PRIO`, reads `TRAPSTS`, and checks `TRAPSTS.SAVECTX`. If set, it immediately enters `L_SAVE`. Otherwise it loads the next-level trap handler from the trap memory area pointed to by TMA. When a second-level TBA is nonzero, it restores status without `SPI_PRIO` and jumps via `s_setpc_b64`.

If there is no next-level handler, the code distinguishes exception versus explicit trap cases. For non-exception `s_trap`, it advances PC by 4 bytes to avoid re-entering the same trap. It masks PC high bits, restores status, and returns with `s_rfe_b64`.

`L_SAVE` clears `SAVECTX`, saves XNACK masks and `IB_STS` replay fields into unused PC high bits, clears replay fields, saves EXEC, sends `MSG_SAVEWAVE`, waits for SPI to write EXEC, constructs a buffer resource from SPI init state including ATC and MTYPE, saves HWREGs, SGPRs, the first four VGPRs, LDS for the first wave, and remaining VGPRs. VGPR save uses `s_set_gpr_idx_on` for indexed VGPR access.

`L_RESTORE` rebuilds the same state in reverse. It restores LDS for the first wave, restores VGPRs with v0-v3 last, restores SGPRs from the end toward zero, restores HWREGs and XNACK masks, reconstructs `IB_STS` replay fields from PC high bits, restores status without `SPI_PRIO`, uses a barrier to make LDS visible to the workgroup, and returns with `s_rfe_restore_b64` so `STATUS.INST_ATC` can be restored.

## State And Persistence Behavior

The save area layout is calculated as VGPR block first, SGPR block second, HWREG block third, and LDS after HWREG. HWREG size is fixed at 128 bytes. SGPR size is computed from `GPR_ALLOC.SGPR_SIZE`; VGPR size is computed as `(VGPR_SIZE + 1) * 4 * 64 * 4`. LDS size uses `LDS_ALLOC.LDS_SIZE` with gfx8 granularity. Only the first wave saves and restores LDS, gated by the SPI first-wave bit in `s_save_exec_hi` or `s_restore_spi_init_hi`.

Persisted HWREGs include M0, PC, EXEC, STATUS, TRAPSTS, XNACK masks, MODE, TBA_LO, and TBA_HI. `TRAPSTS` is restored in pre- and post-SAVECTX parts to avoid overwriting a concurrently raised save-context request. `STATUS.SPI_PRIO` is intentionally not restored by `set_status_without_spi_prio`.

## Dependencies And Integration Points

This handler integrates with the VI assembler profile, KFD CWSR save-area allocation, SPI `MSG_SAVEWAVE`, scalar buffer memory operations, indexed VGPR access through `s_set_gpr_idx_on/off`, LDS load/store paths, and the debugger next-level TBA/TMA ABI. It also depends on host-side consumers understanding the gfx8-specific use of PC high bits for replay count and first-replay state.

## Risks

The code has several comments marking older uncertainties, including SGPR allocation field width and offset overflow. Because gfx8 packs replay information into PC high bits, any PC masking or host-side PC interpretation mismatch can break resume after XNACK/replay. The use of `tma_lo/tma_hi` as temporary storage is called out as a possible conflict. LDS save/restore relies on first-wave detection and a final barrier; mistakes can produce workgroup-local corruption. The handler also uses older indexed VGPR semantics, so instruction scheduling hazards around `m0` and `s_set_gpr_idx_on/off` are sensitive.

## Test Signals

Signals should include successful VI assembly, CWSR preemption/resume of kernels that use high VGPR counts, variable SGPR counts, LDS, XNACK replay, ATC/MTYPE addressing, and debug trap fallback. Shader-side checksum tests over VGPR/SGPR/LDS state, debugger `s_trap` tests with and without next-level handlers, and KFD queue eviction/resume stability are the most useful runtime checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/cwsr_trap_handler_gfx8.asm -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/cwsr_trap_handler_gfx9.asm -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/cwsr_trap_handler_gfx9.asm

## Purpose

`cwsr_trap_handler_gfx9.asm` is the gfx9-family CWSR trap handler for VegaM, Arcturus, Aldebaran, GC 9.4.3, and GC 9.5.0. It extends the gfx8 model with richer trap routing, XNACK/TCP-store workarounds, ACKs after SQC stores, optional accumulator VGPR save/restore, changed VGPR allocation fields on newer ASICs, alternate VMEM modifiers for GC 9.4.3+, and GC 9.5.0 LDS restore granularity.

The file is responsible for first-level trap triage, second-level debugger dispatch, CWSR save, and restore to the interrupted shader. It persists the full wave context plus ASIC-specific state needed for replay and matrix/accumulator execution.

## Important APIs, Macros, And Register Contracts

Important labels include `L_SAVE`, `L_RESTORE`, `L_FETCH_2ND_TRAP`, `L_SAVE_LDS_LOOP_SQC`, `L_SAVE_VGPR_LOOP_SQC`, `L_SAVE_ACCVGPR_LOOP`, `L_RESTORE_ACCVGPR_LOOP`, `L_RESTORE_HWREG`, and `L_END_PGM`.

Important helpers include:

- `ack_sqc_store_workaround`: waits after scalar stores when `ACK_SQC_STORE` is enabled.
- `check_if_tcp_store_ok`: detects the `ALLOW_REPLAY=0` plus `TRAPSTS.XNACK_ERROR` case where TCP stores are unsafe.
- `write_4vgprs_to_mem`, `read_4vgprs_from_mem`, `write_vgprs_to_mem_with_sqc`: vector/scalar save paths for VGPR blocks.
- `get_num_arch_vgprs` and, on Aldebaran and later, `get_num_acc_vgprs`: split architectural VGPRs from accumulator VGPRs.
- `save_and_clear_ib_sts` and `restore_ib_sts`: pack and restore `IB_STS` replay fields through unused bits in `s_save_ib_sts`.
- `set_status_without_spi_prio`: restores status fields while leaving scheduler priority alone.

The handler uses `ttmp0/ttmp1` for PC, `ttmp2/ttmp3` for EXEC, `ttmp12` for STATUS, `ttmp15` for TRAPSTS, `ttmp6/ttmp7` or `ttmp13` for XNACK/IB state depending on ASIC, and `exec_lo/exec_hi` for SPI save base after the save-wave handshake.

## Control Flow

At normal entry the handler reads `STATUS`, clears `SPI_PRIO` and `ECC_ERR`, reads `TRAPSTS`, and branches around halted/non-halted cases. Halted waves can be host traps, save-context requests, or instruction-fetch memory violations that sleep and poll until save-context is raised. Non-halted waves send memory violations, illegal instructions, debugger events, enabled maskable exceptions, trap IDs, and single-step debug cases to `L_FETCH_2ND_TRAP`; save-context requests go to `L_SAVE`.

`L_FETCH_2ND_TRAP` saves and clears scalar XNACK/replay state, reads the second-level trap memory pointer from shader TMA registers, sign-extends the pointer, reads the debug flag plus second-level TBA/TMA, and jumps to the second-level trap handler when installed. Without one, it halts non-trap exceptions, advances trap instructions, restores replay state, restores status without `SPI_PRIO`, and returns.

`L_SAVE` clears save-context, saves replay state, sends `MSG_SAVEWAVE`, waits for SPI to provide the save area, stores TTMPs, builds a buffer resource, saves M0/PC/EXEC/STATUS/TRAPSTS/XNACK/MODE, clears VSKIP after MODE is saved, records first-wave state, saves SGPRs, saves v0-v3, saves LDS with SQC fallback if TCP stores are unsafe, saves remaining architectural VGPRs, and on Arcturus or newer saves accumulator VGPRs. It ends with `s_endpgm_saved`.

`L_RESTORE` restores LDS for the first wave, restores architectural VGPRs 4..N, optionally restores ACC VGPRs, restores v0-v3 last, restores SGPRs, reads HWREG state, restores TRAPSTS in parts, MODE, TTMPs, IB_STS replay state, EXEC/VCC-derived status, and returns through `s_rfe_b64`.

## State And Persistence Behavior

The layout is VGPRs first, with ACC VGPRs included in the VGPR-size calculation for Arcturus and later; SGPRs follow; the HWREG block is 128 bytes; LDS follows the HWREG block. For Aldebaran and later, `GPR_ALLOC.ACCV_OFFSET` gives the architectural VGPR count and `GPR_ALLOC.VGPR_SIZE` contributes the total count used to derive ACC VGPR count. GC 9.5.0 uses larger LDS allocation fields and a 1280-byte restore granularity.

Persisted HWREGs include M0, PC, EXEC, STATUS, TRAPSTS, XNACK masks, and MODE. TTMP state is stored after the SGPR area at offsets for `ttmp4` through `ttmp11` and `ttmp13`. Replay state is packed into `s_save_ib_sts` high bits while the handler clears `IB_STS` for safe scalar memory operations. `TRAPSTS.SAVECTX` is not blindly restored, and `STATUS.SPI_PRIO` is not restored.

## Dependencies And Integration Points

This handler integrates with the gfx9 assembler profiles advertised in the header, KFD save/restore allocation, SPI `MSG_SAVEWAVE`, second-level debugger trap memory, hardware XNACK replay state, scalar and vector memory paths, ACC VGPR instructions (`v_accvgpr_read`/`v_accvgpr_write`), and per-ASIC VMEM cache modifier policy (`slc/glc` versus `sc0/nt`). It also depends on host and debugger code understanding the gfx9 save-area layout, including ACC VGPR expansion on later devices.

## Risks

The handler carries several ASIC-specific hazards. TCP stores after XNACK errors can fail when replay is disabled, so `check_if_tcp_store_ok` and SQC fallback coverage are critical. ACKing SQC stores is a workaround for suspected store ordering under concurrency. ACC VGPR sizing differs across Arcturus and Aldebaran, making save-area size calculations fragile. GC 9.5.0 changes LDS restore granularity and allocation size, so old assumptions can truncate LDS. Clearing `VSKIP` only after saving MODE is important; moving it can alter user shader state. As with gfx8, `TRAPSTS` and `STATUS` partial restoration is necessary to avoid clobbering live trap/save requests or scheduler priority.

## Test Signals

Tests should compile all advertised `ASIC_FAMILY` variants and run CWSR eviction/resume on kernels that use LDS, high VGPR counts, ACC VGPRs, XNACK faults, single-step debugging, host traps, and no-second-level-handler paths. Specific runtime signals include correct ACC VGPR checksums on Arcturus/Aldebaran, successful GC 9.5.0 LDS restore for allocations beyond older field sizes, absence of hangs in XNACK-error scenarios, and preserved MODE/VSKIP and EXEC/VCC-derived status after resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/cwsr_trap_handler_gfx9.asm -->
