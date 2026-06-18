# Research: subset-b-005450 tty and 8250 serial sources

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/pty.c -->
# sources/distributed-fs/ceph-client/drivers/tty/pty.c

## Purpose
Implements Linux pseudoterminal support for both legacy BSD PTYs and Unix98 `/dev/ptmx`/`devpts` PTYs. It creates paired `tty_struct` objects, wires master/slave data paths through flip buffers, exposes PTY ioctls, manages packet mode and window-size signaling, and registers the `ptm`/`pts` tty drivers plus the `/dev/ptmx` character device.

## Important APIs, types, and functions
- Global Unix98 state: `ptm_driver`, `pts_driver`, `devpts_mutex`, and `ptmx_cdev`.
- Common tty operations: `pty_open()`, `pty_close()`, `pty_write()`, `pty_write_room()`, `pty_flush_buffer()`, `pty_unthrottle()`, `pty_resize()`, `pty_set_termios()`, `pty_start()`, and `pty_stop()`.
- Pair allocation and lifetime: `pty_common_install()` allocates both tty ports and the peer tty, links them via `tty->link`, sets buffer limits, and bumps driver refs; `pty_cleanup()` releases the tty port.
- Ioctls: `pty_set_lock()`, `pty_get_lock()`, `pty_set_pktmode()`, `pty_get_pktmode()`, and `pty_signal()` back `TIOCSPTLCK`, `TIOCGPTLCK`, `TIOCPKT`, `TIOCGPKT`, `TIOCGPTN`, and `TIOCSIG`.
- Legacy path: `legacy_pty_init()`, `pty_install()`, `pty_remove()`, `master_pty_ops_bsd`, and `slave_pty_ops_bsd`.
- Unix98 path: `ptmx_open()`, `ptm_open_peer()`, `ptm_open_peer_file()`, `ptm_unix98_lookup()`, `pts_unix98_lookup()`, `pty_unix98_install()`, `pty_unix98_remove()`, `ptm_unix98_ops`, `pty_unix98_ops`, and `unix98_pty_init()`.

## Control flow
Initialization runs from `device_initcall(pty_init)`, first registering legacy PTYs when enabled, then Unix98 drivers and `/dev/ptmx`. Opening `/dev/ptmx` allocates a tty file, acquires a devpts instance, reserves an index, initializes the master tty under `tty_mutex`, locks the slave with `TTY_PTY_LOCK`, creates the devpts slave dentry, and opens the master. Slave lookup is deliberately devpts-mediated: `pts_unix98_lookup()` returns the master-private tty only when the master exists.

I/O is a direct paired-tty path. `pty_write()` inserts bytes into the peer port's flip buffer and pushes it. `pty_write_room()` reports the peer buffer's available space. The unthrottle path wakes writers on the peer and intentionally keeps `TTY_THROTTLED` set so line disciplines keep issuing unthrottle notifications. Packet mode state changes are latched in `tty->ctrl.pktstatus` and wake the master read side on flow-control, ioctl, stop/start, or flush events.

Close marks I/O error, wakes local wait queues, clears packet mode, marks the peer as closed, and for a master close kills the devpts node and vhangups the slave. Last-close removal releases devpts index and fs info for Unix98 PTYs.

## State and persistence behavior
State lives in tty flags (`TTY_IO_ERROR`, `TTY_OTHER_CLOSED`, `TTY_PTY_LOCK`, `TTY_THROTTLED`), `tty->ctrl.packet`/`pktstatus`, paired `tty_port` buffers, devpts indexes and dentries, tty refcounts, and driver arrays for legacy PTYs. There is no persistent storage beyond kernel device model/devpts state. Window size is mirrored to both ends and foreground process groups receive `SIGWINCH`.

## Dependencies and integration points
This file integrates with the tty core, line disciplines, devpts, VFS file allocation/opening, cdev registration, poll wait queues, signal delivery, compat ioctl handling, and tty console/device class registration. Unix98 behavior depends on `CONFIG_UNIX98_PTYS`; legacy BSD support depends on `CONFIG_LEGACY_PTYS` and `CONFIG_LEGACY_PTY_COUNT`.

## Risks and edge cases
- Pair lifetime depends on tty core locking and refcounts; stale `tty->link` assumptions are guarded in several paths but remain central to correctness.
- Packet mode uses ctrl spinlocks and memory ordering; missed packet status wakeups could break applications that depend on `TIOCPKT`.
- `ptmx_open()` has several staged cleanup paths; devpts index/fs references must stay paired with tty release on every failure.
- Legacy driver arrays are updated manually in `pty_common_install()`/`pty_remove()`.
- Slave open rules reject locked slaves and opens after peer closure; regressions are user-visible in pty allocation/open behavior.

## Test signals
Useful signals include Unix98 pty allocation/open/close tests through `/dev/ptmx` and `/dev/pts/N`, `TIOCSPTLCK`/`TIOCGPTLCK`, `TIOCPKT` status events for stop/start/flush/ioctl, `TIOCSWINSZ`/`SIGWINCH`, `TIOCSIG`, `TIOCGPTN`, `ptm_open_peer()`, namespace/devpts mount coverage, and stress around concurrent close, hangup, and slave open.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/pty.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/rpmsg_tty.c -->
# sources/distributed-fs/ceph-client/drivers/tty/rpmsg_tty.c

## Purpose
Provides a tty frontend for RPMsg endpoints named `rpmsg-tty`, creating `/dev/ttyRPMSG<N>` devices so userspace can exchange RPMsg messages through standard tty read/write paths.

## Important APIs, types, and functions
- `struct rpmsg_tty_port` embeds `struct tty_port`, stores an IDR index, and points at the backing `struct rpmsg_device`.
- ID allocation is handled by global `tty_idr` under `idr_lock`.
- TTY operations are `rpmsg_tty_install()`, `rpmsg_tty_open()`, `rpmsg_tty_close()`, `rpmsg_tty_write()`, `rpmsg_tty_write_room()`, `rpmsg_tty_hangup()`, and `rpmsg_tty_cleanup()`.
- RPMsg integration is through `rpmsg_tty_probe()`, `rpmsg_tty_cb()`, `rpmsg_tty_remove()`, `rpmsg_driver_tty_id_table`, and `rpmsg_tty_rpmsg_drv`.
- Driver lifetime is `rpmsg_tty_init()`/`rpmsg_tty_exit()`.

## Control flow
Module init allocates a dynamic tty driver for up to 32 raw tty devices, disables canonical echo/output postprocessing by default, registers the tty driver, then registers the RPMsg driver. When a remote processor announces `rpmsg-tty`, probe allocates a port, assigns an ID, initializes the tty port with destructor operations, registers the tty device, stores `rpdev`, and binds the cport as device driver data.

RX runs from the RPMsg callback. Non-empty inbound payloads are copied into the tty flip buffer and pushed; truncation is reported with ratelimited logging. TX runs from tty `.write`: it queries RPMsg endpoint MTU, clips the tty write to one RPMsg message, and uses `rpmsg_trysend()` so tty writers are not indefinitely blocked by unavailable RPMsg buffers.

Removal hangs up users, unregisters the tty device, and drops the tty port reference. The port destructor removes the IDR entry and frees the allocation.

## State and persistence behavior
State is per live RPMsg channel: IDR slot, `tty_port` reference count, registered tty device, and `rpdev` pointer. There is no persistent state. The driver intentionally implements no hardware or software flow control; write capacity is the RPMsg MTU and backpressure is surfaced as short writes or `rpmsg_trysend()` errors.

