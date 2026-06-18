# subset-b-005460 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/qcom_geni_serial.c -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/qcom_geni_serial.c

## Purpose

`qcom_geni_serial.c` is the UART driver for Qualcomm GENI/QUP serial engines. It exposes two UART personalities through serial core: a FIFO-mode debug console device named `ttyMSM` for `qcom,geni-debug-uart` compatibles, and DMA-mode high-speed UART devices named `ttyHS` for `qcom,geni-uart` compatibles. It also handles SA8255P variants where baud/performance selection is driven through power-domain performance levels rather than direct GENI clock programming.

## Important APIs, Types, and Functions

`struct qcom_geni_serial_port` is the main per-port state: `uart_port`, `geni_se`, FIFO geometry, DMA addresses, setup flag, clock/poll timeout, RX buffer, swap/flow-control flags, RS485 state helpers, active TX accounting, wake IRQ, private serial-driver data, device match data, and optional power-domain list. `struct qcom_geni_device_data` selects console versus UART mode, GENI transfer mode, resource initialization, rate-setting, and power-state callbacks. `struct qcom_geni_private_data` carries the associated `uart_driver` and byte caches for poll/console paths.

Key UART operations are split by mode. Console ports use `qcom_geni_console_pops` with FIFO `start_tx`, `stop_tx`, `start_rx`, `stop_rx`, poll callbacks, and console write support. Non-console ports use `qcom_geni_uart_pops` with DMA `start_tx`, `stop_tx`, `start_rx`, and `stop_rx`. `qcom_geni_serial_port_setup()` loads UART firmware if needed, stops RX, discovers FIFO depths, configures RX stale count, optional pin swaps, packing, watermarks, and selected FIFO/DMA mode. `qcom_geni_serial_set_termios()` programs baud, parity, word length, stop bits, CTS masking/manual flow, loopback, timeout accounting, and clock/interconnect votes. `qcom_geni_serial_isr()` is the shared interrupt path for FIFO and DMA events.

## Control Flow

Probe resolves OF match data, chooses the console or high-speed UART driver, obtains a stable line number through serial aliases/IDA allocation, maps resources through serial core request/config callbacks, initializes GENI resources or SA8255P power domains, allocates a DMA RX buffer for high-speed ports, requests the IRQ with `IRQ_NOAUTOEN`, parses optional wake IRQ and pin-swap properties, gets RS485 defaults, enables runtime PM, and registers the UART port.

Startup lazily runs port setup, starts RX using the selected mode, and enables the main IRQ. FIFO RX starts a secondary GENI command and enables RX FIFO watermark/last interrupts. DMA RX starts the secondary command with RFR open and prepares a fixed 2048-byte DMA buffer. TX uses either FIFO watermark interrupts and `uart_fifo_out()` chunks or a DMA mapping prepared from the linear xmit FIFO tail. The ISR clears GENI/DMA statuses first, updates error counters and break/parity/drop state, completes DMA TX/RX, restarts RX DMA, drains RX FIFO for console paths, and feeds TX FIFO until the active command is complete.

Console write disables GENI master/secondary interrupts, handles any active transmit command by waiting or draining, cancels the command, writes the full console string through FIFO words with newline expansion, waits for completion, restores interrupt enables, and releases the port lock. Early console setup assumes firmware is already UART, cancels stale TX/RX state, configures packing/FIFO mode and 8N1-like defaults, and installs early read/write callbacks when configured.

## State and Persistence Behavior

There is no filesystem persistence. Long-lived state is the allocated `qcom_geni_serial_port`, IDA line ownership, GENI hardware state, FIFO/DMA accounting, optional wake IRQ state, selected clock/performance level, and runtime PM/interconnect votes. Hardware state persists across open/close while the device is powered: sequencer commands, watermarks, transfer configuration, pin swap, loopback, manual RFR, and baud clock selection. Suspend routes through serial core; console suspend also changes interconnect tagging to allow lower-power suspend even with `no_console_suspend`.

## Dependencies and Integration Points

The driver depends on platform devices, OF match data, Qualcomm GENI serial-engine helpers, QUP wrapper state from the parent, clocks or OPP/performance domains, interconnect bandwidth APIs, runtime/system PM, wake IRQ infrastructure, serial core, tty flip buffers, DMA helpers in the GENI SE layer, and optional console/earlycon/poll support. It integrates with RS485 via `uart_port.rs485_config`, with DT properties `rx-tx-swap` and `cts-rts-swap`, and with serial aliases `serial`/`hsuart`.

