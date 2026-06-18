# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_trace.h

Purpose: defines the ice driver's tracepoint namespace and trace events for RX/TX datapath, DIM tuning, TX timestamps, eswitch bridge events, and switch rule statistics. It lets production kernels observe fast-path and eswitch behavior with ftrace/perf without adding ad hoc logging.

Important APIs and types: `TRACE_SYSTEM ice` establishes the subsystem. `ice_trace(name, args...)` and `ice_trace_enabled(name)` wrap `trace_ice_*` symbols so driver code can call tracepoints through a common macro. Event classes include `ice_rx_dim_template`, `ice_tx_dim_template`, `ice_tx_template`, `ice_rx_template`, `ice_rx_indicate_template`, `ice_xmit_template`, `ice_tx_tstamp_template`, `ice_esw_br_fdb_template`, `ice_esw_br_vlan_template`, `ice_esw_br_port_template`, and `ice_switch_stats_template`.

Control flow role: this file is included by C files that emit trace events, especially `ice_txrx.c` for `clean_tx_irq`, `clean_rx_irq`, `xmit_frame_ring`, and timestamp request/completion points. Each `DECLARE_EVENT_CLASS` defines the recorded fields and `TP_printk` format, and `DEFINE_EVENT` creates concrete tracepoints.

State and persistence: tracepoints do not own persistent driver state. They snapshot pointers, queue indices, netdev names, DIM fields, bridge FDB/VLAN data, switch recipe/rule counts, and timestamp indices at event time. Runtime enablement is controlled by the kernel tracing subsystem.

Dependencies and integration: depends on Linux `tracepoint.h`, `trace/define_trace.h`, ice ring types, DIM structures, and eswitch bridge types from `ice_eswitch_br.h`. The `TRACE_INCLUDE_FILE` override points back to the driver-local header path because this is built as a module rather than under the global trace include tree.

Risks: tracepoint field expressions dereference ring/netdev and eswitch bridge objects, so callers must only emit events while those objects are live. Format or field changes affect scripts consuming trace output. Pointer-valued fields are useful for correlation but not stable identifiers across lifetimes.

Test signals: build with tracing enabled, confirm generated `trace_ice_*` symbols, enable events under `/sys/kernel/tracing/events/ice/`, run TX/RX, DIM, timestamp, and eswitch bridge scenarios, and verify trace output includes expected netdev names, queue indices, bridge data, and switch rule counts.
