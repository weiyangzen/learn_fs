# subset-b-005423 Research Group

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/most/net/net.c -->
# sources/distributed-fs/ceph-client/drivers/staging/most/net/net.c

## Purpose
Mostcore networking component that binds one async RX channel and one async TX channel from the same MOST interface into a Linux Ethernet netdev named `meth%d`. It encapsulates Ethernet frames into MOST Ethernet Packet (MEP) or MOST Asynchronous MAC (MAMAC/MDP) wire formats and decapsulates received MBOs back into skbs.

## Important APIs, Types, And Functions
`struct net_dev_context` owns the MOST interface, netdev, RX/TX channel ids, MAMAC mode flag, and global-list node. `struct net_dev_channel` tracks one linked channel. Key functions are `comp_probe_channel()`, `comp_disconnect_channel()`, `most_nd_open()`, `most_nd_stop()`, `most_nd_start_xmit()`, `comp_rx_data()`, `comp_resume_tx_channel()`, `skb_to_mamac()`, `skb_to_mep()`, `most_nd_set_mac_address()`, and `on_netinfo()`.

## Control Flow
Mostcore probes TX and RX async channels separately. The first channel allocates a netdev and the second registers it; open starts both MOST channels, wakes the net queue, and optionally requests HDM netinfo. Transmit gets an MBO from the TX channel, wraps the skb as MAMAC when the configured MAC begins with four zero bytes or as MEP otherwise, submits the MBO, updates stats, and frees the skb. RX completion validates MAMAC/MEP headers, allocates an skb, reconstructs Ethernet addressing for MAMAC, calls `eth_type_trans()`, and injects via `netif_rx()`.

## State And Persistence
State is in-memory only: linked channel flags, channel ids, `is_mamac`, netdev stats, queue/carrier state, and global `net_devices`. `probe_disc_mt` serializes probe/disconnect/open, while `list_lock` protects list membership and linked flags for refcounted lookups. No durable state is stored.

## Dependencies And Integration Points
Depends on Mostcore component/configfs APIs, `struct mbo`, Linux netdev/etherdevice helpers, skb allocation, and optional interface `request_netinfo`. It registers as Mostcore component `net`.

## Risks
The two-channel pairing is order-dependent and registration only happens on the second channel. MAMAC address synthesis uses protocol-specific offsets and assumes validated MDP headers. Disconnect relies on `unregister_netdev()` to drive `ndo_stop()` before channel stop. TX queue wake depends on Mostcore TX completion callbacks.

## Test Signals
Probe TX/RX in both orders, duplicate direction rejection, open/stop with netinfo callbacks, short/oversized skb drops, MEP and MAMAC packet round trips, invalid RX header rejection, TX MBO exhaustion queue stop/resume, MAC-address changes switching MTU/MAMAC mode, and disconnect while the netdev is up.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/most/net/net.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/most/video/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/staging/most/video/Kconfig

## Purpose
Kconfig entry for enabling the Mostcore V4L2 component.

## Important APIs, Types, And Functions
Defines `config MOST_VIDEO` as a tristate option named "Video". It depends on `VIDEO_DEV` and documents the module name `most_video`.

## Control Flow
When selected as built-in or module, the kernel build includes the MOST video component from the corresponding Makefile. The dependency ensures V4L2 core symbols are available.

## State And Persistence
No runtime state. The selected Kconfig symbol persists only in the kernel build configuration.

## Dependencies And Integration Points
Integrates with Kbuild and the media/V4L2 subsystem through `VIDEO_DEV`; the object mapping lives in `drivers/staging/most/video/Makefile`.

## Risks
The help text contains a typo, but the functional risk is mostly configuration: selecting this without compatible Mostcore channels will build a module that has no device to bind.

## Test Signals
`CONFIG_MOST_VIDEO=m` should build `most_video.ko`; `CONFIG_MOST_VIDEO=y` should link the object when `VIDEO_DEV` is enabled; disabled `VIDEO_DEV` should hide or reject the option.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/most/video/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/most/video/Makefile -->
# sources/distributed-fs/ceph-client/drivers/staging/most/video/Makefile

## Purpose
Kbuild recipe for the Mostcore V4L2 component.

## Important APIs, Types, And Functions
Maps `CONFIG_MOST_VIDEO` to `most_video.o` and defines `most_video-objs := video.o`.

## Control Flow
Kbuild compiles `video.c` into the composite `most_video` module or built-in object when `MOST_VIDEO` is enabled.

## State And Persistence
No runtime state. Build output names are determined by this file.

## Dependencies And Integration Points
Consumes the `MOST_VIDEO` Kconfig symbol and integrates with the kernel module build.

## Risks
The build unit has only one source file, so missing exports or V4L2 API changes surface directly as compile/link errors.

