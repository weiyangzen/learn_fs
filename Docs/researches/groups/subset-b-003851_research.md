# subset-b-003851 research

Grouped research for Linux I2C bus controller drivers under `sources/distributed-fs/ceph-client/drivers/i2c/busses/`. Each section preserves the source path in its title and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-imx.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-imx.c

Purpose: implements the I2C adapter driver for Freescale/NXP i.MX, MXC, VF610, S32G, and compatible controllers. It supports master transfers, atomic transfers, optional DMA, SMBus block reads, slave mode, clock-change handling, runtime/system PM, and basic pinctrl-based bus recovery.

Important APIs, types, and functions: `struct imx_i2c_struct` is the main per-controller state, combining `i2c_adapter`, MMIO base, clock, wait queue, runtime clock data, DMA state, slave state, ISR state machine fields, and bus recovery info. `struct imx_i2c_hwdata` captures SoC-specific register shift, divider table, interrupt-clear opcode, enable opcode, and errata flags. `i2c_imx_xfer()` and `i2c_imx_xfer_atomic()` implement the `i2c_algorithm`; `i2c_imx_reg_slave()` and `i2c_imx_unreg_slave()` expose slave registration. Key transfer helpers include `i2c_imx_start()`, `i2c_imx_stop()`, `i2c_imx_write()`, `i2c_imx_read()`, atomic PIO variants, and DMA variants.

Control flow: probe maps registers, gets the clock, initializes runtime PM, requests a shared no-suspend IRQ, chooses hardware data from OF/ACPI/platform id, registers a clock notifier, configures bus speed, resets registers, optionally enables recovery and DMA, then registers the numbered adapter. Master transfer resumes the device, starts the controller, handles repeated starts for each message, chooses atomic PIO, interrupt-driven PIO, or DMA based on context and message flags, then always stops the controller and restores slave mode if a slave client is registered. The IRQ first services slave-mode events when not in master mode, otherwise runs a master ISR state machine for read, write, DMA, and SMBus block data states.

State and persistence: persistent runtime state includes selected divider `ifdr`, current parent clock rate, requested bitrate, stopped flag, multi-master flag, DMA channels, current transfer message/index/state, and registered slave client. Hardware state is reset on probe and after transfers, disabled on stop, and managed through runtime PM clock enable/disable. Slave event sequencing is persisted through `last_slave_event` and a high-resolution timer that checks missed stop conditions.

Dependencies and integration points: integrates with the platform bus, OF compatible data, ACPI id `NXP0001`, I2C core adapter and slave APIs, DMAengine channels named `tx` and `rx`, clk notifiers, runtime PM, pinctrl sleep/default states, and generic I2C bus recovery. It consumes optional platform data for bitrate and DT properties such as `clock-frequency` and `single-master`.

Risks: register clear semantics differ between i.MX and Vybrid/S32G, so incorrect `i2sr_clr_opcode` or enable opcode corrupts interrupt handling. STOP timing is delicate for reads and DMA, especially the final-byte read ordering that prevents an extra clock. DMA has CPU-transferred edge bytes and timeout paths that must terminate and unmap correctly. Multi-master arbitration lost handling returns `-EAGAIN` in multiple paths. Slave mode shares IRQ and state with master transfers, protected by a spinlock and timer, so regressions can cause duplicate or missing slave events.

Test signals: boot/probe on at least one classic i.MX, VF610, and S32G-compatible target; standard/fast mode timing and ERR007805 frequency clamp; write, read, repeated-start read, SMBus block read, atomic transfer path, DMA-safe transfers above threshold, NACK and arbitration-lost handling, runtime suspend/resume and system suspend/resume, bus recovery when pins are available, and slave callback sequencing including read-requested, write-received, and stop events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-imx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-iop3xx.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-iop3xx.c

Purpose: provides the platform I2C adapter driver for Intel XScale IOP3xx and IXP46x controllers. It is an interrupt-driven byte-oriented master driver using the register definitions in `i2c-iop3xx.h`.

Important APIs, types, and functions: `struct i2c_algo_iop3xx_data` stores MMIO address, wait queue, spinlock-protected interrupt status, enabled status bits, adapter id, and optional GPIO descriptors used to clear GPOD before enabling. `iop3xx_i2c_xfer()` is the algorithm transfer hook. Helper layers split into reset/enable/cleanup, wait helpers, address emission, byte read/write, message handling, IRQ handling, and platform probe/remove.

