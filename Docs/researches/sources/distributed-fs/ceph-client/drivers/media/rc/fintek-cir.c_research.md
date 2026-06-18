<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/fintek-cir.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/fintek-cir.c

Purpose: PNP driver for Fintek LPC Super I/O consumer IR receivers/transceivers. It configures the CIR logical device, receives raw IR packets from I/O registers, registers an rc-core raw receiver, and enables CIR wake support.

Important APIs and functions: config helpers include `fintek_cr_read/write`, config-mode enter/exit, logical-device selection, CIR register read/write, and `cir_dump_regs`. Hardware setup uses `fintek_hw_detect`, `fintek_cir_ldev_init`, `fintek_cir_regs_init`, and `fintek_enable_wake`. RX parsing uses `fintek_cmdsize`, `fintek_get_rx_ir_data`, and `fintek_process_rx_ir_data`. Interrupt/lifecycle callbacks are `fintek_cir_isr`, `fintek_open`, `fintek_close`, `fintek_probe`, `fintek_remove`, `fintek_suspend`, `fintek_resume`, and `fintek_shutdown`.

Control flow: probe validates PNP port/IRQ resources, initializes config port defaults, detects vendor/chip/logical-device revision and TX capability, programs CIR base/IRQ into the logical device, clears/enables CIR interrupts, fills an rc raw device descriptor, requests the I/O region and shared IRQ, registers rc-core, and enables wake capability. ISR selects the CIR logical device, reads status, drains RX data while receive/timeout flags remain, parses command/data versus pulse samples, stores raw IR events, acknowledges status bits, and returns handled. Open enables the logical device and interrupts; close disables it. Suspend disables IRQ/logical device and enables ACPI wake bits; resume re-enables and reinitializes registers.

State and persistence: `struct fintek_dev` stores PNP resources, locks, RX parse buffer and parser state, config/index ports, CIR address/IRQ/length, chip IDs, feature flags, learning/carrier flags, TX queue fields reserved by the structure, and carrier. Hardware configuration is reprogrammed on resume; wake bits may persist through shutdown for IR power-on.

Dependencies and integration points: depends on PNP, direct I/O port access, shared IRQs, spinlocks, wait queues, and rc-core raw event APIs. Header `fintek-cir.h` supplies the register map and state. PNP table matches `FIT0002`.

Risks: `fintek_hw_detect` reads `CIR_CR_CLASS` through the CIR runtime register accessor while in config mode, which is unusual because class is documented as a config register; behavior depends on chip decode semantics. TX-capable fields exist but this file exposes only RX callbacks, so transmit support is incomplete or absent. RX buffer length is 32 bytes but the hardware drain loop increments `pkts` without an explicit bound check. Wake enable is unconditional on remove/shutdown.

Test signals: PNP probe on supported Fintek chips, config port 0x2e/0x4e fallback, RX packet parsing including command headers and overflow, interrupt ack behavior, suspend/resume wake tests, and debug register dump validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/fintek-cir.c -->
