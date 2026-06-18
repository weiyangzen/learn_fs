# Research: subset-b-005904

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pinctrl/pinconf-generic.h -->
# sources/distributed-fs/ceph-client/include/linux/pinctrl/pinconf-generic.h

Purpose: defines the generic pin configuration vocabulary used by the Linux pinctrl subsystem and the helper interface that converts firmware/Device Tree configuration nodes into pinctrl maps. It standardizes common electrical and low-power settings so drivers can share parsing, debug output, and packed config representation instead of inventing private properties for every controller.

Important APIs and types: `enum pin_config_param` enumerates generic parameters such as bias modes, open-drain/source/push-pull drive, drive strength in mA/uA, input debounce, Schmitt trigger, input/output enable, output impedance, power source, skew delay, sleep hardware state, and slew rate. `PIN_CONF_PACKED()`, `pinconf_to_config_param()`, `pinconf_to_config_argument()`, and `pinconf_to_config_packed()` encode a parameter in the low 8 bits and a 24-bit argument above it. `struct pin_config_item` describes debug-display metadata, while `struct pinconf_generic_params` maps firmware property names to generic params, defaults, and value tables. The DT helpers include `pinconf_generic_dt_subnode_to_map()`, `pinconf_generic_dt_node_to_map()`, `pinconf_generic_dt_free_map()`, and inline group/pin/all wrappers.

Control flow: pinctrl drivers that opt into generic pinconf hand firmware nodes to the parser; the parser allocates `struct pinctrl_map` entries with either group or pin config map types, packs each property as an `unsigned long`, and returns the map array to pinctrl core. The `*_group`, `*_pin`, and `*_all` wrappers select the desired `enum pinctrl_map_type`; passing `PIN_MAP_TYPE_INVALID` asks the parser to infer the map type from DT properties.

State and persistence: this header owns no runtime state. Packed config values are transient kernel data consumed during state selection and passed to controller callbacks. Persistence is external: firmware describes desired states and the hardware may retain or lose them depending on driver handling of `PIN_CONFIG_PERSIST_STATE`, sleep states, and controller reset behavior.

Dependencies and integration points: depends on `linux/types.h`, `linux/pinctrl/machine.h`, `device_node`, `pinctrl_dev`, and `pinctrl_map`. It integrates Device Tree parsing, generic pin configuration, debugfs display tables, and controller-specific `pinconf_ops` implementations.

Risks and test signals: risks include truncating arguments above 24 bits, drivers interpreting units inconsistently, custom parameters colliding with `PIN_CONFIG_END`, incorrect map type inference, and missing cleanup for allocated map entries. Test signals include DT parsing for pin and group configs, debugfs decoding, custom parameter tables, disabled/unsupported parameter error paths, suspend/resume pin states, and compile coverage with and without `CONFIG_GENERIC_PINCONF`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pinctrl/pinconf-generic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pinctrl/pinconf.h -->
# sources/distributed-fs/ceph-client/include/linux/pinctrl/pinconf.h

Purpose: declares the driver callback contract for pin configuration-capable pinctrl controllers. It is the generic-to-driver boundary for reading and applying electrical pin settings on individual pins or groups.

Important APIs and types: `struct pinconf_ops` contains optional `is_generic` under `CONFIG_GENERIC_PINCONF`, pin-level `pin_config_get()` and `pin_config_set()`, group-level `pin_config_group_get()` and `pin_config_group_set()`, and debugfs hooks `pin_config_dbg_show()`, `pin_config_group_dbg_show()`, and `pin_config_config_dbg_show()`.

Control flow: pinctrl core resolves a requested state into config values and calls the relevant pin or group setter with an array of packed `unsigned long` configs. Query/debug paths call the getter or debug hooks. The documented error convention distinguishes unsupported settings (`-ENOTSUPP`) from settings that exist but are currently disabled (`-EINVAL`).

State and persistence: this header stores no state. Runtime state lives in the pin controller driver and hardware registers; config callbacks mutate hardware as part of pinctrl state selection and may be replayed by PM resume flows.

Dependencies and integration points: depends on `pinctrl_dev` and `seq_file` forward declarations and integrates with `pinctrl_desc.confops`, generic pinconf packing, pinctrl state selection, and debugfs reporting.

Risks and test signals: risks include callbacks accepting unsupported configs silently, failing to apply all configs atomically enough for hardware requirements, inconsistent pin vs group behavior, and stale debug display. Test by applying known DT states, reading back configs, exercising unsupported/disabled parameters, group setters, and debugfs output across generic and custom pinconf drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pinctrl/pinconf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pinctrl/pinctrl-state.h -->
# sources/distributed-fs/ceph-client/include/linux/pinctrl/pinctrl-state.h

Purpose: centralizes the standard pinctrl state names used by consumers, hogs, and power-management code.

Important APIs and types: defines `PINCTRL_STATE_DEFAULT`, `PINCTRL_STATE_INIT`, `PINCTRL_STATE_IDLE`, and `PINCTRL_STATE_SLEEP` as the canonical string names `"default"`, `"init"`, `"idle"`, and `"sleep"`.

Control flow: device core and drivers request/select these named states through the pinctrl consumer API. `init` can be applied before probe to avoid glitches, then transitioned to `default`; `idle` is commonly selected for runtime suspend/idle; `sleep` is selected for system suspend.

State and persistence: no state is stored here. The names map to firmware-described pinctrl state objects, and hardware persistence depends on the controller and PM path.

Dependencies and integration points: it is a dependency-light naming contract between board firmware, device drivers, pinctrl core, runtime PM, system suspend/resume, and pin hog setup.

Risks and test signals: risks are naming drift in firmware, missing states causing fallback behavior, and incorrect `init`/`default` sequencing that can glitch external signals. Test by booting with hog states, probing devices with `init`, runtime suspend/resume selecting `idle`, and system suspend/resume selecting `sleep`/`default`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pinctrl/pinctrl-state.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pinctrl/pinctrl.h -->
# sources/distributed-fs/ceph-client/include/linux/pinctrl/pinctrl.h

Purpose: declares the core provider-side pinctrl interface: pin and group descriptors, GPIO range mapping, controller operations, registration APIs, and function metadata.

Important APIs and types: `struct pingroup` and `PINCTRL_PINGROUP()` describe named pin groups. `struct pinctrl_pin_desc`, `PINCTRL_PIN()`, and `PINCTRL_PIN_ANON()` describe controller pins. `struct pinctrl_gpio_range` maps GPIO number ranges to controller pin ranges. `struct pinctrl_ops` exposes group enumeration, group pin lookup, debug display, and DT map parsing/freeing. `struct pinctrl_desc` ties together pins, `pctlops`, `pmxops`, `confops`, module owner, optional generic pinconf custom params/items, and `link_consumers`. Registration APIs include `pinctrl_register_and_init()`, `pinctrl_enable()`, legacy `pinctrl_register()`, `pinctrl_unregister()`, and devm variants. GPIO range and lookup helpers include `pinctrl_add_gpio_range()`, `pinctrl_add_gpio_ranges()`, `pinctrl_remove_gpio_range()`, `pinctrl_find_and_add_gpio_range()`, `pinctrl_find_gpio_range_from_pin()`, and `pinctrl_get_group_pins()`. `struct pinfunction`, `PINCTRL_PINFUNCTION()`, and `PINCTRL_GPIO_PINFUNCTION()` describe selectable mux functions.

