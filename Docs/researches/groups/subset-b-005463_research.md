# subset-b-005463 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/stm32-usart.c -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/stm32-usart.c

## Purpose
This is the STM32 USART platform serial driver. It adapts three STM32 register layouts, F4, F7, and H7, to the Linux `uart_port`/`uart_driver` framework and supports normal tty operation, console and earlycon output, RS485, modem-control GPIOs, DMA-assisted RX/TX, runtime PM, system sleep, and H7 wake-from-low-power behavior.

## Important APIs, Types, And Functions
The driver is centered on the static `stm32_ports[STM32_MAX_PORTS]` array declared in the companion header and the `stm32_usart_driver` registered from `stm32_usart_init()`. `stm32f4_info`, `stm32f7_info`, and `stm32h7_info` provide register offsets and feature flags consumed through `struct stm32_usart_info`.

The `uart_ops` implementation is `stm32_uart_ops`: `startup`, `shutdown`, `set_termios`, `start_tx`, `stop_tx`, `stop_rx`, throttle/unthrottle, `pm`, console poll hooks, and mctrl hooks. Probe flow is `stm32_usart_serial_probe()` -> `stm32_usart_of_get_port()` -> DMA channel discovery -> `stm32_usart_init_port()` -> optional DMA buffer setup -> `uart_add_one_port()`. Remove reverses runtime PM, uart registration, DMA buffers/channels, wake IRQ, and clock enable state.

RX/TX data movement has separate PIO and DMA helpers. `stm32_usart_receive_chars_pio()` reads `RDR`, handles error bits, sysrq, and tty flip insertion. `stm32_usart_receive_chars_dma()` consumes a cyclic coherent RX buffer using DMA residue and `last_res`. `stm32_usart_receive_chars()` selects DMA or PIO and temporarily disables `DMAR` to handle DMA-mode RX errors in PIO. TX uses `stm32_usart_transmit_chars_pio()` or `stm32_usart_transmit_chars_dma()` and falls back to PIO if DMA preparation/submission fails.

## Control Flow
Interrupt handling begins in `stm32_usart_interrupt()`. It handles RS485 transmit-complete polarity changes, receiver timeout, wake-up flags, RX ready/error paths, PIO TX empty, and forced DMA RX flushes. `startup()` requests the IRQ, configures optional RX/TX swap, flushes RX FIFO when supported, starts RX DMA if available, and enables RX plus configured IRQ bits. `shutdown()` terminates TX/RX DMA, disables DMA request bits, waits for transmission complete, flushes FIFOs, clears enable/interrupt bits, and frees the IRQ.

`set_termios()` is the main hardware programming path. It waits for `TC`, disables CR1, flushes FIFOs, computes word length/parity/stop bits, selects 8x or 16x oversampling, programs prescaler/BRR, configures read/ignore masks, sets DMA and FIFO timeout bits, applies hardware flow control, applies RS485, configures wake-on-start-bit, writes CR3/CR2/CR1, then reenables the USART.

## State And Persistence
Persistent driver state is in `struct stm32_port`: mapped `uart_port`, clock, matched register info, DMA channels/buffers, DMA busy flags, RX residue tracking, IRQ masks, FIFO threshold config, RS485/GPIO modem control, pin swap, wake source, `rdr_mask`, and throttled state. No disk state is persisted. Hardware register state is rederived from DT properties, termios, runtime PM, and uart-core callbacks.

## Dependencies And Integration Points
The file depends on platform/OF probing, clocks, DMAengine, coherent DMA allocation, runtime PM, wake IRQ support, pinctrl sleep/idle states, tty flip buffers, serial core, sysrq, console/earlycon infrastructure, and `serial_mctrl_gpio`. Device-tree integration includes `serial` aliases, `st,stm32-uart`, `st,stm32f7-uart`, `st,stm32h7-uart`, `rx-tx-swap`, `wakeup-source`, `uart-has-rtscts`, deprecated `st,hw-flow-ctrl`, and FIFO threshold properties.