## Test Signals
Kernel build with `CONFIG_MOST_VIDEO=m` should produce `most_video.ko` containing `video.o`; `modinfo` should show metadata from `video.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/most/video/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/most/video/video.c -->
# sources/distributed-fs/ceph-client/drivers/staging/most/video/video.c

## Purpose
Mostcore video component that exposes one RX sync/isoc MOST channel as a V4L2 read/poll capture node carrying compressed MPEG data.

## Important APIs, Types, And Functions
`struct most_video_dev` stores interface/channel identity, pending MBO list, mute flag, V4L2 device/video_device, open refcount, lock, and waitqueue. `struct comp_fh` tracks one file handle and read offset. Key functions are `comp_probe_channel()`, `comp_disconnect_channel()`, `comp_vdev_open()`, `comp_vdev_close()`, `comp_vdev_read()`, `comp_vdev_poll()`, `comp_rx_data()`, `comp_register_videodev()`, V4L2 ioctl handlers, `comp_init()`, and `comp_exit()`.

## Control Flow
Mostcore probes only RX sync or isoc channels, creates a `v4l2_device`, allocates/registers a `video_device`, and adds it to a global list. Open allows a single active client through `access_ref`, initializes a V4L2 file handle, and starts the MOST channel. RX completions append MBOs to `pending_mbos` unless muted and wake readers. Reads block unless nonblocking, copy data from the head MBO respecting per-file offset, and return MBOs when fully consumed. Close mutes completions, drains pending MBOs, stops the channel, and releases the file handle.

## State And Persistence
Runtime state includes pending MBO queues, read offsets, single-client refcount, mute flag, selected input, and global device list. `list_lock` protects global lookup; per-device `list_lock` protects MBO queues. No persistent storage exists.

## Dependencies And Integration Points
Depends on Mostcore component/configfs APIs, V4L2 core, video ioctl helpers, waitqueues, spinlocks, and user-copy APIs. It registers component `video`.

## Risks
The close path uses `mute` as a workaround because Mostcore can still deliver completions until stop; missed coordination can leak or lose MBOs. `data_ready()` is queried without always holding the queue lock. Format handling is minimal and fixed to MPEG with placeholder dimensions. Exit manually disconnects devices because core teardown lacks automatic disconnects.

## Test Signals
Probe rejects TX and non-sync/isoc channels; `/dev/video*` appears for valid channels; only one open succeeds; blocking and nonblocking reads behave correctly; poll signals readable on RX; partial reads preserve offsets; close drains MBOs without use-after-free; V4L2 querycap/format/input ioctls return expected values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/most/video/video.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/nvec/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/staging/nvec/Kconfig

## Purpose
Kconfig menu for the NVIDIA Embedded Controller staging MFD and its keyboard, PS/2 mouse, power-supply, and PAZ00 LED child drivers.

## Important APIs, Types, And Functions
Defines `MFD_NVEC`, `KEYBOARD_NVEC`, `SERIO_NVEC_PS2`, `NVEC_POWER`, and `NVEC_PAZ00`. `MFD_NVEC` depends on `I2C`, `GPIOLIB`, and `ARCH_TEGRA`, and selects `MFD_CORE`; child drivers depend on `MFD_NVEC` plus their subsystem core.

## Control Flow
The parent MFD option builds the EC transport. Child symbols enable platform drivers that bind to MFD cells created by `nvec.c`.

## State And Persistence
No runtime state. The selected symbols persist in the kernel configuration.

## Dependencies And Integration Points
Integrates Kbuild with MFD, input, serio, power_supply, LED class, and Tegra platforms.

## Risks
The parent is Tegra-specific and staging-only. Enabling children without hardware support yields unused modules. The child modules depend on the parent creating matching platform devices.

## Test Signals
Kconfig dependency checks, module builds for each selected symbol, and parent MFD probe creating cells named `nvec-kbd`, `nvec-mouse`, `nvec-power`, and `nvec-paz00`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/nvec/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/nvec/Makefile -->
# sources/distributed-fs/ceph-client/drivers/staging/nvec/Makefile

## Purpose
Kbuild object mapping for the NVEC MFD stack.

## Important APIs, Types, And Functions
Builds `nvec.o`, `nvec_kbd.o`, `nvec_ps2.o`, `nvec_power.o`, and `nvec_paz00.o` from their matching Kconfig symbols.

## Control Flow
When a symbol is enabled, Kbuild includes the corresponding source in the kernel or builds it as a module.

## State And Persistence
No runtime state. Build artifacts and module names are determined by object filenames.

## Dependencies And Integration Points
Consumes the symbols declared in `Kconfig` and feeds kernel module linking.

## Risks
The modules are independent objects, so child modules can be loaded separately but still require the parent MFD device at runtime.

## Test Signals
Build each Kconfig combination and verify generated modules: `nvec`, `nvec_kbd`, `nvec_ps2`, `nvec_power`, and `nvec_paz00`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/nvec/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/nvec/nvec-keytable.h -->
# sources/distributed-fs/ceph-client/drivers/staging/nvec/nvec-keytable.h

## Purpose
Keyboard scancode translation tables for the NVEC keyboard driver, mapping EC key positions to Linux input key codes.

## Important APIs, Types, And Functions
Defines `code_tab_102us[]` for base 102-key US keyboard scancodes, `extcode_tab_us102[]` for extended scancodes, and `code_tabs[]` selecting the table by NVEC event-size encoding.

## Control Flow
`nvec_kbd.c` copies both tables into its input keycode array during probe and uses `code_tabs[_size][code]` when translating `NVEC_KB_EVT` messages.

## State And Persistence
The arrays are static compile-time data. No mutable or persistent state exists in this header.

## Dependencies And Integration Points
Requires Linux input key-code constants from the including translation unit. It is tightly coupled to `nvec_kbd.c` and the EC keyboard event-size encoding.

## Risks
Zero entries intentionally represent unsupported keys; events landing on zero are suppressed by clearing keybit 0 but still pass through translation. The table is US-layout-specific and contains sparse OEM/media mappings.

## Test Signals
Keyboard event tests should verify base and extended scancodes, Caps Lock, arrow/navigation keys, keypad keys, Fn/search/power entries, and unknown scancodes producing no key event.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/nvec/nvec-keytable.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/nvec/nvec.c -->
# sources/distributed-fs/ceph-client/drivers/staging/nvec/nvec.c

## Purpose
Parent MFD and transport driver for NVIDIA/Compal NVEC embedded controllers. It runs a Tegra I2C slave state machine, queues sync/async EC commands, dispatches EC events to notifier subscribers, and creates child devices for keyboard, mouse, power, and OEM LED functions.

## Important APIs, Types, And Functions
Exports `nvec_write_async()`, `nvec_write_sync()`, `nvec_register_notifier()`, `nvec_unregister_notifier()`, and `nvec_msg_free()`. Internals include `nvec_msg_alloc()`, `nvec_request_master()`, `nvec_dispatch()`, `nvec_interrupt()`, `nvec_rx_completed()`, `nvec_tx_completed()`, `tegra_init_i2c_slave()`, `tegra_nvec_probe()`, remove and PM callbacks, and the `nvec_devices[]` MFD cells.

## Control Flow
Probe reads `slave-addr`, maps the I2C-slave controller, gets IRQ/clock/reset/request GPIO, initializes lists, completions, work items, and the message pool, requests an IRQ with `IRQF_NO_AUTOEN`, enables the slave controller, turns on EC global events, installs a catch-all status notifier, optionally fetches firmware version synchronously, adds MFD children, unmutes speakers, and enables lid/power-button events. Async writes allocate TX messages and schedule `tx_work`, which pulls the request GPIO low and waits for the EC transfer completion. The IRQ handler reads/writes bytes through a finite-state machine, queues complete RX messages, and completes TX/sync waiters. `rx_work` matches sync responses or calls the notifier chain for unsolicited events.

## State And Persistence
`struct nvec_chip` owns MMIO, clock/reset/GPIO, notifier list, RX/TX queues, message pool, current RX/TX pointers, completions, locks, sync-write bookkeeping, and state-machine integer. `nvec_power_handle` and `pm_power_off` are global side effects. No durable storage exists.

## Dependencies And Integration Points
Depends on platform/OF, Tegra I2C registers, clk/reset/GPIO, IRQs, workqueues, MFD core, atomic notifiers, and PM sleep. Child drivers use the exported write/notifier APIs through their parent platform device.

## Risks
The interrupt state machine is sensitive to status flag combinations and manually recovers from partial RX/TX. Message pool exhaustion can break RX or TX; TX buffers deliberately start at one quarter of the pool to reserve RX capacity. `nvec_write_sync()` has a fixed 2s timeout and global pending tuple. `pm_power_off` is overwritten and unconditionally cleared on remove with a FIXME. Suspend depends on synchronous EC commands.

## Test Signals
OF probe with valid/invalid `slave-addr`, IRQ byte-sequence tests for RX event, sync response, EC read request, premature END_TRANS, pool exhaustion, TX timeout, child MFD creation, notifier dispatch, firmware request, suspend/resume, global event toggling, and `pm_power_off` behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/nvec/nvec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/nvec/nvec.h -->
# sources/distributed-fs/ceph-client/drivers/staging/nvec/nvec.h

## Purpose
Shared interface and core data structures for the NVEC MFD parent and child drivers.

## Important APIs, Types, And Functions
Defines `NVEC_POOL_SIZE`, `NVEC_MSG_SIZE`, `enum nvec_event_size`, `enum nvec_msg_type`, `struct nvec_msg`, and `struct nvec_chip`. Declares `nvec_write_async()`, `nvec_write_sync()`, `nvec_register_notifier()`, `nvec_unregister_notifier()`, and `nvec_msg_free()`.

## Control Flow
Child drivers include this header to send commands and register notifier callbacks. The parent uses the same types for queueing TX/RX messages and dispatching events.

## State And Persistence
The header describes runtime state but stores none itself. `struct nvec_chip` state is in-memory transport, queue, sync-write, and state-machine state.

## Dependencies And Integration Points
Pulls in kernel atomics, clk, completions, lists, mutexes, notifiers, reset controls, spinlocks, and workqueues. It is the contract between `nvec.c` and all NVEC children.

## Risks
The message size assumes SMBus block semantics: one command byte, one count byte, and up to 32 payload bytes. Event type and size encodings are protocol-specific; misuse by children can misparse EC messages.

## Test Signals
Compile all child modules against the header, validate event type values used by keyboard/mouse/power, and exercise sync/async API ownership rules including freeing returned sync messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/nvec/nvec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/nvec/nvec_kbd.c -->
# sources/distributed-fs/ceph-client/drivers/staging/nvec/nvec_kbd.c

## Purpose
Input keyboard driver for keys reported by the NVEC embedded controller.

## Important APIs, Types, And Functions
`struct nvec_keys` stores the input device, notifier, NVEC pointer, and Caps Lock LED state. Key functions are `nvec_kbd_probe()`, `nvec_kbd_remove()`, `nvec_keys_notifier()`, `nvec_kbd_event()`, and `nvec_kbd_toggle_led()`. It uses tables from `nvec-keytable.h`.

## Control Flow
Probe builds the keycode table, allocates/registers an `input_dev`, marks key/repeat/LED capabilities, registers an NVEC notifier, synchronously enables the keyboard, configures wake and wake-key reporting, and clears LEDs. The notifier handles `NVEC_KB_EVT`, ignores variable-size power events, adjusts for 3-byte extended events, translates scancode/state to input key events, toggles Caps Lock LED on press, and stops notifier propagation. LED events from input core send `SET_LEDS` commands to the EC. Remove disables wake reporting and keyboard and unregisters the notifier.

## State And Persistence
Uses one static global `keys_dev`, so only one keyboard instance is supported. Caps Lock state is cached in memory. The input keycode array is static mutable initialization data. No durable storage exists.

## Dependencies And Integration Points
Depends on NVEC notifier/write APIs, Linux input core, platform children from the NVEC MFD, and the local keytable header.

## Risks
The global singleton prevents multiple controllers. No bounds check guards `code_tabs[_size][code]` beyond protocol assumptions. Caps Lock LED toggling uses all three LED bits due to a documented firmware bug. Synchronous probe commands can delay or fail boot.

## Test Signals
Probe/remove, base and extended key events, key release polarity, Caps Lock LED via key press and EV_LED, wake configuration commands, variable-size event suppression, and notifier unregister on remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/nvec/nvec_kbd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/nvec/nvec_paz00.c -->
# sources/distributed-fs/ceph-client/drivers/staging/nvec/nvec_paz00.c

## Purpose
OEM LED class driver for Compal PAZ00/Toshiba AC100 style devices controlled through NVEC OEM commands.

## Important APIs, Types, And Functions
`struct nvec_led` embeds `led_classdev` and stores the NVEC parent pointer. `nvec_led_brightness_set()` sends the OEM LED command, and `nvec_paz00_probe()` registers the LED class device.

## Control Flow
Probe allocates `nvec_led`, sets max brightness to 8, names the LED `paz00-led`, enables suspend/resume handling, stores the parent NVEC pointer, and registers with the LED class. Brightness changes copy `NVEC_LED_REQ`, place the requested value in byte 4, send it asynchronously, and update cached brightness.

## State And Persistence
Runtime state is only the allocated LED object and cached brightness. No persistent LED state is saved across driver reloads or power cycles.

## Dependencies And Integration Points
Depends on the NVEC MFD child device, NVEC async command API, platform bus, and LED class framework.

## Risks
Brightness values are passed directly to firmware without validation beyond LED core max brightness. Async command failure is ignored by the LED callback. Device coverage is OEM-specific.

## Test Signals
LED class registration, sysfs brightness writes from 0 through 8, suspend/resume restoration by LED core, command bytes observed on NVEC, and removal cleanup through devm.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/nvec/nvec_paz00.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/nvec/nvec_power.c -->
# sources/distributed-fs/ceph-client/drivers/staging/nvec/nvec_power.c

## Purpose
Power-supply driver exposing NVEC AC and battery information through Linux `power_supply`.

## Important APIs, Types, And Functions
`struct nvec_power` stores notifier/work state, EC pointer, AC online flag, battery presence/status/measurements, capacity, temperature, and strings. `struct bat_response` overlays EC responses. Key functions are `nvec_power_probe()`, `nvec_power_remove()`, `nvec_power_poll()`, `nvec_power_notifier()`, `nvec_power_bat_notifier()`, `get_bat_mfg_data()`, and the AC/battery `get_property` callbacks.

## Control Flow
The NVEC parent creates two `nvec-power` cells with ids for AC and battery. AC probe registers a system-status notifier, power_supply named `ac`, and a delayed poller that requests AC status and one battery metric every five seconds. Battery probe registers a battery notifier, requests manufacturer/model/type/capacity data, and registers power_supply named `battery`. Notifiers parse `NVEC_SYS` and `NVEC_BAT` responses into cached fields and signal `power_supply_changed()` on online/presence/status changes.

## State And Persistence
All readings are cached in `struct nvec_power`; static globals hold the registered AC and battery power_supply pointers, and a static `counter` rotates polled battery commands. No durable state exists.

## Dependencies And Integration Points
Depends on NVEC notifier/write APIs, platform MFD children, delayed work, `power_supply` core, and EC battery/system command formats.

## Risks
The same notifier field is used for AC and battery instances but registered with a broad event argument; correctness depends on event-type filtering. Static globals and poll counter make multi-controller support unsafe. Manufacturer/model/type copies trust `res->length - 2` to fit 30-byte arrays. Polling deliberately spaces requests because the EC can be overloaded.

## Test Signals
AC and battery cell probe by id, property reads before/after EC responses, status transitions, battery insert/remove triggering manufacturer refresh, string response bounds, delayed poll cadence, remove canceling work, and power_supply_changed notifications.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/nvec/nvec_power.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/nvec/nvec_ps2.c -->
# sources/distributed-fs/ceph-client/drivers/staging/nvec/nvec_ps2.c

## Purpose
Serio PS/2 mouse/touchpad bridge for pointer data and commands transported by NVEC.

## Important APIs, Types, And Functions
`struct nvec_ps2` stores a serio port, notifier, and NVEC pointer. Key functions are `nvec_mouse_probe()`, `nvec_mouse_remove()`, `ps2_sendcommand()`, `ps2_startstreaming()`, `ps2_stopstreaming()`, `nvec_ps2_notifier()`, and PM suspend/resume callbacks.

## Control Flow
Probe allocates a `SERIO_8042` port named `nvec mouse`, fills write/start/stop callbacks, registers an NVEC notifier, and registers the serio port. Starting streaming sends `AUTO_RECEIVE_N` for six-byte packets; stopping sends cancel autoreceive. Serio writes send a synchronous NVEC PS/2 command and feed the response bytes back through `serio_interrupt()`. Asynchronous `NVEC_PS2_EVT` events and command responses are translated to serio interrupts.

## State And Persistence
Uses a static global `ps2_dev`, so only one controller/port is supported. Streaming state is held by EC commands and serio callbacks. No persistent storage exists.

## Dependencies And Integration Points
Depends on NVEC sync/async write APIs, NVEC notifiers, Linux serio/psmouse stack, platform MFD children, and PM sleep.

## Risks
Global singleton blocks multiple instances. Probe uses plain `kzalloc_obj()` for the serio port and relies on `serio_unregister_port()` for cleanup. Command response parsing assumes `msg[2] == 1` and length fields are sane. Remove/suspend send commands that can fail but ignore return values.

## Test Signals
Serio port registration, psmouse probe command exchange, streaming packet delivery, stop/cancel autoreceive, suspend disables and resume re-enables mouse, EC command timeout handling, and notifier unregister on removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/nvec/nvec_ps2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/octeon/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/staging/octeon/Kconfig

## Purpose
Kconfig entry for the Cavium Networks Octeon on-board Ethernet driver.

## Important APIs, Types, And Functions
Defines `OCTEON_ETHERNET` as tristate, depends on `CAVIUM_OCTEON_SOC || COMPILE_TEST` and `NETDEVICES`, and selects `PHYLIB` and `MDIO_OCTEON`.

## Control Flow
Selecting the option builds the multi-file `octeon-ethernet` driver and ensures PHY/MDIO support is available.

## State And Persistence
No runtime state. The symbol persists in the kernel configuration.

## Dependencies And Integration Points
Connects the staging Ethernet driver to Octeon SoC support, netdev core, PHY library, and Cavium MDIO driver.

## Risks
`COMPILE_TEST` is supported through local stubs but real operation requires Octeon hardware and SDK-style CSR helpers. The driver covers older CN3XXX/CN5XXX-era hardware.

## Test Signals
Build under Octeon defconfig, build under `COMPILE_TEST`, dependency selection of `MDIO_OCTEON`, and module name `octeon-ethernet`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/octeon/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/octeon/Makefile -->
# sources/distributed-fs/ceph-client/drivers/staging/octeon/Makefile

## Purpose
Kbuild recipe for the Octeon Ethernet composite object.

## Important APIs, Types, And Functions
Maps `CONFIG_OCTEON_ETHERNET` to `octeon-ethernet.o` and lists component objects: core, MDIO/ethtool, memory pools, RGMII, RX, SGMII, SPI, and TX.

## Control Flow
Kbuild compiles and links the listed objects into one module or built-in driver when enabled.

## State And Persistence
No runtime state. Object ordering is build-time metadata.

## Dependencies And Integration Points
Consumes the `OCTEON_ETHERNET` Kconfig symbol and relies on shared headers in the same directory.

## Risks
The Makefile uses `obj-${CONFIG_OCTEON_ETHERNET}` rather than the more common `obj-$(CONFIG_OCTEON_ETHERNET)` spelling; if not accepted by Kbuild expansion, the driver would not build.

## Test Signals
Build with `CONFIG_OCTEON_ETHERNET=m/y` and verify all listed objects are included in `octeon-ethernet`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/octeon/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/octeon/ethernet-defines.h -->
# sources/distributed-fs/ceph-client/drivers/staging/octeon/ethernet-defines.h

## Purpose
Shared compile-time tuning constants and FAU/FPA indices for the Octeon Ethernet driver.

## Important APIs, Types, And Functions
Defines `REUSE_SKBUFFS_WITHOUT_FREE`, `USE_ASYNC_IOBDMA`, `MAX_OUT_QUEUE_DEPTH`, FAU counter locations, and `TOTAL_NUMBER_OF_PORTS`.

## Control Flow
Included by RX/TX/core files to select fast paths, queue cleanup thresholds, and array sizing. `REUSE_SKBUFFS_WITHOUT_FREE` is disabled when netfilter is enabled; async IOBDMA depends on CVMSEG size.

## State And Persistence
No runtime state. Values shape allocation sizes, buffer reuse behavior, and hardware counter addresses.

## Dependencies And Integration Points
Depends on Octeon CVMX constants from architecture headers or `octeon-stubs.h`.

## Risks
Buffer reuse is explicitly performance-oriented and can expose networking-stack lifetime bugs if an skb is reused without full cleanup. FAU address arithmetic must not collide with other registers.

## Test Signals
Compile with and without `CONFIG_NETFILTER`, with CVMSEG enabled/disabled, verify `TOTAL_NUMBER_OF_PORTS` matches `cvm_oct_device[]`, and stress TX queue cleanup depth.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/octeon/ethernet-defines.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/octeon/ethernet-mdio.c -->
# sources/distributed-fs/ceph-client/drivers/staging/octeon/ethernet-mdio.c

## Purpose
PHY, ethtool, ioctl, carrier logging, and common stop/link helpers for Octeon Ethernet ports.

## Important APIs, Types, And Functions
Exports `cvm_oct_ethtool_ops`, `cvm_oct_ioctl()`, `cvm_oct_note_carrier()`, `cvm_oct_adjust_link()`, `cvm_oct_common_stop()`, and `cvm_oct_phy_setup_device()`.

## Control Flow
EtHTool reports driver info, exposes link state, and delegates link settings to phylib. IOCTL validates the device is running and has a PHY before calling `phy_mii_ioctl()`. PHY setup resolves `phy-handle` or fixed-link OF nodes, connects via `of_phy_connect()`, starts the PHY, or assumes carrier on for direct MAC links. Link adjustment converts phylib status into `cvmx_helper_link_info`, sets hardware link state, and logs changes. Stop disables GMX port, clears polling, disconnects PHY, and reports link down.

## State And Persistence
Updates `struct octeon_ethernet` fields `last_link`, `link_info`, and `poll`. No persistent storage exists.

## Dependencies And Integration Points
Depends on phylib, OF MDIO/fixed-link helpers, netdev ethtool/ioctl hooks, and CVMX link/GMX CSR helpers.

## Risks
No-PHY mode assumes link up. `phydev->duplex` and speed are trusted. Stop directly touches GMX registers and assumes `INTERFACE()`/`INDEX()` are valid for the port.

## Test Signals
PHY and fixed-link DT cases, missing PHY fallback, ethtool get/set link settings, MII ioctl, link-up/down transitions, stop while carrier is up, and probe deferral from missing PHY.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/octeon/ethernet-mdio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/octeon/ethernet-mdio.h -->
# sources/distributed-fs/ceph-client/drivers/staging/octeon/ethernet-mdio.h

## Purpose
Shared declarations and common includes for Octeon PHY/MDIO support.

## Important APIs, Types, And Functions
Declares `cvm_oct_ethtool_ops`, `cvm_oct_ioctl()`, and `cvm_oct_phy_setup_device()`. It includes netdevice, ethtool, proc/seq, routing, and optional XFRM headers.

## Control Flow
Core netdev operations include this header to attach ethtool ops, ioctl handlers, and PHY setup helpers.

## State And Persistence
No state; declarations only.

## Dependencies And Integration Points
Links `ethernet.c`, port-mode helpers, and `ethernet-mdio.c` through shared prototypes and kernel networking headers.

## Risks
Broad includes increase compile coupling. Prototype mismatches would surface at build time.

## Test Signals
Compile all Octeon objects, verify netdev ops can reference the declared symbols, and build with optional XFRM enabled/disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/octeon/ethernet-mdio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/octeon/ethernet-mem.c -->
# sources/distributed-fs/ceph-client/drivers/staging/octeon/ethernet-mem.c

## Purpose
Fills and drains Octeon FPA hardware memory pools used for packet buffers, work queue entries, and output buffers.

## Important APIs, Types, And Functions
Exports `cvm_oct_mem_fill_fpa()` and `cvm_oct_mem_empty_fpa()`. Internal helpers are `cvm_oct_fill_hw_skbuff()`, `cvm_oct_free_hw_skbuff()`, `cvm_oct_fill_hw_memory()`, and `cvm_oct_free_hw_memory()`.

## Control Flow
Packet-pool fills allocate skbs, reserve to a 128-byte boundary with extra headroom, save the skb pointer just before data, and free the aligned data pointer to FPA. Non-packet pools allocate raw kmalloc memory with alignment padding and save the original pointer before the aligned block. Emptying reverses the process by allocating from FPA until empty, recovering the original skb or kmalloc pointer, and freeing it.

## State And Persistence
State lives in FPA pools and hidden back-pointers stored immediately before aligned buffers. No durable state exists.

## Dependencies And Integration Points
Depends on CVMX FPA allocation/free primitives, skb allocation/free, kmalloc/kfree, and pool constants from Octeon headers.

## Risks
Correctness relies on alignment math and metadata stored before the buffer. Drain warnings detect count mismatches but cannot repair leaks. Packet pool buffers are skbs, while other pools are raw memory; using the wrong pool id would free incorrectly.

## Test Signals
Fill and empty each pool, simulate partial allocation failure, verify 128-byte alignment, validate skb back-pointer recovery, check warning paths for too many/missing buffers, and run RX/TX stress with FPA refill.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/octeon/ethernet-mem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/octeon/ethernet-mem.h -->
# sources/distributed-fs/ceph-client/drivers/staging/octeon/ethernet-mem.h

## Purpose
Declaration header for Octeon FPA pool fill/drain helpers.

## Important APIs, Types, And Functions
Declares `cvm_oct_mem_fill_fpa(int pool, int size, int elements)` and `cvm_oct_mem_empty_fpa(int pool, int size, int elements)`.

## Control Flow
Core and RX code call these helpers to populate and replenish hardware pools and to empty them during module removal.

## State And Persistence
No state; prototypes only.

## Dependencies And Integration Points
Included by `ethernet.c`, `ethernet-rx.h`, and `ethernet-mem.c`.

## Risks
Callers must pass the correct pool id, element size, and expected count because the implementation uses those to choose skb versus raw-memory handling.

## Test Signals
Build all call sites and verify pool fill/empty behavior through the implementation tests described for `ethernet-mem.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/octeon/ethernet-mem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/octeon/ethernet-rgmii.c -->
# sources/distributed-fs/ceph-client/drivers/staging/octeon/ethernet-rgmii.c