Control flow: a controller driver builds a `pinctrl_desc`, registers and initializes a `pinctrl_dev`, adds GPIO ranges if needed, then enables the device. Pinctrl core uses `pctlops` to enumerate groups, resolve firmware mappings through `dt_node_to_map()`, map GPIO requests to pin numbers, and expose debugfs. Function metadata is consumed with `pinmux_ops` to select mux functions over groups.

State and persistence: this header defines provider descriptors and callback contracts; runtime state is in pinctrl core (`pinctrl_dev`, maps, GPIO ranges, device links) and in hardware registers programmed by controller drivers. `link_consumers` influences suspend/resume ordering but no durable data is stored here.

Dependencies and integration points: depends on bits, types, device model, OF, GPIO chips, modules, seq files, pinmux, and pinconf. It is the shared contract among pinctrl providers, GPIO controllers, Device Tree parsers, debugfs, module refcounting, and PM dependency ordering.

Risks and test signals: risks include incorrect group/pin arrays, GPIO range off-by-one errors, callbacks returning pointers with insufficient lifetime, missing `dt_free_map()`, using legacy registration paths incorrectly, and suspend ordering bugs when consumer links are absent. Test controller registration/unregistration, devm cleanup, group lookup, GPIO-to-pin mapping, DT parsing/freeing, debugfs reads, OF-disabled builds, and suspend/resume with pinctrl consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pinctrl/pinctrl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pinctrl/pinmux.h -->
# sources/distributed-fs/ceph-client/include/linux/pinctrl/pinmux.h

Purpose: declares the pin multiplexing operation contract implemented by pin controllers that can route pins or pin groups to hardware functions or GPIO mode.

Important APIs and types: `struct pinmux_ops` includes pin request/free callbacks, function enumeration (`get_functions_count()`, `get_function_name()`, `get_function_groups()`), optional `function_is_gpio()`, `set_mux()` for function/group selection, GPIO acceleration hooks (`gpio_request_enable()`, `gpio_disable_free()`, `gpio_set_direction()`), and the `strict` ownership flag.

Control flow: pinctrl core requests pins before selecting mux settings, queries available functions and groups, checks ownership conflicts, calls `set_mux()` for device functions, and uses GPIO hooks when gpiolib asks to use pins as GPIOs. With `strict`, the core prevents simultaneous GPIO and mux owners for the same pin.

State and persistence: no state is stored here. Ownership, selected functions, and GPIO modes are tracked by pinctrl core and hardware registers in the controller driver. Settings are replayed through pinctrl state selection and PM callbacks.

Dependencies and integration points: depends on `pinctrl_dev` and `pinctrl_gpio_range` forward declarations. It integrates pinctrl providers, gpiolib GPIO requests, Device Tree function/group maps, and controller-specific mux programming.

Risks and test signals: risks include drivers failing to reject unavailable pins, inaccurate GPIO-function detection, group/function mismatches, direction changes not updating mux state, and insufficient `strict` enforcement. Test mux selection, GPIO request/free, GPIO direction changes, conflicting GPIO/function requests, one-group-per-pin controllers, and debug/error paths for unavailable groups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pinctrl/pinmux.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pipe_fs_i.h -->
# sources/distributed-fs/ceph-client/include/linux/pipe_fs_i.h

Purpose: defines the internal Linux pipe data structures, ring helpers, pipe buffer operations, locking/wait APIs, accounting hooks, resize/fcntl helpers, and creation helpers used by `fs/pipe.c`, splice, watch queues, and file descriptor code.

Important APIs and types: `PIPE_DEF_BUFFERS`, `PIPE_SIZE`, and `PIPE_BUF_FLAG_*` define default ring size and per-buffer flags including LRU, atomic map, gift, packet, merge, whole-buffer, and optional watch-queue loss markers. `struct pipe_buffer` stores page, offset, length, ops, flags, and private data. `union pipe_index` packs `head` and `tail` into `head_tail`; `pipe_index_t` is sized by architecture. `struct pipe_inode_info` contains the pipe mutex, read/write wait queues, head/tail, usage limits, reader/writer/file counters, cached temp pages, fasync state, buffer array, creator user, and optional `watch_queue`. `struct pipe_buf_operations` supplies `confirm()`, `release()`, `try_steal()`, and `get()`. Inline helpers cover watch queue detection, occupancy/full/empty checks, ring slot lookup, buffer reference/release/confirm/steal. External APIs include pipe locking, wait helpers, allocation/free, generic buffer ops, user buffer accounting and limit checks, ring resize, fcntl handling, `get_pipe_info()`, `create_pipe_files()`, and `round_pipe_size()`.

Control flow: producers write or splice pages into `bufs[head & (ring_size - 1)]`, readers consume from tail, and occupancy is computed by wrapping subtraction. Callers hold the pipe mutex around most structural changes, use wait helpers to drop the lock while sleeping for readable/writable conditions, and invoke buffer ops to validate data, take references, release pages, or steal pages after confirmation. Resize and fcntl paths adjust the ring and account buffer usage against `user_struct`.

State and persistence: pipe state is in-memory and tied to pipe inode/file lifetime: ring contents, counters, wait queues, buffer ownership, user accounting, fasync registrations, and optional notification state. It does not persist across reboot or close; page ownership may transfer through splice/steal flows.

Dependencies and integration points: depends on page structs, mutexes, wait queues, fasync, user accounting, files, splice users, optional `CONFIG_WATCH_QUEUE`, and MM page ownership. It integrates VFS pipe file descriptors, epoll/poll wakeups, splice/vmsplice/tee, notification pipes, and per-user pipe buffer limits.

Risks and test signals: high-risk areas include head/tail wrap arithmetic, ring size power-of-two assumptions, missing lock coverage, reference leaks in buffer ops, `try_steal()` without prior confirmation, packet/whole-buffer read semantics, watch queue loss reporting, and user accounting during resize/free. Test normal read/write, nonblocking I/O, poll/epoll wakeups, fasync, pipe resize limits, splice/vmsplice/tee, packet mode, watch queue notification loss, concurrent close, and soft/hard per-user pipe limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pipe_fs_i.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pkeys.h -->
# sources/distributed-fs/ceph-client/include/linux/pkeys.h

