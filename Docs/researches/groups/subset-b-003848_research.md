# Research: subset-b-003848

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-at91-core.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-at91-core.c

## Purpose
Shared platform-driver core for the Atmel/Microchip AT91 TWI controller. It owns resource discovery, compatible-to-capability selection, adapter registration, runtime/system PM, and mode dispatch between the master implementation in `i2c-at91-master.c` and optional slave implementation in `i2c-at91-slave.c`.

## APIs, Control Flow, and State
Important shared helpers are `at91_twi_read()`, `at91_twi_write()`, `at91_disable_twi_interrupts()`, `at91_twi_irq_save()`, `at91_twi_irq_restore()`, and `at91_init_twi_bus()`. `at91_twi_probe()` allocates `struct at91_twi_dev`, maps MMIO, gets IRQ and clock, fills `struct i2c_adapter`, detects slave mode with `i2c_detect_slave_mode()`, calls `at91_twi_probe_master()` or `at91_twi_probe_slave()`, resets/initializes hardware, enables runtime autosuspend, and registers a numbered adapter. Device-specific `struct at91_twi_pdata` entries encode clock divider limits and feature flags for UNRE, alternative command mode, HOLD, digital/analog filters, FIFO-related behavior, and the CLEAR bus recovery command.

## Dependencies and Integration
Integrates with platform bus, OF match tables, legacy platform IDs, Linux I2C core, clk, pinctrl sleep/default states, and runtime PM. Its exported state is in `struct at91_twi_dev`, which is consumed by the master/slave compilation units through `i2c-at91.h`.

## Risks and Test Signals
Risk centers on SoC capability mismatches, PM sequencing, and wrong master/slave dispatch. Test with DT compatibles across AT91/SAMA5/SAM9x60 variants, runtime suspend/resume, system suspend_noirq/resume_noirq, missing clocks/IRQs, slave-mode DT detection, and adapter add/remove. Failures show as incorrect bus speed/features, lost register state after resume, or probe deferral/resource leaks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-at91-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-at91-master.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-at91-master.c

## Purpose
Master-mode AT91 TWI implementation. It calculates bus timing, drives CPU and DMA transfers, handles RX/TX interrupts, supports limited repeated-start transactions through the internal address feature, configures optional FIFO/filter/alternative-command features, and wires bus recovery.

## APIs, Control Flow, and State
`at91_twi_probe_master()` installs `atmel_twi_interrupt()`, optionally configures DMA channels, reads `atmel,fifo-size`, filter properties, computes `twi_cwgr_reg`, and assigns `at91_twi_algorithm` plus quirks. `at91_twi_xfer()` accepts normal I2C messages, folds a two-message write-then-read/write sequence into `IADR`/`IADRSZ`, enables alternative command mode for short transfers, chooses DMA-safe buffers, and calls `at91_do_twi_transfer()`. The transfer routine clears stale status, resets FIFO thresholds, starts quick/read/write paths, waits on `cmd_complete`, maps hardware status to errno, cleans DMA, unlocks/flushes TX, and invokes `i2c_recover_bus()` on errors. ISR ordering intentionally drains RXRDY before TXCOMP/NACK to avoid stale RHR data; NACK/TXCOMP complete the transaction, while TXRDY feeds CPU writes. DMA callbacks unmap buffers and defer TXCOMP/STOP sequencing.

## Dependencies and Integration
Depends on DMAEngine, DMA mapping, I2C core quirks, runtime PM from the core file, GPIO/pinctrl recovery support, firmware timing parsing, and AT91 register definitions. It advertises `I2C_FUNC_I2C`, SMBus emulation, and SMBus block read.

## Risks and Test Signals
Highest risk is hardware-ordering drift around TXCOMP/NACK/LOCK, DMA callback races, last-byte read STOP timing, SMBus block length aborts, and CLEAR-vs-GPIO recovery selection. Test CPU and DMA reads/writes around the 8-byte threshold, short alt-command transfers, FIFO aligned/unaligned buffers, EEPROM NACKs, zero-length quick commands, combined messages with 1-3 byte internal addresses, stuck SDA recovery, filters from DT timings, and suspend/resume with active autosuspend.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-at91-master.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-at91-slave.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-at91-slave.c

