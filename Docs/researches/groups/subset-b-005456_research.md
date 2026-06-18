# subset-b-005456 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/icom.c -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/icom.c

## Purpose
`icom.c` is the Linux serial-core driver for IBM iSeries ICOM PCI serial I/O adapters. It discovers supported IBM PCI device IDs, maps adapter registers, loads adapter firmware, allocates per-port coherent DMA buffers/status areas, and exposes active adapter ports as `ttyA*` UART devices through a `struct uart_driver`.

## Important APIs, types, and functions
- Core data types are `struct icom_adapter`, `struct icom_port`, `struct icom_regs`, `struct func_dram`, and `struct statusArea`. `struct icom_adapter` owns PCI/MMIO state, up to four `icom_port` objects, adapter version/subdevice data, and a `kref` used to defer teardown while ports are open. `struct icom_port` embeds `struct uart_port` and stores per-port DRAM, interrupt register, coherent TX/RX/status buffers, cable ID, and status masks.
- PCI integration is handled by `icom_pci_table`, `icom_probe()`, `icom_remove()`, and `icom_pci_driver`.
- Serial-core integration is `icom_uart_driver` plus `icom_ops`, including `icom_open()`, `icom_close()`, `icom_start_tx()`, `icom_stop_tx()`, `icom_stop_rx()`, `icom_send_xchar()`, `icom_break()`, `icom_set_termios()`, modem control helpers, and `icom_config_port()`.
- Firmware and adapter bring-up are concentrated in `load_code()`, `start_processor()`, `stop_processor()`, `icom_startup()`, and `icom_shutdown()`. Firmware names are declared with `MODULE_FIRMWARE()` for `icom_call_setup.bin`, `icom_res_dce.bin`, and `icom_asc.bin`.
- Data movement is built around `get_port_memory()`, `free_port_memory()`, `icom_write()`, `xmit_interrupt()`, and `recv_interrupt()`.

## Control flow
Module init registers the UART driver, then the PCI driver. Probe enables the PCI device, requests BAR regions, enables memory/master/parity/SERR, applies adapter-specific PCI config writes, allocates an adapter, determines active ports from adapter version/subsystem ID, maps BAR0, requests a shared IRQ, allocates port DMA resources, and registers each active UART line.

Opening a line increments the adapter `kref` and runs `icom_startup()`. Startup validates the cable ID, reloads firmware if the visible cable ID changed, clears per-port interrupt latches, and unmasks the correct interrupt bits in the global adapter mask. Termios setup programs async format bytes, status/ignore masks, firmware command registers, receive descriptor address, transmit restart address, and enables TX/RX.

The IRQ handler demultiplexes adapter interrupt registers for V1 and V2 layouts, dispatching each active port through `process_interrupt()` and then modem-status handling. RX interrupts walk the two receive descriptors while `SA_FL_RCV_DONE` is set, copy data into the tty flip buffer, account break/parity/frame/overrun conditions, reset descriptors, and push the flip buffer. TX completion clears the ready flag, advances the tty xmit FIFO, and either starts another hardware transfer or wakes the line discipline.

Removal finds the adapter by PCI device and drops the `kref`; final release removes UART ports, drops modem outputs, stops processors, frees coherent memory, frees IRQ, unmaps MMIO, releases PCI regions, and frees adapter state.

## State and persistence behavior
Persistent runtime state lives in kernel memory and device DRAM only. Per-port state includes descriptor rings, next receive index, cached cable ID, status masks, coherent TX/RX pages, and the embedded `uart_port` counters. Adapter state is kept on the global `icom_adapter_head` list. Hardware state includes adapter control/mask registers and firmware DRAM command/status bytes. There is no disk persistence; firmware is requested from the kernel firmware loader at bring-up or cable-ID reload.

## Dependencies and integration points
The file depends on PCI, DMA coherent memory APIs, firmware loading, MMIO accessors, interrupt handling, serial core, tty flip buffers, kfifo-based transmit queues, and Linux reference counting. It integrates externally as a PCI driver named `icom`, a UART driver named `icom` with device name `ttyA`, and firmware blobs supplied by userspace or built-in firmware mechanisms.

## Risks and edge cases
- Port bring-up depends on three firmware images and on adapter-reported cable ID. Missing or oversized firmware causes the port to be disabled.
- `check_modem_status()` uses a static `old_status`, so modem delta tracking is shared across ports rather than per-port.
- Interrupt demux assumes certain ports are always active for adapter variants; inactive port checks exist for some but not all paths.
- The code uses coherent buffers and little-endian descriptor fields; descriptor setup and adapter-visible DMA addresses are central correctness points.
- Error unwinding in probe handles high-level resources, but partial per-port memory allocation failures in `icom_load_ports()` only log and continue, so inactive or partially initialized ports need careful audit.
- Firmware command polling uses short bounded loops without rich diagnostics when hardware does not clear command bytes.

