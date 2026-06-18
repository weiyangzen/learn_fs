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

This file integrates with KFD CWSR firmware loading and per-ASIC trap handler selection, SPI save/restore handshakes through `MSG_SAVEWAVE`, `MSG_RTN_SAVE_WAVE`, and, on supported ASICs, `MSG_RTN_GET_TMA`, the debugger second-level trap ABI, AMDGPU code that allocates and interprets the save area layout, and hardware generation feature gates for XNACK, SQC-store availability, sendmsg return, buffer LDS load, software-assisted traps, and wave32/wave64 support.

## Risks

The highest-risk behavior is layout compatibility. Any change to `get_vgpr_size_bytes`, `get_svgpr_size_bytes`, SGPR count, HWREG size, or TTMP offsets must be mirrored by restore code and by host-side save-area consumers. Trap routing is also delicate: incorrect exception masking can either hide debugger traps or spin in the first-level handler. XNACK and TCP-store workarounds are correctness-critical; choosing the wrong SQC/TCP path after an XNACK error can produce incomplete saves. Wave32/wave64 divergence affects offsets by a factor of two, so tests must cover both. The Plum Bonito `SW_SA_TRAP` path adds barrier and PRIV-return behavior that can regress save-after-trap ordering.

## Test Signals

Useful signals include successful assembly for each advertised `ASIC_FAMILY`, CWSR preemption/resume tests for wave32 and wave64 queues, debugger single-step and host-trap tests, XNACK fault and replay tests, LDS save/restore validation for first-wave and non-first-wave workgroups, shared VGPR context validation on gfx10, and negative tests where no second-level trap handler is installed. Kernel logs, GPU reset counters, KFD queue eviction/resume success, and shader-visible register/LDS checksum tests are the most direct runtime indicators.