## Purpose
RGMII/GMII open and link polling support, including a 10Mbps preamble-error workaround.

## Important APIs, Types, And Functions
Exports `cvm_oct_rgmii_open()`. Internal helpers are `cvm_oct_set_hw_preamble()`, `cvm_oct_check_preamble_errors()`, and `cvm_oct_rgmii_poll()`.

## Control Flow
Open calls common PHY/MAC setup with `cvm_oct_rgmii_poll()`. If phylib is used on true RGMII or GMII port 0, it installs periodic preamble checking. The checker takes a global register lock, watches speed changes and GMX preamble error bits, disables hardware preamble checking/FCS stripping for broken 10Mbps links, or re-enables hardware handling when speed changes. Link polling reads CVMX link info, applies it to hardware, updates carrier, and logs changes.

## State And Persistence
Uses global `global_register_lock` plus per-port `last_speed`, `link_info`, `last_link`, and `poll` fields. State is volatile.

## Dependencies And Integration Points
Depends on common open/stop/link helpers, phylib, netdev carrier, and CVMX GMX/IPD CSR access.

## Risks
Global CSR changes affect more than one port, so locking is critical. The software preamble workaround is hardware- and speed-specific. Incorrect `phy_mode` or DT delay settings in `ethernet.c` can affect this path.