## Test signals
Useful validation signals include PCI probe/remove on each supported adapter model, firmware load failure and success paths, open/close reference counting while removing a device, cable pull/reinsert behavior, TX FIFO wakeups, RX parity/frame/break/overrun handling, modem-control ioctls, interrupt sharing, and termios transitions across all supported baud table entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/icom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/imx.c -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/imx.c

## Purpose
`imx.c` is the platform serial-core driver for Motorola/Freescale/NXP i.MX UART controllers. It supports i.MX1 and i.MX21-style register layouts, Device Tree probing, normal TTY operation, console and nbcon output, optional cyclic RX/TX DMA, modem GPIOs, RS485 direction control, console polling, and suspend/resume context management.

## Important APIs, types, and functions
- `struct imx_port` embeds `struct uart_port` and stores clock handles, Device Tree feature flags, mctrl GPIOs, DMA channels and buffers, saved registers, RX flood state, console newline state, RX trigger level, and RS485 TX state machine timers.
- `struct imx_uart_data` distinguishes the i.MX1 test register offset from later i.MX21-compatible controllers. `imx_uart_dt_ids` binds `fsl,imx6q-uart`, `fsl,imx1-uart`, and `fsl,imx21-uart`.
- Serial-core operations are in `imx_uart_pops`: TX/RX start-stop, modem control, startup/shutdown, flush, termios, port verification, optional console poll hooks, and RS485 configuration through `port.rs485_config`.
- DMA support is implemented by `imx_uart_dma_init()`, `imx_uart_dma_exit()`, `imx_uart_start_rx_dma()`, `imx_uart_dma_rx_callback()`, `imx_uart_dma_tx()`, `imx_uart_dma_tx_callback()`, and enable/disable helpers.
- Console support is compiled under `CONFIG_SERIAL_IMX_CONSOLE` and uses `imx_uart_console_write_atomic()`, `imx_uart_console_write_thread()`, setup/exit helpers, and `struct console imx_uart_console`.
- Power management uses `imx_uart_save_context()`, `imx_uart_restore_context()`, wakeup enablement, and the `dev_pm_ops` suspend/resume/freeze/thaw methods.

## Control flow
Module init registers the `ttymxc` UART driver then the `imx-uart` platform driver. Probe allocates `imx_port`, reads the serial alias for the line number, parses Device Tree flags for RTS/CTS, DTE mode, GPIO RTS, inverted TX/RX, and DMA buffer sizing, maps MMIO, gets IRQs and clocks, initializes modem GPIOs, reads RS485 defaults, disables interrupt sources, handles RS485 loopback setup, configures DTE/DCEDTE direction, initializes RS485 hrtimers, requests either split i.MX1 IRQs or the combined IRQ, records the port in `imx_uart_ports`, and registers it with serial core.

Startup enables clocks, chooses RX trigger levels, disables data-ready interrupts before IRQ use, optionally initializes DMA for non-console ports, soft-resets FIFOs/state machines, clears interrupt latches, enables UART/RX/TX and modem interrupt sources, starts modem polling, and either starts cyclic RX DMA or enables PIO RX interrupts and aging timer. Shutdown reverses this path: terminates and unmaps DMA, stops TX/RX, disables DMA, disables modem GPIO polling, disables interrupts, handles RS485 RTS release including delayed hrtimer states, and disables clocks.

The combined interrupt path masks raw status bits by enabled interrupt sources before dispatching RX, TX, modem, wake, and overrun work. PIO RX drains `URXD0` while `URXD_CHARRDY`, classifies break/parity/frame/overrun, honors sysrq and ignore masks, and pushes flip data. DMA RX computes ring head/tail from DMA residue and period size, syncs the buffer for CPU/device ownership, copies a contiguous segment into the tty layer, and checks for RX flood. TX either writes bytes directly while FIFO has room or maps kfifo segments to DMA and completes through the DMA callback.

## State and persistence behavior
All persistent driver state is volatile. Hardware configuration is mirrored partly in `saved_reg[10]` during suspend/noirq, including UCR registers, FIFO config, escape/timer registers, baud registers, and UTS. The RX DMA buffer is an in-memory cyclic buffer with `circ_buf` head/tail state. RS485 direction is represented by `tx_state` and two hrtimers. Modem state is cached in `old_status` and periodically refreshed because many modem lines have no IRQ.

## Dependencies and integration points
The file depends on platform devices, Device Tree, clk APIs, pinctrl PM state, DMAengine, tty/serial core, sysrq, console/nbcon, mctrl GPIO helpers from `serial_mctrl_gpio.h`, hrtimers, timers, and memory-mapped I/O. External integration points include DT properties such as `uart-has-rtscts`, `fsl,dte-mode`, `rts-gpios`, `fsl,inverted-tx`, `fsl,inverted-rx`, and `fsl,dma-info`, plus serial core RS485 configuration.

