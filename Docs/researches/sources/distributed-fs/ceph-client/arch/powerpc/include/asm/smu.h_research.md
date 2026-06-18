<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/smu.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/smu.h

Purpose: Defines the Apple System Management Unit command interface and request structures.

Important APIs/types/functions: SMU command IDs, transfer flags, `struct smu_cmd`, async request queues, partition/RTC/I2C/fan/LED/battery helpers, and platform init declarations. Source-visible declarations include: #define _SMU_H; #define SMU_CMD_PARTITION_COMMAND 0x3e; #define SMU_CMD_PARTITION_LATEST 0x01; #define SMU_CMD_PARTITION_BASE 0x02; #define SMU_CMD_PARTITION_UPDATE 0x03; #define SMU_CMD_FAN_COMMAND 0x4a; #define SMU_CMD_BATTERY_COMMAND 0x6f; #define SMU_CMD_GET_BATTERY_INFO 0x00.

Control flow: callers prepare a command buffer, submit sync or async requests, and callbacks consume firmware replies. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: request objects, command buffers, SMU firmware state, and sysfs-visible device state persist outside this header. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are #include <linux/list.h>, #include <linux/types.h>. Integrated with PowerMac thermal, fan, RTC, I2C, LED, battery, and reboot/power-control code.

Risks: firmware command lengths and callback lifetimes are fragile; bad commands can stall platform management. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 694 lines, 19789 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/smu.h -->