Control flow: probe allocates adapter and private state, obtains optional SCL/SDA GPIOs, requests and maps the memory region, requests the IRQ, initializes wait queues and locks, resets/enables hardware, and registers a numbered adapter. A transfer waits idle, resets/enables the unit, then handles each message by sending the target address followed by byte-wise read or write. Each byte operation starts a hardware transfer and waits for TX-empty or RX-full status captured by the IRQ handler. Cleanup clears master start/byte/stop/SCL enable bits.

State and persistence: transient state is mostly interrupt status in `SR_received`, protected by `lock` and consumed by waiters. The driver resets and re-enables the controller at the start of each transfer, so hardware transaction state is intentionally short-lived. The global `i2c_id` assigns an internal id but adapter numbering uses platform id.

Dependencies and integration points: integrates with platform devices, OF compatibles `intel,iop3xx-i2c` and `intel,ixp4xx-i2c`, legacy `I2C_CLASS_HWMON`, raw MMIO access, optional GPIO descriptors, Linux IRQ and wait queue APIs, and the I2C core.

Risks: the driver refuses address `MYSAR` because writing to the local target address can latch up IOP331 hardware. `iop3xx_i2c_wait_idle()` uses the same interrupt status mechanism as transfer waits, so stale status handling matters. The IRQ handler always returns handled after masking status, which may obscure unexpected shared IRQ behavior. Probe uses manual allocation, mapping, request_irq, and release paths rather than devm for most resources.

Test signals: validate probe/remove resource unwinding, IRQ-driven TX/RX completion, timeout when no interrupt arrives, bus error and arbitration loss status mapping, local target address refusal, combined read/write messages with repeated starts, optional GPIO clearing before enable, and compatibility on both IOP3xx and IXP46x variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-iop3xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-iop3xx.h -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-iop3xx.h

Purpose: private header for the IOP3xx/IXP46x I2C driver. It defines register offsets, control/status bit meanings, local constants, error codes, IO size, and the private adapter data structure consumed by `i2c-iop3xx.c`.

Important APIs, types, and functions: the header does not export callable functions. The central type is `struct i2c_algo_iop3xx_data`, containing the mapped register base, wait queue, spinlock, enabled/received status masks, logical id, and optional GPIO descriptors. Register constants cover control register operations such as reset, unit enable, SCL enable, START/STOP, NACK, and transfer byte, plus status bits for bus error, RX full, TX empty, arbitration loss, bus busy, unit busy, NACK, and read/write direction.

Control flow: this header shapes the C file's byte-level state machine. Control bits are written to `CR_OFFSET`, status bits are read/cleared through `SR_OFFSET`, and data is moved through `DBR_OFFSET`. `IOP3XX_ISR_CLEARBITS` is used during reset, while `IOP3XX_ISR_*` masks drive wait conditions and error mapping.

State and persistence: the structure fields persist per adapter. `SR_received` is an interrupt-to-waiter handoff field, while `SR_enabled` limits which status bits the IRQ handler records. Optional SCL/SDA GPIO descriptors persist only to support the GPOD clearing requirement before enabling the controller.

Dependencies and integration points: depends on Linux `wait_queue_head_t`, `spinlock_t`, `u32`, `void __iomem`, and `struct gpio_desc`. It is included only by the IOP3xx driver and is not a public kernel API.

Risks: bit definitions are hardware contract. Any mismatch in clear bits, offsets, or interrupt masks changes live bus behavior. Error codes `I2C_ERR_BERR` and `I2C_ERR_ALD` are private numeric constants that the C file negates, so callers see unusual negative values rather than standard errno for those two cases.

Test signals: compile coverage with the C file, register offset validation on real hardware or emulation, interrupt bit clear tests, error mapping for bus error and arbitration loss, and GPOD-related enable sequencing on systems that provide SCL/SDA GPIO descriptors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-iop3xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-isch.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-isch.c

Purpose: implements an SMBus-only platform adapter for Intel SCH chipsets such as AF82US15W/US15L/UL11L. It provides SMBus quick, byte, byte-data, word-data, and block-data transactions through IO port mapped host controller registers.

Important APIs, types, and functions: `struct sch_i2c` embeds an `i2c_adapter` and `smba` IO mapping. `sch_access()` is the `smbus_xfer` implementation. `sch_transaction()` starts the host transaction, polls for busy clear, interprets completion/error bits, and clears completion status. Small helpers wrap 8-bit and 16-bit IO reads/writes.