## Risks and edge cases
- DMA mode is disabled for console ports and falls back to PIO if channels are unavailable; both paths must preserve identical termios and error behavior.
- RX flood detection deliberately soft-resets the UART after repeated RX interrupts without line activity. This protects known i.MX hardware behavior but can affect active sessions if the heuristic is wrong.
- RS485 handling has multiple hardware limitations around low-active RTS, loopback, and receiver-off operation; shutdown contains explicit recovery to avoid leaving a bus-blocking RTS state.
- Baud programming avoids rewriting unchanged UBIR/UBMR because the hardware can corrupt active transfers when these registers are rewritten unnecessarily.
- Suspend/resume requires clocks in the right phase and noirq context save/restore; wakeup signaling depends on the tty device being wake-capable.
- Probe relies on a valid DT serial alias and rejects line numbers beyond eight ports.

## Test signals
High-value tests include DT probe variants for i.MX1 and i.MX21-compatible controllers, PIO and DMA RX/TX, DMA fallback, console and nbcon writes under contention, sysrq and console poll, RS485 with/without GPIO RTS and delays, modem GPIO polling, low baud rates, custom baud via divisor, suspend/resume with wakeup, RX flood reproduction, and termios changes while traffic is active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/imx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/imx_earlycon.c -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/imx_earlycon.c

## Purpose
`imx_earlycon.c` provides the minimal early console writer for i.MX21/i.MX6Q-compatible UARTs before the full `imx.c` serial driver is available. It lets early boot messages be emitted through a Device Tree earlycon binding.

## Important APIs, types, and functions
- `imx_uart_console_early_putchar()` busy-waits until the TX FIFO is not full by polling `IMX21_UTS`, then writes one byte to `URTX0` with relaxed MMIO accessors.
- `imx_uart_console_early_write()` delegates string emission to `uart_console_write()`.
- `imx_console_early_setup()` validates `dev->port.membase` and installs the write callback.
- `OF_EARLYCON_DECLARE()` registers compatible strings for `fsl,imx6q-uart` and `fsl,imx21-uart`.

## Control flow
During early boot, the earlycon framework matches one of the declared compatible strings, creates an `earlycon_device`, and calls setup. Once setup installs the console write function, each early printk path calls `imx_uart_console_early_write()`, which emits characters one by one through the polling putchar helper.

## State and persistence behavior
The file keeps no private persistent state. It uses only the `earlycon_device` port supplied by the earlycon framework and direct MMIO register state. It does not program baud, clocks, FIFO levels, or line control; it assumes firmware or earlier boot code already made the UART usable.

## Dependencies and integration points
Dependencies are early console infrastructure, serial core console helpers, Device Tree earlycon matching, and relaxed MMIO access. It integrates with the full i.MX serial support by using the same compatible strings and TX/test register offsets for i.MX21-style controllers.

## Risks and edge cases
- Only i.MX21-style `IMX21_UTS` offset is supported; i.MX1 early console is not declared here.
- The polling loop can spin forever if the mapped UART never clears `UTS_TXFULL`.
- No locking, clock management, or register programming exists in this early path, which is appropriate for early boot but unsuitable for runtime driver use.

## Test signals
Boot with `earlycon` on `fsl,imx6q-uart` or `fsl,imx21-uart`, verify output before normal console registration, test failure when `membase` is absent, and compare character ordering/newline behavior with the later `imx.c` console.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/imx_earlycon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/ip22zilog.c -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/ip22zilog.c

## Purpose
`ip22zilog.c` is the serial-core driver for the Zilog SCC serial channels found on SGI IP22 workstations and servers. It exposes the two channels as `ttyS` lines, supports optional console operation, handles the IP22 register access timing requirements, and maps SCC interrupt/status/data semantics into Linux UART operations.

## Important APIs, types, and functions
- `struct uart_ip22zilog_port` wraps `struct uart_port` with software shadow registers (`curregs`), flags for console/KGDB/modem/TX state/deferred register loads/reset state, a break marker, parity mask, and previous status.
- Register access is via `read_zsreg()`, `write_zsreg()`, `ip22zilog_clear_fifo()`, `__load_zsregs()`, and `ip22zilog_maybe_update_regs()`.
- Interrupt work is split among `ip22zilog_interrupt()`, `ip22zilog_receive_chars()`, `ip22zilog_status_handle()`, and `ip22zilog_transmit_chars()`.
- Serial-core operations are provided by `ip22zilog_pops`, including modem control, start/stop TX/RX, break control, startup/shutdown, termios conversion, and fixed port request/release behavior.
- Platform lifecycle is `ip22zilog_probe()`, `ip22zilog_remove()`, `ip22zilog_init()`, and `ip22zilog_exit()`. Console support is conditional under `CONFIG_SERIAL_IP22_ZILOG_CONSOLE`.