## Risks and Edge Cases

The FIFO console path can lose the current console payload if a TX watermark never appears; it cancels/aborts the command after timeout. DMA RX uses a fixed buffer and immediately re-prepares it after each completion, so bad DMA residue or missing `RX_EOT` can stall reception. `qcom_geni_serial_stop_rx_dma()` polls for `RX_EOT` and falls back to sequencer abort/reset, but failure to see reset completion is not strongly surfaced. Error handling intentionally drops RX data on parity/general-purpose error IRQs, which is safe but coarse. Probe error paths detach power domains but line IDA cleanup is only explicit in some wake-IRQ failure/remove paths, so line allocation paths should be reviewed when adding new failures. Polling paths rely on bounded udelay loops and may be used before full timer infrastructure during early console.

## Test Signals

Useful tests include OF probe for console, UART, and SA8255P compatibles; alias and IDA line allocation; FIFO console boot/earlycon/poll read/write; DMA TX/RX under sustained traffic; RX timeout/EOT/parity/break/overrun paths; RS485 RTS polarity before and after send; CRTSCTS/manual flow transitions; loopback and pin-swap properties; runtime suspend/resume; system suspend/resume with and without console; wake IRQ behavior; DMA preparation failure; firmware load failure; and high baud rates that drive OPP and interconnect vote changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/qcom_geni_serial.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/rda-uart.c -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/rda-uart.c

## Purpose

`rda-uart.c` implements the serial-core driver for the RDA8810PL UART block. It provides up to three `ttyRDA` ports, supports platform/OF probing, interrupt-driven PIO transmit and receive, modem-control bits for RTS/CTS/loopback, regular console support, and OF early console support for `rda,8810pl-uart`.

## Important APIs, Types, and Functions

`struct rda_uart_port` wraps `uart_port` with the controller clock. The global `rda_uart_ports[]` array backs console lookup by line. `rda_uart_read()` and `rda_uart_write()` are the MMIO helpers. The `uart_ops` table maps serial core callbacks to `rda_uart_tx_empty()`, modem control helpers, TX/RX start/stop, startup/shutdown, termios programming, request/release/config/verify hooks, and type reporting.

`rda_uart_set_termios()` is the main configuration routine. It chooses a supported baud, sets the input clock to `baud * 8`, programs 7- or 8-bit characters, stop bits, parity including mark/space, hardware flow control, trigger levels, interrupt masks, and timeout state. `rda_uart_send_chars()` drains x_char and the tty xmit FIFO into the TX register while room remains. `rda_uart_receive_chars()` drains the RX FIFO and maps parity, framing, and overrun bits into tty flags and counters. `rda_interrupt()` acknowledges IRQ cause bits and dispatches RX or TX work.

## Control Flow

Probe obtains the OF serial alias as `pdev->id`, validates it against the three-port limit, maps the MMIO resource through the serial-core request path, obtains the IRQ and clock, initializes the `uart_port`, stores the port in `rda_uart_ports[]`, and calls `uart_add_one_port()`. Startup masks all interrupts, requests the IRQ with `IRQF_NO_SUSPEND`, enables the UART, and enables RX-data and RX-timeout interrupts. TX starts by enabling the TX-data-needed interrupt; the ISR then disables that interrupt while it fills the FIFO and re-enables it if more data remains. RX starts from RX data/timeout IRQs and drains until the RX FIFO count is zero. Shutdown stops TX/RX, disables the UART, and leaves IRQ release to serial core shutdown teardown through the requested IRQ path.

## State and Persistence Behavior

The driver has no persistent storage. Runtime state is per-port MMIO state, the selected clock rate, the global console lookup array, tty counters, xmit FIFO contents owned by serial core, and IRQ mask bits. Hardware FIFO contents and control/trigger settings persist while the UART block remains powered. Console writes temporarily mask interrupts, poll for TX room, write characters, wait for completion, and restore the previous IRQ mask.

## Dependencies and Integration Points

The file depends on platform device resources, OF aliases and compatible matching, clocks, MMIO, IRQs, serial core, tty flip buffers, console and earlycon infrastructure. It integrates with `uart_register_driver()`/`platform_driver_register()` at module init and with the console layer through `rda_uart_console` and `OF_EARLYCON_DECLARE()`.

