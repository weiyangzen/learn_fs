# subset-b-004013 Research

Grouped research for the requested source files. Each section is bounded by the required markers so reconciliation can split this report into source-tree-aligned per-file documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/rgb/leds-qcom-lpg.c -->
# sources/distributed-fs/ceph-client/drivers/leds/rgb/leds-qcom-lpg.c

Purpose: Qualcomm LPG is a combined LED and PWM driver for SPMI/PMIC light pulse generator hardware. It exposes individual LEDs, multicolor LEDs, hardware/software blink, LED pattern playback through LPG LUT or SDAM/PPG storage, and a PWM chip for channels not consumed by LED class devices. It is a hardware-facing driver with direct PMIC register writes through a parent regmap and optional NVMEM/PBS integration.

Important APIs, types, and functions: `struct lpg` is the device context and owns the regmap, mutex, PWM chip, LUT bitmap, PBS/NVMEM handles, TRILED register metadata, and channels. `struct lpg_channel` stores one hardware channel's register base, subtype, DTEST state, PWM timing, TRILED/LUT masks, SDAM offset, and active pattern state. `struct lpg_led` joins one or more channels into a LED class or multicolor LED class device. The central public-facing callbacks are `lpg_brightness_single_set()`, `lpg_brightness_mc_set()`, `lpg_blink_single_set()`, `lpg_blink_mc_set()`, `lpg_pattern_single_set()`, `lpg_pattern_mc_set()`, `lpg_pattern_*_clear()`, and PWM callbacks `lpg_pwm_request()`, `lpg_pwm_apply()`, and `lpg_pwm_get_state()`. Probe-time helpers initialize channels, TRILED, LUT, SDAM, device-tree LEDs, DTEST, and PWM registration.

Control flow: `lpg_probe()` obtains match data, the parent regmap, allocates channel state, parses optional `qcom,dtest`, initializes TRILED/SDAM/LUT resources, registers one LED object per child node, applies DTEST routing, then registers a PWM chip. Brightness changes take the driver mutex, compute channel frequency and duty for a 1 ms default period or arm an already loaded pattern, call `lpg_apply()` per channel, update TRILED enable bits, and optionally trigger LUT/PBS playback. Blink requests compute frequency/duty from requested on/off delays and return the actual delays. Pattern setup validates the LED trigger pattern format, compresses palindromic LUT patterns when supported, validates timing constraints, allocates LUT slots, records ramp metadata on all LED channels, and starts playback through the brightness path.

State and persistence: All runtime state is in devm-managed `struct lpg`, per-channel fields, the LUT allocation bitmap, and hardware registers/NVMEM SDAM bytes. Nothing persists beyond hardware state and device-tree defaults. The mutex serializes LED and PWM callbacks because both mutate the same channel registers. `chan->in_use` prevents PWM consumers from requesting channels already exposed as LEDs. `pbs_en_bitmap` tracks whether PBS trigger enable/clear writes are needed.

Dependencies and integration points: The file depends on LED class, multicolor LED class, PWM framework, OF bindings, regmap, NVMEM, Qualcomm PBS, and SPMI parent devices. Device-tree compatible strings map PMIC variants to `struct lpg_data` tables. LED child nodes supply `reg`, `color`, `linux,default-trigger`, and `default-state`; parent nodes may supply `qcom,power-source`, `qcom,dtest`, and `nvmem-names`.

Risks: Frequency calculation is integer-heavy and rejects periods at or below hardware minimum while clamping overly long periods, so boundary tests matter. SDAM pattern support differs from LUT-backed support: ping-pong is disabled and pause support depends on a dedicated LUT SDAM. `lpg_lut_free()` intentionally does not free length-one allocations because hardware treats length-one patterns specially; future changes can leak LUT slots if they miss that constraint. Multicolor pattern setup disables TRILED before programming; failure paths must not leave confusing hardware state. `lpg_pwm_get_state()` decodes register fields and can return `-EINVAL` if hardware contains unsupported indices.

Test signals: Exercise LED registration from representative DT nodes, single-channel and multicolor brightness, default-on state, blink delay round-tripping, PWM apply/get for normal and high-resolution subtypes, pattern acceptance/rejection cases, LUT exhaustion, SDAM devices with one and two NVMEM cells, DTEST parsing validation, and probe on each compatible data table.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/rgb/leds-qcom-lpg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/simatic/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/leds/simatic/Kconfig

Purpose: This Kconfig file declares LED driver options for Siemens SIMATIC industrial PCs, covering a legacy I/O-port implementation and GPIO-backed variants for Intel Apollo Lake, Intel Elkhart Lake, and Nuvoton F7188x hardware.

Important entries: `LEDS_SIEMENS_SIMATIC_IPC` depends on `LEDS_CLASS` and `SIEMENS_SIMATIC_IPC` and defaults to `y`, building `simatic-ipc-leds`. `LEDS_SIEMENS_SIMATIC_IPC_APOLLOLAKE`, `LEDS_SIEMENS_SIMATIC_IPC_F7188X`, and `LEDS_SIEMENS_SIMATIC_IPC_ELKHARTLAKE` depend on `LEDS_GPIO`, the relevant pinctrl/GPIO controller option, and `SIEMENS_SIMATIC_IPC`; they default to the base SIMATIC LED option.

Control flow and integration: Kconfig selection constrains the Makefile objects so the common GPIO helper is compiled with each GPIO board wrapper. The dependencies ensure the platform base driver is present to instantiate platform devices with `struct simatic_ipc_platform` data, and that the LED/GPIO providers required by the drivers are enabled.

State and persistence: This file has no runtime state. It persists build-time policy and module names.

Risks and test signals: The default-to-base relationship can enable GPIO LED modules whenever the base option is enabled, but hard dependencies on pinctrl/GPIO providers keep impossible builds out. Build tests should cover each tristate as built-in and module, and negative dependency combinations should not expose unavailable options.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/simatic/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/simatic/Makefile -->
# sources/distributed-fs/ceph-client/drivers/leds/simatic/Makefile

Purpose: This Makefile maps SIMATIC LED Kconfig symbols to object files.

Important mappings: `CONFIG_LEDS_SIEMENS_SIMATIC_IPC` builds `simatic-ipc-leds.o`. Each GPIO hardware family builds `simatic-ipc-leds-gpio-core.o` plus its board-specific lookup-table wrapper: Apollo Lake, F7188x, or Elkhart Lake.

Control flow and dependencies: The object grouping means the common GPIO probe/remove helpers are linked into every selected GPIO variant module, while board-specific modules contribute pin mappings and platform-driver registration. There is no runtime control flow in this file.

Risks and test signals: Selecting more than one GPIO family builds multiple copies of `simatic-ipc-leds-gpio-core.o` into separate modules, which is intentional because the helper exports GPL symbols. Verify module link names and soft dependencies for each variant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/simatic/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/simatic/simatic-ipc-leds-gpio-apollolake.c -->
# sources/distributed-fs/ceph-client/drivers/leds/simatic/simatic-ipc-leds-gpio-apollolake.c

Purpose: This module provides Apollo Lake GPIO lookup tables for SIMATIC IPC LED support and delegates the actual LED device creation to the shared GPIO core helper.

Important APIs and state: `simatic_ipc_led_gpio_table` maps six active-low GPIO lines on `apollolake-pinctrl.0` to the generic `leds-gpio` device indices. `simatic_ipc_led_gpio_table_extra` maps two additional GPIOs for `PM_BIOS_BOOT_N` and `PM_WDT_OUT`; its `dev_id` is filled by the core helper during probe. The platform driver hooks are `simatic_ipc_leds_gpio_apollolake_probe()` and `_remove()`.