## Control flow
Module init registers the UART driver and platform driver. Probe maps the SCC layout resource, prepares channel B as line 0 and channel A as line 1, requests the shared IRQ, and adds both UART ports. `ip22zilog_prepare()` initializes default 9600-8N1-style shadow registers, one-byte FIFO size, clock rate, and uart ops.

Startup resets the chip once, loads the shadow register set, enables master interrupts, records initial status, enables RX/TX, and enables external/RX/TX interrupts. Termios changes compute a Zilog baud-rate-generator constant, update shadow registers for clock mode, character width, parity, stop bits, read/ignore masks, and then either reload immediately or defer reload while TX is active.

The IRQ handler reads channel A register R3 for pending interrupt bits, services channel A and B under their port locks, resets highest interrupt-under-service, drains RX data, handles external status/break/modem events, advances TX, and pushes tty flip data after unlocking. TX is single-byte interrupt-driven; console writes poll for TX empty and write directly.

## State and persistence behavior
The driver keeps all intended SCC write-register values in `curregs`. This shadow state is authoritative for reprogramming the device, and reloads can be held with `IP22ZILOG_FLAG_REGS_HELD` until a transmit completes. `prev_status` tracks modem/break edge detection, while `tty_break` carries a break/sysrq marker to the following received null byte. Hardware reset state is shared through flags on both channel objects.

## Dependencies and integration points
The driver depends on SGI IP22 platform headers, platform resources, serial core, tty flip buffers, sysrq, optional console infrastructure, and MMIO byte access. It relies on constants and register layout from `ip22zilog.h`. It integrates as platform driver `ip22zilog` and UART driver `serial_ip22zilog` with `ttyS` lines on the traditional TTY major/minor range.

## Risks and edge cases
- Register access requires strict delays; missing or reordered delays can break SCC programming on IP22.
- `ip22zilog_clear_fifo()` appears to break when `Rx_CH_AV` is set, so FIFO-clearing behavior should be reviewed against intended SCC semantics.
- Register reloads are deferred during active TX; bugs in `TX_ACTIVE`/`REGS_HELD` handling can leave stale line settings.
- Console ports intentionally skip normal startup/shutdown paths because early console startup cannot allocate resources.
- The shared IRQ request uses `NULL` as `dev_id`; this limits shared interrupt bookkeeping and must match free behavior.
- Modem status delta logic is hand-maintained because the SCC only indicates that an external status interrupt occurred.

## Test signals
Useful tests include probe/remove on real or emulated IP22 resources, interrupt handling for both channels, console and non-console opens, termios updates during active TX, break/sysrq handling, modem status waits, RX error classification, and validation that baud constants match expected rates for `ZS_CLOCK / 16`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/ip22zilog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/ip22zilog.h -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/ip22zilog.h

## Purpose
`ip22zilog.h` defines the memory layout, baud-rate-generator formulas, register numbers, command bits, status bits, interrupt bits, and small clearing macros used by the SGI IP22 Zilog SCC serial driver.

## Important APIs, types, and functions
- `struct zilog_channel` describes one SCC channel's control and data registers with byte ordering differences for big-endian and little-endian builds.
- `struct zilog_layout` describes the device layout as channel B followed by channel A.
- `NUM_ZSREGS`, `BRG_TO_BPS()`, and `BPS_TO_BRG()` provide driver-side register array sizing and baud conversion.
- Register constants `R0` through `R15` index the SCC write/read register set.
- Bit definitions cover write registers for interrupt enable, RX/TX enable, parity/stop/clock mode, modem outputs, master interrupt/reset, clock source, baud generator, and external/status interrupts.
- Read-register definitions cover receive character availability, TX buffer empty, DCD/CTS/SYNC, break/abort, all-sent, parity/overrun/framing errors, and channel interrupt-pending encodings.

## Control flow
This header has no executable flow except macros. The `.c` file includes it to program `curregs`, convert termios speeds to SCC divisors, decode interrupt pending bits from R3, classify R1/R0 receive and modem status, and issue error/status/FIFO clear commands.

## State and persistence behavior
No state is stored in the header itself. Its constants define the shape of persistent state held elsewhere: the driver's 16-byte `curregs` shadow array, the MMIO channel layout, and the SCC's hardware register bits.

## Dependencies and integration points
The header depends on `asm/byteorder.h` for MMIO layout. It is tightly coupled to `ip22zilog.c` and the Zilog SCC programming model. The clearing macros use `writeb()`, `readb()`, and `udelay()`, so any user must include appropriate I/O and delay declarations before use or include through a file that already does.