Purpose: provides the generic kernel wrapper for memory protection keys (pkeys), including fallback stubs for architectures without pkey support.

Important APIs and types: `ARCH_DEFAULT_PKEY` is the default key. With `CONFIG_ARCH_HAS_PKEYS`, architecture definitions come from `asm/pkeys.h`; without it, fallback macros define one available key, no execute-only dedicated key, no VM pkey flags, and neutral `arch_override_mprotect_pkey()`. Stub helpers include `vma_pkey()`, `mm_pkey_is_allocated()`, `mm_pkey_alloc()`, `mm_pkey_free()`, `arch_set_user_pkey_access()`, and `arch_pkeys_enabled()`.

Control flow: MM and syscall paths can call the generic helpers unconditionally. On pkey-capable architectures, arch code handles allocation, VMA key extraction, mprotect overrides, and user access register programming; on other architectures, only pkey 0 appears allocated and allocation/free requests fail or no-op.

State and persistence: this header owns no state. Supported architectures store pkey allocation state in `mm_struct` and access permissions in task/CPU-specific registers. Fallback builds have no persistent pkey state.

Dependencies and integration points: depends on `linux/mm.h` and optional `asm/pkeys.h`. It integrates `pkey_alloc`, `pkey_free`, `mprotect`, VMA flags, execute-only mappings, and per-task architecture access controls.

Risks and test signals: risks include fallback behavior masking feature assumptions, incorrect default key semantics, VMA flag drift, and architecture code failing to synchronize task access registers. Test pkey syscalls and mprotect on pkey-capable systems, compile fallback architectures, execute-only mapping behavior, fork/exec inheritance expectations, and invalid pkey error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pkeys.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pl320-ipc.h -->
# sources/distributed-fs/ceph-client/include/linux/pl320-ipc.h

Purpose: declares the minimal public interface for the ARM PL320 inter-processor communication mailbox driver.

Important APIs and types: `pl320_ipc_transmit(u32 *data)` sends a message payload, while `pl320_ipc_register_notifier()` and `pl320_ipc_unregister_notifier()` attach or detach `notifier_block` receivers for incoming IPC events.

Control flow: platform or subsystem code registers a notifier to receive mailbox events, transmits messages through the driver, and unregisters the notifier during teardown. Actual interrupt handling, mailbox register access, and notifier invocation live in the implementation.

State and persistence: this header stores no state. Runtime state is in the PL320 driver: notifier chain membership, mailbox registers, pending interrupts, and synchronization around transfers.

Dependencies and integration points: relies on `u32` and `struct notifier_block` declarations from surrounding includes. It integrates ARM platform code, mailbox/IPI-style communication, interrupt handling, and notifier chains.

Risks and test signals: risks include notifier lifetime races, message buffer ownership ambiguity, concurrent transmit serialization, and unregister during callback. Test registering multiple notifiers, transmit success/failure paths, interrupt delivery, teardown with pending IPC, and build coverage on platforms that expose PL320.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pl320-ipc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/ad5761.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/ad5761.h

Purpose: supplies platform data for AD5721/AD5721R/AD5761/AD5761R voltage-output DAC drivers, primarily the board-selected output voltage range.

Important APIs and types: `enum ad5761_voltage_range` lists bipolar and unipolar ranges from -10..10 V through 0..20 V. `struct ad5761_platform_data` contains the selected `voltage_range`.

Control flow: board setup or legacy platform-device code passes this struct to the DAC driver; probe programs range registers and uses the range to scale IIO output values.

State and persistence: platform data is boot-time configuration, not mutable runtime state. The DAC's programmed range persists only as hardware register state while powered.

Dependencies and integration points: integrates legacy platform data with the IIO DAC driver and board wiring/reference-voltage assumptions.

Risks and test signals: risks include range mismatch with board power rails, invalid enum values, and scale reporting not matching hardware. Test probe with each supported range, IIO scale/offset reporting, output saturation, and fallback behavior when no platform data exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/ad5761.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/ad7266.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/ad7266.h

Purpose: defines platform data for the AD7266/AD7265 SPI ADC driver, describing hardware strap choices for input range, sampling mode, and address pin wiring.

Important APIs and types: `enum ad7266_range` selects `0..VREF` or `0..2*VREF`. `enum ad7266_mode` selects differential, pseudo-differential, or single-ended sampling. `struct ad7266_platform_data` holds `range`, `mode`, and `fixed_addr`.

Control flow: platform code supplies this data at probe; the ADC driver uses it to interpret channel topology, address behavior, and conversion scaling.

State and persistence: the data describes static board wiring and does not change at runtime. Conversion state and SPI transfers live in the driver.

Dependencies and integration points: integrates legacy board files with the IIO ADC subsystem and SPI device registration.

Risks and test signals: risks include mismatched strap descriptions, wrong channel exposure, incorrect scale for `2*VREF`, and fixed address handling drift. Test channel enumeration, raw reads in each mode/range, DT/platform-data parity, and absent-data defaults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/ad7266.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/ad7791.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/ad7791.h

Purpose: provides static board configuration for the AD7791 ADC driver.

Important APIs and types: `struct ad7791_platform_data` carries `buffered`, `burnout_current`, and `unipolar` booleans for input buffering, sensor burnout current, and conversion polarity mode.

Control flow: during probe, the ADC driver reads these flags and programs mode/configuration registers before exposing IIO channels.

State and persistence: the struct is static platform configuration. Runtime conversion mode is mirrored in ADC registers and driver state, but this header owns none of it.

Dependencies and integration points: integrates legacy platform-device registration with an IIO SPI ADC driver.

Risks and test signals: risks include unit/comment drift for burnout current, wrong unipolar/bipolar scaling, and buffered-mode impedance assumptions. Test raw conversion scale/offset, buffered vs unbuffered inputs, burnout-current enablement, and no-platform-data defaults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/ad7791.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/ad7793.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/ad7793.h

Purpose: defines detailed platform data for AD7792/AD7793 and related sigma-delta ADC drivers, covering clock source, references, bias, buffering, polarity, and excitation current routing.

Important APIs and types: `enum ad7793_clock_source` selects internal clock, internal clock output, external clock, or external clock divided by two. `enum ad7793_bias_voltage` selects disabled or AIN pin bias. `enum ad7793_refsel` chooses external or internal reference sources. `enum ad7793_current_source_direction` routes excitation current sources to output pins. `enum ad7793_excitation_current` selects disabled, 10 uA, 210 uA, or 1 mA. `struct ad7793_platform_data` combines these enums with `burnout_current`, `boost_enable`, `buffered`, and `unipolar`.

Control flow: board code supplies the struct; probe maps each field to ADC configuration registers and channel scaling. Reference, excitation, and bias settings affect sensor front-end behavior before conversions start.