## Risks
DMA error recovery is delicate: RX DMA errors require fast PIO draining because the hardware masks DMA requests while FIFO data stacks up. `last_res`/residue handling must remain correct across cyclic wraparound. RS485 RTS polarity and delayed DE timing depend on baud/divisor math and on whether RTS is hardware or GPIO controlled. Sleep wakeup paths temporarily stop RX DMA and manually flush data, so missed ordering can drop wake characters. `set_termios()` rewrites core registers while waiting for `TC`; any timeout can leave partially reprogrammed hardware.

## Test Signals
Useful tests include boot probe on each compatible, fallback operation with missing DMA channels, RX/TX under PIO and DMA, RX error handling during DMA, FIFO threshold DT variants, RS485 with both RTS polarities and delays, `rx-tx-swap`, console and earlycon output, sysrq/break handling, suspend/resume with wakeup-source, runtime PM clock toggling, and CREAD/IGNBRK/IGNPAR termios behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/stm32-usart.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/stm32-usart.h -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/stm32-usart.h

## Purpose
This header defines the private STM32 USART register model used by `stm32-usart.c`: per-SoC offsets, feature flags, register bit definitions, buffer sizes, and the per-port state container.

## Important APIs, Types, And Functions
`struct stm32_usart_offsets` abstracts F4/F7/H7 register placement. `struct stm32_usart_config` records feature presence such as seven-bit data, RX/TX swap, wakeup, FIFO support, and the USART enable bit position. `struct stm32_usart_info` combines offsets and feature flags for OF match data.

`struct stm32_port` embeds `struct uart_port` and adds clock, match info, DMA channels and coherent buffers, DMA busy flags, interrupt bit caches, cyclic-RX residue state, flow-control flags, FIFO threshold config, wakeup state, RDR masking, GPIO modem-control handle, and DMA residue state. The header also declares the static `stm32_ports` array and `stm32_usart_driver` for shared use inside the translation unit.

## Control Flow
The header has no executable flow, but its constants drive every control path in the C file. Offset fields choose which hardware registers are valid. `UNDEF_REG` gates features not present on older variants. `USART_SR_ERR_MASK`, interrupt masks, FIFO threshold fields, DMA bits, RS485 DE bits, wakeup bits, and flush request bits are used by startup, interrupt, termios, DMA, console, and PM paths.

## State And Persistence
The key persistent runtime state is `struct stm32_port`. It is static per alias id and survives open/close while the driver is loaded. Hardware state is reflected through cached flags and DMA pointers rather than through any filesystem persistence.

## Dependencies And Integration Points
The definitions assume Linux bit helpers such as `BIT`, `GENMASK`, and DMAengine/serial-core types are visible from the including C file. They integrate directly with STM32 OF match data and Linux serial core port registration.

## Risks
Incorrect register offsets or bit definitions can corrupt unrelated USART registers. The `UNDEF_REG` sentinel is central: callers must check it before touching optional registers. Buffer size constants couple the cyclic DMA setup and residue math. Feature booleans must match silicon capabilities or `set_termios()`, wakeup, FIFO, and swap paths will program unsupported bits.

## Test Signals
Header correctness is exercised through compile coverage for all compatibles and runtime probe on F4, F7, H7/MP1-like hardware. Tests should include variants without `icr`, without prescaler, without FIFO, and with H7 wake/FIFO bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/stm32-usart.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/suncore.c -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/suncore.c

## Purpose
This file is the shared Sun serial support layer used by multiple SPARC serial drivers. It centralizes dynamic minor allocation, firmware console matching and termios extraction, and legacy Sun mouse baud-rate detection.

## Important APIs, Types, And Functions
`sunserial_register_minors()` assigns a contiguous minor range starting at `sunserial_current_minor`, grows `drv->nr`, registers the uart driver on first use, and adjusts `tty_driver->name_base`. `sunserial_unregister_minors()` shrinks the range and unregisters when the last user leaves. `sunserial_console_match()` wires a console into a driver, compares the device node to `of_console_device`, optionally validates A/B line selection, and adds a preferred console when the command line did not already select one.

`sunserial_console_termios()` parses firmware properties such as `ttyX-mode`, `ssp-console-modes`, and LOM defaults into `console->cflag`. `suncore_mouse_baud_cflag_next()` rotates mouse baud rates through 1200, 2400, 4800, and 9600. `suncore_mouse_baud_detection()` watches break patterns and the 0x87 byte to decide whether mouse baud should advance.