## Dependencies and integration points
Depends on the RPMsg bus and endpoint MTU/send APIs, tty core/tty_port helpers, flip buffers, IDR, and module registration. Userspace observes dynamic `ttyRPMSG<N>` devices.

## Risks and edge cases
- `rpmsg_tty_install()` assumes `idr_find()` returns a live cport for the tty index; mismatched unregister/open races would be serious.
- RX truncation can occur if tty flip buffers are full; the driver logs but drops excess data.
- `rpmsg_trysend()` can return `-ENOMEM`, so callers must handle transient write failures.
- No flow control means high-throughput remote senders can overrun tty buffers.

## Test signals
Probe/remove with a remote endpoint named `rpmsg-tty`, creation of `ttyRPMSG<N>`, open/close/hangup behavior, RX payload delivery including zero-length rejection and truncation logging, MTU-limited writes, and retry behavior when RPMsg buffers are unavailable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/rpmsg_tty.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serdev/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/tty/serdev/Kconfig

## Purpose
Defines configuration for the serial device bus and its tty-port controller bridge.

## Important APIs, types, and functions
- `menuconfig SERIAL_DEV_BUS`: tristate core support for devices connected over serial ports.
- `config SERIAL_DEV_CTRL_TTYPORT`: boolean tty-port controller support for using common tty drivers as serdev controllers.

## Control flow
The Kconfig block exposes the serdev bus as a selectable feature. When `SERIAL_DEV_BUS` is enabled, `SERIAL_DEV_CTRL_TTYPORT` becomes available, depends on `TTY`, depends on the bus not being modular, and defaults to `y`.

## State and persistence behavior
No runtime state. The file controls compile-time inclusion of `core.o` and `serdev-ttyport.o` through the matching Makefile.

## Dependencies and integration points
Integrates the serdev subsystem with kernel configuration. The tty-port controller option is intentionally built-in only when the serdev core is built-in, avoiding a bool-to-module mismatch.

## Risks and edge cases
Disabling `SERIAL_DEV_CTRL_TTYPORT` while enabling `SERIAL_DEV_BUS` leaves serdev core available but prevents tty serial ports from acting as controllers. The dependency `SERIAL_DEV_BUS != m` means module builds of the core do not get this bool controller path.

## Test signals
Kconfig coverage should check built-in, module, and disabled combinations for `SERIAL_DEV_BUS`, and verify that `serdev-ttyport.o` only appears when `CONFIG_SERIAL_DEV_CTRL_TTYPORT=y`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serdev/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serdev/Makefile -->
# sources/distributed-fs/ceph-client/drivers/tty/serdev/Makefile

## Purpose
Builds the serdev core object and the optional tty-port controller object based on Kconfig selections.

## Important APIs, types, and functions
- `serdev-objs := core.o` defines the composite serdev core module/built-in object.
- `obj-$(CONFIG_SERIAL_DEV_BUS) += serdev.o` includes core serdev support.
- `obj-$(CONFIG_SERIAL_DEV_CTRL_TTYPORT) += serdev-ttyport.o` includes the tty-port bridge.

## Control flow
Kbuild compiles `core.o` into `serdev.o` when the bus is selected, and separately compiles `serdev-ttyport.o` when the tty-port controller is enabled.

## State and persistence behavior
No runtime state. This is build metadata only.

## Dependencies and integration points
Directly mirrors `Kconfig` and drives inclusion of `core.c` and `serdev-ttyport.c` in the tty driver subtree.

## Risks and edge cases
The Makefile is simple; the main risk is config skew where serdev bus code is enabled without the bridge expected by serial drivers or board descriptions.

## Test signals
Kernel build matrix should verify `CONFIG_SERIAL_DEV_BUS=y/m` creates `serdev.o`, and `CONFIG_SERIAL_DEV_CTRL_TTYPORT=y` creates `serdev-ttyport.o`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serdev/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serdev/core.c -->
# sources/distributed-fs/ceph-client/drivers/tty/serdev/core.c

## Purpose
Implements the serial device bus core: controller/device allocation, bus matching, OF/ACPI enumeration, exported client APIs for open/close/write/baud/parity/flow/modem/break control, driver registration, runtime PM, and power-domain integration.

## Important APIs, types, and functions
- Bus/device model: `serdev_bus_type`, `serdev_device_type`, `serdev_ctrl_type`, `serdev_device_match()`, `serdev_device_uevent()`, `modalias_show()`.
- Device lifecycle: `serdev_device_alloc()`, `serdev_device_add()`, `serdev_device_remove()`, `serdev_device_put()` via release, and single-slave storage in `ctrl->serdev`.
- Controller lifecycle: `serdev_controller_alloc()`, `serdev_controller_add()`, `serdev_controller_remove()`, controller release through `ctrl_ida`.
- Client APIs: `serdev_device_open()`, `serdev_device_close()`, `devm_serdev_device_open()`, `serdev_device_write_buf()`, `serdev_device_write()`, `serdev_device_write_wakeup()`, `serdev_device_write_flush()`, `serdev_device_set_baudrate()`, `serdev_device_set_flow_control()`, `serdev_device_set_parity()`, `serdev_device_wait_until_sent()`, `serdev_device_get_tiocm()`, `serdev_device_set_tiocm()`, and `serdev_device_break_ctl()`.
- Enumeration: `of_serdev_register_devices()`, `of_find_serdev_controller_by_node()`, `serdev_acpi_get_uart_resource()`, `acpi_serdev_register_devices()`, `acpi_serdev_check_resources()`, and blacklist/quirk paths.
- Driver registration: `__serdev_device_driver_register()`, `serdev_drv_probe()`, `serdev_drv_remove()`, and `serdev_drv_shutdown()`.

## Control flow
`postcore_initcall(serdev_init)` registers the `serial` bus before serial drivers create controllers. A controller driver allocates a controller, sets operations, then calls `serdev_controller_add()`. The core adds the controller device, enables runtime PM, then enumerates child serdev devices from devicetree children or ACPI UARTSerialBus resources. Device add enforces the current single-slave limit by checking `ctrl->serdev`.

Client drivers match by ACPI or OF modalias. Probe attaches a PM domain with power-on semantics, then calls the serdev driver's `probe`. Serdev clients open the controller through `ctrl->ops->open`, then take a runtime PM reference; close releases runtime PM and calls controller close.

Synchronous write serializes through `serdev->write_lock`, repeatedly calls controller `write_buf`, advances the buffer by accepted bytes, and waits on `write_comp` until `serdev_device_write_wakeup()` is called by the controller side.

## State and persistence behavior
State is transient kernel device-model state: controller IDs from `ctrl_ida`, controller/device references, `ctrl->serdev`, completions and mutexes per serdev device, runtime PM state, ACPI enumeration marks, and OF/ACPI fwnodes. No persistent storage is used.

## Dependencies and integration points
Depends on Linux driver core, OF and ACPI matching/enumeration, PM domains, runtime PM, property APIs, IDA allocation, and serdev controller operation callbacks usually supplied by `serdev-ttyport.c` or hardware-specific controllers. ACPI has Apple-specific fallback behavior for empty resource templates and a blacklist for known problematic INT3511/INT3512 devices.

## Risks and edge cases
- Only one serdev child per controller is supported; additional children return `-EBUSY`.
- `serdev_device_write()` requires client `write_wakeup`; without it, synchronous writes fail with `-EINVAL` or can time out.
- `serdev_controller_add()` treats absence of both OF and ACPI devices as `-ENODEV`, except DT graph connector cases.
- ACPI scan depth and resource matching must avoid claiming unrelated UARTSerialBus devices.
- Runtime PM ordering matters: open first calls controller open, then gets PM; failures must close the controller.