## Purpose
Optional experimental AT91 slave-mode support, compiled when `CONFIG_I2C_AT91_SLAVE_EXPERIMENTAL` is enabled. It presents the AT91 TWI controller as an I2C slave endpoint and translates hardware slave events into Linux `i2c_slave_event()` callbacks.

## APIs, Control Flow, and State
`at91_twi_probe_slave()` requests the IRQ and installs `at91_twi_algorithm_slave`. `at91_reg_slave()` rejects duplicate or 10-bit clients, runtime-resumes the controller to keep the TWI clock alive, stores the `struct i2c_client`, programs `SMR`, reinitializes the bus, and enables `SVACC`. `atmel_twi_interrupt_slave()` handles address match, read/write direction, byte transmit/receive readiness, and end-of-slave-access, emitting `READ_REQUESTED`, `READ_PROCESSED`, `WRITE_REQUESTED`, `WRITE_RECEIVED`, and `STOP`. `at91_unreg_slave()` clears `slave`/`smr`, reinitializes hardware, and releases the runtime PM reference.

## Dependencies and Integration
Shares register access and device state from `i2c-at91-core.c`/`.h`. Integrates with the I2C slave framework and runtime PM; the core file decides whether to call this probe path through `i2c_detect_slave_mode()`.

## Risks and Test Signals
Risks include missing PM puts, stale `SMR` after unregister, incorrect interrupt mask transitions between `SVACC`, `TXRDY`, `RXRDY`, and `EOSACC`, and backend callbacks reentering unexpectedly. Test slave EEPROM-like backends, master reads/writes, repeated STARTs, STOP handling, unregister while idle, runtime suspend prevention while registered, and 10-bit rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-at91-slave.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-at91.h -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-at91.h

## Purpose
Shared private header for the AT91 TWI driver family. It defines register offsets, bitfields, feature constants, and the private state structures used by the AT91 core, master, and optional slave files.

## APIs, Control Flow, and State
Key constants include `AT91_I2C_TIMEOUT`, `AT91_I2C_DMA_THRESHOLD`, `AUTOSUSPEND_TIMEOUT`, and `AT91_I2C_MAX_ALT_CMD_DATA_SIZE`. The register map covers control, mode, status, interrupt, FIFO, filter, alternative command, and version registers. `struct at91_twi_pdata` captures per-SoC capability flags; `struct at91_twi_dma` tracks DMA channels, SG entries, mapping direction, and in-progress state; `struct at91_twi_dev` holds MMIO, completion, clock, adapter, current buffer/message, IRQ masks/status, DMA, FIFO/filter settings, recovery info, and optional slave fields.

## Dependencies and Integration
Includes Linux clk, completion, DMA, I2C, and platform-device types. It declares the shared core helpers plus `at91_twi_probe_master()`/`at91_init_twi_bus_master()` and conditional slave prototypes or stubs.

## Risks and Test Signals
Risks are contract drift between compilation units, wrong bit masks for newer SoCs, and conditional slave fields being used outside the config guard. Test by building with and without `CONFIG_I2C_AT91_SLAVE_EXPERIMENTAL`, with DMA/FIFO-capable DTs, and by checking sparse/build warnings around register bit use and function prototypes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-at91.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-au1550.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-au1550.c

## Purpose
PIO-based I2C/SMBus adapter for the Alchemy Au1550 PSC SMBus mode. Despite hardware naming, the driver performs raw I2C-style byte sequencing and lets the I2C core emulate most SMBus operations.

## APIs, Control Flow, and State
`struct i2c_au1550_data` stores the PSC MMIO base, transfer timeout, and adapter. Low-level `WR()`/`RD()` accessors use raw MMIO and write barriers. Transfer control uses polling helpers `wait_xfer_done()`, `wait_ack()`, and `wait_controller_done()`. `do_address()` clears events/FIFOs, emits the 7-bit address plus direction, and handles zero-length quick transfers with STOP. `i2c_read()` clocks reads by writing dummy bytes and STOP on the last byte; `i2c_write()` sends bytes and marks the final one with STOP. `au1550_xfer()` enables PSC control, iterates messages, and suspends the controller afterward. Probe maps the PSC, sets fixed timeout/timing through `i2c_au1550_setup()`, then registers a numbered adapter.