Control flow: Probe calls `simatic_ipc_leds_gpio_probe(pdev, &table, &table_extra)`, which validates platform device mode, registers lookup tables, creates a `leds-gpio` platform device, and requests the extra lines as outputs. Remove delegates lookup-table cleanup and `leds-gpio` unregistration to the shared helper.

Dependencies and integration: The module depends on GPIO machine lookup tables, the Apollo Lake pinctrl provider, `leds-gpio`, and platform data from the SIMATIC IPC base driver. The soft dependency requests `simatic-ipc-leds-gpio-core` and `platform:apollolake-pinctrl` first.

Risks and test signals: Correct GPIO polarity and index ordering are the main behavioral risks. Test with an IPC127E-class platform that exposes the expected pinctrl label, confirm all six LED names toggle the intended front-panel LEDs, and verify remove unloads lookup tables before devices disappear.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/simatic/simatic-ipc-leds-gpio-apollolake.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/simatic/simatic-ipc-leds-gpio-core.c -->
# sources/distributed-fs/ceph-client/drivers/leds/simatic/simatic-ipc-leds-gpio-core.c

Purpose: This shared module implements the common probe/remove path for SIMATIC IPC GPIO-based LEDs. Board-specific wrappers provide GPIO lookup tables; this file registers a generic `leds-gpio` platform device with six named status LEDs.

Important APIs and state: `simatic_ipc_gpio_leds[]` defines red/green status LED names for status groups 1 through 3. `simatic_ipc_gpio_leds_pdata` is passed to `platform_device_register_resndata()`. `simatic_leds_pdev` stores the singleton `leds-gpio` device. Exported symbols `simatic_ipc_leds_gpio_probe()` and `simatic_ipc_leds_gpio_remove()` are used by the Apollo Lake, Elkhart Lake, and F7188x modules.

Control flow: Probe checks `plat->devmode` and accepts 127E, 227G, BX-21A, and BX-59A. It adds the primary lookup table, registers `leds-gpio`, then optionally adds an extra lookup table scoped to the SIMATIC platform device and requests indices 6 and 7 as low outputs for BIOS boot and watchdog output control. Any failure calls the remove helper to unwind lookup tables and the child platform device. Remove removes both lookup tables and unregisters the singleton child platform device.

State and persistence: State is limited to the global child platform-device pointer and kernel GPIO lookup-table registration. LED state is managed by the generic `leds-gpio` driver after registration.

Risks and test signals: The helper assumes a single active GPIO LED device; concurrent multiple SIMATIC platform devices would collide through `simatic_leds_pdev`. `gpiod_remove_lookup_table(NULL)` must remain tolerated for wrappers that pass no extra table. Test accepted and rejected `devmode` values, error unwind after `leds-gpio` registration, and extra GPIO request paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/simatic/simatic-ipc-leds-gpio-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/simatic/simatic-ipc-leds-gpio-elkhartlake.c -->
# sources/distributed-fs/ceph-client/drivers/leds/simatic/simatic-ipc-leds-gpio-elkhartlake.c

Purpose: This board wrapper supplies Elkhart Lake GPIO line mappings for SIMATIC IPC GPIO LEDs.

Important APIs and state: A single `gpiod_lookup_table` maps six active-high GPIOs on ACPI controller `INTC1020:04` to `leds-gpio` indices 0-5. Probe and remove directly wrap the shared core helper with no extra GPIO table.

Control flow: Probe calls `simatic_ipc_leds_gpio_probe()` with the lookup table and `NULL` extra table. Remove calls the common remove helper with the same arguments.

Dependencies and integration: It integrates with `leds-gpio`, the Elkhart Lake pinctrl provider, and the SIMATIC IPC platform base driver. The module soft dependency names the common helper and Elkhart Lake pinctrl platform provider.

Risks and test signals: The key risk is ACPI/pinctrl naming and active-high polarity drift across board revisions. Test on BX-21A hardware by checking each of the six status LED names against physical LEDs and by unloading/reloading the module.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/simatic/simatic-ipc-leds-gpio-elkhartlake.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/simatic/simatic-ipc-leds-gpio-f7188x.c -->
# sources/distributed-fs/ceph-client/drivers/leds/simatic/simatic-ipc-leds-gpio-f7188x.c

Purpose: This board wrapper handles SIMATIC GPIO LEDs wired through Nuvoton F7188x GPIO controllers, with different lookup tables for IPC227G and BX-59A device modes.

Important APIs and state: `struct simatic_ipc_led_tables` stores selected primary and extra lookup tables in platform driver data. IPC227G uses six active-low LED lines from `gpio-f7188x-2` and two active-high extra outputs from `gpio-f7188x-3`. BX-59A uses a six-line active-low table spread across `gpio-f7188x-2`, `gpio-f7188x-5`, and `gpio-f7188x-7`.

Control flow: Probe allocates table-selection state, switches on `plat->devmode`, stores the selected tables with `platform_set_drvdata()`, then calls the common GPIO probe. Remove retrieves the table pointers and calls common cleanup.

Dependencies and integration: The module relies on `GPIO_F7188X`, the shared SIMATIC GPIO helper, the SIMATIC platform base driver, and generic `leds-gpio`. The soft dependency names `gpio_f7188x` and the core helper.

Risks and test signals: Device-mode selection is the main source of correctness. Missing extra table handling must be valid for BX-59A. Test both device modes, confirm table index ordering and polarity, and verify that a default/unknown `devmode` returns `-ENODEV` without registering lookup tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/simatic/simatic-ipc-leds-gpio-f7188x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/simatic/simatic-ipc-leds-gpio.h -->
# sources/distributed-fs/ceph-client/drivers/leds/simatic/simatic-ipc-leds-gpio.h

Purpose: This header declares the shared SIMATIC GPIO LED helper API used by board-specific GPIO mapping modules.

Important APIs: `simatic_ipc_leds_gpio_probe()` accepts a platform device plus a primary and optional extra `gpiod_lookup_table`. `simatic_ipc_leds_gpio_remove()` removes the same resources. Both are implemented in the core helper and exported GPL-only.

Control flow and state: The header has no control flow or state. It defines the contract that board wrappers pass the same table pointers to probe and remove so lookup-table lifetime is balanced.

Dependencies and risks: The declarations require `struct platform_device` and `struct gpiod_lookup_table` to be visible through including C files. Test signal is compile coverage for every wrapper using this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/simatic/simatic-ipc-leds-gpio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/simatic/simatic-ipc-leds.c -->
# sources/distributed-fs/ceph-client/drivers/leds/simatic/simatic-ipc-leds.c

Purpose: This is the legacy direct-I/O SIMATIC IPC LED class driver for platforms whose LEDs are controlled through a two-byte I/O port at `0x404E`.

Important APIs, types, and functions: `struct simatic_ipc_led` binds an active-low bit mask, LED name, and `led_classdev`. `simatic_ipc_led_set_io()` reads the port, sets or clears the LED bit, and writes it back under a spinlock. `simatic_ipc_led_get_io()` reads the active-low bit. `simatic_ipc_leds_probe()` validates the SIMATIC device mode, requests the I/O region, handles byte-swapping for `SIMATIC_IPC_DEVICE_227D`, and registers all LED class devices.

Control flow: Probe accepts `SIMATIC_IPC_DEVICE_227D` and `SIMATIC_IPC_DEVICE_427E`. For 227D, the bit values in the static LED table are byte-swapped once because the two I/O bytes are wired in the opposite order. Each table entry gets brightness set/get callbacks, max brightness `LED_ON`, and a fixed color/function name.

State and persistence: LED state persists only in the hardware I/O port. A global spinlock serializes read-modify-write access to the shared register. The static LED table is mutated for 227D byte swapping, so this driver assumes a single platform instance and a stable `devmode`.

Dependencies and integration: It integrates with `LEDS_CLASS`, `SIEMENS_SIMATIC_IPC` platform data, x86 I/O port accessors, and platform-device probing through module alias `platform:KBUILD_MODNAME`.