## Control Flow
Sun serial drivers call `sunserial_register_minors()` during module init once they count firmware nodes, call `sunserial_console_match()` during per-device probe, and call `sunserial_console_termios()` from console setup. Keyboard/mouse drivers call the mouse helpers in their RX interrupt paths when breaks indicate mismatched baud.

## State And Persistence
`sunserial_current_minor` is process-global in kernel memory and tracks assigned minors across Sun serial driver registrations. Mouse detection stores `mouse_got_break` and `ctr` as static state shared across calls. There is no persistent storage.

## Dependencies And Integration Points
The file depends on serial core, console core, OF PROM data, `of_console_device`, `of_console_options`, and `linux/sunserialcore.h` exports. It is consumed by `sunsu`, `sunsab`, `sunzilog`, and `sunhv`.

## Risks
Minor accounting is global and assumes balanced register/unregister calls with the original count. Console matching depends on firmware naming and A/B line offset conventions. `sunserial_console_termios()` performs minimal validation and ignores handshake fields. Mouse baud detection is global static state, so concurrent mouse-like streams could interfere.

## Test Signals
Validation should include multiple Sun serial drivers registering in one boot, console node matching with and without command-line console, A/B line offset handling, RSC/LOM/default termios parsing, and mouse break-driven baud rotation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/suncore.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/sunhv.c -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/sunhv.c

## Purpose
This driver exposes the SUN4V hypervisor console as a Linux UART named `ttyHV`. It uses SPARC hypervisor console calls instead of memory-mapped UART registers and provides both tty and console support.

## Important APIs, Types, And Functions
The driver switches between `bychar_ops` (`sun4v_con_putchar/getchar`) and `bywrite_ops` (`sun4v_con_write/read`) depending on hypervisor API support detected in `hv_probe()`. `sunhv_pops` implements `uart_ops` for serial core. `sunhv_console` is the console object. `sunhv_migrate_hvcons_irq()` exports IRQ affinity migration for CPU migration paths.

RX helpers handle hypervisor break and hangup values: `receive_chars_getchar()` and `receive_chars_read()` feed tty flip buffers, sysrq, DCD changes, and `sun_do_break()`. TX helpers drain the uart xmit FIFO by byte or page. Console write uses either per-character CRLF expansion or a page buffer filled by `fill_con_write_page()`.

## Control Flow
`sunhv_init()` only registers on hypervisor systems. `hv_probe()` validates IRQ availability, allocates a `uart_port`, optionally allocates one-page read/write buffers when the newer HV API is available, registers minors through `suncore`, matches the firmware console, adds the uart port, requests the IRQ, and stores driver data. Interrupts lock the port, receive pending console input, transmit pending tty bytes, then push flip buffers.

## State And Persistence
Global state includes `sunhv_port`, optional `con_write_page`/`con_read_page`, selected `sunhv_ops`, and `hung_up`. The allocated `uart_port` stores serial-core counters and masks. No state is persisted beyond driver lifetime.

## Dependencies And Integration Points
The driver depends on SPARC hypervisor APIs, IRQ/PROM/platform-device data, serial core, console core, sysrq, tty flip buffers, and `sunserial_register_minors()`/`sunserial_console_match()`. OF matching accepts `qcn` and `SUNW,sun4v-console` console nodes.

## Risks
The page-mode path depends on physically contiguous pages and correct `__pa()` usage. Console write loops can spin up to large retry limits if HV calls do not accept data. Hangup handling is global and single-port. `ignore_status_mask` is configured but receive paths largely rely on hypervisor status handling, so termios semantics are narrower than a hardware UART.

## Test Signals
Test on SUN4V guests with old and new HV console APIs, console output during oops/sysrq, tty read/write, break handling, hangup/DCD transition, IRQ migration, remove cleanup, and no-probe behavior on non-hypervisor systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/sunhv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/sunplus-uart.c -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/sunplus-uart.c

## Purpose
This is the Sunplus SP7021 UART platform driver. It is 8250-like but not register-compatible, so it implements its own register access, IRQ handling, console, earlycon, clock/reset management, and uart-core operations.

## Important APIs, Types, And Functions
`struct sunplus_uart_port` embeds `uart_port` and stores clock/reset handles. `sunplus_uart_ops` covers mctrl, tx/rx start/stop, break, startup/shutdown, termios, line discipline PPS handling, type/config/verify, and optional console polling.