## Risks and edge cases
- Endianness controls the control/data byte offsets inside each 32-bit-spaced channel; wrong endian assumptions would swap or misplace MMIO accesses.
- The baud conversion macros use integer arithmetic and rounding behavior that should be validated at low and high rates.
- The clear macros perform fixed delays and reads/writes without locking; callers must provide the synchronization required by the hardware access rules.
- Many constants are SCC-generic, but comments and usage are IP22-specific, so reuse in another Zilog driver would require timing and layout review.

## Test signals
Validation is mostly compile-time plus driver behavior: check struct offsets on big-endian IP22, verify baud macro outputs, confirm interrupt bit decoding for channels A/B, and exercise error/status/FIFO clear commands through `ip22zilog.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/ip22zilog.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/jsm/Makefile -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/jsm/Makefile

## Purpose
This Makefile wires the Digi Jasmine (`jsm`) serial driver into the kernel build. It builds `jsm.o` when `CONFIG_SERIAL_JSM` is enabled and composes that module/object from the shared PCI driver, Neo chip support, tty integration, and Classic chip support.

## Important APIs, types, and functions
- `obj-$(CONFIG_SERIAL_JSM) += jsm.o` selects the driver object based on Kconfig.
- `jsm-objs := jsm_driver.o jsm_neo.o jsm_tty.o jsm_cls.o` declares the compilation units linked into `jsm.o`.

## Control flow
There is no runtime control flow. Build flow is delegated to Kbuild: enabling `CONFIG_SERIAL_JSM` causes the listed objects to be compiled and linked as the `jsm` driver.

## State and persistence behavior
The file has no runtime state. Its persistent effect is build-system metadata controlling which object files are present in the kernel or module.

## Dependencies and integration points
It integrates with Linux Kbuild and with the source files that share `jsm.h`. The object order makes the module include PCI probe/remove (`jsm_driver.o`), board-specific ops (`jsm_neo.o`, `jsm_cls.o`), and serial-core/tty glue (`jsm_tty.o`).

## Risks and edge cases
- Omitting `jsm_tty.o` would leave symbols declared in `jsm.h` unresolved and remove the UART registration path.
- Omitting either chip-specific object would break PCI devices whose probe selects `jsm_neo_ops` or `jsm_cls_ops`.
- The Makefile assumes Kconfig defines `CONFIG_SERIAL_JSM`; build coverage should include built-in and module configurations.

## Test signals
Build with `CONFIG_SERIAL_JSM=y` and `CONFIG_SERIAL_JSM=m`, confirm `jsm.o` links all four objects, and run a disabled-config build to ensure no JSM objects are emitted.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/jsm/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/jsm/jsm.h -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/jsm/jsm.h

## Purpose
`jsm.h` is the shared internal contract for the Digi Neo and Classic PCI serial driver. It defines debug categories, supported PCI IDs, board/channel state, board operation callbacks, UART register layouts for Classic and Neo chips, Exar-specific flow-control/FIFO constants, and cross-file function prototypes.

## Important APIs, types, and functions
- `struct board_ops` is the chip-specific method table used by shared code for interrupts, UART init/off, termios programming, modem assertion, FIFO flushing, receiver control, break control, start/stop character send, and TX queue draining.
- `struct jsm_board` stores PCI device identity, resource ranges, remapped MMIO, IRQ, port count, interrupt lock, per-channel pointers, board-specific UART spacing/dividend, and selected `board_ops`.
- `struct jsm_channel` embeds `struct uart_port` and stores per-channel locks, flags, termios snapshots, modem output/input state, Classic/Neo MMIO pointers, software read/error queues, queue indices, counters, FIFO thresholds, flow-control watermarks, and error statistics.
- `struct cls_uart_struct` and `struct neo_uart_struct` describe the memory-mapped UART register layouts for Exar 16654-style Classic and 17158-style Neo hardware.
- Debug and state macros include `jsm_dbg()`, `MAXPORTS`, `WRITEBUFLEN`, board state constants, `CH_*` channel flags, queue sizes, and Exar FIFO/flow-control interrupt definitions.
- Externs and prototypes connect `jsm_driver.c`, `jsm_tty.c`, `jsm_cls.c`, and `jsm_neo.c`.

## Control flow
The header defines no runtime flow. It enables the shared PCI driver to select `jsm_cls_ops` or `jsm_neo_ops` at probe time, lets tty glue call chip-specific methods through `board_ops`, and lets chip interrupt handlers move data through common channel queues consumed by `jsm_input()` and flow-control helpers.

## State and persistence behavior
The main volatile state model is documented here: one `jsm_board` per PCI adapter, up to eight `jsm_channel` objects per board, per-channel 8 KiB read and error queues, per-channel modem and termios snapshots, and cumulative counters for RX/TX and errors. There is no disk persistence.

## Dependencies and integration points
The header depends on kernel types, tty, serial core, and device APIs. It integrates the JSM driver with PCI IDs from kernel PCI headers, serial-core `uart_port`, Linux tty termios state, and board-specific source files. Its register-layout structs are used directly with `readb()`, `writeb()`, and burst I/O helpers in the `.c` files.

## Risks and edge cases
- `struct jsm_channel` combines tty/uart state, software queues, hardware pointers, and statistics; lock ownership must be respected by all users to avoid queue or modem state races.
- The Exar register definitions differ between Classic and Neo; using the wrong `board_ops` or UART pointer corrupts hardware programming.
- Queue masks assume power-of-two queue sizes; producers drop oldest data on overflow in board-specific code.
- Some PCI IDs referenced by `jsm_driver.c` come from broader kernel PCI headers, while others are defined here, so portability depends on the surrounding kernel headers.

## Test signals
Compile all JSM objects together, probe representative Classic and Neo IDs, validate `bd_uart_offset`-based channel mapping, exercise every `board_ops` method through tty open/close/termios/break/flow-control paths, and stress software queue wraparound/overflow.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/jsm/jsm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/jsm/jsm_cls.c -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/jsm/jsm_cls.c

## Purpose
`jsm_cls.c` implements `board_ops` for Digi Classic PCI serial adapters using Exar 16654-like UARTs. It programs Classic-specific enhanced registers, handles the 8-bit board interrupt poll path, manages FIFO thresholds and hardware/software flow control, transfers RX data into JSM software queues, drains tty TX data to the UART, and controls modem/break/receiver state.

## Important APIs, types, and functions
- Flow-control programming is split into `cls_set_cts_flow_control()`, `cls_set_ixon_flow_control()`, `cls_set_no_output_flow_control()`, `cls_set_rts_flow_control()`, `cls_set_ixoff_flow_control()`, and `cls_set_no_input_flow_control()`.
- Data movement uses `cls_copy_data_from_uart_to_queue()` for RX and `cls_copy_data_from_queue_to_uart()` for TX.
- Interrupt handling is `cls_intr()` at board level and `cls_parse_isr()` at channel level.
- Termios/hardware programming is `cls_param()`, using the local baud table and `bd_dividend`.
- Lifecycle and controls include `cls_uart_init()`, `cls_uart_off()`, `cls_assert_modem_signals()`, receiver enable/disable, FIFO flushes, break send/clear, and XON/XOFF character send helpers.
- `struct board_ops jsm_cls_ops` exports this implementation to `jsm_driver.c`.

## Control flow
Probe selects `jsm_cls_ops` for Classic PCI IDs. Channel init disables interrupts, enters Exar enhanced register access with LCR `0xbf`, enables enhanced controls, clears FIFOs, marks FIFO state flags, and reads LSR/MSR to clear stale status. Runtime interrupts acquire the board interrupt lock, read `UART_CLASSIC_POLL_ADDR_OFFSET`, and parse every active port if any bit is pending. Each channel parser loops while the UART ISR reports pending work, servicing RX ready/timeouts, TX holding-register empty, and modem changes.

RX reads LSR and data byte by byte into `ch_rqueue` and `ch_equeue`, applies IGNBRK filtering, drops oldest queued bytes on overflow, updates parity/break/frame/overrun counters, and updates queue heads. TX checks stop/break flags and FIFO-empty/low-water flags, writes up to 32 bytes from the tty kfifo to the UART, updates transmit counts, clears FIFO-ready flags when enough data was written, and wakes the tty layer when the xmit FIFO empties.

Termios programming handles B0 by flushing queues and dropping RTS/DTR; otherwise it computes baud, line control, divisor latch values, interrupt enables, output flow control, input flow control, modem outputs, and current modem input status.

## State and persistence behavior
The Classic path mutates `jsm_channel` queue indices, flags, modem status bytes, FIFO trigger levels, flow-control watermarks, and counters. Hardware state is held in the Classic UART registers and enhanced register set, accessed by temporarily setting LCR to `UART_EXAR654_ENHANCED_REGISTER_SET`. No state persists beyond the driver instance and hardware registers.

## Dependencies and integration points
This file depends on `jsm.h`, serial register definitions, PCI device logging, tty kfifo state, and MMIO byte access. It integrates with shared JSM tty code through `jsm_input()` and `jsm_check_queue_flow_control()`, with `jsm_driver.c` through `jsm_cls_ops`, and with Classic hardware through `struct cls_uart_struct`.

## Risks and edge cases
- Enhanced-register access requires saving/restoring LCR correctly; failures can leave the UART in an alternate register bank.
- RX queue overflow intentionally discards oldest data; tests should verify error counters and tail movement.
- Comments note a Classic UART bug where clearing RX FIFO can also disrupt write data, so `cls_flush_uart_read()` avoids actual RX FIFO clearing.
- `cls_parse_modem()` calls `uart_handle_dcd_change()` for the DDSR/CTS path, which is suspicious and should be checked against expected CTS handling.
- TX FIFO count behavior is treated as unreliable, so TX readiness depends on flags set by interrupts.

## Test signals
Exercise Classic PCI probe, open/close, all baud table rates, B0 hangup, CRTSCTS, IXON/IXOFF, disabled start/stop chars, RX timeout and RX data interrupts, TX empty interrupts, modem deltas, break send/clear, queue overflow, and FIFO flush behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/jsm/jsm_cls.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/jsm/jsm_driver.c -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/jsm/jsm_driver.c

## Purpose
`jsm_driver.c` is the shared PCI and module lifecycle layer for the Digi JSM Neo and Classic multiport serial driver. It registers the UART driver, matches supported Digi PCI IDs, maps board resources, selects the correct Classic or Neo `board_ops`, initializes tty/UART ports, handles removal, and provides PCI error recovery callbacks.

## Important APIs, types, and functions
- `jsm_uart_driver` is the shared serial-core driver with device name `ttyn` and dynamic major.
- `jsm_probe_one()` performs PCI enablement, resource acquisition, board allocation, model classification, BAR mapping, IRQ request, tty initialization, and UART port initialization.
- `jsm_remove_one()` disables Classic board interrupts, removes UART ports, frees IRQ/MMIO/channel queues, releases PCI regions, disables the device, and frees the board.
- `jsm_pci_tbl` lists supported Digi Neo, Neo PCIe, IBM Neo, and Classic PCI device IDs.
- PCI error handling is `jsm_io_error_detected()`, `jsm_io_slot_reset()`, and `jsm_io_resume()`.
- Module lifecycle is `jsm_init_module()` and `jsm_exit_module()`, and `jsm_debug` is a module parameter consumed by `jsm_dbg()`.

## Control flow
Module init registers `jsm_uart_driver`, then registers the PCI driver. Probe enables the PCI device and regions, allocates `jsm_board`, assigns a board number, computes `maxports` from device ID, records revision/IRQ, and branches by Classic versus Neo hardware. Classic uses BAR4 memory plus BAR1 I/O control, selects `jsm_cls_ops`, sets UART spacing to 8 and dividend to 921600, maps BAR4, and enables PLX local/PCI interrupts through an I/O register. Neo uses BAR0 memory, selects `jsm_neo_ops`, sets UART spacing to 0x200 and dividend to 921600, and maps BAR0.

After board setup, probe requests the shared IRQ with the selected board interrupt handler, initializes tty-side resources via `jsm_tty_init()`, initializes UART ports via `jsm_uart_port_init()`, logs the board, stores driver data, and saves PCI state. Removal reverses this and frees per-channel read/error queues.

PCI error detection removes UART ports and requests reset. Slot reset re-enables the PCI device and bus mastering. Resume restores PCI config state and reinitializes UART ports.

## State and persistence behavior
The file owns one allocated `jsm_board` per PCI device. Board state includes resource addresses, remapped MMIO, selected ops, IRQ, channel pointers, and adapter numbering. It also maintains a static `adapter_count` for board numbering and a global `jsm_debug` parameter. There is no durable persistence; PCI state is saved/restored through kernel PCI APIs.

## Dependencies and integration points
Dependencies include PCI core, serial core through `jsm_uart_driver`, shared JSM declarations in `jsm.h`, IRQ handling, MMIO mapping, and tty setup functions in `jsm_tty.c`. The file integrates with Classic/Neo implementations through `jsm_cls_ops` and `jsm_neo_ops`.

## Risks and edge cases
- If `jsm_uart_port_init()` fails after `jsm_tty_init()`, the comment notes leaked resources from tty initialization.
- `adapter_count` increments during probe and is not decremented on remove or failed late probe, so board numbers are monotonic rather than compact.
- Classic interrupt enablement uses an I/O BAR side effect; missing disable on unusual error paths could leave hardware interrupting.
- PCI error resume reinitializes UART ports after previous removal, so duplicated or stale channel state should be tested.
- Resource selection differs sharply by device ID; a misclassified PCI ID would use the wrong BAR and `board_ops`.

## Test signals
Test module load/unload, probe/remove for representative Classic and Neo IDs, failed PCI enable/resource/map/IRQ/tty/UART init paths, PCI AER recovery callbacks, shared IRQ behavior, dynamic major allocation, and `jsm_debug` logging paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/jsm/jsm_driver.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/jsm/jsm_neo.c -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/jsm/jsm_neo.c

## Purpose
`jsm_neo.c` implements `board_ops` for Digi Neo PCI/PCIe serial adapters using Exar 17C158-like UARTs. It handles Neo-specific enhanced registers, FIFO burst transfer paths, 32-bit interrupt polling, auto hardware/software flow control, modem state, break handling, and PCI write posting flushes.

## Important APIs, types, and functions
- Flow-control configuration is implemented by `neo_set_cts_flow_control()`, `neo_set_rts_flow_control()`, `neo_set_ixon_flow_control()`, `neo_set_ixoff_flow_control()`, `neo_set_no_input_flow_control()`, `neo_set_no_output_flow_control()`, and `neo_set_new_start_stop_chars()`.
- RX/TX movement is `neo_copy_data_from_uart_to_queue()` and `neo_copy_data_from_queue_to_uart()`, using burst MMIO buffers when FIFOs are enabled.
- Interrupt handling is `neo_intr()` at board level, with per-port helpers `neo_parse_isr()` and `neo_parse_lsr()`.
- Termios/hardware programming is `neo_param()`.
- Control helpers include `neo_pci_posting_flush()`, modem assertion, FIFO flushes, receiver enable/disable, break send/clear, XON/XOFF send, UART init/off, and exported `struct board_ops jsm_neo_ops`.

## Control flow
Probe selects `jsm_neo_ops` for Neo PCI IDs. Channel init disables interrupts and enhanced features, enables ECB, clears FIFOs, reads stale status, marks FIFO enabled, and asserts cached modem outputs. Runtime interrupts lock the board, read the Neo 32-bit poll register at `UART_17158_POLL_ADDR_OFFSET`, use low eight bits to find pending ports, decode each port's three-bit interrupt type, clear the pending port bit, and dispatch RX timeout, RX line status, TX ready, or modem/status work. Unknown interrupt types are logged and ignored because the hardware can emit bogus types under load.

RX first tries burst reads using the reported RX FIFO count minus a hardware-bug fudge factor, limits copies to queue space and small chunks, records clean error bytes in `ch_equeue`, then falls back to byte-by-byte reads when errors or leftovers are present. It handles cached LSR bits, IGNBRK filtering, queue overflow by dropping oldest data, and calls `jsm_input()`. TX uses burst writes from the tty kfifo into `txrxburst` when FIFOs are enabled, or single-byte writes when disabled; readiness is governed by `CH_TX_FIFO_EMPTY` and `CH_TX_FIFO_LWM`.

Termios programming handles B0 by flushing queues and dropping RTS/DTR, otherwise computes divisor/lcr, enables RX/TX/modem interrupts, programs start/stop chars, configures output and input flow control, adjusts RX trigger level for baud rates below 9600, asserts modem outputs, and parses current modem inputs.

## State and persistence behavior
Neo state is held in `jsm_channel` flags, queue pointers, cached LSR, modem input/output bytes, FIFO thresholds, watermarks, and counters. Hardware state is in the Neo UART registers, including EFR, FCTR, TX/RX FIFO trigger registers, start/stop character registers, LCR divisor latches, IER, MCR, and MSR. `neo_pci_posting_flush()` reads a device ID location to force prior MMIO writes to reach the device.

## Dependencies and integration points
The file depends on `jsm.h`, serial register constants, tty kfifo APIs, PCI/device debug logging, MMIO byte/burst helpers, and shared JSM tty functions. It integrates with `jsm_driver.c` through `jsm_neo_ops` and with common tty processing through `jsm_input()` and `jsm_check_queue_flow_control()`.

## Risks and edge cases
- Several Exar hardware quirks are encoded directly: EFR must be zeroed before setting, RX FIFO count can be off by up to three bytes, burst reads are limited for IBM pSeries behavior, and bogus interrupt types can appear under load.
- Queue overflow drops oldest data and increments overrun stats; high-rate burst RX should be stress-tested.
- Cached LSR bits can affect TX readiness and RX error handling; stale cache handling is a race-sensitive area.
- Hardware/software flow-control combinations modify EFR/IER/FCTR and start/stop registers, so transitions between CRTSCTS, IXON, and IXOFF are high risk.
- MMIO writes that affect modem and receiver state often require posting flushes; missing flushes can delay visible hardware changes.

## Test signals
Test Neo PCI and PCIe probe, burst RX/TX, low-baud RX trigger adjustment, hardware CTS/RTS flow, software IXON/IXOFF detection, flow-control disable transitions, RX line-status errors, bogus interrupt types, queue overflow, break send/clear, modem state changes, FIFO flushes, and write-posting-sensitive modem updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/jsm/jsm_neo.c -->