## Test Signals
RGMII and GMII open, PHY and no-PHY operation, 10Mbps preamble errors, speed changes re-enabling hardware checks, carrier transitions, and concurrent polling on multiple ports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/octeon/ethernet-rgmii.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/octeon/ethernet-rx.c -->
# sources/distributed-fs/ceph-client/drivers/staging/octeon/ethernet-rx.c

## Purpose
NAPI receive path for Octeon Ethernet packets delivered by POW/SSO work queues.

## Important APIs, Types, And Functions
Defines `struct oct_rx_group` and exports `cvm_oct_rx_initialize()`, `cvm_oct_rx_shutdown()`, and `cvm_oct_poll_controller()` when netpoll is enabled. Important internals include `cvm_oct_do_interrupt()`, `cvm_oct_napi_poll()`, `cvm_oct_poll()`, `cvm_oct_check_rcv_error()`, and `copy_segments_to_skb()`.

## Control Flow
Initialization chooses an existing netdev for NAPI ownership, creates a NAPI instance per configured POW receive group, requests work-queue IRQs, configures interrupt thresholds, disables IRQs, and schedules NAPI to prime receive. IRQs disable themselves and schedule NAPI. Polling restricts the current core to the group, optionally uses async IOBDMA, fetches work entries up to budget, handles receive errors, either reuses an skb stored in the hardware packet pool for single-buffer packets or copies packet data into a fresh skb, maps the hardware port to `cvm_oct_device[]`, sets checksum status, delivers with `netif_receive_skb()`, and frees or refills hardware resources.