Risks and test signals: Static table mutation for 227D can be wrong if multiple different SIMATIC devices were ever probed in one kernel. Active-low semantics are easy to invert. Test I/O resource contention, 227D and 427E bit mappings, LED get after set, and failure when unsupported `devmode` is provided.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/simatic/simatic-ipc-leds.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/trigger/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/leds/trigger/Kconfig

Purpose: This Kconfig file defines the LED trigger subsystem menu and selectable trigger implementations.

Important entries: `LEDS_TRIGGERS` is a bool gate depending on `LEDS_CLASS`. Under it, trigger symbols cover timer, oneshot, disk, MTD, heartbeat, backlight, CPU, activity, GPIO, default-on, transient, camera, panic, netdev, pattern, TTY, and input-events. Several entries have domain dependencies: disk depends on ATA, MTD on MTD, CPU excludes PREEMPT_RT, GPIO depends on GPIOLIB or compile test, netdev depends on NET, TTY depends on TTY, and input-events depends on INPUT.

Control flow and integration: These symbols drive the trigger Makefile and indirectly expose sysfs trigger names for LED class devices. Some options are bool because they provide exported hooks used by core subsystems or boot-time/device-init triggers; others are tristate modules.

State and persistence: This file stores build-time policy only.

Risks and test signals: Dependency regressions can break allmodconfig or create dangling exported APIs. Test all relevant config combinations, especially triggers built as modules with LED core built-in and bool triggers that use `device_initcall()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/trigger/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/trigger/Makefile -->
# sources/distributed-fs/ceph-client/drivers/leds/trigger/Makefile

Purpose: This Makefile maps LED trigger Kconfig symbols to the trigger implementation objects in `drivers/leds/trigger`.

Important mappings: Each `CONFIG_LEDS_TRIGGER_*` symbol builds one `ledtrig-*.o` object. This includes timer, oneshot, disk, MTD, heartbeat, backlight, GPIO, CPU, activity, default-on, transient, camera, panic, netdev, pattern, TTY, and input-events.

Control flow and dependencies: There is no runtime logic. The file controls which trigger modules or built-in objects provide trigger names and exported control functions.

Risks and test signals: Missing object mapping silently removes a selected trigger. Build coverage should verify every Kconfig symbol results in the expected object or module name.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/trigger/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/trigger/ledtrig-activity.c -->
# sources/distributed-fs/ceph-client/drivers/leds/trigger/ledtrig-activity.c

Purpose: The activity trigger blinks an LED according to immediate aggregate CPU usage, with faint slow flashes when idle and higher duty/frequency under load. On panic it leaves the LED at full brightness.

Important APIs and state: `struct activity_data` stores a timer, LED pointer, last CPU-used and boot-time totals, remaining timing budget, blink state, and `invert` sysfs setting. `led_activity_function()` is the timer callback. `activity_activate()` allocates state and starts the timer; `activity_deactivate()` shuts it down. Sysfs exposes `invert`. Reboot and panic notifier blocks unregister or force panic behavior.

Control flow: The timer samples per-CPU kernel cpustats and boot time, computes a percentage, toggles LED state when the current pulse expires, calculates the next on/off delay, caps sleeps to 100 ms for responsiveness, and rearms itself. It also handles `LED_BLINK_BRIGHTNESS_CHANGE`. Activation initializes blink brightness and calls the timer function once to start the cycle.

State and persistence: Per-LED state is heap allocated and stored as trigger data. A global `panic_detected` flag permanently changes behavior after panic notification. There is no persistence across trigger deactivation.

Dependencies and integration: It depends on cpustat accessors, timers, reboot and panic notifier chains, LED trigger registration, and internal LED work flags.

Risks and test signals: CPU accounting math shifts values down to avoid overflow; large CPU-count systems and wraparound deserve coverage. Timer teardown uses `timer_shutdown_sync()`, so deactivate should be safe against callbacks. Test invert sysfs, brightness changes, panic/reboot notifier behavior, and CPU-load response.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/trigger/ledtrig-activity.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/trigger/ledtrig-backlight.c -->
# sources/distributed-fs/ceph-client/drivers/leds/trigger/ledtrig-backlight.c

Purpose: The backlight trigger lets LEDs emulate display backlight blank/unblank state. External display/backlight code calls `ledtrig_backlight_blank()` to turn registered LEDs off or restore brightness.

Important APIs and state: `struct bl_trig_notifier` stores the LED pointer, saved brightness, previous blank state, invert setting, and list node. `ledtrig_backlight_blank(bool blank)` is exported. Sysfs exposes `inverted`. A global list of active trigger instances is protected by `ledtrig_backlight_list_mutex`.

Control flow: Activation allocates notifier state, records current brightness and `UNBLANK`, then links it into the global list. The exported blank callback locks the list and updates each LED only when state changes. Inverting sysfs immediately recomputes current LED brightness.

State and persistence: Per-LED saved brightness and old blank status live until deactivation. No hardware state is persisted outside the LED class brightness setting.

Dependencies and integration: It integrates with LED triggers and any backlight/display path that calls the exported blank function.

Risks and test signals: Correctness depends on callers consistently reporting blank state. Saved brightness can be stale if the LED brightness changes while blanked. Test activation/deactivation under concurrent blank events, invert toggling, and exported symbol use from display code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/trigger/ledtrig-backlight.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/trigger/ledtrig-camera.c -->
# sources/distributed-fs/ceph-client/drivers/leds/trigger/ledtrig-camera.c

Purpose: This trigger provides simple global camera flash and torch LED triggers controlled by exported kernel functions.

Important APIs and state: `DEFINE_LED_TRIGGER(ledtrig_flash)` and `DEFINE_LED_TRIGGER(ledtrig_torch)` hold trigger pointers. `ledtrig_flash_ctrl(bool on)` and `ledtrig_torch_ctrl(bool on)` export on/off control and call `led_trigger_event()` with `LED_FULL` or `LED_OFF`.

Control flow: Module init registers simple triggers named `flash` and `torch`; exit unregisters torch then flash. No per-LED activation state is used.

Dependencies and integration: Camera flash/torch drivers can bind LEDs to these trigger names and call the exported GPL control functions.

Risks and test signals: There is no locking beyond LED trigger core behavior. Test module load/unload, exported controls with no LED attached, and both trigger names appearing in LED trigger lists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/trigger/ledtrig-camera.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/trigger/ledtrig-cpu.c -->
# sources/distributed-fs/ceph-client/drivers/leds/trigger/ledtrig-cpu.c

Purpose: The CPU trigger exposes per-CPU LED triggers for CPU0-CPU7 and an aggregate `cpu` trigger whose brightness reflects the proportion of active CPUs.

Important APIs and state: `struct led_trigger_cpu` is per-CPU state with active flag, name, and trigger pointer. `ledtrig_cpu(enum cpu_led_event ledevt)` is exported for architecture or idle code to signal CPU activity. `trig_cpu_all` is the aggregate trigger. `num_active_cpus` tracks active CPUs atomically. Syscore and CPU hotplug callbacks translate suspend/resume/shutdown/online/down events to trigger events.

Control flow: Init registers the aggregate trigger, registers up to eight per-CPU triggers, registers syscore callbacks, and installs a dynamic CPU hotplug state. `ledtrig_cpu()` updates current CPU active state, adjusts the active count, fires the per-CPU LED full/off, and updates aggregate brightness.

State and persistence: State lives in per-CPU storage and an atomic global. It persists for the lifetime of the built-in trigger and has no module exit path.

Dependencies and integration: It integrates with the LED core, CPU hotplug, syscore suspend/resume, and kernel CPU event callers. It is disabled on PREEMPT_RT by Kconfig.

Risks and test signals: Only CPU0-CPU7 get individual triggers while aggregate covers all present CPUs. Mismatched START/STOP events can skew `num_active_cpus`. Test hotplug online/down, suspend/resume, aggregate brightness on multi-core systems, and no overrun with high `CONFIG_NR_CPUS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/trigger/ledtrig-cpu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/trigger/ledtrig-default-on.c -->
# sources/distributed-fs/ceph-client/drivers/leds/trigger/ledtrig-default-on.c