State and persistence: static platform data is copied/consumed at initialization. Register-programmed state remains in the ADC until reset/power loss and may be restored by driver resume.

Dependencies and integration points: integrates legacy platform data with IIO sigma-delta ADC drivers, SPI, regulators/references, and sensor bridge circuits.

Risks and test signals: risks include invalid enum combinations for chip variants, typo-prone `exitation_current` field usage, reference mismatch causing wrong scale, and current-source routing damaging sensors if board assumptions are wrong. Test probe on supported variants, scale calculation for each reference, excitation current programming, buffered/unipolar modes, and suspend/resume register restoration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/ad7793.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/ad7887.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/ad7887.h

Purpose: defines platform data for the AD7887 SPI ADC, selecting single-channel or dual-channel operation.

Important APIs and types: `struct ad7887_platform_data` contains `en_dual`, which determines whether AIN1 is exposed as a second input with Vref tied to Vdd, or used as the VREF input in single-channel mode.

Control flow: the ADC driver reads `en_dual` during probe and configures channel tables and scale/reference assumptions accordingly.

State and persistence: this is static board wiring information. Runtime conversion state is in the driver and ADC registers.

Dependencies and integration points: integrates platform-device board data with IIO SPI ADC channel setup.

Risks and test signals: risks include exposing the wrong channel count, misusing AIN1/Vref wiring, and wrong IIO scale. Test single and dual mode channel enumeration, raw reads, scale reporting, and no-platform-data defaults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/ad7887.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/adau17x1.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/adau17x1.h

Purpose: provides platform data for Analog Devices ADAU17x1-family audio codecs, describing microphone bias, jack/digital-mic pin use, debounce, polarity, output topology, and differential input wiring.

Important APIs and types: `enum adau17x1_micbias_voltage` selects 0.90 or 0.65 AVDD microphone bias. `enum adau1761_digmic_jackdet_pin_mode` selects disabled, digital microphone, or jack detect for the shared pin. `enum adau1761_jackdetect_debounce_time` chooses 5/10/20/40 ms. `enum adau1761_output_mode` selects headphone, capless headphone, or line output. `struct adau1761_platform_data` carries input differential, line/headphone modes, shared-pin mode, debounce, jackdetect polarity, and micbias. `struct adau1781_platform_data` carries left/right differential input flags, digital mic selection, and micbias.

Control flow: board code supplies codec platform data at device creation; the ASoC codec driver consumes it during probe to configure DAPM routes, jack detect, bias voltage, pin modes, and analog output registers.

State and persistence: platform data is static board/audio-jack topology. Runtime codec register/cache state lives in the driver and hardware and is typically restored through regmap/ASoC resume.

Dependencies and integration points: integrates legacy board files with ASoC codec drivers, DAPM routing, jack detection, microphone bias, and machine-driver topology.

Risks and test signals: risks include choosing mutually exclusive shared-pin modes incorrectly, wrong active-low jack polarity, differential/single-ended mismatch, and output mode mismatch causing audio distortion or missing routes. Test codec probe, DAPM route availability, headphone/line output, jack insertion/removal with debounce, digital mic capture, suspend/resume, and platform-data versus firmware-property parity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/adau17x1.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/adp8860.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/adp8860.h

Purpose: defines constants and platform data for ADP8860/ADP8863-style backlight and independent LED current-sink drivers.

Important APIs and types: constants cover chip ID, max brightness, LED blink off/on timing fields, LED sink identifiers D1-D7, backlight LED assignment bits, fade timers/laws, ambient-light filter times, and scaling macros `ADP8860_BL_CUR_mA()`, `ADP8860_L2_COMP_CURR_uA()`, and `ADP8860_L3_COMP_CURR_uA()`. `struct adp8860_backlight_platform_data` defines backlight LED assignment, fade behavior, ambient sensor enable/filtering, daylight/office/dark max/dim currents, comparator trip/hysteresis thresholds, optional independent LED class entries (`num_leds`, `leds`), LED fade/blink settings, and `gdwn_dis` charge-pump gain-down disable.

Control flow: platform code passes the struct to the I2C backlight driver; probe programs backlight current tables, ambient thresholds, fade behavior, and registers unassigned sinks as LED class devices.

State and persistence: the struct is boot-time hardware policy. Runtime state includes backlight brightness, LED class devices, ALS mode, and chip registers; hardware state is lost on power/reset and must be restored by the driver.

Dependencies and integration points: includes `linux/leds.h` and `linux/types.h`. Integrates backlight class, LED class, I2C device setup, ambient-light based brightness control, and board-specific current-sink wiring.

Risks and test signals: risks include unit-scaling macro overflow or out-of-range inputs, wrong LED assignment bitmasks, ambient threshold inversion, charge-pump policy unsuitable for board capacitors, and dangling `led_info` arrays. Test probe/register, brightness changes, ALS transitions across thresholds, independent LED blink/fade, suspend/resume restore, and invalid platform-data bounds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/adp8860.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/adp8870.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/adp8870.h

Purpose: defines constants and platform data for the ADP8870 backlight and LED current-sink driver.

Important APIs and types: constants mirror ADP8860-style controls for chip ID, max brightness, LED blink timing, LED sinks D1-D7, backlight assignment bits, fade timers/laws, ALS filter times, and scaling macros for backlight current plus L2-L5 comparator currents. `struct adp8870_backlight_platform_data` adds `pwm_assign`, five ambient zones (daylight/bright/office/indoor/dark), comparator trip/hysteresis values, and independent LED class configuration.

Control flow: board code supplies this data at I2C probe; the driver configures PWM/backlight sink assignment, ambient light thresholds, fade curves, brightness tables, and optional LED class devices.

State and persistence: platform data is static board policy. Runtime brightness, ambient zone, PWM mode, and LED state live in driver memory and chip registers.

Dependencies and integration points: integrates with backlight, LED class, I2C, and board wiring for current sinks and ALS comparators.

Risks and test signals: risks include misspelled/comment-drift fields (`l4_indor_dim`, L6 comment for L5), out-of-range current conversion, incorrect PWM assignment, threshold ordering errors, and wrong LED sink ownership. Test all ambient zones, PWM/backlight mode, LED registration, brightness scaling, fade/blink behavior, and suspend/resume register restoration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/adp8870.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/ads7828.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/ads7828.h

Purpose: defines optional platform data for the TI ADS7828 hardware-monitor ADC.

Important APIs and types: `struct ads7828_platform_data` contains `diff_input`, `ext_vref`, and `vref_mv` to describe differential input mode and reference-voltage source/value.

Control flow: the hwmon/I2C driver consumes these fields at probe to select command mode and calculate voltage readings.

State and persistence: static connectivity/reference information only; runtime sampling state is maintained by the driver and chip.

Dependencies and integration points: integrates legacy platform-device data with the hwmon ADS7828 driver and board reference-voltage wiring.

