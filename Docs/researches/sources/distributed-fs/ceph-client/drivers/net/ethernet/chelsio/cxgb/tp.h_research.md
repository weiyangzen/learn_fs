# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb/tp.h

## Purpose
`tp.h` is the public interface for the first-generation Chelsio Terminator Protocol Engine. It defines TP MIB statistic layout, a receive coalescing maximum, opaque TP state, and the lifecycle/control APIs implemented by `tp.c`.

## Important APIs, Types, And Functions
- `TP_MAX_RX_COALESCING_SIZE` sets a 16224-byte TP receive coalescing limit.
- `struct tp_mib_statistics` mirrors hardware IP and TCP MIB counters, with high/low pairs for wide counters and scalar TCP state/timer counters.
- `struct petp` and `struct tp_params` are forward declarations.
- Public functions are `t1_tp_create`, `t1_tp_destroy`, `t1_tp_intr_disable`, `t1_tp_intr_enable`, `t1_tp_intr_clear`, `t1_tp_intr_handler`, `t1_tp_set_tcp_checksum_offload`, `t1_tp_set_ip_checksum_offload`, and `t1_tp_reset`.

## Control Flow And State
This header exposes no implementation, but its APIs describe TP control flow: allocate TP state, reset/program the hardware block, enable/clear/handle/disable TP interrupts as adapter state changes, toggle checksum offload bits, and destroy state on removal or failed initialization.

## Dependencies And Integration Points
The header includes `common.h` for `adapter_t`, `u32`, and TP parameter definitions. It is consumed by adapter initialization and interrupt code in `subr.c`, by TP implementation in `tp.c`, and by any diagnostics collecting TP MIB statistics.

## Risks And Edge Cases
The MIB structure must match hardware register layout exactly; reordering or type changes would corrupt stats reads. The API is opaque around locking and register access, so callers must rely on implementation-side synchronization. The coalescing limit is a hardware constraint and should not be raised without validating descriptor/data-path limits.

## Test Signals
Build tests should catch prototype drift between `tp.h` and `tp.c`. Runtime signals include stable TP initialization, checksum offload feature toggles, interrupt handling during slow interrupt tests, and correctly decoded IP/TCP MIB counters under traffic.