Purpose: The default-on trigger sets an LED to maximum brightness when the trigger is activated.

Important APIs and control flow: `defon_trig_activate()` calls `led_set_brightness_nosleep()` with `max_brightness`. `module_led_trigger(defon_led_trigger)` registers the trigger named `default-on`.

State and dependencies: There is no per-trigger state, no sysfs attributes, and no persistence beyond the LED class brightness. It depends only on the LED trigger core.

Risks and test signals: Behavior is intentionally minimal. Test that selecting the trigger on a LED sets full brightness and that the module alias `ledtrig:default-on` resolves.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/trigger/ledtrig-default-on.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/trigger/ledtrig-disk.c -->
# sources/distributed-fs/ceph-client/drivers/leds/trigger/ledtrig-disk.c

Purpose: The disk trigger exports disk activity indications through three trigger names: aggregate disk activity, disk read, and disk write.

Important APIs and state: `ledtrig_disk_activity(bool write)` is exported and blinks `disk-activity` plus either `disk-write` or `disk-read` using `led_trigger_blink_oneshot()` with a fixed 30 ms on/off delay. Trigger pointers are defined with `DEFINE_LED_TRIGGER`.

Control flow: `device_initcall(ledtrig_disk_init)` registers all three simple triggers. There is no exit path because this bool trigger is built in.

Dependencies and integration: Storage code can call the exported symbol to report read/write activity. Kconfig depends on ATA.

Risks and test signals: The fixed delay is simple but can coalesce under high I/O. Test trigger registration, exported calls before/after LED binding, and read/write-specific blink selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/trigger/ledtrig-disk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/trigger/ledtrig-gpio.c -->
# sources/distributed-fs/ceph-client/drivers/leds/trigger/ledtrig-gpio.c

Purpose: The GPIO trigger drives an LED from a GPIO input, typically described by the LED device's `trigger-sources` property.

Important APIs and state: `struct gpio_trig_data` stores the LED pointer, desired on brightness, and GPIO descriptor. Sysfs exposes `desired_brightness`. `gpio_trig_irq()` reads the GPIO value and sets LED brightness full/desired or off.

Control flow: Activation allocates state, obtains an optional GPIO named `trigger-sources` as input, names it `led-trigger`, requests a shared threaded IRQ on both rising and falling edges, and calls the IRQ handler once for initial state. Deactivation frees the IRQ, releases the GPIO, and frees state.

State and persistence: Per-LED trigger state lives until deactivation. Brightness follows the current GPIO level and requested brightness value; no state persists across trigger changes.

Dependencies and integration: It depends on GPIOLIB, LED trigger core, IRQ support, and firmware properties for trigger source mapping.

Risks and test signals: `gpiod_get_value_cansleep()` is used in a threaded IRQ, which is appropriate for sleeping GPIO providers. Missing GPIO returns `-EINVAL`. Test firmware property resolution, IRQ edge handling, desired brightness sysfs, and teardown while interrupts fire.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/trigger/ledtrig-gpio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/trigger/ledtrig-heartbeat.c -->
# sources/distributed-fs/ceph-client/drivers/leds/trigger/ledtrig-heartbeat.c

Purpose: The heartbeat trigger produces a double-pulse LED pattern whose period varies with the one-minute load average.

Important APIs and state: `struct heartbeat_trig_data` stores the LED, phase, period, timer, and invert flag. `led_heartbeat_function()` implements the phase machine. Sysfs exposes `invert`. Reboot and panic notifiers unregister or suppress blinking on panic.

Control flow: Activation allocates trigger data, initializes a timer, sets blink brightness, starts the heartbeat function, and marks software blinking. The timer cycles through four phases: on pulse, pause, second on pulse, long pause. Phase 0 recalculates period from `avenrun[0]`. Deactivation shuts down the timer and clears software blink state.

State and persistence: Per-LED phase state is transient. Global `panic_heartbeats` stops heartbeat output once a panic is observed.

Dependencies and integration: It uses LED core, timers, scheduler load average, panic notifier, and reboot notifier chains.

Risks and test signals: Delay arithmetic assumes period stays larger than pulse widths; load-average extremes should be checked. Test invert behavior, panic path, reboot unregister, brightness-change work flag, and trigger deactivation while timer is active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/trigger/ledtrig-heartbeat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/trigger/ledtrig-input-events.c -->
# sources/distributed-fs/ceph-client/drivers/leds/trigger/ledtrig-input-events.c

Purpose: The input-events trigger turns LEDs on after input activity and off after a configurable idle delay, intended for keyboard or capacitive-button backlights.

Important APIs and state: Global `input_events_data` contains delayed work, a spinlock, `led_on`, and `led_off_time`. Module parameter `led_off_delay_ms` controls idle timeout. An input handler subscribes to devices with EV_KEY, EV_REL, or EV_ABS support. `input_events_led_trigger` is the simple trigger pointer.

Control flow: Init initializes work and lock, registers the trigger named `input-events`, then registers the input handler. On each input event, the spinlocked path turns the trigger on if not already on, updates the off deadline, and schedules delayed work. The work function checks if the deadline has actually passed before turning the trigger off, avoiding races with new events.

State and persistence: State is global across all input devices and all LEDs bound to the trigger. It persists until module exit. LED on/off is trigger-wide rather than per input device.

Dependencies and integration: It depends on the input core, system per-CPU workqueue, LED trigger core, jiffies timing, and module parameters.

Risks and test signals: High event rates should not repeatedly call `led_trigger_event(LED_FULL)` thanks to `led_on`. Race coverage around delayed work and new events is important. Test handler connect/disconnect, off delay parameter, multiple input devices, nonblocking module exit, and delayed work cancellation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/trigger/ledtrig-input-events.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/trigger/ledtrig-mtd.c -->
# sources/distributed-fs/ceph-client/drivers/leds/trigger/ledtrig-mtd.c

Purpose: The MTD trigger provides activity LEDs for MTD/NAND operations.

Important APIs and state: It defines trigger pointers `ledtrig_mtd` and `ledtrig_nand`. Exported `ledtrig_mtd_activity()` blinks both triggers with fixed 30 ms on/off delays.

Control flow: `device_initcall(ledtrig_mtd_init)` registers simple triggers named `mtd` and `nand-disk`. There is no exit path for the bool trigger.

Dependencies and integration: MTD code calls the exported symbol to report activity. Kconfig depends on MTD.

Risks and test signals: Fixed one-shot blink behavior may coalesce under heavy I/O. Test trigger registration, exported call paths, and operation when no LED is attached.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/trigger/ledtrig-mtd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/trigger/ledtrig-netdev.c -->
# sources/distributed-fs/ceph-client/drivers/leds/trigger/ledtrig-netdev.c

Purpose: The netdev trigger drives LEDs from a named network interface's link, speed, duplex, RX/TX, and error activity. It can either use software polling/blinking or offload supported modes to LED hardware control.

Important APIs and state: `struct led_netdev_data` stores a mutex, delayed work, netdevice notifier, LED pointer, held `net_device`, selected device name, blink interval, last activity counter, mode bitset, cached link speed/duplex/supported modes, carrier state, and hardware-control flag. Sysfs attributes include `device_name`, link and speed bits, half/full duplex, rx/tx/error bits, `interval`, and readonly `offloaded`.