Control flow: probe maps the IORESOURCE_IO range, fills the adapter metadata, and registers it with devm. For each SMBus access, the driver checks the host busy bit, initializes clock divider defaults if needed, writes address/command/data registers according to transaction size, writes the encoded protocol into `SMBHSTCNT`, calls `sch_transaction()`, and copies readback data from the data/block registers on read transactions.

State and persistence: persistent state is only the adapter and mapped SMBus base. Hardware persists the host clock divider, which the driver initializes lazily from the `backbone_speed` module parameter when the divider is zero. There is no interrupt state, DMA state, or runtime PM.

Dependencies and integration points: integrates as platform driver `isch_smbus`, uses IO port mapping, the I2C SMBus algorithm interface, module parameter `backbone_speed`, and HWMON class scanning.

Risks: status bits are packed into the low nibble of `SMBHSTSTS`; clearing or interpreting them incorrectly can leave the host unusable. Bus collision is reported as a condition that may lock the SMBus until hard reset. Block read length must be validated against `I2C_SMBUS_BLOCK_MAX`. Unsupported SMBus protocol sizes return `-EOPNOTSUPP`.

Test signals: SMBus quick/byte/byte-data/word/block read and write transactions, uninitialized clock divider path, busy host rejection, timeout path from `read_poll_timeout`, no-response and bus-collision status handling, invalid block lengths, and platform probe with IO region conflicts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-isch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-ismt.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-ismt.c

Purpose: implements the Intel SMBus Message Transport PCI driver for Atom S12xx and related Intel devices. It supports hardware PEC, block buffer, process call, block process call, I2C block transactions, descriptor-ring execution, MSI or INTx completion, and ACPI resource conflict checks.

Important APIs, types, and functions: `struct ismt_desc` is the packed hardware descriptor with target address, command/write length, read length, control/status, retry, byte counts, and DMA pointer. `struct ismt_priv` stores the adapter, PCI BAR, coherent descriptor ring, head pointer, completion, aligned data buffer, and interrupt log. `ismt_access()` is the SMBus algorithm hook. `ismt_process_desc()` translates descriptor status and copies read results. `ismt_hw_init()`, `ismt_dev_init()`, and `ismt_int_init()` configure hardware, coherent memory, and interrupts.

Control flow: probe enables the PCI device, sets bus mastering, checks BAR and ACPI conflicts, maps BAR0, enables 64-bit coherent DMA, allocates descriptors and interrupt log, initializes hardware registers, requests MSI or shared INTx, and registers the adapter. Each SMBus operation clears the current descriptor and log, fills descriptor fields and an aligned DMA buffer based on the SMBus protocol, maps the data buffer if needed, submits the descriptor by advancing firmware head pointer and setting start, waits up to one second for interrupt completion, unmaps DMA, processes descriptor status, then advances the ring head.

State and persistence: persistent state includes coherent descriptor memory, interrupt log memory, `head` ring index, `cmp` completion, bus speed module parameter-derived hardware speed, and adapter retry count. Hardware persists descriptor base, interrupt cause location, descriptor size, retry policy, and speed timing until reinitialized.

Dependencies and integration points: integrates with PCI ids for multiple Intel SMT devices, ACPI companion/resource checks, DMA mapping/coherent APIs, MSI/INTx IRQ APIs, `i2c_add_adapter`, and SMBus core functionality flags including PEC.

Risks: descriptor and DMA buffer layout is hardware-sensitive, including 16-byte alignment of `priv->buffer`. I2C block read forces the address R/W bit to write per hardware spec, which is easy to regress. MSI and INTx have different interrupt acknowledgement semantics. Timeout kills the transaction but descriptor/ring state still advances after cleanup. Large-packet, CRC, collision, and timeout statuses map to distinct errno values.

Test signals: PCI probe on MSI-capable and INTx-only systems, every advertised SMBus protocol including PEC and block process call, I2C block read/write, DMA mapping failure, descriptor timeout and kill path, NAK/CRC/collision/large-packet/clock-low status translation, bus speed module parameter values 0/80/100/400/1000, and remove while adapter is registered.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-ismt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-jz4780.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-jz4780.c

Purpose: implements an interrupt-driven I2C master driver for Ingenic JZ4770/JZ4780 and X1000 controllers. It handles SoC-specific FIFO size and STOP generation differences, clock timing setup, read-command FIFO scheduling, and PIO data movement through controller FIFOs.