## State And Persistence
Static `oct_rx_group[16]` holds IRQ/group/NAPI state, and `oct_rx_ready` gates netpoll. FPA refill debt is tracked through FAU counters. State is runtime-only.

## Dependencies And Integration Points
Depends on netdev/NAPI, POW/SSO work queues, CVMX WQE and FPA structures, global `cvm_oct_device[]`, FPA memory helpers, and hardware group mask CSRs.

## Risks
Zero-copy receive depends on skb pointers stored before FPA buffers and on single-buffer WQEs. Error workaround rewrites packet pointers for bad 10Mbps preambles. Group-mask save/restore and scratch-space save/restore are required to avoid corrupting other users. Invalid or down ports drop packets.

## Test Signals
Single and multi-segment packets, WQE-contained packets, checksum flags, receive errors including length/FCS/alignment, down or unknown ports, multiple receive groups, CN68XX versus older POW paths, NAPI budget completion, netpoll, and FPA refill under pressure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/octeon/ethernet-rx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/octeon/ethernet-rx.h -->
# sources/distributed-fs/ceph-client/drivers/staging/octeon/ethernet-rx.h

## Purpose
RX declarations and inline FPA packet-pool refill helper for Octeon Ethernet.

## Important APIs, Types, And Functions
Declares `cvm_oct_poll_controller()`, `cvm_oct_rx_initialize()`, and `cvm_oct_rx_shutdown()`. Defines inline `cvm_oct_rx_refill_pool(int fill_threshold)`.

## Control Flow
The refill helper reads the FAU count of packet buffers to replace, and if the count exceeds the threshold, decrements the debt, fills the FPA packet pool, and restores any unfilled remainder to the counter.

## State And Persistence
Manipulates the hardware FAU packet-buffer debt counter. No header-local state.

