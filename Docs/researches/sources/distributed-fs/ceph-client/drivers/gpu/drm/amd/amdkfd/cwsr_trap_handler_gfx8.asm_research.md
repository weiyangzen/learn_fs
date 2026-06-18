# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/cwsr_trap_handler_gfx8.asm

## Purpose

`cwsr_trap_handler_gfx8.asm` is the older VI/gfx8 CWSR trap handler. It implements a first-level compute shader trap program that either saves a wave for CWSR preemption, restores a previously saved wave, delegates ordinary traps to a next-level handler, or returns directly to the shader when no next-level trap handler is installed.

Compared with newer handlers, this file is simpler and assumes wave64-style save sizing. It still persists the full execution context needed for resume: VGPRs, SGPRs, selected HWREGs, XNACK masks, TBA/TMA, LDS for the first wave, EXEC, PC, STATUS, TRAPSTS, MODE, and M0.

## Important APIs, Macros, And Register Contracts

The externally meaningful labels are `main`, `L_JUMP_TO_RESTORE`, `L_SKIP_RESTORE`, `L_SAVE`, `L_RESTORE`, and `L_END_PGM`. Save and restore sublabels include `L_SAVE_HWREG`, `L_SAVE_SGPR_LOOP`, `L_SAVE_LDS`, `L_SAVE_VGPR`, `L_RESTORE_LDS`, `L_RESTORE_VGPR`, `L_RESTORE_SGPR_LOOP`, and `L_RESTORE_HWREG`.

Helper functions define the storage contract: `write_hwreg_to_mem`, `read_hwreg_from_mem`, `write_16sgpr_to_mem`, `read_16sgpr_from_mem`, `get_vgpr_size_bytes`, `get_sgpr_size_bytes`, `get_lds_size_bytes`, `get_hwreg_size_bytes`, and `set_status_without_spi_prio`.

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
