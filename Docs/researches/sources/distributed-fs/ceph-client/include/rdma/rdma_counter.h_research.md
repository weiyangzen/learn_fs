# sources/distributed-fs/ceph-client/include/rdma/rdma_counter.h

Purpose: RDMA counter management API for per-port modes, QP-to-counter binding, stats querying, and netlink/restrack exposure.

Important APIs/types/functions: `struct auto_mode_param`, `struct rdma_counter_mode`, `struct rdma_port_counter`, `struct rdma_counter`, `rdma_counter_init`, `rdma_counter_release`, `rdma_counter_set_auto_mode`, `rdma_counter_bind_qp_auto`, `rdma_counter_unbind_qp`, `rdma_counter_query_stats`, `rdma_counter_get_hwstat_value`, QPN bind/unbind/alloc helpers, `rdma_counter_get_mode`, and `rdma_counter_modify`.

Control flow: Device init creates per-port counter state. Netlink/admin changes configure auto mode or explicit bindings. QP lifecycle binds/unbinds counters automatically or by QPN. Query/update paths refresh hardware stats through provider callbacks.

State and persistence behavior: Runtime-only per-device, per-port, and per-counter state. `kref` protects counter lifetime, mutexes serialize mode/stats changes, and restrack entries expose objects.

Dependencies and integration points: Depends on mutexes, PID namespace types, RDMA restrack, RDMA netlink enums, `ib_device`, `ib_qp`, and counter callbacks in `ib_device_ops`.

Risks: Binding consistency across QP destroy, counter dealloc, and mode changes is critical. Lock/kref mistakes can race stats queries with unbind/release. Hardware support for modes/masks is provider-specific.

Test signals: Init/release, auto mode set/get, auto bind by QP type, explicit QPN bind/unbind, allocated counter IDs, concurrent query/unbind, enable/disable modify, unsupported callbacks, and netlink dumps.