## Dependencies and Integration
Depends on MIPS Alchemy PSC register definitions, platform resources, and Linux I2C core. PM sleep hooks disable and reinitialize the PSC across suspend/resume.

## Risks and Test Signals
Risks are polling timeouts, FIFO/event clear races, fixed protocol timing assumptions, lack of interrupts, and poor error discrimination because ACK/data/arbitration events collapse to `-EIO` or timeout. Test reads, writes, SMBus emulation, zero-length commands, suspend/resume, PSC clock/routing setup by board code, and stuck/NAK targets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-au1550.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-axxia.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-axxia.c

## Purpose
I2C master and slave driver for the LSI Axxia API2C controller. It supports 7/10-bit addressing, SMBus block reads, combined write-read sequence mode, generic SCL recovery, and controller-backed slave operation.

## APIs, Control Flow, and State
`struct axxia_i2c_dev` tracks MMIO, current TX/RX messages, FIFO counters, completion, clock, bus rate, slave client, and IRQ. `axxia_i2c_init()` resets the block, enables master mode, computes SCL high/low/setup/hold/filter timing from the input clock and `clock-frequency`, configures timeout counters, and masks interrupts. Master transfers use either `axxia_i2c_xfer_seq()` for exactly one short write followed by read to the same address, or `axxia_i2c_xfer_msg()` for individual auto/manual commands. ISR logic services RX/TX FIFOs, maps arbitration/NACK/invalid/timeout status to errno, and completes the wait. Slave registration enables slave mode/address decode and slave interrupts; slave ISR paths convert FIFO/start/stop/read events into `i2c_slave_event()` callbacks.

## Dependencies and Integration
Integrates with OF compatible `lsi,api2c`, clk, platform IRQ/MMIO, I2C adapter quirks with 255-byte limits, and `i2c_generic_scl_recovery` via controller SCL/SDA monitor/control bits.

## Risks and Test Signals
Risks include sequence-mode NAK timing, busy command recovery, SMBus block length validation, manual-mode timeout handling, slave/master interrupt sharing, and reset side effects during recovery. Test single and combined transfers, lengths near 255 and FIFO size 8, 10-bit targets, invalid SMBus block lengths, arbitration loss, clock stretching timeouts, bus recovery, slave write/read/stop flows, and remove ordering around clock disable and adapter deletion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-axxia.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-bcm-iproc.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-bcm-iproc.c

## Purpose
Broadcom iProc SMBus/I2C controller driver with master support, optional slave support, IRQ or polling completion, NIC indirect-access handling, and sleep PM reinitialization.

## APIs, Control Flow, and State
`struct bcm_iproc_i2c_dev` stores direct or IDM-mediated MMIO, adapter, speed, completion, current message, FIFO counters, slave state, tasklet, and interrupt masks. `iproc_i2c_rd_reg()`/`wr_reg()` optionally serialize indirect NIC access through `idm_lock` and `ape_addr_mask`. Master flow initializes/reset FIFOs with `bcm_iproc_i2c_init()`, formats address/data into TX FIFO in `bcm_iproc_i2c_xfer_internal()`, supports a two-message write-then-read process call, dynamically sets RX thresholds, and waits in IRQ or polling mode through `bcm_iproc_i2c_xfer_wait()`. Status codes map lost arbitration, NACK, timeout, underrun, and RX full to Linux errno. Slave flow programs address slot 3, handles RX FIFO data in a tasklet, and services TX underruns to feed read data to an external master.

## Dependencies and Integration
Uses OF compatibles `brcm,iproc-i2c` and `brcm,iproc-nic-i2c`, platform IRQ/MMIO, I2C adapter quirks, tasklets, completions, and PM suspend_late/resume_early. NIC type disables slave callbacks on the shared algorithm.

