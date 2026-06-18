# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/cwsr_trap_handler_gfx9.asm

## Purpose

`cwsr_trap_handler_gfx9.asm` is the gfx9-family CWSR trap handler for VegaM, Arcturus, Aldebaran, GC 9.4.3, and GC 9.5.0. It extends the gfx8 model with richer trap routing, XNACK/TCP-store workarounds, ACKs after SQC stores, optional accumulator VGPR save/restore, changed VGPR allocation fields on newer ASICs, alternate VMEM modifiers for GC 9.4.3+, and GC 9.5.0 LDS restore granularity.

The file is responsible for first-level trap triage, second-level debugger dispatch, CWSR save, and restore to the interrupted shader. It persists the full wave context plus ASIC-specific state needed for replay and matrix/accumulator execution.

## Important APIs, Macros, And Register Contracts

Important labels include `L_SAVE`, `L_RESTORE`, `L_FETCH_2ND_TRAP`, `L_SAVE_LDS_LOOP_SQC`, `L_SAVE_VGPR_LOOP_SQC`, `L_SAVE_ACCVGPR_LOOP`, `L_RESTORE_ACCVGPR_LOOP`, `L_RESTORE_HWREG`, and `L_END_PGM`.

Important helpers include `ack_sqc_store_workaround`, `check_if_tcp_store_ok`, `write_4vgprs_to_mem`, `read_4vgprs_from_mem`, `write_vgprs_to_mem_with_sqc`, `get_num_arch_vgprs`, `get_num_acc_vgprs`, `save_and_clear_ib_sts`, `restore_ib_sts`, and `set_status_without_spi_prio`.

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
