<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/fintek-cir.h -->
# sources/distributed-fs/ceph-client/drivers/media/rc/fintek-cir.h

Purpose: private definitions for the Fintek LPC Super I/O CIR driver, including register addresses, packet constants, debug macros, and `struct fintek_dev`.

Important APIs and types: `struct fintek_dev` captures PNP/rc resources, spinlocks, RX packet buffer/parser state, TX staging queue fields, config-register ports, CIR I/O resources, chip/vendor IDs, logical-device number, feature flags, learning/carrier flags, and current carrier period. Macros cover Fintek vendor ID, config-mode magic, global control registers, CIR logical-device registers, ACPI wake registers, CIR runtime registers/status bits, RX/TX packet encodings, and sample period.

Control flow: `fintek-cir.c` consumes these definitions for hardware detection, logical-device setup, IRQ handling, raw sample parsing, power management, and wake enablement.

State and persistence: header state is in-memory driver state plus hardware register constants. Wake configuration registers can persist across suspend/shutdown as platform firmware-visible state.

Dependencies and integration points: includes spinlock and ioctl headers and is private to `fintek-cir.c`. Debug macros use the translation unit's `debug` module parameter.

Risks: TX-related fields and packet constants are present even though the C file does not expose TX rc-core callbacks, which can mislead maintainers. Parser constants mirror MCEUSB-like framing and must stay synchronized with hardware packet format. Direct I/O register constants are revision-sensitive.

Test signals: compile coverage, hardware detection logs, parser tests using known packet streams, and suspend/resume wake register validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/fintek-cir.h -->