## Test signals
Tests should cover OF child enumeration, ACPI UARTSerialBus enumeration and blacklists, single-child busy rejection, modalias uevents, open/close runtime PM reference behavior, synchronous write completion/timeout/signal paths, and exported parameter setters returning `-EOPNOTSUPP` when controller callbacks are missing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serdev/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serdev/serdev-ttyport.c -->
# sources/distributed-fs/ceph-client/drivers/tty/serdev/serdev-ttyport.c

## Purpose
Bridges an existing `tty_port` and `tty_driver` into a serdev controller, allowing serial-attached device drivers to use common tty/UART drivers as their transport.

## Important APIs, types, and functions
- `struct serport` stores the tty port, opened `tty_struct`, tty driver, tty index, and `SERPORT_ACTIVE` flag.
- TTY-port callbacks: `ttyport_receive_buf()` forwards RX bytes to `serdev_controller_receive_buf()`, and `ttyport_write_wakeup()` forwards write wakeups to serdev.
- Serdev controller operations: `ttyport_write_buf()`, `ttyport_write_flush()`, `ttyport_open()`, `ttyport_close()`, `ttyport_set_baudrate()`, `ttyport_set_flow_control()`, `ttyport_set_parity()`, `ttyport_wait_until_sent()`, `ttyport_get_tiocm()`, `ttyport_set_tiocm()`, and `ttyport_break_ctl()`.
- Public registration: `serdev_tty_port_register()` and `serdev_tty_port_unregister()`.

## Control flow
Registration allocates a serdev controller with embedded `struct serport`, records the tty driver/index, installs `client_ops` and `client_data` on the tty port, and calls `serdev_controller_add()`. If controller add fails, the tty port is restored to default client ops and the controller ref is dropped.

When a serdev client opens, `ttyport_open()` initializes the tty with `tty_init_dev()`, validates driver open/close callbacks, calls tty open, unlocks the tty, normalizes termios to raw 8-bit, hardware-flow-control-enabled, carrier-ignore mode, then sets `SERPORT_ACTIVE`. RX bytes are only forwarded while active. Writes set `TTY_DO_WRITE_WAKEUP` and call the tty driver's `.write`. Close clears active, calls tty close under the tty lock, and releases the tty struct.

## State and persistence behavior
State is per controller: active flag, currently opened tty pointer, and tty port client callbacks. No persistent state. Termios is deliberately reprogrammed on open to a known raw baseline.

## Dependencies and integration points
Depends on tty core internals (`tty_init_dev`, driver ops, termios updates, wait queues, modem-control callbacks), `tty_port_client_operations`, and serdev controller core callbacks. It is the integration point that lets normal serial drivers expose serdev children.

## Risks and edge cases
- The bridge assumes the underlying tty driver supplies compatible open/close/write semantics without a userspace file.
- RX and write wakeup are gated by `SERPORT_ACTIVE`; races around open/close must not deliver stale data to serdev clients.
- `ttyport_set_parity()` verifies the resulting termios because hardware may silently reject mark/space parity.
- Registration mutates `port->client_ops`; unregister must always restore defaults.

## Test signals
Register/unregister a tty port as a serdev controller, open/close from a serdev client, RX forwarding while active and suppression while inactive, write wakeup completion, baud/flow/parity termios changes, modem control and break callback propagation, and failure cleanup when controller add fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serdev/serdev-ttyport.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/21285.c -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/21285.c

## Purpose
Implements a UART driver for the Intel/DEC 21285 Footbridge StrongARM core logic serial port, exposing one `ttyFB` uart_core port and optional console support.

## Important APIs, types, and functions
- UART ops: `serial21285_ops` with TX/RX enable/disable, IRQ startup/shutdown, termios, break, resource request/release, config, and verify callbacks.
- IRQ handlers: `serial21285_rx_chars()` and `serial21285_tx_chars()`.
- State helpers encode TX/RX enabled bits in `uart_port.private_data`: `is_enabled()`, `enable()`, `disable()`.
- Console support: `serial21285_console_putchar()`, `serial21285_console_write()`, `serial21285_get_options()`, `serial21285_console_setup()`, and `rs285_console_init()`.
- Driver lifetime: `serial21285_init()` registers `serial21285_reg` and adds `serial21285_port`; exit removes it.

## Control flow
Module init computes `uartclk` from `mem_fclk_21285`, registers a one-port uart driver, then adds the static port. Startup marks TX/RX enabled and requests separate RX and TX IRQs. RX IRQ drains up to 256 bytes while the UART flag says data is present, updates icount/status, maps parity/frame errors to tty flags, inserts chars, and pushes the flip buffer. TX IRQ sends up to 256 bytes while the UART can accept data. Termios recomputes baud divisor, word length, parity, stop bits, FIFO enable, read/ignore masks, and rewrites UART control registers while holding the port lock.

## State and persistence behavior
The driver has one static `uart_port`, uses private-data bits for TX/RX IRQ state, and stores uart_core icount/read/ignore masks. Hardware state is in memory-mapped 21285 CSR registers. No persistent state.

## Dependencies and integration points
Depends on ARM Footbridge machine headers and CSR register definitions, uart_core, tty flip buffers, console core, and fixed IRQs `IRQ_CONRX`/`IRQ_CONTX`. It uses major 204/minor 4 and `ttyFB`.

## Risks and edge cases
- `private_data` is used as a small bit field, so it must not be repurposed elsewhere.
- RX ignores break recognition and forces local carrier/no modem controls in termios.
- Divisor calculation subtracts one before programming hardware; wrong clock assumptions produce baud error.
- Startup failure after RX IRQ allocation must free RX IRQ if TX IRQ request fails.

## Test signals
Boot and module init on Footbridge hardware, console output/input when enabled, baud/word/parity/stop changes, RX error accounting for parity/frame/overrun, TX wakeups under sustained writes, resource request/release, and `TIOCSSERIAL` verification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/21285.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250.h -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250.h

## Purpose
Provides shared internal declarations, capability/bug flags, DMA state, helper functions, and cross-file prototypes for the 8250/16550 serial driver family.

## Important APIs, types, and functions
- `struct uart_8250_dma` stores DMA callbacks, filter parameters, slave configs, channels, DMA addresses, cookies, RX buffer, sizes, and running/error flags.
- `struct old_serial_port` and `struct serial8250_config` model legacy and per-UART configuration.
- Capability flags include FIFO, EFR, sleep, AFE, UUE, RTOIE, hidden FIFO, runtime PM, IrDA, mini-UART, and no-TEMT behavior.
- Bug flags include quotient, TXEN, missing MSR, THRE, and TX race workarounds.
- Helpers wrap serial in/out, LSR saved flags, 16C950 ICR access, divisor latch access, THRI set/clear, MCR/MSR to TIOCM conversion, GPIO-backed modem control, DMA stubs/real prototypes, RSA/Fintek/OMAP conditionals, and NS16550A high-speed mode.
- Shared declarations include `serial8250_reg`, `serial8250_register_ports()`, `serial8250_setup_port()`, `serial8250_get_port()`, `serial8250_em485_*`, DMA functions, PNP/RSA hooks, and ISA config hooks.

## Control flow
This header is included by the generic core, DMA implementation, and many platform drivers. Inline helpers centralize register access and enforce lock assumptions for interrupt-enable changes. Conditional sections compile real DMA/PNP/RSA helpers only when corresponding config options are enabled; otherwise stubs return neutral errors/no-ops.

## State and persistence behavior
No standalone runtime state except inline mutations of caller-owned `struct uart_8250_port`. The header defines how LSR sticky flags, DMA running flags, modem-control GPIO state, and capabilities are represented.

