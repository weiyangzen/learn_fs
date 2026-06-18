<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/sym53c8xx_2/sym53c8xx.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/sym53c8xx_2/sym53c8xx.h

## Purpose
`sym53c8xx.h` is the Linux configuration header for the Symbios/LSI 53C8XX/53C1010 driver. It translates Kconfig choices into driver constants, declares the boot/module setup structure, and sets global limits for tags, scatter-gather, targets, LUNs, NVRAM, generic-chip support, immediate arbitration, and residual reporting.

## Important APIs, Types, And Functions
The central type is `struct sym_driver_setup`, containing max tags, burst order, LED/differential/IRQ/bus-check/host-ID settings, verbosity, settle delay, NVRAM usage, and excluded devices. `SYM_LINUX_DRIVER_SETUP` provides defaults derived from Kconfig. Macros such as `SYM_CONF_DMA_ADDRESSING_MODE`, `SYM_CONF_NVRAM_SUPPORT`, `SYM_CONF_GENERIC_SUPPORT`, `SYM_CONF_MAX_TAG`, `SYM_CONF_MAX_TAG_ORDER`, `SYM_CONF_MAX_SG`, `SYM_CONF_MAX_TARGET`, `SYM_CONF_MAX_LUN`, `SYM_SETUP_*`, and `SYM_SETUP_RESIDUAL_SUPPORT` are consumed throughout the driver. The header declares `sym_driver_setup` and `sym_debug_flags`.

## Control Flow
There is no executable control flow. Compile-time conditionals clamp tag limits to 2..256 and select a tag-order power based on that maximum. Runtime setup flows through objects that instantiate `sym_driver_setup`, parse boot/module overrides, and use these macros in allocation, negotiation, queue-depth, and firmware selection.

## State And Persistence Behavior
The header defines shape and defaults for runtime setup state but stores no state itself. `sym_driver_setup` is externally defined and mutable at boot/module parameter parsing time. No persistent state is maintained.

## Dependencies And Integration Points
It depends on SCSI Symbios Kconfig symbols and is included by driver implementation files. It directly influences firmware selection (`SYM_CONF_GENERIC_SUPPORT`), firmware relocation/runtime data sizes (`SYM_CONF_MAX_SG`, tag order), PCI DMA addressing behavior, proc/debug/user-command support, and NVRAM behavior.

## Risks
Risks include compile-time limits that must match firmware table sizes and C data structures, tag-order mismatches, enabling unsupported DMA addressing modes, and global defaults that affect all adapters. Increasing `SYM_CONF_MAX_SG` or max tags without matching memory/script assumptions could corrupt firmware scripts or queues.

## Test Signals
Test builds across DMA addressing modes 0/1/2, max tags below 2, normal, and above 256, default tag overrides, NVRAM enabled behavior, generic-chip fallback, residual reporting, and driver parameter parsing that updates `sym_driver_setup`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/sym53c8xx_2/sym53c8xx.h -->
