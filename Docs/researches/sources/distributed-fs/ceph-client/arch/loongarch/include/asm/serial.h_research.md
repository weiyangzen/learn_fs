<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/serial.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/serial.h

Purpose: supplies LoongArch serial-port defaults to generic 8250/serial code.
Important APIs and types: defines `BASE_BAUD` and includes generic serial support.
Control flow: no runtime control flow; serial drivers consume constants during console/port setup.
State and persistence: no state, but baud-rate defaults influence early console and legacy serial configuration.
Dependencies and integration: integrates with `serial_core`, 8250 drivers, ACPI SPCR parsing, and early console fallback.
Risks and test signals: wrong baud assumptions affect console readability. Signals are earlycon boot logs and serial console regression testing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/serial.h -->