Important APIs, types, and functions: `struct jz4780_i2c` stores MMIO, IRQ, clock, adapter, SoC config, spinlock, read/write buffer state shared with the IRQ handler, speed, completion, and debug counters. `struct ingenic_i2c_config` identifies JZ4780 versus X1000 behavior and FIFO thresholds. `jz4780_i2c_xfer()` is the algorithm hook, with helpers for enable/disable, target address setup, speed calculation, cleanup, read/write transfer setup, and ISR work.

Control flow: probe gets match data, maps registers, enables the clock, reads required DT `clock-frequency`, programs timing, clears stop-hold for pre-X1000, masks interrupts, requests IRQ, and registers the adapter. A transfer prepares the controller, updates target address when needed, then runs each message through read or write setup. The IRQ drains RX FIFO before issuing more read commands, manages TX-empty interrupts to enqueue read commands or write data, emits STOP either through X1000 command bits or old controller stop-hold clearing, and completes the transfer.

State and persistence: persistent state includes controller speed in kHz, SoC FIFO thresholds, current target register value, and completion object. During transfer, `rbuf`, `wbuf`, byte counts, read-command counts, stop-hold, and direction are shared between thread and IRQ under `lock`. Hardware is cleaned after every transfer by masking/clearing interrupts, toggling controller enable, and disabling the device.

Dependencies and integration points: integrates with OF compatibles `ingenic,jz4770-i2c`, `ingenic,jz4780-i2c`, and `ingenic,x1000-i2c`, platform IRQ/MMIO, clock framework, and the I2C core.

Risks: read path must avoid RX FIFO overrun by draining before sending more read commands. X1000 uses per-command STOP while older hardware uses `STPHLD`, so cross-version regressions can create missing or early STOPs. `clock-frequency` is mandatory and converted to kHz, with a minimum of 1000 Hz. Timeout is scaled by message length and maps many failures to `-EIO`. Cleanup toggles control bits under lock and then disables the controller, which is sensitive to interrupt timing.

Test signals: JZ4770/JZ4780 and X1000 probe, standard and fast mode clock programming, read lengths below and above FIFO size, multi-message repeated-start transfers, write completion waiting for FIFO empty/master inactive, TX abort and RX overflow handling, timeout cleanup, missing `clock-frequency` rejection, and no interrupt leakage after cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-jz4780.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-k1.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-k1.c

Purpose: implements the SpacemiT K1 I2C master driver. It supports normal interrupt-driven transfers plus atomic PIO transfers, basic bus reset/release recovery, clock-frequency clamping to standard/fast mode, and a byte-oriented controller state machine.

Important APIs, types, and functions: `struct spacemit_i2c_dev` stores device, adapter, MMIO base, IRQ, configured bus frequency, message array, current message/index/buffer/count, current state, direction, PIO flag, completion, and last status. `spacemit_i2c_xfer_common()` is shared by normal and atomic algorithm hooks. State helpers include `spacemit_i2c_start()`, `spacemit_i2c_handle_state()`, `spacemit_i2c_handle_read()`, `spacemit_i2c_handle_write()`, `spacemit_i2c_err_check()`, and PIO wait emulation.

Control flow: probe reads/clamps `clock-frequency`, maps registers, requests an IRQ with `IRQF_NO_SUSPEND`, enables functional and bus clocks, deasserts optional reset, resets hardware, initializes the adapter, and registers a numbered adapter. A transfer configures interrupt or PIO mode, calculates timeout from total bytes and bus frequency, initializes control bits, enables the unit, waits for bus idle, then processes each message by writing address, sending START, and driving byte progress from IRQ or polling. After transfer it disables the unit and logs timeout/arbitration failures.

State and persistence: persistent state is small: bus frequency, hardware base, clocks managed by devm, adapter, and completion. Transfer state is stored in `msgs`, `msg_idx`, `msg_buf`, `unprocessed`, `state`, `read`, `use_pio`, and `status`. Hardware may be reset when arbitration, bus error, or timeout is observed. Bus line state is sampled through `IBMR` for recovery.

Dependencies and integration points: integrates with OF compatible `spacemit,k1-i2c`, platform resources, reset controls, two named clocks `func` and `bus`, readl polling helpers, completions, and I2C atomic transfer API.

Risks: interrupt and PIO paths share the same state machine but different completion semantics. Last-byte STOP/NAK detection is subtle, especially reads where `ACKNAK` is set for the final byte. `spacemit_i2c_wait_pio_xfer()` returns synthetic nonzero success rather than remaining jiffies. Bus recovery toggles reset cycles up to nine times and warns if SDA stays low. The glitch-fix disable in `IRCR` is required for restart behavior.

