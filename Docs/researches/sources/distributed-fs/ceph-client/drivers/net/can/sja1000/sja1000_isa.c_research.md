# sources/distributed-fs/ceph-client/drivers/net/can/sja1000/sja1000_isa.c

Purpose: legacy ISA-bus wrapper for SJA1000 CAN controllers configured through module parameters. It creates platform devices for up to eight manually described controllers and binds them to the shared SJA1000 core.

Important APIs/types/functions: module parameters `port`, `mem`, `irq`, `clk`, `cdr`, `ocr`, and `indirect` describe hardware. Register accessors cover memory-mapped, port I/O, and two-port indirect address/data access with per-device spinlocks. `sja1000_isa_probe()` allocates/configures/registers a CAN netdev; `sja1000_isa_remove()` releases resources; init/exit create platform devices and register the platform driver.

Control flow: module init scans parameter arrays. Entries with port or mem plus IRQ become `platform_device`s; incomplete first or explicitly configured entries fail. Probe reserves either memory or I/O ports, maps memory as needed, selects register accessor, derives CAN clock from oscillator divided by two, applies OCR/CDR defaults or overrides, and calls `register_sja1000dev()`. Remove unregisters the CAN device and releases I/O or memory regions.

State and persistence: static module parameter arrays and `sja1000_isa_devs[]` persist for module lifetime. Indirect I/O locks are static per index. Hardware state is reset and initialized by the core at register/open time; no disk persistence exists.

Dependencies/integration: depends on platform bus, ISA-style I/O port APIs, io memory mapping, SocketCAN SJA1000 core, and `linux/can/platform/sja1000.h` OCR/CDR constants.

Risks: fully manual resource configuration can collide with other devices. Indirect mode inheritance from `indirect[0]` is subtle. `priv->reg_base` stores port addresses cast through `void __iomem *`, so accessors must remain consistent. Invalid clock/OCR/CDR module params can produce nonfunctional CAN timing or output drive.

Test signals: load with valid `port`/`irq` or `mem`/`irq`; verify region reservation errors on conflicts; test indirect address/data mode; confirm default and indexed parameter fallback; unload should release all platform devices and regions.