## Risks and Edge Cases

`rda_uart_tx_empty()` appears to return `TIOCSER_TEMT` when the TX FIFO mask is nonzero, which is counterintuitive if the mask encodes occupancy rather than available space; this should be validated against hardware documentation. TX and console paths busy-wait with `cpu_relax()` and no timeout if the TX FIFO never becomes writable. `rda_uart_stop_rx()` reads one RXTX word before resetting RX FIFO to avoid timeout, which may discard a byte. DMA bits are deliberately cleared even though the register definitions expose DMA completion IRQs. Unsupported CS5/CS6 is coerced to CS7, and no runtime PM or clock prepare/enable calls are present beyond using the clock for rate control.

## Test Signals

Test DT alias bounds, missing clock or zero clock rate, IRQ request failure, 7-bit and 8-bit termios, parity variants, two stop bits, CRTSCTS and manual RTS, loopback, RX timeout and RX data IRQs, parity/frame/overrun flags, TX x_char priority, FIFO reset on stop, console write with active interrupts, early console output, and behavior when TX-ready polling never completes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/rda-uart.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/rp2.c -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/rp2.c

## Purpose

`rp2.c` drives Comtrol RocketPort EXPRESS and INFINITY PCI multiport serial cards. It registers `ttyRP` UARTs, discovers the port count from PCI IDs, initializes one or two ASICs, loads required firmware `rp2.fw` into each port's microcode window, and services all card ports through a shared PCI interrupt.

## Important APIs, Types, and Functions

`struct rp2_card` tracks the PCI device, BAR0/BAR1 mappings, per-card spinlock, number of ports, minor range, initialized count, and SMPTE capability flag. `struct rp2_uart_port` embeds `uart_port` and stores card linkage plus ASIC, port, and microcode MMIO bases. The driver-level `rp2_uart_driver` exposes `ttyRP` ports up to `CONFIG_SERIAL_RP2_NR_UARTS`.

Important helpers include `rp2_alloc_ports()` for monotonically assigning minor ranges, `rp2_rmw*()` register updates, `rp2_mask_ch_irq()` for shared channel IRQ masks, `rp2_init_card()` and `rp2_reset_asic()` for card/ASIC setup, `rp2_init_port()` for channel reset, firmware copy, default termios, modem control, FIFO enable, and TX/RX enable, and `rp2_load_firmware()` for per-port serial-core registration. Runtime UART callbacks implement modem control, termios, RX/TX, startup/shutdown, and verification.

## Control Flow

PCI probe allocates card state, enables the device with pcim helpers, requests BARs, maps BAR0/BAR1, decodes port count from the matched ID, reserves a global minor range, resets the card and ASICs, allocates the port array, requests `rp2.fw`, initializes and registers every port, releases firmware, and finally requests the shared IRQ. Each port's startup flushes FIFOs, enables RX IRQs and modem-status behavior, sets RX trigger level to 1 byte, clears channel status, and unmasks that channel. Shutdown clears break, masks the channel IRQ, and clears channel status.

On interrupt, `rp2_uart_interrupt()` checks ASIC 0 and ASIC 1 when present. `rp2_asic_interrupt()` reads pending channel bits after applying the inverse channel mask and calls `rp2_ch_interrupt()` for each bit. The channel handler clears status bits by writing them back, drains RX FIFO count bytes through `RP2_DATA_BYTE`, translates hardware exception bits into tty flags, handles sysrq, services TX-empty by filling the FIFO through `uart_port_tx_limited()`, and wakes modem-status waiters on DSR/CTS/DCD/RI deltas.

## State and Persistence Behavior

There is no local filesystem persistence apart from dependency on the external firmware file at load time. In-kernel state persists for the lifetime of the PCI device: minor allocation is monotonic and explicitly does not support reclaiming individual hot-unplugged card ranges, card/port structures, mapped BARs, microcode contents, per-port termios, and serial-core FIFOs. Hardware state includes ASIC resets, clock prescaler, channel IRQ masks, firmware bytes, FIFO enable state, baud divisors, flow-control microcode toggles, and modem outputs.

## Dependencies and Integration Points

