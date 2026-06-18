<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/misc/xilinx_sdfec.h -->
# sources/distributed-fs/ceph-client/include/uapi/misc/xilinx_sdfec.h

## Purpose
Defines the userspace ABI for the Xilinx Soft Decision FEC misc device. It exposes LDPC table address bounds, Turbo/LDPC configuration structures, runtime status and error counters, and the ioctl command set used to start, stop, configure, query, and reset the SD-FEC core.

## Important APIs, Types, and Functions
Read coverage: 448 lines and 12341 bytes. Visible type families include enum xsdfec_code, enum xsdfec_order, enum xsdfec_turbo_alg, enum xsdfec_state, enum xsdfec_axis_width, enum xsdfec_axis_word_include, struct xsdfec_turbo, struct xsdfec_ldpc_params, struct xsdfec_status, struct xsdfec_irq, struct xsdfec_config, struct xsdfec_stats, struct xsdfec_ldpc_param_table_sizes. Important macros/constants include __XILINX_SDFEC_H__, XSDFEC_LDPC_SC_TABLE_ADDR_BASE, XSDFEC_LDPC_SC_TABLE_ADDR_HIGH, XSDFEC_LDPC_LA_TABLE_ADDR_BASE, XSDFEC_LDPC_LA_TABLE_ADDR_HIGH, XSDFEC_LDPC_QC_TABLE_ADDR_BASE, XSDFEC_LDPC_QC_TABLE_ADDR_HIGH, XSDFEC_SC_TABLE_DEPTH, XSDFEC_LA_TABLE_DEPTH, XSDFEC_QC_TABLE_DEPTH, XSDFEC_MAGIC, XSDFEC_START_DEV, XSDFEC_STOP_DEV, XSDFEC_GET_STATUS, XSDFEC_SET_IRQ, XSDFEC_SET_TURBO, XSDFEC_ADD_LDPC_CODE_PARAMS, XSDFEC_GET_CONFIG, XSDFEC_GET_TURBO, XSDFEC_SET_ORDER, XSDFEC_SET_BYPASS, XSDFEC_IS_ACTIVE, XSDFEC_CLEAR_STATS, XSDFEC_GET_STATS, XSDFEC_SET_DEFAULT_CONFIG. Explicit ioctl-style command names include XSDFEC_START_DEV, XSDFEC_STOP_DEV, XSDFEC_GET_STATUS, XSDFEC_SET_IRQ, XSDFEC_SET_TURBO, XSDFEC_GET_CONFIG, XSDFEC_GET_TURBO, XSDFEC_SET_ORDER, XSDFEC_SET_BYPASS, XSDFEC_IS_ACTIVE, XSDFEC_CLEAR_STATS, XSDFEC_GET_STATS, XSDFEC_SET_DEFAULT_CONFIG.

## Control Flow
Userspace opens the misc device, configures static parameters while the core is stopped, optionally loads LDPC code parameters, sets ordering/bypass/IRQ policy, then starts the core. Status and activity ioctls observe processing, statistics are accumulated by the driver until cleared, and stop/default-config ioctls return the hardware to a known state. Several setters are explicitly valid only in `XSDFEC_STOPPED` state, so the ABI encodes a stopped-configure-start lifecycle.

## State and Persistence Behavior
Persistent state is in the device driver and hardware registers: selected code mode, Turbo algorithm, LDPC tables, AXIS widths, bypass/order flags, IRQ enablement, and accumulated ISR/ECC counters. The header is layout-only, but its table sizes and fixed arrays define the userspace buffer sizes that the kernel copies.

## Dependencies and Integration Points
It depends on fixed-width Linux integer types, ioctl encoding, and userspace-visible `bool`. It integrates with the Xilinx SD-FEC misc driver and hardware blocks that expose Turbo and LDPC datapaths. Direct includes are #include <linux/types.h>.

## Risks and Edge Cases
ABI risks center on fixed-size LDPC arrays, 32/64-bit bool and unsigned-long ioctl payloads, table address range changes, and enforcing stopped-state restrictions before mutating hardware. The bypass comment contains a likely wording error around false/true semantics, so implementation and tests should be treated as authoritative.

## Test Signals
Exercise ioctl number compatibility, stopped-state rejection for setters, LDPC table bounds, Turbo and LDPC mode-specific validation, start requiring order configuration, IRQ/stat clear behavior, and 32-bit userspace compatibility for `unsigned long` and `bool` arguments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/misc/xilinx_sdfec.h -->
