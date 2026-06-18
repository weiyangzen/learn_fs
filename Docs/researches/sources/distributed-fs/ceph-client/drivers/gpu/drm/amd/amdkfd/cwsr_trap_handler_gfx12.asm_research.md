# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/cwsr_trap_handler_gfx12.asm

## Purpose

`cwsr_trap_handler_gfx12.asm` is the gfx12/gfx12.5 CWSR trap handler. It performs the same first-level trap routing, context-save, and context-restore duties as older handlers, but it is adapted to gfx12 register names and semantics: `WAVE_STATE_PRIV`, `WAVE_EXCP_FLAG_PRIV`, `WAVE_TRAP_CTRL`, `WAVE_STATUS`, `WAVE_XNACK_STATE_PRIV`, global `*_addtid` memory operations, optional 57-bit addresses, banked VGPR state, named barriers, cluster barriers, relaxed scheduling mode, and instruction fixup for newer VALU encodings.

The file supports `CHIP_GFX12` and `CHIP_GC_12_0_3`, with multiple feature gates: XNACK, 57-bit addresses, banked VGPRs, wave32-only operation, named barriers, cluster barriers, trap scheduling mode, and instruction fixup.

## Important APIs, Macros, And Register Contracts

Key labels are `L_SAVE`, `L_RESTORE`, `L_FETCH_2ND_TRAP`, `L_SAVE_HWREG`, `L_RESTORE_HWREG`, `L_RESTORE_NAMED_BARRIER_LOOP`, `L_BARRIER_RESTORE_LOOP`, and the instruction-fixup labels under `fixup_instruction`.

Important helper functions are `write_hwreg_to_v2`, `write_16sgpr_to_v2`, `write_12sgpr_to_v2`, `get_vgpr_size_bytes`, `get_sgpr_size_bytes`, `get_hwreg_size_bytes`, `get_wave_size2`, `save_and_clear_xnack_state_priv`, `restore_xnack_state_priv`, `wait_trap_barriers`, `restore_barrier_signal_count`, `restore_sched_mode`, and `fixup_instruction`.

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