`transmit_chars()` drains the tty xmit FIFO while the TX FIFO is not full. `receive_chars()` loops while RX data is present, updates icount for break/parity/frame/overrun, handles sysrq, honors CREAD via `SUP_DUMMY_READ`, inserts tty chars, and pushes flip buffers. `sunplus_uart_irq()` reads the interrupt status/control register and dispatches RX/TX handling.

Probe obtains `serial` alias id, allocates state, enables the optional clock, deasserts reset, maps registers, sets port fields, stores console port state when enabled, and calls `uart_add_one_port()`.

## Control Flow
Module init registers the uart driver and platform driver. `startup()` requests the IRQ and enables RX interrupts. TX interrupts are enabled only by `start_tx()` and disabled when the FIFO empties. `shutdown()` writes zero to the interrupt control register and frees the IRQ. `set_termios()` computes Sunplus's split divisor/ext divisor format, configures data bits/parity/stop bits, updates timeout and status masks, optionally flushes RX when CREAD is clear, then writes divisor and LCR registers.

## State And Persistence
Runtime state lives in the per-device `sunplus_uart_port`, register bits, and serial-core counters/masks. Console builds a static `sunplus_console_ports[SUP_UART_NR]` lookup. There is no persistent storage.

## Dependencies And Integration Points
The driver depends on platform/OF, `serial` aliases, clock framework, reset controller, serial core, tty flip buffers, console/earlycon, sysrq, and generic 8250 bit definitions from `serial_reg.h`. It matches `sunplus,sp7021-uart` and exposes `ttySUP`.

## Risks
`sunplus_tx_empty()` checks `UART_LSR_TEMT` against the Sunplus LSR layout even though TX-not-full is bit 0; this depends on hardware exposing a compatible TEMT bit or may underreport empty state. Interrupt status bits are read-to-clear while enable bits share the same register, so careless read/modify/write ordering can drop status or mask interrupts. The driver maps modem outputs through MCR bits, but external modem behavior depends on hardware wiring. Suspend skips console ports, so non-console-only PM coverage is needed.

## Test Signals
Tests should cover probe/remove, alias id bounds, clock/reset failure unwind, RX/TX interrupt operation, break/parity/frame/overrun status accounting, CREAD clearing and RX flush, termios divisor accuracy, PPS line discipline flag toggling, console/earlycon writes, suspend/resume, and TX empty behavior on real hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/sunplus-uart.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/sunsab.c -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/sunsab.c

## Purpose
This driver supports Siemens SAB82532 DUSCC asynchronous serial controllers on Sun systems. Each chip exposes two channels, registered as `ttyS` ports through the shared Sun minor allocator.

## Important APIs, Types, And Functions
`struct uart_sunsab_port` wraps `uart_port`, mapped SAB register union, IRQ flags, DSR state, command timeouts, interrupt masks, DTR/DSR PVR bit assignments, GIS shift, chip version, and cached register values. `sunsab_pops` provides the uart-core callbacks.

`receive_chars()` handles RPF/TCD/TIME/RFO/BRK events, reads FIFO bytes, acknowledges receive completion, updates counters, processes sysrq/break, applies read/ignore masks, and returns a tty port for flip push. `transmit_chars()` reacts to ALLS/XPR interrupts, applies pending cached register updates via `sunsab_tx_idle()`, fills the transmit FIFO, issues `CMDR_XF`, wakes writers, and masks XPR when idle. `check_status()` handles DCD/CTS/DSR deltas.

`calc_ebrg()` computes SAB baud generator values. `sunsab_convert_to_sab()` translates termios into DAFO, EBRG, timeout, read/ignore masks, receiver enable, and deferred register updates.

## Control Flow
Init counts matching OF nodes, allocates channel state, registers the required minor count, then registers the platform driver. `sab_probe()` initializes both channels in one device, matches console nodes for each line, and adds both uart ports. `startup()` requests a shared IRQ, waits for command engines, resets RX/TX, clears interrupt registers, programs async mode, powers the channel, masks/unmasks selected interrupts, and marks TX idle. `shutdown()` masks interrupts, disables break and receiver, avoids power-down due known reboot crashes, and frees the IRQ.