The driver depends on PCI core, managed PCI resource mapping, Linux firmware loading, serial core, tty flip buffers, shared IRQs, sysrq support, and DMA-independent MMIO PIO. It integrates with many RocketPort PCI product IDs through the `rp2_pci_tbl`, with `MODULE_FIRMWARE("rp2.fw")`, and with serial userspace through `ttyRP` line numbers.

## Risks and Edge Cases

The global minor allocator never frees ranges, so repeated hotplug can exhaust `CONFIG_SERIAL_RP2_NR_UARTS` until module unload. Firmware load is mandatory and probe fails without `rp2.fw`. `rp2_asic_interrupt()` indexes `card->ports[ch]` for each ASIC-local channel; second-ASIC pending bits are read from the second ASIC base but still use the first 16 entries rather than offsetting by `PORTS_PER_ASIC`, which is a point to verify for 32-port cards. A macro typo defines `RP2_TXRX_CTL_TX_TRIG_m` using the RX shift, though this mask is not used. TX-empty status is based on FIFO count because the TXEMPTY bit is described as unreliable unless TX IRQ is enabled.

## Test Signals

Test probe for 2/4/8/16/32-port PCI IDs, insufficient configured UART minors, missing or short firmware, BAR mapping failures, shared IRQ behavior, second ASIC interrupts, RX exception bits, CREAD clearing via `RP2_DUMMY_READ`, XON/XOFF microcode toggles, hardware flow control, modem status changes, break control, startup/shutdown masking, and hot-unplug/remove after partial port registration failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/rp2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/rsci.c -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/rsci.c

## Purpose

`rsci.c` adds Renesas RSCI UART support to the shared SH-SCI serial framework. It provides RSCI-specific register definitions, serial-core operations, SH-SCI port operations, SoC match data for RZ/G3E, RZ/G3L, and RZ/T2H-style ports, and optional early console setup. The implementation focuses on FIFO asynchronous UART mode and delegates common probe, clock, IRQ, console, and PM scaffolding to `sh-sci-common`.

## Important APIs, Types, and Functions

The file exports three `struct sci_of_data` instances: `of_rsci_rzg3e_data`, `of_rsci_rzg3l_data`, and `of_rsci_rzt2h_data`. These bind the RSCI port type, `rsci_port_ops`, `rsci_uart_ops`, and FIFO/error parameters. `rsci_serial_in()` and `rsci_serial_out()` are the MMIO accessors used by both local code and SH-SCI common code. `rsci_set_termios()` programs RSCI CCR registers, baud divisors, FIFO mode, reset bits, RX trigger level, error masks, hardware flow-control/autorts state, and RX enable. `rsci_transmit_chars()` and `rsci_receive_chars()` are the SH-SCI data movers. `rsci_poll_put_char()`, `rsci_prepare_console_write()`, and `rsci_finish_console_write()` support console paths.

## Control Flow

Common SH-SCI probe code selects one of the exported OF data blocks and uses the supplied ops. Termios setup calculates the maximum usable baud from available SCI clocks and sampling-rate constraints, uses `sci_scbrr_calc()` to choose FCK divisor values, enables the port, locks the UART, disables CCR0, programs FIFO mode and CCR2 baud fields, resets FIFOs, applies RX trigger level, updates autorts/CTS state, clears common and FIFO flags, enables receive, and finally enables RX interrupts only when `CREAD` is set. TX starts by enabling TIE and TE together as required by hardware. The transmit worker waits for TDRE, fills TDR while TX room is available, wakes writers, and switches from TIE to TEIE when the xmit FIFO empties. RX checks CSR/FRSR, reserves tty buffer room, reads RDR entries, maps FIFO framing/parity bits into tty flags, handles sysrq, clears RDRF/DR flags, and pushes tty data.

## State and Persistence Behavior

No filesystem persistence exists. Runtime state lives mostly in the common `sci_port` and `uart_port`: selected clocks, GPIO modem controls, autorts flag, FIFO trigger, error masks, and tty buffers. RSCI hardware state is fully register-based: CCR0-CCR4 mode/control, FIFO control, status clear registers, baud divisors, and modem/CTS configuration. `rsci_suspend_regs_size()` returns zero, so this RSCI layer does not add a private suspend-register image; common SCI PM must reestablish relevant state.

## Dependencies and Integration Points