Risks and test signals: risks include wrong differential/single-ended interpretation, zero or inaccurate external reference values, and mismatch with documented sysfs scaling. Test sysfs voltage readings with internal/external references, differential mode, absent platform data, and boundary reference values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/ads7828.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/amd_qdma.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/amd_qdma.h

Purpose: defines platform data and DMA-channel filter metadata for AMD QDMA engine integration.

Important APIs and types: `struct qdma_queue_info` carries `enum dma_transfer_direction dir` for DMA channel matching. `QDMA_FILTER_PARAM(qinfo)` casts queue info for dmaengine filter callbacks. `struct qdma_platdata` provides `max_mm_channels`, `irq_index`, a `dma_slave_map *device_map`, and a `device *dma_dev` for DMA operations.

Control flow: platform code supplies QDMA platform data during device registration. DMA clients pass `QDMA_FILTER_PARAM()` to request channels matching transfer direction; the QDMA driver uses max channel counts, IRQ index base, slave map, and DMA device pointer during probe and channel allocation.

State and persistence: static probe-time capability and mapping data. Runtime DMA descriptors, queues, interrupts, and channel state live in the DMA engine driver.

Dependencies and integration points: depends on `linux/dmaengine.h`, `dma_slave_map`, and device model. Integrates platform devices, dmaengine channel lookup, interrupt allocation, and DMA client mapping.

Risks and test signals: risks include direction filter mismatches, wrong IRQ base, stale or undersized slave maps, and invalid channel-count limits. Test dmaengine channel requests for both directions, interrupt handling, probe/remove, slave-map lookup, and DMA transfer completion/error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/amd_qdma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/amd_xdma.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/amd_xdma.h

Purpose: defines platform data and channel filter metadata for AMD XDMA engine integration.

Important APIs and types: `struct xdma_chan_info` carries DMA transfer direction, `XDMA_FILTER_PARAM(chan_info)` casts it for dmaengine filtering, and `struct xdma_platdata` provides `max_dma_channels`, `device_map_cnt`, and `dma_slave_map *device_map`.

Control flow: platform code registers XDMA with the platform data; clients request DMA channels using filter info, and the driver validates requested direction and slave map entries against the advertised channel count.

State and persistence: the header describes static platform capabilities and mappings. Active channels, descriptors, and hardware queues are runtime driver state.

Dependencies and integration points: depends on `linux/dmaengine.h` and integrates with dmaengine client channel request paths, platform devices, and DMA slave mapping.

Risks and test signals: risks include wrong `device_map_cnt`, invalid map lifetime, direction mismatch, and channel limit off-by-one errors. Test probe with multiple map counts, channel request/release, H2D/D2H transfers, error IRQs, and remove while channels are idle/active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/amd_xdma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/ams-delta-fiq.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/ams-delta-fiq.h

Purpose: defines shared offsets into the Amstrad E3/AMS Delta FIQ buffer used by FIQ assembly and drivers that service GPIO-triggered keyboard, modem, and hook-switch events.

Important APIs and types: macros `FIQ_MASK` through `IRQ_SIR_CODE_L2`, `FIQ_CNT_INT_*`, and `FIQ_CIRC_BUFF` define word offsets for mask/state, key counters, circular buffer head/tail/length, missed keys, GPIO interrupt mask, pending IRQ flags, soft interrupt codes, interrupt counters, and circular buffer data start.

Control flow: low-level FIQ code writes event state and counters into the shared buffer using these offsets; normal interrupt or device drivers read/update fields to drain events and coordinate masking.

State and persistence: state lives in a shared in-memory FIQ buffer. It is volatile and platform-specific, but must remain layout-compatible across FIQ and driver code.

Dependencies and integration points: integrates OMAP/AMS Delta board FIQ handling with keyboard/modem/hook-switch GPIO drivers and interrupt dispatch code.

Risks and test signals: risks include offset drift breaking assembly/users agreement, circular-buffer overflow, missed-key accounting errors, and races between FIQ and IRQ context. Test keyboard/modem/hook events, buffer wrap, missed interrupt counters, mask updates, and platform compile coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/ams-delta-fiq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/apds990x.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/apds990x.h

Purpose: defines platform tuning data for the APDS990x combined proximity and ambient light sensor driver.

Important APIs and types: IR LED current constants select 12, 25, 50, or 100 mA. `struct apds990x_chip_factors` contains glass attenuation and clear/IR conversion factors scaled by `APDS_PARAM_SCALE`, plus device factor `df`. `struct apds990x_platform_data` includes chip factors, proximity LED drive `pdrive`, pulse count `ppcount`, and resource setup/release callbacks for interrupt wiring.

Control flow: board code supplies optical calibration and interrupt callbacks at probe. The driver programs proximity pulse/drive settings, converts raw ALS channels to lux using factors, and calls setup/release hooks around IRQ resource lifetime.

State and persistence: calibration data is static board/platform state. Runtime sensor thresholds, IRQ state, and measurements live in the driver and hardware registers.

Dependencies and integration points: uses fixed-width integer types from kernel headers and integrates with I2C sensor drivers, input/IIO-style reporting depending on implementation, IRQ setup, and board-specific optical cover design.

Risks and test signals: risks include bad calibration producing wrong lux/proximity values, invalid pulse/current combinations, callback lifetime errors, and resource leaks on probe failure. Test ALS conversion with known light levels, proximity thresholds, IRQ setup/release failure paths, suspend/resume, and default factors when attenuation is zero.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/apds990x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/arm-ux500-pm.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/arm-ux500-pm.h

Purpose: declares UX500 platform power-management helpers for coordinating PRCMU/GIC state around low-power CPU idle and suspend flows.

Important APIs and types: exported functions include `prcmu_gic_decouple()`, `prcmu_gic_recouple()`, `prcmu_gic_pending_irq()`, `prcmu_pending_irq()`, `prcmu_is_cpu_in_wfi()`, `prcmu_copy_gic_settings()`, and `ux500_pm_init(phy_base, size)`.

Control flow: platform PM code initializes the PM interface, copies GIC settings, decouples interrupt control before deep idle/suspend, checks pending IRQ/PRCMU wake state, observes CPU WFI status, and recouples the GIC on exit.

State and persistence: runtime PM state is held by UX500 PRCMU/GIC platform code and hardware registers. No state is stored in this declaration header.

Dependencies and integration points: integrates ARM UX500 cpuidle/suspend code, PRCMU firmware/register access, GIC interrupt controller state, and wakeup handling.

Risks and test signals: risks include entering deep idle with pending interrupts, failing to restore GIC coupling, stale copied GIC settings, and CPU WFI detection races. Test cpuidle AFTR/deep states, wake interrupts, suspend/resume, multi-CPU WFI checks, and initialization with invalid physical base/size.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/arm-ux500-pm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/asoc-imx-ssi.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/asoc-imx-ssi.h