Test signals: normal and atomic transfers, read/write single-byte and multi-byte messages, repeated starts, STOP on final message only, no SMBus quick advertised, timeout path with bus reset, arbitration lost mapping to `-EAGAIN`, NACK mapping to `-ENXIO`, busy-bus wait and recovery, clock-frequency clamping, and probe with absent optional reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-k1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-keba.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-keba.c

Purpose: implements an auxiliary-bus I2C adapter for the KEBA FPGA I2C controller IP core. It supports a hardware `IN_USE` semaphore for sharing with non-Linux processors, direct SCL/SDA bus recovery when available, bytewise fallback recovery, and registration of known board devices supplied by the parent KEBA auxiliary device.

Important APIs, types, and functions: `struct ki2c` stores the KEBA auxiliary device wrapper, mapped register base, adapter, and client list. `ki2c_xfer()` is the algorithm hook. Important helpers handle hardware semaphore lock/unlock, wait for transfer complete/ACK cycles, direct-control capability, bitwise and bytewise bus reset, address/start/repeated-start/stop, byte read/write, and child-device registration.

Control flow: probe allocates state and client array, maps the auxiliary IO resource, initializes the adapter, enables the controller, resets the bus, registers the adapter, then scans/registers known devices from `keba_i2c_auxdev->info`. A transfer locks the hardware semaphore, sends START for the first message or repeated START for later read messages, performs byte-wise read or write, sends STOP, then unlocks the semaphore.

State and persistence: persistent software state includes the registered adapter and array of scanned `i2c_client` pointers for cleanup. Hardware persistence includes controller enable, direct-control line state, and the hardware semaphore. The driver explicitly disables the controller on probe failure and remove.

Dependencies and integration points: integrates with KEBA MFD/auxiliary bus types from `linux/misc/keba.h`, MMIO register access, devm resource mapping, `i2c_new_scanned_device`, HWMON class devices, and the I2C core.

Risks: repeated-start write is explicitly unsupported and returns `-EINVAL`, so combined write-write sequences cannot work. The bytewise recovery fallback may write an extra `0xff` to EEPROM-like devices; the comment recommends bitwise recovery where direct control exists. The hardware semaphore may block for up to ten seconds. ACK status maps to `-EIO` rather than `-ENXIO`, which affects clients expecting address-specific errors.

Test signals: auxiliary probe/remove, bus reset with and without direct-control capability, SCL stuck-low and SDA stuck-low recovery failures, hardware semaphore contention, read zero-length and one-byte paths, read final-byte NACK timing, write ACK failure, repeated-start read success, repeated-start write rejection, child device scanning/unregistering, and controller disable on failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-keba.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-kempld.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-kempld.c

Purpose: implements the Kontron KEM PLD I2C bus driver. It is a polling state-machine adapter built on the parent KEMPLD MFD register access and mutex, with optional GPIO I2C muxing, configurable bus frequency, 10-bit address support, suspend/resume handling, and preservation of pre-existing controller enable state.

Important APIs, types, and functions: `struct kempld_i2c_data` stores device, parent PLD data, adapter, current message pointer, buffer position, remaining message count, state, and `was_active`. `kempld_i2c_process()` is the central state machine. `kempld_i2c_xfer()` repeatedly calls it under the parent mutex until done or timeout. `kempld_i2c_device_init()` programs prescaler, mux config, interrupt acknowledgement, and controller enable.

Control flow: probe captures whether the controller was already enabled, initializes hardware under the PLD mutex, registers a numbered adapter using module parameter `i2c_bus` if set, and reports the selected frequency. Transfers initialize state to `STATE_INIT` and poll until the bus is free, address bytes are sent, data bytes are written/read, repeated messages are handled, STOP is emitted, or errors occur. Suspend disables the controller; resume re-runs device init.

State and persistence: software transfer state is stored in `msg`, `pos`, `nmsgs`, and `state`. Persistent configuration comes from module parameters `bus_frequency`, `i2c_bus`, and `i2c_gpio_mux`. Remove disables the controller only if it was not active before probe. Hardware prescaler and GPIO mux bits persist in the PLD until changed.

Dependencies and integration points: depends on the KEMPLD MFD APIs `kempld_read8`, `kempld_write8`, `kempld_get_mutex`, and `kempld_release_mutex`, ACPI companion propagation, platform device registration, and I2C core functionality flags including 10-bit addressing and SMBus emulation.