## Risks and Test Signals
Risks include global mutation of the algorithm callbacks for NIC instances, interrupt disable/synchronize ordering, long 50-second transfer timeout masking hangs, slave tasklet races with unregister, threshold changes for large reads, and indirect register serialization. Test IRQ and poll mode, combined transfers, reads over the 50-byte threshold and 255-byte max, no-IRQ fallback, NIC DT resources, slave write/read/write-read cases, suspend/resume, and removal with pending interrupts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-bcm-iproc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-bcm-kona.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-bcm-kona.c

## Purpose
Broadcom Kona BSC I2C master driver. It supports standard, fast, fast-mode-plus, and high-speed timing presets, FIFO-based reads/writes, 10-bit addressing, and `I2C_M_NOSTART`.

## APIs, Control Flow, and State
`struct bcm_kona_i2c_dev` holds MMIO, IRQ, external clock, adapter, completion, and selected timing tables. Command helpers issue START/RESTART/STOP/NOACTION and wait on the shared ISR completion. Reads are chunked through the 64-byte RX FIFO with last-byte NAK control; writes fill the 64-byte TX FIFO and temporarily disable the IRQ while loading a FIFO batch. `bcm_kona_i2c_xfer()` enables the external and internal clocks, enables pad output, sends START, optionally performs the high-speed controller-code handshake, loops messages with restarts and address phases, transfers data, sends STOP, restores standard timing, disables pad output, and drops clocks. Probe selects timing from `clock-frequency`, configures autosense, FIFOs, IRQ, and registers the adapter.

## Dependencies and Integration
Depends on clk rate changes between 13 MHz and 104 MHz, platform IRQ/MMIO, OF compatible `brcm,kona-i2c`, and the I2C core functionality/quirk surface.

## Risks and Test Signals
Risks are high-speed handshake failure, IRQ disable while filling FIFO, NAK interpretation, pad/clock cleanup on error paths, and strict accepted bus frequencies. Test 100 kHz/400 kHz/1 MHz/3.4 MHz modes, 10-bit reads, multi-message restarts and `NOSTART`, long FIFO-chunked reads/writes, NAK on address/data, timeout paths, and repeated probe/remove with shared IRQs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-bcm-kona.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-bcm2835.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-bcm2835.c

## Purpose
BCM2835/BCM2711 I2C controller driver for Raspberry Pi class hardware. It implements interrupt-driven FIFO transfers and a local clock-divider provider used to program the bus rate.

## APIs, Control Flow, and State
`struct bcm2835_i2c_dev` tracks registers, IRQ, adapter, completion, current messages, divider clock, error bits, and active buffer pointers. The embedded `clk_bcm2835_i2c` clock ops compute even dividers, program `DIV` and falling/rising edge delays, and expose the derived bus rate. Transfer flow forbids read messages except as the final message, starts each message with address/DLEN/control bits, feeds TX FIFO on TXW, drains RX FIFO on RXR/DONE, and uses TXW without prefill to trigger repeated starts for write-then-read sequences. The ISR distinguishes ERR/CLKT, DONE length mismatches, TX/RX FIFO service, clears status/control on completion, and wakes `bcm2835_i2c_xfer()`.

## Dependencies and Integration
Integrates with clk provider/clkdev, OF match data for BCM2835 clock-stretch quirk, platform resources, and I2C core. Probe sets an exclusive bus clock rate, disables hardware clock-stretch timeout, registers a shared IRQ, and adds the adapter.

## Risks and Test Signals
Risks include repeated-start timing, FIFO length mismatch detection, clearing the controller after read errors, exclusive clock-rate lifetime, and the BCM2835 no-clock-stretch limitation. Test write, read, write-then-read register transactions, unsupported read-before-last sequences, NACK, clock timeout, transfer length mismatches, BCM2711 vs BCM2835 compatibles, and probe/remove clock/IRQ cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-bcm2835.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-brcmstb.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-brcmstb.c

## Purpose
Broadcom set-top/peripheral BSC I2C master driver. It supports endian-aware MMIO, interrupt or polling completion, atomic transfers, 1-byte or 4-byte data register layouts, `NOSTART`, 10-bit addressing, and BCM2711 HDMI auto-I2C release.