Purpose: declares platform data and FIQ-related symbols for Freescale/NXP i.MX SSI ASoC support.

Important APIs and types: extern FIQ symbols expose `imx_ssi_fiq_start/end/base/tx_buffer/rx_buffer`. `struct imx_ssi_platform_data` carries mode flags (`IMX_SSI_DMA`, `IMX_SSI_USE_AC97`, `IMX_SSI_NET`, `IMX_SSI_SYN`, `IMX_SSI_USE_I2S_SLAVE`) and AC97 reset/warm-reset callbacks. `mxc_set_irq_fiq()` configures an IRQ as FIQ.

Control flow: machine/platform code supplies SSI flags and AC97 callbacks; the ASoC SSI driver chooses DMA or FIQ paths, AC97/I2S/network/synchronous modes, and configures FIQ interrupt handling when needed.

State and persistence: platform data is static audio-interface configuration. Runtime audio buffers, FIQ code/data, DMA channels, and codec state live in driver/platform code.

Dependencies and integration points: integrates i.MX SSI controller drivers, ASoC, AC97 codec handling, FIQ assembly code, IRQ configuration, and optional DMA.

Risks and test signals: risks include incompatible mode flags, FIQ buffer symbol/linkage issues, AC97 reset callback lifetime, and IRQ/FIQ misconfiguration. Test playback/capture with DMA and FIQ, AC97 cold/warm reset, I2S slave mode, network/synchronous modes, and build/link coverage for FIQ symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/asoc-imx-ssi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/asoc-kirkwood.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/asoc-kirkwood.h

Purpose: provides a small platform-data struct for Kirkwood ASoC audio controller configuration.

Important APIs and types: `struct kirkwood_asoc_platform_data` contains `burst`, likely controlling DMA/audio burst behavior for the controller.

Control flow: platform setup passes the struct to the Kirkwood audio driver, which uses `burst` during controller/DMA configuration.

State and persistence: static boot-time configuration only. Runtime PCM/DMA state lives in the ASoC driver.

Dependencies and integration points: integrates Marvell Kirkwood board files with the ASoC platform driver.

Risks and test signals: risks include unsupported burst values and mismatch with DMA/FIFO capabilities. Test audio playback/capture with configured burst sizes, underrun/overrun behavior, and platform-data absence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/asoc-kirkwood.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/asoc-pxa.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/asoc-pxa.h

Purpose: declares PXA2xx audio/AC97 platform operations and setup hooks used by legacy PXA board files and ASoC drivers.

Important APIs and types: `pxa2xx_audio_ops_t` contains PCM lifecycle callbacks (`startup`, `shutdown`, `suspend`, `resume`), private data, `reset_gpio`, and per-codec `codec_pdata[AC97_BUS_MAX_DEVICES]`. `pxa_set_ac97_info()` registers the ops, and `pxa27x_configure_ac97reset()` controls whether the PXA27x AC97 reset line is routed through GPIO.

Control flow: board code initializes audio ops through `pxa_set_ac97_info()`. The AC97/ASoC driver invokes lifecycle callbacks around PCM use and configures reset behavior, including the PXA27x reset-line workaround.

State and persistence: platform ops are static function/data pointers. Runtime PCM streams, AC97 bus devices, reset GPIO state, and suspend state live in audio drivers and hardware.

Dependencies and integration points: includes ALSA core, PCM, and AC97 codec headers. Integrates PXA board code, ASoC platform drivers, AC97 bus, GPIO reset handling, and codec-specific platform data.

Risks and test signals: risks include callback lifetime issues, wrong reset GPIO defaults, codec platform-data array bounds, and suspend/resume ordering bugs. Test AC97 reset on PXA27x, playback/capture callbacks, suspend/resume, multi-codec pdata, and no-reset-gpio configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/asoc-pxa.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/asoc-s3c.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/asoc-s3c.h

Purpose: defines Samsung S3C/S5P ASoC platform data for AC97/I2S/PCM GPIO setup, DMA filtering, and I2S controller quirks.

Important APIs and types: `S3C64XX_AC97_GPD` and `S3C64XX_AC97_GPE` identify GPIO banks for AC97 pins. `struct samsung_i2s_type` contains quirk bits such as primary 5.1 channels, secondary DAI, no internal mux/prescaler, reset clear requirement, TDM support, IDMA support, and an IDMA address. `struct s3c_audio_pdata` supplies `cfg_gpio()`, DMA filter function, playback/capture DMA data for primary/secondary/mic paths, and the I2S type descriptor.

Control flow: machine init code selects GPIO bank and passes platform data; the ASoC driver configures pin muxes, chooses DMA channels through `dma_filter`, and adapts register/DAI behavior according to quirks.

State and persistence: static SoC/board description. Runtime DAI, DMA, clock, and register state live in Samsung ASoC drivers.

Dependencies and integration points: depends on dmaengine types and `platform_device`. Integrates Samsung pin configuration, DMA engine channel selection, ASoC DAI setup, AC97/PCM/I2S modes, and SoC-specific I2S variants.

Risks and test signals: risks include wrong quirk bits causing broken clocks/channels, DMA filter data mismatch, GPIO config callback failure, and IDMA address errors. Test playback/capture on primary/secondary/mic paths, TDM/5.1 modes, AC97 GPIO bank setup, DMA allocation failure, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/asoc-s3c.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/asoc-ti-mcbsp.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/asoc-ti-mcbsp.h

Purpose: defines platform configuration for TI OMAP McBSP audio serial ports.

Important APIs and types: `struct omap_mcbsp_ops` provides optional `request()` and `free()` hooks per McBSP instance. `struct omap_mcbsp_platform_data` carries ops, buffer size, register size/step, wakeup capability, CCR support, and `force_ick_on()` clock callback. `omap3_mcbsp_init_pdata_callback()` initializes callback fields for OMAP3 platform data.

Control flow: platform code populates McBSP pdata; the driver calls request/free hooks for ownership, uses register sizing/stepping for IO access, configures wakeup/CCR features, and may force the interface clock through the callback.

State and persistence: platform data describes static controller capabilities. Runtime port ownership, clocks, buffers, DMA, and audio stream state live in the McBSP driver.

Dependencies and integration points: depends on spinlocks and clock framework declarations. Integrates OMAP platform setup, ASoC McBSP drivers, clock management, wakeup handling, and DMA/buffer sizing.

Risks and test signals: risks include wrong register stride/width, unbalanced request/free hooks, clock force leaks, and wakeup capability mismatch. Test probe on OMAP variants, playback/capture, suspend wakeup, force-clock paths, and request/free error handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/asoc-ti-mcbsp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/ata-pxa.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/ata-pxa.h

Purpose: defines platform data for the generic PXA PATA/ATA driver.

