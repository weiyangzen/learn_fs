# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen6_tl.h

Purpose: defines the Gen6 telemetry DMA layout, maximum telemetry resource counts, hardware unit conversion constants, and the public initializer for Gen6 telemetry metadata.

Important types and macros: `adf_gen6_tl_slice_data_regs`, `adf_gen6_tl_cmdq_data_regs`, `adf_gen6_tl_device_data_regs`, `adf_gen6_tl_ring_pair_data_regs`, and `adf_gen6_tl_layout` mirror firmware-written memory. Macros define layout sizes, message-count offset, max slices/cmdqs, max ring-pairs, history buffer count, and conversion constants.

Control flow and state: no executable state. The layout structs define how common telemetry reads coherent DMA memory and how debugfs offsets are calculated.

Dependencies and integration: depends on Linux types and, under `CONFIG_DEBUG_FS`, declares `adf_gen6_init_tl_data`. Shared offset macros in `adf_tl_debugfs.h` reference these struct names.

Risks and test signals: structure packing/alignment and field order must match firmware exactly. Tests should validate `sizeof`-driven layout against firmware ABI, successful telemetry admin start, monotonic `reg_tl_msg_cnt`, and plausible values for device, slice, cmdq, and ring-pair counters.