## State And Persistence
State is per channel in `sunsab_ports`. Register programming is intentionally cached in `cached_ebrg`, `cached_mode`, `cached_pvr`, and `cached_dafo`; `SAB82532_REGS_PENDING` delays writes until transmitter idle to avoid emitting garbage. Global state includes the allocated `sunsab_ports` array and uart driver registration. No disk persistence exists.

## Dependencies And Integration Points
The driver depends on OF/platform resources, SPARC IRQ data, serial core, console core, tty flip buffers, sysrq, `suncore` minor/console helpers, and the register definitions in `sunsab.h`. It matches OF nodes named `se` or compatible `sab82532`.

## Risks
Deferred register updates are essential; writing mode/baud/data-format while TX is active can corrupt output. The stop-RX path writes `interrupt_mask1` to `imr0`, which is suspicious and should be regression-tested. Probe uses a static `inst` counter and expects init-time counting to match actual probe count. Shutdown intentionally leaves power enabled due historical crash behavior, so power-state expectations are unusual.

## Test Signals
Test dual-channel probe/remove, shared IRQ dispatch for ISR0/ISR1, RX FIFO counts for RPF/TCD/TIME/RFO, break/sysrq and `sun_do_break()`, modem status waits, termios baud and parity/stop/data changes while TX active, console setup from firmware termios, and cleanup when the second channel fails to add.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/sunsab.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/sunsab.h -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/sunsab.h

## Purpose
This header models the SAB82532 asynchronous register layout and names the bit fields used by `sunsab.c`.

## Important APIs, Types, And Functions
`struct sab82532_async_rd_regs`, `struct sab82532_async_wr_regs`, and `struct sab82532_async_rw_regs` describe read-only, write-only, and read/write views over the same register block. `union sab82532_async_regs` lets the driver access the correct semantic view. `union sab82532_irq_status` overlays ISR0/ISR1 as a 16-bit status word for compact interrupt dispatch.

The rest of the header defines command bits, mode bits, data-format fields, FIFO settings, baud/config registers, version/status bits, global interrupt bits, interrupt masks/status, port interrupt bits, and internal software irqflag bits.

## Control Flow
There is no executable flow. The C driver uses the register structures for MMIO offsets and the macros to build startup, interrupt, termios, transmit, receive, and modem-control programming sequences.

## State And Persistence
The header does not store state. Its software flag definitions, especially `SAB82532_ALLS`, `SAB82532_XPR`, and `SAB82532_REGS_PENDING`, define how `sunsab.c` persists channel status in memory.

## Dependencies And Integration Points
It depends on Linux integer aliases such as `u8` being available in the including file. It is private to the SAB driver and tightly coupled to the Siemens SAB82532 async register map.

## Risks
The register structs depend on exact padding and byte offsets. Any mistake changes every MMIO access. The same numeric bits are reused in different register contexts, so caller-side register selection must be correct. The volatile union exposes raw hardware state without additional type safety.

## Test Signals
Compile-time use through `sunsab.c`, runtime channel initialization, interrupt masking/acknowledgment, FIFO read/write, modem status, and termios conversion are the practical validation signals for this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/sunsab.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/sunsu.c -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/sunsu.c

## Purpose
This driver supports Sun SU UARTs, largely 8250-family devices used as serial ports and sometimes as keyboard/mouse interfaces. It provides both normal tty serial behavior and `serio` integration for Sun keyboard/mouse ports.

## Important APIs, Types, And Functions
`struct uart_sunsu_port` embeds `uart_port` and tracks ACR/IER/LCR, detected UART type, SU role, register size, cached cflag, break flags, and optional serio state. `sunsu_pops` is the uart-core operation table for normal serial ports.

`serial_in()`/`serial_out()` abstract IO-space, hub6, and MMIO access, including a sparc32 MCR OUT2 workaround. `sunsu_autoconfig()` performs 8250-compatible existence, loopback, FIFO, StarTech, 16750, and scratch-register tests. `receive_chars()` and `transmit_chars()` implement normal tty RX/TX; `receive_kbd_ms_chars()` and `sunsu_kbd_ms_interrupt()` handle keyboard/mouse devices and mouse auto-baud using `suncore_mouse_baud_detection()`.