Risks: all register accesses require the parent mutex; missing that contract can race other KEMPLD functions. `I2C_STAT_TIP` and busy states use polling with one-second timeout. NACK during address/data transitions sends STOP and returns `-ENXIO`; arbitration lost returns `-EAGAIN`. Prescaler formulas differ by PLD spec major and clamp negative values to zero. `I2C_M_NOSTART` message handling reuses the current state and must preserve `pos` correctly.

Test signals: standard and 10-bit addressing, read/write multi-message transfers with and without `I2C_M_NOSTART`, arbitration loss, NACK, stuck busy timeout, bus-frequency clamping and prescaler values for spec major 1 and later, GPIO mux module parameter, suspend/resume reinitialization, and remove behavior when hardware was pre-enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-kempld.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-ljca.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-ljca.c

Purpose: implements the Intel La Jolla Cove Adapter USB-to-I2C auxiliary driver. It exposes LJCA firmware I2C channels as Linux I2C adapters by sending LJCA protocol commands for init, start, stop, read, and write.

Important APIs, types, and functions: `struct ljca_i2c_dev` stores the LJCA client, per-channel info, adapter, and fixed 60-byte input/output buffers. `struct ljca_i2c_rw_packet` is the packed LJCA command packet with channel id, little-endian length, and data payload. `ljca_i2c_xfer()` is the algorithm hook, using `ljca_i2c_read()` or `ljca_i2c_write()` per message.

Control flow: probe allocates state, obtains `ljca_i2c_info` platform data, initializes the LJCA channel at 400 kHz, registers the adapter with max transfer quirks, and clears ACPI dependencies if present. Each I2C message is handled independently: send START with address and direction, issue a pure read or write LJCA command, validate returned id and length, then send STOP. There is no repeated-start preservation across messages.

State and persistence: persistent state is only the LJCA client/channel metadata, adapter, and reusable packet buffers. No hardware register state is owned by this driver; LJCA firmware owns bus timing and transaction execution after `ljca_transfer`.

Dependencies and integration points: integrates with the auxiliary bus id `usb_ljca.ljca-i2c`, LJCA USB API and namespace, ACPI companion handling, I2C adapter quirks, HWMON class, and I2C core. It advertises I2C plus SMBus emulation except quick and disallows zero-length transfers.

Risks: fixed packet buffer size limits reads/writes to 57 bytes after packet header; adapter quirks enforce this. Each message emits its own STOP, so Linux combined transactions that rely on repeated start semantics are not faithfully represented. Return validation only checks response length/id, not deeper firmware status bytes. `ljca_i2c_init()` hardcodes 400 kHz.

Test signals: adapter creation for each LJCA I2C channel, read/write lengths at 1 and max 57, zero-length rejection through quirks, response id mismatch and short response handling, ACPI dependency clearing, firmware transfer errors, and multi-message client behavior where repeated start might be expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-ljca.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-lpc2k.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-lpc2k.c

Purpose: implements an interrupt-driven I2C master driver for NXP LPC2xxx/LPC178x controllers. The hardware exposes a classic I2C status-code state machine, and the driver pumps one message at a time through IRQs with support for `I2C_M_NOSTART`.

Important APIs, types, and functions: `struct lpc2k_i2c` stores MMIO base, clock, IRQ, wait queue, adapter, current message, byte index, message status, and last-message flag. `i2c_lpc2k_xfer()` is the algorithm hook. `i2c_lpc2k_pump_msg()` interprets controller status codes and drives data/address/ACK/STOP sequencing. Probe programs SCL high/low divisors based on requested bus frequency and mode duty-cycle constants.

Control flow: probe maps MMIO, gets IRQ and clock, requests IRQ, disables it until transfers, resets the controller, reads optional `clock-frequency`, writes SCL timing registers, and registers the adapter. A transfer first verifies idle status or tries `i2c_lpc2k_clear_arb()`, then processes messages sequentially. `lpc2k_process_msg()` emits START or continues `NOSTART`, enables IRQ, and waits for `msg_status` to leave `-EBUSY`. The IRQ handler checks SI and calls the pump.

State and persistence: persistent state includes programmed SCL timing and enabled controller state. Transfer state is stored in `msg`, `msg_idx`, `msg_status`, and `is_last`. IRQ is enabled only during a message and disabled when the message completes or fails. Suspend disables the clock; resume re-enables it and resets the controller.

