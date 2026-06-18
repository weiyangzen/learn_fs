# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-ls2x.c

Purpose: implements the Loongson-2K and Loongson LS7A I2C controller-mode driver. It is an interrupt-completion byte driver derived from an OpenCores-like register model and supports OF and ACPI discovery.

Important APIs, types, and functions: `struct ls2x_i2c_priv` embeds the adapter, MMIO base, parsed timings, and command completion. `ls2x_i2c_xfer()` is the algorithm hook. `ls2x_i2c_adjust_bus_speed()` parses firmware/ACPI bus speed and programs low/high prescaler bytes. `ls2x_i2c_start()`, `ls2x_i2c_tx()`, `ls2x_i2c_rx()`, and `ls2x_i2c_stop()` implement byte-level transfers.

Control flow: probe maps registers, gets a shared IRQ, initializes adapter fields and completion, programs controller frequency and interrupt-enabled master mode, requests IRQ, then registers the adapter through devm. A transfer loops over messages; each message sends START and address, then reads or writes bytes using `wait_for_completion_timeout()` after command writes. STOP is emitted only after the final message.

State and persistence: persistent hardware state includes prescaler registers and control bits. Software stores firmware timings and completion. A timeout or failed STOP triggers `ls2x_i2c_init()` to reinitialize the controller. Runtime PM suspend disables interrupts and resume reinitializes the device.

Dependencies and integration points: integrates with OF compatibles `loongson,ls2k-i2c` and `loongson,ls7a-i2c`, ACPI id `LOON0004`, firmware timing helpers, runtime PM ops, platform resources, shared IRQ, and I2C core.

Risks: manual byte access is required for prescaler registers because wider writes truncate high bits. ACPI speed and firmware speed are combined with `max()`, which affects unexpected dual-source configurations. `ls2x_i2c_xfer_byte()` waits for completion without reinitializing completion for every byte; the ISR must acknowledge and complete reliably. NACK and arbitration lost are read from status after each command and map to `-ENXIO` and `-EAGAIN`.

Test signals: OF and ACPI probe, default 33 kHz fallback, standard and fast mode timings, read/write and multi-message repeated-start transfers, final STOP idle polling, timeout reinitialization, shared IRQ `IRQ_NONE` path, NACK/arbitration-lost mapping, and PM suspend/resume.
