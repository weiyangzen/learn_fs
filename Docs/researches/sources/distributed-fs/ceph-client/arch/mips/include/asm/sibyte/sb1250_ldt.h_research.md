# sources/distributed-fs/ceph-client/arch/mips/include/asm/sibyte/sb1250_ldt.h

Purpose: defines SB1250 Lightning Data Transport/HyperTransport bridge configuration-space offsets and bitfields. It lets platform PCI/HT setup and error handling code program the on-chip LDT interface.

Important APIs/types/functions: important symbols include vendor/device IDs `K_LDT_VENDOR_SIBYTE` and `K_LDT_DEVICE_SB1250`, type-1 config header offsets (`R_LDT_TYPE1_*`), device ID/class/header fields, command/status and bridge-control masks, LDT command fields, link control/frequency fields, SRI command/control and buffer count fields, error status/control bits, CRC counters, and additional status bits for later revisions.

Control flow: platform code reads config header identity, enables I/O/memory/mastering, configures bridge windows and bus numbers, programs link control/frequency, handles CRC/error/status registers, and configures SRI flow-control behavior. Some macros assume a 32-bit read of combined command/status-style registers, which shapes how callers must access config space.

State and persistence: all represented values live in LDT/PCI configuration or status registers. Command/bridge/link settings persist until reset or reconfiguration; error/status bits may be latched and require explicit clearing.

Dependencies and integration: depends on `sb1250_defs.h` and feature gates for pass2/112x fields. It integrates with `sb1250_regs.h` LDT/PCI base addresses, PCI subsystem setup, interrupt mapper LDT sources, and error-reporting paths.

Risks and test signals: register-width assumptions are important; reading or writing only 16 bits where macros expect a combined 32-bit value can misplace bits. Link frequency/control mistakes can break bus enumeration. Test signals include config-space read/write tests, PCI/HT enumeration, link training/status checks, injected fatal/nonfatal LDT errors, and compile coverage for pass1 versus pass2 fields.