Dependencies and integration points: integrates with OF compatible `nxp,lpc1788-i2c`, platform IRQ/MMIO, clock framework, noirq PM callbacks, wait queues, and I2C core. SMBus support is emulated by the core.

Risks: status-code sequencing is strict; clearing SI at the wrong time can stall the hardware. Read NACK status is treated as successful final read data, which is intentional. The code increments `msg_idx` in write ACK cases even when no more data is sent, so off-by-one changes are dangerous. Timeout disables IRQ but bus cleanup depends on later transfer idle checks. `I2C_M_NOSTART` is warned for zero length and only directly seeds write data.

Test signals: START and repeated START transfers, read lengths one and multiple bytes, final-byte NACK behavior, write data ACK/NACK, address NACK mapping to `-ENXIO`, arbitration lost mapping to `-EAGAIN`, bus-not-idle clear/reset path, `I2C_M_NOSTART` write continuation, timeout with disabled IRQ, clock divider programming for standard/fast/fast-plus requests, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-lpc2k.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-ls2x.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-ls2x.c

Purpose: implements the Loongson-2K and Loongson LS7A I2C controller-mode driver. It is an interrupt-completion byte driver derived from an OpenCores-like register model and supports OF and ACPI discovery.

Important APIs, types, and functions: `struct ls2x_i2c_priv` embeds the adapter, MMIO base, parsed timings, and command completion. `ls2x_i2c_xfer()` is the algorithm hook. `ls2x_i2c_adjust_bus_speed()` parses firmware/ACPI bus speed and programs low/high prescaler bytes. `ls2x_i2c_start()`, `ls2x_i2c_tx()`, `ls2x_i2c_rx()`, and `ls2x_i2c_stop()` implement byte-level transfers.

Control flow: probe maps registers, gets a shared IRQ, initializes adapter fields and completion, programs controller frequency and interrupt-enabled master mode, requests IRQ, then registers the adapter through devm. A transfer loops over messages; each message sends START and address, then reads or writes bytes using `wait_for_completion_timeout()` after command writes. STOP is emitted only after the final message.

State and persistence: persistent hardware state includes prescaler registers and control bits. Software stores firmware timings and completion. A timeout or failed STOP triggers `ls2x_i2c_init()` to reinitialize the controller. Runtime PM suspend disables interrupts and resume reinitializes the device.

Dependencies and integration points: integrates with OF compatibles `loongson,ls2k-i2c` and `loongson,ls7a-i2c`, ACPI id `LOON0004`, firmware timing helpers, runtime PM ops, platform resources, shared IRQ, and I2C core.

Risks: manual byte access is required for prescaler registers because wider writes truncate high bits. ACPI speed and firmware speed are combined with `max()`, which affects unexpected dual-source configurations. `ls2x_i2c_xfer_byte()` waits for completion without reinitializing completion for every byte; the ISR must acknowledge and complete reliably. NACK and arbitration lost are read from status after each command and map to `-ENXIO` and `-EAGAIN`.

Test signals: OF and ACPI probe, default 33 kHz fallback, standard and fast mode timings, read/write and multi-message repeated-start transfers, final STOP idle polling, timeout reinitialization, shared IRQ `IRQ_NONE` path, NACK/arbitration-lost mapping, and PM suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-ls2x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-mchp-pci1xxxx.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-mchp-pci1xxxx.c

Purpose: implements the Microchip PCI1xxxx PCIe switch I2C/SMBus adapter. It uses the device's SMBus master core and 128-byte buffer/DMA engine to perform I2C transfers, supports SMBus block-read handling, wake-capable SMBALERT, configurable bus speed from a protected GPR, and PCI PM integration.

Important APIs, types, and functions: `struct pci1xxxx_i2c` stores the adapter, MMIO base, completion, transfer-in-progress flag, selected frequency, and flags for direct mode, STOP, and SMBus block read. `pci1xxxx_i2c_xfer()` is the algorithm hook. Key helpers configure system lock, core enable, pad control, timing registers, high/low-level interrupts, transfer direction, buffer contents, START/STOP, counts, auto-start-read, and DMA run/proceed.

Control flow: probe enables the PCI function, maps BAR0, initializes the SMBus core, installs a devm shutdown action, allocates one IRQ vector, requests the IRQ, initializes adapter metadata, and registers it. Each transfer marks progress, iterates messages, derives the 8-bit address, sets STOP and SMB block flags, and calls read or write. Reads and writes split transfers into chunks of up to 128 bytes, program buffer/count registers, arm DMA termination interrupts, start DMA, wait up to one second for completion, inspect completion status for NAK, copy data from/to MMIO buffer, then mask interrupts and clear flags.