The driver depends on `sh-sci-common.h`, `serial_sci.h`, SH-SCI exported namespace symbols, `serial_mctrl_gpio`, bitfield helpers, MMIO polling, serial core, and tty flip buffers. It integrates with common SCI startup/shutdown/PM/request/release/config/verify functions, OF early console through `scix_early_console_setup()`, and modem GPIO helpers for CTS/DSR/DCD when not handled by hardware.

## Risks and Edge Cases

Only CS7 and CS8 are supported; other sizes are coerced to CS8. The receive path notes that 9-bit data is not supported but masks a 9-bit field, so true multiprocessor/9-bit modes are not implemented. If tty buffers are full, it reads one RDR entry and clears flags to prevent lockup, which drops data. `rsci_set_mctrl()` only sets loopback and does not clear it when `TIOCM_LOOP` is absent. Baud setup currently only considers the standard FCK divisor calculation visible in this file. Error clearing is explicit and must match hardware write-one-to-clear semantics.

## Test Signals

Test all three OF data variants and FIFO sizes, early console setup for each compatible, CS7/CS8 and unsupported size coercion, parity and stop bits, baud divisor accuracy, RX trigger clamping, CRTSCTS/autorts with and without GPIO CTS, modem GPIO reads, loopback set/clear behavior, TX empty/TEIE transition, RX parity/frame/overrun/buffer-full paths, break control, console polling timeout, and suspend/resume through the shared SCI layer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/rsci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/rsci.h -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/rsci.h

## Purpose

`rsci.h` is the small public header connecting the RSCI implementation with the shared SH-SCI serial driver. It declares the RSCI OF data objects that other SH-SCI code can reference when matching Renesas RSCI-compatible devices.

## Important APIs, Types, and Functions

The header includes `sh-sci-common.h` so `struct sci_of_data` is available, then declares `extern struct sci_of_data of_rsci_rzg3e_data`, `of_rsci_rzg3l_data`, and `of_rsci_rzt2h_data`. These objects are defined in `rsci.c` and describe the RSCI port operations, UART operations, FIFO parameters, error masks, and type identifiers for the supported SoC families.

## Control Flow

There is no executable control flow in the header. Its role is compile-time linkage: files that include it can bind OF match entries or common driver tables to the RSCI-specific data blocks exported by `rsci.c`.

## State and Persistence Behavior

The header owns no state and has no persistence behavior. State associated with the declared objects is static data in `rsci.c`.

## Dependencies and Integration Points

The dependency is the SH-SCI common header. The integration point is the common Renesas serial framework's OF data plumbing: RSCI support is kept in a separate C file while the declarations allow shared code to reference its per-compatible descriptors.

## Risks and Edge Cases

The main risk is declaration/definition drift: if an exported `sci_of_data` object is renamed or conditionally removed in `rsci.c`, users of this header will fail to link. The include guard prevents double inclusion, and the header intentionally contains no inline behavior or register definitions.

## Test Signals

Build tests should cover configurations that compile RSCI support together with SH-SCI common code, including early console configurations. Link failures around the three declared OF data objects would be the primary signal of header/API drift.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/rsci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/sa1100.c -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/sa1100.c

## Purpose

`sa1100.c` is the serial-core driver for Intel/StrongARM SA11x0 UART ports. It supports up to three low-density serial ports exposed as `ttySA`, includes platform registration hooks for board code, handles GPIO-backed modem control polling, supports console output, and provides platform suspend/resume integration.

## Important APIs, Types, and Functions

`struct sa1100_port` wraps `uart_port` with a modem-status polling timer, cached modem status, and optional `mctrl_gpios`. `sa1100_ports[]` is the static three-port array initialized by `sa1100_init_ports()`. Board-level hooks `sa1100_register_uart_fns()` and `sa1100_register_uart()` let platform code install modem/PM callbacks and map logical driver indices to hardware UART blocks.

Runtime callbacks in `sa1100_pops` implement TX/RX enable, modem control, break, startup/shutdown, termios, resource request/release, config, and verify. `sa1100_rx_chars()` drains receive data and maps parity/framing/overrun/break status into tty flags. `sa1100_tx_chars()` checks modem status before writing TX data through `uart_port_tx()`. `sa1100_int()` loops over RX, break, and TX status with a pass limit. `sa1100_set_termios()` programs UTCR registers, divisors, masks, and timeout state.