## Dependencies and integration points
Depends on `linux/serial_8250.h`, `serial_core`, DMA engine APIs, and `serial_mctrl_gpio`. It is the internal ABI between 8250 core, platform glue, DMA, RS485 emulation, and legacy probe modules.

## Risks and edge cases
- Inline helpers assume correct port locking, especially `serial8250_set_THRI()` and `serial8250_clear_THRI()`.
- Capability and bug bits are shared across many drivers; collisions or mis-set flags alter core behavior globally for a port.
- DMA stubs returning `-1` must be interpreted consistently by callers.
- GPIO-backed MCR composition combines register and GPIO state and can confuse drivers that assume pure register state.

## Test signals
Compile coverage across DMA/non-DMA, PNP, RSA, OMAP, Fintek, and GPIO modem-control configs; runtime checks for THRI transitions under lockdep; LSR sticky flag preservation; MCR/MSR conversion correctness; and platform driver builds that consume the shared prototypes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_accent.c -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_accent.c

## Purpose
Registers fixed legacy I/O-port definitions for Accent Async 8250-compatible serial cards through the platform `serial8250` driver.

## Important APIs, types, and functions
- `accent_data[]` declares two ports at I/O bases `0x330` and `0x338`, both IRQ 4, using `SERIAL8250_PORT`.
- `accent_device` is a `platform_device` named `serial8250` with ID `PLAT8250_DEV_ACCENT`.
- `accent_init()` registers the platform device.

## Control flow
At module init, the platform device is registered. The generic 8250 platform driver consumes the `plat_serial8250_port` array and registers the two legacy ports.

## State and persistence behavior
Static platform data only. No remove path is defined in this tiny probe module, so lifetime is effectively module/device lifetime.

## Dependencies and integration points
Depends on `serial_8250.h`, `8250.h` macros, and the generic `serial8250` platform-device consumer.

## Risks and edge cases
Hard-coded I/O bases and IRQs can conflict with other hardware. Shared IRQ behavior and resource ownership are delegated to generic 8250 handling.

## Test signals
Module load should create a `serial8250` platform device with two expected ports; verify no I/O resource conflicts and that the generic 8250 driver probes both entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_accent.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_acorn.c -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_acorn.c

## Purpose
Supports Acorn expansion-card 8250-compatible serial boards, mapping ecard resources and registering each UART with the 8250 core.

## Important APIs, types, and functions
- `struct serial_card_type` describes port count, UART clock, resource type, and per-port offsets.
- `struct serial_card_info` stores port line numbers and mapped virtual address.
- `serial_card_probe()` maps the ecard resource and calls `serial8250_register_8250_port()` for each port.
- `serial_card_remove()` unregisters registered ports.
- `serial_cids[]` matches Atomwide and Serport products; `serial_card_driver` registers with the ecard bus.

## Control flow
On ecard probe, the driver allocates info, maps the card resource, builds a reusable `uart_8250_port` template with shared IRQ, memory I/O, regshift 2, and card-specific clock, then iterates over offsets to register each UART. Removal unregisters positive line numbers and frees the info structure.

## State and persistence behavior
Per-card state stores mapped resource and registered 8250 line numbers. Hardware mapping persists for card lifetime. No persistent storage.

## Dependencies and integration points
Depends on ARM ecard infrastructure, 8250 registration APIs, memory-mapped UART access, and shared IRQ handling through generic 8250.

## Risks and edge cases
- Probe does not unwind ports if a later `serial8250_register_8250_port()` fails; stored negative line numbers are skipped on removal.
- `ecardm_iomap()` mapping lifetime is tied to ecard APIs, while only `info` is freed explicitly.
- Fixed offsets/clocks must match the specific expansion-card type.

## Test signals
Probe/remove on Atomwide and Serport cards, all expected port offsets registered, shared IRQ operation, failure injection for mapping/allocation/partial port registration, and tty data transfer on each port.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_acorn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_aspeed_vuart.c -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_aspeed_vuart.c

## Purpose
Implements the BMC-side Aspeed virtual UART, an 8250-like device that exposes a host LPC UART endpoint and lets BMC userspace configure host I/O address, SIRQ, and polarity.

## Important APIs, types, and functions
- `struct aspeed_vuart` stores device, 8250 line, unthrottle timer, and registered 8250 port pointer.
- Sysfs attributes: `lpc_address`, `sirq`, and `sirq_polarity`.
- Hardware control helpers: `aspeed_vuart_set_lpc_address()`, `aspeed_vuart_set_sirq()`, `aspeed_vuart_set_sirq_polarity()`, `aspeed_vuart_set_enabled()`, and `aspeed_vuart_set_host_tx_discard()`.
- UART callbacks: `aspeed_vuart_startup()`, `aspeed_vuart_shutdown()`, `aspeed_vuart_throttle()`, `aspeed_vuart_unthrottle()`, and custom `aspeed_vuart_handle_irq()`.
- Probe/remove: `aspeed_vuart_probe()` and `aspeed_vuart_remove()` with OF matches for AST2400/AST2500 VUART.

## Control flow
Probe allocates private data, creates sysfs controls, reads port properties and clock, sets optional current-speed divisor, installs custom startup/shutdown/throttle/IRQ callbacks, registers an 8250 port of type `PORT_ASPEED_VUART`, then configures optional SIRQ polarity sensing, LPC I/O address, SIRQ number/polarity, enables the VUART, and initially discards host TX until the tty is opened.

The IRQ handler reads IIR/LSR, checks flip-buffer space before draining RX, and if there is no space disables receive-related IER bits and arms a timer to retry unthrottle after `HZ/10`. If space exists, it reads up to the available space or 256 chars, pushes the flip buffer, services modem status, and sends TX chars when THRE is set. Startup enables host TX delivery after normal 8250 startup; shutdown discards host TX before normal shutdown.

## State and persistence behavior
Runtime state includes sysfs-programmed LPC address/SIRQ registers, enabled bit, host TX discard bit, receive interrupt throttle state in IER, and a retry timer. These hardware settings persist while the device is bound but are not stored across reboot.

## Dependencies and integration points
Depends on platform/OF resources, optional clocks, syscon/regmap for polarity auto-sensing, tty flip-buffer availability, and serial8250 registration/core IRQ helpers. It exposes policy knobs to BMC userspace through sysfs.

## Risks and edge cases
- Sysfs attributes directly mutate host-visible LPC/SIRQ registers; invalid policy can break host console discovery.
- RX throttling depends on flip-buffer space and timer retry; bad interactions can cause dropped host bytes or stuck receive interrupts.
- Error paths after `serial8250_register_8250_port()` should unregister the port; current later configuration failures jump only to sysfs removal, so line cleanup is a point to audit.
- `UART_BUG_TXRACE` and `UPF_NO_THRE_TEST` indicate hardware quirks that should not be removed casually.

## Test signals
OF probe with/without clock-frequency, sysfs read/write validation for address/SIRQ/polarity, host-side LPC console enumeration, RX stress that fills tty buffers and verifies throttle/unthrottle recovery, startup/shutdown host TX discard behavior, and removal cleanup including timer deletion and port unregister.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_aspeed_vuart.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_bcm2835aux.c -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_bcm2835aux.c

## Purpose
Provides an 8250-based driver for the Raspberry Pi BCM2835 auxiliary mini UART, including clock handling, ACPI register-offset fixup, RS485 support, suspend/resume, and early console setup.

## Important APIs, types, and functions
- `struct bcm2835aux_data` stores clock, 8250 line, and cached CNTL register.
- RS485 callbacks: `bcm2835aux_rs485_start_tx()` and `bcm2835aux_rs485_stop_tx()`.
- Probe/remove: `bcm2835aux_serial_probe()` and `bcm2835aux_serial_remove()`.
- PM helpers: `bcm2835aux_can_disable_clock()`, `bcm2835aux_suspend()`, and `bcm2835aux_resume()`.
- Early console: `early_bcm2835aux_setup()`.