State and persistence: persistent hardware state includes core timing registers, pad controls, pull-up for SMBALERT, direct-buffer mode, and interrupt masks. `i2c_xfer_in_progress` persists across suspend so suspend waits for active transfers. `freq` is selected from `SMB_GPR_REG` under `SMB_GPR_LOCK_REG`, defaulting to fast mode if lock is unavailable.

Dependencies and integration points: integrates with PCI ids for EFAR devices `0xA003` through `0xA043`, PCI managed MMIO/IRQ APIs, I2C adapter quirks, I2C SMBus helper definitions, PM sleep ops, PCI wake from D3, and high/low-level interrupt status registers in the device.

Risks: several control/status registers have write-one-to-clear semantics, so read-modify-write is explicitly avoided for core control but still used for other registers. Chunked reads require different setup for the first chunk versus subsequent chunks and special FW_ACK handling so only the final read NACKs. NAK currently maps to `-ETIMEDOUT` in read/write paths. Suspend busy-waits in 20 ms sleeps until transfer completion. System lock failure silently forces default fast-mode programming.

Test signals: PCI probe on all ids, speed selection values 0/1/2/3 and lock failure, standard/fast/fast-plus timing programming, writes and reads shorter/equal/longer than 128 bytes, SMBus block read with length byte copyout, no-zero-length quirk, NAK and DMA timeout paths with core reinit, IRQ ack for buffer master and SMBALERT, suspend during active transfer, wake interrupt enable/disable, and shutdown disabling pads/core.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-mchp-pci1xxxx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-meson.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-meson.c

Purpose: implements the Amlogic Meson I2C bus driver for Meson6, GXBB, and AXG-style controllers. The hardware executes token lists with up to eight data bytes per batch, and the driver supports interrupt and atomic polling transfers.

Important APIs, types, and functions: `struct meson_i2c` stores adapter, device, MMIO registers, clock, current message, transfer state, last-message flag, byte count/position, error, spinlock, completion, two token registers, and SoC data. `struct meson_i2c_data` provides the SoC-specific clock divider function. `meson_i2c_xfer()` and `meson_i2c_xfer_atomic()` share `meson_i2c_xfer_messages()`. Token helpers build START, address, DATA, DATA_LAST, and STOP sequences.

Control flow: probe parses I2C timings, maps registers, requests IRQ, enables the clock, clears the START bit, disables input filters, programs the SoC-specific clock divider, and registers the adapter. For each message, transfer setup resets tokens, configures ACK-ignore from `I2C_M_IGNORE_NAK`, optionally emits START/address unless `I2C_M_NOSTART`, prepares a token batch and write data, sets START, then waits by completion or atomic polling. The IRQ clears START, checks error/status, copies read data, advances position, either completes or queues the next token batch and restarts.

State and persistence: persistent state includes clock divider/filter register configuration and SoC clock algorithm. Per-transfer state is protected by `lock` because timeouts can race with late IRQs. `tokens[0]`, `tokens[1]`, `num_tokens`, `pos`, `count`, `state`, and `error` persist across batched IRQ completions for a message.

Dependencies and integration points: integrates with OF compatibles `amlogic,meson6-i2c`, `amlogic,meson-gxbb-i2c`, and `amlogic,meson-axg-i2c`, platform MMIO/IRQ, clock framework, firmware timing parsing, I2C atomic transfer API, and SMBus emulation through the I2C core.

Risks: token batches are limited to eight data bytes, so batching and restart logic must preserve position exactly. The controller auto-generates STOP on NAK when ACK-ignore is not set; the driver maps this to `-ENXIO`. Atomic mode only calls transfer completion once after polling the hardware status bit, so multi-batch atomic messages are risky unless the hardware has finished the prepared batch and state is updated correctly. Clock divider formulas subtract filter delay and clamp low frequencies to 12-bit fields.

Test signals: Meson6 and GXBB/AXG clock divider paths, read/write messages of 0/1/8/9+ bytes, multi-message transfers with STOP only on last message, `I2C_M_NOSTART`, `I2C_M_IGNORE_NAK`, interrupt and atomic paths, timeout with late IRQ race, NAK error mapping, filter disabled state, and remove clock disable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-meson.c -->
