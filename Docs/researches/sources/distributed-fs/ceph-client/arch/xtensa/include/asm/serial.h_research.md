<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/serial.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/serial.h

Purpose: delegates Xtensa serial-port configuration to platform-specific `platform/serial.h`, supporting 8250-style serial setup without hardcoding board details in the architecture header.

Control flow is none; it is an include bridge. State is determined by platform serial definitions such as base addresses, IRQs, or baud settings provided elsewhere. Dependencies are the platform header path and serial driver expectations. Integration points are early console, 8250/legacy serial drivers, board platform code, and boot parameter serial tags. Risks are missing or incompatible platform serial definitions, which can break console availability or serial IRQ mapping. Test signals include early printk/console output, 8250 driver probe logs, serial loopback, and platform build coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/serial.h -->