Control flow: Activation allocates state, initializes interval, detects existing hardware-control default, sets trigger data, and registers a netdevice notifier. `device_name_store()` cancels work, takes RTNL then the trigger mutex, swaps the held netdevice reference, refreshes link state, and updates baseline LED state. Mode stores validate mutually exclusive generic link vs speed-specific modes, recompute hardware-control suitability, and set a baseline. Netdevice notifier responds to up/down/change/register/unregister/rename events for the tracked device, updates cached state, refreshes link-speed sysfs visibility, and resets baseline. Delayed work samples stats, detects selected activity counter changes, and blinks oneshot with inversion if link baseline is on.

State and persistence: Per-LED trigger state owns a netdevice reference when configured and persists until deactivation. Hardware offload state is delegated through LED class `hw_control_*` callbacks when available and valid. Software state uses delayed work and cached last activity.

Dependencies and integration: It depends on NET, ethtool link settings, RTNL locking, netdevice notifier chain, LED trigger core, optional LED hardware-control callbacks, and sysfs attribute groups with dynamic visibility for supported link speeds.

Risks and test signals: Lock ordering is explicit: RTNL before trigger mutex in device-name changes. `dev_put(trigger_data->net_dev)` is called in several paths and must handle NULL safely. Hardware-control mode rejects non-default intervals and mismatched associated netdevs. Test rename/register/unregister, interface removal while work is queued, speed attribute visibility, unsupported offload fallback, LEDs without software brightness callbacks, all mode-bit combinations, and RX/TX/error polling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/trigger/ledtrig-netdev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/trigger/ledtrig-oneshot.c -->
# sources/distributed-fs/ceph-client/drivers/leds/trigger/ledtrig-oneshot.c

Purpose: The oneshot trigger exposes a manual pulse trigger with configurable on/off delays and invert behavior.

Important APIs and state: `struct oneshot_trig_data` stores `invert`. Sysfs attributes are `delay_on`, `delay_off`, `invert`, and write-only `shot`. `led_shot()` calls `led_blink_set_oneshot()` using the LED's delay fields and invert flag.

Control flow: Activation allocates state and, for LEDs initialized with a default trigger pattern, reads a two-value default pattern into `blink_delay_on/off` or falls back to 100 ms defaults. Writing `shot` starts a oneshot blink. Writing `invert` updates the idle brightness to full or off. Deactivation frees state and turns the LED off.

State and persistence: Delay values are stored in the LED class device; invert is per-trigger data. Default-trigger initialization clears `LED_INIT_DEFAULT_TRIGGER` to avoid repeated parsing.

Dependencies and integration: It uses LED class blink helpers, firmware default pattern helpers, and trigger sysfs groups.

Risks and test signals: Default pattern size must be exactly two values. Deactivation should stop any ongoing blink. Test pattern initialization, invalid sysfs values, invert idle state, repeated shot writes, and LEDs with hardware blink support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/trigger/ledtrig-oneshot.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/trigger/ledtrig-panic.c -->
# sources/distributed-fs/ceph-client/drivers/leds/trigger/ledtrig-panic.c

Purpose: The panic trigger redirects LEDs marked `LED_PANIC_INDICATOR` to a panic blink trigger and installs the global `panic_blink` hook.

Important APIs and state: A global `trigger` pointer stores the simple trigger named `panic`. `led_trigger_set_panic()` moves a LED class device onto the panic trigger list and clears blink delays to avoid delayed blinking. `led_trigger_panic_notifier()` scans global `leds_list` for panic indicators. `led_panic_blink()` emits full/off events for the panic blink state.

Control flow: Device init registers the trigger, registers an atomic panic notifier, and assigns `panic_blink`. On panic, matching LEDs are forcibly rebound to the panic trigger without normal locking because panic context is special.

State and persistence: Once panic occurs, LED trigger list membership is changed for panic-indicator LEDs. There is no unload path.

Dependencies and integration: It depends on LED core internals (`leds_list`, trigger lists), panic notifier chain, and the global panic blink callback.

Risks and test signals: Panic context intentionally bypasses normal locking, so only minimal list operations are performed. Test with LEDs flagged as panic indicators, no-indicator systems, and panic blinking in atomic context.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/trigger/ledtrig-panic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/trigger/ledtrig-pattern.c -->
# sources/distributed-fs/ceph-client/drivers/leds/trigger/ledtrig-pattern.c

Purpose: The pattern trigger plays brightness/duration tuples through software timers, high-resolution timers, or LED hardware pattern callbacks when available.

Important APIs and state: `struct pattern_trig_data` holds the LED, up to 1024 `struct led_pattern` tuples, current/next pointers, mutex, repeat counters, interpolation state, pattern type, timer, and hrtimer. Sysfs exposes `pattern`, `hr_pattern`, `hw_pattern` when hardware supports it, and `repeat`. Activation validates hardware `pattern_set`/`pattern_clear` pairing and initializes timers.

Control flow: Pattern stores cancel current playback, clear hardware pattern if needed, parse tuples from text or firmware default data, set the requested type, and call `pattern_trig_start_pattern()`. Software playback requires at least two tuples and starts either timer. The common timer function advances current/next tuples, handles finite repeat counts, applies step changes immediately, interpolates brightness every 50 ms for gradual dimming, and schedules the next callback. Hardware pattern playback delegates the full tuple array and repeat count to the LED driver. Repeat changes restart playback with the new repeat mode.

State and persistence: Per-LED trigger state persists until deactivation. Pattern tuples and repeat values are in memory only. `LED_INIT_DEFAULT_TRIGGER` is cleared after default pattern parsing. Hardware pattern state may persist in the LED driver until `pattern_clear()`.

Dependencies and integration: It integrates with LED class pattern callbacks, firmware `led_get_default_pattern()`, normal timers, hrtimers, sysfs attribute visibility, and LED brightness helpers.

Risks and test signals: Text parsing must avoid exceeding `MAX_PATTERNS` and must reject brightness over max. `pattern_trig_show_patterns()` assumes count is nonzero before writing newline. Timer/hrtimmer cancellation under sysfs mutation is protected by the mutex. Test finite and indefinite repeats, invalid tuple counts, gradual dimming, zero-duration tuples, hrtimer mode, hardware callbacks, default pattern init, and deactivation during active playback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/trigger/ledtrig-pattern.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/trigger/ledtrig-timer.c -->
# sources/distributed-fs/ceph-client/drivers/leds/trigger/ledtrig-timer.c

Purpose: The timer trigger blinks an LED continuously with configurable `delay_on` and `delay_off` intervals.

Important APIs and state: Sysfs attributes `delay_on` and `delay_off` read and write `led_cdev->blink_delay_on/off`. Stores call `led_blink_set()` with updated timing. `pattern_init()` optionally reads a two-value default pattern into delay fields for LEDs initialized with this trigger.

Control flow: Activation parses default pattern if requested, clears the initialization flag, and starts blinking with the LED class blink helper. Deactivation turns the LED off.

State and persistence: Blink delays are stored on the LED class device. Hardware or software blink state is owned by LED core and the LED driver. No private trigger data is allocated.

Dependencies and integration: It uses LED class blink helpers, firmware pattern helpers, trigger sysfs groups, and `module_led_trigger()`.

Risks and test signals: Invalid default pattern sizes warn and are ignored. Delay values are unsigned long with no explicit bounds here. Test delay sysfs, zero/default delays, default pattern parsing, deactivation stopping blink, and drivers with hardware blink callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/trigger/ledtrig-timer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/trigger/ledtrig-transient.c -->
# sources/distributed-fs/ceph-client/drivers/leds/trigger/ledtrig-transient.c

Purpose: The transient trigger provides a one-shot timed activation for LEDs, primarily for GPIO/PWM hardware that needs a temporary state then restoration.