## Dependencies And Integration Points
Depends on `FAU_NUM_PACKET_BUFFERS_TO_FREE`, `CVMX_FPA_PACKET_POOL`, `CVMX_FPA_PACKET_POOL_SIZE`, and `cvm_oct_mem_fill_fpa()`.

## Risks
Incorrect thresholding can starve the packet pool or over-refill. Partial fill errors must restore debt accurately.

## Test Signals
RX refill worker and NAPI refill paths, partial FPA allocation failure, threshold behavior, and packet-pool starvation recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/octeon/ethernet-rx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/octeon/ethernet-sgmii.c -->
# sources/distributed-fs/ceph-client/drivers/staging/octeon/ethernet-sgmii.c

## Purpose
Minimal SGMII mode integration for Octeon Ethernet ports.

## Important APIs, Types, And Functions
Exports `cvm_oct_sgmii_init()` and `cvm_oct_sgmii_open()`.

## Control Flow
Initialization delegates to `cvm_oct_common_init()` and leaves a FIXME for autonegotiation logic. Open delegates to `cvm_oct_common_open()` with generic CVMX link polling.

## State And Persistence
Uses common per-netdev `struct octeon_ethernet` state only. No file-local state.

## Dependencies And Integration Points
Integrates SGMII netdev ops in `ethernet.c` with common init/open/link code and phylib/MDIO support.

## Risks
Autonegotiation is explicitly incomplete. SGMII behavior relies on common link polling or PHY setup rather than mode-specific configuration.

## Test Signals
SGMII port registration, common init side effects, PHY link negotiation, carrier polling, and regression around the FIXME on autoneg-capable hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/octeon/ethernet-sgmii.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/octeon/ethernet-spi.c -->
# sources/distributed-fs/ceph-client/drivers/staging/octeon/ethernet-spi.c

## Purpose
SPI4 Ethernet interface support for Octeon, including error interrupt handling and retraining.

## Important APIs, Types, And Functions
Exports `cvm_oct_spi_init()` and `cvm_oct_spi_uninit()`. Internal helpers include `cvm_oct_spi_rml_interrupt()`, `cvm_oct_spi_spx_int()`, `cvm_oct_spi_enable_error_reporting()`, `cvm_oct_spi_poll()`, `cvm_oct_spxx_int_pr()`, and `cvm_oct_stxx_int_pr()`.

## Control Flow
First SPI port initialization requests the shared RML IRQ. Interface-leading ports enable SPX/STX error masks and install `cvm_oct_spi_poll()`. RML interrupt checks SPX blocks, prints masked errors unless retraining is already pending, disables masks, and sets `need_retrain`. Polling restarts interfaces needing retrain, re-enables error reporting on success, and slowly checks SPI4000 speed for one port per second. Uninit decrements the active-port count; the last port disables masks and frees the IRQ.

## State And Persistence
Static `number_spi_ports` counts users, and `need_retrain[2]` tracks per-interface retraining. Per-port `priv->poll` is set for leading ports. State is runtime-only.

## Dependencies And Integration Points
Depends on common init/uninit, CVMX SPI/SPX/STX/NPI CSRs, RML IRQ, netdev private port/interface mapping, and SPI4000 helper code.

## Risks
Shared IRQ lifetime depends on correct active-port counting. Error masks are disabled on first error until polling retrains. Slow SPI4000 polling delays speed-change detection. Only two SPI interfaces are tracked.

## Test Signals
Single and multiple SPI ports, RML interrupt from SPX0/SPX1, each error bit log path, retrain success/failure, uninit of last port freeing IRQ, and SPI4000 speed polling rotation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/octeon/ethernet-spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/octeon/ethernet-tx.c -->
# sources/distributed-fs/ceph-client/drivers/staging/octeon/ethernet-tx.c

## Purpose
Transmit path for Octeon Ethernet hardware queues and optional POW software handoff.

## Important APIs, Types, And Functions
Exports `cvm_oct_xmit()`, `cvm_oct_xmit_pow()`, `cvm_oct_transmit_qos()` by declaration context, `cvm_oct_tx_initialize()`, `cvm_oct_tx_shutdown()`, and `cvm_oct_tx_shutdown_dev()`. Important internals are `cvm_oct_free_tx_skbs()`, `cvm_oct_adjust_skb_to_free()`, `cvm_oct_kick_tx_poll_watchdog()`, cleanup tasklet, and timer IRQ handler.

## Control Flow
`cvm_oct_xmit()` selects a QoS queue, optionally linearizes skbs with too many fragments, pads small CN3XXX half-duplex frames, builds PKO command and buffer/gather pointers, optionally places eligible skb data buffers into the FPA for hardware freeing, enables IPv4 TCP/UDP checksum offload, checks FAU cleanup counters, throttles when the free-list depth is high, sends through PKO, queues core-owned skbs for later cleanup or records hardware-free debt, frees completed skbs, and arms a timer watchdog. `cvm_oct_xmit_pow()` copies skb data into FPA packet memory, builds a WQE, submits it to a POW group, updates stats, and consumes the skb. Cleanup tasklet scans all devices and frees skbs whose FAU counters show hardware completion.

## State And Persistence
Uses per-port `tx_free_list[qos]`, FAU outstanding counters, static cleanup tasklet, and CIU timer interrupt. Scratch registers are saved/restored around async IOBDMA. No durable state.

## Dependencies And Integration Points
Depends on netdev TX APIs, PKO, POW, FPA, FAU, CVMX scratch/IOBDMA, skb fragment APIs, checksum/IP helpers, global `cvm_oct_device[]`, and queue stop/wake.

## Risks
The skb reuse fast path is delicate and must reset stack-owned metadata correctly. Queue-depth handling can stop/wake netdev queues under lock pressure. Fragment gather supports at most six segment pointers. Hardware-free versus core-free accounting uses negative FAU conventions that are easy to regress.

## Test Signals
Linear and fragmented skbs, more than five frags, short CN3XXX half-duplex packets, checksum offload eligibility, queue stop/wake at depth, hardware-free skb reuse with netfilter on/off, POW transmit, cleanup timer/tasklet, shutdown draining all QoS lists, and TX failure/drop paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/octeon/ethernet-tx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/octeon/ethernet-tx.h -->
# sources/distributed-fs/ceph-client/drivers/staging/octeon/ethernet-tx.h

## Purpose
Transmit declarations for Octeon Ethernet.

## Important APIs, Types, And Functions
Declares `cvm_oct_xmit()`, `cvm_oct_xmit_pow()`, `cvm_oct_transmit_qos()`, `cvm_oct_tx_initialize()`, `cvm_oct_tx_shutdown()`, and `cvm_oct_tx_shutdown_dev()`.

## Control Flow
`ethernet.c` netdev ops call `cvm_oct_xmit()` for hardware ports and `cvm_oct_xmit_pow()` for the virtual POW device; module probe/remove call TX initialize/shutdown helpers.

## State And Persistence
No header-local state. Functions operate on per-netdev TX lists and hardware counters.

## Dependencies And Integration Points
Included by core and TX implementation files; uses kernel `netdev_tx_t`, `sk_buff`, and `net_device`.

## Risks
The declaration of `cvm_oct_transmit_qos()` must match an implementation elsewhere in the driver snapshot or trigger link failures if referenced.