## APIs, Control Flow, and State
`struct brcmstb_i2c_dev` stores MMIO, cached `struct bsc_regs`, adapter, completion, configured bus frequency, data register size, and atomic flag. `brcmstb_i2c_xfer()` chunks messages by the data-register window (`N_DATA_REGS * data_regsz`), computes START/STOP/RESTART/NOSTART conditions, writes the address, and calls `brcmstb_i2c_xfer_bsc_data()` for each chunk. Data packing/unpacking differs for 1-byte peripheral cores and 4-byte STB cores. `brcmstb_send_i2c_cmd()` enables BSC interrupts, starts the transfer, waits by IRQ or polling, checks NOACK unless ignored, then clears count/enable. `xfer_atomic()` disables the IRQ and forces polling. Probe handles optional IRQ fallback, clock-frequency selection from a fixed table, compatible-specific data width, and optional `auto-i2c` release for HDMI.

## Dependencies and Integration
Uses OF compatibles `brcm,brcmstb-i2c`, `brcm,brcmper-i2c`, and `brcm,bcm2711-hdmi-i2c`, platform MMIO/IRQ, I2C core atomic xfer hooks, and PM sleep adapter suspend markers.

## Risks and Test Signals
Risks include cached register state diverging from hardware, wrong endian/data-width packing, polling fallback behavior, `IGNORE_NAK` command selection, and chunk boundary START/STOP errors. Test 1-byte and 4-byte cores, interrupt and polling mode, atomic transfers from late contexts, long reads/writes across chunks, `NOSTART` sequences, 10-bit read setup, unsupported clock-frequency fallback, BCM2711 HDMI release, and suspend/resume register restoration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-brcmstb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-cadence.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-cadence.c

## Purpose
Cadence/Xilinx I2C controller driver with master, atomic master, optional slave mode, runtime PM, bus recovery, reset control, and input-clock rate change handling.

## APIs, Control Flow, and State
`struct cdns_i2c` holds MMIO, adapter, current message, completions, send/receive counters, clock/reset handles, notifier, cached control/divider state, recovery info, FIFO depth, detected transfer-size limit, atomic flag, and optional slave role state. Master transfer uses `cdns_i2c_master_common_xfer()` to wait for bus idle, set HOLD for repeated starts, reject receive-then-more sequences on broken HOLD hardware, and process each message through `cdns_i2c_process_msg()`. `cdns_i2c_msend()` and `cdns_i2c_mrecv()` program direction, FIFO, transfer-size, HOLD, address, and interrupts; large receives use a transfer-size/HOLD workaround so the controller does not prematurely NACK. Atomic variants poll ISR/status rather than sleeping. Slave mode switches controller roles, sets the slave address, and maps DATA/COMP/NACK/overflow interrupts to I2C slave callbacks.

## Dependencies and Integration
Uses OF compatibles `cdns,i2c-r1p10` and `cdns,i2c-r1p14`, clk, reset, runtime PM autosuspend, pinctrl bus recovery, Linux I2C master/slave APIs, clock notifiers, and optional `fifo-depth`/`clock-frequency` properties.

## Risks and Test Signals
Risks are concentrated in HOLD-bit timing, large receive transfer-size rollover, clock-rate notifier updates while active, slave/master role switching, and PM/reset cleanup. Test r1p10 broken-HOLD paths, repeated starts, large reads over FIFO and transfer-size boundaries, SMBus block reads with PEC length, arbitration loss/retry, atomic transfers, bus recovery on busy bus, slave send/receive/stop, runtime/system suspend, invalid clock rates, and clock rate change abort/post-change cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-cadence.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-cbus-gpio.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-cbus-gpio.c

## Purpose
GPIO bit-banged CBUS adapter for Nokia Internet Tablets, exposed through the I2C SMBus word-data API. CBUS is not normal I2C; this driver maps its 3-bit device, 1-bit direction, 5-bit register, and 16-bit data protocol onto SMBus word read/write operations.

## APIs, Control Flow, and State
`struct cbus_host` holds a spinlock, device, and three GPIO descriptors (`clk`, `dat`, `sel`). Bit helpers drive/read GPIOs without delays. `cbus_transfer()` disables local interrupts via `spin_lock_irqsave()`, asserts SEL, switches DAT direction, shifts address/direction/register and optional write data, reads 16-bit words for reads, then deasserts SEL and clocks an end pulse. `cbus_i2c_smbus_xfer()` accepts only `I2C_SMBUS_WORD_DATA` and passes the SMBus address/command/data to CBUS. Probe requires exactly three unnamed GPIOs, sets consumer names, fills a numbered HWMON-class adapter, and registers it.