## Control flow
Probe allocates private data, initializes an 8250 template with mini-UART capabilities, fixed type/port flags, RS485 emulation callbacks, optional software node for ACPI reg offset, reads port properties, enables the clock, doubles the clock rate because the hardware divider is 8 while 8250 expects 16, and registers the 8250 port. Removal unregisters the port, disables the clock, and removes the software node.

RS485 TX start optionally disables RX during transmit and drives RTS with inverted semantics appropriate to the mini-UART MCR. TX stop restores RTS and RX enable. Suspend suspends the 8250 port and disables the clock only if wakeup/console constraints allow; resume re-enables the clock when needed and resumes the port.

## State and persistence behavior
Per-device state is the cached CNTL register, clock handle, and 8250 line. The cached CNTL value tracks RX/TX enable changes for RS485. No persistent storage.

## Dependencies and integration points
Depends on platform/OF/ACPI matching, `uart_read_port_properties()`, clk APIs, serial8250 core, RS485 emulation helpers, console suspend policy, and earlycon registration for `brcm,bcm2835-aux-uart`.

## Risks and edge cases
- Incorrect clock doubling yields wrong baud rates.
- ACPI firmware may describe the shared auxiliary block rather than the mini-UART base, so the software-node `reg-offset` must be applied.
- RS485 and future auto-RTS support are mutually sensitive; comments warn not to enable auto flow control simultaneously with RS485.
- Clock disable is unsafe for wakeup-enabled devices or active non-suspended consoles.

## Test signals
OF and ACPI probe, baud accuracy, RS485 direction/RX suppression behavior, suspend/resume with wakeup and console combinations, earlycon output, and software-node cleanup on probe failures/removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_bcm2835aux.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_bcm7271.c -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_bcm7271.c

## Purpose
Adds Broadcom STB BCM7271/BCM7278 ns16550a-compatible UART support on top of 8250, including optional private UDMA hardware, baud clock mux selection, RX-timeout erratum handling, debugfs counters, and system sleep support.

## Important APIs, types, and functions
- `struct brcmuart_priv` stores line, baud mux clock/rates, hrtimer, 8250 port, DMA enable/state, register windows, coherent RX/TX buffers, debugfs counters, and saved modem state.
- DMA register helpers: `udma_readl()`, `udma_writel()`, `udma_set()`, `udma_unset()`.
- DMA lifecycle/data path: `brcmuart_arbitration()`, `brcmuart_init_dma_hardware()`, `start_rx_dma()`, `stop_rx_dma()`, `stop_tx_dma()`, `brcmuart_tx_dma()`, `brcmuart_rx_buf_done_isr()`, `brcmuart_rx_isr()`, `brcmuart_tx_isr()`, and `brcmuart_isr()`.
- UART callbacks: `brcmuart_startup()`, `brcmuart_shutdown()`, `brcmstb_set_termios()`, `brcmuart_handle_irq()`, `brcmuart_throttle()`, and `brcmuart_unthrottle()`.
- Clock/error helpers: `init_real_clk_rates()`, `find_quot()`, `set_clock_mux()`, and `brcmuart_hrtimer_func()`.
- Probe/remove/PM: `brcmuart_probe()`, `brcmuart_remove()`, `brcmuart_suspend()`, `brcmuart_resume()`, `brcmuart_init()`, and `brcmuart_deinit()`.

## Control flow
Probe maps named resources. A single UART register window is enough for PIO; all five windows enable the private UDMA path if arbitration and revision checks pass. It configures an 8250 template with custom IRQ, startup/shutdown, throttle, unthrottle, and termios callbacks, optional baud mux clock, and DMA buffers when enabled. After registering the 8250 port, it requests the DMA IRQ if needed and creates debugfs stats.

Startup temporarily hides `up->dma` so generic 8250 startup does not allocate DMA engine channels, then, if private DMA is enabled, disables normal RX data interrupts, installs private TX DMA callback state, initializes the UDMA block, and starts RX DMA. RX DMA uses two 4 KiB buffers and handles buffer-ready interrupts in sequence, inserting data into tty flip buffers and tracking full/partial/error counters. TX DMA copies data out of the uart xmit FIFO into a coherent buffer and kicks UDMA.

Termios stops RX DMA while changing clock/8250 settings, chooses the best mux rate for the requested baud, computes a character wait timeout, then restarts RX DMA. The IRQ handler works around false RX timeout interrupts by deasserting RTS and using an hrtimer to wait for late chars before clearing/re-enabling receive.

## State and persistence behavior
State includes mapped register windows, UDMA arbitration ownership, coherent DMA buffers, RX/TX running flags, clock mux rate, per-port hrtimer, debugfs counters, saved RTS modem state across suspend, and the 8250 line. No persistent storage. Hardware returns to defaults across suspend, so resume restores mux and DMA hardware.

## Dependencies and integration points
Depends on platform OF matches, named MMIO resources, clk APIs, DMA coherent allocation, 8250 core registration, hrtimers, debugfs, tty flip buffers, and serial8250 suspend/resume. Compatible strings distinguish BCM7271 and BCM7278 rate tables.

## Risks and edge cases
- Private UDMA is shared hardware; arbitration only supports one user and must release on error/remove/suspend.
- RX buffer-ready interrupts must arrive in sequence; out-of-sequence events restart RX DMA and can lose buffered data.
- False RX timeout recovery changes IER/MCR and depends on `char_wait`; wrong baud timing can drop or delay data.
- DMA path bypasses generic DMA allocation, so startup/shutdown must keep `up->dma` ownership carefully controlled.
- Error paths around DMA IRQ registration, buffer allocation, and port registration must release arbitration and coherent memory.

## Test signals
PIO-only and DMA-enabled probe, UDMA revision/arbitration failures, sustained RX/TX DMA, RX error counters and flip-buffer overrun, baud mux selection accuracy and >3% error logging, false RX timeout recovery with hardware flow control, debugfs stats, suspend/resume with RTS restore, and remove cleanup of hrtimer/debugfs/DMA arbitration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_bcm7271.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_boca.c -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_boca.c

## Purpose
Registers fixed legacy port definitions for Boca multiport 8250-compatible serial cards through the generic `serial8250` platform driver.

## Important APIs, types, and functions
- `boca_data[]` defines sixteen ports from I/O base `0x100` through `0x178` in 8-byte increments, all IRQ 12.
- `boca_device` is a `serial8250` platform device with ID `PLAT8250_DEV_BOCA`.
- `boca_init()` registers the platform device.

## Control flow
Module init registers the static platform device. Generic serial8250 platform support consumes the platform data and creates the ports.

## State and persistence behavior
Static platform data only. No dynamic runtime state in this file.

## Dependencies and integration points
Depends on legacy I/O port access, `serial_8250.h`, `8250.h`, and the generic 8250 platform driver.

## Risks and edge cases
Hard-coded port and IRQ assignments can conflict with other ISA devices. All ports sharing IRQ 12 rely on generic 8250 shared IRQ handling.

## Test signals
Module load should register sixteen Boca ports, verify resource conflicts are handled, and exercise shared IRQ RX/TX across multiple active ports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_boca.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_ce4100.c -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_ce4100.c

## Purpose
Provides Intel CE4100 platform-specific 8250 ISA fixups, including MMIO accessors and a TX interrupt erratum workaround.

