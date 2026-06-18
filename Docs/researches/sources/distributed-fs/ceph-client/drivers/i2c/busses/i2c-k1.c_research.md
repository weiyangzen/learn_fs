# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-k1.c

Purpose: implements the SpacemiT K1 I2C master driver. It supports normal interrupt-driven transfers plus atomic PIO transfers, basic bus reset/release recovery, clock-frequency clamping to standard/fast mode, and a byte-oriented controller state machine.

Important APIs, types, and functions: `struct spacemit_i2c_dev` stores device, adapter, MMIO base, IRQ, configured bus frequency, message array, current message/index/buffer/count, current state, direction, PIO flag, completion, and last status. `spacemit_i2c_xfer_common()` is shared by normal and atomic algorithm hooks. State helpers include `spacemit_i2c_start()`, `spacemit_i2c_handle_state()`, `spacemit_i2c_handle_read()`, `spacemit_i2c_handle_write()`, `spacemit_i2c_err_check()`, and PIO wait emulation.

Control flow: probe reads/clamps `clock-frequency`, maps registers, requests an IRQ with `IRQF_NO_SUSPEND`, enables functional and bus clocks, deasserts optional reset, resets hardware, initializes the adapter, and registers a numbered adapter. A transfer configures interrupt or PIO mode, calculates timeout from total bytes and bus frequency, initializes control bits, enables the unit, waits for bus idle, then processes each message by writing address, sending START, and driving byte progress from IRQ or polling. After transfer it disables the unit and logs timeout/arbitration failures.

State and persistence: persistent state is small: bus frequency, hardware base, clocks managed by devm, adapter, and completion. Transfer state is stored in `msgs`, `msg_idx`, `msg_buf`, `unprocessed`, `state`, `read`, `use_pio`, and `status`. Hardware may be reset when arbitration, bus error, or timeout is observed. Bus line state is sampled through `IBMR` for recovery.

Dependencies and integration points: integrates with OF compatible `spacemit,k1-i2c`, platform resources, reset controls, two named clocks `func` and `bus`, readl polling helpers, completions, and I2C atomic transfer API.

Risks: interrupt and PIO paths share the same state machine but different completion semantics. Last-byte STOP/NAK detection is subtle, especially reads where `ACKNAK` is set for the final byte. `spacemit_i2c_wait_pio_xfer()` returns synthetic nonzero success rather than remaining jiffies. Bus recovery toggles reset cycles up to nine times and warns if SDA stays low. The glitch-fix disable in `IRCR` is required for restart behavior.

Test signals: normal and atomic transfers, read/write single-byte and multi-byte messages, repeated starts, STOP on final message only, no SMBus quick advertised, timeout path with bus reset, arbitration lost mapping to `-EAGAIN`, NACK mapping to `-ENXIO`, busy-bus wait and recovery, clock-frequency clamping, and probe with absent optional reset.