## Control Flow
Init counts OF `su`, `su_pnp`, and compatible `serial` nodes that are true serial ports, registers Sun minors, and registers the platform driver. `su_probe()` classifies a node through `/aliases` as keyboard, mouse, or serial. Keyboard/mouse devices allocate private state, initialize baud and serio, start the UART, and do not register a tty port. Serial devices use a static `sunsu_ports` entry, autoconfigure the UART, match possible console nodes, and call `uart_add_one_port()`.

For tty ports, `startup()` initializes special 16C950/RSA paths, clears FIFOs and interrupt registers, requests a shared IRQ, sets MCR, enables RX/status interrupts, and clears registers again. The serial interrupt loops until IIR reports no interrupt, handling RX, modem deltas, TX, and flip push.

## State And Persistence
Global state includes `sunsu_ports[UART_NR]` and `nr_inst`. Keyboard/mouse ports allocate separate state and optional serio registration. Per-port cached state includes IER, LCR, cflag, detected type, and line status break flags. No state is persisted outside memory.

## Dependencies And Integration Points
The driver depends on OF/platform resources, SPARC IRQ setup, serial core, tty flip buffers, console/sysrq, optional serio, `serial_reg.h`, optional RSA support, and `suncore` helpers. Console setup gets firmware termios through `sunserial_console_termios()`.

## Risks
The driver mixes legacy 8250 probing with platform OF enumeration and has several hardware-specific special cases. `nr_inst` is shared by serial and keyboard/mouse probes, so ordering matters. Keyboard/mouse ports bypass uart registration but still use startup/IRQ paths. Autoconfig writes many legacy UART registers and can misdetect quirky devices. Busy waits in serio write and console output can stall if hardware stops reporting THRE/TEMT.

## Test Signals
Test normal tty ports and keyboard/mouse aliases separately, autoconfig across 16450/16550A/16750/16C950-like hardware, shared IRQ behavior, RX error/break/sysrq handling, modem deltas, termios divisor/FIFO changes, console output with firmware settings, serio open/close/write, mouse baud rotation, and probe/remove cleanup for allocated keyboard/mouse state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/sunsu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/sunzilog.c -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/sunzilog.c

## Purpose
This driver supports Zilog Z8530/ESCC serial chips on Sun SPARC systems. Each chip has channel A and channel B, used either as tty serial ports or as keyboard/mouse serio devices.

## Important APIs, Types, And Functions
`struct uart_sunzilog_port` embeds `uart_port`, links into an IRQ-service chain, caches all Zilog write registers in `curregs`, stores flags for console, keyboard, mouse, KGDB, modem status, channel A, deferred register update, TX stopped/active, ESCC, and ISR availability, plus parity mask, previous status, and optional serio state.

`read_zsreg()`/`write_zsreg()` implement indexed register access with platform-specific delay/write-sync rules. `__load_zsregs()` programs the channel safely, detects ESCC extensions, resets errors/FIFOs/status, and loads baud/format/interrupt registers. `sunzilog_maybe_update_regs()` defers full register reloads while TX is active. RX, status, and TX interrupt paths are `sunzilog_receive_chars()`, `sunzilog_status_handle()`, and `sunzilog_transmit_chars()`.

## Control Flow
Init counts `zs` nodes, allocates channel and chip-register tables, registers minors for non-keyboard/mouse chips, registers the platform driver, then requests a shared IRQ after probes establish `zilog_irq`. Probe maps the chip, initializes both channels, registers tty ports for serial chips, or prints/registers serio devices for keyboard/mouse chips. The shared ISR walks the linked channel chain, reads channel A pending bits from R3, handles A events, then advances to channel B and handles B events.

Termios changes compute BRG constants and update cached registers for word size, stop bits, parity, masks, modem status interest, timeout, and deferred hardware reload. Console setup reads firmware termios, configures break interrupts, sets mctrl, and starts the channel without depending on normal startup.

## State And Persistence
State persists in `sunzilog_port_table`, `sunzilog_chip_regs`, `sunzilog_irq_chain`, `zilog_irq`, and per-port cached registers. The cached-register model is important because many changes must wait until transmit is no longer active. No disk persistence exists.