Important APIs and state: `struct transient_trig_data` stores activate flag, target state, restore state, duration, timer, and LED pointer. Sysfs attributes are `activate`, `duration`, and `state`.

Control flow: Activation allocates state and initializes the timer. Writing `state` selects the transient brightness as full or off. Writing `duration` sets the timer length in milliseconds. Writing `activate=1` starts a timer only if not already active and duration is nonzero, sets the LED to target state, computes opposite restore state, and arms the timer. Writing `activate=0` while active deletes the timer and restores state immediately. Timer expiry clears activate and restores brightness. Deactivation shuts down the timer, restores brightness, and frees state.

State and persistence: State is per LED and in memory only. `restore_state` is computed as the opposite of target state, not the previous LED brightness.

Dependencies and integration: It uses LED trigger sysfs, kernel timers, and LED brightness helpers.

Risks and test signals: There is no mutex around sysfs/timer fields, so tests should stress concurrent sysfs writes and expiry. `timer_delete()` in sysfs cancel is not synchronous, while deactivate uses `timer_shutdown_sync()`. Test duration zero, repeated activate writes, state toggles, cancel behavior, and deactivation during active timer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/trigger/ledtrig-transient.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/trigger/ledtrig-tty.c -->
# sources/distributed-fs/ceph-client/drivers/leds/trigger/ledtrig-tty.c

Purpose: The TTY trigger monitors a named TTY for RX/TX counter changes and modem-control line states, then blinks or enables/disables a LED.

Important APIs and state: `struct ledtrig_tty_data` stores LED pointer, delayed work, a completion used to serialize some sysfs operations with the polling worker, configured tty name, held `tty_struct`, last rx/tx counters, and mode booleans for rx, tx, cts, dsr, dcd, and rng. Sysfs exposes `ttyname` and all mode booleans. Default mode enables rx and tx.

Control flow: Activation allocates state, initializes delayed work and completion, stores trigger data, and schedules the worker immediately. The worker resolves `ttyname` to a device number when needed, opens a shared TTY reference, reads modem-control bits, checks rx/tx counters after line-state evaluation so activity has priority, then either blinks oneshot, sets brightness to blink brightness, or turns off. It completes sysfs waiters and reschedules itself every 100 ms. `ttyname_store()` trims newline, waits for the worker completion, drops any old TTY reference, and replaces the name. Deactivation cancels work, frees the name, drops the TTY reference, and frees state.

State and persistence: Per-LED trigger state persists until deactivation. The TTY reference is held once resolved and released when the name changes or trigger deactivates. There is no persisted configuration across trigger changes.

Dependencies and integration: It depends on TTY core helpers, serial icounter APIs, LED blink helpers, delayed work, sysfs attributes, and completions.

Risks and test signals: Sysfs synchronization uses completion timeouts tied to the polling interval; a wedged worker can cause `-ETIMEDOUT`. Mode stores are not completion-serialized. Test nonexistent TTY retry, TTY hotplug/removal, rx/tx blinking priority over line-state enable, modem-control modes, name replacement, and deactivation with a held TTY.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/trigger/ledtrig-tty.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/uleds.c -->
# sources/distributed-fs/ceph-client/drivers/leds/uleds.c

Purpose: `uleds` is a misc-device based userspace LED provider. A userspace process writes a `struct uleds_user_dev` to `/dev/uleds` to register a LED class device, then reads brightness changes generated by kernel LED users.

Important APIs and state: `struct uleds_device` contains the userspace descriptor, LED class device, mutex, registration state, waitqueue, current brightness, and `new_data` flag. File operations are open, read, write, poll, and release. `uleds_brightness_set()` is the LED class brightness callback.

Control flow: Open allocates per-file state and initializes the embedded LED class device name pointer to the user descriptor name buffer. Write validates size, name, and max brightness, then registers the LED with the misc device as parent and marks data available. Brightness callbacks update the brightness field, mark new data, and wake readers. Read blocks unless data is available or the device is unregistered, copies an `int` brightness to userspace, and clears `new_data`. Poll reports readable when new data exists. Release unregisters the LED if registered and frees state.

State and persistence: Each open file can create at most one LED. The LED lifetime is bound to the file descriptor. There is no persistence after close. The mutex protects write/read state transitions, but the brightness callback updates fields without taking that mutex.

Dependencies and integration: It integrates with miscdevice registration, LED class registration, user ABI `uapi/linux/uleds.h`, waitqueues, poll, and copy_to/from_user.

Risks and test signals: `uleds_read()` unconditionally sets `retval = sizeof(udev->brightness)` after `copy_to_user()`, losing `-EFAULT` if copying fails; that is a notable bug signal. Brightness callback lockless updates can race with read/release. Test invalid names, invalid size, max brightness <= 0, duplicate writes after registration, blocking/nonblocking reads, poll, close while blocked, and fault-injection for user copies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/uleds.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/macintosh/Kconfig

Purpose: This Kconfig menu defines Macintosh-specific driver options for ADB, PMU/CUDA/SMU system controllers, PowerMac backlight and thermal management, Mac input emulation, and Apple Motion Sensor support.

Important entries: `MACINTOSH_DRIVERS` gates the submenu for PPC, m68k Mac, and x86 builds. ADB options select controller backends (`ADB_MACII`, `ADB_IOP`, `ADB_CUDA`, `ADB_PMU`, `ADB_MACIO`) and input integration (`INPUT_ADBHID`). PMU LED/backlight/APM options integrate with LED, ATA, backlight, and PM frameworks. Thermal entries cover Windtunnel, ADT746x, and windfarm families. `SENSORS_AMS` selects the Apple Motion Sensor aggregate module with PMU and I2C backend options.

Control flow and integration: These symbols determine which Macintosh platform objects are compiled by the Makefile and which cross-subsystem interfaces are available, such as ADB client notifications, input devices, LED triggers, RTC library, and I2C PowerMac support.

State and persistence: Kconfig stores build-time feature policy only.

Risks and test signals: Many dependencies are architecture-specific and include legacy `BROKEN` gates; allmodconfig and randconfig coverage on PPC, m68k Mac, and x86 are important. AMS dependency combinations are subtle because PMU and I2C variants can be enabled together or independently.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/Makefile -->
# sources/distributed-fs/ceph-client/drivers/macintosh/Makefile

Purpose: This Makefile maps Macintosh driver Kconfig options to object files and subdirectories.

Important mappings: It builds MacIO support for `PPC_PMAC`, media bay, Mac HID emulated mouse buttons, ADB HID, ANS LCD, PMU/CUDA/SMU and related LED/backlight/APM/event objects, ADB core and controller backends, thermal drivers, windfarm thermal modules, rack-meter, and the AMS subdirectory.

Control flow and dependencies: There is no runtime logic. Multi-object windfarm configurations list the shared control/sensor/PID objects needed by each machine family. `CONFIG_SENSORS_AMS` descends into `ams/`.

Risks and test signals: Object sharing across windfarm targets can cause duplicate symbol or missing dependency problems if Kconfig changes. Build-test key PPC/m68k configurations and module/built-in combinations where supported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/adb-iop.c -->
# sources/distributed-fs/ceph-client/drivers/macintosh/adb-iop.c

Purpose: This is an Apple Desktop Bus controller backend for Macintosh systems with an I/O Processor (IOP), such as IIfx/Quadra 9x0-class systems. It adapts unified ADB requests to IOP messages and handles autopoll responses.

Important APIs and state: It provides `struct adb_driver adb_iop_driver` with probe, init, send_request, autopoll, poll, and reset_bus callbacks. Global request queue state is `current_req`, `last_req`, and `adb_iop_state` (`idle`, `sending`, `awaiting_reply`). Autopoll state is `autopoll_devs` and `autopoll_addr`.

