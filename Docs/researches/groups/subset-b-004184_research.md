# subset-b-004184 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/ite-cir.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/ite-cir.c

## Purpose

`ite-cir.c` is the Linux rc-core PNP driver for ITE Consumer IR transceivers, covering direct IT87-style CIR blocks and IT8512-based bridges exposed as ITE8708 or ITE8709. It receives raw IR samples, decodes hardware FIFO bytes into `ir_raw_event` pulse/space durations, supports IR transmit through run-length encoded FIFO writes, and registers an `rc_dev` with receive, transmit, carrier, duty-cycle, idle, open, and close callbacks.

## Important APIs, Types, and Functions

- Module parameters `sample_period` and `model_number` tune the sample clock and optionally override PNP model autodetection.
- `ite_decode_bytes()` converts little-endian bit runs from RX FIFO bytes into pulse/space events with `ir_raw_event_store_with_filter()` and `ir_raw_event_handle()`.
- `ite_set_carrier_params()`, `ite_get_carrier_freq_bits()`, and `ite_get_pulse_width_bits()` translate rc-core carrier/duty settings into chip-specific register fields through the active `ite_dev_params` backend.
- `ite_cir_isr()` handles RX FIFO, RX overrun, and TX FIFO-space interrupts under `dev->lock`, deliberately dropping the lock before handing received data to rc-core.
- `ite_tx_ir()` is the transmit path; it disables RX, encodes alternating pulse/space durations into 7-bit run-length bytes, blocks on `tx_queue` when the TX FIFO is full, waits for the remaining FIFO time, restores RX parameters, and wakes `tx_ended`.
- Hardware backend functions implement IT87 direct I/O, IT8708 banked IT8512 access, and IT8709 SRAM/microcontroller bridge access.
- `ite_probe()`, `ite_remove()`, `ite_suspend()`, `ite_resume()`, and `ite_shutdown()` bind the PNP device, register rc-core state, claim I/O and IRQ resources, and handle power transitions.

## Control Flow

Probe allocates `struct ite_dev` and `struct rc_dev`, selects a model from `ite_ids[]` or the `model_number` override, validates PNP port and IRQ resources, initializes locks and wait queues, programs default carrier and FIFO registers, fills rc-core callbacks, registers the `rc_dev`, claims the I/O region, and finally requests the shared IRQ. Opening the rc device enables RX; closing waits for any in-flight transmit and disables the backend.

Receive flow starts in `ite_cir_isr()`: the backend reports interrupt causes, RX overflow is signaled to rc-core, FIFO bytes are read into a 32-byte stack buffer, and the lock is dropped while the raw event layer receives decoded pulse/space events. Transmit flow starts from rc-core `tx_ir`, switches the device into transmit mode, updates carrier registers, disables RX, writes RLE bytes to the TX FIFO, sleeps on an interrupt-driven wait queue when fewer than eight slots are available, delays for the final queued duration, then re-enables RX and wakes close/suspend waiters.

## State and Persistence Behavior

Driver-owned state lives in `struct ite_dev`: the PNP and rc-core objects, spinlock, `transmitting` flag, two wait queues, RX carrier range, TX carrier/duty settings, I/O base, IRQ, and the selected immutable backend descriptor. Hardware state persists in CIR registers and FIFOs until reset, shutdown, suspend, or backend disable. The driver does not write disk state; module parameters and userspace rc-core configuration determine behavior across loads.

## Dependencies and Integration Points

The file depends on PNP discovery, port I/O helpers (`inb`/`outb`), IRQ infrastructure, wait queues, rc-core raw-event APIs, input IDs, and constants from `ite-cir.h`. It integrates with rc-core as an `RC_DRIVER_IR_RAW` device with `allowed_protocols = RC_PROTO_BIT_ALL_IR_DECODER` and default map `RC_MAP_RC6_MCE`. It also consumes Linux PCI vendor IDs for ITE input identification and relies on the keymap and decoder infrastructure to convert raw events into user-visible key events.

## Risks and Edge Cases

The TX path calls `get_tx_used_slots()` while waiting without holding the spinlock, which the source comments acknowledge as an assumption. `wait_event_interruptible()` return values are ignored in TX, close, and suspend paths, so signal interruption does not abort or report partial progress. The IT8709 SRAM bridge clears RX FIFO state through a protocol described as inherently racy, making overflow and lost samples plausible under load. Carrier calculations clamp ranges but accept arbitrary module/user inputs; invalid duty-cycle values from callers would distort pulse width selection. Resource teardown must respect the order `free_irq`, `release_region`, `rc_unregister_device`, and `kfree` to avoid IRQ callbacks touching freed state. Incorrect model override can select the wrong register backend and write unrelated I/O ports.

## Test Signals

Build coverage should include the PNP driver and all three backend families. Runtime tests should probe each supported PNP ID, open/close the rc device repeatedly, receive known NEC/RC5/RC6 remotes through raw decoders, inject or observe RX overrun handling, transmit long pulse trains that exceed the 32-byte FIFO, verify `s_tx_carrier`, `s_tx_duty_cycle`, and `s_rx_carrier_range`, suspend/resume during idle and after TX, unload while no users are active, and exercise the `model_number` override only on controlled hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/ite-cir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/ite-cir.h -->
# sources/distributed-fs/ceph-client/drivers/media/rc/ite-cir.h

## Purpose

`ite-cir.h` is the private hardware contract for the ITE CIR driver. It defines the shared device model, backend operation table, FIFO/IRQ constants, carrier-frequency conversion limits, transmit RLE encoding, and register offsets/bit masks for IT87, IT8512, ITE8708, and ITE8709 access paths. The header has no executable code beyond simple conversion macros; it gives `ite-cir.c` the exact fields needed to program several related hardware generations through one common driver.

## Important APIs, Types, and Functions

- `struct ite_dev_params` describes one supported model, including I/O region size/resource number and function pointers for IRQ cause detection, RX enable/idle/disable, RX FIFO readout, TX interrupt control, TX FIFO occupancy/write, hardware disable/init, and carrier programming.
- `struct ite_dev` stores PNP/rc-core pointers, `spinlock_t lock`, `transmitting`, TX wait queues, carrier and duty settings, I/O/IRQ resources, and the selected `ite_dev_params`.
- Common constants define FIFO sizes, software interrupt cause bits, baud divisor, low/high carrier ranges, default carrier, demodulator tolerance units, high-frequency carrier selectors, transmit pulse-width selectors, and TX byte layout (`ITE_TX_SPACE`, `ITE_TX_MAX_RLE`, `ITE_TX_RLE_MASK`).
- Register blocks define direct IT87 offsets and masks, generic IT85 CIR register fields, ITE8708 bank-select mappings, and ITE8709 SRAM bridge offsets and request modes.

## Control Flow

The header itself has no control flow. At runtime, `ite_probe()` selects one `ite_dev_params` instance and all driver operations dispatch through its function pointers. The macros and bit masks are used by backend helpers to initialize hardware, identify pending IRQ causes, drain RX FIFOs, feed TX FIFOs, clear FIFO state, toggle interrupts, and program carrier/demodulator parameters.

## State and Persistence Behavior

No state is allocated or persisted by this header. It defines the in-memory shape of driver state and the register-backed hardware state that `ite-cir.c` mutates. The fields in `struct ite_dev` persist for the lifetime of a bound PNP device; hardware register values persist until reset, disable, suspend, resume reinitialization, or module unload.

## Dependencies and Integration Points

The declarations depend on kernel types made available before inclusion, including `struct pnp_dev`, `struct rc_dev`, `spinlock_t`, wait queues, `u8`, and `bool`. The header is tightly coupled to `ite-cir.c`; the operation table mirrors every backend hook implemented there. It also bridges ITE hardware documentation into rc-core concepts such as sample periods, carrier ranges, pulse widths, and raw IR FIFO data.

## Risks and Edge Cases

Register constants are untyped preprocessor values, so a wrong offset, mask, or bank-select bit can compile cleanly while corrupting the wrong I/O register. The IT8708 mapping is based on reverse-engineered bank layout with some unknown registers, and the IT8709 SRAM protocol is explicitly reverse engineered, so those constants carry higher hardware-compatibility risk than direct IT87 definitions. Comments note that most backend operations must be called with the spinlock held, but the type system cannot enforce that contract. The `rx_high_carrier_freq` comment labels it as TX high carrier frequency, which can confuse maintenance even though the field is used as the high end of the RX carrier range.

## Test Signals

Useful validation includes compile coverage of `ite-cir.c`, static review that every backend fills all `ite_dev_params` hooks, hardware smoke tests for each PNP ID, register read/write tracing during init/disable/RX/TX, carrier-frequency tests across low and high ranges, and regression tests that RX FIFO, TX FIFO, bank switching, and SRAM bridge constants still match known working hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/ite-cir.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/Kconfig

## Purpose

`drivers/media/rc/keymaps/Kconfig` declares `config RC_MAP`, the tristate build option that controls compilation of the kernel remote-controller keymap modules. It gates the large collection of small rc-core scan-code tables under `drivers/media/rc/keymaps`.

## Important APIs, Types, and Functions

- `config RC_MAP` is prompted as "Compile Remote Controller keymap modules".
- It depends on `RC_CORE`, so the maps are only buildable when the remote-controller core exists.
- It defaults to `y`, which makes in-kernel keymaps available by default.
- The help text points users who prefer userspace-loaded maps to `ir-keytable` from v4l-utils.

## Control Flow

There is no runtime control flow. Kconfig resolves `CONFIG_RC_MAP` to built-in, module, or disabled. Kbuild then evaluates the keymaps `Makefile`, building every `obj-$(CONFIG_RC_MAP)` entry as built-in objects or modules. At runtime, each built map registers itself with rc-core through its own init hook, unless it is a special rc-core-linked map such as CEC.

## State and Persistence Behavior

The only persistent state is the kernel `.config` value and the resulting build artifacts. No device state, key state, or user remap is stored here. Disabling the option removes the built-in map set, leaving userspace tooling or driver-specific defaults to supply maps.

## Dependencies and Integration Points

`RC_MAP` integrates the keymap directory with `RC_CORE`, the rc-core registry, module autoloading, and v4l-utils compatibility. It indirectly affects many receiver drivers whose default `map_name` values assume these maps are available in the kernel or loadable as modules.

## Risks and Edge Cases

Changing the default or dependency can remove expected keymaps from common media builds. If `RC_MAP=m`, drivers that request maps by name depend on module availability and aliases; if disabled, default remotes may produce raw scancodes but no key events until userspace loads a table. The help text references external tooling and can drift from current package names or URLs.

## Test Signals

Build matrix tests should cover `CONFIG_RC_MAP=y`, `=m`, and unset with `RC_CORE` enabled and disabled. Runtime signals include map lookup success for representative `RC_MAP_*` names, module autoload for map modules, and successful userspace fallback through `ir-keytable` when kernel maps are disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/Makefile

## Purpose

`drivers/media/rc/keymaps/Makefile` is the Kbuild manifest for the rc-core remote-controller keymap modules. It lists the individual `rc-*.o` objects that are built when `CONFIG_RC_MAP` is enabled and asks maintainers to keep the list alphabetically sorted by directory/file name.

## Important APIs, Types, and Functions

- `obj-$(CONFIG_RC_MAP) += ...` attaches the whole keymap object list to the `RC_MAP` Kconfig symbol.
- This snapshot lists 138 keymap objects, including the files covered by this work item such as `rc-adstech-dvb-t-pci.o`, `rc-hauppauge.o`, and `rc-mygica-utv3.o`.
- `rc-cec.o` is intentionally not in this list; it is linked through the parent rc-core Makefile under `CONFIG_MEDIA_CEC_RC`.

## Control Flow

There is no runtime flow. During Kbuild evaluation, enabled objects are compiled either into the kernel or into modules according to `CONFIG_RC_MAP`. Each compiled keymap C file then supplies its own module initialization path that registers a `struct rc_map_list` with rc-core.

## State and Persistence Behavior

The file controls build artifacts only. Omitting an object prevents that keymap from existing as a built-in or module. Adding an object makes the static map available for rc-core registration but does not create runtime state until the object is loaded or linked.

## Dependencies and Integration Points

The Makefile depends on `drivers/media/rc/keymaps/Kconfig`, Kbuild composite-object semantics, and the source filenames in this directory. It integrates with receiver drivers via the `RC_MAP_*` names exported by the compiled objects and with distribution packaging through the module set produced for media keymaps.

## Risks and Edge Cases

The list is hand-maintained and large, so missing a new `rc-*.c`, leaving a deleted object, or breaking alphabetical order are common maintenance risks. Build failures catch stale filenames, but omission of a valid new map may only appear as runtime map lookup failure. Special maps such as CEC must remain in the parent rc-core build path rather than this generic `CONFIG_RC_MAP` list.

## Test Signals

Useful checks include `make M=drivers/media/rc/keymaps`, full media builds with `CONFIG_RC_MAP=y` and `=m`, `LC_ALL=C sort` comparison for list ordering, module packaging checks for expected `rc-*.ko` outputs, and runtime lookup or autoload tests for representative maps from the beginning, middle, and end of the list.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-adstech-dvb-t-pci.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-adstech-dvb-t-pci.c

## Purpose

`rc-adstech-dvb-t-pci.c` provides the `RC_MAP_ADSTECH_DVB_T_PCI` remote-controller keymap for `ADS Tech Instant TV DVB-T PCI Remote`. It is a data-only rc-core map: decoded remote-control scan codes are translated into Linux input `KEY_*` events for the bundled receiver or board driver. The table has 44 scan-code entries; early entries include `0x4d->KEY_NUMERIC_0`, `0x57->KEY_NUMERIC_1`, `0x4f->KEY_NUMERIC_2`, `0x53->KEY_NUMERIC_3`, `0x56->KEY_NUMERIC_4`, `0x4e->KEY_NUMERIC_5`. The represented controls cover numeric entry, power/input selection, navigation/menu, channel/volume, DVR/media transport, colored function keys, teletext/EPG/application keys.

## Important APIs, Types, and Functions

- `struct rc_map_table adstech_dvb_t_pci[]` is the static scan-code-to-keycode table.
- `struct rc_map_list adstech_dvb_t_pci_map` publishes `.scan = adstech_dvb_t_pci`, `.size = ARRAY_SIZE(adstech_dvb_t_pci)`, `.rc_proto = RC_PROTO_UNKNOWN`, and `.name = RC_MAP_ADSTECH_DVB_T_PCI` to rc-core.
- The module init function calls `rc_map_register()` and the exit function calls `rc_map_unregister()`, so the map is visible to rc-core only while the object is built in or the module is loaded.
- It has normal `module_init()`/`module_exit()` hooks.

## Control Flow

There is no active decode algorithm in this file. At build or module-load time, the map is registered with the rc-core map registry. A receiver driver later sets an `rc_dev->map_name` matching `RC_MAP_ADSTECH_DVB_T_PCI` or userspace selects that map with tooling such as `ir-keytable`; rc-core then looks up decoded scancodes in `adstech_dvb_t_pci` and emits the associated input keycodes. Unload or rc-core teardown unregisters the map, after which new lookups by name should fail or fall back to another configured map.

## State and Persistence Behavior

The persistent state is the compiled static table plus the registry node in rc-core. The file does not allocate per-device memory, take locks, touch hardware, or persist user settings. Runtime key state, repeat filtering, protocol decoding, and user remaps live in rc-core, the receiver driver, and input/ir-keytable configuration rather than in this keymap source.

## Dependencies and Integration Points

The file depends on `media/rc-map.h`, `linux/module.h`, Linux input `KEY_*` definitions, the `RC_MAP_*` string namespace, and the protocol enum `RC_PROTO_UNKNOWN`. It is built through `drivers/media/rc/keymaps/Makefile` when `CONFIG_RC_MAP` is enabled, except for CEC-style integration if noted above. Board, USB, PCI, CEC, or platform IR drivers integrate with it by naming `RC_MAP_ADSTECH_DVB_T_PCI` as their default map.

## Risks and Edge Cases

Incorrect scancodes, wrong `KEY_*` assignments, a mismatched `.rc_proto`, or a stale `.name` break user-visible remote buttons without producing compile errors. Because the protocol is `RC_PROTO_UNKNOWN`, correctness depends on the consuming hardware driver or legacy decoder path supplying matching scancodes. Table ordering is not semantically important for lookups, but duplicate or vendor-overloaded scancodes should be reviewed carefully. The map can also drift from the v4l-utils userspace copy, causing different behavior between built-in maps and maps loaded from userspace.

## Test Signals

Useful checks include compiling the keymap with `CONFIG_RC_MAP=y` and `=m`, loading/unloading the generated module where applicable, confirming `rc_map_register()` exposes `RC_MAP_ADSTECH_DVB_T_PCI`, using `ir-keytable -r` or equivalent rc-core introspection to inspect the map, and pressing representative numeric, navigation, volume/channel, power, and media keys on the target remote. Protocol-specific tests should verify that decoded `RC_PROTO_UNKNOWN` scancodes match the table values and that unknown buttons do not alias to unsafe actions such as power or record.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-adstech-dvb-t-pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-alink-dtu-m.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-alink-dtu-m.c

## Purpose

`rc-alink-dtu-m.c` provides the `RC_MAP_ALINK_DTU_M` remote-controller keymap for `A-Link DTU(m) slim remote, 6 rows, 3 columns.`. It is a data-only rc-core map: decoded remote-control scan codes are translated into Linux input `KEY_*` events for the bundled receiver or board driver. The table has 18 scan-code entries; early entries include `0x0800->KEY_VOLUMEUP`, `0x0801->KEY_NUMERIC_1`, `0x0802->KEY_NUMERIC_3`, `0x0803->KEY_NUMERIC_7`, `0x0804->KEY_NUMERIC_9`, `0x0805->KEY_NEW`. The represented controls cover numeric entry, power/input selection, channel/volume.

## Important APIs, Types, and Functions

- `struct rc_map_table alink_dtu_m[]` is the static scan-code-to-keycode table.
- `struct rc_map_list alink_dtu_m_map` publishes `.scan = alink_dtu_m`, `.size = ARRAY_SIZE(alink_dtu_m)`, `.rc_proto = RC_PROTO_NEC`, and `.name = RC_MAP_ALINK_DTU_M` to rc-core.
- The module init function calls `rc_map_register()` and the exit function calls `rc_map_unregister()`, so the map is visible to rc-core only while the object is built in or the module is loaded.
- It has normal `module_init()`/`module_exit()` hooks.

## Control Flow

There is no active decode algorithm in this file. At build or module-load time, the map is registered with the rc-core map registry. A receiver driver later sets an `rc_dev->map_name` matching `RC_MAP_ALINK_DTU_M` or userspace selects that map with tooling such as `ir-keytable`; rc-core then looks up decoded scancodes in `alink_dtu_m` and emits the associated input keycodes. Unload or rc-core teardown unregisters the map, after which new lookups by name should fail or fall back to another configured map.

## State and Persistence Behavior

The persistent state is the compiled static table plus the registry node in rc-core. The file does not allocate per-device memory, take locks, touch hardware, or persist user settings. Runtime key state, repeat filtering, protocol decoding, and user remaps live in rc-core, the receiver driver, and input/ir-keytable configuration rather than in this keymap source.

## Dependencies and Integration Points

The file depends on `media/rc-map.h`, `linux/module.h`, Linux input `KEY_*` definitions, the `RC_MAP_*` string namespace, and the protocol enum `RC_PROTO_NEC`. It is built through `drivers/media/rc/keymaps/Makefile` when `CONFIG_RC_MAP` is enabled, except for CEC-style integration if noted above. Board, USB, PCI, CEC, or platform IR drivers integrate with it by naming `RC_MAP_ALINK_DTU_M` as their default map.

## Risks and Edge Cases

Incorrect scancodes, wrong `KEY_*` assignments, a mismatched `.rc_proto`, or a stale `.name` break user-visible remote buttons without producing compile errors. The declared protocol `RC_PROTO_NEC` tells rc-core which decoded scancode namespace this map expects. Table ordering is not semantically important for lookups, but duplicate or vendor-overloaded scancodes should be reviewed carefully. The map can also drift from the v4l-utils userspace copy, causing different behavior between built-in maps and maps loaded from userspace.

## Test Signals

Useful checks include compiling the keymap with `CONFIG_RC_MAP=y` and `=m`, loading/unloading the generated module where applicable, confirming `rc_map_register()` exposes `RC_MAP_ALINK_DTU_M`, using `ir-keytable -r` or equivalent rc-core introspection to inspect the map, and pressing representative numeric, navigation, volume/channel, power, and media keys on the target remote. Protocol-specific tests should verify that decoded `RC_PROTO_NEC` scancodes match the table values and that unknown buttons do not alias to unsafe actions such as power or record.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-alink-dtu-m.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-anysee.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-anysee.c

## Purpose

`rc-anysee.c` provides the `RC_MAP_ANYSEE` remote-controller keymap for `Anysee remote keytable`. It is a data-only rc-core map: decoded remote-control scan codes are translated into Linux input `KEY_*` events for the bundled receiver or board driver. The table has 44 scan-code entries; early entries include `0x0800->KEY_NUMERIC_0`, `0x0801->KEY_NUMERIC_1`, `0x0802->KEY_NUMERIC_2`, `0x0803->KEY_NUMERIC_3`, `0x0804->KEY_NUMERIC_4`, `0x0805->KEY_NUMERIC_5`. The represented controls cover numeric entry, power/input selection, navigation/menu, channel/volume, DVR/media transport, colored function keys, teletext/EPG/application keys.

## Important APIs, Types, and Functions

- `struct rc_map_table anysee[]` is the static scan-code-to-keycode table.
- `struct rc_map_list anysee_map` publishes `.scan = anysee`, `.size = ARRAY_SIZE(anysee)`, `.rc_proto = RC_PROTO_NEC`, and `.name = RC_MAP_ANYSEE` to rc-core.
- The module init function calls `rc_map_register()` and the exit function calls `rc_map_unregister()`, so the map is visible to rc-core only while the object is built in or the module is loaded.
- It has normal `module_init()`/`module_exit()` hooks.

## Control Flow

There is no active decode algorithm in this file. At build or module-load time, the map is registered with the rc-core map registry. A receiver driver later sets an `rc_dev->map_name` matching `RC_MAP_ANYSEE` or userspace selects that map with tooling such as `ir-keytable`; rc-core then looks up decoded scancodes in `anysee` and emits the associated input keycodes. Unload or rc-core teardown unregisters the map, after which new lookups by name should fail or fall back to another configured map.

## State and Persistence Behavior

The persistent state is the compiled static table plus the registry node in rc-core. The file does not allocate per-device memory, take locks, touch hardware, or persist user settings. Runtime key state, repeat filtering, protocol decoding, and user remaps live in rc-core, the receiver driver, and input/ir-keytable configuration rather than in this keymap source.

## Dependencies and Integration Points

The file depends on `media/rc-map.h`, `linux/module.h`, Linux input `KEY_*` definitions, the `RC_MAP_*` string namespace, and the protocol enum `RC_PROTO_NEC`. It is built through `drivers/media/rc/keymaps/Makefile` when `CONFIG_RC_MAP` is enabled, except for CEC-style integration if noted above. Board, USB, PCI, CEC, or platform IR drivers integrate with it by naming `RC_MAP_ANYSEE` as their default map.

## Risks and Edge Cases

Incorrect scancodes, wrong `KEY_*` assignments, a mismatched `.rc_proto`, or a stale `.name` break user-visible remote buttons without producing compile errors. The declared protocol `RC_PROTO_NEC` tells rc-core which decoded scancode namespace this map expects. Table ordering is not semantically important for lookups, but duplicate or vendor-overloaded scancodes should be reviewed carefully. The map can also drift from the v4l-utils userspace copy, causing different behavior between built-in maps and maps loaded from userspace.

## Test Signals

Useful checks include compiling the keymap with `CONFIG_RC_MAP=y` and `=m`, loading/unloading the generated module where applicable, confirming `rc_map_register()` exposes `RC_MAP_ANYSEE`, using `ir-keytable -r` or equivalent rc-core introspection to inspect the map, and pressing representative numeric, navigation, volume/channel, power, and media keys on the target remote. Protocol-specific tests should verify that decoded `RC_PROTO_NEC` scancodes match the table values and that unknown buttons do not alias to unsafe actions such as power or record.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-anysee.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-apac-viewcomp.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-apac-viewcomp.c

## Purpose

`rc-apac-viewcomp.c` provides the `RC_MAP_APAC_VIEWCOMP` remote-controller keymap for `apac-viewcomp remote controller keytable`. It is a data-only rc-core map: decoded remote-control scan codes are translated into Linux input `KEY_*` events for the bundled receiver or board driver. The table has 31 scan-code entries; early entries include `0x01->KEY_NUMERIC_1`, `0x02->KEY_NUMERIC_2`, `0x03->KEY_NUMERIC_3`, `0x04->KEY_NUMERIC_4`, `0x05->KEY_NUMERIC_5`, `0x06->KEY_NUMERIC_6`. The represented controls cover numeric entry, power/input selection, channel/volume, DVR/media transport, teletext/EPG/application keys.

## Important APIs, Types, and Functions

- `struct rc_map_table apac_viewcomp[]` is the static scan-code-to-keycode table.
- `struct rc_map_list apac_viewcomp_map` publishes `.scan = apac_viewcomp`, `.size = ARRAY_SIZE(apac_viewcomp)`, `.rc_proto = RC_PROTO_UNKNOWN`, and `.name = RC_MAP_APAC_VIEWCOMP` to rc-core.
- The module init function calls `rc_map_register()` and the exit function calls `rc_map_unregister()`, so the map is visible to rc-core only while the object is built in or the module is loaded.
- It has normal `module_init()`/`module_exit()` hooks.

## Control Flow

There is no active decode algorithm in this file. At build or module-load time, the map is registered with the rc-core map registry. A receiver driver later sets an `rc_dev->map_name` matching `RC_MAP_APAC_VIEWCOMP` or userspace selects that map with tooling such as `ir-keytable`; rc-core then looks up decoded scancodes in `apac_viewcomp` and emits the associated input keycodes. Unload or rc-core teardown unregisters the map, after which new lookups by name should fail or fall back to another configured map.

## State and Persistence Behavior

The persistent state is the compiled static table plus the registry node in rc-core. The file does not allocate per-device memory, take locks, touch hardware, or persist user settings. Runtime key state, repeat filtering, protocol decoding, and user remaps live in rc-core, the receiver driver, and input/ir-keytable configuration rather than in this keymap source.

## Dependencies and Integration Points

The file depends on `media/rc-map.h`, `linux/module.h`, Linux input `KEY_*` definitions, the `RC_MAP_*` string namespace, and the protocol enum `RC_PROTO_UNKNOWN`. It is built through `drivers/media/rc/keymaps/Makefile` when `CONFIG_RC_MAP` is enabled, except for CEC-style integration if noted above. Board, USB, PCI, CEC, or platform IR drivers integrate with it by naming `RC_MAP_APAC_VIEWCOMP` as their default map.

## Risks and Edge Cases

Incorrect scancodes, wrong `KEY_*` assignments, a mismatched `.rc_proto`, or a stale `.name` break user-visible remote buttons without producing compile errors. Because the protocol is `RC_PROTO_UNKNOWN`, correctness depends on the consuming hardware driver or legacy decoder path supplying matching scancodes. Table ordering is not semantically important for lookups, but duplicate or vendor-overloaded scancodes should be reviewed carefully. The map can also drift from the v4l-utils userspace copy, causing different behavior between built-in maps and maps loaded from userspace.

## Test Signals

Useful checks include compiling the keymap with `CONFIG_RC_MAP=y` and `=m`, loading/unloading the generated module where applicable, confirming `rc_map_register()` exposes `RC_MAP_APAC_VIEWCOMP`, using `ir-keytable -r` or equivalent rc-core introspection to inspect the map, and pressing representative numeric, navigation, volume/channel, power, and media keys on the target remote. Protocol-specific tests should verify that decoded `RC_PROTO_UNKNOWN` scancodes match the table values and that unknown buttons do not alias to unsafe actions such as power or record.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-apac-viewcomp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-astrometa-t2hybrid.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-astrometa-t2hybrid.c

## Purpose

`rc-astrometa-t2hybrid.c` provides the `RC_MAP_ASTROMETA_T2HYBRID` remote-controller keymap for `Astrometa T2hybrid remote controller keytable`. It is a data-only rc-core map: decoded remote-control scan codes are translated into Linux input `KEY_*` events for the bundled receiver or board driver. The table has 21 scan-code entries; early entries include `0x4d->KEY_POWER2`, `0x54->KEY_VIDEO`, `0x16->KEY_MUTE`, `0x4c->KEY_RECORD`, `0x05->KEY_CHANNELUP`, `0x0c->KEY_TIME`. The represented controls cover numeric entry, power/input selection, channel/volume, DVR/media transport.

## Important APIs, Types, and Functions

- `struct rc_map_table t2hybrid[]` is the static scan-code-to-keycode table.
- `struct rc_map_list t2hybrid_map` publishes `.scan = t2hybrid`, `.size = ARRAY_SIZE(t2hybrid)`, `.rc_proto = RC_PROTO_NEC`, and `.name = RC_MAP_ASTROMETA_T2HYBRID` to rc-core.
- The module init function calls `rc_map_register()` and the exit function calls `rc_map_unregister()`, so the map is visible to rc-core only while the object is built in or the module is loaded.
- It has normal `module_init()`/`module_exit()` hooks.

## Control Flow

There is no active decode algorithm in this file. At build or module-load time, the map is registered with the rc-core map registry. A receiver driver later sets an `rc_dev->map_name` matching `RC_MAP_ASTROMETA_T2HYBRID` or userspace selects that map with tooling such as `ir-keytable`; rc-core then looks up decoded scancodes in `t2hybrid` and emits the associated input keycodes. Unload or rc-core teardown unregisters the map, after which new lookups by name should fail or fall back to another configured map.

## State and Persistence Behavior

The persistent state is the compiled static table plus the registry node in rc-core. The file does not allocate per-device memory, take locks, touch hardware, or persist user settings. Runtime key state, repeat filtering, protocol decoding, and user remaps live in rc-core, the receiver driver, and input/ir-keytable configuration rather than in this keymap source.

## Dependencies and Integration Points

The file depends on `media/rc-map.h`, `linux/module.h`, Linux input `KEY_*` definitions, the `RC_MAP_*` string namespace, and the protocol enum `RC_PROTO_NEC`. It is built through `drivers/media/rc/keymaps/Makefile` when `CONFIG_RC_MAP` is enabled, except for CEC-style integration if noted above. Board, USB, PCI, CEC, or platform IR drivers integrate with it by naming `RC_MAP_ASTROMETA_T2HYBRID` as their default map.

## Risks and Edge Cases

Incorrect scancodes, wrong `KEY_*` assignments, a mismatched `.rc_proto`, or a stale `.name` break user-visible remote buttons without producing compile errors. The declared protocol `RC_PROTO_NEC` tells rc-core which decoded scancode namespace this map expects. Table ordering is not semantically important for lookups, but duplicate or vendor-overloaded scancodes should be reviewed carefully. The map can also drift from the v4l-utils userspace copy, causing different behavior between built-in maps and maps loaded from userspace.

## Test Signals

Useful checks include compiling the keymap with `CONFIG_RC_MAP=y` and `=m`, loading/unloading the generated module where applicable, confirming `rc_map_register()` exposes `RC_MAP_ASTROMETA_T2HYBRID`, using `ir-keytable -r` or equivalent rc-core introspection to inspect the map, and pressing representative numeric, navigation, volume/channel, power, and media keys on the target remote. Protocol-specific tests should verify that decoded `RC_PROTO_NEC` scancodes match the table values and that unknown buttons do not alias to unsafe actions such as power or record.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-astrometa-t2hybrid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-asus-pc39.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-asus-pc39.c

## Purpose

`rc-asus-pc39.c` provides the `RC_MAP_ASUS_PC39` remote-controller keymap for `Model PC-39 keytable for asus-pc39 remote controller`. It is a data-only rc-core map: decoded remote-control scan codes are translated into Linux input `KEY_*` events for the bundled receiver or board driver. The table has 39 scan-code entries; early entries include `0x082a->KEY_NUMERIC_0`, `0x0816->KEY_NUMERIC_1`, `0x0812->KEY_NUMERIC_2`, `0x0814->KEY_NUMERIC_3`, `0x0836->KEY_NUMERIC_4`, `0x0832->KEY_NUMERIC_5`. The represented controls cover numeric entry, power/input selection, navigation/menu, channel/volume, DVR/media transport.

## Important APIs, Types, and Functions

- `struct rc_map_table asus_pc39[]` is the static scan-code-to-keycode table.
- `struct rc_map_list asus_pc39_map` publishes `.scan = asus_pc39`, `.size = ARRAY_SIZE(asus_pc39)`, `.rc_proto = RC_PROTO_RC5`, and `.name = RC_MAP_ASUS_PC39` to rc-core.
- The module init function calls `rc_map_register()` and the exit function calls `rc_map_unregister()`, so the map is visible to rc-core only while the object is built in or the module is loaded.
- It has normal `module_init()`/`module_exit()` hooks.

## Control Flow

There is no active decode algorithm in this file. At build or module-load time, the map is registered with the rc-core map registry. A receiver driver later sets an `rc_dev->map_name` matching `RC_MAP_ASUS_PC39` or userspace selects that map with tooling such as `ir-keytable`; rc-core then looks up decoded scancodes in `asus_pc39` and emits the associated input keycodes. Unload or rc-core teardown unregisters the map, after which new lookups by name should fail or fall back to another configured map.

## State and Persistence Behavior

The persistent state is the compiled static table plus the registry node in rc-core. The file does not allocate per-device memory, take locks, touch hardware, or persist user settings. Runtime key state, repeat filtering, protocol decoding, and user remaps live in rc-core, the receiver driver, and input/ir-keytable configuration rather than in this keymap source.

## Dependencies and Integration Points

The file depends on `media/rc-map.h`, `linux/module.h`, Linux input `KEY_*` definitions, the `RC_MAP_*` string namespace, and the protocol enum `RC_PROTO_RC5`. It is built through `drivers/media/rc/keymaps/Makefile` when `CONFIG_RC_MAP` is enabled, except for CEC-style integration if noted above. Board, USB, PCI, CEC, or platform IR drivers integrate with it by naming `RC_MAP_ASUS_PC39` as their default map.

## Risks and Edge Cases

Incorrect scancodes, wrong `KEY_*` assignments, a mismatched `.rc_proto`, or a stale `.name` break user-visible remote buttons without producing compile errors. The declared protocol `RC_PROTO_RC5` tells rc-core which decoded scancode namespace this map expects. Table ordering is not semantically important for lookups, but duplicate or vendor-overloaded scancodes should be reviewed carefully. The map can also drift from the v4l-utils userspace copy, causing different behavior between built-in maps and maps loaded from userspace.

## Test Signals

Useful checks include compiling the keymap with `CONFIG_RC_MAP=y` and `=m`, loading/unloading the generated module where applicable, confirming `rc_map_register()` exposes `RC_MAP_ASUS_PC39`, using `ir-keytable -r` or equivalent rc-core introspection to inspect the map, and pressing representative numeric, navigation, volume/channel, power, and media keys on the target remote. Protocol-specific tests should verify that decoded `RC_PROTO_RC5` scancodes match the table values and that unknown buttons do not alias to unsafe actions such as power or record.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-asus-pc39.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-asus-ps3-100.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-asus-ps3-100.c

## Purpose

`rc-asus-ps3-100.c` provides the `RC_MAP_ASUS_PS3_100` remote-controller keymap for `Asus My Cinema PS3-100 remote controller keytable`. It is a data-only rc-core map: decoded remote-control scan codes are translated into Linux input `KEY_*` events for the bundled receiver or board driver. The table has 41 scan-code entries; early entries include `0x081c->KEY_HOME`, `0x081e->KEY_TV`, `0x0803->KEY_TEXT`, `0x0829->KEY_POWER`, `0x080b->KEY_RED`, `0x080d->KEY_YELLOW`. The represented controls cover numeric entry, power/input selection, navigation/menu, channel/volume, DVR/media transport, colored function keys, teletext/EPG/application keys.

## Important APIs, Types, and Functions

- `struct rc_map_table asus_ps3_100[]` is the static scan-code-to-keycode table.
- `struct rc_map_list asus_ps3_100_map` publishes `.scan = asus_ps3_100`, `.size = ARRAY_SIZE(asus_ps3_100)`, `.rc_proto = RC_PROTO_RC5`, and `.name = RC_MAP_ASUS_PS3_100` to rc-core.
- The module init function calls `rc_map_register()` and the exit function calls `rc_map_unregister()`, so the map is visible to rc-core only while the object is built in or the module is loaded.
- It has normal `module_init()`/`module_exit()` hooks.

## Control Flow

There is no active decode algorithm in this file. At build or module-load time, the map is registered with the rc-core map registry. A receiver driver later sets an `rc_dev->map_name` matching `RC_MAP_ASUS_PS3_100` or userspace selects that map with tooling such as `ir-keytable`; rc-core then looks up decoded scancodes in `asus_ps3_100` and emits the associated input keycodes. Unload or rc-core teardown unregisters the map, after which new lookups by name should fail or fall back to another configured map.

## State and Persistence Behavior

The persistent state is the compiled static table plus the registry node in rc-core. The file does not allocate per-device memory, take locks, touch hardware, or persist user settings. Runtime key state, repeat filtering, protocol decoding, and user remaps live in rc-core, the receiver driver, and input/ir-keytable configuration rather than in this keymap source.

## Dependencies and Integration Points

The file depends on `media/rc-map.h`, `linux/module.h`, Linux input `KEY_*` definitions, the `RC_MAP_*` string namespace, and the protocol enum `RC_PROTO_RC5`. It is built through `drivers/media/rc/keymaps/Makefile` when `CONFIG_RC_MAP` is enabled, except for CEC-style integration if noted above. Board, USB, PCI, CEC, or platform IR drivers integrate with it by naming `RC_MAP_ASUS_PS3_100` as their default map.

## Risks and Edge Cases

Incorrect scancodes, wrong `KEY_*` assignments, a mismatched `.rc_proto`, or a stale `.name` break user-visible remote buttons without producing compile errors. The declared protocol `RC_PROTO_RC5` tells rc-core which decoded scancode namespace this map expects. Table ordering is not semantically important for lookups, but duplicate or vendor-overloaded scancodes should be reviewed carefully. The map can also drift from the v4l-utils userspace copy, causing different behavior between built-in maps and maps loaded from userspace.

## Test Signals

Useful checks include compiling the keymap with `CONFIG_RC_MAP=y` and `=m`, loading/unloading the generated module where applicable, confirming `rc_map_register()` exposes `RC_MAP_ASUS_PS3_100`, using `ir-keytable -r` or equivalent rc-core introspection to inspect the map, and pressing representative numeric, navigation, volume/channel, power, and media keys on the target remote. Protocol-specific tests should verify that decoded `RC_PROTO_RC5` scancodes match the table values and that unknown buttons do not alias to unsafe actions such as power or record.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-asus-ps3-100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-ati-tv-wonder-hd-600.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-ati-tv-wonder-hd-600.c

## Purpose

`rc-ati-tv-wonder-hd-600.c` provides the `RC_MAP_ATI_TV_WONDER_HD_600` remote-controller keymap for `ati-tv-wonder-hd-600 remote controller keytable`. It is a data-only rc-core map: decoded remote-control scan codes are translated into Linux input `KEY_*` events for the bundled receiver or board driver. The table has 24 scan-code entries; early entries include `0x00->KEY_RECORD`, `0x01->KEY_PLAYPAUSE`, `0x02->KEY_STOP`, `0x03->KEY_POWER`, `0x04->KEY_PREVIOUS`, `0x05->KEY_REWIND`. The represented controls cover power/input selection, navigation/menu, channel/volume, DVR/media transport, teletext/EPG/application keys.

## Important APIs, Types, and Functions

- `struct rc_map_table ati_tv_wonder_hd_600[]` is the static scan-code-to-keycode table.
- `struct rc_map_list ati_tv_wonder_hd_600_map` publishes `.scan = ati_tv_wonder_hd_600`, `.size = ARRAY_SIZE(ati_tv_wonder_hd_600)`, `.rc_proto = RC_PROTO_UNKNOWN`, and `.name = RC_MAP_ATI_TV_WONDER_HD_600` to rc-core.
- The module init function calls `rc_map_register()` and the exit function calls `rc_map_unregister()`, so the map is visible to rc-core only while the object is built in or the module is loaded.
- It has normal `module_init()`/`module_exit()` hooks.

## Control Flow

There is no active decode algorithm in this file. At build or module-load time, the map is registered with the rc-core map registry. A receiver driver later sets an `rc_dev->map_name` matching `RC_MAP_ATI_TV_WONDER_HD_600` or userspace selects that map with tooling such as `ir-keytable`; rc-core then looks up decoded scancodes in `ati_tv_wonder_hd_600` and emits the associated input keycodes. Unload or rc-core teardown unregisters the map, after which new lookups by name should fail or fall back to another configured map.

## State and Persistence Behavior

The persistent state is the compiled static table plus the registry node in rc-core. The file does not allocate per-device memory, take locks, touch hardware, or persist user settings. Runtime key state, repeat filtering, protocol decoding, and user remaps live in rc-core, the receiver driver, and input/ir-keytable configuration rather than in this keymap source.

## Dependencies and Integration Points

The file depends on `media/rc-map.h`, `linux/module.h`, Linux input `KEY_*` definitions, the `RC_MAP_*` string namespace, and the protocol enum `RC_PROTO_UNKNOWN`. It is built through `drivers/media/rc/keymaps/Makefile` when `CONFIG_RC_MAP` is enabled, except for CEC-style integration if noted above. Board, USB, PCI, CEC, or platform IR drivers integrate with it by naming `RC_MAP_ATI_TV_WONDER_HD_600` as their default map.

## Risks and Edge Cases

Incorrect scancodes, wrong `KEY_*` assignments, a mismatched `.rc_proto`, or a stale `.name` break user-visible remote buttons without producing compile errors. Because the protocol is `RC_PROTO_UNKNOWN`, correctness depends on the consuming hardware driver or legacy decoder path supplying matching scancodes. Table ordering is not semantically important for lookups, but duplicate or vendor-overloaded scancodes should be reviewed carefully. The map can also drift from the v4l-utils userspace copy, causing different behavior between built-in maps and maps loaded from userspace.

## Test Signals

Useful checks include compiling the keymap with `CONFIG_RC_MAP=y` and `=m`, loading/unloading the generated module where applicable, confirming `rc_map_register()` exposes `RC_MAP_ATI_TV_WONDER_HD_600`, using `ir-keytable -r` or equivalent rc-core introspection to inspect the map, and pressing representative numeric, navigation, volume/channel, power, and media keys on the target remote. Protocol-specific tests should verify that decoded `RC_PROTO_UNKNOWN` scancodes match the table values and that unknown buttons do not alias to unsafe actions such as power or record.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-ati-tv-wonder-hd-600.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-ati-x10.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-ati-x10.c

## Purpose

`rc-ati-x10.c` provides the `RC_MAP_ATI_X10` remote-controller keymap for `ATI X10 RF remote controller keytable`. It is a data-only rc-core map: decoded remote-control scan codes are translated into Linux input `KEY_*` events for the bundled receiver or board driver. The table has 48 scan-code entries; early entries include `0x00->KEY_A`, `0x01->KEY_B`, `0x02->KEY_POWER`, `0x03->KEY_TV`, `0x04->KEY_DVD`, `0x05->KEY_WWW`. The represented controls cover numeric entry, power/input selection, navigation/menu, channel/volume, DVR/media transport, teletext/EPG/application keys.

## Important APIs, Types, and Functions

- `struct rc_map_table ati_x10[]` is the static scan-code-to-keycode table.
- `struct rc_map_list ati_x10_map` publishes `.scan = ati_x10`, `.size = ARRAY_SIZE(ati_x10)`, `.rc_proto = RC_PROTO_OTHER`, and `.name = RC_MAP_ATI_X10` to rc-core.
- The module init function calls `rc_map_register()` and the exit function calls `rc_map_unregister()`, so the map is visible to rc-core only while the object is built in or the module is loaded.
- It has normal `module_init()`/`module_exit()` hooks.

## Control Flow

There is no active decode algorithm in this file. At build or module-load time, the map is registered with the rc-core map registry. A receiver driver later sets an `rc_dev->map_name` matching `RC_MAP_ATI_X10` or userspace selects that map with tooling such as `ir-keytable`; rc-core then looks up decoded scancodes in `ati_x10` and emits the associated input keycodes. Unload or rc-core teardown unregisters the map, after which new lookups by name should fail or fall back to another configured map.

## State and Persistence Behavior

The persistent state is the compiled static table plus the registry node in rc-core. The file does not allocate per-device memory, take locks, touch hardware, or persist user settings. Runtime key state, repeat filtering, protocol decoding, and user remaps live in rc-core, the receiver driver, and input/ir-keytable configuration rather than in this keymap source.

## Dependencies and Integration Points

The file depends on `media/rc-map.h`, `linux/module.h`, Linux input `KEY_*` definitions, the `RC_MAP_*` string namespace, and the protocol enum `RC_PROTO_OTHER`. It is built through `drivers/media/rc/keymaps/Makefile` when `CONFIG_RC_MAP` is enabled, except for CEC-style integration if noted above. Board, USB, PCI, CEC, or platform IR drivers integrate with it by naming `RC_MAP_ATI_X10` as their default map.

## Risks and Edge Cases

Incorrect scancodes, wrong `KEY_*` assignments, a mismatched `.rc_proto`, or a stale `.name` break user-visible remote buttons without producing compile errors. `RC_PROTO_OTHER` marks a non-standard transport, so consumers should treat scancode shape as device-specific rather than decoded NEC/RC5/etc. Table ordering is not semantically important for lookups, but duplicate or vendor-overloaded scancodes should be reviewed carefully. The map can also drift from the v4l-utils userspace copy, causing different behavior between built-in maps and maps loaded from userspace.

## Test Signals

Useful checks include compiling the keymap with `CONFIG_RC_MAP=y` and `=m`, loading/unloading the generated module where applicable, confirming `rc_map_register()` exposes `RC_MAP_ATI_X10`, using `ir-keytable -r` or equivalent rc-core introspection to inspect the map, and pressing representative numeric, navigation, volume/channel, power, and media keys on the target remote. Protocol-specific tests should verify that decoded `RC_PROTO_OTHER` scancodes match the table values and that unknown buttons do not alias to unsafe actions such as power or record.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-ati-x10.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-avermedia-a16d.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-avermedia-a16d.c

## Purpose

`rc-avermedia-a16d.c` provides the `RC_MAP_AVERMEDIA_A16D` remote-controller keymap for `avermedia-a16d remote controller keytable`. It is a data-only rc-core map: decoded remote-control scan codes are translated into Linux input `KEY_*` events for the bundled receiver or board driver. The table has 34 scan-code entries; early entries include `0x20->KEY_LIST`, `0x00->KEY_POWER`, `0x28->KEY_NUMERIC_1`, `0x18->KEY_NUMERIC_2`, `0x38->KEY_NUMERIC_3`, `0x24->KEY_NUMERIC_4`. The represented controls cover numeric entry, power/input selection, navigation/menu, channel/volume, DVR/media transport, colored function keys, teletext/EPG/application keys.

## Important APIs, Types, and Functions

- `struct rc_map_table avermedia_a16d[]` is the static scan-code-to-keycode table.
- `struct rc_map_list avermedia_a16d_map` publishes `.scan = avermedia_a16d`, `.size = ARRAY_SIZE(avermedia_a16d)`, `.rc_proto = RC_PROTO_UNKNOWN`, and `.name = RC_MAP_AVERMEDIA_A16D` to rc-core.
- The module init function calls `rc_map_register()` and the exit function calls `rc_map_unregister()`, so the map is visible to rc-core only while the object is built in or the module is loaded.
- It has normal `module_init()`/`module_exit()` hooks.

## Control Flow

There is no active decode algorithm in this file. At build or module-load time, the map is registered with the rc-core map registry. A receiver driver later sets an `rc_dev->map_name` matching `RC_MAP_AVERMEDIA_A16D` or userspace selects that map with tooling such as `ir-keytable`; rc-core then looks up decoded scancodes in `avermedia_a16d` and emits the associated input keycodes. Unload or rc-core teardown unregisters the map, after which new lookups by name should fail or fall back to another configured map.

## State and Persistence Behavior

The persistent state is the compiled static table plus the registry node in rc-core. The file does not allocate per-device memory, take locks, touch hardware, or persist user settings. Runtime key state, repeat filtering, protocol decoding, and user remaps live in rc-core, the receiver driver, and input/ir-keytable configuration rather than in this keymap source.

## Dependencies and Integration Points

The file depends on `media/rc-map.h`, `linux/module.h`, Linux input `KEY_*` definitions, the `RC_MAP_*` string namespace, and the protocol enum `RC_PROTO_UNKNOWN`. It is built through `drivers/media/rc/keymaps/Makefile` when `CONFIG_RC_MAP` is enabled, except for CEC-style integration if noted above. Board, USB, PCI, CEC, or platform IR drivers integrate with it by naming `RC_MAP_AVERMEDIA_A16D` as their default map.

## Risks and Edge Cases

Incorrect scancodes, wrong `KEY_*` assignments, a mismatched `.rc_proto`, or a stale `.name` break user-visible remote buttons without producing compile errors. Because the protocol is `RC_PROTO_UNKNOWN`, correctness depends on the consuming hardware driver or legacy decoder path supplying matching scancodes. Table ordering is not semantically important for lookups, but duplicate or vendor-overloaded scancodes should be reviewed carefully. The map can also drift from the v4l-utils userspace copy, causing different behavior between built-in maps and maps loaded from userspace.

## Test Signals

Useful checks include compiling the keymap with `CONFIG_RC_MAP=y` and `=m`, loading/unloading the generated module where applicable, confirming `rc_map_register()` exposes `RC_MAP_AVERMEDIA_A16D`, using `ir-keytable -r` or equivalent rc-core introspection to inspect the map, and pressing representative numeric, navigation, volume/channel, power, and media keys on the target remote. Protocol-specific tests should verify that decoded `RC_PROTO_UNKNOWN` scancodes match the table values and that unknown buttons do not alias to unsafe actions such as power or record.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-avermedia-a16d.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-avermedia-cardbus.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-avermedia-cardbus.c

## Purpose

`rc-avermedia-cardbus.c` provides the `RC_MAP_AVERMEDIA_CARDBUS` remote-controller keymap for `avermedia-cardbus remote controller keytable`. It is a data-only rc-core map: decoded remote-control scan codes are translated into Linux input `KEY_*` events for the bundled receiver or board driver. The table has 54 scan-code entries; early entries include `0x00->KEY_POWER`, `0x01->KEY_TUNER`, `0x03->KEY_TEXT`, `0x04->KEY_EPG`, `0x05->KEY_NUMERIC_1`, `0x06->KEY_NUMERIC_2`. The represented controls cover numeric entry, power/input selection, navigation/menu, channel/volume, DVR/media transport, colored function keys, teletext/EPG/application keys.

## Important APIs, Types, and Functions

- `struct rc_map_table avermedia_cardbus[]` is the static scan-code-to-keycode table.
- `struct rc_map_list avermedia_cardbus_map` publishes `.scan = avermedia_cardbus`, `.size = ARRAY_SIZE(avermedia_cardbus)`, `.rc_proto = RC_PROTO_UNKNOWN`, and `.name = RC_MAP_AVERMEDIA_CARDBUS` to rc-core.
- The module init function calls `rc_map_register()` and the exit function calls `rc_map_unregister()`, so the map is visible to rc-core only while the object is built in or the module is loaded.
- It has normal `module_init()`/`module_exit()` hooks.

## Control Flow

There is no active decode algorithm in this file. At build or module-load time, the map is registered with the rc-core map registry. A receiver driver later sets an `rc_dev->map_name` matching `RC_MAP_AVERMEDIA_CARDBUS` or userspace selects that map with tooling such as `ir-keytable`; rc-core then looks up decoded scancodes in `avermedia_cardbus` and emits the associated input keycodes. Unload or rc-core teardown unregisters the map, after which new lookups by name should fail or fall back to another configured map.

## State and Persistence Behavior

The persistent state is the compiled static table plus the registry node in rc-core. The file does not allocate per-device memory, take locks, touch hardware, or persist user settings. Runtime key state, repeat filtering, protocol decoding, and user remaps live in rc-core, the receiver driver, and input/ir-keytable configuration rather than in this keymap source.

## Dependencies and Integration Points

The file depends on `media/rc-map.h`, `linux/module.h`, Linux input `KEY_*` definitions, the `RC_MAP_*` string namespace, and the protocol enum `RC_PROTO_UNKNOWN`. It is built through `drivers/media/rc/keymaps/Makefile` when `CONFIG_RC_MAP` is enabled, except for CEC-style integration if noted above. Board, USB, PCI, CEC, or platform IR drivers integrate with it by naming `RC_MAP_AVERMEDIA_CARDBUS` as their default map.

## Risks and Edge Cases

Incorrect scancodes, wrong `KEY_*` assignments, a mismatched `.rc_proto`, or a stale `.name` break user-visible remote buttons without producing compile errors. Because the protocol is `RC_PROTO_UNKNOWN`, correctness depends on the consuming hardware driver or legacy decoder path supplying matching scancodes. Table ordering is not semantically important for lookups, but duplicate or vendor-overloaded scancodes should be reviewed carefully. The map can also drift from the v4l-utils userspace copy, causing different behavior between built-in maps and maps loaded from userspace.

## Test Signals

Useful checks include compiling the keymap with `CONFIG_RC_MAP=y` and `=m`, loading/unloading the generated module where applicable, confirming `rc_map_register()` exposes `RC_MAP_AVERMEDIA_CARDBUS`, using `ir-keytable -r` or equivalent rc-core introspection to inspect the map, and pressing representative numeric, navigation, volume/channel, power, and media keys on the target remote. Protocol-specific tests should verify that decoded `RC_PROTO_UNKNOWN` scancodes match the table values and that unknown buttons do not alias to unsafe actions such as power or record.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-avermedia-cardbus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-avermedia-dvbt.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-avermedia-dvbt.c

## Purpose

`rc-avermedia-dvbt.c` provides the `RC_MAP_AVERMEDIA_DVBT` remote-controller keymap for `avermedia-dvbt remote controller keytable`. It is a data-only rc-core map: decoded remote-control scan codes are translated into Linux input `KEY_*` events for the bundled receiver or board driver. The table has 34 scan-code entries; early entries include `0x28->KEY_NUMERIC_0`, `0x22->KEY_NUMERIC_1`, `0x12->KEY_NUMERIC_2`, `0x32->KEY_NUMERIC_3`, `0x24->KEY_NUMERIC_4`, `0x14->KEY_NUMERIC_5`. The represented controls cover numeric entry, power/input selection, channel/volume, DVR/media transport, colored function keys, teletext/EPG/application keys.

## Important APIs, Types, and Functions

- `struct rc_map_table avermedia_dvbt[]` is the static scan-code-to-keycode table.
- `struct rc_map_list avermedia_dvbt_map` publishes `.scan = avermedia_dvbt`, `.size = ARRAY_SIZE(avermedia_dvbt)`, `.rc_proto = RC_PROTO_UNKNOWN`, and `.name = RC_MAP_AVERMEDIA_DVBT` to rc-core.
- The module init function calls `rc_map_register()` and the exit function calls `rc_map_unregister()`, so the map is visible to rc-core only while the object is built in or the module is loaded.
- It has normal `module_init()`/`module_exit()` hooks.

## Control Flow

There is no active decode algorithm in this file. At build or module-load time, the map is registered with the rc-core map registry. A receiver driver later sets an `rc_dev->map_name` matching `RC_MAP_AVERMEDIA_DVBT` or userspace selects that map with tooling such as `ir-keytable`; rc-core then looks up decoded scancodes in `avermedia_dvbt` and emits the associated input keycodes. Unload or rc-core teardown unregisters the map, after which new lookups by name should fail or fall back to another configured map.

## State and Persistence Behavior

The persistent state is the compiled static table plus the registry node in rc-core. The file does not allocate per-device memory, take locks, touch hardware, or persist user settings. Runtime key state, repeat filtering, protocol decoding, and user remaps live in rc-core, the receiver driver, and input/ir-keytable configuration rather than in this keymap source.

## Dependencies and Integration Points

The file depends on `media/rc-map.h`, `linux/module.h`, Linux input `KEY_*` definitions, the `RC_MAP_*` string namespace, and the protocol enum `RC_PROTO_UNKNOWN`. It is built through `drivers/media/rc/keymaps/Makefile` when `CONFIG_RC_MAP` is enabled, except for CEC-style integration if noted above. Board, USB, PCI, CEC, or platform IR drivers integrate with it by naming `RC_MAP_AVERMEDIA_DVBT` as their default map.

## Risks and Edge Cases

Incorrect scancodes, wrong `KEY_*` assignments, a mismatched `.rc_proto`, or a stale `.name` break user-visible remote buttons without producing compile errors. Because the protocol is `RC_PROTO_UNKNOWN`, correctness depends on the consuming hardware driver or legacy decoder path supplying matching scancodes. Table ordering is not semantically important for lookups, but duplicate or vendor-overloaded scancodes should be reviewed carefully. The map can also drift from the v4l-utils userspace copy, causing different behavior between built-in maps and maps loaded from userspace.

## Test Signals

Useful checks include compiling the keymap with `CONFIG_RC_MAP=y` and `=m`, loading/unloading the generated module where applicable, confirming `rc_map_register()` exposes `RC_MAP_AVERMEDIA_DVBT`, using `ir-keytable -r` or equivalent rc-core introspection to inspect the map, and pressing representative numeric, navigation, volume/channel, power, and media keys on the target remote. Protocol-specific tests should verify that decoded `RC_PROTO_UNKNOWN` scancodes match the table values and that unknown buttons do not alias to unsafe actions such as power or record.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-avermedia-dvbt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-avermedia-m135a.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-avermedia-m135a.c

## Purpose

`rc-avermedia-m135a.c` provides the `RC_MAP_AVERMEDIA_M135A` remote-controller keymap for `Avermedia M135A with RM-JX and RM-K6 remote controller keytable`. It is a data-only rc-core map: decoded remote-control scan codes are translated into Linux input `KEY_*` events for the bundled receiver or board driver. The table has 80 scan-code entries; early entries include `0x0200->KEY_POWER2`, `0x022e->KEY_DOT`, `0x0201->KEY_MODE`, `0x0205->KEY_NUMERIC_1`, `0x0206->KEY_NUMERIC_2`, `0x0207->KEY_NUMERIC_3`. The represented controls cover numeric entry, power/input selection, navigation/menu, channel/volume, DVR/media transport, colored function keys, teletext/EPG/application keys.

## Important APIs, Types, and Functions

- `struct rc_map_table avermedia_m135a[]` is the static scan-code-to-keycode table.
- `struct rc_map_list avermedia_m135a_map` publishes `.scan = avermedia_m135a`, `.size = ARRAY_SIZE(avermedia_m135a)`, `.rc_proto = RC_PROTO_NEC`, and `.name = RC_MAP_AVERMEDIA_M135A` to rc-core.
- The module init function calls `rc_map_register()` and the exit function calls `rc_map_unregister()`, so the map is visible to rc-core only while the object is built in or the module is loaded.
- It has normal `module_init()`/`module_exit()` hooks.

## Control Flow

There is no active decode algorithm in this file. At build or module-load time, the map is registered with the rc-core map registry. A receiver driver later sets an `rc_dev->map_name` matching `RC_MAP_AVERMEDIA_M135A` or userspace selects that map with tooling such as `ir-keytable`; rc-core then looks up decoded scancodes in `avermedia_m135a` and emits the associated input keycodes. Unload or rc-core teardown unregisters the map, after which new lookups by name should fail or fall back to another configured map.

## State and Persistence Behavior

The persistent state is the compiled static table plus the registry node in rc-core. The file does not allocate per-device memory, take locks, touch hardware, or persist user settings. Runtime key state, repeat filtering, protocol decoding, and user remaps live in rc-core, the receiver driver, and input/ir-keytable configuration rather than in this keymap source.

## Dependencies and Integration Points

The file depends on `media/rc-map.h`, `linux/module.h`, Linux input `KEY_*` definitions, the `RC_MAP_*` string namespace, and the protocol enum `RC_PROTO_NEC`. It is built through `drivers/media/rc/keymaps/Makefile` when `CONFIG_RC_MAP` is enabled, except for CEC-style integration if noted above. Board, USB, PCI, CEC, or platform IR drivers integrate with it by naming `RC_MAP_AVERMEDIA_M135A` as their default map.

## Risks and Edge Cases

Incorrect scancodes, wrong `KEY_*` assignments, a mismatched `.rc_proto`, or a stale `.name` break user-visible remote buttons without producing compile errors. The declared protocol `RC_PROTO_NEC` tells rc-core which decoded scancode namespace this map expects. Table ordering is not semantically important for lookups, but duplicate or vendor-overloaded scancodes should be reviewed carefully. The map can also drift from the v4l-utils userspace copy, causing different behavior between built-in maps and maps loaded from userspace.

## Test Signals

Useful checks include compiling the keymap with `CONFIG_RC_MAP=y` and `=m`, loading/unloading the generated module where applicable, confirming `rc_map_register()` exposes `RC_MAP_AVERMEDIA_M135A`, using `ir-keytable -r` or equivalent rc-core introspection to inspect the map, and pressing representative numeric, navigation, volume/channel, power, and media keys on the target remote. Protocol-specific tests should verify that decoded `RC_PROTO_NEC` scancodes match the table values and that unknown buttons do not alias to unsafe actions such as power or record.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-avermedia-m135a.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-avermedia-m733a-rm-k6.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-avermedia-m733a-rm-k6.c

## Purpose

`rc-avermedia-m733a-rm-k6.c` provides the `RC_MAP_AVERMEDIA_M733A_RM_K6` remote-controller keymap for `Avermedia M733A with IR model RM-K6 remote controller keytable`. It is a data-only rc-core map: decoded remote-control scan codes are translated into Linux input `KEY_*` events for the bundled receiver or board driver. The table has 44 scan-code entries; early entries include `0x0401->KEY_POWER2`, `0x0406->KEY_MUTE`, `0x0408->KEY_MODE`, `0x0409->KEY_NUMERIC_1`, `0x040a->KEY_NUMERIC_2`, `0x040b->KEY_NUMERIC_3`. The represented controls cover numeric entry, power/input selection, navigation/menu, channel/volume, DVR/media transport, colored function keys, teletext/EPG/application keys.

## Important APIs, Types, and Functions

- `struct rc_map_table avermedia_m733a_rm_k6[]` is the static scan-code-to-keycode table.
- `struct rc_map_list avermedia_m733a_rm_k6_map` publishes `.scan = avermedia_m733a_rm_k6`, `.size = ARRAY_SIZE(avermedia_m733a_rm_k6)`, `.rc_proto = RC_PROTO_NEC`, and `.name = RC_MAP_AVERMEDIA_M733A_RM_K6` to rc-core.
- The module init function calls `rc_map_register()` and the exit function calls `rc_map_unregister()`, so the map is visible to rc-core only while the object is built in or the module is loaded.
- It has normal `module_init()`/`module_exit()` hooks.

## Control Flow

There is no active decode algorithm in this file. At build or module-load time, the map is registered with the rc-core map registry. A receiver driver later sets an `rc_dev->map_name` matching `RC_MAP_AVERMEDIA_M733A_RM_K6` or userspace selects that map with tooling such as `ir-keytable`; rc-core then looks up decoded scancodes in `avermedia_m733a_rm_k6` and emits the associated input keycodes. Unload or rc-core teardown unregisters the map, after which new lookups by name should fail or fall back to another configured map.

## State and Persistence Behavior

The persistent state is the compiled static table plus the registry node in rc-core. The file does not allocate per-device memory, take locks, touch hardware, or persist user settings. Runtime key state, repeat filtering, protocol decoding, and user remaps live in rc-core, the receiver driver, and input/ir-keytable configuration rather than in this keymap source.

## Dependencies and Integration Points

The file depends on `media/rc-map.h`, `linux/module.h`, Linux input `KEY_*` definitions, the `RC_MAP_*` string namespace, and the protocol enum `RC_PROTO_NEC`. It is built through `drivers/media/rc/keymaps/Makefile` when `CONFIG_RC_MAP` is enabled, except for CEC-style integration if noted above. Board, USB, PCI, CEC, or platform IR drivers integrate with it by naming `RC_MAP_AVERMEDIA_M733A_RM_K6` as their default map.

## Risks and Edge Cases

Incorrect scancodes, wrong `KEY_*` assignments, a mismatched `.rc_proto`, or a stale `.name` break user-visible remote buttons without producing compile errors. The declared protocol `RC_PROTO_NEC` tells rc-core which decoded scancode namespace this map expects. Table ordering is not semantically important for lookups, but duplicate or vendor-overloaded scancodes should be reviewed carefully. The map can also drift from the v4l-utils userspace copy, causing different behavior between built-in maps and maps loaded from userspace.

## Test Signals

Useful checks include compiling the keymap with `CONFIG_RC_MAP=y` and `=m`, loading/unloading the generated module where applicable, confirming `rc_map_register()` exposes `RC_MAP_AVERMEDIA_M733A_RM_K6`, using `ir-keytable -r` or equivalent rc-core introspection to inspect the map, and pressing representative numeric, navigation, volume/channel, power, and media keys on the target remote. Protocol-specific tests should verify that decoded `RC_PROTO_NEC` scancodes match the table values and that unknown buttons do not alias to unsafe actions such as power or record.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-avermedia-m733a-rm-k6.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-avermedia-rm-ks.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-avermedia-rm-ks.c

## Purpose

`rc-avermedia-rm-ks.c` provides the `RC_MAP_AVERMEDIA_RM_KS` remote-controller keymap for `AverMedia RM-KS remote controller keytable`. It is a data-only rc-core map: decoded remote-control scan codes are translated into Linux input `KEY_*` events for the bundled receiver or board driver. The table has 27 scan-code entries; early entries include `0x0501->KEY_POWER2`, `0x0502->KEY_CHANNELUP`, `0x0503->KEY_CHANNELDOWN`, `0x0504->KEY_VOLUMEUP`, `0x0505->KEY_VOLUMEDOWN`, `0x0506->KEY_MUTE`. The represented controls cover numeric entry, power/input selection, navigation/menu, channel/volume, DVR/media transport, teletext/EPG/application keys.

## Important APIs, Types, and Functions

- `struct rc_map_table avermedia_rm_ks[]` is the static scan-code-to-keycode table.
- `struct rc_map_list avermedia_rm_ks_map` publishes `.scan = avermedia_rm_ks`, `.size = ARRAY_SIZE(avermedia_rm_ks)`, `.rc_proto = RC_PROTO_NEC`, and `.name = RC_MAP_AVERMEDIA_RM_KS` to rc-core.
- The module init function calls `rc_map_register()` and the exit function calls `rc_map_unregister()`, so the map is visible to rc-core only while the object is built in or the module is loaded.
- It has normal `module_init()`/`module_exit()` hooks.

## Control Flow

There is no active decode algorithm in this file. At build or module-load time, the map is registered with the rc-core map registry. A receiver driver later sets an `rc_dev->map_name` matching `RC_MAP_AVERMEDIA_RM_KS` or userspace selects that map with tooling such as `ir-keytable`; rc-core then looks up decoded scancodes in `avermedia_rm_ks` and emits the associated input keycodes. Unload or rc-core teardown unregisters the map, after which new lookups by name should fail or fall back to another configured map.

## State and Persistence Behavior

The persistent state is the compiled static table plus the registry node in rc-core. The file does not allocate per-device memory, take locks, touch hardware, or persist user settings. Runtime key state, repeat filtering, protocol decoding, and user remaps live in rc-core, the receiver driver, and input/ir-keytable configuration rather than in this keymap source.

## Dependencies and Integration Points

The file depends on `media/rc-map.h`, `linux/module.h`, Linux input `KEY_*` definitions, the `RC_MAP_*` string namespace, and the protocol enum `RC_PROTO_NEC`. It is built through `drivers/media/rc/keymaps/Makefile` when `CONFIG_RC_MAP` is enabled, except for CEC-style integration if noted above. Board, USB, PCI, CEC, or platform IR drivers integrate with it by naming `RC_MAP_AVERMEDIA_RM_KS` as their default map.

## Risks and Edge Cases

Incorrect scancodes, wrong `KEY_*` assignments, a mismatched `.rc_proto`, or a stale `.name` break user-visible remote buttons without producing compile errors. The declared protocol `RC_PROTO_NEC` tells rc-core which decoded scancode namespace this map expects. Table ordering is not semantically important for lookups, but duplicate or vendor-overloaded scancodes should be reviewed carefully. The map can also drift from the v4l-utils userspace copy, causing different behavior between built-in maps and maps loaded from userspace.

## Test Signals

Useful checks include compiling the keymap with `CONFIG_RC_MAP=y` and `=m`, loading/unloading the generated module where applicable, confirming `rc_map_register()` exposes `RC_MAP_AVERMEDIA_RM_KS`, using `ir-keytable -r` or equivalent rc-core introspection to inspect the map, and pressing representative numeric, navigation, volume/channel, power, and media keys on the target remote. Protocol-specific tests should verify that decoded `RC_PROTO_NEC` scancodes match the table values and that unknown buttons do not alias to unsafe actions such as power or record.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-avermedia-rm-ks.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-avermedia.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-avermedia.c

## Purpose

`rc-avermedia.c` provides the `RC_MAP_AVERMEDIA` remote-controller keymap for `avermedia remote controller keytable`. It is a data-only rc-core map: decoded remote-control scan codes are translated into Linux input `KEY_*` events for the bundled receiver or board driver. The table has 36 scan-code entries; early entries include `0x28->KEY_NUMERIC_1`, `0x18->KEY_NUMERIC_2`, `0x38->KEY_NUMERIC_3`, `0x24->KEY_NUMERIC_4`, `0x14->KEY_NUMERIC_5`, `0x34->KEY_NUMERIC_6`. The represented controls cover numeric entry, power/input selection, channel/volume, DVR/media transport, colored function keys, teletext/EPG/application keys.

## Important APIs, Types, and Functions

- `struct rc_map_table avermedia[]` is the static scan-code-to-keycode table.
- `struct rc_map_list avermedia_map` publishes `.scan = avermedia`, `.size = ARRAY_SIZE(avermedia)`, `.rc_proto = RC_PROTO_UNKNOWN`, and `.name = RC_MAP_AVERMEDIA` to rc-core.
- The module init function calls `rc_map_register()` and the exit function calls `rc_map_unregister()`, so the map is visible to rc-core only while the object is built in or the module is loaded.
- It has normal `module_init()`/`module_exit()` hooks.

## Control Flow

There is no active decode algorithm in this file. At build or module-load time, the map is registered with the rc-core map registry. A receiver driver later sets an `rc_dev->map_name` matching `RC_MAP_AVERMEDIA` or userspace selects that map with tooling such as `ir-keytable`; rc-core then looks up decoded scancodes in `avermedia` and emits the associated input keycodes. Unload or rc-core teardown unregisters the map, after which new lookups by name should fail or fall back to another configured map.

## State and Persistence Behavior

The persistent state is the compiled static table plus the registry node in rc-core. The file does not allocate per-device memory, take locks, touch hardware, or persist user settings. Runtime key state, repeat filtering, protocol decoding, and user remaps live in rc-core, the receiver driver, and input/ir-keytable configuration rather than in this keymap source.

## Dependencies and Integration Points

The file depends on `media/rc-map.h`, `linux/module.h`, Linux input `KEY_*` definitions, the `RC_MAP_*` string namespace, and the protocol enum `RC_PROTO_UNKNOWN`. It is built through `drivers/media/rc/keymaps/Makefile` when `CONFIG_RC_MAP` is enabled, except for CEC-style integration if noted above. Board, USB, PCI, CEC, or platform IR drivers integrate with it by naming `RC_MAP_AVERMEDIA` as their default map.

## Risks and Edge Cases

Incorrect scancodes, wrong `KEY_*` assignments, a mismatched `.rc_proto`, or a stale `.name` break user-visible remote buttons without producing compile errors. Because the protocol is `RC_PROTO_UNKNOWN`, correctness depends on the consuming hardware driver or legacy decoder path supplying matching scancodes. Table ordering is not semantically important for lookups, but duplicate or vendor-overloaded scancodes should be reviewed carefully. The map can also drift from the v4l-utils userspace copy, causing different behavior between built-in maps and maps loaded from userspace.

## Test Signals

Useful checks include compiling the keymap with `CONFIG_RC_MAP=y` and `=m`, loading/unloading the generated module where applicable, confirming `rc_map_register()` exposes `RC_MAP_AVERMEDIA`, using `ir-keytable -r` or equivalent rc-core introspection to inspect the map, and pressing representative numeric, navigation, volume/channel, power, and media keys on the target remote. Protocol-specific tests should verify that decoded `RC_PROTO_UNKNOWN` scancodes match the table values and that unknown buttons do not alias to unsafe actions such as power or record.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-avermedia.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-avertv-303.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-avertv-303.c

## Purpose

`rc-avertv-303.c` provides the `RC_MAP_AVERTV_303` remote-controller keymap for `AVERTV STUDIO 303 Remote controller keytable`. It is a data-only rc-core map: decoded remote-control scan codes are translated into Linux input `KEY_*` events for the bundled receiver or board driver. The table has 36 scan-code entries; early entries include `0x2a->KEY_NUMERIC_1`, `0x32->KEY_NUMERIC_2`, `0x3a->KEY_NUMERIC_3`, `0x4a->KEY_NUMERIC_4`, `0x52->KEY_NUMERIC_5`, `0x5a->KEY_NUMERIC_6`. The represented controls cover numeric entry, power/input selection, navigation/menu, channel/volume, DVR/media transport, colored function keys, teletext/EPG/application keys.

## Important APIs, Types, and Functions

- `struct rc_map_table avertv_303[]` is the static scan-code-to-keycode table.
- `struct rc_map_list avertv_303_map` publishes `.scan = avertv_303`, `.size = ARRAY_SIZE(avertv_303)`, `.rc_proto = RC_PROTO_UNKNOWN`, and `.name = RC_MAP_AVERTV_303` to rc-core.
- The module init function calls `rc_map_register()` and the exit function calls `rc_map_unregister()`, so the map is visible to rc-core only while the object is built in or the module is loaded.
- It has normal `module_init()`/`module_exit()` hooks.

## Control Flow

There is no active decode algorithm in this file. At build or module-load time, the map is registered with the rc-core map registry. A receiver driver later sets an `rc_dev->map_name` matching `RC_MAP_AVERTV_303` or userspace selects that map with tooling such as `ir-keytable`; rc-core then looks up decoded scancodes in `avertv_303` and emits the associated input keycodes. Unload or rc-core teardown unregisters the map, after which new lookups by name should fail or fall back to another configured map.

## State and Persistence Behavior

The persistent state is the compiled static table plus the registry node in rc-core. The file does not allocate per-device memory, take locks, touch hardware, or persist user settings. Runtime key state, repeat filtering, protocol decoding, and user remaps live in rc-core, the receiver driver, and input/ir-keytable configuration rather than in this keymap source.

## Dependencies and Integration Points

The file depends on `media/rc-map.h`, `linux/module.h`, Linux input `KEY_*` definitions, the `RC_MAP_*` string namespace, and the protocol enum `RC_PROTO_UNKNOWN`. It is built through `drivers/media/rc/keymaps/Makefile` when `CONFIG_RC_MAP` is enabled, except for CEC-style integration if noted above. Board, USB, PCI, CEC, or platform IR drivers integrate with it by naming `RC_MAP_AVERTV_303` as their default map.

## Risks and Edge Cases

Incorrect scancodes, wrong `KEY_*` assignments, a mismatched `.rc_proto`, or a stale `.name` break user-visible remote buttons without producing compile errors. Because the protocol is `RC_PROTO_UNKNOWN`, correctness depends on the consuming hardware driver or legacy decoder path supplying matching scancodes. Table ordering is not semantically important for lookups, but duplicate or vendor-overloaded scancodes should be reviewed carefully. The map can also drift from the v4l-utils userspace copy, causing different behavior between built-in maps and maps loaded from userspace.

## Test Signals

Useful checks include compiling the keymap with `CONFIG_RC_MAP=y` and `=m`, loading/unloading the generated module where applicable, confirming `rc_map_register()` exposes `RC_MAP_AVERTV_303`, using `ir-keytable -r` or equivalent rc-core introspection to inspect the map, and pressing representative numeric, navigation, volume/channel, power, and media keys on the target remote. Protocol-specific tests should verify that decoded `RC_PROTO_UNKNOWN` scancodes match the table values and that unknown buttons do not alias to unsafe actions such as power or record.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-avertv-303.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-azurewave-ad-tu700.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-azurewave-ad-tu700.c

## Purpose

`rc-azurewave-ad-tu700.c` provides the `RC_MAP_AZUREWAVE_AD_TU700` remote-controller keymap for `TwinHan AzureWave AD-TU700(704J) remote controller keytable`. It is a data-only rc-core map: decoded remote-control scan codes are translated into Linux input `KEY_*` events for the bundled receiver or board driver. The table has 53 scan-code entries; early entries include `0x0000->KEY_TAB`, `0x0001->KEY_NUMERIC_2`, `0x0002->KEY_CHANNELDOWN`, `0x0003->KEY_NUMERIC_1`, `0x0004->KEY_MENU`, `0x0005->KEY_CHANNELUP`. The represented controls cover numeric entry, power/input selection, navigation/menu, channel/volume, DVR/media transport, colored function keys, teletext/EPG/application keys.

## Important APIs, Types, and Functions

- `struct rc_map_table azurewave_ad_tu700[]` is the static scan-code-to-keycode table.
- `struct rc_map_list azurewave_ad_tu700_map` publishes `.scan = azurewave_ad_tu700`, `.size = ARRAY_SIZE(azurewave_ad_tu700)`, `.rc_proto = RC_PROTO_NEC`, and `.name = RC_MAP_AZUREWAVE_AD_TU700` to rc-core.
- The module init function calls `rc_map_register()` and the exit function calls `rc_map_unregister()`, so the map is visible to rc-core only while the object is built in or the module is loaded.
- It has normal `module_init()`/`module_exit()` hooks.

## Control Flow

There is no active decode algorithm in this file. At build or module-load time, the map is registered with the rc-core map registry. A receiver driver later sets an `rc_dev->map_name` matching `RC_MAP_AZUREWAVE_AD_TU700` or userspace selects that map with tooling such as `ir-keytable`; rc-core then looks up decoded scancodes in `azurewave_ad_tu700` and emits the associated input keycodes. Unload or rc-core teardown unregisters the map, after which new lookups by name should fail or fall back to another configured map.

## State and Persistence Behavior

The persistent state is the compiled static table plus the registry node in rc-core. The file does not allocate per-device memory, take locks, touch hardware, or persist user settings. Runtime key state, repeat filtering, protocol decoding, and user remaps live in rc-core, the receiver driver, and input/ir-keytable configuration rather than in this keymap source.

## Dependencies and Integration Points

The file depends on `media/rc-map.h`, `linux/module.h`, Linux input `KEY_*` definitions, the `RC_MAP_*` string namespace, and the protocol enum `RC_PROTO_NEC`. It is built through `drivers/media/rc/keymaps/Makefile` when `CONFIG_RC_MAP` is enabled, except for CEC-style integration if noted above. Board, USB, PCI, CEC, or platform IR drivers integrate with it by naming `RC_MAP_AZUREWAVE_AD_TU700` as their default map.

## Risks and Edge Cases

Incorrect scancodes, wrong `KEY_*` assignments, a mismatched `.rc_proto`, or a stale `.name` break user-visible remote buttons without producing compile errors. The declared protocol `RC_PROTO_NEC` tells rc-core which decoded scancode namespace this map expects. Table ordering is not semantically important for lookups, but duplicate or vendor-overloaded scancodes should be reviewed carefully. The map can also drift from the v4l-utils userspace copy, causing different behavior between built-in maps and maps loaded from userspace.

## Test Signals

Useful checks include compiling the keymap with `CONFIG_RC_MAP=y` and `=m`, loading/unloading the generated module where applicable, confirming `rc_map_register()` exposes `RC_MAP_AZUREWAVE_AD_TU700`, using `ir-keytable -r` or equivalent rc-core introspection to inspect the map, and pressing representative numeric, navigation, volume/channel, power, and media keys on the target remote. Protocol-specific tests should verify that decoded `RC_PROTO_NEC` scancodes match the table values and that unknown buttons do not alias to unsafe actions such as power or record.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-azurewave-ad-tu700.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-beelink-gs1.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-beelink-gs1.c

## Purpose

`rc-beelink-gs1.c` provides the `RC_MAP_BEELINK_GS1` remote-controller keymap for `Beelink GS1 remote controller keytable`. It is a data-only rc-core map: decoded remote-control scan codes are translated into Linux input `KEY_*` events for the bundled receiver or board driver. The table has 34 scan-code entries; early entries include `0x40400d->KEY_TV`, `0x80f1->KEY_TV`, `0x80f3->KEY_TV`, `0x80f4->KEY_TV`, `0x8051->KEY_POWER`, `0x804d->KEY_MUTE`. The represented controls cover numeric entry, power/input selection, navigation/menu, channel/volume, teletext/EPG/application keys.

## Important APIs, Types, and Functions

- `struct rc_map_table beelink_gs1_table[]` is the static scan-code-to-keycode table.
- `struct rc_map_list beelink_gs1_map` publishes `.scan = beelink_gs1_table`, `.size = ARRAY_SIZE(beelink_gs1_table)`, `.rc_proto = RC_PROTO_NEC`, and `.name = RC_MAP_BEELINK_GS1` to rc-core.
- The module init function calls `rc_map_register()` and the exit function calls `rc_map_unregister()`, so the map is visible to rc-core only while the object is built in or the module is loaded.
- It has normal `module_init()`/`module_exit()` hooks.

## Control Flow

There is no active decode algorithm in this file. At build or module-load time, the map is registered with the rc-core map registry. A receiver driver later sets an `rc_dev->map_name` matching `RC_MAP_BEELINK_GS1` or userspace selects that map with tooling such as `ir-keytable`; rc-core then looks up decoded scancodes in `beelink_gs1_table` and emits the associated input keycodes. Unload or rc-core teardown unregisters the map, after which new lookups by name should fail or fall back to another configured map.

## State and Persistence Behavior

The persistent state is the compiled static table plus the registry node in rc-core. The file does not allocate per-device memory, take locks, touch hardware, or persist user settings. Runtime key state, repeat filtering, protocol decoding, and user remaps live in rc-core, the receiver driver, and input/ir-keytable configuration rather than in this keymap source.

## Dependencies and Integration Points

The file depends on `media/rc-map.h`, `linux/module.h`, Linux input `KEY_*` definitions, the `RC_MAP_*` string namespace, and the protocol enum `RC_PROTO_NEC`. It is built through `drivers/media/rc/keymaps/Makefile` when `CONFIG_RC_MAP` is enabled, except for CEC-style integration if noted above. Board, USB, PCI, CEC, or platform IR drivers integrate with it by naming `RC_MAP_BEELINK_GS1` as their default map.

## Risks and Edge Cases

Incorrect scancodes, wrong `KEY_*` assignments, a mismatched `.rc_proto`, or a stale `.name` break user-visible remote buttons without producing compile errors. The declared protocol `RC_PROTO_NEC` tells rc-core which decoded scancode namespace this map expects. Table ordering is not semantically important for lookups, but duplicate or vendor-overloaded scancodes should be reviewed carefully. The map can also drift from the v4l-utils userspace copy, causing different behavior between built-in maps and maps loaded from userspace.

## Test Signals

Useful checks include compiling the keymap with `CONFIG_RC_MAP=y` and `=m`, loading/unloading the generated module where applicable, confirming `rc_map_register()` exposes `RC_MAP_BEELINK_GS1`, using `ir-keytable -r` or equivalent rc-core introspection to inspect the map, and pressing representative numeric, navigation, volume/channel, power, and media keys on the target remote. Protocol-specific tests should verify that decoded `RC_PROTO_NEC` scancodes match the table values and that unknown buttons do not alias to unsafe actions such as power or record.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-beelink-gs1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-beelink-mxiii.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-beelink-mxiii.c

## Purpose

`rc-beelink-mxiii.c` provides the `RC_MAP_BEELINK_MXIII` remote-controller keymap for `Beelink Mini MXIII remote controller keytable`. It is a data-only rc-core map: decoded remote-control scan codes are translated into Linux input `KEY_*` events for the bundled receiver or board driver. The table has 12 scan-code entries; early entries include `0xb2dc->KEY_POWER`, `0xb288->KEY_MUTE`, `0xb282->KEY_HOME`, `0xb2ca->KEY_UP`, `0xb299->KEY_LEFT`, `0xb2ce->KEY_OK`. The represented controls cover power/input selection, navigation/menu, channel/volume.

## Important APIs, Types, and Functions

- `struct rc_map_table beelink_mxiii[]` is the static scan-code-to-keycode table.
- `struct rc_map_list beelink_mxiii_map` publishes `.scan = beelink_mxiii`, `.size = ARRAY_SIZE(beelink_mxiii)`, `.rc_proto = RC_PROTO_NEC`, and `.name = RC_MAP_BEELINK_MXIII` to rc-core.
- The module init function calls `rc_map_register()` and the exit function calls `rc_map_unregister()`, so the map is visible to rc-core only while the object is built in or the module is loaded.
- It has normal `module_init()`/`module_exit()` hooks.

## Control Flow

There is no active decode algorithm in this file. At build or module-load time, the map is registered with the rc-core map registry. A receiver driver later sets an `rc_dev->map_name` matching `RC_MAP_BEELINK_MXIII` or userspace selects that map with tooling such as `ir-keytable`; rc-core then looks up decoded scancodes in `beelink_mxiii` and emits the associated input keycodes. Unload or rc-core teardown unregisters the map, after which new lookups by name should fail or fall back to another configured map.

## State and Persistence Behavior

The persistent state is the compiled static table plus the registry node in rc-core. The file does not allocate per-device memory, take locks, touch hardware, or persist user settings. Runtime key state, repeat filtering, protocol decoding, and user remaps live in rc-core, the receiver driver, and input/ir-keytable configuration rather than in this keymap source.

## Dependencies and Integration Points

The file depends on `media/rc-map.h`, `linux/module.h`, Linux input `KEY_*` definitions, the `RC_MAP_*` string namespace, and the protocol enum `RC_PROTO_NEC`. It is built through `drivers/media/rc/keymaps/Makefile` when `CONFIG_RC_MAP` is enabled, except for CEC-style integration if noted above. Board, USB, PCI, CEC, or platform IR drivers integrate with it by naming `RC_MAP_BEELINK_MXIII` as their default map.

## Risks and Edge Cases

Incorrect scancodes, wrong `KEY_*` assignments, a mismatched `.rc_proto`, or a stale `.name` break user-visible remote buttons without producing compile errors. The declared protocol `RC_PROTO_NEC` tells rc-core which decoded scancode namespace this map expects. Table ordering is not semantically important for lookups, but duplicate or vendor-overloaded scancodes should be reviewed carefully. The map can also drift from the v4l-utils userspace copy, causing different behavior between built-in maps and maps loaded from userspace.

## Test Signals

Useful checks include compiling the keymap with `CONFIG_RC_MAP=y` and `=m`, loading/unloading the generated module where applicable, confirming `rc_map_register()` exposes `RC_MAP_BEELINK_MXIII`, using `ir-keytable -r` or equivalent rc-core introspection to inspect the map, and pressing representative numeric, navigation, volume/channel, power, and media keys on the target remote. Protocol-specific tests should verify that decoded `RC_PROTO_NEC` scancodes match the table values and that unknown buttons do not alias to unsafe actions such as power or record.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-beelink-mxiii.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-behold-columbus.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-behold-columbus.c

## Purpose

`rc-behold-columbus.c` provides the `RC_MAP_BEHOLD_COLUMBUS` remote-controller keymap for `BeholdTV Columbus remote controller keytable`. It is a data-only rc-core map: decoded remote-control scan codes are translated into Linux input `KEY_*` events for the bundled receiver or board driver. The table has 28 scan-code entries; early entries include `0x13->KEY_MUTE`, `0x11->KEY_VIDEO`, `0x1C->KEY_TUNER`, `0x12->KEY_POWER`, `0x01->KEY_NUMERIC_1`, `0x02->KEY_NUMERIC_2`. The represented controls cover numeric entry, power/input selection, channel/volume, DVR/media transport.

## Important APIs, Types, and Functions

- `struct rc_map_table behold_columbus[]` is the static scan-code-to-keycode table.
- `struct rc_map_list behold_columbus_map` publishes `.scan = behold_columbus`, `.size = ARRAY_SIZE(behold_columbus)`, `.rc_proto = RC_PROTO_UNKNOWN`, and `.name = RC_MAP_BEHOLD_COLUMBUS` to rc-core.
- The module init function calls `rc_map_register()` and the exit function calls `rc_map_unregister()`, so the map is visible to rc-core only while the object is built in or the module is loaded.
- It has normal `module_init()`/`module_exit()` hooks.

## Control Flow

There is no active decode algorithm in this file. At build or module-load time, the map is registered with the rc-core map registry. A receiver driver later sets an `rc_dev->map_name` matching `RC_MAP_BEHOLD_COLUMBUS` or userspace selects that map with tooling such as `ir-keytable`; rc-core then looks up decoded scancodes in `behold_columbus` and emits the associated input keycodes. Unload or rc-core teardown unregisters the map, after which new lookups by name should fail or fall back to another configured map.

## State and Persistence Behavior

The persistent state is the compiled static table plus the registry node in rc-core. The file does not allocate per-device memory, take locks, touch hardware, or persist user settings. Runtime key state, repeat filtering, protocol decoding, and user remaps live in rc-core, the receiver driver, and input/ir-keytable configuration rather than in this keymap source.

## Dependencies and Integration Points

The file depends on `media/rc-map.h`, `linux/module.h`, Linux input `KEY_*` definitions, the `RC_MAP_*` string namespace, and the protocol enum `RC_PROTO_UNKNOWN`. It is built through `drivers/media/rc/keymaps/Makefile` when `CONFIG_RC_MAP` is enabled, except for CEC-style integration if noted above. Board, USB, PCI, CEC, or platform IR drivers integrate with it by naming `RC_MAP_BEHOLD_COLUMBUS` as their default map.

## Risks and Edge Cases

Incorrect scancodes, wrong `KEY_*` assignments, a mismatched `.rc_proto`, or a stale `.name` break user-visible remote buttons without producing compile errors. Because the protocol is `RC_PROTO_UNKNOWN`, correctness depends on the consuming hardware driver or legacy decoder path supplying matching scancodes. Table ordering is not semantically important for lookups, but duplicate or vendor-overloaded scancodes should be reviewed carefully. The map can also drift from the v4l-utils userspace copy, causing different behavior between built-in maps and maps loaded from userspace.

## Test Signals

Useful checks include compiling the keymap with `CONFIG_RC_MAP=y` and `=m`, loading/unloading the generated module where applicable, confirming `rc_map_register()` exposes `RC_MAP_BEHOLD_COLUMBUS`, using `ir-keytable -r` or equivalent rc-core introspection to inspect the map, and pressing representative numeric, navigation, volume/channel, power, and media keys on the target remote. Protocol-specific tests should verify that decoded `RC_PROTO_UNKNOWN` scancodes match the table values and that unknown buttons do not alias to unsafe actions such as power or record.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-behold-columbus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-behold.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-behold.c

## Purpose

`rc-behold.c` provides the `RC_MAP_BEHOLD` remote-controller keymap for `BeholdTV 60x series remote controller keytable`. It is a data-only rc-core map: decoded remote-control scan codes are translated into Linux input `KEY_*` events for the bundled receiver or board driver. The table has 34 scan-code entries; early entries include `0x866b1c->KEY_TUNER`, `0x866b12->KEY_POWER`, `0x866b01->KEY_NUMERIC_1`, `0x866b02->KEY_NUMERIC_2`, `0x866b03->KEY_NUMERIC_3`, `0x866b04->KEY_NUMERIC_4`. The represented controls cover numeric entry, power/input selection, navigation/menu, channel/volume, DVR/media transport, colored function keys, teletext/EPG/application keys.

## Important APIs, Types, and Functions

- `struct rc_map_table behold[]` is the static scan-code-to-keycode table.
- `struct rc_map_list behold_map` publishes `.scan = behold`, `.size = ARRAY_SIZE(behold)`, `.rc_proto = RC_PROTO_NECX`, and `.name = RC_MAP_BEHOLD` to rc-core.
- The module init function calls `rc_map_register()` and the exit function calls `rc_map_unregister()`, so the map is visible to rc-core only while the object is built in or the module is loaded.
- It has normal `module_init()`/`module_exit()` hooks.

## Control Flow

There is no active decode algorithm in this file. At build or module-load time, the map is registered with the rc-core map registry. A receiver driver later sets an `rc_dev->map_name` matching `RC_MAP_BEHOLD` or userspace selects that map with tooling such as `ir-keytable`; rc-core then looks up decoded scancodes in `behold` and emits the associated input keycodes. Unload or rc-core teardown unregisters the map, after which new lookups by name should fail or fall back to another configured map.

## State and Persistence Behavior

The persistent state is the compiled static table plus the registry node in rc-core. The file does not allocate per-device memory, take locks, touch hardware, or persist user settings. Runtime key state, repeat filtering, protocol decoding, and user remaps live in rc-core, the receiver driver, and input/ir-keytable configuration rather than in this keymap source.

## Dependencies and Integration Points

The file depends on `media/rc-map.h`, `linux/module.h`, Linux input `KEY_*` definitions, the `RC_MAP_*` string namespace, and the protocol enum `RC_PROTO_NECX`. It is built through `drivers/media/rc/keymaps/Makefile` when `CONFIG_RC_MAP` is enabled, except for CEC-style integration if noted above. Board, USB, PCI, CEC, or platform IR drivers integrate with it by naming `RC_MAP_BEHOLD` as their default map.

## Risks and Edge Cases

Incorrect scancodes, wrong `KEY_*` assignments, a mismatched `.rc_proto`, or a stale `.name` break user-visible remote buttons without producing compile errors. The declared protocol `RC_PROTO_NECX` tells rc-core which decoded scancode namespace this map expects. Table ordering is not semantically important for lookups, but duplicate or vendor-overloaded scancodes should be reviewed carefully. The map can also drift from the v4l-utils userspace copy, causing different behavior between built-in maps and maps loaded from userspace.

## Test Signals

Useful checks include compiling the keymap with `CONFIG_RC_MAP=y` and `=m`, loading/unloading the generated module where applicable, confirming `rc_map_register()` exposes `RC_MAP_BEHOLD`, using `ir-keytable -r` or equivalent rc-core introspection to inspect the map, and pressing representative numeric, navigation, volume/channel, power, and media keys on the target remote. Protocol-specific tests should verify that decoded `RC_PROTO_NECX` scancodes match the table values and that unknown buttons do not alias to unsafe actions such as power or record.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-behold.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-budget-ci-old.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-budget-ci-old.c

## Purpose

`rc-budget-ci-old.c` provides the `RC_MAP_BUDGET_CI_OLD` remote-controller keymap for `budget-ci-old remote controller keytable`. It is a data-only rc-core map: decoded remote-control scan codes are translated into Linux input `KEY_*` events for the bundled receiver or board driver. The table has 45 scan-code entries; early entries include `0x00->KEY_NUMERIC_0`, `0x01->KEY_NUMERIC_1`, `0x02->KEY_NUMERIC_2`, `0x03->KEY_NUMERIC_3`, `0x04->KEY_NUMERIC_4`, `0x05->KEY_NUMERIC_5`. The represented controls cover numeric entry, power/input selection, navigation/menu, channel/volume, DVR/media transport, colored function keys.

## Important APIs, Types, and Functions

- `struct rc_map_table budget_ci_old[]` is the static scan-code-to-keycode table.
- `struct rc_map_list budget_ci_old_map` publishes `.scan = budget_ci_old`, `.size = ARRAY_SIZE(budget_ci_old)`, `.rc_proto = RC_PROTO_UNKNOWN`, and `.name = RC_MAP_BUDGET_CI_OLD` to rc-core.
- The module init function calls `rc_map_register()` and the exit function calls `rc_map_unregister()`, so the map is visible to rc-core only while the object is built in or the module is loaded.
- It has normal `module_init()`/`module_exit()` hooks.

## Control Flow

There is no active decode algorithm in this file. At build or module-load time, the map is registered with the rc-core map registry. A receiver driver later sets an `rc_dev->map_name` matching `RC_MAP_BUDGET_CI_OLD` or userspace selects that map with tooling such as `ir-keytable`; rc-core then looks up decoded scancodes in `budget_ci_old` and emits the associated input keycodes. Unload or rc-core teardown unregisters the map, after which new lookups by name should fail or fall back to another configured map.

## State and Persistence Behavior

The persistent state is the compiled static table plus the registry node in rc-core. The file does not allocate per-device memory, take locks, touch hardware, or persist user settings. Runtime key state, repeat filtering, protocol decoding, and user remaps live in rc-core, the receiver driver, and input/ir-keytable configuration rather than in this keymap source.

## Dependencies and Integration Points

The file depends on `media/rc-map.h`, `linux/module.h`, Linux input `KEY_*` definitions, the `RC_MAP_*` string namespace, and the protocol enum `RC_PROTO_UNKNOWN`. It is built through `drivers/media/rc/keymaps/Makefile` when `CONFIG_RC_MAP` is enabled, except for CEC-style integration if noted above. Board, USB, PCI, CEC, or platform IR drivers integrate with it by naming `RC_MAP_BUDGET_CI_OLD` as their default map.

## Risks and Edge Cases

Incorrect scancodes, wrong `KEY_*` assignments, a mismatched `.rc_proto`, or a stale `.name` break user-visible remote buttons without producing compile errors. Because the protocol is `RC_PROTO_UNKNOWN`, correctness depends on the consuming hardware driver or legacy decoder path supplying matching scancodes. Table ordering is not semantically important for lookups, but duplicate or vendor-overloaded scancodes should be reviewed carefully. The map can also drift from the v4l-utils userspace copy, causing different behavior between built-in maps and maps loaded from userspace.

## Test Signals

Useful checks include compiling the keymap with `CONFIG_RC_MAP=y` and `=m`, loading/unloading the generated module where applicable, confirming `rc_map_register()` exposes `RC_MAP_BUDGET_CI_OLD`, using `ir-keytable -r` or equivalent rc-core introspection to inspect the map, and pressing representative numeric, navigation, volume/channel, power, and media keys on the target remote. Protocol-specific tests should verify that decoded `RC_PROTO_UNKNOWN` scancodes match the table values and that unknown buttons do not alias to unsafe actions such as power or record.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-budget-ci-old.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-cec.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-cec.c

## Purpose

`rc-cec.c` provides the `RC_MAP_CEC` remote-controller keymap for `rc-cec.c`. It is a data-only rc-core map: decoded remote-control scan codes are translated into Linux input `KEY_*` events for the bundled receiver or board driver. The table has 97 scan-code entries; early entries include `0x00->KEY_OK`, `0x01->KEY_UP`, `0x02->KEY_DOWN`, `0x03->KEY_LEFT`, `0x04->KEY_RIGHT`, `0x05->KEY_RIGHT_UP`. The represented controls cover numeric entry, power/input selection, navigation/menu, channel/volume, DVR/media transport, colored function keys, teletext/EPG/application keys.

## Important APIs, Types, and Functions

- `struct rc_map_table cec[]` is the static scan-code-to-keycode table.
- `struct rc_map_list cec_map` publishes `.scan = cec`, `.size = ARRAY_SIZE(cec)`, `.rc_proto = RC_PROTO_CEC`, and `.name = RC_MAP_CEC` to rc-core.
- Unlike the ordinary keymap modules, this file defines the global `cec_map` and is linked into `rc-core` under `CONFIG_MEDIA_CEC_RC`; `rc-main.c` registers it directly because asynchronous CEC adapter creation cannot safely request a module.
- It does not declare standalone module init/exit hooks.

## Control Flow

There is no active decode algorithm in this file. At build or module-load time, the map is registered with the rc-core map registry. A receiver driver later sets an `rc_dev->map_name` matching `RC_MAP_CEC` or userspace selects that map with tooling such as `ir-keytable`; rc-core then looks up decoded scancodes in `cec` and emits the associated input keycodes. Unload or rc-core teardown unregisters the map, after which new lookups by name should fail or fall back to another configured map.

## State and Persistence Behavior

The persistent state is the compiled static table plus the registry node in rc-core. The file does not allocate per-device memory, take locks, touch hardware, or persist user settings. Runtime key state, repeat filtering, protocol decoding, and user remaps live in rc-core, the receiver driver, and input/ir-keytable configuration rather than in this keymap source.

## Dependencies and Integration Points

The file depends on `media/rc-map.h`, `linux/module.h`, Linux input `KEY_*` definitions, the `RC_MAP_*` string namespace, and the protocol enum `RC_PROTO_CEC`. It is built through `drivers/media/rc/keymaps/Makefile` when `CONFIG_RC_MAP` is enabled, except for CEC-style integration if noted above. Board, USB, PCI, CEC, or platform IR drivers integrate with it by naming `RC_MAP_CEC` as their default map.

## Risks and Edge Cases

Incorrect scancodes, wrong `KEY_*` assignments, a mismatched `.rc_proto`, or a stale `.name` break user-visible remote buttons without producing compile errors. The declared protocol `RC_PROTO_CEC` tells rc-core which decoded scancode namespace this map expects. Table ordering is not semantically important for lookups, but duplicate or vendor-overloaded scancodes should be reviewed carefully. The map can also drift from the v4l-utils userspace copy, causing different behavior between built-in maps and maps loaded from userspace.

## Test Signals

Useful checks include compiling the keymap with `CONFIG_RC_MAP=y` and `=m`, loading/unloading the generated module where applicable, confirming `rc_map_register()` exposes `RC_MAP_CEC`, using `ir-keytable -r` or equivalent rc-core introspection to inspect the map, and pressing representative numeric, navigation, volume/channel, power, and media keys on the target remote. Protocol-specific tests should verify that decoded `RC_PROTO_CEC` scancodes match the table values and that unknown buttons do not alias to unsafe actions such as power or record.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-cec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-cinergy-1400.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-cinergy-1400.c

## Purpose

`rc-cinergy-1400.c` provides the `RC_MAP_CINERGY_1400` remote-controller keymap for `Cinergy 1400 DVB-T remote controller keytable`. It is a data-only rc-core map: decoded remote-control scan codes are translated into Linux input `KEY_*` events for the bundled receiver or board driver. The table has 37 scan-code entries; early entries include `0x01->KEY_POWER`, `0x02->KEY_NUMERIC_1`, `0x03->KEY_NUMERIC_2`, `0x04->KEY_NUMERIC_3`, `0x05->KEY_NUMERIC_4`, `0x06->KEY_NUMERIC_5`. The represented controls cover numeric entry, power/input selection, navigation/menu, channel/volume, DVR/media transport, colored function keys, teletext/EPG/application keys.

## Important APIs, Types, and Functions

- `struct rc_map_table cinergy_1400[]` is the static scan-code-to-keycode table.
- `struct rc_map_list cinergy_1400_map` publishes `.scan = cinergy_1400`, `.size = ARRAY_SIZE(cinergy_1400)`, `.rc_proto = RC_PROTO_UNKNOWN`, and `.name = RC_MAP_CINERGY_1400` to rc-core.
- The module init function calls `rc_map_register()` and the exit function calls `rc_map_unregister()`, so the map is visible to rc-core only while the object is built in or the module is loaded.
- It has normal `module_init()`/`module_exit()` hooks.

## Control Flow

There is no active decode algorithm in this file. At build or module-load time, the map is registered with the rc-core map registry. A receiver driver later sets an `rc_dev->map_name` matching `RC_MAP_CINERGY_1400` or userspace selects that map with tooling such as `ir-keytable`; rc-core then looks up decoded scancodes in `cinergy_1400` and emits the associated input keycodes. Unload or rc-core teardown unregisters the map, after which new lookups by name should fail or fall back to another configured map.

## State and Persistence Behavior

The persistent state is the compiled static table plus the registry node in rc-core. The file does not allocate per-device memory, take locks, touch hardware, or persist user settings. Runtime key state, repeat filtering, protocol decoding, and user remaps live in rc-core, the receiver driver, and input/ir-keytable configuration rather than in this keymap source.

## Dependencies and Integration Points

The file depends on `media/rc-map.h`, `linux/module.h`, Linux input `KEY_*` definitions, the `RC_MAP_*` string namespace, and the protocol enum `RC_PROTO_UNKNOWN`. It is built through `drivers/media/rc/keymaps/Makefile` when `CONFIG_RC_MAP` is enabled, except for CEC-style integration if noted above. Board, USB, PCI, CEC, or platform IR drivers integrate with it by naming `RC_MAP_CINERGY_1400` as their default map.

## Risks and Edge Cases

Incorrect scancodes, wrong `KEY_*` assignments, a mismatched `.rc_proto`, or a stale `.name` break user-visible remote buttons without producing compile errors. Because the protocol is `RC_PROTO_UNKNOWN`, correctness depends on the consuming hardware driver or legacy decoder path supplying matching scancodes. Table ordering is not semantically important for lookups, but duplicate or vendor-overloaded scancodes should be reviewed carefully. The map can also drift from the v4l-utils userspace copy, causing different behavior between built-in maps and maps loaded from userspace.

## Test Signals

Useful checks include compiling the keymap with `CONFIG_RC_MAP=y` and `=m`, loading/unloading the generated module where applicable, confirming `rc_map_register()` exposes `RC_MAP_CINERGY_1400`, using `ir-keytable -r` or equivalent rc-core introspection to inspect the map, and pressing representative numeric, navigation, volume/channel, power, and media keys on the target remote. Protocol-specific tests should verify that decoded `RC_PROTO_UNKNOWN` scancodes match the table values and that unknown buttons do not alias to unsafe actions such as power or record.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-cinergy-1400.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-cinergy.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-cinergy.c

## Purpose

`rc-cinergy.c` provides the `RC_MAP_CINERGY` remote-controller keymap for `cinergy remote controller keytable`. It is a data-only rc-core map: decoded remote-control scan codes are translated into Linux input `KEY_*` events for the bundled receiver or board driver. The table has 34 scan-code entries; early entries include `0x00->KEY_NUMERIC_0`, `0x01->KEY_NUMERIC_1`, `0x02->KEY_NUMERIC_2`, `0x03->KEY_NUMERIC_3`, `0x04->KEY_NUMERIC_4`, `0x05->KEY_NUMERIC_5`. The represented controls cover numeric entry, power/input selection, navigation/menu, channel/volume, DVR/media transport, teletext/EPG/application keys.

## Important APIs, Types, and Functions

- `struct rc_map_table cinergy[]` is the static scan-code-to-keycode table.
- `struct rc_map_list cinergy_map` publishes `.scan = cinergy`, `.size = ARRAY_SIZE(cinergy)`, `.rc_proto = RC_PROTO_UNKNOWN`, and `.name = RC_MAP_CINERGY` to rc-core.
- The module init function calls `rc_map_register()` and the exit function calls `rc_map_unregister()`, so the map is visible to rc-core only while the object is built in or the module is loaded.
- It has normal `module_init()`/`module_exit()` hooks.

## Control Flow

There is no active decode algorithm in this file. At build or module-load time, the map is registered with the rc-core map registry. A receiver driver later sets an `rc_dev->map_name` matching `RC_MAP_CINERGY` or userspace selects that map with tooling such as `ir-keytable`; rc-core then looks up decoded scancodes in `cinergy` and emits the associated input keycodes. Unload or rc-core teardown unregisters the map, after which new lookups by name should fail or fall back to another configured map.

## State and Persistence Behavior

The persistent state is the compiled static table plus the registry node in rc-core. The file does not allocate per-device memory, take locks, touch hardware, or persist user settings. Runtime key state, repeat filtering, protocol decoding, and user remaps live in rc-core, the receiver driver, and input/ir-keytable configuration rather than in this keymap source.

## Dependencies and Integration Points

The file depends on `media/rc-map.h`, `linux/module.h`, Linux input `KEY_*` definitions, the `RC_MAP_*` string namespace, and the protocol enum `RC_PROTO_UNKNOWN`. It is built through `drivers/media/rc/keymaps/Makefile` when `CONFIG_RC_MAP` is enabled, except for CEC-style integration if noted above. Board, USB, PCI, CEC, or platform IR drivers integrate with it by naming `RC_MAP_CINERGY` as their default map.

## Risks and Edge Cases

Incorrect scancodes, wrong `KEY_*` assignments, a mismatched `.rc_proto`, or a stale `.name` break user-visible remote buttons without producing compile errors. Because the protocol is `RC_PROTO_UNKNOWN`, correctness depends on the consuming hardware driver or legacy decoder path supplying matching scancodes. Table ordering is not semantically important for lookups, but duplicate or vendor-overloaded scancodes should be reviewed carefully. The map can also drift from the v4l-utils userspace copy, causing different behavior between built-in maps and maps loaded from userspace.

## Test Signals

Useful checks include compiling the keymap with `CONFIG_RC_MAP=y` and `=m`, loading/unloading the generated module where applicable, confirming `rc_map_register()` exposes `RC_MAP_CINERGY`, using `ir-keytable -r` or equivalent rc-core introspection to inspect the map, and pressing representative numeric, navigation, volume/channel, power, and media keys on the target remote. Protocol-specific tests should verify that decoded `RC_PROTO_UNKNOWN` scancodes match the table values and that unknown buttons do not alias to unsafe actions such as power or record.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-cinergy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-ct-90405.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-ct-90405.c

## Purpose

`rc-ct-90405.c` provides the `RC_MAP_CT_90405` remote-controller keymap for `Toshiba CT-90405 remote controller keytable`. It is a data-only rc-core map: decoded remote-control scan codes are translated into Linux input `KEY_*` events for the bundled receiver or board driver. The table has 49 scan-code entries; early entries include `0x4014->KEY_SWITCHVIDEOMODE`, `0x4012->KEY_POWER`, `0x4044->KEY_TV`, `0x40be43->KEY_3D_MODE`, `0x400c->KEY_SUBTITLE`, `0x4001->KEY_NUMERIC_1`. The represented controls cover numeric entry, power/input selection, navigation/menu, channel/volume, DVR/media transport, colored function keys, teletext/EPG/application keys.

## Important APIs, Types, and Functions

- `struct rc_map_table ct_90405[]` is the static scan-code-to-keycode table.
- `struct rc_map_list ct_90405_map` publishes `.scan = ct_90405`, `.size = ARRAY_SIZE(ct_90405)`, `.rc_proto = RC_PROTO_NEC`, and `.name = RC_MAP_CT_90405` to rc-core.
- The module init function calls `rc_map_register()` and the exit function calls `rc_map_unregister()`, so the map is visible to rc-core only while the object is built in or the module is loaded.
- It has normal `module_init()`/`module_exit()` hooks.

## Control Flow

There is no active decode algorithm in this file. At build or module-load time, the map is registered with the rc-core map registry. A receiver driver later sets an `rc_dev->map_name` matching `RC_MAP_CT_90405` or userspace selects that map with tooling such as `ir-keytable`; rc-core then looks up decoded scancodes in `ct_90405` and emits the associated input keycodes. Unload or rc-core teardown unregisters the map, after which new lookups by name should fail or fall back to another configured map.

## State and Persistence Behavior

The persistent state is the compiled static table plus the registry node in rc-core. The file does not allocate per-device memory, take locks, touch hardware, or persist user settings. Runtime key state, repeat filtering, protocol decoding, and user remaps live in rc-core, the receiver driver, and input/ir-keytable configuration rather than in this keymap source.

## Dependencies and Integration Points

The file depends on `media/rc-map.h`, `linux/module.h`, Linux input `KEY_*` definitions, the `RC_MAP_*` string namespace, and the protocol enum `RC_PROTO_NEC`. It is built through `drivers/media/rc/keymaps/Makefile` when `CONFIG_RC_MAP` is enabled, except for CEC-style integration if noted above. Board, USB, PCI, CEC, or platform IR drivers integrate with it by naming `RC_MAP_CT_90405` as their default map.

## Risks and Edge Cases

Incorrect scancodes, wrong `KEY_*` assignments, a mismatched `.rc_proto`, or a stale `.name` break user-visible remote buttons without producing compile errors. The declared protocol `RC_PROTO_NEC` tells rc-core which decoded scancode namespace this map expects. Table ordering is not semantically important for lookups, but duplicate or vendor-overloaded scancodes should be reviewed carefully. The map can also drift from the v4l-utils userspace copy, causing different behavior between built-in maps and maps loaded from userspace.

## Test Signals

Useful checks include compiling the keymap with `CONFIG_RC_MAP=y` and `=m`, loading/unloading the generated module where applicable, confirming `rc_map_register()` exposes `RC_MAP_CT_90405`, using `ir-keytable -r` or equivalent rc-core introspection to inspect the map, and pressing representative numeric, navigation, volume/channel, power, and media keys on the target remote. Protocol-specific tests should verify that decoded `RC_PROTO_NEC` scancodes match the table values and that unknown buttons do not alias to unsafe actions such as power or record.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-ct-90405.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-d680-dmb.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-d680-dmb.c

## Purpose

`rc-d680-dmb.c` provides the `RC_MAP_D680_DMB` remote-controller keymap for `d680-dmb remote controller keytable`. It is a data-only rc-core map: decoded remote-control scan codes are translated into Linux input `KEY_*` events for the bundled receiver or board driver. The table has 35 scan-code entries; early entries include `0x0038->KEY_SWITCHVIDEOMODE`, `0x080c->KEY_ZOOM`, `0x0800->KEY_NUMERIC_0`, `0x0001->KEY_NUMERIC_1`, `0x0802->KEY_NUMERIC_2`, `0x0003->KEY_NUMERIC_3`. The represented controls cover numeric entry, power/input selection, navigation/menu, channel/volume, DVR/media transport.

## Important APIs, Types, and Functions

- `struct rc_map_table rc_map_d680_dmb_table[]` is the static scan-code-to-keycode table.
- `struct rc_map_list d680_dmb_map` publishes `.scan = rc_map_d680_dmb_table`, `.size = ARRAY_SIZE(rc_map_d680_dmb_table)`, `.rc_proto = RC_PROTO_UNKNOWN`, and `.name = RC_MAP_D680_DMB` to rc-core.
- The module init function calls `rc_map_register()` and the exit function calls `rc_map_unregister()`, so the map is visible to rc-core only while the object is built in or the module is loaded.
- It has normal `module_init()`/`module_exit()` hooks.

## Control Flow

There is no active decode algorithm in this file. At build or module-load time, the map is registered with the rc-core map registry. A receiver driver later sets an `rc_dev->map_name` matching `RC_MAP_D680_DMB` or userspace selects that map with tooling such as `ir-keytable`; rc-core then looks up decoded scancodes in `rc_map_d680_dmb_table` and emits the associated input keycodes. Unload or rc-core teardown unregisters the map, after which new lookups by name should fail or fall back to another configured map.

## State and Persistence Behavior

The persistent state is the compiled static table plus the registry node in rc-core. The file does not allocate per-device memory, take locks, touch hardware, or persist user settings. Runtime key state, repeat filtering, protocol decoding, and user remaps live in rc-core, the receiver driver, and input/ir-keytable configuration rather than in this keymap source.

## Dependencies and Integration Points

The file depends on `media/rc-map.h`, `linux/module.h`, Linux input `KEY_*` definitions, the `RC_MAP_*` string namespace, and the protocol enum `RC_PROTO_UNKNOWN`. It is built through `drivers/media/rc/keymaps/Makefile` when `CONFIG_RC_MAP` is enabled, except for CEC-style integration if noted above. Board, USB, PCI, CEC, or platform IR drivers integrate with it by naming `RC_MAP_D680_DMB` as their default map.

## Risks and Edge Cases

Incorrect scancodes, wrong `KEY_*` assignments, a mismatched `.rc_proto`, or a stale `.name` break user-visible remote buttons without producing compile errors. Because the protocol is `RC_PROTO_UNKNOWN`, correctness depends on the consuming hardware driver or legacy decoder path supplying matching scancodes. Table ordering is not semantically important for lookups, but duplicate or vendor-overloaded scancodes should be reviewed carefully. The map can also drift from the v4l-utils userspace copy, causing different behavior between built-in maps and maps loaded from userspace.

## Test Signals

Useful checks include compiling the keymap with `CONFIG_RC_MAP=y` and `=m`, loading/unloading the generated module where applicable, confirming `rc_map_register()` exposes `RC_MAP_D680_DMB`, using `ir-keytable -r` or equivalent rc-core introspection to inspect the map, and pressing representative numeric, navigation, volume/channel, power, and media keys on the target remote. Protocol-specific tests should verify that decoded `RC_PROTO_UNKNOWN` scancodes match the table values and that unknown buttons do not alias to unsafe actions such as power or record.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-d680-dmb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-delock-61959.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-delock-61959.c

## Purpose

`rc-delock-61959.c` provides the `RC_MAP_DELOCK_61959` remote-controller keymap for `Delock 61959 remote keytable`. It is a data-only rc-core map: decoded remote-control scan codes are translated into Linux input `KEY_*` events for the bundled receiver or board driver. The table has 32 scan-code entries; early entries include `0x866b16->KEY_POWER2`, `0x866b0c->KEY_POWER`, `0x866b00->KEY_NUMERIC_1`, `0x866b01->KEY_NUMERIC_2`, `0x866b02->KEY_NUMERIC_3`, `0x866b03->KEY_NUMERIC_4`. The represented controls cover numeric entry, power/input selection, navigation/menu, channel/volume, DVR/media transport.

## Important APIs, Types, and Functions

- `struct rc_map_table delock_61959[]` is the static scan-code-to-keycode table.
- `struct rc_map_list delock_61959_map` publishes `.scan = delock_61959`, `.size = ARRAY_SIZE(delock_61959)`, `.rc_proto = RC_PROTO_NECX`, and `.name = RC_MAP_DELOCK_61959` to rc-core.
- The module init function calls `rc_map_register()` and the exit function calls `rc_map_unregister()`, so the map is visible to rc-core only while the object is built in or the module is loaded.
- It has normal `module_init()`/`module_exit()` hooks.

## Control Flow

There is no active decode algorithm in this file. At build or module-load time, the map is registered with the rc-core map registry. A receiver driver later sets an `rc_dev->map_name` matching `RC_MAP_DELOCK_61959` or userspace selects that map with tooling such as `ir-keytable`; rc-core then looks up decoded scancodes in `delock_61959` and emits the associated input keycodes. Unload or rc-core teardown unregisters the map, after which new lookups by name should fail or fall back to another configured map.

## State and Persistence Behavior

The persistent state is the compiled static table plus the registry node in rc-core. The file does not allocate per-device memory, take locks, touch hardware, or persist user settings. Runtime key state, repeat filtering, protocol decoding, and user remaps live in rc-core, the receiver driver, and input/ir-keytable configuration rather than in this keymap source.

## Dependencies and Integration Points

The file depends on `media/rc-map.h`, `linux/module.h`, Linux input `KEY_*` definitions, the `RC_MAP_*` string namespace, and the protocol enum `RC_PROTO_NECX`. It is built through `drivers/media/rc/keymaps/Makefile` when `CONFIG_RC_MAP` is enabled, except for CEC-style integration if noted above. Board, USB, PCI, CEC, or platform IR drivers integrate with it by naming `RC_MAP_DELOCK_61959` as their default map.

## Risks and Edge Cases

Incorrect scancodes, wrong `KEY_*` assignments, a mismatched `.rc_proto`, or a stale `.name` break user-visible remote buttons without producing compile errors. The declared protocol `RC_PROTO_NECX` tells rc-core which decoded scancode namespace this map expects. Table ordering is not semantically important for lookups, but duplicate or vendor-overloaded scancodes should be reviewed carefully. The map can also drift from the v4l-utils userspace copy, causing different behavior between built-in maps and maps loaded from userspace.

## Test Signals

Useful checks include compiling the keymap with `CONFIG_RC_MAP=y` and `=m`, loading/unloading the generated module where applicable, confirming `rc_map_register()` exposes `RC_MAP_DELOCK_61959`, using `ir-keytable -r` or equivalent rc-core introspection to inspect the map, and pressing representative numeric, navigation, volume/channel, power, and media keys on the target remote. Protocol-specific tests should verify that decoded `RC_PROTO_NECX` scancodes match the table values and that unknown buttons do not alias to unsafe actions such as power or record.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-delock-61959.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-dib0700-nec.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-dib0700-nec.c

## Purpose

`rc-dib0700-nec.c` provides the `RC_MAP_DIB0700_NEC_TABLE` remote-controller keymap for `dib0700-nec remote controller keytable`. It is a data-only rc-core map: decoded remote-control scan codes are translated into Linux input `KEY_*` events for the bundled receiver or board driver. The table has 70 scan-code entries; early entries include `0x866b13->KEY_MUTE`, `0x866b12->KEY_POWER`, `0x866b01->KEY_NUMERIC_1`, `0x866b02->KEY_NUMERIC_2`, `0x866b03->KEY_NUMERIC_3`, `0x866b04->KEY_NUMERIC_4`. The represented controls cover numeric entry, power/input selection, navigation/menu, channel/volume, DVR/media transport, colored function keys.

## Important APIs, Types, and Functions

- `struct rc_map_table dib0700_nec_table[]` is the static scan-code-to-keycode table.
- `struct rc_map_list dib0700_nec_map` publishes `.scan = dib0700_nec_table`, `.size = ARRAY_SIZE(dib0700_nec_table)`, `.rc_proto = RC_PROTO_NEC`, and `.name = RC_MAP_DIB0700_NEC_TABLE` to rc-core.
- The module init function calls `rc_map_register()` and the exit function calls `rc_map_unregister()`, so the map is visible to rc-core only while the object is built in or the module is loaded.
- It has normal `module_init()`/`module_exit()` hooks.

## Control Flow

There is no active decode algorithm in this file. At build or module-load time, the map is registered with the rc-core map registry. A receiver driver later sets an `rc_dev->map_name` matching `RC_MAP_DIB0700_NEC_TABLE` or userspace selects that map with tooling such as `ir-keytable`; rc-core then looks up decoded scancodes in `dib0700_nec_table` and emits the associated input keycodes. Unload or rc-core teardown unregisters the map, after which new lookups by name should fail or fall back to another configured map.

## State and Persistence Behavior

The persistent state is the compiled static table plus the registry node in rc-core. The file does not allocate per-device memory, take locks, touch hardware, or persist user settings. Runtime key state, repeat filtering, protocol decoding, and user remaps live in rc-core, the receiver driver, and input/ir-keytable configuration rather than in this keymap source.

## Dependencies and Integration Points

The file depends on `media/rc-map.h`, `linux/module.h`, Linux input `KEY_*` definitions, the `RC_MAP_*` string namespace, and the protocol enum `RC_PROTO_NEC`. It is built through `drivers/media/rc/keymaps/Makefile` when `CONFIG_RC_MAP` is enabled, except for CEC-style integration if noted above. Board, USB, PCI, CEC, or platform IR drivers integrate with it by naming `RC_MAP_DIB0700_NEC_TABLE` as their default map.

## Risks and Edge Cases

Incorrect scancodes, wrong `KEY_*` assignments, a mismatched `.rc_proto`, or a stale `.name` break user-visible remote buttons without producing compile errors. The declared protocol `RC_PROTO_NEC` tells rc-core which decoded scancode namespace this map expects. Table ordering is not semantically important for lookups, but duplicate or vendor-overloaded scancodes should be reviewed carefully. The map can also drift from the v4l-utils userspace copy, causing different behavior between built-in maps and maps loaded from userspace.

## Test Signals

Useful checks include compiling the keymap with `CONFIG_RC_MAP=y` and `=m`, loading/unloading the generated module where applicable, confirming `rc_map_register()` exposes `RC_MAP_DIB0700_NEC_TABLE`, using `ir-keytable -r` or equivalent rc-core introspection to inspect the map, and pressing representative numeric, navigation, volume/channel, power, and media keys on the target remote. Protocol-specific tests should verify that decoded `RC_PROTO_NEC` scancodes match the table values and that unknown buttons do not alias to unsafe actions such as power or record.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-dib0700-nec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-dib0700-rc5.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-dib0700-rc5.c

## Purpose

`rc-dib0700-rc5.c` provides the `RC_MAP_DIB0700_RC5_TABLE` remote-controller keymap for `dib0700-rc5 remote controller keytable`. It is a data-only rc-core map: decoded remote-control scan codes are translated into Linux input `KEY_*` events for the bundled receiver or board driver. The table has 180 scan-code entries; early entries include `0x0700->KEY_MUTE`, `0x0701->KEY_MENU`, `0x0739->KEY_POWER`, `0x0703->KEY_VOLUMEUP`, `0x0709->KEY_VOLUMEDOWN`, `0x0706->KEY_CHANNELUP`. The represented controls cover numeric entry, power/input selection, navigation/menu, channel/volume, DVR/media transport, colored function keys, teletext/EPG/application keys.

## Important APIs, Types, and Functions

- `struct rc_map_table dib0700_rc5_table[]` is the static scan-code-to-keycode table.
- `struct rc_map_list dib0700_rc5_map` publishes `.scan = dib0700_rc5_table`, `.size = ARRAY_SIZE(dib0700_rc5_table)`, `.rc_proto = RC_PROTO_RC5`, and `.name = RC_MAP_DIB0700_RC5_TABLE` to rc-core.
- The module init function calls `rc_map_register()` and the exit function calls `rc_map_unregister()`, so the map is visible to rc-core only while the object is built in or the module is loaded.
- It has normal `module_init()`/`module_exit()` hooks.

## Control Flow

There is no active decode algorithm in this file. At build or module-load time, the map is registered with the rc-core map registry. A receiver driver later sets an `rc_dev->map_name` matching `RC_MAP_DIB0700_RC5_TABLE` or userspace selects that map with tooling such as `ir-keytable`; rc-core then looks up decoded scancodes in `dib0700_rc5_table` and emits the associated input keycodes. Unload or rc-core teardown unregisters the map, after which new lookups by name should fail or fall back to another configured map.

## State and Persistence Behavior

The persistent state is the compiled static table plus the registry node in rc-core. The file does not allocate per-device memory, take locks, touch hardware, or persist user settings. Runtime key state, repeat filtering, protocol decoding, and user remaps live in rc-core, the receiver driver, and input/ir-keytable configuration rather than in this keymap source.

## Dependencies and Integration Points

The file depends on `media/rc-map.h`, `linux/module.h`, Linux input `KEY_*` definitions, the `RC_MAP_*` string namespace, and the protocol enum `RC_PROTO_RC5`. It is built through `drivers/media/rc/keymaps/Makefile` when `CONFIG_RC_MAP` is enabled, except for CEC-style integration if noted above. Board, USB, PCI, CEC, or platform IR drivers integrate with it by naming `RC_MAP_DIB0700_RC5_TABLE` as their default map.

## Risks and Edge Cases

Incorrect scancodes, wrong `KEY_*` assignments, a mismatched `.rc_proto`, or a stale `.name` break user-visible remote buttons without producing compile errors. The declared protocol `RC_PROTO_RC5` tells rc-core which decoded scancode namespace this map expects. Table ordering is not semantically important for lookups, but duplicate or vendor-overloaded scancodes should be reviewed carefully. The map can also drift from the v4l-utils userspace copy, causing different behavior between built-in maps and maps loaded from userspace.

## Test Signals

Useful checks include compiling the keymap with `CONFIG_RC_MAP=y` and `=m`, loading/unloading the generated module where applicable, confirming `rc_map_register()` exposes `RC_MAP_DIB0700_RC5_TABLE`, using `ir-keytable -r` or equivalent rc-core introspection to inspect the map, and pressing representative numeric, navigation, volume/channel, power, and media keys on the target remote. Protocol-specific tests should verify that decoded `RC_PROTO_RC5` scancodes match the table values and that unknown buttons do not alias to unsafe actions such as power or record.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-dib0700-rc5.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-digitalnow-tinytwin.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-digitalnow-tinytwin.c

## Purpose

`rc-digitalnow-tinytwin.c` provides the `RC_MAP_DIGITALNOW_TINYTWIN` remote-controller keymap for `DigitalNow TinyTwin remote controller keytable`. It is a data-only rc-core map: decoded remote-control scan codes are translated into Linux input `KEY_*` events for the bundled receiver or board driver. The table has 49 scan-code entries; early entries include `0x0000->KEY_MUTE`, `0x0001->KEY_VOLUMEUP`, `0x0002->KEY_POWER2`, `0x0003->KEY_NUMERIC_2`, `0x0004->KEY_NUMERIC_3`, `0x0005->KEY_NUMERIC_4`. The represented controls cover numeric entry, power/input selection, navigation/menu, channel/volume, DVR/media transport, colored function keys, teletext/EPG/application keys.

## Important APIs, Types, and Functions

- `struct rc_map_table digitalnow_tinytwin[]` is the static scan-code-to-keycode table.
- `struct rc_map_list digitalnow_tinytwin_map` publishes `.scan = digitalnow_tinytwin`, `.size = ARRAY_SIZE(digitalnow_tinytwin)`, `.rc_proto = RC_PROTO_NEC`, and `.name = RC_MAP_DIGITALNOW_TINYTWIN` to rc-core.
- The module init function calls `rc_map_register()` and the exit function calls `rc_map_unregister()`, so the map is visible to rc-core only while the object is built in or the module is loaded.
- It has normal `module_init()`/`module_exit()` hooks.

## Control Flow

There is no active decode algorithm in this file. At build or module-load time, the map is registered with the rc-core map registry. A receiver driver later sets an `rc_dev->map_name` matching `RC_MAP_DIGITALNOW_TINYTWIN` or userspace selects that map with tooling such as `ir-keytable`; rc-core then looks up decoded scancodes in `digitalnow_tinytwin` and emits the associated input keycodes. Unload or rc-core teardown unregisters the map, after which new lookups by name should fail or fall back to another configured map.

## State and Persistence Behavior

The persistent state is the compiled static table plus the registry node in rc-core. The file does not allocate per-device memory, take locks, touch hardware, or persist user settings. Runtime key state, repeat filtering, protocol decoding, and user remaps live in rc-core, the receiver driver, and input/ir-keytable configuration rather than in this keymap source.

## Dependencies and Integration Points

The file depends on `media/rc-map.h`, `linux/module.h`, Linux input `KEY_*` definitions, the `RC_MAP_*` string namespace, and the protocol enum `RC_PROTO_NEC`. It is built through `drivers/media/rc/keymaps/Makefile` when `CONFIG_RC_MAP` is enabled, except for CEC-style integration if noted above. Board, USB, PCI, CEC, or platform IR drivers integrate with it by naming `RC_MAP_DIGITALNOW_TINYTWIN` as their default map.

## Risks and Edge Cases

Incorrect scancodes, wrong `KEY_*` assignments, a mismatched `.rc_proto`, or a stale `.name` break user-visible remote buttons without producing compile errors. The declared protocol `RC_PROTO_NEC` tells rc-core which decoded scancode namespace this map expects. Table ordering is not semantically important for lookups, but duplicate or vendor-overloaded scancodes should be reviewed carefully. The map can also drift from the v4l-utils userspace copy, causing different behavior between built-in maps and maps loaded from userspace.

## Test Signals

Useful checks include compiling the keymap with `CONFIG_RC_MAP=y` and `=m`, loading/unloading the generated module where applicable, confirming `rc_map_register()` exposes `RC_MAP_DIGITALNOW_TINYTWIN`, using `ir-keytable -r` or equivalent rc-core introspection to inspect the map, and pressing representative numeric, navigation, volume/channel, power, and media keys on the target remote. Protocol-specific tests should verify that decoded `RC_PROTO_NEC` scancodes match the table values and that unknown buttons do not alias to unsafe actions such as power or record.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-digitalnow-tinytwin.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-digittrade.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-digittrade.c

## Purpose

`rc-digittrade.c` provides the `RC_MAP_DIGITTRADE` remote-controller keymap for `Digittrade DVB-T USB Stick remote controller keytable`. It is a data-only rc-core map: decoded remote-control scan codes are translated into Linux input `KEY_*` events for the bundled receiver or board driver. The table has 28 scan-code entries; early entries include `0x0000->KEY_NUMERIC_9`, `0x0001->KEY_EPG`, `0x0002->KEY_VOLUMEDOWN`, `0x0003->KEY_TEXT`, `0x0004->KEY_NUMERIC_8`, `0x0005->KEY_MUTE`. The represented controls cover numeric entry, power/input selection, navigation/menu, channel/volume, DVR/media transport, teletext/EPG/application keys.

## Important APIs, Types, and Functions

- `struct rc_map_table digittrade[]` is the static scan-code-to-keycode table.
- `struct rc_map_list digittrade_map` publishes `.scan = digittrade`, `.size = ARRAY_SIZE(digittrade)`, `.rc_proto = RC_PROTO_NEC`, and `.name = RC_MAP_DIGITTRADE` to rc-core.
- The module init function calls `rc_map_register()` and the exit function calls `rc_map_unregister()`, so the map is visible to rc-core only while the object is built in or the module is loaded.
- It has normal `module_init()`/`module_exit()` hooks.

## Control Flow

There is no active decode algorithm in this file. At build or module-load time, the map is registered with the rc-core map registry. A receiver driver later sets an `rc_dev->map_name` matching `RC_MAP_DIGITTRADE` or userspace selects that map with tooling such as `ir-keytable`; rc-core then looks up decoded scancodes in `digittrade` and emits the associated input keycodes. Unload or rc-core teardown unregisters the map, after which new lookups by name should fail or fall back to another configured map.

## State and Persistence Behavior

The persistent state is the compiled static table plus the registry node in rc-core. The file does not allocate per-device memory, take locks, touch hardware, or persist user settings. Runtime key state, repeat filtering, protocol decoding, and user remaps live in rc-core, the receiver driver, and input/ir-keytable configuration rather than in this keymap source.

## Dependencies and Integration Points

The file depends on `media/rc-map.h`, `linux/module.h`, Linux input `KEY_*` definitions, the `RC_MAP_*` string namespace, and the protocol enum `RC_PROTO_NEC`. It is built through `drivers/media/rc/keymaps/Makefile` when `CONFIG_RC_MAP` is enabled, except for CEC-style integration if noted above. Board, USB, PCI, CEC, or platform IR drivers integrate with it by naming `RC_MAP_DIGITTRADE` as their default map.

## Risks and Edge Cases

Incorrect scancodes, wrong `KEY_*` assignments, a mismatched `.rc_proto`, or a stale `.name` break user-visible remote buttons without producing compile errors. The declared protocol `RC_PROTO_NEC` tells rc-core which decoded scancode namespace this map expects. Table ordering is not semantically important for lookups, but duplicate or vendor-overloaded scancodes should be reviewed carefully. The map can also drift from the v4l-utils userspace copy, causing different behavior between built-in maps and maps loaded from userspace.

## Test Signals

Useful checks include compiling the keymap with `CONFIG_RC_MAP=y` and `=m`, loading/unloading the generated module where applicable, confirming `rc_map_register()` exposes `RC_MAP_DIGITTRADE`, using `ir-keytable -r` or equivalent rc-core introspection to inspect the map, and pressing representative numeric, navigation, volume/channel, power, and media keys on the target remote. Protocol-specific tests should verify that decoded `RC_PROTO_NEC` scancodes match the table values and that unknown buttons do not alias to unsafe actions such as power or record.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-digittrade.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-dm1105-nec.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-dm1105-nec.c

## Purpose

`rc-dm1105-nec.c` provides the `RC_MAP_DM1105_NEC` remote-controller keymap for `dm1105-nec remote controller keytable`. It is a data-only rc-core map: decoded remote-control scan codes are translated into Linux input `KEY_*` events for the bundled receiver or board driver. The table has 31 scan-code entries; early entries include `0x0a->KEY_POWER2`, `0x0c->KEY_MUTE`, `0x11->KEY_NUMERIC_1`, `0x12->KEY_NUMERIC_2`, `0x13->KEY_NUMERIC_3`, `0x14->KEY_NUMERIC_4`. The represented controls cover numeric entry, power/input selection, navigation/menu, channel/volume, DVR/media transport.

## Important APIs, Types, and Functions

- `struct rc_map_table dm1105_nec[]` is the static scan-code-to-keycode table.
- `struct rc_map_list dm1105_nec_map` publishes `.scan = dm1105_nec`, `.size = ARRAY_SIZE(dm1105_nec)`, `.rc_proto = RC_PROTO_UNKNOWN`, and `.name = RC_MAP_DM1105_NEC` to rc-core.
- The module init function calls `rc_map_register()` and the exit function calls `rc_map_unregister()`, so the map is visible to rc-core only while the object is built in or the module is loaded.
- It has normal `module_init()`/`module_exit()` hooks.

## Control Flow

There is no active decode algorithm in this file. At build or module-load time, the map is registered with the rc-core map registry. A receiver driver later sets an `rc_dev->map_name` matching `RC_MAP_DM1105_NEC` or userspace selects that map with tooling such as `ir-keytable`; rc-core then looks up decoded scancodes in `dm1105_nec` and emits the associated input keycodes. Unload or rc-core teardown unregisters the map, after which new lookups by name should fail or fall back to another configured map.

## State and Persistence Behavior

The persistent state is the compiled static table plus the registry node in rc-core. The file does not allocate per-device memory, take locks, touch hardware, or persist user settings. Runtime key state, repeat filtering, protocol decoding, and user remaps live in rc-core, the receiver driver, and input/ir-keytable configuration rather than in this keymap source.

## Dependencies and Integration Points

The file depends on `media/rc-map.h`, `linux/module.h`, Linux input `KEY_*` definitions, the `RC_MAP_*` string namespace, and the protocol enum `RC_PROTO_UNKNOWN`. It is built through `drivers/media/rc/keymaps/Makefile` when `CONFIG_RC_MAP` is enabled, except for CEC-style integration if noted above. Board, USB, PCI, CEC, or platform IR drivers integrate with it by naming `RC_MAP_DM1105_NEC` as their default map.

## Risks and Edge Cases

Incorrect scancodes, wrong `KEY_*` assignments, a mismatched `.rc_proto`, or a stale `.name` break user-visible remote buttons without producing compile errors. Because the protocol is `RC_PROTO_UNKNOWN`, correctness depends on the consuming hardware driver or legacy decoder path supplying matching scancodes. Table ordering is not semantically important for lookups, but duplicate or vendor-overloaded scancodes should be reviewed carefully. The map can also drift from the v4l-utils userspace copy, causing different behavior between built-in maps and maps loaded from userspace.

## Test Signals

Useful checks include compiling the keymap with `CONFIG_RC_MAP=y` and `=m`, loading/unloading the generated module where applicable, confirming `rc_map_register()` exposes `RC_MAP_DM1105_NEC`, using `ir-keytable -r` or equivalent rc-core introspection to inspect the map, and pressing representative numeric, navigation, volume/channel, power, and media keys on the target remote. Protocol-specific tests should verify that decoded `RC_PROTO_UNKNOWN` scancodes match the table values and that unknown buttons do not alias to unsafe actions such as power or record.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-dm1105-nec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-dntv-live-dvb-t.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-dntv-live-dvb-t.c

## Purpose

`rc-dntv-live-dvb-t.c` provides the `RC_MAP_DNTV_LIVE_DVB_T` remote-controller keymap for `dntv-live-dvb-t remote controller keytable`. It is a data-only rc-core map: decoded remote-control scan codes are translated into Linux input `KEY_*` events for the bundled receiver or board driver. The table has 32 scan-code entries; early entries include `0x00->KEY_ESC`, `0x0a->KEY_NUMERIC_0`, `0x01->KEY_NUMERIC_1`, `0x02->KEY_NUMERIC_2`, `0x03->KEY_NUMERIC_3`, `0x04->KEY_NUMERIC_4`. The represented controls cover numeric entry, power/input selection, navigation/menu, channel/volume, DVR/media transport, teletext/EPG/application keys.

## Important APIs, Types, and Functions

- `struct rc_map_table dntv_live_dvb_t[]` is the static scan-code-to-keycode table.
- `struct rc_map_list dntv_live_dvb_t_map` publishes `.scan = dntv_live_dvb_t`, `.size = ARRAY_SIZE(dntv_live_dvb_t)`, `.rc_proto = RC_PROTO_UNKNOWN`, and `.name = RC_MAP_DNTV_LIVE_DVB_T` to rc-core.
- The module init function calls `rc_map_register()` and the exit function calls `rc_map_unregister()`, so the map is visible to rc-core only while the object is built in or the module is loaded.
- It has normal `module_init()`/`module_exit()` hooks.

## Control Flow

There is no active decode algorithm in this file. At build or module-load time, the map is registered with the rc-core map registry. A receiver driver later sets an `rc_dev->map_name` matching `RC_MAP_DNTV_LIVE_DVB_T` or userspace selects that map with tooling such as `ir-keytable`; rc-core then looks up decoded scancodes in `dntv_live_dvb_t` and emits the associated input keycodes. Unload or rc-core teardown unregisters the map, after which new lookups by name should fail or fall back to another configured map.

## State and Persistence Behavior

The persistent state is the compiled static table plus the registry node in rc-core. The file does not allocate per-device memory, take locks, touch hardware, or persist user settings. Runtime key state, repeat filtering, protocol decoding, and user remaps live in rc-core, the receiver driver, and input/ir-keytable configuration rather than in this keymap source.

## Dependencies and Integration Points

The file depends on `media/rc-map.h`, `linux/module.h`, Linux input `KEY_*` definitions, the `RC_MAP_*` string namespace, and the protocol enum `RC_PROTO_UNKNOWN`. It is built through `drivers/media/rc/keymaps/Makefile` when `CONFIG_RC_MAP` is enabled, except for CEC-style integration if noted above. Board, USB, PCI, CEC, or platform IR drivers integrate with it by naming `RC_MAP_DNTV_LIVE_DVB_T` as their default map.

## Risks and Edge Cases

Incorrect scancodes, wrong `KEY_*` assignments, a mismatched `.rc_proto`, or a stale `.name` break user-visible remote buttons without producing compile errors. Because the protocol is `RC_PROTO_UNKNOWN`, correctness depends on the consuming hardware driver or legacy decoder path supplying matching scancodes. Table ordering is not semantically important for lookups, but duplicate or vendor-overloaded scancodes should be reviewed carefully. The map can also drift from the v4l-utils userspace copy, causing different behavior between built-in maps and maps loaded from userspace.

## Test Signals

Useful checks include compiling the keymap with `CONFIG_RC_MAP=y` and `=m`, loading/unloading the generated module where applicable, confirming `rc_map_register()` exposes `RC_MAP_DNTV_LIVE_DVB_T`, using `ir-keytable -r` or equivalent rc-core introspection to inspect the map, and pressing representative numeric, navigation, volume/channel, power, and media keys on the target remote. Protocol-specific tests should verify that decoded `RC_PROTO_UNKNOWN` scancodes match the table values and that unknown buttons do not alias to unsafe actions such as power or record.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-dntv-live-dvb-t.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-dntv-live-dvbt-pro.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-dntv-live-dvbt-pro.c

## Purpose

`rc-dntv-live-dvbt-pro.c` provides the `RC_MAP_DNTV_LIVE_DVBT_PRO` remote-controller keymap for `DigitalNow DNTV Live DVB-T Remote controller keytable`. It is a data-only rc-core map: decoded remote-control scan codes are translated into Linux input `KEY_*` events for the bundled receiver or board driver. The table has 53 scan-code entries; early entries include `0x16->KEY_POWER`, `0x5b->KEY_HOME`, `0x55->KEY_TV`, `0x58->KEY_TUNER`, `0x5a->KEY_RADIO`, `0x59->KEY_DVD`. The represented controls cover numeric entry, power/input selection, navigation/menu, channel/volume, DVR/media transport, colored function keys, teletext/EPG/application keys.

## Important APIs, Types, and Functions

- `struct rc_map_table dntv_live_dvbt_pro[]` is the static scan-code-to-keycode table.
- `struct rc_map_list dntv_live_dvbt_pro_map` publishes `.scan = dntv_live_dvbt_pro`, `.size = ARRAY_SIZE(dntv_live_dvbt_pro)`, `.rc_proto = RC_PROTO_UNKNOWN`, and `.name = RC_MAP_DNTV_LIVE_DVBT_PRO` to rc-core.
- The module init function calls `rc_map_register()` and the exit function calls `rc_map_unregister()`, so the map is visible to rc-core only while the object is built in or the module is loaded.
- It has normal `module_init()`/`module_exit()` hooks.

## Control Flow

There is no active decode algorithm in this file. At build or module-load time, the map is registered with the rc-core map registry. A receiver driver later sets an `rc_dev->map_name` matching `RC_MAP_DNTV_LIVE_DVBT_PRO` or userspace selects that map with tooling such as `ir-keytable`; rc-core then looks up decoded scancodes in `dntv_live_dvbt_pro` and emits the associated input keycodes. Unload or rc-core teardown unregisters the map, after which new lookups by name should fail or fall back to another configured map.

## State and Persistence Behavior

The persistent state is the compiled static table plus the registry node in rc-core. The file does not allocate per-device memory, take locks, touch hardware, or persist user settings. Runtime key state, repeat filtering, protocol decoding, and user remaps live in rc-core, the receiver driver, and input/ir-keytable configuration rather than in this keymap source.

## Dependencies and Integration Points

The file depends on `media/rc-map.h`, `linux/module.h`, Linux input `KEY_*` definitions, the `RC_MAP_*` string namespace, and the protocol enum `RC_PROTO_UNKNOWN`. It is built through `drivers/media/rc/keymaps/Makefile` when `CONFIG_RC_MAP` is enabled, except for CEC-style integration if noted above. Board, USB, PCI, CEC, or platform IR drivers integrate with it by naming `RC_MAP_DNTV_LIVE_DVBT_PRO` as their default map.

## Risks and Edge Cases

Incorrect scancodes, wrong `KEY_*` assignments, a mismatched `.rc_proto`, or a stale `.name` break user-visible remote buttons without producing compile errors. Because the protocol is `RC_PROTO_UNKNOWN`, correctness depends on the consuming hardware driver or legacy decoder path supplying matching scancodes. Table ordering is not semantically important for lookups, but duplicate or vendor-overloaded scancodes should be reviewed carefully. The map can also drift from the v4l-utils userspace copy, causing different behavior between built-in maps and maps loaded from userspace.

## Test Signals

Useful checks include compiling the keymap with `CONFIG_RC_MAP=y` and `=m`, loading/unloading the generated module where applicable, confirming `rc_map_register()` exposes `RC_MAP_DNTV_LIVE_DVBT_PRO`, using `ir-keytable -r` or equivalent rc-core introspection to inspect the map, and pressing representative numeric, navigation, volume/channel, power, and media keys on the target remote. Protocol-specific tests should verify that decoded `RC_PROTO_UNKNOWN` scancodes match the table values and that unknown buttons do not alias to unsafe actions such as power or record.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-dntv-live-dvbt-pro.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-dreambox.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-dreambox.c

## Purpose

`rc-dreambox.c` provides the `RC_MAP_DREAMBOX` remote-controller keymap for `Dreambox RC10/RC0 and RC20/RC-BT remote controller keytable`. It is a data-only rc-core map: decoded remote-control scan codes are translated into Linux input `KEY_*` events for the bundled receiver or board driver. The table has 80 scan-code entries; early entries include `0x3200->KEY_POWER`, `0x3290->KEY_HELP`, `0x3201->KEY_1`, `0x3202->KEY_2`, `0x3203->KEY_3`, `0x3204->KEY_4`. The represented controls cover numeric entry, power/input selection, navigation/menu, channel/volume, DVR/media transport, colored function keys, teletext/EPG/application keys.

## Important APIs, Types, and Functions

- `struct rc_map_table dreambox[]` is the static scan-code-to-keycode table.
- `struct rc_map_list dreambox_map` publishes `.scan = dreambox`, `.size = ARRAY_SIZE(dreambox)`, `.rc_proto = RC_PROTO_NEC`, and `.name = RC_MAP_DREAMBOX` to rc-core.
- The module init function calls `rc_map_register()` and the exit function calls `rc_map_unregister()`, so the map is visible to rc-core only while the object is built in or the module is loaded.
- It has normal `module_init()`/`module_exit()` hooks.

## Control Flow

There is no active decode algorithm in this file. At build or module-load time, the map is registered with the rc-core map registry. A receiver driver later sets an `rc_dev->map_name` matching `RC_MAP_DREAMBOX` or userspace selects that map with tooling such as `ir-keytable`; rc-core then looks up decoded scancodes in `dreambox` and emits the associated input keycodes. Unload or rc-core teardown unregisters the map, after which new lookups by name should fail or fall back to another configured map.

## State and Persistence Behavior

The persistent state is the compiled static table plus the registry node in rc-core. The file does not allocate per-device memory, take locks, touch hardware, or persist user settings. Runtime key state, repeat filtering, protocol decoding, and user remaps live in rc-core, the receiver driver, and input/ir-keytable configuration rather than in this keymap source.

## Dependencies and Integration Points

The file depends on `media/rc-map.h`, `linux/module.h`, Linux input `KEY_*` definitions, the `RC_MAP_*` string namespace, and the protocol enum `RC_PROTO_NEC`. It is built through `drivers/media/rc/keymaps/Makefile` when `CONFIG_RC_MAP` is enabled, except for CEC-style integration if noted above. Board, USB, PCI, CEC, or platform IR drivers integrate with it by naming `RC_MAP_DREAMBOX` as their default map.

## Risks and Edge Cases

Incorrect scancodes, wrong `KEY_*` assignments, a mismatched `.rc_proto`, or a stale `.name` break user-visible remote buttons without producing compile errors. The declared protocol `RC_PROTO_NEC` tells rc-core which decoded scancode namespace this map expects. Table ordering is not semantically important for lookups, but duplicate or vendor-overloaded scancodes should be reviewed carefully. The map can also drift from the v4l-utils userspace copy, causing different behavior between built-in maps and maps loaded from userspace.

## Test Signals

Useful checks include compiling the keymap with `CONFIG_RC_MAP=y` and `=m`, loading/unloading the generated module where applicable, confirming `rc_map_register()` exposes `RC_MAP_DREAMBOX`, using `ir-keytable -r` or equivalent rc-core introspection to inspect the map, and pressing representative numeric, navigation, volume/channel, power, and media keys on the target remote. Protocol-specific tests should verify that decoded `RC_PROTO_NEC` scancodes match the table values and that unknown buttons do not alias to unsafe actions such as power or record.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-dreambox.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-dtt200u.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-dtt200u.c

## Purpose

`rc-dtt200u.c` provides the `RC_MAP_DTT200U` remote-controller keymap for `Wideview WT-220U remote controller keytable`. It is a data-only rc-core map: decoded remote-control scan codes are translated into Linux input `KEY_*` events for the bundled receiver or board driver. The table has 18 scan-code entries; early entries include `0x8001->KEY_MUTE`, `0x8002->KEY_CHANNELDOWN`, `0x8003->KEY_VOLUMEDOWN`, `0x8004->KEY_NUMERIC_1`, `0x8005->KEY_NUMERIC_2`, `0x8006->KEY_NUMERIC_3`. The represented controls cover numeric entry, power/input selection, navigation/menu, channel/volume.

## Important APIs, Types, and Functions

- `struct rc_map_table dtt200u_table[]` is the static scan-code-to-keycode table.
- `struct rc_map_list dtt200u_map` publishes `.scan = dtt200u_table`, `.size = ARRAY_SIZE(dtt200u_table)`, `.rc_proto = RC_PROTO_NEC`, and `.name = RC_MAP_DTT200U` to rc-core.
- The module init function calls `rc_map_register()` and the exit function calls `rc_map_unregister()`, so the map is visible to rc-core only while the object is built in or the module is loaded.
- It has normal `module_init()`/`module_exit()` hooks.

## Control Flow

There is no active decode algorithm in this file. At build or module-load time, the map is registered with the rc-core map registry. A receiver driver later sets an `rc_dev->map_name` matching `RC_MAP_DTT200U` or userspace selects that map with tooling such as `ir-keytable`; rc-core then looks up decoded scancodes in `dtt200u_table` and emits the associated input keycodes. Unload or rc-core teardown unregisters the map, after which new lookups by name should fail or fall back to another configured map.

## State and Persistence Behavior

The persistent state is the compiled static table plus the registry node in rc-core. The file does not allocate per-device memory, take locks, touch hardware, or persist user settings. Runtime key state, repeat filtering, protocol decoding, and user remaps live in rc-core, the receiver driver, and input/ir-keytable configuration rather than in this keymap source.

## Dependencies and Integration Points

The file depends on `media/rc-map.h`, `linux/module.h`, Linux input `KEY_*` definitions, the `RC_MAP_*` string namespace, and the protocol enum `RC_PROTO_NEC`. It is built through `drivers/media/rc/keymaps/Makefile` when `CONFIG_RC_MAP` is enabled, except for CEC-style integration if noted above. Board, USB, PCI, CEC, or platform IR drivers integrate with it by naming `RC_MAP_DTT200U` as their default map.

## Risks and Edge Cases

Incorrect scancodes, wrong `KEY_*` assignments, a mismatched `.rc_proto`, or a stale `.name` break user-visible remote buttons without producing compile errors. The declared protocol `RC_PROTO_NEC` tells rc-core which decoded scancode namespace this map expects. Table ordering is not semantically important for lookups, but duplicate or vendor-overloaded scancodes should be reviewed carefully. The map can also drift from the v4l-utils userspace copy, causing different behavior between built-in maps and maps loaded from userspace.

## Test Signals

Useful checks include compiling the keymap with `CONFIG_RC_MAP=y` and `=m`, loading/unloading the generated module where applicable, confirming `rc_map_register()` exposes `RC_MAP_DTT200U`, using `ir-keytable -r` or equivalent rc-core introspection to inspect the map, and pressing representative numeric, navigation, volume/channel, power, and media keys on the target remote. Protocol-specific tests should verify that decoded `RC_PROTO_NEC` scancodes match the table values and that unknown buttons do not alias to unsafe actions such as power or record.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-dtt200u.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-dvbsky.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-dvbsky.c

## Purpose

`rc-dvbsky.c` provides the `RC_MAP_DVBSKY` remote-controller keymap for `DVBSky remote controller keytable`. It is a data-only rc-core map: decoded remote-control scan codes are translated into Linux input `KEY_*` events for the bundled receiver or board driver. The table has 32 scan-code entries; early entries include `0x0000->KEY_NUMERIC_0`, `0x0001->KEY_NUMERIC_1`, `0x0002->KEY_NUMERIC_2`, `0x0003->KEY_NUMERIC_3`, `0x0004->KEY_NUMERIC_4`, `0x0005->KEY_NUMERIC_5`. The represented controls cover numeric entry, power/input selection, navigation/menu, channel/volume, DVR/media transport, teletext/EPG/application keys.

## Important APIs, Types, and Functions

- `struct rc_map_table rc5_dvbsky[]` is the static scan-code-to-keycode table.
- `struct rc_map_list rc5_dvbsky_map` publishes `.scan = rc5_dvbsky`, `.size = ARRAY_SIZE(rc5_dvbsky)`, `.rc_proto = RC_PROTO_RC5`, and `.name = RC_MAP_DVBSKY` to rc-core.
- The module init function calls `rc_map_register()` and the exit function calls `rc_map_unregister()`, so the map is visible to rc-core only while the object is built in or the module is loaded.
- It has normal `module_init()`/`module_exit()` hooks.

## Control Flow

There is no active decode algorithm in this file. At build or module-load time, the map is registered with the rc-core map registry. A receiver driver later sets an `rc_dev->map_name` matching `RC_MAP_DVBSKY` or userspace selects that map with tooling such as `ir-keytable`; rc-core then looks up decoded scancodes in `rc5_dvbsky` and emits the associated input keycodes. Unload or rc-core teardown unregisters the map, after which new lookups by name should fail or fall back to another configured map.

## State and Persistence Behavior

The persistent state is the compiled static table plus the registry node in rc-core. The file does not allocate per-device memory, take locks, touch hardware, or persist user settings. Runtime key state, repeat filtering, protocol decoding, and user remaps live in rc-core, the receiver driver, and input/ir-keytable configuration rather than in this keymap source.

## Dependencies and Integration Points

The file depends on `media/rc-map.h`, `linux/module.h`, Linux input `KEY_*` definitions, the `RC_MAP_*` string namespace, and the protocol enum `RC_PROTO_RC5`. It is built through `drivers/media/rc/keymaps/Makefile` when `CONFIG_RC_MAP` is enabled, except for CEC-style integration if noted above. Board, USB, PCI, CEC, or platform IR drivers integrate with it by naming `RC_MAP_DVBSKY` as their default map.

## Risks and Edge Cases

Incorrect scancodes, wrong `KEY_*` assignments, a mismatched `.rc_proto`, or a stale `.name` break user-visible remote buttons without producing compile errors. The declared protocol `RC_PROTO_RC5` tells rc-core which decoded scancode namespace this map expects. Table ordering is not semantically important for lookups, but duplicate or vendor-overloaded scancodes should be reviewed carefully. The map can also drift from the v4l-utils userspace copy, causing different behavior between built-in maps and maps loaded from userspace.

## Test Signals

Useful checks include compiling the keymap with `CONFIG_RC_MAP=y` and `=m`, loading/unloading the generated module where applicable, confirming `rc_map_register()` exposes `RC_MAP_DVBSKY`, using `ir-keytable -r` or equivalent rc-core introspection to inspect the map, and pressing representative numeric, navigation, volume/channel, power, and media keys on the target remote. Protocol-specific tests should verify that decoded `RC_PROTO_RC5` scancodes match the table values and that unknown buttons do not alias to unsafe actions such as power or record.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-dvbsky.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-dvico-mce.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-dvico-mce.c

## Purpose

`rc-dvico-mce.c` provides the `RC_MAP_DVICO_MCE` remote-controller keymap for `dvico-mce remote controller keytable`. It is a data-only rc-core map: decoded remote-control scan codes are translated into Linux input `KEY_*` events for the bundled receiver or board driver. The table has 45 scan-code entries; early entries include `0x0102->KEY_TV`, `0x010e->KEY_MP3`, `0x011a->KEY_DVD`, `0x011e->KEY_FAVORITES`, `0x0116->KEY_SETUP`, `0x0146->KEY_POWER2`. The represented controls cover numeric entry, power/input selection, navigation/menu, channel/volume, DVR/media transport, teletext/EPG/application keys.

## Important APIs, Types, and Functions

- `struct rc_map_table rc_map_dvico_mce_table[]` is the static scan-code-to-keycode table.
- `struct rc_map_list dvico_mce_map` publishes `.scan = rc_map_dvico_mce_table`, `.size = ARRAY_SIZE(rc_map_dvico_mce_table)`, `.rc_proto = RC_PROTO_NEC`, and `.name = RC_MAP_DVICO_MCE` to rc-core.
- The module init function calls `rc_map_register()` and the exit function calls `rc_map_unregister()`, so the map is visible to rc-core only while the object is built in or the module is loaded.
- It has normal `module_init()`/`module_exit()` hooks.

## Control Flow

There is no active decode algorithm in this file. At build or module-load time, the map is registered with the rc-core map registry. A receiver driver later sets an `rc_dev->map_name` matching `RC_MAP_DVICO_MCE` or userspace selects that map with tooling such as `ir-keytable`; rc-core then looks up decoded scancodes in `rc_map_dvico_mce_table` and emits the associated input keycodes. Unload or rc-core teardown unregisters the map, after which new lookups by name should fail or fall back to another configured map.

## State and Persistence Behavior

The persistent state is the compiled static table plus the registry node in rc-core. The file does not allocate per-device memory, take locks, touch hardware, or persist user settings. Runtime key state, repeat filtering, protocol decoding, and user remaps live in rc-core, the receiver driver, and input/ir-keytable configuration rather than in this keymap source.

## Dependencies and Integration Points

The file depends on `media/rc-map.h`, `linux/module.h`, Linux input `KEY_*` definitions, the `RC_MAP_*` string namespace, and the protocol enum `RC_PROTO_NEC`. It is built through `drivers/media/rc/keymaps/Makefile` when `CONFIG_RC_MAP` is enabled, except for CEC-style integration if noted above. Board, USB, PCI, CEC, or platform IR drivers integrate with it by naming `RC_MAP_DVICO_MCE` as their default map.

## Risks and Edge Cases

Incorrect scancodes, wrong `KEY_*` assignments, a mismatched `.rc_proto`, or a stale `.name` break user-visible remote buttons without producing compile errors. The declared protocol `RC_PROTO_NEC` tells rc-core which decoded scancode namespace this map expects. Table ordering is not semantically important for lookups, but duplicate or vendor-overloaded scancodes should be reviewed carefully. The map can also drift from the v4l-utils userspace copy, causing different behavior between built-in maps and maps loaded from userspace.

## Test Signals

Useful checks include compiling the keymap with `CONFIG_RC_MAP=y` and `=m`, loading/unloading the generated module where applicable, confirming `rc_map_register()` exposes `RC_MAP_DVICO_MCE`, using `ir-keytable -r` or equivalent rc-core introspection to inspect the map, and pressing representative numeric, navigation, volume/channel, power, and media keys on the target remote. Protocol-specific tests should verify that decoded `RC_PROTO_NEC` scancodes match the table values and that unknown buttons do not alias to unsafe actions such as power or record.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-dvico-mce.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-dvico-portable.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-dvico-portable.c

## Purpose

`rc-dvico-portable.c` provides the `RC_MAP_DVICO_PORTABLE` remote-controller keymap for `dvico-portable remote controller keytable`. It is a data-only rc-core map: decoded remote-control scan codes are translated into Linux input `KEY_*` events for the bundled receiver or board driver. The table has 36 scan-code entries; early entries include `0x0302->KEY_SETUP`, `0x0343->KEY_POWER2`, `0x0306->KEY_EPG`, `0x035a->KEY_BACK`, `0x0305->KEY_MENU`, `0x0347->KEY_INFO`. The represented controls cover numeric entry, power/input selection, navigation/menu, channel/volume, DVR/media transport, teletext/EPG/application keys.

## Important APIs, Types, and Functions

- `struct rc_map_table rc_map_dvico_portable_table[]` is the static scan-code-to-keycode table.
- `struct rc_map_list dvico_portable_map` publishes `.scan = rc_map_dvico_portable_table`, `.size = ARRAY_SIZE(rc_map_dvico_portable_table)`, `.rc_proto = RC_PROTO_NEC`, and `.name = RC_MAP_DVICO_PORTABLE` to rc-core.
- The module init function calls `rc_map_register()` and the exit function calls `rc_map_unregister()`, so the map is visible to rc-core only while the object is built in or the module is loaded.
- It has normal `module_init()`/`module_exit()` hooks.

## Control Flow

There is no active decode algorithm in this file. At build or module-load time, the map is registered with the rc-core map registry. A receiver driver later sets an `rc_dev->map_name` matching `RC_MAP_DVICO_PORTABLE` or userspace selects that map with tooling such as `ir-keytable`; rc-core then looks up decoded scancodes in `rc_map_dvico_portable_table` and emits the associated input keycodes. Unload or rc-core teardown unregisters the map, after which new lookups by name should fail or fall back to another configured map.

## State and Persistence Behavior

The persistent state is the compiled static table plus the registry node in rc-core. The file does not allocate per-device memory, take locks, touch hardware, or persist user settings. Runtime key state, repeat filtering, protocol decoding, and user remaps live in rc-core, the receiver driver, and input/ir-keytable configuration rather than in this keymap source.

## Dependencies and Integration Points

The file depends on `media/rc-map.h`, `linux/module.h`, Linux input `KEY_*` definitions, the `RC_MAP_*` string namespace, and the protocol enum `RC_PROTO_NEC`. It is built through `drivers/media/rc/keymaps/Makefile` when `CONFIG_RC_MAP` is enabled, except for CEC-style integration if noted above. Board, USB, PCI, CEC, or platform IR drivers integrate with it by naming `RC_MAP_DVICO_PORTABLE` as their default map.

## Risks and Edge Cases

Incorrect scancodes, wrong `KEY_*` assignments, a mismatched `.rc_proto`, or a stale `.name` break user-visible remote buttons without producing compile errors. The declared protocol `RC_PROTO_NEC` tells rc-core which decoded scancode namespace this map expects. Table ordering is not semantically important for lookups, but duplicate or vendor-overloaded scancodes should be reviewed carefully. The map can also drift from the v4l-utils userspace copy, causing different behavior between built-in maps and maps loaded from userspace.

## Test Signals

Useful checks include compiling the keymap with `CONFIG_RC_MAP=y` and `=m`, loading/unloading the generated module where applicable, confirming `rc_map_register()` exposes `RC_MAP_DVICO_PORTABLE`, using `ir-keytable -r` or equivalent rc-core introspection to inspect the map, and pressing representative numeric, navigation, volume/channel, power, and media keys on the target remote. Protocol-specific tests should verify that decoded `RC_PROTO_NEC` scancodes match the table values and that unknown buttons do not alias to unsafe actions such as power or record.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-dvico-portable.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-em-terratec.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-em-terratec.c

## Purpose

`rc-em-terratec.c` provides the `RC_MAP_EM_TERRATEC` remote-controller keymap for `em-terratec remote controller keytable`. It is a data-only rc-core map: decoded remote-control scan codes are translated into Linux input `KEY_*` events for the bundled receiver or board driver. The table has 28 scan-code entries; early entries include `0x01->KEY_CHANNEL`, `0x02->KEY_SELECT`, `0x03->KEY_MUTE`, `0x04->KEY_POWER`, `0x05->KEY_NUMERIC_1`, `0x06->KEY_NUMERIC_2`. The represented controls cover numeric entry, power/input selection, navigation/menu, channel/volume, DVR/media transport.

## Important APIs, Types, and Functions

- `struct rc_map_table em_terratec[]` is the static scan-code-to-keycode table.
- `struct rc_map_list em_terratec_map` publishes `.scan = em_terratec`, `.size = ARRAY_SIZE(em_terratec)`, `.rc_proto = RC_PROTO_UNKNOWN`, and `.name = RC_MAP_EM_TERRATEC` to rc-core.
- The module init function calls `rc_map_register()` and the exit function calls `rc_map_unregister()`, so the map is visible to rc-core only while the object is built in or the module is loaded.
- It has normal `module_init()`/`module_exit()` hooks.

## Control Flow

There is no active decode algorithm in this file. At build or module-load time, the map is registered with the rc-core map registry. A receiver driver later sets an `rc_dev->map_name` matching `RC_MAP_EM_TERRATEC` or userspace selects that map with tooling such as `ir-keytable`; rc-core then looks up decoded scancodes in `em_terratec` and emits the associated input keycodes. Unload or rc-core teardown unregisters the map, after which new lookups by name should fail or fall back to another configured map.

## State and Persistence Behavior

The persistent state is the compiled static table plus the registry node in rc-core. The file does not allocate per-device memory, take locks, touch hardware, or persist user settings. Runtime key state, repeat filtering, protocol decoding, and user remaps live in rc-core, the receiver driver, and input/ir-keytable configuration rather than in this keymap source.

## Dependencies and Integration Points

The file depends on `media/rc-map.h`, `linux/module.h`, Linux input `KEY_*` definitions, the `RC_MAP_*` string namespace, and the protocol enum `RC_PROTO_UNKNOWN`. It is built through `drivers/media/rc/keymaps/Makefile` when `CONFIG_RC_MAP` is enabled, except for CEC-style integration if noted above. Board, USB, PCI, CEC, or platform IR drivers integrate with it by naming `RC_MAP_EM_TERRATEC` as their default map.

## Risks and Edge Cases

Incorrect scancodes, wrong `KEY_*` assignments, a mismatched `.rc_proto`, or a stale `.name` break user-visible remote buttons without producing compile errors. Because the protocol is `RC_PROTO_UNKNOWN`, correctness depends on the consuming hardware driver or legacy decoder path supplying matching scancodes. Table ordering is not semantically important for lookups, but duplicate or vendor-overloaded scancodes should be reviewed carefully. The map can also drift from the v4l-utils userspace copy, causing different behavior between built-in maps and maps loaded from userspace.

## Test Signals

Useful checks include compiling the keymap with `CONFIG_RC_MAP=y` and `=m`, loading/unloading the generated module where applicable, confirming `rc_map_register()` exposes `RC_MAP_EM_TERRATEC`, using `ir-keytable -r` or equivalent rc-core introspection to inspect the map, and pressing representative numeric, navigation, volume/channel, power, and media keys on the target remote. Protocol-specific tests should verify that decoded `RC_PROTO_UNKNOWN` scancodes match the table values and that unknown buttons do not alias to unsafe actions such as power or record.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-em-terratec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-encore-enltv-fm53.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-encore-enltv-fm53.c

## Purpose

`rc-encore-enltv-fm53.c` provides the `RC_MAP_ENCORE_ENLTV_FM53` remote-controller keymap for `Encore ENLTV-FM v5.3 remote controller keytable`. It is a data-only rc-core map: decoded remote-control scan codes are translated into Linux input `KEY_*` events for the bundled receiver or board driver. The table has 29 scan-code entries; early entries include `0x10->KEY_POWER2`, `0x06->KEY_MUTE`, `0x09->KEY_NUMERIC_1`, `0x1d->KEY_NUMERIC_2`, `0x1f->KEY_NUMERIC_3`, `0x19->KEY_NUMERIC_4`. The represented controls cover numeric entry, power/input selection, navigation/menu, channel/volume, DVR/media transport.

## Important APIs, Types, and Functions

- `struct rc_map_table encore_enltv_fm53[]` is the static scan-code-to-keycode table.
- `struct rc_map_list encore_enltv_fm53_map` publishes `.scan = encore_enltv_fm53`, `.size = ARRAY_SIZE(encore_enltv_fm53)`, `.rc_proto = RC_PROTO_UNKNOWN`, and `.name = RC_MAP_ENCORE_ENLTV_FM53` to rc-core.
- The module init function calls `rc_map_register()` and the exit function calls `rc_map_unregister()`, so the map is visible to rc-core only while the object is built in or the module is loaded.
- It has normal `module_init()`/`module_exit()` hooks.

## Control Flow

There is no active decode algorithm in this file. At build or module-load time, the map is registered with the rc-core map registry. A receiver driver later sets an `rc_dev->map_name` matching `RC_MAP_ENCORE_ENLTV_FM53` or userspace selects that map with tooling such as `ir-keytable`; rc-core then looks up decoded scancodes in `encore_enltv_fm53` and emits the associated input keycodes. Unload or rc-core teardown unregisters the map, after which new lookups by name should fail or fall back to another configured map.

## State and Persistence Behavior

The persistent state is the compiled static table plus the registry node in rc-core. The file does not allocate per-device memory, take locks, touch hardware, or persist user settings. Runtime key state, repeat filtering, protocol decoding, and user remaps live in rc-core, the receiver driver, and input/ir-keytable configuration rather than in this keymap source.

## Dependencies and Integration Points

The file depends on `media/rc-map.h`, `linux/module.h`, Linux input `KEY_*` definitions, the `RC_MAP_*` string namespace, and the protocol enum `RC_PROTO_UNKNOWN`. It is built through `drivers/media/rc/keymaps/Makefile` when `CONFIG_RC_MAP` is enabled, except for CEC-style integration if noted above. Board, USB, PCI, CEC, or platform IR drivers integrate with it by naming `RC_MAP_ENCORE_ENLTV_FM53` as their default map.

## Risks and Edge Cases

Incorrect scancodes, wrong `KEY_*` assignments, a mismatched `.rc_proto`, or a stale `.name` break user-visible remote buttons without producing compile errors. Because the protocol is `RC_PROTO_UNKNOWN`, correctness depends on the consuming hardware driver or legacy decoder path supplying matching scancodes. Table ordering is not semantically important for lookups, but duplicate or vendor-overloaded scancodes should be reviewed carefully. The map can also drift from the v4l-utils userspace copy, causing different behavior between built-in maps and maps loaded from userspace.

## Test Signals

Useful checks include compiling the keymap with `CONFIG_RC_MAP=y` and `=m`, loading/unloading the generated module where applicable, confirming `rc_map_register()` exposes `RC_MAP_ENCORE_ENLTV_FM53`, using `ir-keytable -r` or equivalent rc-core introspection to inspect the map, and pressing representative numeric, navigation, volume/channel, power, and media keys on the target remote. Protocol-specific tests should verify that decoded `RC_PROTO_UNKNOWN` scancodes match the table values and that unknown buttons do not alias to unsafe actions such as power or record.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-encore-enltv-fm53.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-encore-enltv.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-encore-enltv.c

## Purpose

`rc-encore-enltv.c` provides the `RC_MAP_ENCORE_ENLTV` remote-controller keymap for `Encore ENLTV-FM remote controller keytable`. It is a data-only rc-core map: decoded remote-control scan codes are translated into Linux input `KEY_*` events for the bundled receiver or board driver. The table has 52 scan-code entries; early entries include `0x0d->KEY_MUTE`, `0x1e->KEY_TV`, `0x00->KEY_VIDEO`, `0x01->KEY_AUDIO`, `0x02->KEY_CAMERA`, `0x1f->KEY_NUMERIC_1`. The represented controls cover numeric entry, power/input selection, navigation/menu, channel/volume, DVR/media transport, colored function keys, teletext/EPG/application keys.

## Important APIs, Types, and Functions

- `struct rc_map_table encore_enltv[]` is the static scan-code-to-keycode table.
- `struct rc_map_list encore_enltv_map` publishes `.scan = encore_enltv`, `.size = ARRAY_SIZE(encore_enltv)`, `.rc_proto = RC_PROTO_UNKNOWN`, and `.name = RC_MAP_ENCORE_ENLTV` to rc-core.
- The module init function calls `rc_map_register()` and the exit function calls `rc_map_unregister()`, so the map is visible to rc-core only while the object is built in or the module is loaded.
- It has normal `module_init()`/`module_exit()` hooks.

## Control Flow

There is no active decode algorithm in this file. At build or module-load time, the map is registered with the rc-core map registry. A receiver driver later sets an `rc_dev->map_name` matching `RC_MAP_ENCORE_ENLTV` or userspace selects that map with tooling such as `ir-keytable`; rc-core then looks up decoded scancodes in `encore_enltv` and emits the associated input keycodes. Unload or rc-core teardown unregisters the map, after which new lookups by name should fail or fall back to another configured map.

## State and Persistence Behavior

The persistent state is the compiled static table plus the registry node in rc-core. The file does not allocate per-device memory, take locks, touch hardware, or persist user settings. Runtime key state, repeat filtering, protocol decoding, and user remaps live in rc-core, the receiver driver, and input/ir-keytable configuration rather than in this keymap source.

## Dependencies and Integration Points

The file depends on `media/rc-map.h`, `linux/module.h`, Linux input `KEY_*` definitions, the `RC_MAP_*` string namespace, and the protocol enum `RC_PROTO_UNKNOWN`. It is built through `drivers/media/rc/keymaps/Makefile` when `CONFIG_RC_MAP` is enabled, except for CEC-style integration if noted above. Board, USB, PCI, CEC, or platform IR drivers integrate with it by naming `RC_MAP_ENCORE_ENLTV` as their default map.

## Risks and Edge Cases

Incorrect scancodes, wrong `KEY_*` assignments, a mismatched `.rc_proto`, or a stale `.name` break user-visible remote buttons without producing compile errors. Because the protocol is `RC_PROTO_UNKNOWN`, correctness depends on the consuming hardware driver or legacy decoder path supplying matching scancodes. Table ordering is not semantically important for lookups, but duplicate or vendor-overloaded scancodes should be reviewed carefully. The map can also drift from the v4l-utils userspace copy, causing different behavior between built-in maps and maps loaded from userspace.

## Test Signals

Useful checks include compiling the keymap with `CONFIG_RC_MAP=y` and `=m`, loading/unloading the generated module where applicable, confirming `rc_map_register()` exposes `RC_MAP_ENCORE_ENLTV`, using `ir-keytable -r` or equivalent rc-core introspection to inspect the map, and pressing representative numeric, navigation, volume/channel, power, and media keys on the target remote. Protocol-specific tests should verify that decoded `RC_PROTO_UNKNOWN` scancodes match the table values and that unknown buttons do not alias to unsafe actions such as power or record.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-encore-enltv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-encore-enltv2.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-encore-enltv2.c

## Purpose

`rc-encore-enltv2.c` provides the `RC_MAP_ENCORE_ENLTV2` remote-controller keymap for `Encore ENLTV2-FM remote controller keytable`. It is a data-only rc-core map: decoded remote-control scan codes are translated into Linux input `KEY_*` events for the bundled receiver or board driver. The table has 39 scan-code entries; early entries include `0x4c->KEY_POWER2`, `0x4a->KEY_TUNER`, `0x40->KEY_NUMERIC_1`, `0x60->KEY_NUMERIC_2`, `0x50->KEY_NUMERIC_3`, `0x70->KEY_NUMERIC_4`. The represented controls cover numeric entry, power/input selection, navigation/menu, channel/volume, DVR/media transport, teletext/EPG/application keys.

## Important APIs, Types, and Functions

- `struct rc_map_table encore_enltv2[]` is the static scan-code-to-keycode table.
- `struct rc_map_list encore_enltv2_map` publishes `.scan = encore_enltv2`, `.size = ARRAY_SIZE(encore_enltv2)`, `.rc_proto = RC_PROTO_UNKNOWN`, and `.name = RC_MAP_ENCORE_ENLTV2` to rc-core.
- The module init function calls `rc_map_register()` and the exit function calls `rc_map_unregister()`, so the map is visible to rc-core only while the object is built in or the module is loaded.
- It has normal `module_init()`/`module_exit()` hooks.

## Control Flow

There is no active decode algorithm in this file. At build or module-load time, the map is registered with the rc-core map registry. A receiver driver later sets an `rc_dev->map_name` matching `RC_MAP_ENCORE_ENLTV2` or userspace selects that map with tooling such as `ir-keytable`; rc-core then looks up decoded scancodes in `encore_enltv2` and emits the associated input keycodes. Unload or rc-core teardown unregisters the map, after which new lookups by name should fail or fall back to another configured map.

## State and Persistence Behavior

The persistent state is the compiled static table plus the registry node in rc-core. The file does not allocate per-device memory, take locks, touch hardware, or persist user settings. Runtime key state, repeat filtering, protocol decoding, and user remaps live in rc-core, the receiver driver, and input/ir-keytable configuration rather than in this keymap source.

## Dependencies and Integration Points

The file depends on `media/rc-map.h`, `linux/module.h`, Linux input `KEY_*` definitions, the `RC_MAP_*` string namespace, and the protocol enum `RC_PROTO_UNKNOWN`. It is built through `drivers/media/rc/keymaps/Makefile` when `CONFIG_RC_MAP` is enabled, except for CEC-style integration if noted above. Board, USB, PCI, CEC, or platform IR drivers integrate with it by naming `RC_MAP_ENCORE_ENLTV2` as their default map.

## Risks and Edge Cases

Incorrect scancodes, wrong `KEY_*` assignments, a mismatched `.rc_proto`, or a stale `.name` break user-visible remote buttons without producing compile errors. Because the protocol is `RC_PROTO_UNKNOWN`, correctness depends on the consuming hardware driver or legacy decoder path supplying matching scancodes. Table ordering is not semantically important for lookups, but duplicate or vendor-overloaded scancodes should be reviewed carefully. The map can also drift from the v4l-utils userspace copy, causing different behavior between built-in maps and maps loaded from userspace.

## Test Signals

Useful checks include compiling the keymap with `CONFIG_RC_MAP=y` and `=m`, loading/unloading the generated module where applicable, confirming `rc_map_register()` exposes `RC_MAP_ENCORE_ENLTV2`, using `ir-keytable -r` or equivalent rc-core introspection to inspect the map, and pressing representative numeric, navigation, volume/channel, power, and media keys on the target remote. Protocol-specific tests should verify that decoded `RC_PROTO_UNKNOWN` scancodes match the table values and that unknown buttons do not alias to unsafe actions such as power or record.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-encore-enltv2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-evga-indtube.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-evga-indtube.c

## Purpose

`rc-evga-indtube.c` provides the `RC_MAP_EVGA_INDTUBE` remote-controller keymap for `EVGA inDtube remote controller keytable`. It is a data-only rc-core map: decoded remote-control scan codes are translated into Linux input `KEY_*` events for the bundled receiver or board driver. The table has 16 scan-code entries; early entries include `0x12->KEY_POWER`, `0x02->KEY_MODE`, `0x14->KEY_MUTE`, `0x1a->KEY_CHANNELUP`, `0x16->KEY_TV2`, `0x1d->KEY_VOLUMEUP`. The represented controls cover power/input selection, channel/volume, DVR/media transport.

## Important APIs, Types, and Functions

- `struct rc_map_table evga_indtube[]` is the static scan-code-to-keycode table.
- `struct rc_map_list evga_indtube_map` publishes `.scan = evga_indtube`, `.size = ARRAY_SIZE(evga_indtube)`, `.rc_proto = RC_PROTO_UNKNOWN`, and `.name = RC_MAP_EVGA_INDTUBE` to rc-core.
- The module init function calls `rc_map_register()` and the exit function calls `rc_map_unregister()`, so the map is visible to rc-core only while the object is built in or the module is loaded.
- It has normal `module_init()`/`module_exit()` hooks.

## Control Flow

There is no active decode algorithm in this file. At build or module-load time, the map is registered with the rc-core map registry. A receiver driver later sets an `rc_dev->map_name` matching `RC_MAP_EVGA_INDTUBE` or userspace selects that map with tooling such as `ir-keytable`; rc-core then looks up decoded scancodes in `evga_indtube` and emits the associated input keycodes. Unload or rc-core teardown unregisters the map, after which new lookups by name should fail or fall back to another configured map.

## State and Persistence Behavior

The persistent state is the compiled static table plus the registry node in rc-core. The file does not allocate per-device memory, take locks, touch hardware, or persist user settings. Runtime key state, repeat filtering, protocol decoding, and user remaps live in rc-core, the receiver driver, and input/ir-keytable configuration rather than in this keymap source.

## Dependencies and Integration Points

The file depends on `media/rc-map.h`, `linux/module.h`, Linux input `KEY_*` definitions, the `RC_MAP_*` string namespace, and the protocol enum `RC_PROTO_UNKNOWN`. It is built through `drivers/media/rc/keymaps/Makefile` when `CONFIG_RC_MAP` is enabled, except for CEC-style integration if noted above. Board, USB, PCI, CEC, or platform IR drivers integrate with it by naming `RC_MAP_EVGA_INDTUBE` as their default map.

## Risks and Edge Cases

Incorrect scancodes, wrong `KEY_*` assignments, a mismatched `.rc_proto`, or a stale `.name` break user-visible remote buttons without producing compile errors. Because the protocol is `RC_PROTO_UNKNOWN`, correctness depends on the consuming hardware driver or legacy decoder path supplying matching scancodes. Table ordering is not semantically important for lookups, but duplicate or vendor-overloaded scancodes should be reviewed carefully. The map can also drift from the v4l-utils userspace copy, causing different behavior between built-in maps and maps loaded from userspace.

## Test Signals

Useful checks include compiling the keymap with `CONFIG_RC_MAP=y` and `=m`, loading/unloading the generated module where applicable, confirming `rc_map_register()` exposes `RC_MAP_EVGA_INDTUBE`, using `ir-keytable -r` or equivalent rc-core introspection to inspect the map, and pressing representative numeric, navigation, volume/channel, power, and media keys on the target remote. Protocol-specific tests should verify that decoded `RC_PROTO_UNKNOWN` scancodes match the table values and that unknown buttons do not alias to unsafe actions such as power or record.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-evga-indtube.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-eztv.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-eztv.c

## Purpose

`rc-eztv.c` provides the `RC_MAP_EZTV` remote-controller keymap for `eztv remote controller keytable`. It is a data-only rc-core map: decoded remote-control scan codes are translated into Linux input `KEY_*` events for the bundled receiver or board driver. The table has 44 scan-code entries; early entries include `0x12->KEY_POWER`, `0x01->KEY_TV`, `0x15->KEY_DVD`, `0x17->KEY_AUDIO`, `0x1b->KEY_MUTE`, `0x02->KEY_LANGUAGE`. The represented controls cover numeric entry, power/input selection, navigation/menu, channel/volume, DVR/media transport, teletext/EPG/application keys.

## Important APIs, Types, and Functions

- `struct rc_map_table eztv[]` is the static scan-code-to-keycode table.
- `struct rc_map_list eztv_map` publishes `.scan = eztv`, `.size = ARRAY_SIZE(eztv)`, `.rc_proto = RC_PROTO_UNKNOWN`, and `.name = RC_MAP_EZTV` to rc-core.
- The module init function calls `rc_map_register()` and the exit function calls `rc_map_unregister()`, so the map is visible to rc-core only while the object is built in or the module is loaded.
- It has normal `module_init()`/`module_exit()` hooks.

## Control Flow

There is no active decode algorithm in this file. At build or module-load time, the map is registered with the rc-core map registry. A receiver driver later sets an `rc_dev->map_name` matching `RC_MAP_EZTV` or userspace selects that map with tooling such as `ir-keytable`; rc-core then looks up decoded scancodes in `eztv` and emits the associated input keycodes. Unload or rc-core teardown unregisters the map, after which new lookups by name should fail or fall back to another configured map.

## State and Persistence Behavior

The persistent state is the compiled static table plus the registry node in rc-core. The file does not allocate per-device memory, take locks, touch hardware, or persist user settings. Runtime key state, repeat filtering, protocol decoding, and user remaps live in rc-core, the receiver driver, and input/ir-keytable configuration rather than in this keymap source.

## Dependencies and Integration Points

The file depends on `media/rc-map.h`, `linux/module.h`, Linux input `KEY_*` definitions, the `RC_MAP_*` string namespace, and the protocol enum `RC_PROTO_UNKNOWN`. It is built through `drivers/media/rc/keymaps/Makefile` when `CONFIG_RC_MAP` is enabled, except for CEC-style integration if noted above. Board, USB, PCI, CEC, or platform IR drivers integrate with it by naming `RC_MAP_EZTV` as their default map.

## Risks and Edge Cases

Incorrect scancodes, wrong `KEY_*` assignments, a mismatched `.rc_proto`, or a stale `.name` break user-visible remote buttons without producing compile errors. Because the protocol is `RC_PROTO_UNKNOWN`, correctness depends on the consuming hardware driver or legacy decoder path supplying matching scancodes. Table ordering is not semantically important for lookups, but duplicate or vendor-overloaded scancodes should be reviewed carefully. The map can also drift from the v4l-utils userspace copy, causing different behavior between built-in maps and maps loaded from userspace.

## Test Signals

Useful checks include compiling the keymap with `CONFIG_RC_MAP=y` and `=m`, loading/unloading the generated module where applicable, confirming `rc_map_register()` exposes `RC_MAP_EZTV`, using `ir-keytable -r` or equivalent rc-core introspection to inspect the map, and pressing representative numeric, navigation, volume/channel, power, and media keys on the target remote. Protocol-specific tests should verify that decoded `RC_PROTO_UNKNOWN` scancodes match the table values and that unknown buttons do not alias to unsafe actions such as power or record.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-eztv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-flydvb.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-flydvb.c

## Purpose

`rc-flydvb.c` provides the `RC_MAP_FLYDVB` remote-controller keymap for `flydvb remote controller keytable`. It is a data-only rc-core map: decoded remote-control scan codes are translated into Linux input `KEY_*` events for the bundled receiver or board driver. The table has 32 scan-code entries; early entries include `0x01->KEY_ZOOM`, `0x00->KEY_POWER`, `0x03->KEY_NUMERIC_1`, `0x04->KEY_NUMERIC_2`, `0x05->KEY_NUMERIC_3`, `0x07->KEY_NUMERIC_4`. The represented controls cover numeric entry, power/input selection, navigation/menu, channel/volume, DVR/media transport.

## Important APIs, Types, and Functions

- `struct rc_map_table flydvb[]` is the static scan-code-to-keycode table.
- `struct rc_map_list flydvb_map` publishes `.scan = flydvb`, `.size = ARRAY_SIZE(flydvb)`, `.rc_proto = RC_PROTO_UNKNOWN`, and `.name = RC_MAP_FLYDVB` to rc-core.
- The module init function calls `rc_map_register()` and the exit function calls `rc_map_unregister()`, so the map is visible to rc-core only while the object is built in or the module is loaded.
- It has normal `module_init()`/`module_exit()` hooks.

## Control Flow

There is no active decode algorithm in this file. At build or module-load time, the map is registered with the rc-core map registry. A receiver driver later sets an `rc_dev->map_name` matching `RC_MAP_FLYDVB` or userspace selects that map with tooling such as `ir-keytable`; rc-core then looks up decoded scancodes in `flydvb` and emits the associated input keycodes. Unload or rc-core teardown unregisters the map, after which new lookups by name should fail or fall back to another configured map.

## State and Persistence Behavior

The persistent state is the compiled static table plus the registry node in rc-core. The file does not allocate per-device memory, take locks, touch hardware, or persist user settings. Runtime key state, repeat filtering, protocol decoding, and user remaps live in rc-core, the receiver driver, and input/ir-keytable configuration rather than in this keymap source.

## Dependencies and Integration Points

The file depends on `media/rc-map.h`, `linux/module.h`, Linux input `KEY_*` definitions, the `RC_MAP_*` string namespace, and the protocol enum `RC_PROTO_UNKNOWN`. It is built through `drivers/media/rc/keymaps/Makefile` when `CONFIG_RC_MAP` is enabled, except for CEC-style integration if noted above. Board, USB, PCI, CEC, or platform IR drivers integrate with it by naming `RC_MAP_FLYDVB` as their default map.

## Risks and Edge Cases

Incorrect scancodes, wrong `KEY_*` assignments, a mismatched `.rc_proto`, or a stale `.name` break user-visible remote buttons without producing compile errors. Because the protocol is `RC_PROTO_UNKNOWN`, correctness depends on the consuming hardware driver or legacy decoder path supplying matching scancodes. Table ordering is not semantically important for lookups, but duplicate or vendor-overloaded scancodes should be reviewed carefully. The map can also drift from the v4l-utils userspace copy, causing different behavior between built-in maps and maps loaded from userspace.

## Test Signals

Useful checks include compiling the keymap with `CONFIG_RC_MAP=y` and `=m`, loading/unloading the generated module where applicable, confirming `rc_map_register()` exposes `RC_MAP_FLYDVB`, using `ir-keytable -r` or equivalent rc-core introspection to inspect the map, and pressing representative numeric, navigation, volume/channel, power, and media keys on the target remote. Protocol-specific tests should verify that decoded `RC_PROTO_UNKNOWN` scancodes match the table values and that unknown buttons do not alias to unsafe actions such as power or record.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-flydvb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-flyvideo.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-flyvideo.c

## Purpose

`rc-flyvideo.c` provides the `RC_MAP_FLYVIDEO` remote-controller keymap for `flyvideo remote controller keytable`. It is a data-only rc-core map: decoded remote-control scan codes are translated into Linux input `KEY_*` events for the bundled receiver or board driver. The table has 27 scan-code entries; early entries include `0x0f->KEY_NUMERIC_0`, `0x03->KEY_NUMERIC_1`, `0x04->KEY_NUMERIC_2`, `0x05->KEY_NUMERIC_3`, `0x07->KEY_NUMERIC_4`, `0x08->KEY_NUMERIC_5`. The represented controls cover numeric entry, power/input selection, navigation/menu, channel/volume.

## Important APIs, Types, and Functions

- `struct rc_map_table flyvideo[]` is the static scan-code-to-keycode table.
- `struct rc_map_list flyvideo_map` publishes `.scan = flyvideo`, `.size = ARRAY_SIZE(flyvideo)`, `.rc_proto = RC_PROTO_UNKNOWN`, and `.name = RC_MAP_FLYVIDEO` to rc-core.
- The module init function calls `rc_map_register()` and the exit function calls `rc_map_unregister()`, so the map is visible to rc-core only while the object is built in or the module is loaded.
- It has normal `module_init()`/`module_exit()` hooks.

## Control Flow

There is no active decode algorithm in this file. At build or module-load time, the map is registered with the rc-core map registry. A receiver driver later sets an `rc_dev->map_name` matching `RC_MAP_FLYVIDEO` or userspace selects that map with tooling such as `ir-keytable`; rc-core then looks up decoded scancodes in `flyvideo` and emits the associated input keycodes. Unload or rc-core teardown unregisters the map, after which new lookups by name should fail or fall back to another configured map.

## State and Persistence Behavior

The persistent state is the compiled static table plus the registry node in rc-core. The file does not allocate per-device memory, take locks, touch hardware, or persist user settings. Runtime key state, repeat filtering, protocol decoding, and user remaps live in rc-core, the receiver driver, and input/ir-keytable configuration rather than in this keymap source.

## Dependencies and Integration Points

The file depends on `media/rc-map.h`, `linux/module.h`, Linux input `KEY_*` definitions, the `RC_MAP_*` string namespace, and the protocol enum `RC_PROTO_UNKNOWN`. It is built through `drivers/media/rc/keymaps/Makefile` when `CONFIG_RC_MAP` is enabled, except for CEC-style integration if noted above. Board, USB, PCI, CEC, or platform IR drivers integrate with it by naming `RC_MAP_FLYVIDEO` as their default map.

## Risks and Edge Cases

Incorrect scancodes, wrong `KEY_*` assignments, a mismatched `.rc_proto`, or a stale `.name` break user-visible remote buttons without producing compile errors. Because the protocol is `RC_PROTO_UNKNOWN`, correctness depends on the consuming hardware driver or legacy decoder path supplying matching scancodes. Table ordering is not semantically important for lookups, but duplicate or vendor-overloaded scancodes should be reviewed carefully. The map can also drift from the v4l-utils userspace copy, causing different behavior between built-in maps and maps loaded from userspace.

## Test Signals

Useful checks include compiling the keymap with `CONFIG_RC_MAP=y` and `=m`, loading/unloading the generated module where applicable, confirming `rc_map_register()` exposes `RC_MAP_FLYVIDEO`, using `ir-keytable -r` or equivalent rc-core introspection to inspect the map, and pressing representative numeric, navigation, volume/channel, power, and media keys on the target remote. Protocol-specific tests should verify that decoded `RC_PROTO_UNKNOWN` scancodes match the table values and that unknown buttons do not alias to unsafe actions such as power or record.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-flyvideo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-fusionhdtv-mce.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-fusionhdtv-mce.c

## Purpose

`rc-fusionhdtv-mce.c` provides the `RC_MAP_FUSIONHDTV_MCE` remote-controller keymap for `DViCO FUSION HDTV MCE remote controller keytable`. It is a data-only rc-core map: decoded remote-control scan codes are translated into Linux input `KEY_*` events for the bundled receiver or board driver. The table has 45 scan-code entries; early entries include `0x0b->KEY_NUMERIC_1`, `0x17->KEY_NUMERIC_2`, `0x1b->KEY_NUMERIC_3`, `0x07->KEY_NUMERIC_4`, `0x50->KEY_NUMERIC_5`, `0x54->KEY_NUMERIC_6`. The represented controls cover numeric entry, power/input selection, navigation/menu, channel/volume, DVR/media transport, teletext/EPG/application keys.

## Important APIs, Types, and Functions

- `struct rc_map_table fusionhdtv_mce[]` is the static scan-code-to-keycode table.
- `struct rc_map_list fusionhdtv_mce_map` publishes `.scan = fusionhdtv_mce`, `.size = ARRAY_SIZE(fusionhdtv_mce)`, `.rc_proto = RC_PROTO_UNKNOWN`, and `.name = RC_MAP_FUSIONHDTV_MCE` to rc-core.
- The module init function calls `rc_map_register()` and the exit function calls `rc_map_unregister()`, so the map is visible to rc-core only while the object is built in or the module is loaded.
- It has normal `module_init()`/`module_exit()` hooks.

## Control Flow

There is no active decode algorithm in this file. At build or module-load time, the map is registered with the rc-core map registry. A receiver driver later sets an `rc_dev->map_name` matching `RC_MAP_FUSIONHDTV_MCE` or userspace selects that map with tooling such as `ir-keytable`; rc-core then looks up decoded scancodes in `fusionhdtv_mce` and emits the associated input keycodes. Unload or rc-core teardown unregisters the map, after which new lookups by name should fail or fall back to another configured map.

## State and Persistence Behavior

The persistent state is the compiled static table plus the registry node in rc-core. The file does not allocate per-device memory, take locks, touch hardware, or persist user settings. Runtime key state, repeat filtering, protocol decoding, and user remaps live in rc-core, the receiver driver, and input/ir-keytable configuration rather than in this keymap source.

## Dependencies and Integration Points

The file depends on `media/rc-map.h`, `linux/module.h`, Linux input `KEY_*` definitions, the `RC_MAP_*` string namespace, and the protocol enum `RC_PROTO_UNKNOWN`. It is built through `drivers/media/rc/keymaps/Makefile` when `CONFIG_RC_MAP` is enabled, except for CEC-style integration if noted above. Board, USB, PCI, CEC, or platform IR drivers integrate with it by naming `RC_MAP_FUSIONHDTV_MCE` as their default map.

## Risks and Edge Cases

Incorrect scancodes, wrong `KEY_*` assignments, a mismatched `.rc_proto`, or a stale `.name` break user-visible remote buttons without producing compile errors. Because the protocol is `RC_PROTO_UNKNOWN`, correctness depends on the consuming hardware driver or legacy decoder path supplying matching scancodes. Table ordering is not semantically important for lookups, but duplicate or vendor-overloaded scancodes should be reviewed carefully. The map can also drift from the v4l-utils userspace copy, causing different behavior between built-in maps and maps loaded from userspace.

## Test Signals

Useful checks include compiling the keymap with `CONFIG_RC_MAP=y` and `=m`, loading/unloading the generated module where applicable, confirming `rc_map_register()` exposes `RC_MAP_FUSIONHDTV_MCE`, using `ir-keytable -r` or equivalent rc-core introspection to inspect the map, and pressing representative numeric, navigation, volume/channel, power, and media keys on the target remote. Protocol-specific tests should verify that decoded `RC_PROTO_UNKNOWN` scancodes match the table values and that unknown buttons do not alias to unsafe actions such as power or record.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-fusionhdtv-mce.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-gadmei-rm008z.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-gadmei-rm008z.c

## Purpose

`rc-gadmei-rm008z.c` provides the `RC_MAP_GADMEI_RM008Z` remote-controller keymap for `GADMEI UTV330+ RM008Z remote controller keytable`. It is a data-only rc-core map: decoded remote-control scan codes are translated into Linux input `KEY_*` events for the bundled receiver or board driver. The table has 31 scan-code entries; early entries include `0x14->KEY_POWER2`, `0x0c->KEY_MUTE`, `0x18->KEY_TV`, `0x0e->KEY_VIDEO`, `0x0b->KEY_AUDIO`, `0x0f->KEY_RADIO`. The represented controls cover numeric entry, power/input selection, navigation/menu, channel/volume, DVR/media transport, teletext/EPG/application keys.

## Important APIs, Types, and Functions

- `struct rc_map_table gadmei_rm008z[]` is the static scan-code-to-keycode table.
- `struct rc_map_list gadmei_rm008z_map` publishes `.scan = gadmei_rm008z`, `.size = ARRAY_SIZE(gadmei_rm008z)`, `.rc_proto = RC_PROTO_UNKNOWN`, and `.name = RC_MAP_GADMEI_RM008Z` to rc-core.
- The module init function calls `rc_map_register()` and the exit function calls `rc_map_unregister()`, so the map is visible to rc-core only while the object is built in or the module is loaded.
- It has normal `module_init()`/`module_exit()` hooks.

## Control Flow

There is no active decode algorithm in this file. At build or module-load time, the map is registered with the rc-core map registry. A receiver driver later sets an `rc_dev->map_name` matching `RC_MAP_GADMEI_RM008Z` or userspace selects that map with tooling such as `ir-keytable`; rc-core then looks up decoded scancodes in `gadmei_rm008z` and emits the associated input keycodes. Unload or rc-core teardown unregisters the map, after which new lookups by name should fail or fall back to another configured map.

## State and Persistence Behavior

The persistent state is the compiled static table plus the registry node in rc-core. The file does not allocate per-device memory, take locks, touch hardware, or persist user settings. Runtime key state, repeat filtering, protocol decoding, and user remaps live in rc-core, the receiver driver, and input/ir-keytable configuration rather than in this keymap source.

## Dependencies and Integration Points

The file depends on `media/rc-map.h`, `linux/module.h`, Linux input `KEY_*` definitions, the `RC_MAP_*` string namespace, and the protocol enum `RC_PROTO_UNKNOWN`. It is built through `drivers/media/rc/keymaps/Makefile` when `CONFIG_RC_MAP` is enabled, except for CEC-style integration if noted above. Board, USB, PCI, CEC, or platform IR drivers integrate with it by naming `RC_MAP_GADMEI_RM008Z` as their default map.

## Risks and Edge Cases

Incorrect scancodes, wrong `KEY_*` assignments, a mismatched `.rc_proto`, or a stale `.name` break user-visible remote buttons without producing compile errors. Because the protocol is `RC_PROTO_UNKNOWN`, correctness depends on the consuming hardware driver or legacy decoder path supplying matching scancodes. Table ordering is not semantically important for lookups, but duplicate or vendor-overloaded scancodes should be reviewed carefully. The map can also drift from the v4l-utils userspace copy, causing different behavior between built-in maps and maps loaded from userspace.

## Test Signals

Useful checks include compiling the keymap with `CONFIG_RC_MAP=y` and `=m`, loading/unloading the generated module where applicable, confirming `rc_map_register()` exposes `RC_MAP_GADMEI_RM008Z`, using `ir-keytable -r` or equivalent rc-core introspection to inspect the map, and pressing representative numeric, navigation, volume/channel, power, and media keys on the target remote. Protocol-specific tests should verify that decoded `RC_PROTO_UNKNOWN` scancodes match the table values and that unknown buttons do not alias to unsafe actions such as power or record.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-gadmei-rm008z.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-geekbox.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-geekbox.c

## Purpose

`rc-geekbox.c` provides the `RC_MAP_GEEKBOX` remote-controller keymap for `GeekBox remote controller keytable`. It is a data-only rc-core map: decoded remote-control scan codes are translated into Linux input `KEY_*` events for the bundled receiver or board driver. The table has 12 scan-code entries; early entries include `0x01->KEY_BACK`, `0x02->KEY_DOWN`, `0x03->KEY_UP`, `0x07->KEY_OK`, `0x0b->KEY_VOLUMEUP`, `0x0e->KEY_LEFT`. The represented controls cover power/input selection, navigation/menu, channel/volume.

## Important APIs, Types, and Functions

- `struct rc_map_table geekbox[]` is the static scan-code-to-keycode table.
- `struct rc_map_list geekbox_map` publishes `.scan = geekbox`, `.size = ARRAY_SIZE(geekbox)`, `.rc_proto = RC_PROTO_NEC`, and `.name = RC_MAP_GEEKBOX` to rc-core.
- The module init function calls `rc_map_register()` and the exit function calls `rc_map_unregister()`, so the map is visible to rc-core only while the object is built in or the module is loaded.
- It has normal `module_init()`/`module_exit()` hooks.

## Control Flow

There is no active decode algorithm in this file. At build or module-load time, the map is registered with the rc-core map registry. A receiver driver later sets an `rc_dev->map_name` matching `RC_MAP_GEEKBOX` or userspace selects that map with tooling such as `ir-keytable`; rc-core then looks up decoded scancodes in `geekbox` and emits the associated input keycodes. Unload or rc-core teardown unregisters the map, after which new lookups by name should fail or fall back to another configured map.

## State and Persistence Behavior

The persistent state is the compiled static table plus the registry node in rc-core. The file does not allocate per-device memory, take locks, touch hardware, or persist user settings. Runtime key state, repeat filtering, protocol decoding, and user remaps live in rc-core, the receiver driver, and input/ir-keytable configuration rather than in this keymap source.

## Dependencies and Integration Points

The file depends on `media/rc-map.h`, `linux/module.h`, Linux input `KEY_*` definitions, the `RC_MAP_*` string namespace, and the protocol enum `RC_PROTO_NEC`. It is built through `drivers/media/rc/keymaps/Makefile` when `CONFIG_RC_MAP` is enabled, except for CEC-style integration if noted above. Board, USB, PCI, CEC, or platform IR drivers integrate with it by naming `RC_MAP_GEEKBOX` as their default map.

## Risks and Edge Cases

Incorrect scancodes, wrong `KEY_*` assignments, a mismatched `.rc_proto`, or a stale `.name` break user-visible remote buttons without producing compile errors. The declared protocol `RC_PROTO_NEC` tells rc-core which decoded scancode namespace this map expects. Table ordering is not semantically important for lookups, but duplicate or vendor-overloaded scancodes should be reviewed carefully. The map can also drift from the v4l-utils userspace copy, causing different behavior between built-in maps and maps loaded from userspace.

## Test Signals

Useful checks include compiling the keymap with `CONFIG_RC_MAP=y` and `=m`, loading/unloading the generated module where applicable, confirming `rc_map_register()` exposes `RC_MAP_GEEKBOX`, using `ir-keytable -r` or equivalent rc-core introspection to inspect the map, and pressing representative numeric, navigation, volume/channel, power, and media keys on the target remote. Protocol-specific tests should verify that decoded `RC_PROTO_NEC` scancodes match the table values and that unknown buttons do not alias to unsafe actions such as power or record.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-geekbox.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-genius-tvgo-a11mce.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-genius-tvgo-a11mce.c

## Purpose

`rc-genius-tvgo-a11mce.c` provides the `RC_MAP_GENIUS_TVGO_A11MCE` remote-controller keymap for `Genius TVGO A11MCE remote controller keytable`. It is a data-only rc-core map: decoded remote-control scan codes are translated into Linux input `KEY_*` events for the bundled receiver or board driver. The table has 32 scan-code entries; early entries include `0x48->KEY_NUMERIC_0`, `0x09->KEY_NUMERIC_1`, `0x1d->KEY_NUMERIC_2`, `0x1f->KEY_NUMERIC_3`, `0x19->KEY_NUMERIC_4`, `0x1b->KEY_NUMERIC_5`. The represented controls cover numeric entry, power/input selection, navigation/menu, channel/volume, DVR/media transport, colored function keys.

## Important APIs, Types, and Functions

- `struct rc_map_table genius_tvgo_a11mce[]` is the static scan-code-to-keycode table.
- `struct rc_map_list genius_tvgo_a11mce_map` publishes `.scan = genius_tvgo_a11mce`, `.size = ARRAY_SIZE(genius_tvgo_a11mce)`, `.rc_proto = RC_PROTO_UNKNOWN`, and `.name = RC_MAP_GENIUS_TVGO_A11MCE` to rc-core.
- The module init function calls `rc_map_register()` and the exit function calls `rc_map_unregister()`, so the map is visible to rc-core only while the object is built in or the module is loaded.
- It has normal `module_init()`/`module_exit()` hooks.

## Control Flow

There is no active decode algorithm in this file. At build or module-load time, the map is registered with the rc-core map registry. A receiver driver later sets an `rc_dev->map_name` matching `RC_MAP_GENIUS_TVGO_A11MCE` or userspace selects that map with tooling such as `ir-keytable`; rc-core then looks up decoded scancodes in `genius_tvgo_a11mce` and emits the associated input keycodes. Unload or rc-core teardown unregisters the map, after which new lookups by name should fail or fall back to another configured map.

## State and Persistence Behavior

The persistent state is the compiled static table plus the registry node in rc-core. The file does not allocate per-device memory, take locks, touch hardware, or persist user settings. Runtime key state, repeat filtering, protocol decoding, and user remaps live in rc-core, the receiver driver, and input/ir-keytable configuration rather than in this keymap source.

## Dependencies and Integration Points

The file depends on `media/rc-map.h`, `linux/module.h`, Linux input `KEY_*` definitions, the `RC_MAP_*` string namespace, and the protocol enum `RC_PROTO_UNKNOWN`. It is built through `drivers/media/rc/keymaps/Makefile` when `CONFIG_RC_MAP` is enabled, except for CEC-style integration if noted above. Board, USB, PCI, CEC, or platform IR drivers integrate with it by naming `RC_MAP_GENIUS_TVGO_A11MCE` as their default map.

## Risks and Edge Cases

Incorrect scancodes, wrong `KEY_*` assignments, a mismatched `.rc_proto`, or a stale `.name` break user-visible remote buttons without producing compile errors. Because the protocol is `RC_PROTO_UNKNOWN`, correctness depends on the consuming hardware driver or legacy decoder path supplying matching scancodes. Table ordering is not semantically important for lookups, but duplicate or vendor-overloaded scancodes should be reviewed carefully. The map can also drift from the v4l-utils userspace copy, causing different behavior between built-in maps and maps loaded from userspace.

## Test Signals

Useful checks include compiling the keymap with `CONFIG_RC_MAP=y` and `=m`, loading/unloading the generated module where applicable, confirming `rc_map_register()` exposes `RC_MAP_GENIUS_TVGO_A11MCE`, using `ir-keytable -r` or equivalent rc-core introspection to inspect the map, and pressing representative numeric, navigation, volume/channel, power, and media keys on the target remote. Protocol-specific tests should verify that decoded `RC_PROTO_UNKNOWN` scancodes match the table values and that unknown buttons do not alias to unsafe actions such as power or record.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-genius-tvgo-a11mce.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-gotview7135.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-gotview7135.c

## Purpose

`rc-gotview7135.c` provides the `RC_MAP_GOTVIEW7135` remote-controller keymap for `gotview7135 remote controller keytable`. It is a data-only rc-core map: decoded remote-control scan codes are translated into Linux input `KEY_*` events for the bundled receiver or board driver. The table has 34 scan-code entries; early entries include `0x11->KEY_POWER`, `0x35->KEY_TV`, `0x1b->KEY_NUMERIC_0`, `0x29->KEY_NUMERIC_1`, `0x19->KEY_NUMERIC_2`, `0x39->KEY_NUMERIC_3`. The represented controls cover numeric entry, power/input selection, channel/volume, DVR/media transport.

## Important APIs, Types, and Functions

- `struct rc_map_table gotview7135[]` is the static scan-code-to-keycode table.
- `struct rc_map_list gotview7135_map` publishes `.scan = gotview7135`, `.size = ARRAY_SIZE(gotview7135)`, `.rc_proto = RC_PROTO_UNKNOWN`, and `.name = RC_MAP_GOTVIEW7135` to rc-core.
- The module init function calls `rc_map_register()` and the exit function calls `rc_map_unregister()`, so the map is visible to rc-core only while the object is built in or the module is loaded.
- It has normal `module_init()`/`module_exit()` hooks.

## Control Flow

There is no active decode algorithm in this file. At build or module-load time, the map is registered with the rc-core map registry. A receiver driver later sets an `rc_dev->map_name` matching `RC_MAP_GOTVIEW7135` or userspace selects that map with tooling such as `ir-keytable`; rc-core then looks up decoded scancodes in `gotview7135` and emits the associated input keycodes. Unload or rc-core teardown unregisters the map, after which new lookups by name should fail or fall back to another configured map.

## State and Persistence Behavior

The persistent state is the compiled static table plus the registry node in rc-core. The file does not allocate per-device memory, take locks, touch hardware, or persist user settings. Runtime key state, repeat filtering, protocol decoding, and user remaps live in rc-core, the receiver driver, and input/ir-keytable configuration rather than in this keymap source.

## Dependencies and Integration Points

The file depends on `media/rc-map.h`, `linux/module.h`, Linux input `KEY_*` definitions, the `RC_MAP_*` string namespace, and the protocol enum `RC_PROTO_UNKNOWN`. It is built through `drivers/media/rc/keymaps/Makefile` when `CONFIG_RC_MAP` is enabled, except for CEC-style integration if noted above. Board, USB, PCI, CEC, or platform IR drivers integrate with it by naming `RC_MAP_GOTVIEW7135` as their default map.

## Risks and Edge Cases

Incorrect scancodes, wrong `KEY_*` assignments, a mismatched `.rc_proto`, or a stale `.name` break user-visible remote buttons without producing compile errors. Because the protocol is `RC_PROTO_UNKNOWN`, correctness depends on the consuming hardware driver or legacy decoder path supplying matching scancodes. Table ordering is not semantically important for lookups, but duplicate or vendor-overloaded scancodes should be reviewed carefully. The map can also drift from the v4l-utils userspace copy, causing different behavior between built-in maps and maps loaded from userspace.

## Test Signals

Useful checks include compiling the keymap with `CONFIG_RC_MAP=y` and `=m`, loading/unloading the generated module where applicable, confirming `rc_map_register()` exposes `RC_MAP_GOTVIEW7135`, using `ir-keytable -r` or equivalent rc-core introspection to inspect the map, and pressing representative numeric, navigation, volume/channel, power, and media keys on the target remote. Protocol-specific tests should verify that decoded `RC_PROTO_UNKNOWN` scancodes match the table values and that unknown buttons do not alias to unsafe actions such as power or record.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-gotview7135.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-hauppauge.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-hauppauge.c

## Purpose

`rc-hauppauge.c` provides the `RC_MAP_HAUPPAUGE` remote-controller keymap for `Hauppauge remote controllers keytable`. It is a data-only rc-core map: decoded remote-control scan codes are translated into Linux input `KEY_*` events for the bundled receiver or board driver. The table has 204 scan-code entries; early entries include `0x1e3b->KEY_SELECT`, `0x1e3d->KEY_POWER2`, `0x1e1c->KEY_TV`, `0x1e18->KEY_VIDEO`, `0x1e19->KEY_AUDIO`, `0x1e1a->KEY_CAMERA`. The represented controls cover numeric entry, power/input selection, navigation/menu, channel/volume, DVR/media transport, colored function keys, teletext/EPG/application keys.

## Important APIs, Types, and Functions

- `struct rc_map_table rc5_hauppauge_new[]` is the static scan-code-to-keycode table.
- `struct rc_map_list rc5_hauppauge_new_map` publishes `.scan = rc5_hauppauge_new`, `.size = ARRAY_SIZE(rc5_hauppauge_new)`, `.rc_proto = RC_PROTO_RC5`, and `.name = RC_MAP_HAUPPAUGE` to rc-core.
- The module init function calls `rc_map_register()` and the exit function calls `rc_map_unregister()`, so the map is visible to rc-core only while the object is built in or the module is loaded.
- It has normal `module_init()`/`module_exit()` hooks.

## Control Flow

There is no active decode algorithm in this file. At build or module-load time, the map is registered with the rc-core map registry. A receiver driver later sets an `rc_dev->map_name` matching `RC_MAP_HAUPPAUGE` or userspace selects that map with tooling such as `ir-keytable`; rc-core then looks up decoded scancodes in `rc5_hauppauge_new` and emits the associated input keycodes. Unload or rc-core teardown unregisters the map, after which new lookups by name should fail or fall back to another configured map.

## State and Persistence Behavior

The persistent state is the compiled static table plus the registry node in rc-core. The file does not allocate per-device memory, take locks, touch hardware, or persist user settings. Runtime key state, repeat filtering, protocol decoding, and user remaps live in rc-core, the receiver driver, and input/ir-keytable configuration rather than in this keymap source.

## Dependencies and Integration Points

The file depends on `media/rc-map.h`, `linux/module.h`, Linux input `KEY_*` definitions, the `RC_MAP_*` string namespace, and the protocol enum `RC_PROTO_RC5`. It is built through `drivers/media/rc/keymaps/Makefile` when `CONFIG_RC_MAP` is enabled, except for CEC-style integration if noted above. Board, USB, PCI, CEC, or platform IR drivers integrate with it by naming `RC_MAP_HAUPPAUGE` as their default map.

## Risks and Edge Cases

Incorrect scancodes, wrong `KEY_*` assignments, a mismatched `.rc_proto`, or a stale `.name` break user-visible remote buttons without producing compile errors. The declared protocol `RC_PROTO_RC5` tells rc-core which decoded scancode namespace this map expects. Table ordering is not semantically important for lookups, but duplicate or vendor-overloaded scancodes should be reviewed carefully. The map can also drift from the v4l-utils userspace copy, causing different behavior between built-in maps and maps loaded from userspace.

## Test Signals

Useful checks include compiling the keymap with `CONFIG_RC_MAP=y` and `=m`, loading/unloading the generated module where applicable, confirming `rc_map_register()` exposes `RC_MAP_HAUPPAUGE`, using `ir-keytable -r` or equivalent rc-core introspection to inspect the map, and pressing representative numeric, navigation, volume/channel, power, and media keys on the target remote. Protocol-specific tests should verify that decoded `RC_PROTO_RC5` scancodes match the table values and that unknown buttons do not alias to unsafe actions such as power or record.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-hauppauge.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-hisi-poplar.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-hisi-poplar.c

## Purpose

`rc-hisi-poplar.c` provides the `RC_MAP_HISI_POPLAR` remote-controller keymap for `HiSilicon poplar remote controller keytable`. It is a data-only rc-core map: decoded remote-control scan codes are translated into Linux input `KEY_*` events for the bundled receiver or board driver. The table has 29 scan-code entries; early entries include `0x0000b292->KEY_NUMERIC_1`, `0x0000b293->KEY_NUMERIC_2`, `0x0000b2cc->KEY_NUMERIC_3`, `0x0000b28e->KEY_NUMERIC_4`, `0x0000b28f->KEY_NUMERIC_5`, `0x0000b2c8->KEY_NUMERIC_6`. The represented controls cover numeric entry, power/input selection, navigation/menu, channel/volume, DVR/media transport.

## Important APIs, Types, and Functions

- `struct rc_map_table hisi_poplar_keymap[]` is the static scan-code-to-keycode table.
- `struct rc_map_list hisi_poplar_map` publishes `.scan = hisi_poplar_keymap`, `.size = ARRAY_SIZE(hisi_poplar_keymap)`, `.rc_proto = RC_PROTO_NEC`, and `.name = RC_MAP_HISI_POPLAR` to rc-core.
- The module init function calls `rc_map_register()` and the exit function calls `rc_map_unregister()`, so the map is visible to rc-core only while the object is built in or the module is loaded.
- It has normal `module_init()`/`module_exit()` hooks.

## Control Flow

There is no active decode algorithm in this file. At build or module-load time, the map is registered with the rc-core map registry. A receiver driver later sets an `rc_dev->map_name` matching `RC_MAP_HISI_POPLAR` or userspace selects that map with tooling such as `ir-keytable`; rc-core then looks up decoded scancodes in `hisi_poplar_keymap` and emits the associated input keycodes. Unload or rc-core teardown unregisters the map, after which new lookups by name should fail or fall back to another configured map.

## State and Persistence Behavior

The persistent state is the compiled static table plus the registry node in rc-core. The file does not allocate per-device memory, take locks, touch hardware, or persist user settings. Runtime key state, repeat filtering, protocol decoding, and user remaps live in rc-core, the receiver driver, and input/ir-keytable configuration rather than in this keymap source.

## Dependencies and Integration Points

The file depends on `media/rc-map.h`, `linux/module.h`, Linux input `KEY_*` definitions, the `RC_MAP_*` string namespace, and the protocol enum `RC_PROTO_NEC`. It is built through `drivers/media/rc/keymaps/Makefile` when `CONFIG_RC_MAP` is enabled, except for CEC-style integration if noted above. Board, USB, PCI, CEC, or platform IR drivers integrate with it by naming `RC_MAP_HISI_POPLAR` as their default map.

## Risks and Edge Cases

Incorrect scancodes, wrong `KEY_*` assignments, a mismatched `.rc_proto`, or a stale `.name` break user-visible remote buttons without producing compile errors. Duplicate scancodes are present (0x0000b2c5); this is usually intentional only when aliases map to the same key. The declared protocol `RC_PROTO_NEC` tells rc-core which decoded scancode namespace this map expects. Table ordering is not semantically important for lookups, but duplicate or vendor-overloaded scancodes should be reviewed carefully. The map can also drift from the v4l-utils userspace copy, causing different behavior between built-in maps and maps loaded from userspace.

## Test Signals

Useful checks include compiling the keymap with `CONFIG_RC_MAP=y` and `=m`, loading/unloading the generated module where applicable, confirming `rc_map_register()` exposes `RC_MAP_HISI_POPLAR`, using `ir-keytable -r` or equivalent rc-core introspection to inspect the map, and pressing representative numeric, navigation, volume/channel, power, and media keys on the target remote. Protocol-specific tests should verify that decoded `RC_PROTO_NEC` scancodes match the table values and that unknown buttons do not alias to unsafe actions such as power or record.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-hisi-poplar.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-hisi-tv-demo.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-hisi-tv-demo.c

## Purpose

`rc-hisi-tv-demo.c` provides the `RC_MAP_HISI_TV_DEMO` remote-controller keymap for `HiSilicon tv demo remote controller keytable`. It is a data-only rc-core map: decoded remote-control scan codes are translated into Linux input `KEY_*` events for the bundled receiver or board driver. The table has 39 scan-code entries; early entries include `0x00000092->KEY_NUMERIC_1`, `0x00000093->KEY_NUMERIC_2`, `0x000000cc->KEY_NUMERIC_3`, `0x0000009f->KEY_NUMERIC_4`, `0x0000008e->KEY_NUMERIC_5`, `0x0000008f->KEY_NUMERIC_6`. The represented controls cover numeric entry, power/input selection, navigation/menu, channel/volume, DVR/media transport, colored function keys, teletext/EPG/application keys.

## Important APIs, Types, and Functions

- `struct rc_map_table hisi_tv_demo_keymap[]` is the static scan-code-to-keycode table.
- `struct rc_map_list hisi_tv_demo_map` publishes `.scan = hisi_tv_demo_keymap`, `.size = ARRAY_SIZE(hisi_tv_demo_keymap)`, `.rc_proto = RC_PROTO_NEC`, and `.name = RC_MAP_HISI_TV_DEMO` to rc-core.
- The module init function calls `rc_map_register()` and the exit function calls `rc_map_unregister()`, so the map is visible to rc-core only while the object is built in or the module is loaded.
- It has normal `module_init()`/`module_exit()` hooks.

## Control Flow

There is no active decode algorithm in this file. At build or module-load time, the map is registered with the rc-core map registry. A receiver driver later sets an `rc_dev->map_name` matching `RC_MAP_HISI_TV_DEMO` or userspace selects that map with tooling such as `ir-keytable`; rc-core then looks up decoded scancodes in `hisi_tv_demo_keymap` and emits the associated input keycodes. Unload or rc-core teardown unregisters the map, after which new lookups by name should fail or fall back to another configured map.

## State and Persistence Behavior

The persistent state is the compiled static table plus the registry node in rc-core. The file does not allocate per-device memory, take locks, touch hardware, or persist user settings. Runtime key state, repeat filtering, protocol decoding, and user remaps live in rc-core, the receiver driver, and input/ir-keytable configuration rather than in this keymap source.

## Dependencies and Integration Points

The file depends on `media/rc-map.h`, `linux/module.h`, Linux input `KEY_*` definitions, the `RC_MAP_*` string namespace, and the protocol enum `RC_PROTO_NEC`. It is built through `drivers/media/rc/keymaps/Makefile` when `CONFIG_RC_MAP` is enabled, except for CEC-style integration if noted above. Board, USB, PCI, CEC, or platform IR drivers integrate with it by naming `RC_MAP_HISI_TV_DEMO` as their default map.

## Risks and Edge Cases

Incorrect scancodes, wrong `KEY_*` assignments, a mismatched `.rc_proto`, or a stale `.name` break user-visible remote buttons without producing compile errors. The declared protocol `RC_PROTO_NEC` tells rc-core which decoded scancode namespace this map expects. Table ordering is not semantically important for lookups, but duplicate or vendor-overloaded scancodes should be reviewed carefully. The map can also drift from the v4l-utils userspace copy, causing different behavior between built-in maps and maps loaded from userspace.

## Test Signals

Useful checks include compiling the keymap with `CONFIG_RC_MAP=y` and `=m`, loading/unloading the generated module where applicable, confirming `rc_map_register()` exposes `RC_MAP_HISI_TV_DEMO`, using `ir-keytable -r` or equivalent rc-core introspection to inspect the map, and pressing representative numeric, navigation, volume/channel, power, and media keys on the target remote. Protocol-specific tests should verify that decoded `RC_PROTO_NEC` scancodes match the table values and that unknown buttons do not alias to unsafe actions such as power or record.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-hisi-tv-demo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-imon-mce.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-imon-mce.c

## Purpose

`rc-imon-mce.c` provides the `RC_MAP_IMON_MCE` remote-controller keymap for `iMON MCE remote controller keytable`. It is a data-only rc-core map: decoded remote-control scan codes are translated into Linux input `KEY_*` events for the bundled receiver or board driver. The table has 77 scan-code entries; early entries include `0x800ff415->KEY_REWIND`, `0x800ff414->KEY_FASTFORWARD`, `0x800ff41b->KEY_PREVIOUS`, `0x800ff41a->KEY_NEXT`, `0x800ff416->KEY_PLAY`, `0x800ff418->KEY_PAUSE`. The represented controls cover numeric entry, power/input selection, navigation/menu, channel/volume, DVR/media transport, colored function keys, teletext/EPG/application keys.

## Important APIs, Types, and Functions

- `struct rc_map_table imon_mce[]` is the static scan-code-to-keycode table.
- `struct rc_map_list imon_mce_map` publishes `.scan = imon_mce`, `.size = ARRAY_SIZE(imon_mce)`, `.rc_proto = RC_PROTO_RC6_MCE`, and `.name = RC_MAP_IMON_MCE` to rc-core.
- The module init function calls `rc_map_register()` and the exit function calls `rc_map_unregister()`, so the map is visible to rc-core only while the object is built in or the module is loaded.
- It has normal `module_init()`/`module_exit()` hooks.

## Control Flow

There is no active decode algorithm in this file. At build or module-load time, the map is registered with the rc-core map registry. A receiver driver later sets an `rc_dev->map_name` matching `RC_MAP_IMON_MCE` or userspace selects that map with tooling such as `ir-keytable`; rc-core then looks up decoded scancodes in `imon_mce` and emits the associated input keycodes. Unload or rc-core teardown unregisters the map, after which new lookups by name should fail or fall back to another configured map.

## State and Persistence Behavior

The persistent state is the compiled static table plus the registry node in rc-core. The file does not allocate per-device memory, take locks, touch hardware, or persist user settings. Runtime key state, repeat filtering, protocol decoding, and user remaps live in rc-core, the receiver driver, and input/ir-keytable configuration rather than in this keymap source.

## Dependencies and Integration Points

The file depends on `media/rc-map.h`, `linux/module.h`, Linux input `KEY_*` definitions, the `RC_MAP_*` string namespace, and the protocol enum `RC_PROTO_RC6_MCE`. It is built through `drivers/media/rc/keymaps/Makefile` when `CONFIG_RC_MAP` is enabled, except for CEC-style integration if noted above. Board, USB, PCI, CEC, or platform IR drivers integrate with it by naming `RC_MAP_IMON_MCE` as their default map.

## Risks and Edge Cases

Incorrect scancodes, wrong `KEY_*` assignments, a mismatched `.rc_proto`, or a stale `.name` break user-visible remote buttons without producing compile errors. Duplicate scancodes are present (0x02000028, 0x800ff41d, 0x800ff425); this is usually intentional only when aliases map to the same key. The declared protocol `RC_PROTO_RC6_MCE` tells rc-core which decoded scancode namespace this map expects. Table ordering is not semantically important for lookups, but duplicate or vendor-overloaded scancodes should be reviewed carefully. The map can also drift from the v4l-utils userspace copy, causing different behavior between built-in maps and maps loaded from userspace.

## Test Signals

Useful checks include compiling the keymap with `CONFIG_RC_MAP=y` and `=m`, loading/unloading the generated module where applicable, confirming `rc_map_register()` exposes `RC_MAP_IMON_MCE`, using `ir-keytable -r` or equivalent rc-core introspection to inspect the map, and pressing representative numeric, navigation, volume/channel, power, and media keys on the target remote. Protocol-specific tests should verify that decoded `RC_PROTO_RC6_MCE` scancodes match the table values and that unknown buttons do not alias to unsafe actions such as power or record.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-imon-mce.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-imon-pad.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-imon-pad.c

## Purpose

`rc-imon-pad.c` provides the `RC_MAP_IMON_PAD` remote-controller keymap for `iMON PAD remote controller keytable`. It is a data-only rc-core map: decoded remote-control scan codes are translated into Linux input `KEY_*` events for the bundled receiver or board driver. The table has 84 scan-code entries; early entries include `0x2a8195b7->KEY_REWIND`, `0x298315b7->KEY_REWIND`, `0x2b8115b7->KEY_FASTFORWARD`, `0x2b8315b7->KEY_FASTFORWARD`, `0x2b9115b7->KEY_PREVIOUS`, `0x298195b7->KEY_NEXT`. The represented controls cover numeric entry, power/input selection, navigation/menu, channel/volume, DVR/media transport, teletext/EPG/application keys.

## Important APIs, Types, and Functions

- `struct rc_map_table imon_pad[]` is the static scan-code-to-keycode table.
- `struct rc_map_list imon_pad_map` publishes `.scan = imon_pad`, `.size = ARRAY_SIZE(imon_pad)`, `.rc_proto = RC_PROTO_IMON`, and `.name = RC_MAP_IMON_PAD` to rc-core.
- The module init function calls `rc_map_register()` and the exit function calls `rc_map_unregister()`, so the map is visible to rc-core only while the object is built in or the module is loaded.
- It has normal `module_init()`/`module_exit()` hooks.

## Control Flow

There is no active decode algorithm in this file. At build or module-load time, the map is registered with the rc-core map registry. A receiver driver later sets an `rc_dev->map_name` matching `RC_MAP_IMON_PAD` or userspace selects that map with tooling such as `ir-keytable`; rc-core then looks up decoded scancodes in `imon_pad` and emits the associated input keycodes. Unload or rc-core teardown unregisters the map, after which new lookups by name should fail or fall back to another configured map.

## State and Persistence Behavior

The persistent state is the compiled static table plus the registry node in rc-core. The file does not allocate per-device memory, take locks, touch hardware, or persist user settings. Runtime key state, repeat filtering, protocol decoding, and user remaps live in rc-core, the receiver driver, and input/ir-keytable configuration rather than in this keymap source.

## Dependencies and Integration Points

The file depends on `media/rc-map.h`, `linux/module.h`, Linux input `KEY_*` definitions, the `RC_MAP_*` string namespace, and the protocol enum `RC_PROTO_IMON`. It is built through `drivers/media/rc/keymaps/Makefile` when `CONFIG_RC_MAP` is enabled, except for CEC-style integration if noted above. Board, USB, PCI, CEC, or platform IR drivers integrate with it by naming `RC_MAP_IMON_PAD` as their default map.

## Risks and Edge Cases

Incorrect scancodes, wrong `KEY_*` assignments, a mismatched `.rc_proto`, or a stale `.name` break user-visible remote buttons without producing compile errors. The declared protocol `RC_PROTO_IMON` tells rc-core which decoded scancode namespace this map expects. Table ordering is not semantically important for lookups, but duplicate or vendor-overloaded scancodes should be reviewed carefully. The map can also drift from the v4l-utils userspace copy, causing different behavior between built-in maps and maps loaded from userspace.

## Test Signals

Useful checks include compiling the keymap with `CONFIG_RC_MAP=y` and `=m`, loading/unloading the generated module where applicable, confirming `rc_map_register()` exposes `RC_MAP_IMON_PAD`, using `ir-keytable -r` or equivalent rc-core introspection to inspect the map, and pressing representative numeric, navigation, volume/channel, power, and media keys on the target remote. Protocol-specific tests should verify that decoded `RC_PROTO_IMON` scancodes match the table values and that unknown buttons do not alias to unsafe actions such as power or record.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-imon-pad.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-imon-rsc.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-imon-rsc.c

## Purpose

`rc-imon-rsc.c` provides the `RC_MAP_IMON_RSC` remote-controller keymap for `iMON RSC remote controller keytable`. It is a data-only rc-core map: decoded remote-control scan codes are translated into Linux input `KEY_*` events for the bundled receiver or board driver. The table has 39 scan-code entries; early entries include `0x801010->KEY_EXIT`, `0x80102f->KEY_POWER`, `0x80104a->KEY_SCREENSAVER`, `0x801049->KEY_TIME`, `0x801054->KEY_NUMERIC_1`, `0x801055->KEY_NUMERIC_2`. The represented controls cover numeric entry, power/input selection, navigation/menu, channel/volume, DVR/media transport.

## Important APIs, Types, and Functions

- `struct rc_map_table imon_rsc[]` is the static scan-code-to-keycode table.
- `struct rc_map_list imon_rsc_map` publishes `.scan = imon_rsc`, `.size = ARRAY_SIZE(imon_rsc)`, `.rc_proto = RC_PROTO_NECX`, and `.name = RC_MAP_IMON_RSC` to rc-core.
- The module init function calls `rc_map_register()` and the exit function calls `rc_map_unregister()`, so the map is visible to rc-core only while the object is built in or the module is loaded.
- It has normal `module_init()`/`module_exit()` hooks.

## Control Flow

There is no active decode algorithm in this file. At build or module-load time, the map is registered with the rc-core map registry. A receiver driver later sets an `rc_dev->map_name` matching `RC_MAP_IMON_RSC` or userspace selects that map with tooling such as `ir-keytable`; rc-core then looks up decoded scancodes in `imon_rsc` and emits the associated input keycodes. Unload or rc-core teardown unregisters the map, after which new lookups by name should fail or fall back to another configured map.

## State and Persistence Behavior

The persistent state is the compiled static table plus the registry node in rc-core. The file does not allocate per-device memory, take locks, touch hardware, or persist user settings. Runtime key state, repeat filtering, protocol decoding, and user remaps live in rc-core, the receiver driver, and input/ir-keytable configuration rather than in this keymap source.

## Dependencies and Integration Points

The file depends on `media/rc-map.h`, `linux/module.h`, Linux input `KEY_*` definitions, the `RC_MAP_*` string namespace, and the protocol enum `RC_PROTO_NECX`. It is built through `drivers/media/rc/keymaps/Makefile` when `CONFIG_RC_MAP` is enabled, except for CEC-style integration if noted above. Board, USB, PCI, CEC, or platform IR drivers integrate with it by naming `RC_MAP_IMON_RSC` as their default map.

## Risks and Edge Cases

Incorrect scancodes, wrong `KEY_*` assignments, a mismatched `.rc_proto`, or a stale `.name` break user-visible remote buttons without producing compile errors. The declared protocol `RC_PROTO_NECX` tells rc-core which decoded scancode namespace this map expects. Table ordering is not semantically important for lookups, but duplicate or vendor-overloaded scancodes should be reviewed carefully. The map can also drift from the v4l-utils userspace copy, causing different behavior between built-in maps and maps loaded from userspace.

## Test Signals

Useful checks include compiling the keymap with `CONFIG_RC_MAP=y` and `=m`, loading/unloading the generated module where applicable, confirming `rc_map_register()` exposes `RC_MAP_IMON_RSC`, using `ir-keytable -r` or equivalent rc-core introspection to inspect the map, and pressing representative numeric, navigation, volume/channel, power, and media keys on the target remote. Protocol-specific tests should verify that decoded `RC_PROTO_NECX` scancodes match the table values and that unknown buttons do not alias to unsafe actions such as power or record.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-imon-rsc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-iodata-bctv7e.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-iodata-bctv7e.c

## Purpose

`rc-iodata-bctv7e.c` provides the `RC_MAP_IODATA_BCTV7E` remote-controller keymap for `IO-DATA BCTV7E remote controller keytable`. It is a data-only rc-core map: decoded remote-control scan codes are translated into Linux input `KEY_*` events for the bundled receiver or board driver. The table has 36 scan-code entries; early entries include `0x40->KEY_TV`, `0x20->KEY_RADIO`, `0x60->KEY_EPG`, `0x00->KEY_POWER`, `0x44->KEY_NUMERIC_0`, `0x50->KEY_NUMERIC_1`. The represented controls cover numeric entry, power/input selection, navigation/menu, channel/volume, DVR/media transport, colored function keys, teletext/EPG/application keys.

## Important APIs, Types, and Functions

- `struct rc_map_table iodata_bctv7e[]` is the static scan-code-to-keycode table.
- `struct rc_map_list iodata_bctv7e_map` publishes `.scan = iodata_bctv7e`, `.size = ARRAY_SIZE(iodata_bctv7e)`, `.rc_proto = RC_PROTO_UNKNOWN`, and `.name = RC_MAP_IODATA_BCTV7E` to rc-core.
- The module init function calls `rc_map_register()` and the exit function calls `rc_map_unregister()`, so the map is visible to rc-core only while the object is built in or the module is loaded.
- It has normal `module_init()`/`module_exit()` hooks.

## Control Flow

There is no active decode algorithm in this file. At build or module-load time, the map is registered with the rc-core map registry. A receiver driver later sets an `rc_dev->map_name` matching `RC_MAP_IODATA_BCTV7E` or userspace selects that map with tooling such as `ir-keytable`; rc-core then looks up decoded scancodes in `iodata_bctv7e` and emits the associated input keycodes. Unload or rc-core teardown unregisters the map, after which new lookups by name should fail or fall back to another configured map.

## State and Persistence Behavior

The persistent state is the compiled static table plus the registry node in rc-core. The file does not allocate per-device memory, take locks, touch hardware, or persist user settings. Runtime key state, repeat filtering, protocol decoding, and user remaps live in rc-core, the receiver driver, and input/ir-keytable configuration rather than in this keymap source.

## Dependencies and Integration Points

The file depends on `media/rc-map.h`, `linux/module.h`, Linux input `KEY_*` definitions, the `RC_MAP_*` string namespace, and the protocol enum `RC_PROTO_UNKNOWN`. It is built through `drivers/media/rc/keymaps/Makefile` when `CONFIG_RC_MAP` is enabled, except for CEC-style integration if noted above. Board, USB, PCI, CEC, or platform IR drivers integrate with it by naming `RC_MAP_IODATA_BCTV7E` as their default map.

## Risks and Edge Cases

Incorrect scancodes, wrong `KEY_*` assignments, a mismatched `.rc_proto`, or a stale `.name` break user-visible remote buttons without producing compile errors. Because the protocol is `RC_PROTO_UNKNOWN`, correctness depends on the consuming hardware driver or legacy decoder path supplying matching scancodes. Table ordering is not semantically important for lookups, but duplicate or vendor-overloaded scancodes should be reviewed carefully. The map can also drift from the v4l-utils userspace copy, causing different behavior between built-in maps and maps loaded from userspace.

## Test Signals

Useful checks include compiling the keymap with `CONFIG_RC_MAP=y` and `=m`, loading/unloading the generated module where applicable, confirming `rc_map_register()` exposes `RC_MAP_IODATA_BCTV7E`, using `ir-keytable -r` or equivalent rc-core introspection to inspect the map, and pressing representative numeric, navigation, volume/channel, power, and media keys on the target remote. Protocol-specific tests should verify that decoded `RC_PROTO_UNKNOWN` scancodes match the table values and that unknown buttons do not alias to unsafe actions such as power or record.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-iodata-bctv7e.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-it913x-v1.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-it913x-v1.c

## Purpose

`rc-it913x-v1.c` provides the `RC_MAP_IT913X_V1` remote-controller keymap for `it913x-v1 remote controller keytable`. It is a data-only rc-core map: decoded remote-control scan codes are translated into Linux input `KEY_*` events for the bundled receiver or board driver. The table has 52 scan-code entries; early entries include `0x61d601->KEY_VIDEO`, `0x61d602->KEY_NUMERIC_3`, `0x61d603->KEY_POWER`, `0x61d604->KEY_NUMERIC_1`, `0x61d605->KEY_NUMERIC_5`, `0x61d606->KEY_NUMERIC_6`. The represented controls cover numeric entry, power/input selection, navigation/menu, channel/volume, DVR/media transport, colored function keys.

## Important APIs, Types, and Functions

- `struct rc_map_table it913x_v1_rc[]` is the static scan-code-to-keycode table.
- `struct rc_map_list it913x_v1_map` publishes `.scan = it913x_v1_rc`, `.size = ARRAY_SIZE(it913x_v1_rc)`, `.rc_proto = RC_PROTO_NECX`, and `.name = RC_MAP_IT913X_V1` to rc-core.
- The module init function calls `rc_map_register()` and the exit function calls `rc_map_unregister()`, so the map is visible to rc-core only while the object is built in or the module is loaded.
- It has normal `module_init()`/`module_exit()` hooks.

## Control Flow

There is no active decode algorithm in this file. At build or module-load time, the map is registered with the rc-core map registry. A receiver driver later sets an `rc_dev->map_name` matching `RC_MAP_IT913X_V1` or userspace selects that map with tooling such as `ir-keytable`; rc-core then looks up decoded scancodes in `it913x_v1_rc` and emits the associated input keycodes. Unload or rc-core teardown unregisters the map, after which new lookups by name should fail or fall back to another configured map.

## State and Persistence Behavior

The persistent state is the compiled static table plus the registry node in rc-core. The file does not allocate per-device memory, take locks, touch hardware, or persist user settings. Runtime key state, repeat filtering, protocol decoding, and user remaps live in rc-core, the receiver driver, and input/ir-keytable configuration rather than in this keymap source.

## Dependencies and Integration Points

The file depends on `media/rc-map.h`, `linux/module.h`, Linux input `KEY_*` definitions, the `RC_MAP_*` string namespace, and the protocol enum `RC_PROTO_NECX`. It is built through `drivers/media/rc/keymaps/Makefile` when `CONFIG_RC_MAP` is enabled, except for CEC-style integration if noted above. Board, USB, PCI, CEC, or platform IR drivers integrate with it by naming `RC_MAP_IT913X_V1` as their default map.

## Risks and Edge Cases

Incorrect scancodes, wrong `KEY_*` assignments, a mismatched `.rc_proto`, or a stale `.name` break user-visible remote buttons without producing compile errors. The declared protocol `RC_PROTO_NECX` tells rc-core which decoded scancode namespace this map expects. Table ordering is not semantically important for lookups, but duplicate or vendor-overloaded scancodes should be reviewed carefully. The map can also drift from the v4l-utils userspace copy, causing different behavior between built-in maps and maps loaded from userspace.

## Test Signals

Useful checks include compiling the keymap with `CONFIG_RC_MAP=y` and `=m`, loading/unloading the generated module where applicable, confirming `rc_map_register()` exposes `RC_MAP_IT913X_V1`, using `ir-keytable -r` or equivalent rc-core introspection to inspect the map, and pressing representative numeric, navigation, volume/channel, power, and media keys on the target remote. Protocol-specific tests should verify that decoded `RC_PROTO_NECX` scancodes match the table values and that unknown buttons do not alias to unsafe actions such as power or record.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-it913x-v1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-it913x-v2.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-it913x-v2.c

## Purpose

`rc-it913x-v2.c` provides the `RC_MAP_IT913X_V2` remote-controller keymap for `it913x-v2 remote controller keytable`. It is a data-only rc-core map: decoded remote-control scan codes are translated into Linux input `KEY_*` events for the bundled receiver or board driver. The table has 47 scan-code entries; early entries include `0x807f12->KEY_POWER2`, `0x807f1a->KEY_VIDEO`, `0x807f1e->KEY_MUTE`, `0x807f01->KEY_RECORD`, `0x807f02->KEY_CHANNELUP`, `0x807f03->KEY_TIME`. The represented controls cover numeric entry, power/input selection, channel/volume, DVR/media transport, teletext/EPG/application keys.

## Important APIs, Types, and Functions

- `struct rc_map_table it913x_v2_rc[]` is the static scan-code-to-keycode table.
- `struct rc_map_list it913x_v2_map` publishes `.scan = it913x_v2_rc`, `.size = ARRAY_SIZE(it913x_v2_rc)`, `.rc_proto = RC_PROTO_NECX`, and `.name = RC_MAP_IT913X_V2` to rc-core.
- The module init function calls `rc_map_register()` and the exit function calls `rc_map_unregister()`, so the map is visible to rc-core only while the object is built in or the module is loaded.
- It has normal `module_init()`/`module_exit()` hooks.

## Control Flow

There is no active decode algorithm in this file. At build or module-load time, the map is registered with the rc-core map registry. A receiver driver later sets an `rc_dev->map_name` matching `RC_MAP_IT913X_V2` or userspace selects that map with tooling such as `ir-keytable`; rc-core then looks up decoded scancodes in `it913x_v2_rc` and emits the associated input keycodes. Unload or rc-core teardown unregisters the map, after which new lookups by name should fail or fall back to another configured map.

## State and Persistence Behavior

The persistent state is the compiled static table plus the registry node in rc-core. The file does not allocate per-device memory, take locks, touch hardware, or persist user settings. Runtime key state, repeat filtering, protocol decoding, and user remaps live in rc-core, the receiver driver, and input/ir-keytable configuration rather than in this keymap source.

## Dependencies and Integration Points

The file depends on `media/rc-map.h`, `linux/module.h`, Linux input `KEY_*` definitions, the `RC_MAP_*` string namespace, and the protocol enum `RC_PROTO_NECX`. It is built through `drivers/media/rc/keymaps/Makefile` when `CONFIG_RC_MAP` is enabled, except for CEC-style integration if noted above. Board, USB, PCI, CEC, or platform IR drivers integrate with it by naming `RC_MAP_IT913X_V2` as their default map.

## Risks and Edge Cases

Incorrect scancodes, wrong `KEY_*` assignments, a mismatched `.rc_proto`, or a stale `.name` break user-visible remote buttons without producing compile errors. Duplicate scancodes are present (0x866b18); this is usually intentional only when aliases map to the same key. The declared protocol `RC_PROTO_NECX` tells rc-core which decoded scancode namespace this map expects. Table ordering is not semantically important for lookups, but duplicate or vendor-overloaded scancodes should be reviewed carefully. The map can also drift from the v4l-utils userspace copy, causing different behavior between built-in maps and maps loaded from userspace.

## Test Signals

Useful checks include compiling the keymap with `CONFIG_RC_MAP=y` and `=m`, loading/unloading the generated module where applicable, confirming `rc_map_register()` exposes `RC_MAP_IT913X_V2`, using `ir-keytable -r` or equivalent rc-core introspection to inspect the map, and pressing representative numeric, navigation, volume/channel, power, and media keys on the target remote. Protocol-specific tests should verify that decoded `RC_PROTO_NECX` scancodes match the table values and that unknown buttons do not alias to unsafe actions such as power or record.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-it913x-v2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-kaiomy.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-kaiomy.c

## Purpose

`rc-kaiomy.c` provides the `RC_MAP_KAIOMY` remote-controller keymap for `Kaiomy TVnPC U2 remote controller keytable`. It is a data-only rc-core map: decoded remote-control scan codes are translated into Linux input `KEY_*` events for the bundled receiver or board driver. The table has 32 scan-code entries; early entries include `0x43->KEY_POWER2`, `0x01->KEY_LIST`, `0x0b->KEY_ZOOM`, `0x03->KEY_POWER`, `0x04->KEY_NUMERIC_1`, `0x08->KEY_NUMERIC_2`. The represented controls cover numeric entry, power/input selection, navigation/menu, channel/volume, DVR/media transport, colored function keys.

## Important APIs, Types, and Functions

- `struct rc_map_table kaiomy[]` is the static scan-code-to-keycode table.
- `struct rc_map_list kaiomy_map` publishes `.scan = kaiomy`, `.size = ARRAY_SIZE(kaiomy)`, `.rc_proto = RC_PROTO_UNKNOWN`, and `.name = RC_MAP_KAIOMY` to rc-core.
- The module init function calls `rc_map_register()` and the exit function calls `rc_map_unregister()`, so the map is visible to rc-core only while the object is built in or the module is loaded.
- It has normal `module_init()`/`module_exit()` hooks.

## Control Flow

There is no active decode algorithm in this file. At build or module-load time, the map is registered with the rc-core map registry. A receiver driver later sets an `rc_dev->map_name` matching `RC_MAP_KAIOMY` or userspace selects that map with tooling such as `ir-keytable`; rc-core then looks up decoded scancodes in `kaiomy` and emits the associated input keycodes. Unload or rc-core teardown unregisters the map, after which new lookups by name should fail or fall back to another configured map.

## State and Persistence Behavior

The persistent state is the compiled static table plus the registry node in rc-core. The file does not allocate per-device memory, take locks, touch hardware, or persist user settings. Runtime key state, repeat filtering, protocol decoding, and user remaps live in rc-core, the receiver driver, and input/ir-keytable configuration rather than in this keymap source.

## Dependencies and Integration Points

The file depends on `media/rc-map.h`, `linux/module.h`, Linux input `KEY_*` definitions, the `RC_MAP_*` string namespace, and the protocol enum `RC_PROTO_UNKNOWN`. It is built through `drivers/media/rc/keymaps/Makefile` when `CONFIG_RC_MAP` is enabled, except for CEC-style integration if noted above. Board, USB, PCI, CEC, or platform IR drivers integrate with it by naming `RC_MAP_KAIOMY` as their default map.

## Risks and Edge Cases

Incorrect scancodes, wrong `KEY_*` assignments, a mismatched `.rc_proto`, or a stale `.name` break user-visible remote buttons without producing compile errors. Because the protocol is `RC_PROTO_UNKNOWN`, correctness depends on the consuming hardware driver or legacy decoder path supplying matching scancodes. Table ordering is not semantically important for lookups, but duplicate or vendor-overloaded scancodes should be reviewed carefully. The map can also drift from the v4l-utils userspace copy, causing different behavior between built-in maps and maps loaded from userspace.

## Test Signals

Useful checks include compiling the keymap with `CONFIG_RC_MAP=y` and `=m`, loading/unloading the generated module where applicable, confirming `rc_map_register()` exposes `RC_MAP_KAIOMY`, using `ir-keytable -r` or equivalent rc-core introspection to inspect the map, and pressing representative numeric, navigation, volume/channel, power, and media keys on the target remote. Protocol-specific tests should verify that decoded `RC_PROTO_UNKNOWN` scancodes match the table values and that unknown buttons do not alias to unsafe actions such as power or record.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-kaiomy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-khadas.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-khadas.c

## Purpose

`rc-khadas.c` provides the `RC_MAP_KHADAS` remote-controller keymap for `Khadas VIM/EDGE SBC remote controller keytable`. It is a data-only rc-core map: decoded remote-control scan codes are translated into Linux input `KEY_*` events for the bundled receiver or board driver. The table has 12 scan-code entries; early entries include `0x14->KEY_POWER`, `0x03->KEY_UP`, `0x02->KEY_DOWN`, `0x0e->KEY_LEFT`, `0x1a->KEY_RIGHT`, `0x07->KEY_OK`. The represented controls cover power/input selection, navigation/menu, channel/volume.

## Important APIs, Types, and Functions

- `struct rc_map_table khadas[]` is the static scan-code-to-keycode table.
- `struct rc_map_list khadas_map` publishes `.scan = khadas`, `.size = ARRAY_SIZE(khadas)`, `.rc_proto = RC_PROTO_NEC`, and `.name = RC_MAP_KHADAS` to rc-core.
- The module init function calls `rc_map_register()` and the exit function calls `rc_map_unregister()`, so the map is visible to rc-core only while the object is built in or the module is loaded.
- It has normal `module_init()`/`module_exit()` hooks.

## Control Flow

There is no active decode algorithm in this file. At build or module-load time, the map is registered with the rc-core map registry. A receiver driver later sets an `rc_dev->map_name` matching `RC_MAP_KHADAS` or userspace selects that map with tooling such as `ir-keytable`; rc-core then looks up decoded scancodes in `khadas` and emits the associated input keycodes. Unload or rc-core teardown unregisters the map, after which new lookups by name should fail or fall back to another configured map.

## State and Persistence Behavior

The persistent state is the compiled static table plus the registry node in rc-core. The file does not allocate per-device memory, take locks, touch hardware, or persist user settings. Runtime key state, repeat filtering, protocol decoding, and user remaps live in rc-core, the receiver driver, and input/ir-keytable configuration rather than in this keymap source.

## Dependencies and Integration Points

The file depends on `media/rc-map.h`, `linux/module.h`, Linux input `KEY_*` definitions, the `RC_MAP_*` string namespace, and the protocol enum `RC_PROTO_NEC`. It is built through `drivers/media/rc/keymaps/Makefile` when `CONFIG_RC_MAP` is enabled, except for CEC-style integration if noted above. Board, USB, PCI, CEC, or platform IR drivers integrate with it by naming `RC_MAP_KHADAS` as their default map.

## Risks and Edge Cases

Incorrect scancodes, wrong `KEY_*` assignments, a mismatched `.rc_proto`, or a stale `.name` break user-visible remote buttons without producing compile errors. The declared protocol `RC_PROTO_NEC` tells rc-core which decoded scancode namespace this map expects. Table ordering is not semantically important for lookups, but duplicate or vendor-overloaded scancodes should be reviewed carefully. The map can also drift from the v4l-utils userspace copy, causing different behavior between built-in maps and maps loaded from userspace.

## Test Signals

Useful checks include compiling the keymap with `CONFIG_RC_MAP=y` and `=m`, loading/unloading the generated module where applicable, confirming `rc_map_register()` exposes `RC_MAP_KHADAS`, using `ir-keytable -r` or equivalent rc-core introspection to inspect the map, and pressing representative numeric, navigation, volume/channel, power, and media keys on the target remote. Protocol-specific tests should verify that decoded `RC_PROTO_NEC` scancodes match the table values and that unknown buttons do not alias to unsafe actions such as power or record.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-khadas.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-khamsin.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-khamsin.c

## Purpose

`rc-khamsin.c` provides the `RC_MAP_KHAMSIN` remote-controller keymap for `KHAMSIN remote controller keytable`. It is a data-only rc-core map: decoded remote-control scan codes are translated into Linux input `KEY_*` events for the bundled receiver or board driver. The table has 29 scan-code entries; early entries include `0x70702->KEY_POWER`, `0x70701->KEY_VIDEO`, `0x7076c->KEY_RED`, `0x70714->KEY_GREEN`, `0x70715->KEY_YELLOW`, `0x70716->KEY_BLUE`. The represented controls cover numeric entry, power/input selection, navigation/menu, channel/volume, colored function keys, teletext/EPG/application keys.

## Important APIs, Types, and Functions

- `struct rc_map_table khamsin[]` is the static scan-code-to-keycode table.
- `struct rc_map_list khamsin_map` publishes `.scan = khamsin`, `.size = ARRAY_SIZE(khamsin)`, `.rc_proto = RC_PROTO_NECX`, and `.name = RC_MAP_KHAMSIN` to rc-core.
- The module init function calls `rc_map_register()` and the exit function calls `rc_map_unregister()`, so the map is visible to rc-core only while the object is built in or the module is loaded.
- It has normal `module_init()`/`module_exit()` hooks.

## Control Flow

There is no active decode algorithm in this file. At build or module-load time, the map is registered with the rc-core map registry. A receiver driver later sets an `rc_dev->map_name` matching `RC_MAP_KHAMSIN` or userspace selects that map with tooling such as `ir-keytable`; rc-core then looks up decoded scancodes in `khamsin` and emits the associated input keycodes. Unload or rc-core teardown unregisters the map, after which new lookups by name should fail or fall back to another configured map.

## State and Persistence Behavior

The persistent state is the compiled static table plus the registry node in rc-core. The file does not allocate per-device memory, take locks, touch hardware, or persist user settings. Runtime key state, repeat filtering, protocol decoding, and user remaps live in rc-core, the receiver driver, and input/ir-keytable configuration rather than in this keymap source.

## Dependencies and Integration Points

The file depends on `media/rc-map.h`, `linux/module.h`, Linux input `KEY_*` definitions, the `RC_MAP_*` string namespace, and the protocol enum `RC_PROTO_NECX`. It is built through `drivers/media/rc/keymaps/Makefile` when `CONFIG_RC_MAP` is enabled, except for CEC-style integration if noted above. Board, USB, PCI, CEC, or platform IR drivers integrate with it by naming `RC_MAP_KHAMSIN` as their default map.

## Risks and Edge Cases

Incorrect scancodes, wrong `KEY_*` assignments, a mismatched `.rc_proto`, or a stale `.name` break user-visible remote buttons without producing compile errors. The declared protocol `RC_PROTO_NECX` tells rc-core which decoded scancode namespace this map expects. Table ordering is not semantically important for lookups, but duplicate or vendor-overloaded scancodes should be reviewed carefully. The map can also drift from the v4l-utils userspace copy, causing different behavior between built-in maps and maps loaded from userspace.

## Test Signals

Useful checks include compiling the keymap with `CONFIG_RC_MAP=y` and `=m`, loading/unloading the generated module where applicable, confirming `rc_map_register()` exposes `RC_MAP_KHAMSIN`, using `ir-keytable -r` or equivalent rc-core introspection to inspect the map, and pressing representative numeric, navigation, volume/channel, power, and media keys on the target remote. Protocol-specific tests should verify that decoded `RC_PROTO_NECX` scancodes match the table values and that unknown buttons do not alias to unsafe actions such as power or record.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-khamsin.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-kworld-315u.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-kworld-315u.c

## Purpose

`rc-kworld-315u.c` provides the `RC_MAP_KWORLD_315U` remote-controller keymap for `Kworld 315U remote controller keytable`. It is a data-only rc-core map: decoded remote-control scan codes are translated into Linux input `KEY_*` events for the bundled receiver or board driver. The table has 32 scan-code entries; early entries include `0x6143->KEY_POWER`, `0x6101->KEY_VIDEO`, `0x610b->KEY_ZOOM`, `0x6103->KEY_POWER2`, `0x6104->KEY_NUMERIC_1`, `0x6108->KEY_NUMERIC_2`. The represented controls cover numeric entry, power/input selection, navigation/menu, channel/volume, DVR/media transport, colored function keys.

## Important APIs, Types, and Functions

- `struct rc_map_table kworld_315u[]` is the static scan-code-to-keycode table.
- `struct rc_map_list kworld_315u_map` publishes `.scan = kworld_315u`, `.size = ARRAY_SIZE(kworld_315u)`, `.rc_proto = RC_PROTO_NEC`, and `.name = RC_MAP_KWORLD_315U` to rc-core.
- The module init function calls `rc_map_register()` and the exit function calls `rc_map_unregister()`, so the map is visible to rc-core only while the object is built in or the module is loaded.
- It has normal `module_init()`/`module_exit()` hooks.

## Control Flow

There is no active decode algorithm in this file. At build or module-load time, the map is registered with the rc-core map registry. A receiver driver later sets an `rc_dev->map_name` matching `RC_MAP_KWORLD_315U` or userspace selects that map with tooling such as `ir-keytable`; rc-core then looks up decoded scancodes in `kworld_315u` and emits the associated input keycodes. Unload or rc-core teardown unregisters the map, after which new lookups by name should fail or fall back to another configured map.

## State and Persistence Behavior

The persistent state is the compiled static table plus the registry node in rc-core. The file does not allocate per-device memory, take locks, touch hardware, or persist user settings. Runtime key state, repeat filtering, protocol decoding, and user remaps live in rc-core, the receiver driver, and input/ir-keytable configuration rather than in this keymap source.

## Dependencies and Integration Points

The file depends on `media/rc-map.h`, `linux/module.h`, Linux input `KEY_*` definitions, the `RC_MAP_*` string namespace, and the protocol enum `RC_PROTO_NEC`. It is built through `drivers/media/rc/keymaps/Makefile` when `CONFIG_RC_MAP` is enabled, except for CEC-style integration if noted above. Board, USB, PCI, CEC, or platform IR drivers integrate with it by naming `RC_MAP_KWORLD_315U` as their default map.

## Risks and Edge Cases

Incorrect scancodes, wrong `KEY_*` assignments, a mismatched `.rc_proto`, or a stale `.name` break user-visible remote buttons without producing compile errors. The declared protocol `RC_PROTO_NEC` tells rc-core which decoded scancode namespace this map expects. Table ordering is not semantically important for lookups, but duplicate or vendor-overloaded scancodes should be reviewed carefully. The map can also drift from the v4l-utils userspace copy, causing different behavior between built-in maps and maps loaded from userspace.

## Test Signals

Useful checks include compiling the keymap with `CONFIG_RC_MAP=y` and `=m`, loading/unloading the generated module where applicable, confirming `rc_map_register()` exposes `RC_MAP_KWORLD_315U`, using `ir-keytable -r` or equivalent rc-core introspection to inspect the map, and pressing representative numeric, navigation, volume/channel, power, and media keys on the target remote. Protocol-specific tests should verify that decoded `RC_PROTO_NEC` scancodes match the table values and that unknown buttons do not alias to unsafe actions such as power or record.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-kworld-315u.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-kworld-pc150u.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-kworld-pc150u.c

## Purpose

`rc-kworld-pc150u.c` provides the `RC_MAP_KWORLD_PC150U` remote-controller keymap for `Kworld PC150-U remote controller keytable`. It is a data-only rc-core map: decoded remote-control scan codes are translated into Linux input `KEY_*` events for the bundled receiver or board driver. The table has 44 scan-code entries; early entries include `0x0c->KEY_MEDIA`, `0x16->KEY_EJECTCLOSECD`, `0x1d->KEY_POWER2`, `0x00->KEY_NUMERIC_1`, `0x01->KEY_NUMERIC_2`, `0x02->KEY_NUMERIC_3`. The represented controls cover numeric entry, power/input selection, navigation/menu, channel/volume, DVR/media transport, colored function keys, teletext/EPG/application keys.

## Important APIs, Types, and Functions

- `struct rc_map_table kworld_pc150u[]` is the static scan-code-to-keycode table.
- `struct rc_map_list kworld_pc150u_map` publishes `.scan = kworld_pc150u`, `.size = ARRAY_SIZE(kworld_pc150u)`, `.rc_proto = RC_PROTO_UNKNOWN`, and `.name = RC_MAP_KWORLD_PC150U` to rc-core.
- The module init function calls `rc_map_register()` and the exit function calls `rc_map_unregister()`, so the map is visible to rc-core only while the object is built in or the module is loaded.
- It has normal `module_init()`/`module_exit()` hooks.

## Control Flow

There is no active decode algorithm in this file. At build or module-load time, the map is registered with the rc-core map registry. A receiver driver later sets an `rc_dev->map_name` matching `RC_MAP_KWORLD_PC150U` or userspace selects that map with tooling such as `ir-keytable`; rc-core then looks up decoded scancodes in `kworld_pc150u` and emits the associated input keycodes. Unload or rc-core teardown unregisters the map, after which new lookups by name should fail or fall back to another configured map.

## State and Persistence Behavior

The persistent state is the compiled static table plus the registry node in rc-core. The file does not allocate per-device memory, take locks, touch hardware, or persist user settings. Runtime key state, repeat filtering, protocol decoding, and user remaps live in rc-core, the receiver driver, and input/ir-keytable configuration rather than in this keymap source.

## Dependencies and Integration Points

The file depends on `media/rc-map.h`, `linux/module.h`, Linux input `KEY_*` definitions, the `RC_MAP_*` string namespace, and the protocol enum `RC_PROTO_UNKNOWN`. It is built through `drivers/media/rc/keymaps/Makefile` when `CONFIG_RC_MAP` is enabled, except for CEC-style integration if noted above. Board, USB, PCI, CEC, or platform IR drivers integrate with it by naming `RC_MAP_KWORLD_PC150U` as their default map.

## Risks and Edge Cases

Incorrect scancodes, wrong `KEY_*` assignments, a mismatched `.rc_proto`, or a stale `.name` break user-visible remote buttons without producing compile errors. Because the protocol is `RC_PROTO_UNKNOWN`, correctness depends on the consuming hardware driver or legacy decoder path supplying matching scancodes. Table ordering is not semantically important for lookups, but duplicate or vendor-overloaded scancodes should be reviewed carefully. The map can also drift from the v4l-utils userspace copy, causing different behavior between built-in maps and maps loaded from userspace.

## Test Signals

Useful checks include compiling the keymap with `CONFIG_RC_MAP=y` and `=m`, loading/unloading the generated module where applicable, confirming `rc_map_register()` exposes `RC_MAP_KWORLD_PC150U`, using `ir-keytable -r` or equivalent rc-core introspection to inspect the map, and pressing representative numeric, navigation, volume/channel, power, and media keys on the target remote. Protocol-specific tests should verify that decoded `RC_PROTO_UNKNOWN` scancodes match the table values and that unknown buttons do not alias to unsafe actions such as power or record.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-kworld-pc150u.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-kworld-plus-tv-analog.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-kworld-plus-tv-analog.c

## Purpose

`rc-kworld-plus-tv-analog.c` provides the `RC_MAP_KWORLD_PLUS_TV_ANALOG` remote-controller keymap for `Kworld Plus TV Analog Lite PCI IR remote controller keytable`. It is a data-only rc-core map: decoded remote-control scan codes are translated into Linux input `KEY_*` events for the bundled receiver or board driver. The table has 31 scan-code entries; early entries include `0x0c->KEY_MEDIA`, `0x16->KEY_CLOSECD`, `0x1d->KEY_POWER2`, `0x00->KEY_NUMERIC_1`, `0x01->KEY_NUMERIC_2`, `0x02->KEY_NUMERIC_3`. The represented controls cover numeric entry, power/input selection, navigation/menu, channel/volume, DVR/media transport, colored function keys, teletext/EPG/application keys.

## Important APIs, Types, and Functions

- `struct rc_map_table kworld_plus_tv_analog[]` is the static scan-code-to-keycode table.
- `struct rc_map_list kworld_plus_tv_analog_map` publishes `.scan = kworld_plus_tv_analog`, `.size = ARRAY_SIZE(kworld_plus_tv_analog)`, `.rc_proto = RC_PROTO_UNKNOWN`, and `.name = RC_MAP_KWORLD_PLUS_TV_ANALOG` to rc-core.
- The module init function calls `rc_map_register()` and the exit function calls `rc_map_unregister()`, so the map is visible to rc-core only while the object is built in or the module is loaded.
- It has normal `module_init()`/`module_exit()` hooks.

## Control Flow

There is no active decode algorithm in this file. At build or module-load time, the map is registered with the rc-core map registry. A receiver driver later sets an `rc_dev->map_name` matching `RC_MAP_KWORLD_PLUS_TV_ANALOG` or userspace selects that map with tooling such as `ir-keytable`; rc-core then looks up decoded scancodes in `kworld_plus_tv_analog` and emits the associated input keycodes. Unload or rc-core teardown unregisters the map, after which new lookups by name should fail or fall back to another configured map.

## State and Persistence Behavior

The persistent state is the compiled static table plus the registry node in rc-core. The file does not allocate per-device memory, take locks, touch hardware, or persist user settings. Runtime key state, repeat filtering, protocol decoding, and user remaps live in rc-core, the receiver driver, and input/ir-keytable configuration rather than in this keymap source.

## Dependencies and Integration Points

The file depends on `media/rc-map.h`, `linux/module.h`, Linux input `KEY_*` definitions, the `RC_MAP_*` string namespace, and the protocol enum `RC_PROTO_UNKNOWN`. It is built through `drivers/media/rc/keymaps/Makefile` when `CONFIG_RC_MAP` is enabled, except for CEC-style integration if noted above. Board, USB, PCI, CEC, or platform IR drivers integrate with it by naming `RC_MAP_KWORLD_PLUS_TV_ANALOG` as their default map.

## Risks and Edge Cases

Incorrect scancodes, wrong `KEY_*` assignments, a mismatched `.rc_proto`, or a stale `.name` break user-visible remote buttons without producing compile errors. Because the protocol is `RC_PROTO_UNKNOWN`, correctness depends on the consuming hardware driver or legacy decoder path supplying matching scancodes. Table ordering is not semantically important for lookups, but duplicate or vendor-overloaded scancodes should be reviewed carefully. The map can also drift from the v4l-utils userspace copy, causing different behavior between built-in maps and maps loaded from userspace.

## Test Signals

Useful checks include compiling the keymap with `CONFIG_RC_MAP=y` and `=m`, loading/unloading the generated module where applicable, confirming `rc_map_register()` exposes `RC_MAP_KWORLD_PLUS_TV_ANALOG`, using `ir-keytable -r` or equivalent rc-core introspection to inspect the map, and pressing representative numeric, navigation, volume/channel, power, and media keys on the target remote. Protocol-specific tests should verify that decoded `RC_PROTO_UNKNOWN` scancodes match the table values and that unknown buttons do not alias to unsafe actions such as power or record.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-kworld-plus-tv-analog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-leadtek-y04g0051.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-leadtek-y04g0051.c

## Purpose

`rc-leadtek-y04g0051.c` provides the `RC_MAP_LEADTEK_Y04G0051` remote-controller keymap for `LeadTek Y04G0051 remote controller keytable`. It is a data-only rc-core map: decoded remote-control scan codes are translated into Linux input `KEY_*` events for the bundled receiver or board driver. The table has 50 scan-code entries; early entries include `0x0300->KEY_POWER2`, `0x0303->KEY_SCREEN`, `0x0304->KEY_RIGHT`, `0x0305->KEY_NUMERIC_1`, `0x0306->KEY_NUMERIC_2`, `0x0307->KEY_NUMERIC_3`. The represented controls cover numeric entry, power/input selection, navigation/menu, channel/volume, DVR/media transport, colored function keys, teletext/EPG/application keys.

## Important APIs, Types, and Functions

- `struct rc_map_table leadtek_y04g0051[]` is the static scan-code-to-keycode table.
- `struct rc_map_list leadtek_y04g0051_map` publishes `.scan = leadtek_y04g0051`, `.size = ARRAY_SIZE(leadtek_y04g0051)`, `.rc_proto = RC_PROTO_NEC`, and `.name = RC_MAP_LEADTEK_Y04G0051` to rc-core.
- The module init function calls `rc_map_register()` and the exit function calls `rc_map_unregister()`, so the map is visible to rc-core only while the object is built in or the module is loaded.
- It has normal `module_init()`/`module_exit()` hooks.

## Control Flow

There is no active decode algorithm in this file. At build or module-load time, the map is registered with the rc-core map registry. A receiver driver later sets an `rc_dev->map_name` matching `RC_MAP_LEADTEK_Y04G0051` or userspace selects that map with tooling such as `ir-keytable`; rc-core then looks up decoded scancodes in `leadtek_y04g0051` and emits the associated input keycodes. Unload or rc-core teardown unregisters the map, after which new lookups by name should fail or fall back to another configured map.

## State and Persistence Behavior

The persistent state is the compiled static table plus the registry node in rc-core. The file does not allocate per-device memory, take locks, touch hardware, or persist user settings. Runtime key state, repeat filtering, protocol decoding, and user remaps live in rc-core, the receiver driver, and input/ir-keytable configuration rather than in this keymap source.

## Dependencies and Integration Points

The file depends on `media/rc-map.h`, `linux/module.h`, Linux input `KEY_*` definitions, the `RC_MAP_*` string namespace, and the protocol enum `RC_PROTO_NEC`. It is built through `drivers/media/rc/keymaps/Makefile` when `CONFIG_RC_MAP` is enabled, except for CEC-style integration if noted above. Board, USB, PCI, CEC, or platform IR drivers integrate with it by naming `RC_MAP_LEADTEK_Y04G0051` as their default map.

## Risks and Edge Cases

Incorrect scancodes, wrong `KEY_*` assignments, a mismatched `.rc_proto`, or a stale `.name` break user-visible remote buttons without producing compile errors. The declared protocol `RC_PROTO_NEC` tells rc-core which decoded scancode namespace this map expects. Table ordering is not semantically important for lookups, but duplicate or vendor-overloaded scancodes should be reviewed carefully. The map can also drift from the v4l-utils userspace copy, causing different behavior between built-in maps and maps loaded from userspace.

## Test Signals

Useful checks include compiling the keymap with `CONFIG_RC_MAP=y` and `=m`, loading/unloading the generated module where applicable, confirming `rc_map_register()` exposes `RC_MAP_LEADTEK_Y04G0051`, using `ir-keytable -r` or equivalent rc-core introspection to inspect the map, and pressing representative numeric, navigation, volume/channel, power, and media keys on the target remote. Protocol-specific tests should verify that decoded `RC_PROTO_NEC` scancodes match the table values and that unknown buttons do not alias to unsafe actions such as power or record.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-leadtek-y04g0051.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-lme2510.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-lme2510.c

## Purpose

`rc-lme2510.c` provides the `RC_MAP_LME2510` remote-controller keymap for `LME2510 remote controller keytable`. It is a data-only rc-core map: decoded remote-control scan codes are translated into Linux input `KEY_*` events for the bundled receiver or board driver. The table has 66 scan-code entries; early entries include `0xef12ba45->KEY_NUMERIC_0`, `0xef12a05f->KEY_NUMERIC_1`, `0xef12af50->KEY_NUMERIC_2`, `0xef12a25d->KEY_NUMERIC_3`, `0xef12be41->KEY_NUMERIC_4`, `0xef12f50a->KEY_NUMERIC_5`. The represented controls cover numeric entry, power/input selection, channel/volume, DVR/media transport, teletext/EPG/application keys.

## Important APIs, Types, and Functions

- `struct rc_map_table lme2510_rc[]` is the static scan-code-to-keycode table.
- `struct rc_map_list lme2510_map` publishes `.scan = lme2510_rc`, `.size = ARRAY_SIZE(lme2510_rc)`, `.rc_proto = RC_PROTO_NEC`, and `.name = RC_MAP_LME2510` to rc-core.
- The module init function calls `rc_map_register()` and the exit function calls `rc_map_unregister()`, so the map is visible to rc-core only while the object is built in or the module is loaded.
- It has normal `module_init()`/`module_exit()` hooks.

## Control Flow

There is no active decode algorithm in this file. At build or module-load time, the map is registered with the rc-core map registry. A receiver driver later sets an `rc_dev->map_name` matching `RC_MAP_LME2510` or userspace selects that map with tooling such as `ir-keytable`; rc-core then looks up decoded scancodes in `lme2510_rc` and emits the associated input keycodes. Unload or rc-core teardown unregisters the map, after which new lookups by name should fail or fall back to another configured map.

## State and Persistence Behavior

The persistent state is the compiled static table plus the registry node in rc-core. The file does not allocate per-device memory, take locks, touch hardware, or persist user settings. Runtime key state, repeat filtering, protocol decoding, and user remaps live in rc-core, the receiver driver, and input/ir-keytable configuration rather than in this keymap source.

## Dependencies and Integration Points

The file depends on `media/rc-map.h`, `linux/module.h`, Linux input `KEY_*` definitions, the `RC_MAP_*` string namespace, and the protocol enum `RC_PROTO_NEC`. It is built through `drivers/media/rc/keymaps/Makefile` when `CONFIG_RC_MAP` is enabled, except for CEC-style integration if noted above. Board, USB, PCI, CEC, or platform IR drivers integrate with it by naming `RC_MAP_LME2510` as their default map.

## Risks and Edge Cases

Incorrect scancodes, wrong `KEY_*` assignments, a mismatched `.rc_proto`, or a stale `.name` break user-visible remote buttons without producing compile errors. The declared protocol `RC_PROTO_NEC` tells rc-core which decoded scancode namespace this map expects. Table ordering is not semantically important for lookups, but duplicate or vendor-overloaded scancodes should be reviewed carefully. The map can also drift from the v4l-utils userspace copy, causing different behavior between built-in maps and maps loaded from userspace.

## Test Signals

Useful checks include compiling the keymap with `CONFIG_RC_MAP=y` and `=m`, loading/unloading the generated module where applicable, confirming `rc_map_register()` exposes `RC_MAP_LME2510`, using `ir-keytable -r` or equivalent rc-core introspection to inspect the map, and pressing representative numeric, navigation, volume/channel, power, and media keys on the target remote. Protocol-specific tests should verify that decoded `RC_PROTO_NEC` scancodes match the table values and that unknown buttons do not alias to unsafe actions such as power or record.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-lme2510.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-manli.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-manli.c

## Purpose

`rc-manli.c` provides the `RC_MAP_MANLI` remote-controller keymap for `MANLI MTV00[0x0c] and BeholdTV 40[13] remote controller keytable`. It is a data-only rc-core map: decoded remote-control scan codes are translated into Linux input `KEY_*` events for the bundled receiver or board driver. The table has 31 scan-code entries; early entries include `0x1c->KEY_RADIO`, `0x12->KEY_POWER`, `0x01->KEY_NUMERIC_1`, `0x02->KEY_NUMERIC_2`, `0x03->KEY_NUMERIC_3`, `0x04->KEY_NUMERIC_4`. The represented controls cover numeric entry, power/input selection, navigation/menu, channel/volume, teletext/EPG/application keys.

## Important APIs, Types, and Functions

- `struct rc_map_table manli[]` is the static scan-code-to-keycode table.
- `struct rc_map_list manli_map` publishes `.scan = manli`, `.size = ARRAY_SIZE(manli)`, `.rc_proto = RC_PROTO_UNKNOWN`, and `.name = RC_MAP_MANLI` to rc-core.
- The module init function calls `rc_map_register()` and the exit function calls `rc_map_unregister()`, so the map is visible to rc-core only while the object is built in or the module is loaded.
- It has normal `module_init()`/`module_exit()` hooks.

## Control Flow

There is no active decode algorithm in this file. At build or module-load time, the map is registered with the rc-core map registry. A receiver driver later sets an `rc_dev->map_name` matching `RC_MAP_MANLI` or userspace selects that map with tooling such as `ir-keytable`; rc-core then looks up decoded scancodes in `manli` and emits the associated input keycodes. Unload or rc-core teardown unregisters the map, after which new lookups by name should fail or fall back to another configured map.

## State and Persistence Behavior

The persistent state is the compiled static table plus the registry node in rc-core. The file does not allocate per-device memory, take locks, touch hardware, or persist user settings. Runtime key state, repeat filtering, protocol decoding, and user remaps live in rc-core, the receiver driver, and input/ir-keytable configuration rather than in this keymap source.

## Dependencies and Integration Points

The file depends on `media/rc-map.h`, `linux/module.h`, Linux input `KEY_*` definitions, the `RC_MAP_*` string namespace, and the protocol enum `RC_PROTO_UNKNOWN`. It is built through `drivers/media/rc/keymaps/Makefile` when `CONFIG_RC_MAP` is enabled, except for CEC-style integration if noted above. Board, USB, PCI, CEC, or platform IR drivers integrate with it by naming `RC_MAP_MANLI` as their default map.

## Risks and Edge Cases

Incorrect scancodes, wrong `KEY_*` assignments, a mismatched `.rc_proto`, or a stale `.name` break user-visible remote buttons without producing compile errors. Because the protocol is `RC_PROTO_UNKNOWN`, correctness depends on the consuming hardware driver or legacy decoder path supplying matching scancodes. Table ordering is not semantically important for lookups, but duplicate or vendor-overloaded scancodes should be reviewed carefully. The map can also drift from the v4l-utils userspace copy, causing different behavior between built-in maps and maps loaded from userspace.

## Test Signals

Useful checks include compiling the keymap with `CONFIG_RC_MAP=y` and `=m`, loading/unloading the generated module where applicable, confirming `rc_map_register()` exposes `RC_MAP_MANLI`, using `ir-keytable -r` or equivalent rc-core introspection to inspect the map, and pressing representative numeric, navigation, volume/channel, power, and media keys on the target remote. Protocol-specific tests should verify that decoded `RC_PROTO_UNKNOWN` scancodes match the table values and that unknown buttons do not alias to unsafe actions such as power or record.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-manli.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-mecool-kii-pro.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-mecool-kii-pro.c

## Purpose

`rc-mecool-kii-pro.c` provides the `RC_MAP_MECOOL_KII_PRO` remote-controller keymap for `Mecool Kii Pro remote controller keytable`. It is a data-only rc-core map: decoded remote-control scan codes are translated into Linux input `KEY_*` events for the bundled receiver or board driver. The table has 45 scan-code entries; early entries include `0x59->KEY_POWER`, `0x19->KEY_MUTE`, `0x42->KEY_RED`, `0x40->KEY_GREEN`, `0x00->KEY_YELLOW`, `0x03->KEY_BLUE`. The represented controls cover numeric entry, power/input selection, navigation/menu, channel/volume, DVR/media transport, colored function keys, teletext/EPG/application keys.

## Important APIs, Types, and Functions

- `struct rc_map_table mecool_kii_pro[]` is the static scan-code-to-keycode table.
- `struct rc_map_list mecool_kii_pro_map` publishes `.scan = mecool_kii_pro`, `.size = ARRAY_SIZE(mecool_kii_pro)`, `.rc_proto = RC_PROTO_NEC`, and `.name = RC_MAP_MECOOL_KII_PRO` to rc-core.
- The module init function calls `rc_map_register()` and the exit function calls `rc_map_unregister()`, so the map is visible to rc-core only while the object is built in or the module is loaded.
- It has normal `module_init()`/`module_exit()` hooks.

## Control Flow

There is no active decode algorithm in this file. At build or module-load time, the map is registered with the rc-core map registry. A receiver driver later sets an `rc_dev->map_name` matching `RC_MAP_MECOOL_KII_PRO` or userspace selects that map with tooling such as `ir-keytable`; rc-core then looks up decoded scancodes in `mecool_kii_pro` and emits the associated input keycodes. Unload or rc-core teardown unregisters the map, after which new lookups by name should fail or fall back to another configured map.

## State and Persistence Behavior

The persistent state is the compiled static table plus the registry node in rc-core. The file does not allocate per-device memory, take locks, touch hardware, or persist user settings. Runtime key state, repeat filtering, protocol decoding, and user remaps live in rc-core, the receiver driver, and input/ir-keytable configuration rather than in this keymap source.

## Dependencies and Integration Points

The file depends on `media/rc-map.h`, `linux/module.h`, Linux input `KEY_*` definitions, the `RC_MAP_*` string namespace, and the protocol enum `RC_PROTO_NEC`. It is built through `drivers/media/rc/keymaps/Makefile` when `CONFIG_RC_MAP` is enabled, except for CEC-style integration if noted above. Board, USB, PCI, CEC, or platform IR drivers integrate with it by naming `RC_MAP_MECOOL_KII_PRO` as their default map.

## Risks and Edge Cases

Incorrect scancodes, wrong `KEY_*` assignments, a mismatched `.rc_proto`, or a stale `.name` break user-visible remote buttons without producing compile errors. The declared protocol `RC_PROTO_NEC` tells rc-core which decoded scancode namespace this map expects. Table ordering is not semantically important for lookups, but duplicate or vendor-overloaded scancodes should be reviewed carefully. The map can also drift from the v4l-utils userspace copy, causing different behavior between built-in maps and maps loaded from userspace.

## Test Signals

Useful checks include compiling the keymap with `CONFIG_RC_MAP=y` and `=m`, loading/unloading the generated module where applicable, confirming `rc_map_register()` exposes `RC_MAP_MECOOL_KII_PRO`, using `ir-keytable -r` or equivalent rc-core introspection to inspect the map, and pressing representative numeric, navigation, volume/channel, power, and media keys on the target remote. Protocol-specific tests should verify that decoded `RC_PROTO_NEC` scancodes match the table values and that unknown buttons do not alias to unsafe actions such as power or record.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-mecool-kii-pro.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-mecool-kiii-pro.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-mecool-kiii-pro.c

## Purpose

`rc-mecool-kiii-pro.c` provides the `RC_MAP_MECOOL_KIII_PRO` remote-controller keymap for `Mecool Kiii Pro remote controller keytable`. It is a data-only rc-core map: decoded remote-control scan codes are translated into Linux input `KEY_*` events for the bundled receiver or board driver. The table has 43 scan-code entries; early entries include `0x59->KEY_POWER`, `0x52->KEY_1`, `0x50->KEY_2`, `0x10->KEY_3`, `0x56->KEY_4`, `0x54->KEY_5`. The represented controls cover numeric entry, power/input selection, navigation/menu, channel/volume, DVR/media transport, colored function keys, teletext/EPG/application keys.

## Important APIs, Types, and Functions

- `struct rc_map_table mecool_kiii_pro[]` is the static scan-code-to-keycode table.
- `struct rc_map_list mecool_kiii_pro_map` publishes `.scan = mecool_kiii_pro`, `.size = ARRAY_SIZE(mecool_kiii_pro)`, `.rc_proto = RC_PROTO_NEC`, and `.name = RC_MAP_MECOOL_KIII_PRO` to rc-core.
- The module init function calls `rc_map_register()` and the exit function calls `rc_map_unregister()`, so the map is visible to rc-core only while the object is built in or the module is loaded.
- It has normal `module_init()`/`module_exit()` hooks.

## Control Flow

There is no active decode algorithm in this file. At build or module-load time, the map is registered with the rc-core map registry. A receiver driver later sets an `rc_dev->map_name` matching `RC_MAP_MECOOL_KIII_PRO` or userspace selects that map with tooling such as `ir-keytable`; rc-core then looks up decoded scancodes in `mecool_kiii_pro` and emits the associated input keycodes. Unload or rc-core teardown unregisters the map, after which new lookups by name should fail or fall back to another configured map.

## State and Persistence Behavior

The persistent state is the compiled static table plus the registry node in rc-core. The file does not allocate per-device memory, take locks, touch hardware, or persist user settings. Runtime key state, repeat filtering, protocol decoding, and user remaps live in rc-core, the receiver driver, and input/ir-keytable configuration rather than in this keymap source.

## Dependencies and Integration Points

The file depends on `media/rc-map.h`, `linux/module.h`, Linux input `KEY_*` definitions, the `RC_MAP_*` string namespace, and the protocol enum `RC_PROTO_NEC`. It is built through `drivers/media/rc/keymaps/Makefile` when `CONFIG_RC_MAP` is enabled, except for CEC-style integration if noted above. Board, USB, PCI, CEC, or platform IR drivers integrate with it by naming `RC_MAP_MECOOL_KIII_PRO` as their default map.

## Risks and Edge Cases

Incorrect scancodes, wrong `KEY_*` assignments, a mismatched `.rc_proto`, or a stale `.name` break user-visible remote buttons without producing compile errors. The declared protocol `RC_PROTO_NEC` tells rc-core which decoded scancode namespace this map expects. Table ordering is not semantically important for lookups, but duplicate or vendor-overloaded scancodes should be reviewed carefully. The map can also drift from the v4l-utils userspace copy, causing different behavior between built-in maps and maps loaded from userspace.

## Test Signals

Useful checks include compiling the keymap with `CONFIG_RC_MAP=y` and `=m`, loading/unloading the generated module where applicable, confirming `rc_map_register()` exposes `RC_MAP_MECOOL_KIII_PRO`, using `ir-keytable -r` or equivalent rc-core introspection to inspect the map, and pressing representative numeric, navigation, volume/channel, power, and media keys on the target remote. Protocol-specific tests should verify that decoded `RC_PROTO_NEC` scancodes match the table values and that unknown buttons do not alias to unsafe actions such as power or record.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-mecool-kiii-pro.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-medion-x10-digitainer.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-medion-x10-digitainer.c

## Purpose

`rc-medion-x10-digitainer.c` provides the `RC_MAP_MEDION_X10_DIGITAINER` remote-controller keymap for `Medion X10 RF remote keytable (Digitainer variant)`. It is a data-only rc-core map: decoded remote-control scan codes are translated into Linux input `KEY_*` events for the bundled receiver or board driver. The table has 49 scan-code entries; early entries include `0x02->KEY_POWER`, `0x2c->KEY_TV`, `0x2d->KEY_VIDEO`, `0x04->KEY_DVD`, `0x16->KEY_TEXT`, `0x06->KEY_AUDIO`. The represented controls cover numeric entry, power/input selection, navigation/menu, channel/volume, DVR/media transport, colored function keys, teletext/EPG/application keys.

## Important APIs, Types, and Functions

- `struct rc_map_table medion_x10_digitainer[]` is the static scan-code-to-keycode table.
- `struct rc_map_list medion_x10_digitainer_map` publishes `.scan = medion_x10_digitainer`, `.size = ARRAY_SIZE(medion_x10_digitainer)`, `.rc_proto = RC_PROTO_OTHER`, and `.name = RC_MAP_MEDION_X10_DIGITAINER` to rc-core.
- The module init function calls `rc_map_register()` and the exit function calls `rc_map_unregister()`, so the map is visible to rc-core only while the object is built in or the module is loaded.
- It has normal `module_init()`/`module_exit()` hooks.

## Control Flow

There is no active decode algorithm in this file. At build or module-load time, the map is registered with the rc-core map registry. A receiver driver later sets an `rc_dev->map_name` matching `RC_MAP_MEDION_X10_DIGITAINER` or userspace selects that map with tooling such as `ir-keytable`; rc-core then looks up decoded scancodes in `medion_x10_digitainer` and emits the associated input keycodes. Unload or rc-core teardown unregisters the map, after which new lookups by name should fail or fall back to another configured map.

## State and Persistence Behavior

The persistent state is the compiled static table plus the registry node in rc-core. The file does not allocate per-device memory, take locks, touch hardware, or persist user settings. Runtime key state, repeat filtering, protocol decoding, and user remaps live in rc-core, the receiver driver, and input/ir-keytable configuration rather than in this keymap source.

## Dependencies and Integration Points

The file depends on `media/rc-map.h`, `linux/module.h`, Linux input `KEY_*` definitions, the `RC_MAP_*` string namespace, and the protocol enum `RC_PROTO_OTHER`. It is built through `drivers/media/rc/keymaps/Makefile` when `CONFIG_RC_MAP` is enabled, except for CEC-style integration if noted above. Board, USB, PCI, CEC, or platform IR drivers integrate with it by naming `RC_MAP_MEDION_X10_DIGITAINER` as their default map.

## Risks and Edge Cases

Incorrect scancodes, wrong `KEY_*` assignments, a mismatched `.rc_proto`, or a stale `.name` break user-visible remote buttons without producing compile errors. `RC_PROTO_OTHER` marks a non-standard transport, so consumers should treat scancode shape as device-specific rather than decoded NEC/RC5/etc. Table ordering is not semantically important for lookups, but duplicate or vendor-overloaded scancodes should be reviewed carefully. The map can also drift from the v4l-utils userspace copy, causing different behavior between built-in maps and maps loaded from userspace.

## Test Signals

Useful checks include compiling the keymap with `CONFIG_RC_MAP=y` and `=m`, loading/unloading the generated module where applicable, confirming `rc_map_register()` exposes `RC_MAP_MEDION_X10_DIGITAINER`, using `ir-keytable -r` or equivalent rc-core introspection to inspect the map, and pressing representative numeric, navigation, volume/channel, power, and media keys on the target remote. Protocol-specific tests should verify that decoded `RC_PROTO_OTHER` scancodes match the table values and that unknown buttons do not alias to unsafe actions such as power or record.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-medion-x10-digitainer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-medion-x10-or2x.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-medion-x10-or2x.c

## Purpose

`rc-medion-x10-or2x.c` provides the `RC_MAP_MEDION_X10_OR2X` remote-controller keymap for `Medion X10 OR22/OR24 RF remote keytable`. It is a data-only rc-core map: decoded remote-control scan codes are translated into Linux input `KEY_*` events for the bundled receiver or board driver. The table has 45 scan-code entries; early entries include `0x02->KEY_POWER`, `0x16->KEY_TEXT`, `0x09->KEY_VOLUMEUP`, `0x08->KEY_VOLUMEDOWN`, `0x00->KEY_MUTE`, `0x0b->KEY_CHANNELUP`. The represented controls cover numeric entry, power/input selection, navigation/menu, channel/volume, DVR/media transport, colored function keys, teletext/EPG/application keys.

## Important APIs, Types, and Functions

- `struct rc_map_table medion_x10_or2x[]` is the static scan-code-to-keycode table.
- `struct rc_map_list medion_x10_or2x_map` publishes `.scan = medion_x10_or2x`, `.size = ARRAY_SIZE(medion_x10_or2x)`, `.rc_proto = RC_PROTO_OTHER`, and `.name = RC_MAP_MEDION_X10_OR2X` to rc-core.
- The module init function calls `rc_map_register()` and the exit function calls `rc_map_unregister()`, so the map is visible to rc-core only while the object is built in or the module is loaded.
- It has normal `module_init()`/`module_exit()` hooks.

## Control Flow

There is no active decode algorithm in this file. At build or module-load time, the map is registered with the rc-core map registry. A receiver driver later sets an `rc_dev->map_name` matching `RC_MAP_MEDION_X10_OR2X` or userspace selects that map with tooling such as `ir-keytable`; rc-core then looks up decoded scancodes in `medion_x10_or2x` and emits the associated input keycodes. Unload or rc-core teardown unregisters the map, after which new lookups by name should fail or fall back to another configured map.

## State and Persistence Behavior

The persistent state is the compiled static table plus the registry node in rc-core. The file does not allocate per-device memory, take locks, touch hardware, or persist user settings. Runtime key state, repeat filtering, protocol decoding, and user remaps live in rc-core, the receiver driver, and input/ir-keytable configuration rather than in this keymap source.

## Dependencies and Integration Points

The file depends on `media/rc-map.h`, `linux/module.h`, Linux input `KEY_*` definitions, the `RC_MAP_*` string namespace, and the protocol enum `RC_PROTO_OTHER`. It is built through `drivers/media/rc/keymaps/Makefile` when `CONFIG_RC_MAP` is enabled, except for CEC-style integration if noted above. Board, USB, PCI, CEC, or platform IR drivers integrate with it by naming `RC_MAP_MEDION_X10_OR2X` as their default map.

## Risks and Edge Cases

Incorrect scancodes, wrong `KEY_*` assignments, a mismatched `.rc_proto`, or a stale `.name` break user-visible remote buttons without producing compile errors. `RC_PROTO_OTHER` marks a non-standard transport, so consumers should treat scancode shape as device-specific rather than decoded NEC/RC5/etc. Table ordering is not semantically important for lookups, but duplicate or vendor-overloaded scancodes should be reviewed carefully. The map can also drift from the v4l-utils userspace copy, causing different behavior between built-in maps and maps loaded from userspace.

## Test Signals

Useful checks include compiling the keymap with `CONFIG_RC_MAP=y` and `=m`, loading/unloading the generated module where applicable, confirming `rc_map_register()` exposes `RC_MAP_MEDION_X10_OR2X`, using `ir-keytable -r` or equivalent rc-core introspection to inspect the map, and pressing representative numeric, navigation, volume/channel, power, and media keys on the target remote. Protocol-specific tests should verify that decoded `RC_PROTO_OTHER` scancodes match the table values and that unknown buttons do not alias to unsafe actions such as power or record.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-medion-x10-or2x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-medion-x10.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-medion-x10.c

## Purpose

`rc-medion-x10.c` provides the `RC_MAP_MEDION_X10` remote-controller keymap for `Medion X10 RF remote controller keytable`. It is a data-only rc-core map: decoded remote-control scan codes are translated into Linux input `KEY_*` events for the bundled receiver or board driver. The table has 53 scan-code entries; early entries include `0x2c->KEY_TV`, `0x2d->KEY_VCR`, `0x04->KEY_DVD`, `0x06->KEY_AUDIO`, `0x2e->KEY_RADIO`, `0x05->KEY_DIRECTORY`. The represented controls cover numeric entry, power/input selection, navigation/menu, channel/volume, DVR/media transport, colored function keys, teletext/EPG/application keys.

## Important APIs, Types, and Functions

- `struct rc_map_table medion_x10[]` is the static scan-code-to-keycode table.
- `struct rc_map_list medion_x10_map` publishes `.scan = medion_x10`, `.size = ARRAY_SIZE(medion_x10)`, `.rc_proto = RC_PROTO_OTHER`, and `.name = RC_MAP_MEDION_X10` to rc-core.
- The module init function calls `rc_map_register()` and the exit function calls `rc_map_unregister()`, so the map is visible to rc-core only while the object is built in or the module is loaded.
- It has normal `module_init()`/`module_exit()` hooks.

## Control Flow

There is no active decode algorithm in this file. At build or module-load time, the map is registered with the rc-core map registry. A receiver driver later sets an `rc_dev->map_name` matching `RC_MAP_MEDION_X10` or userspace selects that map with tooling such as `ir-keytable`; rc-core then looks up decoded scancodes in `medion_x10` and emits the associated input keycodes. Unload or rc-core teardown unregisters the map, after which new lookups by name should fail or fall back to another configured map.

## State and Persistence Behavior

The persistent state is the compiled static table plus the registry node in rc-core. The file does not allocate per-device memory, take locks, touch hardware, or persist user settings. Runtime key state, repeat filtering, protocol decoding, and user remaps live in rc-core, the receiver driver, and input/ir-keytable configuration rather than in this keymap source.

## Dependencies and Integration Points

The file depends on `media/rc-map.h`, `linux/module.h`, Linux input `KEY_*` definitions, the `RC_MAP_*` string namespace, and the protocol enum `RC_PROTO_OTHER`. It is built through `drivers/media/rc/keymaps/Makefile` when `CONFIG_RC_MAP` is enabled, except for CEC-style integration if noted above. Board, USB, PCI, CEC, or platform IR drivers integrate with it by naming `RC_MAP_MEDION_X10` as their default map.

## Risks and Edge Cases

Incorrect scancodes, wrong `KEY_*` assignments, a mismatched `.rc_proto`, or a stale `.name` break user-visible remote buttons without producing compile errors. `RC_PROTO_OTHER` marks a non-standard transport, so consumers should treat scancode shape as device-specific rather than decoded NEC/RC5/etc. Table ordering is not semantically important for lookups, but duplicate or vendor-overloaded scancodes should be reviewed carefully. The map can also drift from the v4l-utils userspace copy, causing different behavior between built-in maps and maps loaded from userspace.

## Test Signals

Useful checks include compiling the keymap with `CONFIG_RC_MAP=y` and `=m`, loading/unloading the generated module where applicable, confirming `rc_map_register()` exposes `RC_MAP_MEDION_X10`, using `ir-keytable -r` or equivalent rc-core introspection to inspect the map, and pressing representative numeric, navigation, volume/channel, power, and media keys on the target remote. Protocol-specific tests should verify that decoded `RC_PROTO_OTHER` scancodes match the table values and that unknown buttons do not alias to unsafe actions such as power or record.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-medion-x10.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-minix-neo.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-minix-neo.c

## Purpose

`rc-minix-neo.c` provides the `RC_MAP_MINIX_NEO` remote-controller keymap for `Minix NEO remote controller keytable`. It is a data-only rc-core map: decoded remote-control scan codes are translated into Linux input `KEY_*` events for the bundled receiver or board driver. The table has 12 scan-code entries; early entries include `0x118->KEY_POWER`, `0x146->KEY_UP`, `0x116->KEY_DOWN`, `0x147->KEY_LEFT`, `0x115->KEY_RIGHT`, `0x155->KEY_ENTER`. The represented controls cover power/input selection, navigation/menu, channel/volume.

## Important APIs, Types, and Functions

- `struct rc_map_table minix_neo[]` is the static scan-code-to-keycode table.
- `struct rc_map_list minix_neo_map` publishes `.scan = minix_neo`, `.size = ARRAY_SIZE(minix_neo)`, `.rc_proto = RC_PROTO_NEC`, and `.name = RC_MAP_MINIX_NEO` to rc-core.
- The module init function calls `rc_map_register()` and the exit function calls `rc_map_unregister()`, so the map is visible to rc-core only while the object is built in or the module is loaded.
- It has normal `module_init()`/`module_exit()` hooks.

## Control Flow

There is no active decode algorithm in this file. At build or module-load time, the map is registered with the rc-core map registry. A receiver driver later sets an `rc_dev->map_name` matching `RC_MAP_MINIX_NEO` or userspace selects that map with tooling such as `ir-keytable`; rc-core then looks up decoded scancodes in `minix_neo` and emits the associated input keycodes. Unload or rc-core teardown unregisters the map, after which new lookups by name should fail or fall back to another configured map.

## State and Persistence Behavior

The persistent state is the compiled static table plus the registry node in rc-core. The file does not allocate per-device memory, take locks, touch hardware, or persist user settings. Runtime key state, repeat filtering, protocol decoding, and user remaps live in rc-core, the receiver driver, and input/ir-keytable configuration rather than in this keymap source.

## Dependencies and Integration Points

The file depends on `media/rc-map.h`, `linux/module.h`, Linux input `KEY_*` definitions, the `RC_MAP_*` string namespace, and the protocol enum `RC_PROTO_NEC`. It is built through `drivers/media/rc/keymaps/Makefile` when `CONFIG_RC_MAP` is enabled, except for CEC-style integration if noted above. Board, USB, PCI, CEC, or platform IR drivers integrate with it by naming `RC_MAP_MINIX_NEO` as their default map.

## Risks and Edge Cases

Incorrect scancodes, wrong `KEY_*` assignments, a mismatched `.rc_proto`, or a stale `.name` break user-visible remote buttons without producing compile errors. The declared protocol `RC_PROTO_NEC` tells rc-core which decoded scancode namespace this map expects. Table ordering is not semantically important for lookups, but duplicate or vendor-overloaded scancodes should be reviewed carefully. The map can also drift from the v4l-utils userspace copy, causing different behavior between built-in maps and maps loaded from userspace.

## Test Signals

Useful checks include compiling the keymap with `CONFIG_RC_MAP=y` and `=m`, loading/unloading the generated module where applicable, confirming `rc_map_register()` exposes `RC_MAP_MINIX_NEO`, using `ir-keytable -r` or equivalent rc-core introspection to inspect the map, and pressing representative numeric, navigation, volume/channel, power, and media keys on the target remote. Protocol-specific tests should verify that decoded `RC_PROTO_NEC` scancodes match the table values and that unknown buttons do not alias to unsafe actions such as power or record.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-minix-neo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-msi-digivox-ii.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-msi-digivox-ii.c

## Purpose

`rc-msi-digivox-ii.c` provides the `RC_MAP_MSI_DIGIVOX_II` remote-controller keymap for `MSI DIGIVOX mini II remote controller keytable`. It is a data-only rc-core map: decoded remote-control scan codes are translated into Linux input `KEY_*` events for the bundled receiver or board driver. The table has 18 scan-code entries; early entries include `0x0302->KEY_NUMERIC_2`, `0x0303->KEY_UP`, `0x0304->KEY_NUMERIC_3`, `0x0305->KEY_CHANNELDOWN`, `0x0308->KEY_NUMERIC_5`, `0x0309->KEY_NUMERIC_0`. The represented controls cover numeric entry, power/input selection, navigation/menu, channel/volume.

## Important APIs, Types, and Functions

- `struct rc_map_table msi_digivox_ii[]` is the static scan-code-to-keycode table.
- `struct rc_map_list msi_digivox_ii_map` publishes `.scan = msi_digivox_ii`, `.size = ARRAY_SIZE(msi_digivox_ii)`, `.rc_proto = RC_PROTO_NEC`, and `.name = RC_MAP_MSI_DIGIVOX_II` to rc-core.
- The module init function calls `rc_map_register()` and the exit function calls `rc_map_unregister()`, so the map is visible to rc-core only while the object is built in or the module is loaded.
- It has normal `module_init()`/`module_exit()` hooks.

## Control Flow

There is no active decode algorithm in this file. At build or module-load time, the map is registered with the rc-core map registry. A receiver driver later sets an `rc_dev->map_name` matching `RC_MAP_MSI_DIGIVOX_II` or userspace selects that map with tooling such as `ir-keytable`; rc-core then looks up decoded scancodes in `msi_digivox_ii` and emits the associated input keycodes. Unload or rc-core teardown unregisters the map, after which new lookups by name should fail or fall back to another configured map.

## State and Persistence Behavior

The persistent state is the compiled static table plus the registry node in rc-core. The file does not allocate per-device memory, take locks, touch hardware, or persist user settings. Runtime key state, repeat filtering, protocol decoding, and user remaps live in rc-core, the receiver driver, and input/ir-keytable configuration rather than in this keymap source.

## Dependencies and Integration Points

The file depends on `media/rc-map.h`, `linux/module.h`, Linux input `KEY_*` definitions, the `RC_MAP_*` string namespace, and the protocol enum `RC_PROTO_NEC`. It is built through `drivers/media/rc/keymaps/Makefile` when `CONFIG_RC_MAP` is enabled, except for CEC-style integration if noted above. Board, USB, PCI, CEC, or platform IR drivers integrate with it by naming `RC_MAP_MSI_DIGIVOX_II` as their default map.

## Risks and Edge Cases

Incorrect scancodes, wrong `KEY_*` assignments, a mismatched `.rc_proto`, or a stale `.name` break user-visible remote buttons without producing compile errors. The declared protocol `RC_PROTO_NEC` tells rc-core which decoded scancode namespace this map expects. Table ordering is not semantically important for lookups, but duplicate or vendor-overloaded scancodes should be reviewed carefully. The map can also drift from the v4l-utils userspace copy, causing different behavior between built-in maps and maps loaded from userspace.

## Test Signals

Useful checks include compiling the keymap with `CONFIG_RC_MAP=y` and `=m`, loading/unloading the generated module where applicable, confirming `rc_map_register()` exposes `RC_MAP_MSI_DIGIVOX_II`, using `ir-keytable -r` or equivalent rc-core introspection to inspect the map, and pressing representative numeric, navigation, volume/channel, power, and media keys on the target remote. Protocol-specific tests should verify that decoded `RC_PROTO_NEC` scancodes match the table values and that unknown buttons do not alias to unsafe actions such as power or record.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-msi-digivox-ii.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-msi-digivox-iii.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-msi-digivox-iii.c

## Purpose

`rc-msi-digivox-iii.c` provides the `RC_MAP_MSI_DIGIVOX_III` remote-controller keymap for `MSI DIGIVOX mini III remote controller keytable`. It is a data-only rc-core map: decoded remote-control scan codes are translated into Linux input `KEY_*` events for the bundled receiver or board driver. The table has 32 scan-code entries; early entries include `0x61d601->KEY_VIDEO`, `0x61d602->KEY_NUMERIC_3`, `0x61d603->KEY_POWER`, `0x61d604->KEY_NUMERIC_1`, `0x61d605->KEY_NUMERIC_5`, `0x61d606->KEY_NUMERIC_6`. The represented controls cover numeric entry, power/input selection, navigation/menu, channel/volume, DVR/media transport, colored function keys.

## Important APIs, Types, and Functions

- `struct rc_map_table msi_digivox_iii[]` is the static scan-code-to-keycode table.
- `struct rc_map_list msi_digivox_iii_map` publishes `.scan = msi_digivox_iii`, `.size = ARRAY_SIZE(msi_digivox_iii)`, `.rc_proto = RC_PROTO_NECX`, and `.name = RC_MAP_MSI_DIGIVOX_III` to rc-core.
- The module init function calls `rc_map_register()` and the exit function calls `rc_map_unregister()`, so the map is visible to rc-core only while the object is built in or the module is loaded.
- It has normal `module_init()`/`module_exit()` hooks.

## Control Flow

There is no active decode algorithm in this file. At build or module-load time, the map is registered with the rc-core map registry. A receiver driver later sets an `rc_dev->map_name` matching `RC_MAP_MSI_DIGIVOX_III` or userspace selects that map with tooling such as `ir-keytable`; rc-core then looks up decoded scancodes in `msi_digivox_iii` and emits the associated input keycodes. Unload or rc-core teardown unregisters the map, after which new lookups by name should fail or fall back to another configured map.

## State and Persistence Behavior

The persistent state is the compiled static table plus the registry node in rc-core. The file does not allocate per-device memory, take locks, touch hardware, or persist user settings. Runtime key state, repeat filtering, protocol decoding, and user remaps live in rc-core, the receiver driver, and input/ir-keytable configuration rather than in this keymap source.

## Dependencies and Integration Points

The file depends on `media/rc-map.h`, `linux/module.h`, Linux input `KEY_*` definitions, the `RC_MAP_*` string namespace, and the protocol enum `RC_PROTO_NECX`. It is built through `drivers/media/rc/keymaps/Makefile` when `CONFIG_RC_MAP` is enabled, except for CEC-style integration if noted above. Board, USB, PCI, CEC, or platform IR drivers integrate with it by naming `RC_MAP_MSI_DIGIVOX_III` as their default map.

## Risks and Edge Cases

Incorrect scancodes, wrong `KEY_*` assignments, a mismatched `.rc_proto`, or a stale `.name` break user-visible remote buttons without producing compile errors. The declared protocol `RC_PROTO_NECX` tells rc-core which decoded scancode namespace this map expects. Table ordering is not semantically important for lookups, but duplicate or vendor-overloaded scancodes should be reviewed carefully. The map can also drift from the v4l-utils userspace copy, causing different behavior between built-in maps and maps loaded from userspace.

## Test Signals

Useful checks include compiling the keymap with `CONFIG_RC_MAP=y` and `=m`, loading/unloading the generated module where applicable, confirming `rc_map_register()` exposes `RC_MAP_MSI_DIGIVOX_III`, using `ir-keytable -r` or equivalent rc-core introspection to inspect the map, and pressing representative numeric, navigation, volume/channel, power, and media keys on the target remote. Protocol-specific tests should verify that decoded `RC_PROTO_NECX` scancodes match the table values and that unknown buttons do not alias to unsafe actions such as power or record.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-msi-digivox-iii.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-msi-tvanywhere-plus.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-msi-tvanywhere-plus.c

## Purpose

`rc-msi-tvanywhere-plus.c` provides the `RC_MAP_MSI_TVANYWHERE_PLUS` remote-controller keymap for `MSI TV@nywhere Plus remote controller keytable`. It is a data-only rc-core map: decoded remote-control scan codes are translated into Linux input `KEY_*` events for the bundled receiver or board driver. The table has 36 scan-code entries; early entries include `0x01->KEY_NUMERIC_1`, `0x0b->KEY_NUMERIC_2`, `0x1b->KEY_NUMERIC_3`, `0x05->KEY_NUMERIC_4`, `0x09->KEY_NUMERIC_5`, `0x15->KEY_NUMERIC_6`. The represented controls cover numeric entry, power/input selection, navigation/menu, channel/volume, DVR/media transport.

## Important APIs, Types, and Functions

- `struct rc_map_table msi_tvanywhere_plus[]` is the static scan-code-to-keycode table.
- `struct rc_map_list msi_tvanywhere_plus_map` publishes `.scan = msi_tvanywhere_plus`, `.size = ARRAY_SIZE(msi_tvanywhere_plus)`, `.rc_proto = RC_PROTO_UNKNOWN`, and `.name = RC_MAP_MSI_TVANYWHERE_PLUS` to rc-core.
- The module init function calls `rc_map_register()` and the exit function calls `rc_map_unregister()`, so the map is visible to rc-core only while the object is built in or the module is loaded.
- It has normal `module_init()`/`module_exit()` hooks.

## Control Flow

There is no active decode algorithm in this file. At build or module-load time, the map is registered with the rc-core map registry. A receiver driver later sets an `rc_dev->map_name` matching `RC_MAP_MSI_TVANYWHERE_PLUS` or userspace selects that map with tooling such as `ir-keytable`; rc-core then looks up decoded scancodes in `msi_tvanywhere_plus` and emits the associated input keycodes. Unload or rc-core teardown unregisters the map, after which new lookups by name should fail or fall back to another configured map.

## State and Persistence Behavior

The persistent state is the compiled static table plus the registry node in rc-core. The file does not allocate per-device memory, take locks, touch hardware, or persist user settings. Runtime key state, repeat filtering, protocol decoding, and user remaps live in rc-core, the receiver driver, and input/ir-keytable configuration rather than in this keymap source.

## Dependencies and Integration Points

The file depends on `media/rc-map.h`, `linux/module.h`, Linux input `KEY_*` definitions, the `RC_MAP_*` string namespace, and the protocol enum `RC_PROTO_UNKNOWN`. It is built through `drivers/media/rc/keymaps/Makefile` when `CONFIG_RC_MAP` is enabled, except for CEC-style integration if noted above. Board, USB, PCI, CEC, or platform IR drivers integrate with it by naming `RC_MAP_MSI_TVANYWHERE_PLUS` as their default map.

## Risks and Edge Cases

Incorrect scancodes, wrong `KEY_*` assignments, a mismatched `.rc_proto`, or a stale `.name` break user-visible remote buttons without producing compile errors. Because the protocol is `RC_PROTO_UNKNOWN`, correctness depends on the consuming hardware driver or legacy decoder path supplying matching scancodes. Table ordering is not semantically important for lookups, but duplicate or vendor-overloaded scancodes should be reviewed carefully. The map can also drift from the v4l-utils userspace copy, causing different behavior between built-in maps and maps loaded from userspace.

## Test Signals

Useful checks include compiling the keymap with `CONFIG_RC_MAP=y` and `=m`, loading/unloading the generated module where applicable, confirming `rc_map_register()` exposes `RC_MAP_MSI_TVANYWHERE_PLUS`, using `ir-keytable -r` or equivalent rc-core introspection to inspect the map, and pressing representative numeric, navigation, volume/channel, power, and media keys on the target remote. Protocol-specific tests should verify that decoded `RC_PROTO_UNKNOWN` scancodes match the table values and that unknown buttons do not alias to unsafe actions such as power or record.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-msi-tvanywhere-plus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-msi-tvanywhere.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-msi-tvanywhere.c

## Purpose

`rc-msi-tvanywhere.c` provides the `RC_MAP_MSI_TVANYWHERE` remote-controller keymap for `MSI TV@nywhere MASTER remote controller keytable`. It is a data-only rc-core map: decoded remote-control scan codes are translated into Linux input `KEY_*` events for the bundled receiver or board driver. The table has 24 scan-code entries; early entries include `0x00->KEY_NUMERIC_0`, `0x01->KEY_NUMERIC_1`, `0x02->KEY_NUMERIC_2`, `0x03->KEY_NUMERIC_3`, `0x04->KEY_NUMERIC_4`, `0x05->KEY_NUMERIC_5`. The represented controls cover numeric entry, power/input selection, navigation/menu, channel/volume, DVR/media transport.

## Important APIs, Types, and Functions

- `struct rc_map_table msi_tvanywhere[]` is the static scan-code-to-keycode table.
- `struct rc_map_list msi_tvanywhere_map` publishes `.scan = msi_tvanywhere`, `.size = ARRAY_SIZE(msi_tvanywhere)`, `.rc_proto = RC_PROTO_UNKNOWN`, and `.name = RC_MAP_MSI_TVANYWHERE` to rc-core.
- The module init function calls `rc_map_register()` and the exit function calls `rc_map_unregister()`, so the map is visible to rc-core only while the object is built in or the module is loaded.
- It has normal `module_init()`/`module_exit()` hooks.

## Control Flow

There is no active decode algorithm in this file. At build or module-load time, the map is registered with the rc-core map registry. A receiver driver later sets an `rc_dev->map_name` matching `RC_MAP_MSI_TVANYWHERE` or userspace selects that map with tooling such as `ir-keytable`; rc-core then looks up decoded scancodes in `msi_tvanywhere` and emits the associated input keycodes. Unload or rc-core teardown unregisters the map, after which new lookups by name should fail or fall back to another configured map.

## State and Persistence Behavior

The persistent state is the compiled static table plus the registry node in rc-core. The file does not allocate per-device memory, take locks, touch hardware, or persist user settings. Runtime key state, repeat filtering, protocol decoding, and user remaps live in rc-core, the receiver driver, and input/ir-keytable configuration rather than in this keymap source.

## Dependencies and Integration Points

The file depends on `media/rc-map.h`, `linux/module.h`, Linux input `KEY_*` definitions, the `RC_MAP_*` string namespace, and the protocol enum `RC_PROTO_UNKNOWN`. It is built through `drivers/media/rc/keymaps/Makefile` when `CONFIG_RC_MAP` is enabled, except for CEC-style integration if noted above. Board, USB, PCI, CEC, or platform IR drivers integrate with it by naming `RC_MAP_MSI_TVANYWHERE` as their default map.

## Risks and Edge Cases

Incorrect scancodes, wrong `KEY_*` assignments, a mismatched `.rc_proto`, or a stale `.name` break user-visible remote buttons without producing compile errors. Because the protocol is `RC_PROTO_UNKNOWN`, correctness depends on the consuming hardware driver or legacy decoder path supplying matching scancodes. Table ordering is not semantically important for lookups, but duplicate or vendor-overloaded scancodes should be reviewed carefully. The map can also drift from the v4l-utils userspace copy, causing different behavior between built-in maps and maps loaded from userspace.

## Test Signals

Useful checks include compiling the keymap with `CONFIG_RC_MAP=y` and `=m`, loading/unloading the generated module where applicable, confirming `rc_map_register()` exposes `RC_MAP_MSI_TVANYWHERE`, using `ir-keytable -r` or equivalent rc-core introspection to inspect the map, and pressing representative numeric, navigation, volume/channel, power, and media keys on the target remote. Protocol-specific tests should verify that decoded `RC_PROTO_UNKNOWN` scancodes match the table values and that unknown buttons do not alias to unsafe actions such as power or record.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-msi-tvanywhere.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-mygica-utv3.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-mygica-utv3.c

## Purpose

`rc-mygica-utv3.c` provides the `RC_MAP_MYGICA_UTV3` remote-controller keymap for `MyGica UTV3 Analog USB2.0 TV Box remote keytable`. It is a data-only rc-core map: decoded remote-control scan codes are translated into Linux input `KEY_*` events for the bundled receiver or board driver. The table has 28 scan-code entries; early entries include `0x0d->KEY_MUTE`, `0x38->KEY_VIDEO`, `0x14->KEY_RADIO`, `0x0c->KEY_POWER2`, `0x01->KEY_NUMERIC_1`, `0x02->KEY_NUMERIC_2`. The represented controls cover numeric entry, power/input selection, channel/volume, DVR/media transport.

## Important APIs, Types, and Functions

- `struct rc_map_table mygica_utv3[]` is the static scan-code-to-keycode table.
- `struct rc_map_list mygica_utv3_map` publishes `.scan = mygica_utv3`, `.size = ARRAY_SIZE(mygica_utv3)`, `.rc_proto = RC_PROTO_RC5`, and `.name = RC_MAP_MYGICA_UTV3` to rc-core.
- The module init function calls `rc_map_register()` and the exit function calls `rc_map_unregister()`, so the map is visible to rc-core only while the object is built in or the module is loaded.
- It has normal `module_init()`/`module_exit()` hooks.

## Control Flow

There is no active decode algorithm in this file. At build or module-load time, the map is registered with the rc-core map registry. A receiver driver later sets an `rc_dev->map_name` matching `RC_MAP_MYGICA_UTV3` or userspace selects that map with tooling such as `ir-keytable`; rc-core then looks up decoded scancodes in `mygica_utv3` and emits the associated input keycodes. Unload or rc-core teardown unregisters the map, after which new lookups by name should fail or fall back to another configured map.

## State and Persistence Behavior

The persistent state is the compiled static table plus the registry node in rc-core. The file does not allocate per-device memory, take locks, touch hardware, or persist user settings. Runtime key state, repeat filtering, protocol decoding, and user remaps live in rc-core, the receiver driver, and input/ir-keytable configuration rather than in this keymap source.

## Dependencies and Integration Points

The file depends on `media/rc-map.h`, `linux/module.h`, Linux input `KEY_*` definitions, the `RC_MAP_*` string namespace, and the protocol enum `RC_PROTO_RC5`. It is built through `drivers/media/rc/keymaps/Makefile` when `CONFIG_RC_MAP` is enabled, except for CEC-style integration if noted above. Board, USB, PCI, CEC, or platform IR drivers integrate with it by naming `RC_MAP_MYGICA_UTV3` as their default map.

## Risks and Edge Cases

Incorrect scancodes, wrong `KEY_*` assignments, a mismatched `.rc_proto`, or a stale `.name` break user-visible remote buttons without producing compile errors. The declared protocol `RC_PROTO_RC5` tells rc-core which decoded scancode namespace this map expects. Table ordering is not semantically important for lookups, but duplicate or vendor-overloaded scancodes should be reviewed carefully. The map can also drift from the v4l-utils userspace copy, causing different behavior between built-in maps and maps loaded from userspace.

## Test Signals

Useful checks include compiling the keymap with `CONFIG_RC_MAP=y` and `=m`, loading/unloading the generated module where applicable, confirming `rc_map_register()` exposes `RC_MAP_MYGICA_UTV3`, using `ir-keytable -r` or equivalent rc-core introspection to inspect the map, and pressing representative numeric, navigation, volume/channel, power, and media keys on the target remote. Protocol-specific tests should verify that decoded `RC_PROTO_RC5` scancodes match the table values and that unknown buttons do not alias to unsafe actions such as power or record.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-mygica-utv3.c -->