## Dependencies And Integration Points
The file depends on OF/platform resources, SPARC IRQ setup, serial core, console/sysrq, tty flip buffers, optional serio, `suncore` helpers, and `sunzilog.h` register definitions. It exposes `ttyS` lines and optional `zskbd`/`zsms` serio devices.

## Risks
Indexed Zilog register access is timing-sensitive, especially on 32-bit SPARC where delays are required. The IRQ handler assumes channel pairs and `next` links are valid; table allocation and probe ordering must match counted nodes. There is a probable bug pattern where console matching for channel B sets `up->flags` instead of `up[1].flags`. Modem delta detection uses manual previous-status tracking and must be verified. Deferred register reloads are required to avoid corrupting TX.

## Test Signals
Test serial and keyboard/mouse `zs` nodes, shared IRQ handling for both channels, ESCC detection and FIFO bits, console firmware termios, break/sysrq and `sun_do_break()`, deferred termios changes during active TX, modem status deltas, poll console operations, serio registration/open/write, and module exit disabling MIE/freeing IRQ.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/sunzilog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/sunzilog.h -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/sunzilog.h

## Purpose
This header defines the Zilog channel memory layout and register bit names used by `sunzilog.c`.

## Important APIs, Types, And Functions
`struct zilog_channel` models the control/data byte layout with padding. `struct zilog_layout` models a chip with channel B followed by channel A. `NUM_ZSREGS` and `R7p` define the cached write-register array shape. `BRG_TO_BPS()` and `BPS_TO_BRG()` convert between baud and baud-rate-generator constants.

The macros name write registers R0-R15, ESCC R7 prime, write commands, receive/transmit enable fields, parity/stop/clock modes, DTR/RTS/break bits, baud generator controls, interrupt enable bits, read status bits, interrupt-pending codes, and utility clear macros.

## Control Flow
There is no executable control flow. The driver uses these definitions to build register images, decode interrupt pending status, check RX/TX readiness, handle break/error conditions, and convert termios into Zilog register values.

## State And Persistence
The header does not store state. It defines the constants used by `curregs[NUM_ZSREGS]`, which is the driver's persistent in-memory representation of each channel's hardware programming.

## Dependencies And Integration Points
The layout and bits are private to the Sun Zilog driver and assume Linux byte IO helpers are available in the including file. Some legacy macros use `sbus_readb`/`sbus_writeb`, while the current driver primarily uses `readb`/`writeb` wrappers.

## Risks
Incorrect channel order or padding would map channel A/B incorrectly. Register constants overlap by context, so writes must target the intended register. The BRG conversion macros assume valid nonzero baud input. Legacy utility macros are less integrated with the current access wrappers and could be risky if reused casually.