Control flow: `adb_iop_write()` validates ADB packets, initializes request fields, queues them under local IRQ masking, and starts sending if idle. `adb_iop_start()` strips the leading `ADB_PACKET` byte, wraps the remaining packet in `struct adb_iopmsg`, marks the request sent, and submits to the IOP manager. `adb_iop_complete()` marks the state as awaiting a reply after send completion. `adb_iop_listen()` handles explicit replies and autopoll messages, copies replies into the current ADB request when expected, forwards valid autopoll packets to `adb_input()`, prepares the IOP reply that selects the next autopoll address, completes the IOP message, and finalizes the ADB request if applicable.

State and persistence: State is global to the single IOP ADB controller. Local IRQ disabling protects request queue and state transitions. Autopoll device masks are remembered in globals and programmed through IOP messages.

Dependencies and integration: It depends on m68k Macintosh IOP infrastructure, `linux/adb.h`, `asm/adb_iop.h`, unaligned helpers, and the ADB core's driver table. It calls `adb_input()` for autopoll data.

Risks and test signals: Synchronous sends busy-poll `adb_iop_poll()` until completion. Request lifecycle assumes one explicit reply at a time. Autopoll address selection depends on IOP flags and masks. Test queue ordering, explicit requests with and without reply, autopoll enable/disable masks, reset-bus delay, and timeout packets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/adb-iop.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/adb.c -->
# sources/distributed-fs/ceph-client/drivers/macintosh/adb.c

Purpose: This file is the unified Apple Desktop Bus core and `/dev/adb` character-device interface. It selects one platform ADB controller, scans and resets the bus, dispatches ADB input to registered device handlers, manages sleep/reset notifications, and exposes user requests through major 56.

Important APIs and state: Exported APIs include `adb_request()`, `adb_register()`, `adb_unregister()`, `adb_input()`, `adb_try_handler_change()`, `adb_get_infos()`, `adb_poll()`, and the blocking notifier head `adb_client_list`. `struct adb_handler` records per-address handler, original address, handler ID, and busy flag. Handler metadata is protected by `adb_handler_mutex`; dispatch uses `adb_handler_lock` rwlock. `/dev/adb` uses `struct adbdev_state` with pending count, completed request list, waitqueue, spinlock, and in-use flag.

Control flow: `adb_init()` filters unsupported machines, chooses the first probing controller backend from the compiled list, initializes it, creates `/dev/adb`, and schedules an ADB bus reset. `do_adb_reset_bus()` disables autopoll, sends pre-reset notifications, clears handler state, asks the controller to reset, scans devices, enables autopoll for detected devices, and sends post-reset notifications. `adb_scan_bus()` probes addresses, handles collisions by moving devices to a high free address, records original addresses and handler IDs, and returns an autopoll mask. `adb_request()` builds an ADB packet and optionally waits on a completion for synchronous requests. `adb_input()` dispatches packets by address unless sleep is in progress.

`/dev/adb` control flow: `adb_write()` copies a request from userspace, increments pending count, waits for probe/reset mutex, handles special ADB queries and bus reset, or sends to the controller. Completion callback `adb_write_done()` queues replies for readers or frees requests after close. `adb_read()` waits for a completed request, copies its reply to userspace, and frees it.

State and persistence: The selected controller, handler table, autopoll mask, sleep state, and `/dev/adb` open state are global kernel runtime state. Device address assignments are rederived on every bus reset. PM suspend disables autopoll and notifies clients; resume schedules a new reset.

Dependencies and integration: It integrates with ADB controller backends, platform device PM hooks, character-device registration, device class creation, blocking notifier clients such as ADB HID, OF/machine detection, and PowerMac/m68k architecture code.

Risks and test signals: Bus scanning and handler changes are legacy protocol-sensitive. `adb_unregister()` waits for busy handlers by yielding while holding/releasing the write lock. `/dev/adb` close with pending requests relies on `inuse` and pending count to free state. Test controller absence, reset during userspace requests, sleep/resume notifications, handler registration conflicts, user query handling, nonblocking reads, and bus reset from userspace.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/adb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/adbhid.c -->
# sources/distributed-fs/ceph-client/drivers/macintosh/adbhid.c

Purpose: `adbhid.c` translates Apple Desktop Bus keyboards, mice, trackpads, trackballs, and miscellaneous buttons into Linux input devices. It also programs keyboard LEDs and performs device-specific handler/init sequences.

Important APIs, types, and state: `struct adbhid` stores the input device, ADB id/default/original/current handler IDs, mouse kind, keycode table, names, and flags for Fn/power/caps-lock translation. Global `adbhid[16]` indexes active ADB devices. The ADB notifier `adbhid_adb_notifier` reacts to pre-reset, powerdown, and post-reset events. Input handlers are `adbhid_keyboard_input()`, `adbhid_mouse_input()`, and `adbhid_buttons_input()`. `adbhid_kbd_event()` sends keyboard LED updates back to ADB hardware.

Control flow: Module init gates unsupported machines, marks LED request complete, probes ADB devices, then registers the ADB notifier. `adbhid_probe()` registers ADB handlers for mouse, keyboard, and misc devices, configures keyboard LEDs/handler IDs, identifies and initializes mouse variants through handler changes and register reads, registers or reregisters Linux input devices, and cleans up devices no longer present. Keyboard input validates register 0 packets and reports translated key events, including special caps-lock, Fn-delete, and power-key handling. Mouse input normalizes multiple ADB mouse protocols into BTN_LEFT/MIDDLE/RIGHT and REL_X/Y reports. Misc button input maps audio, eject, brightness, video, and keyboard illumination buttons.

State and persistence: Device state persists in `adbhid[]` until a reset cleanup removes absent devices. Keyboard LED requests are serialized with `leds_lock`, a single global `led_request`, per-device pending LED values, and a ring of pending devices. Caps-lock translation state survives suspend enough to ignore a spurious resume event.

Dependencies and integration: It depends on the ADB core registration/notification API, Linux input core, PMU/CUDA headers, optional PowerMac backlight helpers, and ADB request primitives for handler changes and register writes.

Risks and test signals: The protocol matrix is large and hardware-specific. LED request queuing uses static state and should be stress-tested with rapid LED changes. `adbhid_exit()` is empty, so practical unloading support is limited. Test keyboard type mappings, ISO key swap, caps-lock modes, Fn/delete and Fn/command power translations, all mouse handler fallbacks, reset/powerdown notifier behavior, and input device cleanup after bus topology changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/adbhid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/ams/Makefile -->
# sources/distributed-fs/ceph-client/drivers/macintosh/ams/Makefile

Purpose: This Makefile builds the Apple Motion Sensor composite module.

Important mappings: `ams-y` always includes `ams-core.o` and `ams-input.o`. `CONFIG_SENSORS_AMS_PMU` adds `ams-pmu.o`; `CONFIG_SENSORS_AMS_I2C` adds `ams-i2c.o`. `CONFIG_SENSORS_AMS` builds `ams.o`.

Control flow and dependencies: There is no runtime logic. The object composition matches the runtime backend selection in `ams-core.c`, where I2C is tried before PMU if both are enabled.

Risks and test signals: Backend-only build combinations must still provide the symbols referenced by core through Kconfig guards. Build-test PMU-only, I2C-only, and both-backend configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/ams/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/ams/ams-core.c -->
# sources/distributed-fs/ceph-client/drivers/macintosh/ams/ams-core.c

Purpose: This is the Apple Motion Sensor core. It discovers the sensor backend, normalizes axis orientation, exposes current x/y/z values through sysfs, handles freefall/shock interrupts, and coordinates joystick-style input registration.

