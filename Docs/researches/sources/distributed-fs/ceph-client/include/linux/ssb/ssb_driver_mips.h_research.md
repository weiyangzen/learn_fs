<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ssb/ssb_driver_mips.h -->
# sources/distributed-fs/ceph-client/include/linux/ssb/ssb_driver_mips.h

Purpose: Defines MIPS core support data for SSB embedded systems, including serial ports, parallel/serial flash descriptors, CPU clock, and IRQ mapping.

Important APIs/types/functions: `struct ssb_serial_port`, `struct ssb_pflash`, optional `struct ssb_sflash`, `struct ssb_mipscore`, `ssb_mipscore_init()`, `ssb_cpu_clock()`, and `ssb_mips_irq()`.

Control flow: Enabled builds initialize a MIPS core object with discovered serial/flash resources and expose clock/IRQ helpers. Disabled builds define an empty `ssb_mipscore` and no-op/zero-return stubs.

State and persistence behavior: Runtime state includes SSB device pointer, serial-port descriptors, parallel flash metadata, and optional serial flash metadata. Flash descriptors describe persistent storage windows but do not manipulate contents here.

Dependencies: SSB device declarations and configuration for MIPS and serial flash support.

Integration points: BCM47xx-style MIPS boot/platform code, serial console setup, flash mapping, and IRQ routing for SSB devices.

Risks: Disabled stubs return IRQ 0, which callers must treat carefully. Flash window/buswidth values are hardware-derived and must match actual board wiring.

Test signals: MIPS SSB platform boot tests, serial-port enumeration, CPU clock calculations, flash map detection, and IRQ mapping tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ssb/ssb_driver_mips.h -->