Important APIs and types: `struct pata_pxa_pdata` contains DMA request line `dma_dreq`, register address shift `reg_shift`, and `irq_flags`.

Control flow: board setup supplies the struct to the PXA PATA platform device; the ATA driver uses it for register addressing, DMA channel/request selection, and interrupt request flags.

State and persistence: static hardware wiring/configuration only. Runtime ATA ports, DMA descriptors, IRQ state, and disk data are managed elsewhere.

Dependencies and integration points: integrates PXA board files, libata PATA driver, DMA request routing, MMIO register layout, and IRQ setup.

Risks and test signals: risks include wrong register shift corrupting accesses, wrong DMA request line, and incompatible IRQ trigger flags. Test PIO and DMA transfers, IRQ handling, device detection, suspend/resume, and board variants with different register wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/ata-pxa.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/atmel.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/atmel.h

Purpose: provides a temporary common declaration point for Atmel power-management slow-clock status.

Important APIs and types: when `CONFIG_ATMEL_PM` is enabled, declares `at91_suspend_entering_slow_clock()`. Otherwise, an inline stub returns 0.

Control flow: Atmel drivers can call this helper unconditionally to adjust behavior while the platform is entering slow-clock suspend; non-PM builds take the neutral false path.

State and persistence: no state is stored here. Enabled builds query platform PM state maintained by AT91 suspend code.

Dependencies and integration points: integrates Atmel platform drivers with optional AT91 power-management code while preserving compile coverage for configurations without `CONFIG_ATMEL_PM`.

Risks and test signals: risks include the stub hiding PM-only assumptions and drivers relying on slow-clock status without selecting the config. Test compile with and without `CONFIG_ATMEL_PM`, suspend entry/exit behavior, and driver behavior around slow-clock transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/atmel.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/b53.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/b53.h

Purpose: defines platform data for Broadcom B53 DSA switch registration, including chip identity, enabled ports, and optional memory-mapped register access.

Important APIs and types: `struct b53_platform_data` embeds `struct dsa_chip_data cd` as its first member for DSA access, then adds `chip_id`, `enabled_ports`, `big_endian` bitfield, and `void __iomem *regs` for MMAP access.

Control flow: platform code passes the struct to the B53 switch driver; the DSA core reads the embedded chip data, and the B53 driver uses chip ID, port mask, endian mode, and register base to initialize switch access.

State and persistence: platform data is static board/switch wiring. Runtime switch state, ports, VLANs, and register caches live in DSA/B53 drivers and hardware.

Dependencies and integration points: depends on `linux/types.h` and `linux/platform_data/dsa.h`. Integrates legacy board files, DSA switch registration, memory-mapped B53 variants, and endian-specific register access.

Risks and test signals: risks include breaking the first-member layout expected by DSA, wrong enabled-port mask, incorrect endian selection, and invalid MMIO base lifetime. Test DSA registration, port bring-up, MMAP register reads/writes, big-endian access, VLAN/bridge operations, and remove/error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/b53.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/bcm7038_wdt.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/bcm7038_wdt.h

Purpose: defines the platform-data hook for the Broadcom BCM7038 watchdog timer.

Important APIs and types: `struct bcm7038_wdt_platform_data` contains `const char *clk_name`, naming the clock used by the watchdog.

Control flow: platform setup passes the clock name to the watchdog driver; probe resolves the clock and uses its rate/control to program timeout behavior.

State and persistence: static clock binding data only. Runtime watchdog arming, timeout, and clock state live in the driver/hardware.

Dependencies and integration points: integrates Broadcom platform devices, common clock framework lookup by name, and watchdog subsystem registration.

Risks and test signals: risks include wrong or missing clock names leading to timeout miscalculation or probe failure. Test probe with valid/invalid clock names, watchdog start/stop/ping, timeout programming, and suspend/resume clock behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/bcm7038_wdt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/bd6107.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/bd6107.h

Purpose: supplies platform data for the ROHM BD6107 LED driver.

Important APIs and types: forward-declares `struct device`; `struct bd6107_platform_data` contains a device pointer and a default LED/control value `def_value`.

Control flow: board code supplies platform data at device registration; the LED driver uses the default value during initialization and may use the device pointer for parent/resource context.

State and persistence: static default configuration only. Runtime LED brightness/state lives in the driver and hardware.

Dependencies and integration points: integrates ROHM LED platform devices with the LED subsystem and device model.

Risks and test signals: risks include stale device pointer use, invalid default value, and mismatch with LED class initial brightness. Test probe defaults, brightness changes, remove cleanup, and absent/invalid platform data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/bd6107.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/bh1770glc.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/bh1770glc.h

Purpose: defines board calibration and resource hooks for the ROHM BH1770GLC / OSRAM SFH7770 proximity and ambient light sensor driver.

Important APIs and types: `struct bh1770_platform_data` contains IR LED default current (`BH1770_LED_*` constants), `glass_attenuation` with neutral value `BH1770_NEUTRAL_GA`, and setup/release callbacks for interrupt resources.

Control flow: the sensor driver consumes the platform data during probe, configures LED drive current, uses attenuation to convert raw ALS data, and calls resource callbacks around IRQ setup and teardown.

State and persistence: static optical calibration and board resource behavior. Runtime sensor state, thresholds, and IRQ state live in the driver/hardware.

Dependencies and integration points: uses kernel integer typedefs and integrates I2C sensor drivers, IRQ setup, proximity reporting, and board cover-glass calibration.

Risks and test signals: risks include wrong attenuation scaling, invalid LED current, callback failure leaks, and proximity behavior varying with cover glass. Test ALS calibration, proximity detection, IRQ setup/release failure handling, suspend/resume, and neutral attenuation defaults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/bh1770glc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/brcmfmac.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/brcmfmac.h

Purpose: defines platform-specific configuration for Broadcom/Cypress `brcmfmac` wireless devices, including power hooks, firmware path override, per-device bus settings, country-code translation, and SDIO quirks.

Important APIs and types: `BRCMFMAC_PDATA_NAME` names the platform-data provider and `BRCMFMAC_COUNTRY_BUF_SZ` sizes country strings. `enum brcmf_bus_type` selects SDIO, USB, or PCIE. `struct brcmfmac_sdio_pd` configures SDIO txglom size, drive strength, OOB IRQ support/number/flags, broken scatter-gather alignment constraints, and reset callback. `struct brcmfmac_pd_cc_entry` and flexible-array `struct brcmfmac_pd_cc` translate ISO3166 country codes to firmware country/revision codes. `struct brcmfmac_pd_device` matches device ID/revision/bus type and carries feature-disable flags, country-code table, and bus-specific settings. `struct brcmfmac_platform_data` provides power-on/off callbacks, alternate firmware path, device count, and a flexible array of device entries.