## Control Flow

Module init initializes the static ports, registers the UART driver, and registers the `sa11x0-uart` platform driver. Board code must have populated each active port's membase, mapbase, IRQ, and flags through `sa1100_register_uart()`. Platform probe matches an IORESOURCE_MEM start address to one of the preconfigured ports, initializes modem GPIOs with the no-auto helper, stores drvdata, and calls `uart_add_one_port()`.

Startup requests the port IRQ, clears status, enables RX/TX and RX interrupts, and starts modem-status polling immediately. The interrupt handler reads UTSR0, handles RX FIFO service and receiver-idle clearing, clears break begin/end bits, updates break counters, calls `uart_handle_break()`, and transmits when TX FIFO service is indicated. Shutdown deletes the modem timer, frees the IRQ, and disables UTCR3. Console write disables RX/TX interrupts while forcing TX enabled, writes through polling, waits for the transmitter to become idle, and restores UTCR3.

## State and Persistence Behavior

There is no filesystem persistence. State is static and board-initialized: the `sa1100_ports[]` array, GPIO modem descriptors, timer state, old modem status, serial-core FIFOs, and hardware register state. The polling timer persists only while the port is open and `port.state` is present. Hardware termios and divisor state remain in UTCR registers until reprogrammed or powered down. Suspend/resume delegates to serial core for any probed port.

## Dependencies and Integration Points

The driver depends on SA11x0 machine headers for register/IRQ symbols, platform devices, serial core, tty flip buffers, sysrq, `serial_mctrl_gpio`, console infrastructure, and board-specific platform data callbacks. It integrates with the legacy char major 204 minor range, module aliases for the platform device and char major, and optional `CONFIG_SERIAL_SA1100_CONSOLE`.

## Risks and Edge Cases

The driver relies on board code to pre-register UART mappings; without that, platform probe cannot find a matching static port. Modem status is timer-polled every 250 ms when enabled, so CTS/DCD changes are not instantaneous unless GPIO interrupt support is provided externally. Termios change waits in a busy loop for TX idle before disabling/reprogramming hardware. The ISR uses a pass limit to avoid livelock, which can defer work under interrupt storms. Unsupported character sizes are coerced back toward the old size and then CS8. Resource matching by physical start address is simple but fragile if platform resources do not exactly match board registration.

## Test Signals

Test board registration for UART1/2/3, platform probe matching, missing resource handling, GPIO modem defaults and polling changes, RX parity/frame/overrun/break handling, sysrq, TX wakeups, termios CS7/CS8 and unsupported size fallback, baud divisors, startup/shutdown timer/IRQ lifetime, console setup from bootloader register values, suspend/resume, and ISR pass-limit behavior under continuous RX/TX status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/sa1100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/samsung_tty.c -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/samsung_tty.c

## Purpose

`samsung_tty.c` is the serial-core driver for Samsung S3C/S5P/Exynos-family UARTs plus Apple S5L-compatible UARTs and related derivatives such as ARTPEC and Google GS101. It exposes `ttySAC` ports, supports normal console and early console paths, PIO and optional DMA transfer modes, multiple FIFO geometries, clock-source selection, system suspend/resume, and both platform-ID and OF matching.

## Important APIs, Types, and Functions

`struct s3c24xx_uart_info` describes a hardware family: port type, FIFO masks/shifts/full bits, clock-selection fields, default clock selection, number of baud clocks, register IO width, and fractional divisor support. `struct s3c24xx_serial_drv_data` pairs that info with default platform config and optional per-port FIFO sizes. `struct s3c24xx_uart_dma` stores DMA channels, configs, mappings, descriptors, cookies, buffers, and byte counts. `struct s3c24xx_uart_port` is the per-port serial state: enable flags, PM level, clocks, IRQs, transfer modes, info/config pointers, `uart_port`, and optional DMA state.

Core routines include register helpers `rd_reg*()`/`wr_reg*()`, `s3c24xx_serial_init_port()` for resource/clock/MMIO/IRQ setup, `s3c24xx_serial_set_termios()` for clock/divisor/line-control programming, `s3c24xx_serial_start_tx()` and `s3c24xx_serial_start_next_tx()` for PIO/DMA TX selection, `s3c24xx_serial_rx_irq()` for PIO/DMA RX dispatch, `s3c64xx_serial_handle_irq()` and `apple_serial_handle_irq()` for variant-specific interrupt acknowledgement, and console/earlycon helpers for boot output.