## Test Signals
Build/link checks and TX path tests from `ethernet-tx.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/octeon/ethernet-tx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/octeon/ethernet-util.h -->
# sources/distributed-fs/ceph-client/drivers/staging/octeon/ethernet-util.h

## Purpose
Small inline helpers for translating Octeon hardware buffer and port identifiers.

## Important APIs, Types, And Functions
Defines `cvm_oct_get_buffer_ptr()`, `INTERFACE()`, and `INDEX()`.

## Control Flow
RX/TX/free paths call `cvm_oct_get_buffer_ptr()` to recover the original aligned packet-buffer pointer from a `cvmx_buf_ptr`. Port setup and register programming call `INTERFACE()` and `INDEX()` to map IPD ports to helper interface/index values, with special handling for the POW virtual port.

## State And Persistence
No state.

## Dependencies And Integration Points
Depends on CVMX physical-address conversion and helper port mapping APIs. Included by most Octeon implementation files.

## Risks
`INTERFACE()` panics on illegal ports, so callers must validate hardware port ids. Buffer pointer arithmetic assumes Octeon FPA back-pointer semantics and 128-byte alignment.

## Test Signals
Known port/interface mappings, virtual POW port mapping to interface 10, invalid port panic expectations, and RX/TX buffer pointer round-trip tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/octeon/ethernet-util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/octeon/ethernet.c -->
# sources/distributed-fs/ceph-client/drivers/staging/octeon/ethernet.c

## Purpose
Main platform driver for Cavium Octeon on-board Ethernet. It configures shared hardware, allocates one netdev per hardware port plus an optional POW virtual device, wires mode-specific netdev ops, and coordinates RX/TX subsystem startup/shutdown.

## Important APIs, Types, And Functions
Important module parameters include `num_packet_buffers`, `pow_receive_group`, `receive_group_order`, `pow_send_group`, `always_use_pow`, `pow_send_list`, and `rx_napi_weight`. Key functions are `cvm_oct_probe()`, `cvm_oct_remove()`, `cvm_oct_configure_common_hw()`, `cvm_oct_common_init()`, `cvm_oct_common_uninit()`, `cvm_oct_common_open()`, `cvm_oct_common_change_mtu()`, `cvm_oct_common_set_multicast_list()`, `cvm_oct_common_set_mac_address()`, `cvm_oct_link_poll()`, and periodic/refill workers.

## Control Flow
Probe requires a PIP OF node, enables and fills FPA pools, initializes packet IO, configures POW receive groups and PIP tag registers, enables input, initializes FAU counters, optionally creates a `pow%d` netdev, then iterates hardware interfaces and ports. For each supported mode it allocates an Ethernet netdev, stores `struct octeon_ethernet`, finds the DT child node, initializes per-QoS TX lists and FAU offsets, selects mode-specific netdev ops/name/PHY mode, registers fixed links, registers the netdev, stores it in `cvm_oct_device[]`, and schedules periodic work. After registration it starts TX and RX subsystems and the RX refill worker. Remove disables IPD/PKO, stops workers, shuts down RX/TX, unregisters/free netdevs, shuts hardware down, and drains FPA pools.

## State And Persistence
Global state includes module parameters, `pow_receive_groups`, `cvm_oct_poll_queue_stopping`, `cvm_oct_device[]`, and `cvm_oct_tx_poll_interval`. Per-port state lives in `struct octeon_ethernet`. All state is volatile.

## Dependencies And Integration Points
Depends on Octeon CVMX helper/IPD/PIP/PKO/FPA/FAU APIs, OF net/MDIO/fixed-link helpers, phylib, netdev core, VLAN constants, and local RX/TX/memory/mode helpers.

## Risks
The driver touches global hardware state and assumes bootloader counters need clearing. Error handling during multi-port probe is mostly per-port continue, so partial registration is possible. `pow_send_list` uses substring matching on netdev names. Device removal must preserve ordering across IPD, RX/TX, PKO, netdev unregister, and FPA drain.

## Test Signals
Probe on each interface mode, optional POW device, multiple receive groups, DT child and fixed-link mapping, MTU programming with VLAN, multicast/promisc/MAC filter changes, carrier polling, per-port periodic worker, remove after partial probe, FPA pool counts, and RX/TX subsystem initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/octeon/ethernet.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/octeon/octeon-ethernet.h -->
# sources/distributed-fs/ceph-client/drivers/staging/octeon/octeon-ethernet.h

## Purpose
Primary shared header for the Octeon Ethernet driver, selecting real Octeon architecture headers or compile-test stubs and defining per-netdev private state.

## Important APIs, Types, And Functions
Defines `struct octeon_ethernet` with hardware port/queue/FAU, netdev pointer, interface mode, PHY mode, TX free lists, link state, poll callback, periodic work, and OF node. Declares common, mode-specific, TX/RX, carrier, and global driver symbols.

## Control Flow
All implementation files include this header to access CVMX types and shared driver APIs. `ethernet.c` allocates `struct octeon_ethernet` as netdev private data and mode files consume it.

## State And Persistence
The header defines runtime state shape but stores no data itself. Externs expose module-global state in `ethernet.c`.

## Dependencies And Integration Points
On real Octeon builds it includes many `<asm/octeon/cvmx-...>` headers. Under non-Octeon compile tests it includes `octeon-stubs.h`. It also integrates OF and phylib types.

## Risks
The compatibility boundary between real architecture headers and stubs is broad. Any missing CVMX declaration breaks compile-test or target builds. `struct octeon_ethernet` embeds fixed 16 TX QoS queues, matching assumptions in TX cleanup.

## Test Signals
Compile under `CONFIG_CAVIUM_OCTEON_SOC` and `COMPILE_TEST`, check all shared prototypes, and validate netdev private layout use across core/RX/TX/mode files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/octeon/octeon-ethernet.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/octeon/octeon-stubs.h -->
# sources/distributed-fs/ceph-client/drivers/staging/octeon/octeon-stubs.h

## Purpose
Compile-test shim that provides enough Octeon CVMX constants, types, unions, and inline functions to build the staging Ethernet driver on non-Octeon platforms.

## Important APIs, Types, And Functions
Defines IRQ/model/feature macros, FPA/FAU/GMX/PIP/POW/PKO constants, CVMX WQE and buffer pointer unions, link-info structures, many CSR union layouts, interface-mode enums, and no-op or dummy inline functions for FAU, scratch, FPA, helper, POW, SPI, PKO, and WQE operations.

## Control Flow
`octeon-ethernet.h` includes this file when `CONFIG_CAVIUM_OCTEON_SOC` is not set. The stubs return harmless zero/null values or no-op for hardware operations, allowing type checking and dead-code compile coverage but not real runtime behavior.

## State And Persistence
No real state. Inline functions do not model hardware; most return constants, null pointers, or their input value.

## Dependencies And Integration Points
Bridges Octeon-specific implementation files to generic kernel compile-test builds. It must track the subset of CVMX API and bitfields used by this driver.

## Risks
Because behavior is fake, compile-test can miss runtime ordering, counter, and null-pointer issues. Some stub return values such as zero queues or null FPA allocations can make accidental execution unsafe. Bitfield definitions must remain close enough to real headers for code to compile correctly.

## Test Signals
`COMPILE_TEST` builds on non-Octeon architectures, enabling optional netfilter/XFRM/VLAN variations. Runtime should not bind on non-Octeon hardware; target-hardware testing must use real CVMX headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/octeon/octeon-stubs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/Kconfig

## Purpose
Kconfig entry for the Realtek RTL8723BS SDIO wireless LAN staging driver.

## Important APIs, Types, And Functions
Defines `RTL8723BS` as a tristate option depending on `WLAN`, `MMC`, `CFG80211`, and `m`, and selecting AES, ARC4, and crypto utility libraries.

## Control Flow
When enabled as a module, Kbuild builds the large `r8723bs` composite driver for SDIO Wi-Fi devices such as Intel Compute Stick and CHIP-era boards.

## State And Persistence
No runtime state. The symbol is build configuration state.

## Dependencies And Integration Points
Integrates with cfg80211, MMC/SDIO, crypto libraries, and the driver Makefile.

## Risks
The explicit `depends on m` prevents built-in selection. Being staging code, it carries legacy Realtek architecture and broad internal APIs.

## Test Signals
Kconfig should only allow module builds with required dependencies; `CONFIG_RTL8723BS=m` should build `r8723bs.ko` and select crypto helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/Makefile -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/Makefile

## Purpose
Kbuild recipe for the monolithic RTL8723BS SDIO Wi-Fi module.

## Important APIs, Types, And Functions
Defines `r8723bs-y` as a long object list across `core`, `hal`, and `os_dep`, maps `obj-$(CONFIG_RTL8723BS) := r8723bs.o`, and adds include paths for `include` and `hal`.

## Control Flow
Kbuild compiles all listed Realtek core/PHY/SDIO/OS abstraction objects into one module when `RTL8723BS` is selected.

## State And Persistence
No runtime state. Object composition and include search paths are build metadata.

## Dependencies And Integration Points
Coordinates AP/BT coexistence objects researched here with command, MLME, security, receive/transmit, HAL, SDIO, cfg80211, and regulatory code.

## Risks
The module is tightly coupled; missing one object often breaks many internal symbols. Legacy indentation and broad include paths can hide include-order assumptions.

## Test Signals
Full module build, link all internal Realtek symbols, and verify `ccflags-y` resolves `<drv_types.h>` and HAL headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/core/rtw_ap.c -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/core/rtw_ap.c

## Purpose
Access-point mode management for the RTL8723BS driver. It parses hostapd beacon data, starts/restores/stops BSS state, maintains associated station state, handles beacon/TIM/capability updates, manages AP security keys and ACLs, and ages inactive stations.

## Important APIs, Types, And Functions
Key entry points include `init_mlme_ap_info()`, `free_mlme_ap_info()`, `start_bss_network()`, `rtw_check_beacon_data()`, `expire_timeout_chk()`, `add_ratid()`, `update_bmc_sta()`, `update_sta_info_apmode()`, `sta_info_update()`, `ap_sta_info_defer_update()`, `bss_cap_update_on_sta_join()`, `bss_cap_update_on_sta_leave()`, `ap_free_sta()`, `rtw_sta_flush()`, `rtw_ap_restore_network()`, `start_ap_mode()`, `stop_ap_mode()`, `update_beacon()`, ACL helpers, and key helpers `rtw_ap_set_pairwise_key()`, `rtw_ap_set_group_key()`, `rtw_ap_set_wep_key()`.

## Control Flow
AP initialization sets locks, ACL queues, and AP counters. `rtw_check_beacon_data()` validates the driver is in AP state, copies supplied beacon IEs, extracts beacon interval/capability/SSID/channel/rates, parses ERP, WPA/WPA2, WMM, HT capability/operation, updates security and HT/QoS state, starts BSS through the command path, allocates the AP's own station info, and indicates connection. `start_bss_network()` programs hardware BSSID, security, EDCA, beacon interval, channel/bandwidth, basic rates, capability, beacon/TIM, and bc/mc station state. Station join/update paths calculate QoS/HT/VCS/rate masks and update beacon protection counters; leave/free paths tear down AMPDU, clear keys, notify cfg80211/firmware, update counters, and free station info. Periodic expiry checks auth/asoc lists, sends null-data keepalives when configured, handles sleeping stations through TIM bits, and flushes dead stations.

## State And Persistence
State spans `mlme_priv`, `mlme_ext_priv`, `sta_priv`, `security_priv`, per-station HT/security fields, ACL list, TIM bitmap, beacon IE buffers, AP capability counters, and hardware CAM/key/rate state. It is all runtime state; WPS/P2P IE pointers are reset on AP mode start/stop.

## Dependencies And Integration Points
Depends on Realtek MLME, command, station management, security, HAL register/key/rate APIs, cfg80211 notifications, beacon command transmission, HT/WMM/ERP parsers, SDIO channel selection, and BT coexistence disconnect notification.

## Risks
The code mutates raw beacon IE buffers and uses many protocol offsets, so length validation is critical. Several beacon update stubs are empty, leaving some IEs unchanged. `rtw_ht_operation_update()` returns early when HT is enabled, which may be intentional legacy behavior but is easy to misread. Station list manipulation mixes locks with callbacks that may free state. Static ACL capacity is fixed. Security key commands are asynchronous and allocation failures return generic `_FAIL`.

## Test Signals
Hostapd AP start with open/WEP/WPA/WPA2, WMM and HT beacons, 20/40 MHz channel selection, TIM updates for sleeping stations, station join/leave capability counters, ACL add/remove/broadcast clear, pairwise/group/WEP key installation, inactive station expiry and keepalive, AP restore after power save, AP stop cleanup, and cfg80211 disassociation events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/core/rtw_ap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/core/rtw_btcoex.c -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/core/rtw_btcoex.c

## Purpose
Small core wrapper layer connecting RTL8723BS MLME/power-save behavior to the HAL Bluetooth coexistence implementation.

## Important APIs, Types, And Functions
Defines `rtw_btcoex_MediaStatusNotify()`, `rtw_btcoex_HaltNotify()`, `rtw_btcoex_RejectApAggregatedPacket()`, `rtw_btcoex_LPS_Enter()`, and `rtw_btcoex_LPS_Leave()`.

## Control Flow
Media-status notification downloads reserved pages when connecting in AP mode, then forwards status to HAL coexistence. Halt notification returns early if the adapter is not up or surprise-removed, then calls HAL halt handling. AP aggregation rejection disables accepting ADDBA requests and sends DELBA to the current BSSID station; disabling re-allows ADDBA. LPS enter marks power saving, asks HAL for coexistence LPS value, and enters minimum power-save mode. LPS leave restores active power mode, waits for RF on, and clears the power-saving flag.

## State And Persistence
Mutates `mlmeext_info.accept_addba_req`, station aggregation state through DELBA, and `pwrctrl_priv` power-save flags/mode. No persistent state.

## Dependencies And Integration Points
Depends on Realtek adapter structures, HAL BT coexistence callbacks, MLME AP-state checks, reserved-page hardware variable, station lookup, DELBA transmission, and power-control APIs.

## Risks
Aggregation rejection only finds a station by current BSSID, which may not cover all AP-mode clients. Power-save transitions are driven by coexistence policy and can interact with normal MLME power management. Halt notification silently skips on device-down/surprise-removed paths.

## Test Signals
BT coexistence media connect/disconnect in AP and STA modes, reserved-page download on AP connect, HAL halt calls, ADDBA rejection and DELBA side effects, LPS enter/leave transitions, RF-on check timeout, and surprise removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/core/rtw_btcoex.c -->
