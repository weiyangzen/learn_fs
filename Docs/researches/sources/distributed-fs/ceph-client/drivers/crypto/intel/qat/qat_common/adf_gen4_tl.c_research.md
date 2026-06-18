## sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen4_tl.c

Purpose: Supplies Gen4 telemetry layout metadata and debug counter descriptors.

Important APIs/functions: `adf_gen4_init_tl_data()` fills `adf_tl_hw_data` with layout sizes, number of history buffers, max monitored ring pairs, message counter offset, CPP nanoseconds per cycle, bandwidth conversion factor, counter descriptor arrays, and maximum slice count. Counter arrays describe device-level PCIe/latency/bandwidth/DevTLB metrics, slice utilization/execution metrics, and ring-pair metrics.

Control flow and state: No hardware state is read here. The file describes offsets into firmware-populated telemetry shared memory; telemetry collection/debugfs code uses the descriptors later to interpret snapshots.

Dependencies/integration: Depends on `adf_telemetry` and `adf_tl_debugfs` macros and the Gen4 telemetry structs in the header. Compiled only into debugfs/telemetry capable paths through the header guard.

Risks and test signals: Counter offsets must match the packed layout. Tests should verify `layout_sz`, slice/ring-pair sizes, message count offset, descriptor counts, and sample debugfs output from known telemetry buffers.