Important APIs and state: Global `struct ams ams_info` is the singleton device state. `ams_sensors()` calls the backend `get_xyz()` and applies orientation swap/invert bits. `ams_sensor_attach()` reads OF orientation, registers PMF interrupt clients, creates an OF platform device named `ams`, creates the `current` sysfs file, determines vendor flag, and initializes optional input. `ams_sensor_detach()` removes input/sysfs/device/interrupt clients. `ams_worker()` handles pending interrupt bits and calls backend `clear_irq()`.

Control flow: Module init initializes locks and work, then looks for an I2C node named `accelerometer` compatible with `AAPL,accelerometer_1` if I2C is enabled, otherwise/then a PMU node named `sms` compatible with `sms` if PMU is enabled. The chosen backend fills function pointers and calls `ams_sensor_attach()`. Interrupt handlers only set bits under `irq_lock` and schedule work; the worker takes the main mutex before clearing hardware interrupts.

State and persistence: Singleton runtime state includes OF nodes/devices, orientation values, backend callbacks, vendor flag, pending IRQ bits, input device pointer, and calibration offsets in `ams_info`. No configuration persists beyond module parameters and firmware properties.

Dependencies and integration: It depends on Open Firmware platform creation, PMF interrupt clients, backend modules, input helper code, and PowerMac platform function infrastructure.

Risks and test signals: `ams_sensor_detach()` flushes work after sysfs/input removal but before unregistering PMF clients; comments note interrupts can arrive before backend disable. Orientation property length is assumed to include two u32s. Test backend discovery precedence, missing/short orientation property, freefall/shock IRQ coalescing, sysfs current output, and detach with pending work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/ams/ams-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/ams/ams-i2c.c -->
# sources/distributed-fs/ceph-client/drivers/macintosh/ams/ams-i2c.c

Purpose: This file implements the I2C backend for Apple Motion Sensor devices, using SMBus byte access to reset/start the accelerometer, read axes, configure thresholds, and enable/clear interrupts.

Important APIs and state: `ams_i2c_driver` matches `"MAC,accelerometer_1"`. Backend callbacks are `ams_i2c_get_xyz()`, `ams_i2c_get_vendor()`, `ams_i2c_clear_irq()`, and exit `ams_i2c_exit()`. Helper functions read/write registers and issue commands through `ams_i2c_cmd()`.

Control flow: `ams_i2c_init()` fills `ams_info` with OF node, callbacks, bus type `BUS_I2C`, and registers the I2C driver. Probe rejects a second device, stores the client, resets and starts the chip, reads and validates device and firmware versions, disables interrupts, calls `ams_sensor_attach()`, writes default sensitivity/control registers, clears pending interrupts, marks device present, enables interrupts, and logs success. Remove detaches, disables and clears interrupts, and clears presence state.

State and persistence: The I2C client pointer and presence flag live in `ams_info`. Hardware register defaults are programmed on probe and are not persisted by the driver. Axis reads are synchronous SMBus operations under the core mutex.

Dependencies and integration: It depends on I2C/SMBus, delays/timeouts, the AMS core's singleton state and function-pointer contract, and OF discovery from core.

Risks and test signals: `ams_i2c_cmd()` treats command register zero or bit 7 as success; timeouts return `-1` rather than a standard errno. SMBus read errors are truncated into `u8` in several paths. Test reset/start failures, version mismatch, interrupt enable/disable register bits, remove after partial attach failure, and axis read error behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/ams/ams-i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/ams/ams-input.c -->
# sources/distributed-fs/ceph-client/drivers/macintosh/ams/ams-input.c

Purpose: This file exposes the Apple Motion Sensor as an optional polled input device that behaves like a three-axis joystick.

Important APIs and state: Module parameters `joystick` and `invert` control default enablement and X/Y inversion. `ams_input_enable()` allocates and registers a polled input device. `ams_idev_poll()` reads calibrated sensor values and reports ABS_X/Y/Z. A sysfs `joystick` attribute enables or disables the input device at runtime. `ams_input_mutex` serializes enable/disable.

Control flow: On enable, the code reads current sensor values under `ams_info.lock` and stores them as calibration offsets, allocates an input device with parent `ams_info.of_dev`, sets abs ranges and polling interval 25 ms, registers it, stores it in `ams_info.idev`, and sets global `joystick=true`. Polling reads current oriented axes, subtracts calibration, optionally inverts X/Y, reports ABS axes, and syncs. Exit removes the sysfs file and disables the input device under the mutex.

State and persistence: Input enablement and inversion are module-parameter/global state. Calibration offsets persist while the input device is active and are recalculated on each enable. There is no persistent calibration storage.

Dependencies and integration: It depends on AMS core callbacks/lock, Linux input polling APIs, sysfs device attributes, and module parameters.

Risks and test signals: `ams_input_init()` calls `ams_input_enable()` when `joystick` is set but ignores its return before creating sysfs; failure handling could leave the parameter true/false mismatch. Test enable/disable races, poll output after calibration, invert parameter changes, input registration failure injection, and sysfs removal during polling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/ams/ams-input.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/ams/ams-pmu.c -->
# sources/distributed-fs/ceph-client/drivers/macintosh/ams/ams-pmu.c

Purpose: This file implements the PMU backend for Apple Motion Sensor hardware found on late 2005 PowerBooks. It accesses sensor registers through PMU ADB requests.

Important APIs and state: `ams_pmu_cmd` stores the PMU command byte derived from the OF `reg` property. Backend callbacks are `ams_pmu_get_xyz()`, `ams_pmu_get_vendor()`, `ams_pmu_clear_irq()`, and exit `ams_pmu_exit()`. Register accessors `ams_pmu_set_register()` and `ams_pmu_get_register()` submit PMU requests and wait on completions.

Control flow: `ams_pmu_init()` fills the core callback contract, reads the command byte, disables and clears all interrupts, attaches the core sensor, programs default freefall/shock thresholds and debounce/control values, clears interrupts, marks device present, enables interrupts, and logs success. Exit detaches core resources, disables and clears interrupts, clears presence state, and logs unloading.

State and persistence: The PMU command byte and `ams_info` singleton state persist while loaded. Hardware thresholds are programmed at init and not persisted by the driver. Register access uses static `adb_request` objects in the get/set helpers, which assumes serialized task-context access through the core mutex.

Dependencies and integration: It depends on PMU request APIs, ADB request completions, Open Firmware properties, and AMS core callbacks.

Risks and test signals: The static request objects in register accessors are safe only if callers keep serialization; concurrent direct calls would corrupt state. PMU request failure returns silently with zero/default values. Test missing `reg` property, PMU request failure, interrupt enable/clear bits, attach failure cleanup, and exit with pending interrupt work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/ams/ams-pmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/ams/ams.h -->
# sources/distributed-fs/ceph-client/drivers/macintosh/ams/ams.h

Purpose: This header defines the shared Apple Motion Sensor data model and backend interface used by the core, PMU backend, I2C backend, and input emulation code.

Important APIs and types: `enum ams_irq` defines freefall, shock, global, and all interrupt masks. `struct ams` contains locks, OF/platform device pointers, presence/vendor/orientation fields, interrupt work state, backend callbacks, optional I2C client, input device pointer, bus type, and calibration offsets. It declares the singleton `ams_info` and functions for sensor reading, attach/detach, backend init, and input init/exit.

Control flow and state: The header has no executable control flow but establishes the locking contract: backend function pointers are called with the main mutex held. `irq_lock` protects `worker_irqs`, while `lock` protects sensor and backend operations.

Dependencies and integration: It includes I2C, input, kthread, mutex, platform device, spinlock, and types headers. Conditional I2C fields depend on `CONFIG_SENSORS_AMS_I2C`.

Risks and test signals: Because `ams_info` is a global singleton, the design assumes one sensor per machine. Changes to backend callbacks must preserve the lock-held contract. Compile-test PMU-only and I2C-only configurations to verify conditional fields and prototypes remain valid.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/ams/ams.h -->
