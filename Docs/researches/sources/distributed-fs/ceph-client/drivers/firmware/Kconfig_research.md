# sources/distributed-fs/ceph-client/drivers/firmware/Kconfig

## Purpose
Defines the top-level `Firmware Drivers` Kconfig menu. It exposes common firmware protocol drivers, system firmware data exports, platform-specific secure-firmware interfaces, and sources subdirectory Kconfig files for ARM SCMI/FF-A, EFI, PSCI, Qualcomm, Tegra, Xilinx, and other vendor firmware blocks.

## APIs, Types, And Functions
This is declarative Kconfig. Important symbols include `ARM_SCPI_PROTOCOL`, `ARM_SDE_INTERFACE`, `EDD`, `FIRMWARE_MEMMAP`, `DMIID`, `DMI_SYSFS`, `ISCSI_IBFT`, `RASPBERRYPI_FIRMWARE`, `FW_CFG_SYSFS`, `INTEL_STRATIX10_SERVICE`, `MTK_ADSP_IPC`, `SYSFB`, `SYSFB_SIMPLEFB`, `TH1520_AON_PROTOCOL`, `TI_SCI_PROTOCOL`, `TRUSTED_FOUNDATIONS`, and `TURRIS_MOX_RWTM`.

## Control Flow
Kconfig evaluates dependencies, defaults, and `select` relationships to decide which firmware objects and submenus are available. The file starts by sourcing ARM SCMI, defines many top-level options, then sources ARM FF-A and vendor/platform subtrees before closing the menu.

## State, Persistence, And Dependencies
Persistent output is the configured kernel `.config`; no runtime state is produced directly. Dependencies connect options to architecture support, ACPI/DMI/SCSI/SYSFS, mailbox providers, DMA, OF, KEYS, and other platform facilities.

## Integration Points
The matching `drivers/firmware/Makefile` consumes these symbols to include objects and subdirectories. Downstream drivers depend on these symbols to obtain firmware protocol APIs, sysfs exports, boot firmware data, and platform services.

## Risks And Test Signals
Risks are incorrect dependencies that expose unbuildable drivers, missing `select`s for required helper subsystems, defaults that change boot behavior, and stale sourced paths. Test signals are `olddefconfig`, `allmodconfig`, architecture build coverage, and boot/sysfs smoke tests for enabled firmware features.