## Important APIs, types, and functions
- `mem_serial_in()` and `ce4100_mem_serial_out()` provide 32-bit MMIO register access.
- `ce4100_mem_serial_in()` wraps reads and fakes an interrupt pending condition when IIR says no interrupt but THRI is enabled and LSR shows THRE/TEMT.
- `ce4100_serial_fixup()` rewrites legacy ISA port configuration to CE4100 MMIO settings and installs custom accessors.
- `sdv_serial_fixup()` registers the ISA configurator with `serial8250_set_isa_configurator()`.

## Control flow
Early platform code calls `sdv_serial_fixup()`, making `ce4100_serial_fixup()` run during 8250 ISA setup. The fixup optionally overrides early-printk legacy I/O port assumptions with fixed MMIO mapping, then zeroes `iobase`, installs CE4100 serial in/out accessors, and adds a capability bit.

## State and persistence behavior
No dynamic allocation. It mutates the passed `uart_port` during ISA configuration and maps early console memory through fixmap when needed.

## Dependencies and integration points
Depends on CE4100 architecture headers, fixmap APIs, serial register definitions, and the 8250 ISA configurator hook.

## Risks and edge cases
- The TX interrupt workaround intentionally alters perceived IIR state; incorrect conditions can cause spurious TX handling.
- Early-printk fixmap manipulation is architecture-specific and must match CE4100 MMIO layout.
- The capability bit is set as `(1 << 12)`, corresponding to shared 8250 capability definitions; symbolic drift would be risky.

## Test signals
CE4100 boot with early console, TX under erratum conditions without hangs, ISA port fixup to MMIO addresses, and regression tests that non-CE4100 8250 behavior is unaffected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_ce4100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_core.c -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_core.c

## Purpose
Implements the universal/legacy 8250 driver core: shared IRQ chaining, timeout fallback, global port table setup, console registration, early serial setup, runtime port registration/unregistration, and suspend/resume entry points used by platform drivers.

## Important APIs, types, and functions
- IRQ sharing: `struct irq_info`, `irq_lists`, `hash_mutex`, `serial8250_interrupt()`, `serial_get_or_create_irq_info()`, `serial_link_irq_chain()`, and `serial_unlink_irq_chain()`.
- Timer fallback: `serial8250_timeout()`, `serial8250_backup_timeout()`, `univ8250_setup_timer()`, `univ8250_setup_irq()`, and `univ8250_release_irq()`.
- Global state: `serial8250_ports[UART_NR]`, `serial8250_reg`, `univ8250_port_base_ops`, `univ8250_port_ops`, and module param `skip_txen_test`.
- Port APIs: `serial8250_setup_port()`, `serial8250_get_port()`, `serial8250_register_ports()`, `early_serial_setup()`, `serial8250_register_8250_port()`, and `serial8250_unregister_port()`.
- Console support: `univ8250_console_write()`, `univ8250_console_setup()`, `univ8250_console_match()`, `univ8250_console_exit()`, and `univ8250_console_init()`.
- Power APIs: `serial8250_suspend_port()` and `serial8250_resume_port()`.

## Control flow
Port setup initializes one entry in the global 8250 table, installs universal ops, timers, 8250 defaults, and driver-specific setup/release IRQ callbacks. Shared IRQ registration stores ports in a per-IRQ circular list under a hash. The common interrupt handler walks the list until no more ports report handled interrupts or `PASS_LIMIT` is reached, supporting edge-triggered ISA shared IRQ deassertion.

Console init creates ISA ports first, registers `ttyS` console support, and can match `console=uart[8250],io|mmio...` earlycon command lines to existing ports. `early_serial_setup()` copies a boot-provided `uart_port` into the global table before normal registration.

Dynamic platform drivers call `serial8250_register_8250_port()` with a template. The core finds a matching or unused slot, removes an existing port if needed, copies hardware parameters and callback overrides, applies GPIO modem-control and RS485 setup, applies ISA quirks, adds the uart port, initializes LSR save mask and optional overrun-backoff work, and returns the line. Unregister removes the port, destroys emulated RS485 state, and either restores an ISA placeholder or clears `dev`.

## State and persistence behavior
State is global in `serial8250_ports`, IRQ hash/list nodes, timers, console binding, module parameter `skip_txen_test`, and per-port copied callback/configuration fields. No persistent storage. Suspend may save a scratch-register canary for always-on console ports and resume may re-enter NatSemi high-speed mode.

## Dependencies and integration points
Depends on uart_core, serial8250 lower-level helpers, ISA/PnP/platform setup, PM runtime, mctrl GPIO, console/sysrq, tty flip/xmit FIFOs, and exported APIs consumed by many platform drivers in this work item.

## Risks and edge cases
- Shared IRQ list manipulation has lock ordering across `hash_mutex` and per-IRQ spinlocks; list corruption would affect all ports on an IRQ.
- Backup timer behavior for THRE bugs temporarily disables IER and manually drives TX; races with real IRQ handlers are mitigated by port lock.
- `serial8250_register_8250_port()` copies many optional callbacks and must preserve existing console/PM semantics when replacing a port.
- Dynamic growth of `nr_uarts` and port matching can return `-ENOSPC` or reuse entries unexpectedly if templates are incomplete.
- Error paths after partial field copying leave `port.dev = NULL` but other copied fields remain in the table.

## Test signals
Shared IRQ multiport stress, no-IRQ polling mode, THRE backup timer on known buggy UARTs, console earlycon handoff and matching, dynamic register/unregister from platform drivers, RS485/GPIO modem-control initialization, suspend/resume for console and NatSemi high-speed ports, and lockdep coverage for IRQ/list operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_dfl.c -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_dfl.c

## Purpose
Registers FPGA Device Feature List UART features as 8250 ports, deriving clock, FIFO type, and register layout from DFHv1 parameters.

## Important APIs, types, and functions
- `struct dfl_uart` stores the registered 8250 line.
- `dfh_get_u64_param_val()` reads and validates 64-bit DFH parameters.
- `dfl_uart_get_params()` maps `CLK_FRQ`, `FIFO_LEN`, and `REG_LAYOUT` parameters to `uart_8250_port` fields.
- `dfl_uart_probe()` registers the 8250 port; `dfl_uart_remove()` unregisters it.
- `dfl_uart_ids[]` matches FME feature ID `0x24`.

## Control flow
Probe initializes a `uart_8250_port` with I/O remap flags and MMIO range from the DFL device, reads clock frequency, selects an Altera FIFO port type based on FIFO length 32/64/128, sets regshift and UPIO width based on layout width, optionally assigns the single IRQ, then registers the port and stores the returned line.

## State and persistence behavior
Only stores the registered line in devm-allocated private data. Hardware configuration is discovered each probe from DFH parameters.

## Dependencies and integration points
Depends on DFL bus helpers, DFH parameter parsing, serial8250 registration, MMIO resources, and optional DFL IRQ metadata.

## Risks and edge cases
- Missing or wrongly sized DFH params fail probe.
- Unsupported FIFO lengths or register widths fail with `-EINVAL`.
- No IRQ means the generic 8250 core may rely on polling behavior.

## Test signals
Probe with valid 32/64/128 FIFO parameter sets, invalid/missing parameter failures, MEM16 and MEM32 layouts, IRQ and no-IRQ devices, and unregister on remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_dfl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_dma.c -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_dma.c

## Purpose
Provides generic DMA engine support for 8250 ports, handling TX/RX DMA submission, completion, flush, channel allocation, buffer mapping, and release.

