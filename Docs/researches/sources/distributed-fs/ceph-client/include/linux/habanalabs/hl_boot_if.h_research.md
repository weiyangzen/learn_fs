<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/habanalabs/hl_boot_if.h -->
# sources/distributed-fs/ceph-client/include/linux/habanalabs/hl_boot_if.h

Purpose: This header defines the HabanaLabs boot-loader/firmware communication ABI shared between the Linux kernel driver and device firmware across preboot, U-Boot/Linux firmware, component loading, reset, status, errors, and version reporting.

Important APIs/types/functions: It defines boot magic values, FIT SRAM offset, version length, `enum cpu_boot_err` with fatal mask and bit macros, `enum cpu_boot_dev_sts` with feature/status bit macros, `enum cpu_boot_status`, KMD messages, CPU message status, `struct cpu_dyn_regs` register map, communication descriptor/message magics and validation macros, message types, `struct lkd_fw_binning_info`, descriptor/message headers with CRC/size/version/type, ASCII firmware messages, `struct lkd_fw_comms_desc`, reset causes, `struct lkd_fw_comms_msg`, command/status enums and bitfield wrappers, module/version structures, and FIT version size limit.

Control flow, state, and persistence: The host and firmware exchange commands through registers: host writes a `comms_command`, firmware acknowledges and later writes a `comms_status` containing status plus SRAM/DRAM offset. Descriptor/message headers carry magic, CRC, size, and version so the host can validate data. Boot status/error/device-status registers persist the current firmware stage and capabilities.

Dependencies/integration: It feeds `cpucp_if.h` and the HabanaLabs driver boot path. It assumes firmware-side bitfield producers but host-side code should use masks and endian-aware fields.

Risks and test signals: Many comments warn to consider ABI before changing structures and counts. Bit shifts such as `1 << CPU_BOOT_ERR_SCND_EN` exceed 32-bit masks if used incorrectly; the header separates register 0/1 enabled bits. Tests should cover magic/version validation, CRC/size checks, command/status packing, boot error fatal classification, status feature gating, descriptor compatibility versions, and reset/failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/habanalabs/hl_boot_if.h -->