Control flow: a platform data provider must be initialized before brcmfmac's device initcall if built-in. On driver load, brcmfmac looks up platform data by name, calls `power_on()`, matches the probed device against `devices[]`, applies bus quirks/features/country tables, and calls `power_off()` on unload or reset-style teardown.

State and persistence: platform data is static board/device policy. Runtime wireless state includes firmware, regulatory settings, bus state, IRQs, and power state in brcmfmac and hardware. Flexible arrays require the provider allocation to remain valid for the driver's lifetime.

Dependencies and integration points: integrates platform data providers, brcmfmac SDIO/USB/PCIe bus layers, firmware loading, regulatory country-code translation, OOB interrupt setup, SDIO host quirks, and platform power control.

Risks and test signals: risks include provider initcall ordering, silent fallback when pdata is missing, malformed flexible-array allocation, country-code table bounds, invalid OOB IRQ flags, broken SG alignment values, and power/reset callback races. Test built-in and module load ordering, power cycle, SDIO OOB IRQ operation, country-code translation, firmware alternate path, feature-disable masks, suspend/resume, and reset after bus communication failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/brcmfmac.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/brcmnand.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/brcmnand.h

Purpose: defines platform data for Broadcom NAND controller/chip setup.

Important APIs and types: `struct brcmnand_platform_data` contains `chip_select`, partition parser names `part_probe_types`, and ECC geometry fields `ecc_stepsize` and `ecc_strength`.

Control flow: platform code passes this struct to the NAND driver; probe selects the chip, chooses partition parsers, and configures ECC layout/strength before registering MTD devices.

State and persistence: static flash topology and ECC policy. Persistent data is on NAND flash, but this header only describes how the driver should access and protect it.

Dependencies and integration points: integrates Broadcom platform devices, raw NAND/MTD registration, partition parsing, and ECC configuration.

Risks and test signals: risks include wrong chip-select accessing the wrong device, ECC settings incompatible with existing flash data, and partition parser mismatch. Test NAND probe/read/write, ECC correction stats, bad-block handling, partition discovery, and boot compatibility with existing images.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/brcmnand.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/clk-da8xx-cfgchip.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/clk-da8xx-cfgchip.h

Purpose: defines platform data for the TI DaVinci DA8xx CFGCHIP clock driver.

Important APIs and types: `struct da8xx_cfgchip_clk_platform_data` carries a `struct regmap *cfgchip` pointing at the CFGCHIP syscon register block.

Control flow: platform code creates the clock device with this regmap; the clock driver uses it to read/modify CFGCHIP bits that gate or select DA8xx miscellaneous clocks.

State and persistence: the regmap points to hardware-backed system configuration registers. Platform data itself is static; clock state is runtime register state.

Dependencies and integration points: depends on `linux/regmap.h` and integrates platform devices, syscon/regmap, and common clock framework providers.

Risks and test signals: risks include invalid regmap lifetime, incorrect CFGCHIP bit updates affecting unrelated functions, and clock registration before syscon availability. Test clock registration, enable/disable/set-parent operations, concurrent regmap users, probe deferral, and suspend/resume register state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/clk-da8xx-cfgchip.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/clk-fch.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/clk-fch.h

Purpose: defines platform data for AMD FCH miscellaneous clock framework support.

Important APIs and types: `struct fch_clk_data` contains an MMIO `base` pointer and a clock `name`.

Control flow: platform setup passes this data to the FCH clock driver; the driver maps register operations relative to `base` and registers a named clock provider/output.

State and persistence: the struct is static registration data. Runtime clock state is in MMIO registers and common clock framework objects.

Dependencies and integration points: includes compiler attributes for `__iomem` and integrates AMD platform devices, MMIO register access, and the common clock framework.

Risks and test signals: risks include invalid MMIO base, mutable string lifetime, duplicate clock names, and register bit drift. Test clock registration, enable/disable/rate operations if supported, invalid base handling, and remove cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/clk-fch.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/cpuidle-exynos.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/cpuidle-exynos.h

Purpose: defines Exynos cpuidle platform callbacks for entering and bracketing AFTR/CPU powerdown low-power states.

Important APIs and types: `struct cpuidle_exynos_data` contains callbacks `cpu0_enter_aftr()`, `cpu1_powerdown()`, `pre_enter_aftr()`, and `post_enter_aftr()`.

Control flow: Exynos cpuidle code calls pre-enter hook, invokes CPU0 AFTR entry or CPU1 powerdown as appropriate, then calls post-enter hook on return to restore platform state.

State and persistence: the callbacks manipulate SoC PM registers and CPU state externally; this header stores no state. Low-power transitions are runtime-only.

Dependencies and integration points: integrates Exynos platform PM code, cpuidle driver, CPU hotplug/secondary CPU powerdown paths, and AFTR suspend-like state handling.

Risks and test signals: risks include callback NULL handling, failed entry leaving pre-enter state active, CPU1 powerdown coordination races, and lost wakeup state. Test idle state entry/exit, wake interrupts, CPU0/CPU1 paths, cpuidle disable/enable, and suspend/resume interactions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/cpuidle-exynos.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/cros_ec_chardev.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/cros_ec_chardev.h

Purpose: defines the ChromeOS EC character-device userspace ABI for sending EC commands, reading mapped EC memory, and configuring event masks.

Important APIs and types: `CROS_EC_DEV_VERSION` identifies ABI version. `struct cros_ec_readmem` contains memory-map `offset`, requested `bytes`, and a fixed `buffer[EC_MEMMAP_SIZE]`; zero bytes means read a NUL-terminated string up to the EC memory-map limit. Ioctls use `CROS_EC_DEV_IOC`: `CROS_EC_DEV_IOCXCMD` transfers `struct cros_ec_command`, `CROS_EC_DEV_IOCRDMEM` transfers `struct cros_ec_readmem`, and `CROS_EC_DEV_IOCEVENTMASK` manages event masks.

Control flow: userspace opens the EC chardev and issues ioctls. The driver copies command/readmem structs from userspace, validates offsets and lengths, talks to the EC transport/LPC memory map, copies results back, and reports byte counts or errors.

State and persistence: ABI structs are per-ioctl data. Runtime state includes EC device transport, event masks, and mapped memory contents; persistent EC settings are managed by firmware/commands outside this header.

Dependencies and integration points: depends on bits, ioctl, types, and `linux/platform_data/cros_ec_commands.h`. Integrates userspace tools, ChromeOS EC command protocol, LPC/transport-specific EC drivers, and event handling.

Risks and test signals: risks include ABI layout changes, insufficient bounds checks on `offset`/`bytes`, command size validation bugs, event mask compatibility, and 32/64-bit ioctl issues. Test ioctl command round trips, mapped memory reads including zero-length string mode, invalid offset/length, compat userspace, event mask operations, and EC transport failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/cros_ec_chardev.h -->