## Important APIs, types, and functions
- TX path: `serial8250_tx_dma()`, `__dma_tx_complete()`, and `serial8250_tx_dma_flush()`.
- RX path: `serial8250_rx_dma()`, `dma_rx_complete()`, `__dma_rx_complete()`, and `serial8250_rx_dma_flush()`.
- Lifecycle: `serial8250_request_dma()` and `serial8250_release_dma()`.
- Uses `struct uart_8250_dma` fields defined in `8250.h`.

## Control flow
DMA request configures default byte-wide RX/TX slave addresses from `mapbase`, requests compatible RX/TX channels, validates that RX supports pause/terminate and non-descriptor residue granularity and TX supports terminate, applies slave configs, allocates a coherent RX buffer, and maps the uart xmit buffer for TX.

TX DMA handles x_char specially, refuses work when stopped or FIFO empty, lets platform hooks prepare DMA, builds up to two SG entries from the circular xmit kfifo, submits a DMA_MEM_TO_DEV transfer, syncs the mapped buffer for device, starts DMA, and clears THRI. TX completion syncs for CPU, advances xmit state, wakes writers if below `WAKEUP_CHARS`, attempts another DMA transfer, and re-enables THRI if DMA cannot continue.

RX DMA submits a single DEV_TO_MEM transfer for the coherent RX buffer. Completion checks whether another RX has already started, computes received count from residue, inserts bytes into the tty flip buffer, updates RX count, clears running, pushes the buffer, and restarts if LSR still shows data. Flush pauses, completes partial RX, and terminates asynchronously.

## State and persistence behavior
Per-port DMA state includes channels, configs, DMA addresses, cookies, buffer pointers, transfer sizes, and running/error flags. No persistent storage. TX xmit buffer mapping is held until release; RX coherent buffer persists while DMA is requested.

## Dependencies and integration points
Depends on DMA engine APIs, uart_core xmit FIFO helpers, tty flip buffers, serial8250 register helpers, platform-provided filter/config hooks, and port locking. Exported symbols are used by 8250 core and platform drivers.

## Risks and edge cases
- `serial8250_tx_dma_flush()` assumes async termination finishes before a new TX DMA is issued; violating that can corrupt TX state.
- RX completion uses residue; DMA controllers with descriptor-only residue are rejected.
- TX x_char during running DMA pauses/resumes the channel and writes directly to UART.
- Missing DMA capability validation can produce hangs or stale `rx_running`/`tx_running`.
- Error paths must release RX if TX allocation fails and free/unmap buffers exactly once.

## Test signals
DMA channel request success/failure matrix, TX with wraparound kfifo SG, x_char during active TX DMA, RX residue/count correctness, flush during active TX/RX, fallback to interrupt TX when DMA returns busy, and release after partial allocation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_dw.c -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_dw.c

## Purpose
Implements the Synopsys DesignWare APB UART platform driver on top of 8250, handling busy-detect behavior, register-width variants, clocks/resets/runtime PM, platform quirks, DMA setup, IrDA mode, modem-signal overrides, and OF/ACPI matching.

## Important APIs, types, and functions
- `struct dw8250_platform_data` defines USR register, CPR override, and quirk flags.
- `struct dw8250_data` embeds `dw8250_port_data`, clocks, notifier/work item, reset, modem masks, compatibility flags, and interrupt-storm counter.
- Busy/idle handling: `dw8250_idle_enter()`, `dw8250_idle_exit()`, `dw8250_set_divisor()`, `dw8250_check_lcr()`, and `dw8250_can_skip_reg_write()`.
- Register accessors: byte, 32-bit, big-endian 32-bit, and 64-bit Octeon variants.
- IRQ/quirks: `dw8250_handle_irq()`, `dw8250_quirk_ier_kick()`, `dw8250_quirks()`, `dw8250_prepare_tx_dma()`, and `dw8250_prepare_rx_dma()`.
- Clock/PM: `dw8250_clk_notifier_cb()`, `dw8250_clk_work_cb()`, `dw8250_do_pm()`, `dw8250_set_termios()`, runtime/system suspend/resume callbacks.
- Probe/remove: `dw8250_probe()` and `dw8250_remove()`.

## Control flow
Probe maps MMIO, reads UART properties, selects serial in/out functions based on iotype, applies modem override properties, gets baud and APB clocks, deasserts resets with devm cleanup, marks runtime PM active, reads platform match data, applies quirks, installs a custom IRQ handler for non-16550-compatible DesignWare instances, sets up DMA filters and FIFO/capability data through `dw8250_setup_port()`, registers the port with the 8250 core, registers a clock notifier, and enables runtime PM.

For non-compatible DesignWare UARTs, LCR/divisor writes must avoid the hardware BUSY condition. `dw8250_idle_enter()` disables interrupts, flushes/pauses DMA, waits for TX empty plus frame time, loops back, clears FIFOs until USR busy clears, drains stray RX, and then permits divisor/LCR writes. `dw8250_check_lcr()` verifies LCR writes and retries through idle entry if hardware ignored the write.

The custom IRQ path clears BUSY interrupts by reading USR, works around RX timeout with no data by dummy-reading RX, optionally kicks IER to escape IIR_NO_INT storms, and manually stops RZN1 flow-controller DMA on RX timeout before delegating to locked 8250 IRQ handling.

## State and persistence behavior
Per-device state includes clock handles and current rates, reset state, line number, platform quirk data, DMA config embedded in `dw8250_port_data`, modem signal masks, idle flag, and no-interrupt counter. No persistent storage. Runtime PM turns clocks off/on around port PM.

## Dependencies and integration points
Depends on platform resources, OF/ACPI match tables, clk/reset APIs, runtime PM, serial8250 core, `8250_dwlib.c` helpers, DMA engine filter hooks, system workqueue, and serial namespace import. Compatible strings cover generic `snps,dw-apb-uart`, Octeon, Armada 38x, Renesas RZN1, Sophgo, StarFive, and many ACPI IDs.

## Risks and edge cases
- Busy-detect sequences manipulate IER, MCR, FIFOs, DMA, and loopback under lock; ordering errors can drop data or deadlock.
- Clock rate updates are deferred to avoid lock inversions; missing notifier cleanup could update after remove.
- Quirk flags radically change accessors and behavior; wrong match data can break register width, DMA flow control, or interrupt handling.
- Probe currently returns directly if clock notifier registration fails after port registration, so cleanup of the registered port is a review point.
- Runtime PM clock ordering must keep APB/baud clocks available for register access.

## Test signals
Probe on OF and ACPI variants, iotype byte/MEM32/BE/Octeon access, LCR write while busy, baud changes with clock set_rate, RX timeout dummy-read workaround, IIR_NO_INT storm quirk, RZN1 DMA flow-controller setup, runtime suspend/resume, system suspend/resume, and remove with pending clock notifier work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_dw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_dwlib.c -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_dwlib.c

## Purpose
Provides shared DesignWare 8250 helper logic for fractional divisors, termios integration, hardware RS485/addressing support, FIFO/capability discovery from Component Parameter Register, and fallback to emulated RS485.

## Important APIs, types, and functions
- Fractional divisor helpers: `dw8250_get_divisor()` and local `dw8250_set_divisor()`.
- Exported termios wrapper: `dw8250_do_set_termios()`.
- RS485/addressing helpers: `dw8250_wait_re_deassert()`, `dw8250_update_rar()`, `dw8250_rs485_set_addr()`, `dw8250_rs485_config()`, `dw8250_detect_rs485_hw()`, and `dw8250_rs485_supported`.
- Exported setup: `dw8250_setup_port()`.

## Control flow
`dw8250_setup_port()` first probes whether hardware RS485 exists by writing/reading `RE_EN`. If present, it installs hardware RS485 config, expands LSR save mask for address-detected status, and advertises address receive/destination features; otherwise it installs generic 8250 emulated RS485 callbacks. It then marks no-TEMT capability, probes the DLF register width by writing all ones and restoring the old value, and if present installs fractional divisor callbacks.

