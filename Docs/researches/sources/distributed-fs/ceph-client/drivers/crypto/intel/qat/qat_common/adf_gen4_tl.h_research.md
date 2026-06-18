## sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen4_tl.h

Purpose: Defines the Gen4 firmware telemetry memory layout and telemetry constants.

Important APIs/types: Defines conversion constants, maximum aggregation time, history buffer count, max slices per type, max ring pairs, `struct adf_gen4_tl_slice_data_regs`, `struct adf_gen4_tl_device_data_regs`, `struct adf_gen4_tl_ring_pair_data_regs`, `struct adf_gen4_tl_layout`, layout size macros, and message count offset. Declares `adf_gen4_init_tl_data()` under `CONFIG_DEBUG_FS`, otherwise an inline no-op.

Control flow/state: The structs describe shared telemetry state populated by firmware/device code and consumed by debugfs readers. The header itself stores no state.

Dependencies/integration: Integrated with the common telemetry subsystem through `adf_tl_hw_data`.

Risks and test signals: Struct layout changes are ABI-sensitive against firmware. Tests should use static layout/offset assertions where possible and validate telemetry parsing with firmware-produced buffers.
