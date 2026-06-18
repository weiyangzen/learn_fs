# sources/distributed-fs/ceph-client/drivers/net/can/sja1000/tscan1.c

Purpose: ISA driver for Technologic Systems TS-CAN1 PC/104 boards. It probes board PLD registers, determines IRQ from jumper bits, selects an available SJA1000 I/O base, and delegates CAN operation to the SJA1000 core.

Important APIs/types/functions: constants define PLD offsets, ID magic values, jumper masks, PLD base, SJA1000 candidate bases, and 16 MHz crystal. `tscan1_read()`/`tscan1_write()` use port I/O. `tscan1_probe()` performs board detection/resource selection; `tscan1_remove()` disables and releases resources. `module_isa_driver()` registers up to four jumper-selected boards.

Control flow: probe reserves the PLD region for the ISA ID, validates two ID bytes, maps JP4/JP5 jumper state to IRQ 5/6/7, allocates SJA1000 netdev, configures clock/CDR/OCR and port accessors, then scans a list of SJA1000 base addresses. For each free region it enables the PLD mode with address index and calls `register_sja1000dev()`; failures disable mode and try the next base.

State and persistence: device state is held in the netdev private structure and PLD registers. `netdev->base_addr` stores PLD base, while `priv->reg_base` stores SJA1000 port base. The LED is turned off after successful registration. No disk persistence.

Dependencies/integration: ISA driver core, I/O port reservation, SJA1000 core, and TS-CAN1 PLD hardware semantics documented in comments.

Risks: auto-selecting the first free SJA1000 address may choose an electrically invalid address if the PLD/hardware setup is unexpected. Bad jumper state without IRQ fails probe. Cleanup depends on `dev_get_drvdata()` being populated only after success.

Test signals: probe each JP1/JP2 board slot; verify ID mismatch returns `-ENODEV`; test all JP4/JP5 IRQ combinations; force address conflicts to exercise fallback; unload should disable SJA1000 I/O and release both regions.