## Control Flow

Probe chooses a port index from OF alias or a static probe counter, resets the static port object, obtains match data, selects S3C64xx-style or Apple ops, applies DT FIFO and IO-width properties, computes `min_dma_size`, maps MMIO, obtains the IRQ, optionally allocates DMA metadata when `dmas` is present, enables controller and baud clocks, masks/clears variant interrupts, resets FIFOs, registers the UART driver on first probe, adds the port, stores drvdata, and disables clocks until serial-core PM enables them.

Startup masks interrupts, requests DMA channels if configured, requests the variant IRQ, resets RX/TX FIFO state, enables PIO RX, and unmasks RX interrupts. TX starts by marking TX enabled, optionally disabling RX for console-flow ports, and either enabling PIO TX IRQs or launching a DMA transfer from an aligned linear xmit FIFO region when size and alignment meet `min_dma_size`. DMA completion advances the xmit FIFO by residue-derived count and starts the next TX batch. RX DMA continuously submits a page-sized buffer; timeout IRQs pause/terminate DMA, copy received bytes to tty, switch to PIO, drain the FIFO, push tty data, clear timeout, and later restart DMA.

Termios programming forces local mode, rejects HUPCL/CMSPAR, chooses the closest allowed baud clock by trying `clk_uart_baudN` sources, switches and enables the best clock, calculates fractional divisor or slot value, writes ULCON/UBRDIV/UDIVSLOT, configures AFC for CRTSCTS, updates timeout and read/ignore masks, and supports custom divisors for `UPF_SPD_CUST`. Suspend uses serial core; resume temporarily enables clocks, resets the port, disables clocks, resumes the UART, and a noirq resume hook restores interrupt masks for wake/console-sensitive variants.

## State and Persistence Behavior

There is no filesystem persistence. Persistent in-kernel state is the static `s3c24xx_serial_ports[]` array, match/config data, clocks, DMA mappings, selected baud clock, transfer modes, IRQ numbers, and serial-core state. Hardware state includes FIFO contents, UCON/ULCON/UMCON/UBRDIV/UDIVSLOT values, interrupt masks, timeout bits, and FIFO trigger/reset configuration. Clocks are intentionally enabled during probe and then disabled so serial-core PM owns active runtime state.

## Dependencies and Integration Points

The driver depends on platform and OF device matching, Samsung serial register definitions, clocks, DMAengine, DMA mapping, serial core, tty flip buffers, console/earlycon, sysrq, ARM fixmap handling for Apple earlycon on ARM64, and system PM. It integrates with many compatibles including Samsung S3C6400/S5PV210/Exynos variants, Apple S5L, Axis ARTPEC-8, Google GS101, and Samsung Exynos8895, and with module init by registering the console before the platform driver.

## Risks and Edge Cases

The DMA paths rely on residue granularity and cache-line alignment; misaligned TX tails intentionally fall back or split to PIO, but errors in residue reporting can over/under-advance xmit data. In `s3c24xx_serial_stop_rx()`, the code pauses `dma->tx_chan` while stopping RX, which looks suspicious and should be verified against the intended `rx_chan`. `s3c24xx_serial_remove()` unregisters the shared UART driver on each remove, which is risky if multiple ports are still present. Console code uses a single global `cons_uart`, so console setup order matters. Clock selection opens and releases candidate clocks on every termios change; failure to find a valid clock silently leaves termios unchanged. Apple and S3C64xx interrupt mask semantics differ, making variant-specific regressions likely when changing common paths.

## Test Signals

Test OF and platform-ID probe for each driver data variant, `reg-io-width` 1/4 and invalid values, DT FIFO override, missing clocks, baud clock selection and fractional divisors, PIO TX/RX, DMA TX/RX thresholds and alignment fallbacks, DMA capability failure, RX timeout handoff from DMA to PIO, parity/frame/overrun/break flags, CRTSCTS/AFC, console and earlycon output/read, Apple MMIO32 earlycon fixmap behavior, suspend/resume/noirq IRQ mask restore, multi-port remove ordering, and custom divisor handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/samsung_tty.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/sb1250-duart.c -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/sb1250-duart.c

## Purpose