## Test Signals
Practical validation comes from Zilog probe, channel A/B MMIO mapping, BRG programming, interrupt decoding, RX/TX data movement, break/error handling, and ESCC FIFO enable detection in `sunzilog.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/sunzilog.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/tegra-tcu.c -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/tegra-tcu.c

## Purpose
This driver exposes NVIDIA Tegra Combined UART as a UART backed by mailbox channels rather than MMIO UART registers. It supports a single `ttyTCU` port and optional console output.

## Important APIs, Types, And Functions
`struct tegra_tcu` owns a dynamically registered `uart_driver`, optional `console`, one `uart_port`, and TX/RX mailbox clients/channels. `tegra_tcu_uart_ops` is minimal: TX empty always true, modem controls are no-ops, startup/shutdown/termios are no-ops, and `start_tx()` drains the xmit FIFO into mailbox messages.

`tegra_tcu_write()` packs up to three bytes plus a byte count into a 32-bit mailbox payload and expands newline into CRLF. `tegra_tcu_receive()` unpacks received mailbox payloads into tty flip chars. Probe requests TX first, registers the driver and port, then requests RX so immediate callbacks have a valid port.

## Control Flow
`tegra_tcu_probe()` allocates state, initializes mailbox clients, requests TX, initializes optional console metadata, registers a one-port uart driver, initializes `uart_port`, adds the port, requests RX, stores drvdata, and registers console if configured. Remove unregisters console, frees RX, removes the port, unregisters the uart driver, and frees TX.

## State And Persistence
The only persistent runtime state is the devm-allocated `tegra_tcu` object and mailbox channel handles. No hardware register state or filesystem persistence exists. The mailbox firmware/remote endpoint owns actual transport state.

## Dependencies And Integration Points
The driver depends on platform/OF matching for `nvidia,tegra194-tcu`, Linux mailbox framework channels named `tx` and `rx`, serial core, tty flip buffers, and optional console core. `port->private_data` points back to `tegra_tcu`.

## Risks
`tegra_tcu_receive()` assumes `tcu->port.state` is valid after RX channel request; probe ordering mitigates but runtime callbacks before open may still need scrutiny. `start_tx()` flushes each mailbox message synchronously, which can block on slow firmware. Modem, baud, break, and flow-control semantics are intentionally absent. Packing allows only three bytes because byte count occupies high bits.

## Test Signals
Test mailbox probe failure unwind, TX CRLF expansion and three-byte packing, RX unpacking for 1-3 byte payloads, console registration/write, tty write wakeups, remove cleanup, and behavior when RX messages arrive before a user opens the tty.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/tegra-tcu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/tegra-utc.c -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/tegra-utc.c

## Purpose
This is the NVIDIA Tegra UART Trace Controller driver. It exposes up to 16 `ttyUTC` ports backed by separate RX and TX MMIO client register blocks and supports interrupt-driven tty IO, console polling, earlycon, and nbcon console output.

## Important APIs, Types, And Functions
`struct tegra_utc_port` contains optional console object, `uart_port`, RX/TX base mappings, IRQ masks, FIFO size, and RX/TX thresholds. `tegra_utc_uart_ops` implements TX empty, start/stop TX, stop RX, startup/shutdown, fixed termios, and optional poll operations.

`tegra_utc_init_tx()` and `tegra_utc_init_rx()` configure enable, FIFO thresholds, command reset/flush, interrupt clear/mask/set, and client enable. `tegra_utc_tx_chars()` uses `uart_port_tx()` to feed bytes until TX FIFO full. `tegra_utc_rx_chars()` drains up to 256 RX chars, accounts overflow, handles sysrq outside the port lock, inserts tty chars, and pushes flip buffers. `tegra_utc_isr()` loops over masked RX and TX interrupt status until drained.

## Control Flow
Module init registers a global uart driver and platform driver. Probe reads required `tx-threshold` and `rx-threshold`, obtains SoC FIFO size from match data, maps named `tx` and `rx` resources, calls `tegra_utc_setup_port()` and `uart_read_port_properties()`, stores drvdata, adds the port, and registers console if configured. `startup()` initializes hardware then requests a dedicated IRQ. `shutdown()` disables RX and frees the IRQ. Remove unregisters console and removes the port; module exit unregisters drivers.

Console flow includes earlycon setup for `nvidia,tegra264-utc`, atomic nbcon writes that burst by FIFO occupancy, threaded nbcon writes that poll FIFO space byte-by-byte, and console device lock/unlock wrappers around the uart port lock.

## State And Persistence
Per-device state is in `tegra_utc_port`, especially IRQ masks and thresholds. Hardware state is initialized on startup, poll init, console setup, and earlycon setup. No persistent storage exists.

## Dependencies And Integration Points
The driver depends on platform/OF matching `nvidia,tegra264-utc`, named resources `tx` and `rx`, device properties for thresholds and uart port properties, serial core, tty flip buffers, console/nbcon/earlycon, and MMIO polling helpers.

## Risks
Probe logs setup errors but does not return immediately after `tegra_utc_setup_port()` failure before registering the port, which may be a real bug. Termios forcibly clamps to 8-N-1 with no flow control, so user-requested settings are ignored. RX/TX interrupt loops rely on correct mask/set/clear semantics. Early/console paths must not overflow FIFO; atomic write bursts depend on accurate occupancy. `port.type` uses `PORT_TEGRA_TCU`, which may be intentional reuse or a type-reporting mismatch.

## Test Signals
Test probe with missing threshold properties, named resource failures, `uart_read_port_properties()` failure, IRQ request failure, RX/TX interrupt drain, overflow accounting, sysrq, stop_rx mask behavior, fixed termios enforcement, poll get/put, earlycon output, nbcon atomic/threaded output under FIFO pressure, suspend-like shutdown/startup cycles, and remove/module-exit cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/tegra-utc.c -->