## Dependencies and Integration
Depends on gpiolib descriptor APIs, platform/OF binding `i2c-cbus-gpio`, Linux I2C SMBus xfer hooks, and atomic SMBus support by reusing the same transfer function.

## Risks and Test Signals
Risks include timing sensitivity from no explicit udelays, interrupt masking duration, GPIO direction failures leaving SEL asserted, and protocol mismatch if non-Nokia CBUS variants differ. Test word reads/writes to known CBUS devices, atomic SMBus users, GPIO polarity/order from DT, error paths during DAT direction change, concurrent transfers, and remove after adapter registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-cbus-gpio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-ccgx-ucsi.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-ccgx-ucsi.c

## Purpose
Small helper module that instantiates a Cypress CCGx UCSI Type-C controller as an I2C client on an existing adapter. It centralizes board-info construction for consumers that discover the controller indirectly.

## APIs, Control Flow, and State
The exported API is `i2c_new_ccgx_ucsi(struct i2c_adapter *adapter, int irq, const struct software_node *swnode)`. It creates a local `struct i2c_board_info`, sets `type` to `ccgx-ucsi`, address to `0x08`, propagates IRQ and software node, and calls `i2c_new_client_device()`. There is no persistent module-owned state beyond the created client owned by the I2C core/consumer.

## Dependencies and Integration
Depends on the I2C core, exported GPL symbol use, and the matching `i2c-ccgx-ucsi.h` declaration. Downstream integration is with the `ccgx-ucsi` client driver and platform-specific code that supplies an adapter, IRQ, and software node.

## Risks and Test Signals
Risks are fixed address/type drift, caller lifetime of `swnode`, duplicate client creation on the same adapter, and IRQ propagation mistakes. Test helper callers by confirming the `ccgx-ucsi` device probes at `0x08`, interrupt delivery works, software-node properties are visible, and duplicate/failed adapter cases unwind at the caller.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-ccgx-ucsi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-ccgx-ucsi.h -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-ccgx-ucsi.h

## Purpose
Public internal declaration for the Cypress CCGx UCSI I2C-client instantiation helper.

## APIs, Control Flow, and State
The header forward-declares `struct i2c_adapter`, `struct i2c_client`, and `struct software_node`, then declares `i2c_new_ccgx_ucsi()`. Include guards prevent duplicate declarations. It owns no state and contains no inline behavior.

## Dependencies and Integration
Used by code that wants to create the CCGx UCSI client without depending on full I2C or software-node header inclusion in its own interface. The implementation is in `i2c-ccgx-ucsi.c`.

## Risks and Test Signals
Risks are limited to prototype drift and missing includes in callers. Test with compile coverage of all helper users and module builds where `i2c-ccgx-ucsi.c` is enabled as built-in or module.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-ccgx-ucsi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-cgbc.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-cgbc.c

## Purpose
I2C bus driver for Congatec Board Controller child buses. It tunnels I2C transactions through the parent MFD command interface and exposes separate general-purpose and power-management adapters.

## APIs, Control Flow, and State
`struct cgbc_i2c_data` stores parent `cgbc_device_data`, adapter, active message pointer/count/position, and a small transfer state machine. Frequency helpers encode/decode controller speed registers and size the read polling timeout. `cgbc_i2c_xfer_to_cmd()` builds command packets with START/STOP, read length, last-ACK flag, address, and write payload. `cgbc_i2c_xfer_msg()` checks board-controller status, chunks reads to 31 bytes and writes to 32 bytes, starts new messages when needed, polls read completion, fetches read data through `CGBC_I2C_CMD_DATA`, and advances state. `cgbc_i2c_xfer()` loops until done, error, or one-second inactivity timeout. Probe clones one of two static adapter templates based on platform ID, configures 100 kHz, and registers a numbered adapter.