`sb1250-duart.c` supports the dual UART blocks integrated into Broadcom/SiByte BCM1250, BCM112x, BCM1480, and related SOCs. It registers legacy `duart` tty ports, handles up to two DUART chips with two channels each, provides interrupt-driven PIO RX/TX, modem control, optional console output, and SOC-dependent register/interrupt address selection.

## Important APIs, Types, and Functions

`struct sbd_duart` owns the two `sbd_port` channels for a DUART, the shared control-register physical base, and a `refcount_t` guarding the shared MMIO reservation. `struct sbd_port` embeds `uart_port`, points back to the DUART, stores the mapped shared-control base, and tracks whether TX is stopped and whether sane defaults have been initialized. Register access is split between per-channel helpers `read_sbdchn()`/`write_sbdchn()` and shared helpers `read_sbdshr()`/`write_sbdshr()`, with an optional SB1 pass-2 workaround that reads mode registers after each access.

The `sbd_ops` UART callbacks implement TX empty, modem control, TX/RX start/stop, modem-status enable, break, startup/shutdown, termios, resource management, config, and verify. `sbd_receive_chars()` drains up to 16 RX entries per pass and maps break/framing/parity/overrun status. `sbd_transmit_chars()` handles x_char and a single FIFO byte per TX-ready IRQ. `sbd_interrupt()` loops over RX, input-change, and TX status. `sbd_probe_duarts()` statically describes available channels from `soc_type`.

## Control Flow

Module and console init both call `sbd_probe_duarts()` once. It determines two or four lines based on SOC type, fills each active `uart_port` with IRQ, 80 MHz-style UART clock, FIFO size, MMIO base, line number, ops, and sysrq capability. Serial module init registers the UART driver and adds each populated port. Config/request paths reserve per-channel MMIO and the shared control region, map both areas, set port type, and run `sbd_init_port()` to reset TX/RX, program 8-bit defaults, clear OPCR/AUXCTL, and mask interrupts.

Startup requests the shared IRQ, drains RX, clears break/input-change state, configures RX/TX interrupt modes to FIFO-available behavior, disables TX, enables RX, marks TX stopped, and enables input-change plus RX interrupts. The interrupt handler reads shared ISR and IMR, filters all DUART status bits, dispatches RX, input-change, and TX handlers, and stops after 16 passes to avoid livelock. Termios drains active TX if needed, disables TX/RX, rewrites mode registers, baud generator, AUX CTS-change setting, read/ignore masks, and then re-enables RX and optionally TX based on current state.

## State and Persistence Behavior

There is no filesystem persistence. State is static in `sbd_duarts[]`, with per-port initialization flags, TX-stopped flags, shared-region reference counts, mapped MMIO pointers, and serial-core state. Hardware state includes mode registers, baud generator, interrupt masks, output port bits, AUX control, FIFOs, and break state. Console setup can map and initialize a port before normal serial registration.

## Dependencies and Integration Points

The driver depends on SiByte SOC headers for register addresses, interrupt numbers, UART bit definitions, and `soc_type`; raw 64-bit MMIO accessors; serial core; tty flip buffers; sysrq; console infrastructure; and legacy tty major/minor allocation. It has compile-time branches for BCM1480 versus SB1250/BCM112x register layouts and optional SB1 pass-2 workarounds.

## Risks and Edge Cases

The driver is highly platform-specific and relies on static SOC globals rather than platform devices. Shared control-region reservation is refcounted, so mismatched request/release paths can leak or prematurely release the shared region. The code uses bounded polling loops for RX/TX drain and console output; if hardware never reaches ready/empty, data can be dropped after timeout or console can stall for the loop duration. TX interrupt handling writes only one byte per pass, which is simple but may limit throughput. CS5/CS6 are unsupported and leave part of the previous mode unchanged. There is no runtime PM or hotplug discovery.

## Test Signals

Test SOC-type based two-line and four-line enumeration, request/release of two channels sharing one control region, SB1 workaround builds, startup/shutdown IRQ behavior, RX status mapping for break/frame/parity/overrun, modem input-change wakeups, DTR/RTS/loopback output bits, termios baud bounds and CS7/CS8 behavior, CREAD disable, CRTSCTS AUX updates, console setup/write/restore of TX interrupt state, and init/exit removing ports in reverse order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/sb1250-duart.c -->
