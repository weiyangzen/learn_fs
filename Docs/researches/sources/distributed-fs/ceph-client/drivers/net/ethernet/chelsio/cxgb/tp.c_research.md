# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb/tp.c

## Purpose
`tp.c` implements the `cxgb` Terminator Protocol Engine wrapper. It owns a small `struct petp` backpointer to the adapter, programs TP input/output/global configuration, manages TP interrupts for ASIC and optional FPGA builds, toggles IP/TCP checksum offload bits, and resets the TP block.

## Important APIs, Types, And Functions
- `struct petp` stores the owning `adapter_t`.
- `tp_init` programs `A_TP_IN_CONFIG`, `A_TP_OUT_CONFIG`, and `A_TP_GLOBAL_CONFIG`, including checksum validation/generation, offload disable when protocol memory is absent, default TTL, path MTU behavior, five-tuple lookup, SYN cookie parameter, and T2 pause-deadlock drop controls.
- `t1_tp_create`/`t1_tp_destroy` allocate/free TP software state.
- `t1_tp_intr_enable`, `t1_tp_intr_disable`, `t1_tp_intr_clear`, and `t1_tp_intr_handler` manage TP interrupt enables/causes for both ASIC and `CONFIG_CHELSIO_T1_1G` FPGA cases.
- `set_csum_offload`, `t1_tp_set_ip_checksum_offload`, and `t1_tp_set_tcp_checksum_offload` update `A_TP_GLOBAL_CONFIG`.
- `t1_tp_reset` initializes configuration then writes `F_TP_RESET` to `A_TP_RESET`.

## Control Flow And State
`t1_tp_create` is called during `t1_init_sw_modules`, while `t1_tp_reset` is called during `t1_init_hw_modules`. The reset path calls `tp_init` first, then asserts TP reset. Interrupt enable/disable manipulates both TP-local registers and the top-level PL interrupt enable register. ASIC builds intentionally enable the PL TP interrupt while setting `A_TP_INT_ENABLE` to zero because no TP-specific interrupts are used. FPGA builds use FPGA-specific TP interrupt enable/cause addresses.

## State And Persistence Behavior
Software state is limited to the adapter pointer. Hardware state is persistent in TP MMIO registers until reset or reconfiguration. Checksum offload toggles mutate `A_TP_GLOBAL_CONFIG` in place. T2 multi-port boards get TX-drop/deadlock prevention parameters derived from `tp_clk`.

## Dependencies And Integration Points
The file depends on `common.h`, `regs.h`, `tp.h`, and optionally `fpga_defs.h`. It integrates with `subr.c` for TP lifecycle, global interrupt enable/disable/clear, slow interrupt dispatch, and adapter hardware initialization. It also depends on `tp_params` fields such as `pm_size` and `use_5tuple_mode` as defined in the first-generation driver common headers.

## Risks And Edge Cases
ASIC and FPGA interrupt behavior diverges sharply. `t1_tp_intr_handler` clears whatever TP cause is present but returns 0 on ASIC, so callers must not expect detailed cause decoding. Offload disable is derived from protocol memory size; a wrong parameter can disable TOE-related processing. Pause-deadlock avoidance only applies to T2 multi-port ASICs.

## Test Signals
Signals include successful TP reset during probe, expected `A_TP_*` register values after initialization, checksum offload bits toggling from feature changes, slow interrupt handling clearing TP causes, and T2 multi-port tests verifying drop-deadlock programming when pause is enabled.