It reads UART version and CPR; if CPR is missing, it uses a platform-provided `cpr_value`. CPR FIFO mode makes the port fixed 16550A with computed FIFO size and FIFO capability. CPR bits add auto-flow-control and IrDA capabilities.

RS485 config programs TCR, DE/RE enable registers, DE/RE polarity, transfer mode, and optional 9-bit addressing. Receive address changes deassert RE, waits one frame time, writes RAR, and restores RE.

## State and persistence behavior
Mutates caller-owned `dw8250_port_data`, `uart_port`, and `uart_8250_port`: `dlf_size`, `hw_rs485_support`, rs485 callbacks/supported flags, FIFO size, capabilities, divisor callbacks, and LSR masks. Hardware registers hold RS485, address, DLF, and capability-related state.

## Dependencies and integration points
Depends on `8250_dwlib.h` extended register accessors, serial8250 divisor/termios/RS485 emulation helpers, device properties, and serial_core RS485 structures. Exported symbols are used by `8250_dw.c`.

## Risks and edge cases
- DLF probing writes `~0U` to hardware and must restore firmware value; broken DLF implementations could misreport width.
- Hardware RS485 detection writes `RE_EN`; side effects on active hardware would be risky if called outside setup.
- Address receive config must avoid changing RAR while receiving; the frame-time wait is a heuristic without BUSY signal.
- CPR fallback data must match the SoC, otherwise FIFO/capability detection is wrong.

## Test signals
Hardware RS485 detection present/absent, RS485 enable/disable and polarity/address modes, fractional divisor baud accuracy, CPR-derived FIFO/capability reporting, IrDA line discipline capability, and fallback to emulated RS485 when RE_EN is not writable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_dwlib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_dwlib.h -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_dwlib.h

## Purpose
Declares the shared DesignWare 8250 port-data structure, exported helper prototypes, and endian-aware extended-register read/write helpers.

## Important APIs, types, and functions
- `struct dw8250_port_data` stores registered line, embedded `uart_8250_dma`, CPR override, DLF size, and hardware RS485 support flag.
- Prototypes: `dw8250_do_set_termios()` and `dw8250_setup_port()`.
- Inline helpers: `dw8250_readl_ext()` and `dw8250_writel_ext()` use big-endian accessors when `p->iotype == UPIO_MEM32BE`, otherwise little-endian `readl`/`writel`.

## Control flow
The main DesignWare driver embeds `dw8250_port_data` in its private data and passes it as `uart_port.private_data`. Extended register helpers are used by both the main driver and library to access non-8250 DesignWare registers.

## State and persistence behavior
The header defines state shape only. Runtime state is maintained by `8250_dw.c` and `8250_dwlib.c`.

## Dependencies and integration points
Depends on `linux/io.h`, `linux/types.h`, and internal `8250.h`. It is the private interface between DesignWare 8250 modules.

## Risks and edge cases
The extended register helpers assume extended registers are 32-bit and aligned at raw offsets, not shifted 8250 offsets. Incorrect `iotype` causes endian-swapped access.

## Test signals
Build coverage for little-endian and big-endian DesignWare ports, and runtime validation that extended register values read consistently with the selected iotype.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_dwlib.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_early.c -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_early.c

## Purpose
Implements early console support for 8250/16550 UARTs before full serial driver discovery, supporting I/O port and MMIO access widths plus several OF earlycon compatible strings.

## Important APIs, types, and functions
- Register access: `serial8250_early_in()` and `serial8250_early_out()`.
- Console I/O: `serial_putc()`, `early_serial8250_write()`, and optional `early_serial8250_read()` under `CONFIG_CONSOLE_POLL`.
- Setup: `init_port()`, `early_serial8250_setup()`, `early_serial8250_rs2_setup()`, and optional `early_omap8250_setup()`.
- Declarations: `EARLYCON_DECLARE()` and `OF_EARLYCON_DECLARE()` for generic uart8250/ns16550 and SoC-specific compatible strings.

## Control flow
Early setup validates that an I/O base or membase exists. If a baud is supplied, it initializes 8n1, masks interrupts, disables FIFO, asserts DTR/RTS, and programs divisor from `uartclk`. If no baud is supplied, it assumes firmware initialized the UART and only masks interrupts. It then assigns console write and optional read callbacks.

Writes send chars through `uart_console_write()` and `serial_putc()`, which writes TX then busy-waits for TX empty. Poll reads drain RX while LSR data-ready is set.

## State and persistence behavior
State is in the boot-time `earlycon_device` and hardware UART registers. It does not allocate persistent driver state. Full 8250 console later matches/replaces earlycon through core console matching.

## Dependencies and integration points
Depends on earlycon framework, serial register definitions, MMIO/PIO accessors, OF earlycon matching, and optional console polling. `early_bcm2835aux_setup()` and other platform earlycon declarations build on this generic setup.

## Risks and edge cases
- Busy-wait TX can stall boot if hardware is misdescribed or not clocked.
- Access width/iotype must match hardware; wrong width can fault or write wrong registers.
- Initialization without a baud leaves firmware divisor/format intact, which is useful but can hide bad bootloader setup.

## Test signals
Boot with `earlycon=uart8250,io`, `mmio`, `mmio32`, and OF compatible forms, handoff to `ttyS` console, poll read when enabled, no-baud firmware-initialized console, and invalid base rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_early.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_em.c -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_em.c

## Purpose
Implements an 8250-based Renesas Emma Mobile UART driver with non-standard register layout, reset-on-register-update behavior, custom divisor latch access, clock handling, and OF platform binding.

## Important APIs, types, and functions
- `struct serial8250_em_priv` stores the registered line.
- Register access helpers: `serial8250_em_serial_out_helper()`, `serial8250_em_serial_in()`, `serial8250_em_reg_update()`, and `serial8250_em_serial_out()`.
- Divisor latch helpers: `serial8250_em_serial_dl_read()` and `serial8250_em_serial_dl_write()`.
- Probe/remove: `serial8250_em_probe()` and `serial8250_em_remove()`.
- OF match: `renesas,em-uart`.

## Control flow
Probe gets IRQ and MMIO resource, allocates private data, enables `sclk`, initializes an 8250 template as fixed `PORT_16750`, sets custom serial in/out and divisor latch callbacks, sets `uartclk` from the clock, registers the 8250 port, and stores the line.

The custom accessors map logical 8250 registers to Emma Mobile's shifted/special offsets. Writes to FCR/LCR/MCR go through `serial8250_em_reg_update()`, which snapshots IER/FCR/LCR/MCR/HCR0, clears FIFOs, toggles software reset, applies the requested register change, and restores the saved registers.

## State and persistence behavior
Per-device state is only the 8250 line and clock-managed hardware state. Register snapshots are transient during updates. No persistent storage.

## Dependencies and integration points
Depends on platform resources, clk APIs, OF matching, serial8250 registration, custom register access callbacks, and standard 8250 termios/divisor flows.

## Risks and edge cases
- Register update performs reset and FIFO clears on FCR/LCR/MCR changes; unexpected calls can drop buffered data.
- IER writes mask to four valid bits, so XScale-style bits are intentionally unsupported.
- Custom offset mapping must stay aligned with hardware documentation; generic 8250 assumptions do not apply.

## Test signals
Probe/remove with valid clock and IRQ, baud divisor read/write, LCR/MCR/FCR updates under traffic to detect data loss, RX/TX functionality, and OF binding coverage for `renesas,em-uart`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_em.c -->
