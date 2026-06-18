# sources/distributed-fs/ceph-client/arch/mips/sgi-ip22/ip22-platform.c

Purpose: registers IP22 platform devices for SCSI, Ethernet, audio, buttons, RTC, and Zilog serial.

Important APIs and control flow: device initcalls create `sgiwd93` SCSI devices with HPC register pointers, primary and optional secondary `sgiseeq` Ethernet devices with MAC addresses from NVRAM/EEPROM, `sgihal2`, optional `sgibtns`, `rtc-ds1286`, and `ip22zilog`. Secondary Ethernet is enabled only when a second HPC is present and after MC/HPC GIO settings are adjusted.

State, persistence, and integration: state is platform-device registration and platform data containing IRQs, register pointers, DMA masks, and MAC addresses. Dependencies include HPC/MC/NVRAM initialization, bus-error-safe detection, and platform drivers for SGI devices. Risks include using `IS_ERR()` on integer return values in simple-device helpers, hard-coded NVRAM offsets, and direct side effects on GIO arbitration for mezzanine Ethernet. Test signals are device enumeration, correct eth MACs, SCSI detection, RTC registration, and serial console availability.