## Dependencies and Integration
Depends on the Congatec MFD `cgbc_command()` transport, platform child IDs, I2C core, and `read_poll_timeout()`. It advertises I2C plus SMBus emulation except quick command.

## Risks and Test Signals
Risks include command-packet length encoding, START/STOP across chunk and message boundaries, timeout sizing from effective bus frequency, no 10-bit support despite raw I2C function claim, and parent-command failures. Test both bus IDs, read/write lengths at 31/32 and larger, write-then-read transactions, busy status retry, invalid speed fallback, parent MFD error injection, and adapter removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-cgbc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-cht-wc.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-cht-wc.c

## Purpose
Intel Cherry Trail Whiskey Cove PMIC external-charger I2C adapter. It exposes the PMIC's charger sideband registers as a one-client SMBus byte-data adapter and instantiates known charger devices with board-specific software-node/platform data.

## APIs, Control Flow, and State
`struct cht_wc_i2c_adap` holds the adapter, wait queue, IRQ chip/domain, adapter and irqchip mutexes, PMIC regmap, client pointer/IRQ, masks, read data, and completion/error flags. `cht_wc_i2c_adap_smbus_xfer()` programs client address, write data, register offset, and read/write control registers, then waits up to 30 ms for the threaded PMIC IRQ handler; if delayed by serialized GPIO IRQs it manually polls the handler. The handler reads/acks `EXTCHGRIRQ`, captures read data before acknowledging read IRQs, wakes transfers, and forwards client IRQs through `generic_handle_irq_safe()`. Custom lock ops use nested bus-lock depth 1. Probe creates an IRQ domain for the charger client, requests the threaded IRQ, registers the adapter, and instantiates a model-specific bq24190/bq25890/bq25892 charger.

## Dependencies and Integration
Depends on Intel SoC PMIC MFD regmap/model data, IRQ domains/chips, I2C SMBus byte-data API, charger platform-data headers, software nodes, and ACPI/platform enumeration.

## Risks and Test Signals
Risks include shared IRQ deadlocks, mask synchronization, manual timeout polling races, nested bus-lock assumptions, board-info mutation of IRQ fields, and model-specific charger properties. Test byte read/write success and NACK paths, delayed IRQ handling, client charger IRQ delivery, suspend/resume with charger present, each known `cht_wc_model`, unknown model fallback, remove cleanup of client/adapter/domain, and lockdep with charger drivers performing transfers from IRQ context.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-cht-wc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-cp2615.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-cp2615.c

## Purpose
USB-backed I2C adapter for the Silicon Labs CP2615 Digital Audio Bridge. It wraps I2C transfers in the device's 64-byte I/O Protocol messages over bulk endpoints.

## APIs, Control Flow, and State
Packed IOP structures describe generic messages, accessory info, I2C transfer requests, and transfer results. `cp2615_init_iop_msg()` builds the preamble/length/message header, and `cp2615_init_i2c_msg()` wraps I2C requests. `cp2615_check_status()` maps device status to Linux errno. `cp2615_i2c_send()` sends a transfer over endpoint `0x02`; `cp2615_i2c_recv()` reads endpoint `0x82`, validates result type and tag, checks status, and copies read data. `cp2615_check_iop()` probes accessory info and logs part revision. `cp2615_i2c_xfer()` serializes each Linux I2C message as either read or write with fixed tag `0xdd`. Probe selects interface 1 altsetting 2, validates IOP, names the adapter from the USB serial, applies quirks, and registers the adapter.

## Dependencies and Integration
Depends on USB core, Linux I2C core, CP2615 VID/PID/interface matching, and adapter quirks limiting reads/writes to `MAX_I2C_SIZE` with no zero-length and no repeated START.

## Risks and Test Signals
Risks include no timeout argument to `usb_bulk_msg()`, fixed tag reuse, short/malformed USB response validation, endpoint/altsetting assumptions, serial-number requirement, and protocol limitation mismatch for combined transfers. Test probe on A01/A02/unknown parts, reads and writes near 54-byte limit, NACK/busy/timeout/status mapping, unplug during transfer, missing serial, unsupported repeated-start clients, and adapter removal during active USB I/O.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-cp2615.c -->
