# subset-b-004009 Research

Grouped research for LED framework and LED driver source files. Each section preserves its original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/flash/leds-sy7802.c -->
# sources/distributed-fs/ceph-client/drivers/leds/flash/leds-sy7802.c

## Purpose
Implements the Silergy SY7802 dual-channel flash LED controller as an I2C/regmap LED flash-class driver. It exposes each described LED output, including a joint two-channel mode, as `struct led_classdev_flash` with torch brightness, flash brightness, strobe, timeout, and fault reporting.

## Important APIs, Types, And Functions
`struct sy7802` stores the regmap, enable GPIO, VIN regulator, shared mutex, active channel bitmaps, and flexible array of `struct sy7802_led`. Each `struct sy7802_led` embeds `struct led_classdev_flash`, a backpointer, and `led_id`.

The LED-class callbacks are `sy7802_torch_brightness_set`, `sy7802_flash_brightness_set`, `sy7802_strobe_set`, `sy7802_strobe_get`, `sy7802_timeout_set`, and `sy7802_fault_get`, collected in `sy7802_flash_ops`. Probe support is split across `sy7802_init_flash_properties`, `sy7802_led_register`, `sy7802_probe_dt`, `sy7802_chip_check`, and power helpers.

## Control Flow
`sy7802_probe` validates there are one or two child LED nodes, allocates a sized `struct sy7802`, obtains `enable` GPIO and `vin` regulator, enables the regulator, initializes mutex and regmap, parses/registers child LEDs, enables the chip GPIO, and verifies `SY7802_REG_DEV_ID`. Child parsing reads `led-sources`, rejects duplicated physical channels, converts two sources into `SY7802_LED_JOINT`, initializes flash settings, and registers through `devm_led_classdev_flash_register_ext`.

Torch writes first reject active strobe use, compute a temporary torch-use bitmap, disable torch mode to apply current, program channel or joint current bits, then update enable/mode bits. Strobe does the symmetric operation while rejecting active torch use. Fault reads map SY7802 status bits into generic `LED_FAULT_*` values.

## State And Persistence
The persistent software state is `fled_strobe_used`, `fled_torch_used`, and `leds_active` under `chip->mutex`; hardware state lives in cached regmap registers and the enable GPIO/regulator. Fault reads are destructive because reading `SY7802_REG_FLAGS` clears status. Devm cleanup disables the chip GPIO and regulator.

## Dependencies And Integration Points
Depends on I2C, regmap with MAPLE cache, GPIO consumer, regulator consumer, OF child nodes, and `led-class-flash`. Device tree compatible is `silergy,sy7802`; child nodes provide naming metadata and `led-sources`.

## Risks
Torch and strobe exclusion relies on shared bitmaps, so missed locking would cause invalid mixed modes. Joint output mode writes both channels and can conflict with duplicate `led-sources` if validation regresses. The probe sequence registers LEDs before enabling and checking the chip ID; failures are devm-cleaned, but a bad bus/device can still exercise registration paths before final ID rejection. Fault reads clear hardware state, so polling `flash_fault` consumes evidence.

## Test Signals
Build with the flash LED class and I2C/regmap enabled. Runtime signals include successful probe on `silergy,sy7802`, correct sysfs files for flash brightness/strobe/timeout/fault, rejection of torch while flash is active and vice versa, correct joint channel behavior, cleanup disabling VIN/GPIO, and expected fault-bit translation after induced timeout or undervoltage events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/flash/leds-sy7802.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/flash/leds-tps6131x.c -->
# sources/distributed-fs/ceph-client/drivers/leds/flash/leds-tps6131x.c

## Purpose
Implements the Texas Instruments TPS61310/TPS61311 I2C flash LED controller. The driver exposes one flash-class LED composed from one to three hardware channels and also registers a V4L2 flash device for camera integration, including external strobe control.

## Important APIs, Types, And Functions
`struct tps6131x` owns device state: regmap, optional reset GPIO, register lock, torch watchdog delayed work, channel enable booleans, parsed current/timeout limits, LED fwnode, `struct led_classdev_flash`, and `struct v4l2_flash`.

Key operations are `tps6131x_brightness_set` for torch current, `tps6131x_strobe_set`, `tps6131x_flash_brightness_set`, `tps6131x_flash_timeout_set`, `tps6131x_strobe_get`, and `tps6131x_flash_fault_get`. `tps6131x_timer_configs` maps supported flash timeouts, while `tps6131x_parse_node` validates `led-sources`, current limits, and timeout properties.

## Control Flow
Probe allocates state, initializes a mutex and torch-refresh delayed work, parses the single child LED node, initializes regmap, obtains optional reset GPIO, resets the chip, writes channel/thermal/current-limit configuration, registers the LED flash class device, and initializes V4L2 flash support.

Torch brightness converts the LED framework brightness units into hardware 25 mA steps, distributes current across enabled channels with special handling for channels 1 and 3 sharing a register, writes register 0, enters torch or shutdown mode, and schedules a refresh before the approximate 13 second watchdog expires. Flash brightness similarly distributes current between channel 2 and channels 1/3, writing registers 1 and 2. Timeout selection chooses the nearest supported table entry and writes STIM/range bits.

## State And Persistence
Mutable state includes parsed current steps, channel booleans, `fled_cdev` setting values, and delayed torch refresh work. Register access to interdependent registers 0-3 is serialized by `lock`. Regmap marks registers 3, 4, and 6 precious because they contain read-to-clear/status fields, and status reads bypass cache. Remove releases V4L2 flash and cancels delayed work.

## Dependencies And Integration Points
Depends on I2C, GPIO, regmap, LED flash class, fwnode properties, and `media/v4l2-flash-led-class.h`. Device tree uses compatible `ti,tps61310`; the child node supplies `led-sources`, `led-max-microamp`, `flash-max-microamp`, and `flash-max-timeout-us`.

## Risks
Current distribution is subtle because channel 1 and 3 share controls while channel 2 has higher flash capacity. Bad DT current limits are rejected, but an incorrect board description can still underuse hardware. The torch watchdog depends on delayed work; failure to cancel/refresh can leave the controller shutting down unexpectedly. Fault/status reads bypass cache because normal regmap reads would be unsafe for precious registers.

## Test Signals
Test with LED flash sysfs and V4L2 controls. Probe should reset and initialize without regmap errors, V4L2 flash registration should succeed, torch should remain on past 13 seconds due to refresh work, flash timeouts should snap to supported values, and fault bits should map to timeout, over-temperature, short-circuit, undervoltage, and LED over-temperature. Removal should cancel work without late I2C accesses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/flash/leds-tps6131x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/led-class-flash.c -->
# sources/distributed-fs/ceph-client/drivers/leds/led-class-flash.c

## Purpose
Provides the LED flash-class interface layered on top of `struct led_classdev`. It adds sysfs controls for flash strobe, flash brightness, flash timeout, and fault reporting, and exports registration and setting helpers for flash-capable LED drivers.

## Important APIs, Types, And Functions
The central public APIs are `led_classdev_flash_register_ext`, `led_classdev_flash_unregister`, `devm_led_classdev_flash_register_ext`, `devm_led_classdev_flash_unregister`, `led_set_flash_timeout`, `led_set_flash_brightness`, `led_update_flash_brightness`, `led_set_flash_duration`, and `led_get_flash_fault`.

`struct led_flash_ops` supplied by drivers provides `strobe_set`, optional `strobe_get`, `flash_brightness_set`, `flash_brightness_get`, `timeout_set`, `duration_set`, and `fault_get`. `struct led_flash_setting` values are clamped/aligned by `led_clamp_align`.

## Control Flow
Registration validates flash-capable devices: if `LED_DEV_CAP_FLASH` is set, the underlying classdev must have `brightness_set_blocking`, flash ops must exist, and `strobe_set` is required. It then attaches a flash resume callback, selects sysfs attribute groups based on available ops, and calls `led_classdev_register_ext`.

Sysfs stores acquire `led_access`, reject disabled sysfs, parse numeric input, and route to the exported setting helpers. Setting helpers update the cached `led_flash_setting`, clamp and align it to min/max/step, then call the driver operation unless the LED class device is suspended. Fault display calls `fault_get` and formats generic LED fault names.

## State And Persistence
Persistent state is held in the caller-owned `struct led_classdev_flash`: cached brightness, timeout, and duration settings plus operation pointers. The class does not store hardware state itself. On LED resume, `led_flash_resume` reapplies cached flash brightness and timeout to the hardware.

## Dependencies And Integration Points
Depends on the LED core class, device attributes, devres, and `linux/led-class-flash.h`. It integrates with flash LED drivers and with userspace through the LED sysfs ABI. Camera-facing integration is indirect through drivers that also register V4L2 flash objects.

## Risks
The operation macros assume `fled_cdev->ops` is valid when optional sysfs groups are created. Fault formatting depends on `LED_NUM_FLASH_FAULTS` matching the `led_flash_fault_names` table. `sprintf` use is older style and bounded only by the small fixed fault-name set. Suspended devices silently cache values without programming hardware, so resume reapplication is essential.

## Test Signals
Test by registering fake or real flash LEDs with different operation sets and confirming only supported sysfs attributes appear. Store paths should clamp/align values and reject invalid strobe values. Suspend/resume should restore cached flash brightness and timeout. Fault injection should display the expected generic names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/led-class-flash.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/led-class-multicolor.c -->
# sources/distributed-fs/ceph-client/drivers/leds/led-class-multicolor.c

## Purpose
Implements the multicolor LED class wrapper. It exposes per-subLED color indexes and intensity weights through sysfs, calculates channel brightness components from aggregate brightness, and registers `struct led_classdev_mc` as a normal LED class device with multicolor metadata.

## Important APIs, Types, And Functions
The exported APIs are `led_mc_calc_color_components`, `led_classdev_multicolor_register_ext`, `led_classdev_multicolor_unregister`, `devm_led_classdev_multicolor_register_ext`, and `devm_led_classdev_multicolor_unregister`.

`multi_intensity` accepts one unsigned value per subLED and updates `mcled_cdev->subled_info[i].intensity`. `multi_index` prints color names from `led_get_color_name` for each subLED color index.

## Control Flow
Registration validates the multicolor classdev pointer, requires `num_colors > 0`, rejects more than `LED_COLOR_ID_MAX`, sets `LED_MULTI_COLOR`, attaches the multicolor sysfs groups, and calls `led_classdev_register_ext`.

Brightness calculation multiplies the aggregate brightness by each subLED intensity and divides by max brightness with rounding. Updating `multi_intensity` parses exactly `num_colors` integers, stores them under `led_access`, and if software blinking is not active, reapplies the current brightness so the driver callback sees refreshed subLED component brightness.

## State And Persistence
State lives in the driver-owned `struct led_classdev_mc` and its `subled_info` array. This file mutates only intensity and calculated brightness fields. Devres wrappers keep unregister tied to parent-device lifetime.

## Dependencies And Integration Points
Depends on `linux/led-class-multicolor.h`, the base LED class, device attributes, and `led_get_color_name` from the LED core. Drivers such as BlinkM use this class to expose one RGB LED instead of separate red/green/blue class devices.

## Risks
`multi_intensity_store` does not explicitly clamp intensity values to max brightness; component calculation can therefore produce values larger than expected if userspace writes large intensities and a driver does not constrain them. `multi_index_show` assumes valid color indexes; invalid driver data can yield null names. The parser is strict about extra trailing data.

## Test Signals
Register a multicolor LED and confirm `multi_index`, `multi_intensity`, and normal brightness behavior. Tests should update intensity with valid and invalid cardinality, check recalculated subLED brightness, and verify triggers using `led_mc_set_brightness` honor color count checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/led-class-multicolor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/led-class.c -->
# sources/distributed-fs/ceph-client/drivers/leds/led-class.c

## Purpose
Implements the LED class device layer: `/sys/class/leds` devices, brightness and max-brightness sysfs files, trigger sysfs exposure, LED naming, provider lookup, suspend/resume hooks, and devres-managed registration.

## Important APIs, Types, And Functions
Public APIs include `led_classdev_register_ext`, `led_classdev_unregister`, `devm_led_classdev_register_ext`, `devm_led_classdev_unregister`, `led_get`, `devm_led_get`, `devm_of_led_get`, `devm_of_led_get_optional`, `led_put`, `led_add_lookup`, `led_remove_lookup`, `led_classdev_suspend`, `led_classdev_resume`, and `led_classdev_notify_brightness_hw_changed`.

The class object `leds_class` owns default groups for brightness, max brightness, and optional trigger binary attribute. `leds_lookup_list` supports non-DT lookup tables. `leds_wq` is the ordered workqueue used by the LED core.

## Control Flow
Subsystem init creates the ordered workqueue and registers the `leds` class. Registration composes a name from fwnode properties or legacy fields, resolves collisions by suffixing unless `LED_REJECT_NAME_CONFLICT` is set, creates the device with groups, attaches fwnode, optionally creates `brightness_hw_changed`, initializes work flags and trigger lock, sets default `max_brightness`, updates brightness from hardware, initializes core timer/work, adds the classdev to the global LED list, and applies the default trigger.

Unregister removes triggers, marks unregistering, stops software blinking, turns the LED off unless retain-at-shutdown is set, flushes work, removes optional attributes, unregisters the device, removes from the global list, and destroys `led_access`.

## State And Persistence
Per-LED state is in `struct led_classdev`: device pointer, brightness, max brightness, flags, work flags, trigger state, fwnode-derived metadata, and locks. Global persistent state includes the class, lookup list, LED list shared with trigger code, and ordered workqueue.

## Dependencies And Integration Points
Depends on the device model, sysfs, fwnode/OF, module references, triggers, the LED core, and `uapi/linux/uleds.h`. It integrates with all LED drivers through registration and with consumers through `led_get`/`devm_led_get` using DT phandles or lookup tables.

## Risks
Name composition and collision handling affect ABI-visible sysfs paths. Registration happens under `led_access`, so drivers that call back into LED APIs during probe need to avoid deadlocks. Provider lookup takes parent-driver module references; unusual parent/device ownership can make `led_get` fail. Unregistering while triggers or delayed brightness work are active depends on careful flush and trigger removal ordering.

## Test Signals
KUnit coverage in `led-test.c` exercises registration, brightness initialization, name collision suffixing, conflict rejection, lookup, and `devm_led_get`. Runtime signals include correct sysfs creation, default trigger application, suspend/resume off/restore behavior, and clean unregister with no pending work or trigger references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/led-class.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/led-core.c -->
# sources/distributed-fs/ceph-client/drivers/leds/led-core.c

## Purpose
Provides shared LED runtime mechanics: brightness dispatch, asynchronous fallback for sleeping callbacks, software blinking timers, multicolor trigger brightness, fwnode property parsing, LED name composition, default pattern reading, sysfs disable flags, and color/default-state helpers.

## Important APIs, Types, And Functions
Exports include `led_init_core`, `led_blink_set`, `led_blink_set_oneshot`, `led_blink_set_nosleep`, `led_stop_software_blink`, `led_set_brightness`, `led_set_brightness_nopm`, `led_set_brightness_nosleep`, `led_set_brightness_sync`, `led_mc_set_brightness`, `led_update_brightness`, `led_get_default_pattern`, `led_sysfs_disable`, `led_sysfs_enable`, `led_compose_name`, `led_get_color_name`, and `led_init_default_state_get`.

Global `leds_list` and `leds_list_lock` are exported for trigger registration and default-trigger matching.

## Control Flow
`led_init_core` initializes each classdev work item and blink timer. Brightness updates prefer non-sleeping `brightness_set`; if unavailable they queue work for `brightness_set_blocking`. Software blink toggles brightness from a timer and respects oneshot, inverted oneshot, and brightness-change flags. `led_blink_set` tries hardware `blink_set` first and falls back to software blinking, defaulting unspecified delays to 500 ms.

Name composition parses `label`, `color`, `function`, `function-enumerator`, fallback labels, OF node names, or software node names. Default state parsing maps fwnode `default-state` values to off/on/keep.

## State And Persistence
Per-classdev persistent state includes `brightness`, `blink_brightness`, blink delays, delayed brightness/work values, and atomic work flags. Timer and workqueue state mediate asynchronous changes. Fwnode-derived names, patterns, and default state are read from firmware descriptions but not stored globally beyond classdev fields.

## Dependencies And Integration Points
Depends on timers, workqueues, mutexes/rwsems, fwnode/OF/property APIs, multicolor support, and the base LED headers. It is used by all LED class drivers and trigger code.

## Risks
The ordering of `LED_SET_BRIGHTNESS_OFF`, `LED_SET_BRIGHTNESS`, and `LED_SET_BLINK` is important to avoid off/on reordering when triggers issue rapid changes. Software blink timer callbacks can run in atomic context, so paths must use nosleep dispatch. `led_set_brightness_sync` rejects active blinking, which callers must handle. Name parsing preserves legacy `label` behavior, so changes can break user ABI.

## Test Signals
Exercise immediate and blocking brightness callbacks, rapid off/on trigger sequences, software and hardware blink fallback, oneshot blink behavior, suspend flag behavior, multicolor trigger updates, name composition from firmware properties, and default-pattern/default-state parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/led-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/led-test.c -->
# sources/distributed-fs/ceph-client/drivers/leds/led-test.c

## Purpose
Provides KUnit tests for selected LED framework behavior. The tests validate core LED class registration semantics, brightness initialization from a `brightness_get` callback, name collision handling, conflict rejection, lookup registration, and devm lookup.

## Important APIs, Types, And Functions
`struct led_test_ddata` holds a test classdev and KUnit device. `led_test_brightness_get` returns a fixed post-registration brightness. Test cases are `led_test_class_register` and `led_test_class_add_lookup_and_get`; setup/teardown are `led_test_init` and `led_test_exit`.

## Control Flow
The KUnit init allocates test data and registers a synthetic device named `led_test`. `led_test_class_register` registers `led-test`, verifies default `LED_FULL` max brightness, verifies brightness was updated to `LED_TEST_POST_REG_BRIGHTNESS`, registers a copied classdev with the same name to confirm suffixing to `led-test_1`, then enables `LED_REJECT_NAME_CONFLICT` and confirms another registration fails with `-EEXIST`.

`led_test_class_add_lookup_and_get` registers an LED, adds a `struct led_lookup_data` mapping the test device and connection ID to the provider name, resolves it with `devm_led_get`, verifies the returned provider, and removes the lookup entry.

## State And Persistence
State is KUnit-scoped and devres-managed. The lookup entry is stack-local but explicitly removed before the test exits. The class devices are released through devm cleanup tied to the synthetic KUnit device.

## Dependencies And Integration Points
Depends on KUnit device helpers and the LED class APIs. It directly tests functionality in `led-class.c` and indirectly exercises `led_update_brightness`.

## Risks
Coverage is focused and does not test triggers, blink work/timers, suspend/resume, fwnode naming, or flash/multicolor subclasses. The lookup test depends on provider names remaining stable during registration.

## Test Signals
Run the KUnit suite named `led`. Passing assertions confirm registration success, default max brightness, brightness-get initialization, name collision suffixing, conflict rejection, lookup insertion/removal, and `devm_led_get` resolution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/led-test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/led-triggers.c -->
# sources/distributed-fs/ceph-client/drivers/leds/led-triggers.c

## Purpose
Implements the LED trigger core. It manages trigger registration, sysfs trigger selection, default-trigger matching, trigger activation/deactivation, per-trigger LED lists, trigger-driven brightness events, multicolor events, blink events, and devres/simple trigger helpers.

## Important APIs, Types, And Functions
Exports include `led_trigger_read`, `led_trigger_write`, `led_trigger_set`, `led_trigger_remove`, `led_trigger_set_default`, `led_trigger_register`, `led_trigger_unregister`, `devm_led_trigger_register`, `led_trigger_event`, `led_mc_trigger_event`, `led_trigger_blink`, `led_trigger_blink_oneshot`, `led_trigger_register_simple`, and `led_trigger_unregister_simple`.

Global state is `trigger_list` protected by `triggers_list_lock`; each trigger owns an RCU-protected LED list protected by `leddev_list_lock`.

## Control Flow
Sysfs writes under `led_access` accept `none`, `default`, or a registered trigger name relevant to the LED trigger type. Setting a trigger removes the old trigger, deletes RCU list membership, synchronizes RCU, cancels brightness work, stops software blinking, removes trigger sysfs groups, calls deactivate, clears trigger fields, and turns the LED off. For a new trigger, it adds list membership, synchronizes so activate can emit events, flushes pending brightness work, calls activate or sets default trigger brightness, adds trigger groups, and emits a uevent.

Trigger registration rejects duplicate compatible names, adds the trigger globally, and applies it to LEDs with matching unresolved default triggers. Unregistration removes the trigger globally and detaches it from every LED.

## State And Persistence
State persists in registered `struct led_trigger` objects, their LED lists, `led_cdev->trigger`, `trigger_data`, `activated`, and default-trigger flags. RCU is used for event dispatch while rwsems serialize structural changes.

## Dependencies And Integration Points
Depends on LED class global lists, sysfs binary attributes, device groups, RCU, module autoloading, and kobject uevents. It integrates with trigger providers and all LED class devices that enable `CONFIG_LEDS_TRIGGERS`.

## Risks
Lock ordering is explicit: global trigger list lock nests outside each LED trigger lock. Activation failures require careful unwind to remove list membership and turn the LED off. The trigger sysfs read path uses a dynamically sized binary attribute because CPU triggers can be numerous. Event dispatch walks RCU lists and must not rely on sleeping operations outside LED helpers.

## Test Signals
Runtime tests should register/unregister triggers, select them via sysfs, verify `none` and `default`, observe uevents, confirm default trigger autoloading, exercise trigger attributes, and dispatch brightness/blink/multicolor events while concurrently unregistering LEDs and triggers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/led-triggers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-88pm860x.c -->
# sources/distributed-fs/ceph-client/drivers/leds/leds-88pm860x.c

## Purpose
Implements LED support for Marvell 88PM860x MFD PMIC RGB outputs. Each platform child device represents one color channel and registers a basic LED class device that programs PMIC PWM/current/blink control registers.

## Important APIs, Types, And Functions
`struct pm860x_led` contains the LED classdev, PMIC I2C client, parent chip, per-LED mutex, name, port, current setting, cached brightness, control/blink registers, and blink enable mask. Main callbacks are `pm860x_led_set`, `led_power_set`, `pm860x_led_dt_init`, `pm860x_led_probe`, and `pm860x_led_remove`.

## Control Flow
Probe obtains `control` and `blink` register resources, maps platform ID 0-5 to names `led0-red/green/blue` or `led1-red/green/blue`, selects the proper PMIC I2C client, reads optional DT current setting from the parent `leds` node or platform data, initializes the classdev, registers it, and turns it off.

Brightness writes compress LED brightness to a five-bit PWM value. Transitioning from off to on enables the oscillator group, programs current if configured, sets continuous-on blink timing, and enables the group blink bit. Transitioning to zero writes the PWM and then bulk-reads sibling control registers; if all three channel PWM values are zero it clears current and blink enable and disables the oscillator.

## State And Persistence
Per-LED cached `brightness` and `current_brightness` are protected by `lock`. Hardware state persists in PM860x PMIC registers and oscillator enables shared by RGB groups.

## Dependencies And Integration Points
Depends on the 88PM860x MFD API, platform resources, I2C register helpers, optional OF child lookup, and the LED class. Platform alias is `88pm860x-led`.

## Risks
Group power control is shared across three color channels and relies on bulk-reading adjacent registers to decide when all are off. Platform IDs must match MFD resource layout. Error returns from several PMIC writes are not all propagated in detail, so partial hardware programming can be hard to diagnose.

## Test Signals
Test each of six platform IDs, verify names and current settings, toggle individual colors, ensure oscillator remains enabled while any sibling color is active and disables when all are off, and validate remove unregisters the classdev cleanly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-88pm860x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-acer-a500.c -->
# sources/distributed-fs/ceph-client/drivers/leds/leds-acer-a500.c

## Purpose
Implements two one-bit power-button LEDs for the Acer Iconia Tab A500 embedded controller. The hardware exposes commands to enable the white or orange LED and a shared reset command that turns both off.

## Important APIs, Types, And Functions
`struct a500_led` stores an LED classdev, an enable register sequence, a pointer to the other LED, and the parent EC regmap. `a500_ec_led_brightness_set` is the class callback, and `a500_ec_leds_probe` registers `power:white` and `power:orange`.

## Control Flow
Probe obtains regmap `KB930` from the parent, writes the reset/off sequence, allocates two LED objects, fills names, max brightness, suspend/resume flag, enable sequences, mutual `other` pointers, and registers both through devm LED registration.

Setting brightness on writes the LED-specific enable sequence. Setting brightness off writes the shared reset command; if the other LED's cached brightness is nonzero, it appends the other LED's enable command so that the reset does not unintentionally turn it off.

## State And Persistence
There is no explicit lock or private cache beyond each LED classdev's `brightness` field. Hardware state is stored in the EC and updated through regmap multi-register writes with 100 ms command delays.

## Dependencies And Integration Points
Depends on a parent embedded-controller regmap named `KB930`, platform-device probing, and the LED class. Platform alias is `acer-a500-iconia-leds`.

## Risks
The shared reset/restore behavior depends on the LED core brightness cache for the other LED. Concurrent sysfs writes could interleave because there is no driver-level mutex. Hardware only supports on/off, so max brightness is one and triggers requiring arbitrary brightness will collapse to binary behavior.

## Test Signals
Probe should reset both LEDs and create `power:white` and `power:orange`. Turning either LED off while the other is on should restore the other. Suspend/resume should preserve LED class behavior through `LED_CORE_SUSPENDRESUME`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-acer-a500.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-adp5520.c -->
# sources/distributed-fs/ceph-client/drivers/leds/leds-adp5520.c

## Purpose
Provides LED support for Analog Devices ADP5520/ADP5501 MFD PMICs using platform data. It registers up to three LED class devices and programs current, enable, timing, and fade registers through the parent MFD API.

## Important APIs, Types, And Functions
`struct adp5520_led` embeds a classdev and stores the parent device, LED ID, and flags. Important functions are `adp5520_led_set`, `adp5520_led_setup`, `adp5520_led_prepare`, `adp5520_led_probe`, and `adp5520_led_remove`.

## Control Flow
Probe requires `adp5520_leds_platform_data`, validates LED count, allocates an array of private LEDs, clears LED currents, initializes timing/fade registers, then loops through `struct led_info` entries. Each LED inherits name/default trigger, sets a blocking brightness callback, derives flags/ID, registers the classdev, and enables the corresponding LED output/control bits.

Brightness writes the appropriate current register with `value >> 2`, converting LED-class brightness to the PMIC's coarser current scale. Remove clears all LED enable bits and unregisters classdevs.

## State And Persistence
State is mostly platform-data-derived and static after probe. Hardware state persists in PMIC LED current/time/fade/control registers. No lock is used in the LED callback, relying on parent MFD serialization or simple register writes.

## Dependencies And Integration Points
Depends on the ADP5520 MFD API, platform data, LED class, and platform driver binding `adp5520-led`. It does not parse device tree in this file.

## Risks
The driver ORs multiple setup writes into one `ret`, which can obscure the first failing operation. Platform data must provide valid LED counts, flags, names, and timing fields. Brightness resolution is reduced by shifting right two bits.

## Test Signals
Test platform-data registration for one to three LEDs, verify enable bits per ID, confirm current writes scale brightness correctly, validate fade/on/off timing programming, and ensure remove disables all LED outputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-adp5520.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-an30259a.c -->
# sources/distributed-fs/ceph-client/drivers/leds/leds-an30259a.c

## Purpose
Implements the Panasonic AN30259A three-channel I2C LED driver. It supports brightness, hardware blink/slope mode, and firmware-described default state for up to three channels.

## Important APIs, Types, And Functions
`struct an30259a_led` stores chip pointer, fwnode, classdev, channel number, default state, and `sloping`. `struct an30259a` stores mutex, client, LED array, regmap, and LED count. Key functions are `an30259a_brightness_set`, `an30259a_blink_set`, `an30259a_dt_init`, `an30259a_init_default_state`, and `an30259a_probe`.

## Control Flow
Probe parses child nodes with `reg` values 1-3, records default state, initializes mutex/client/regmap, applies default state for each LED, assigns blocking brightness and blink callbacks, and registers through `devm_led_classdev_register_ext`.

Brightness reads `LED_ON`, clears enable/slope for off, or enables the channel and optional slope bit for on, programs full duty max/mid, writes `LED_ON`, then writes the current register. Blink validates delays are multiples of 500 ms and at most 7500 ms, defaults unspecified blink to 500/500, writes slope/duty/detention registers, enables slope and channel bits, and caches `sloping`.

## State And Persistence
The driver maintains `sloping` per LED and brightness in the classdev. Hardware state persists in LED_ON, LEDCC, SLOPE, and LEDCNT registers. `default-state = keep` reads current hardware enable/current before reprogramming.

## Dependencies And Integration Points
Depends on I2C, regmap, OF child nodes, LED class, and `led_init_default_state_get`. Compatible string is `panasonic,an30259a`.

## Risks
Blink callback parameter names are `delay_off, delay_on`, opposite the usual LED API naming convention, so maintainers must verify call-site expectations carefully. Default-state initialization calls the brightness callback before classdev registration, which relies on initialized chip/regmap and no `cdev.dev` use in the callback. Invalid child nodes reduce the count and can reject all LEDs.

## Test Signals
Validate DT parsing for channels 1-3, default-state off/on/keep behavior, brightness on/off with slope clearing, blink validation for unsupported delays, hardware register writes for 500 ms increments, and devm cleanup on probe failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-an30259a.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-apu.c -->
# sources/distributed-fs/ceph-client/drivers/leds/leds-apu.c

## Purpose
Implements front-panel LEDs for PC Engines APU1 boards by directly writing AMD FCH GPIO MMIO bytes discovered by fixed addresses after DMI matching.

## Important APIs, Types, And Functions
`struct apu_led_profile` defines LED name, initial brightness, and MMIO offset. `struct apu_led_priv` embeds a classdev and mapped address. Global `apu_led` stores the platform device, LED array, and spinlock. Main functions are `apu1_led_brightness_set`, `apu_led_config`, `apu_led_probe`, `apu_led_init`, and `apu_led_exit`.

## Control Flow
Module init first checks strict DMI matches for PC Engines APU/APU1. If matched, it registers a simple platform device and probes the driver. Probe allocates global state, initializes the spinlock, maps three one-byte GPIO addresses, registers LED classdevs named `apu:green:1..3`, and writes initial brightness. Exit unregisters all LED classdevs and platform objects.

Brightness writes `APU1_LEDON` or `APU1_LEDOFF` to the mapped GPIO byte under a spinlock.

## State And Persistence
Global `apu_led` persists for module lifetime. Hardware state is direct MMIO GPIO output. LED brightness is restored by `LED_CORE_SUSPENDRESUME` via classdev flags and by initial writes at probe.

## Dependencies And Integration Points
Depends on DMI, platform devices, MMIO mapping, spinlocks, and LED class. It integrates only with APU1 boards; the code explicitly points APU2/3 users to another configuration.

## Risks
Fixed physical MMIO offsets are board-specific and would be unsafe without DMI gating. Global state makes the driver single-instance. Direct MMIO writes assume byte access semantics and no competing GPIO driver. Exit assumes probe completed enough to populate the LED array.

## Test Signals
On matching APU1 hardware, verify three LEDs register with expected initial states and write the correct GPIO values. On nonmatching systems, init should return `-ENODEV`. Suspend/resume should preserve class behavior through LED core support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-apu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-ariel.c -->
# sources/distributed-fs/ceph-client/drivers/leds/leds-ariel.c

## Purpose
Implements Dell Wyse 3020 "Ariel" embedded-controller status LEDs. It exposes blue power, amber status, and green status LEDs backed by simple EC RAM register values.

## Important APIs, Types, And Functions
`struct ariel_led` stores the parent EC regmap, EC index, and LED classdev. Main callbacks are `ariel_led_get`, `ariel_led_set`, `ariel_blink_set`, and `ariel_led_probe`.

## Control Flow
Probe obtains parent regmap `ec_ram`, allocates three LEDs, assigns EC indexes/names/default triggers, sets brightness get/set and blink callbacks, and registers each via devm LED registration.

Brightness get reads the EC register and reports `LED_FULL` only when the value is `EC_LED_STILL`. Brightness set writes `EC_LED_OFF` or `EC_LED_STILL`. Blink rejects unspecified default blink, maps zero-on to off, zero-off to steady, and otherwise forces 500/500 ms while writing `EC_LED_BLINK`.

## State And Persistence
No private mutable state beyond classdev caches; EC RAM registers persist hardware LED modes. Default triggers are set for blue power and green status.

## Dependencies And Integration Points
Depends on a parent platform device with regmap named `ec_ram`, the LED class, and the platform driver named `dell-wyse-ariel-led`.

## Risks
Only one hardware blink frequency is exposed, so arbitrary blink requests are normalized to 500/500. `ariel_led_get` treats blink/fade as off from the brightness perspective. Regmap write errors in set/blink are ignored because callbacks are nonblocking `void` or return success after writes.

## Test Signals
Probe should create three named LEDs, default triggers should apply, brightness reads should match EC still/off state, blink should write EC blink mode and adjust delays to 500 ms, and missing `ec_ram` should return `-ENODEV`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-ariel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-as3668.c -->
# sources/distributed-fs/ceph-client/drivers/leds/leds-as3668.c

## Purpose
Implements the AMS/Osram AS3668 four-channel I2C current LED driver. Each firmware child node maps to one current channel with independent on/off mode bits and current register.

## Important APIs, Types, And Functions
`struct as3668_led` stores a classdev, chip pointer, fwnode, mode bit mask, and current register. `struct as3668` stores the client and four LED slots. Key functions are `as3668_channel_mode_set`, `as3668_brightness_get`, `as3668_brightness_set`, `as3668_dt_init`, `as3668_probe`, and `as3668_remove`.

## Control Flow
Probe reads the chip ID register and rejects nonmatching hardware, allocates state, parses child nodes, then writes all channel modes and currents to off/zero. Child parsing reads `reg`, fills channel-specific mask/register, assigns max brightness 255, get/set callbacks, and registers classdevs with fwnode metadata.

Setting brightness reads the shared mode register, replaces this channel's two-bit mode with on/off, writes the mode register, then writes the channel current register.

## State And Persistence
There is no explicit lock or regmap cache; hardware state is read/written via SMBus byte operations. Per-channel mode/current is stored in AS3668 registers. Remove writes the mode register to zero.

## Dependencies And Integration Points
Depends on I2C SMBus byte access, OF child nodes, LED class, and compatible `ams,as3668`. It uses `uapi/linux/uleds.h` only for LED brightness constants/types.

## Risks
Concurrent brightness writes can race on the shared mode register because there is no mutex around read-modify-write. `as3668_brightness_get` returns an SMBus error as an enum brightness without filtering negative values. Probe initializes hardware after classdev registration, so userspace activity during probe is theoretically possible before final zeroing.

## Test Signals
Verify chip ID rejection, child `reg` validation, four classdev registration, brightness get/set for each current register, shared mode bit preservation under sequential writes, and remove clearing all modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-as3668.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-aw200xx.c -->
# sources/distributed-fs/ceph-client/drivers/leds/leds-aw200xx.c

## Purpose
Implements Awinic AW20036/AW20054/AW20072/AW20108 LED matrix controllers. It registers firmware-described channels as LED class devices, supports fade brightness plus a per-LED `dim` sysfs control, and computes global current limits from display scan duty.

## Important APIs, Types, And Functions
`struct aw200xx_chipdef` describes channel count and matrix geometry. `struct aw200xx` stores chip definition, client, regmap, mutex, display rows, optional HW enable GPIO, and flexible LED array. `struct aw200xx_led` stores classdev, chip, dim override, and channel number.

Key functions are `dim_show/store`, `aw200xx_brightness_set`, current conversion helpers, `aw200xx_set_imax`, `aw200xx_chip_reset/init/check`, `aw200xx_probe_get_display_rows`, `aw200xx_probe_fw`, and `aw200xx_probe`.

## Control Flow
Probe selects chip definition from OF match data, validates child count, initializes paged regmap, enables optional HWEN GPIO, checks chip ID, initializes mutex, resets the chip, parses firmware children, sets global current, and initializes display size/sleep/global all-on registers.

Firmware parsing computes display rows from highest valid channel, derives allowed per-LED current range from duty ratio, validates each child `reg` and optional `led-max-microamp`, registers a classdev with max brightness 255 and `dim` group, and finally programs the minimum requested current or a default.

Brightness writes page-4 DIM and FADE registers. If `dim` is `auto`, DIM is derived from fade brightness; otherwise a fixed DIM value is used while brightness controls FADE.

## State And Persistence
Per-LED persistent state is `dim` (`-1` for auto) and classdev brightness. Chip-level state includes display rows and selected global current. Regmap uses ranges for paged addressing, MAPLE cache, and disabled internal locking; the driver mutex serializes LED operations.

## Dependencies And Integration Points
Depends on I2C, regmap range windows, optional GPIO, firmware child nodes, LED class, and per-chip compatible strings `awinic,aw20036`, `aw20054`, `aw20072`, and `aw20108`.

## Risks
Current calculation depends on display rows inferred from child channel indexes; invalid or sparse firmware can change duty/current limits. Regmap locking is disabled, making the driver mutex important. Page/range definitions must match hardware or writes can hit wrong pages. `dim_store` accepts `auto` or 0-63, but does not update hardware when switching back to auto until brightness changes.

## Test Signals
Verify all compatible variants, channel count bounds, chip ID check, display row inference, `led-max-microamp` validation, `dim` sysfs behavior, brightness-to-DIM/FADE writes, current register programming, reset action, and HWEN disable on cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-aw200xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-aw2013.c -->
# sources/distributed-fs/ceph-client/drivers/leds/leds-aw2013.c

## Purpose
Implements the Awinic AW2013 three-channel I2C LED driver with regulator-managed power, brightness, and hardware blink timing.

## Important APIs, Types, And Functions
`struct aw2013` stores mutex, two regulators, client, LED array, regmap, LED count, and enabled flag. `struct aw2013_led` stores chip pointer, classdev, channel number, and maximum current setting. Important functions are `aw2013_chip_init/enable/disable/in_use`, `aw2013_brightness_set`, `aw2013_blink_set`, `aw2013_probe_dt`, and `aw2013_probe`.

## Control Flow
Probe initializes mutex, regmap, regulators, powers the chip, reads the reset/ID register, installs a devm disable action, parses child nodes, registers LEDs, then disables regulators to save power. Child parsing resets the chip, reads channel `reg`, optional `led-max-microamp`, computes IMAX, assigns blocking brightness and blink callbacks, and registers each classdev.

Brightness enables regulators/chip when any LED should be active, writes PWM, toggles channel enable, disables blink mode when turning off, and powers the chip down when all cached classdev brightness values are zero. Blink defaults unspecified requests to 500/500, ensures LED brightness is nonzero, converts on/off delays to hardware powers-of-two in 130 ms units, writes timing registers, enables mode and channel bits.

## State And Persistence
Software state tracks `enabled`, LED count, per-classdev brightness, and per-channel IMAX. Hardware state is lost when regulators are disabled and reinitialized by `aw2013_chip_enable`. Mutex protects register writes and power transitions.

## Dependencies And Integration Points
Depends on I2C, regmap, two regulators (`vcc`, `vio`), OF child nodes, and LED class. Compatible string is `awinic,aw2013`.

## Risks
`aw2013_brightness_set` checks `aw2013_chip_in_use` before the LED core updates the target `cdev.brightness`, so power-up decisions depend on current cached state and deserve regression tests. Blink delay conversion uses `ilog2((*delay - 1) / 130) + 1`; very small nonzero delays need careful validation. Power cycling means all state must be restored by `aw2013_chip_init` and subsequent writes.

## Test Signals
Probe should validate chip ID, parse up to three LEDs, compute IMAX, power down when idle, and power up on brightness/blink. Test blink default and quantized delay return values, off transitions clearing mode bits, and regulator cleanup on probe failure/remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-aw2013.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-bcm6328.c -->
# sources/distributed-fs/ceph-client/drivers/leds/leds-bcm6328.c

## Purpose
Implements memory-mapped LED control for Broadcom BCM6328 controllers. It supports up to 24 LEDs, active-low polarity, default-state parsing, two hardware blink intervals, serial LED bus configuration, and optional hardware-controlled link/activity LEDs.

## Important APIs, Types, And Functions
`struct bcm6328_led` stores classdev, MMIO base, shared spinlock, pin, shared blink interval bitmaps/delays, and active-low flag. Important functions are endian-aware read/write helpers, `bcm6328_led_mode`, `bcm6328_led_set`, `bcm6328_blink_set`, `bcm6328_hwled`, `bcm6328_led`, and `bcm6328_leds_probe`.

## Control Flow
Probe maps MMIO, allocates a spinlock and two-entry blink caches, disables hardware control, clears link/activity selectors, configures serial LED options from DT properties, then iterates child nodes. A child with `brcm,hardware-controlled` enables hardware control and programs link/activity source selectors; otherwise it allocates a classdev LED, derives default brightness from `default-state`, programs initial mode, sets callbacks, and registers via devm.

Brightness clears the LED from both blink interval caches and writes ON/OFF mode accounting for active-low. Blink normalizes missing delays to 500 ms, requires equal on/off delay and delay <= 63 * 20 ms, then assigns the LED to one of two shared hardware intervals if free or already using the same delay; otherwise it returns `-EINVAL` so the LED core can use software blink.

## State And Persistence
Shared blink interval state is cached in `blink_leds[2]` and `blink_delay[2]` under the spinlock. Hardware state persists in mode, init, hardware disable, and link/activity selector registers.

## Dependencies And Integration Points
Depends on platform MMIO resources, OF child nodes, LED class, spinlocks, and CPU endian handling. Compatible is `brcm,bcm6328-leds`.

## Risks
Only two hardware blink delays can be active; the fallback path must remain correct. Link/activity selectors are valid only for LEDs 0-7 and same source groups; DT errors become warnings. Bit shift mapping for LEDs 0-7 versus 8-23 is non-obvious and easy to break. Shared registers require spinlock coverage.

## Test Signals
Test default-state off/on/keep, active-low behavior, hardware blink with two matching/different delays, fallback to software blink on unsupported delays, hardware-controlled LEDs with link/activity sources, serial LED DT options, and endian-correct register access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-bcm6328.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-bcm6358.c -->
# sources/distributed-fs/ceph-client/drivers/leds/leds-bcm6358.c

## Purpose
Implements memory-mapped serial LED control for Broadcom BCM6358 controllers. It exposes firmware child nodes as basic LED class devices with active-low and default-state support.

## Important APIs, Types, And Functions
`struct bcm6358_led` stores classdev, MMIO base, shared spinlock, pin, and active-low flag. Main functions are endian-aware register read/write helpers, `bcm6358_led_busy`, `bcm6358_led_set`, `bcm6358_led`, and `bcm6358_leds_probe`.

## Control Flow
Probe maps MMIO, allocates a spinlock, waits for the serial LED controller to be idle, configures polarity and clock divider from DT, writes the control register, then iterates child nodes. Each valid child `reg` below 32 creates a classdev, reads default state from firmware, applies it to hardware, assigns brightness callback, and registers through devm.

Brightness waits for the busy bit to clear, reads the mode register, sets or clears the pin bit based on brightness and active-low polarity, and writes the mode register under the spinlock.

## State And Persistence
The driver has no cached per-LED hardware state beyond classdev brightness; the controller mode register is the source of truth for `default-state = keep`. Hardware control register settings persist until overwritten.

## Dependencies And Integration Points
Depends on platform MMIO, OF child nodes, LED class, spinlocks, delay loops, and endian handling. Compatible is `brcm,bcm6358-leds`.

## Risks
`bcm6358_led_busy` spins with `udelay` until the busy bit clears and has no timeout, so stuck hardware can hang the caller. No hardware blink support is exposed. Shared mode register read-modify-write depends on spinlock coverage.

## Test Signals
Validate clock divider and polarity DT parsing, registration of valid child pins, rejection/warning of invalid pins, default-state keep/on/off, active-low writes, and behavior when the busy bit clears before writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-bcm6358.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-bd2606mvv.c -->
# sources/distributed-fs/ceph-client/drivers/leds/leds-bd2606mvv.c

## Purpose
Implements the ROHM BD2606MVV six-channel I2C LED driver. It supports binary or 6-bit brightness depending on whether both LEDs in a hardware pair are active, because each pair shares one brightness register.

## Important APIs, Types, And Functions
`struct bd2606mvv_priv` stores a six-LED array and regmap. `struct bd2606mvv_led` stores LED number, classdev, and private pointer. The main callback is `bd2606mvv_brightness_set`; probe parses fwnode children and registers LEDs.

## Control Flow
Probe requires a firmware node, initializes regmap, walks child nodes, reads unique `reg` values 0-5, records fwnode handles, counts active pairs, and sets a blocking brightness callback. It then registers each present LED, reducing `max_brightness` to one for LEDs in a pair where both siblings are present.

Brightness zero clears the LED's power bit in `BD2606_REG_PWRCNT`. Nonzero brightness writes the pair's shared brightness register, using full scale when max brightness is one, then sets the power bit.

## State And Persistence
State includes child fwnode references and active-pair-derived max brightness. Hardware state persists in three shared brightness registers and the power-control register.

## Dependencies And Integration Points
Depends on I2C, regmap, fwnode child properties, and LED class. Compatible is `rohm,bd2606mvv`.

## Risks
Fwnode handles are acquired but only released on some registration-error paths, so handle lifetime deserves scrutiny. Shared brightness registers mean two LEDs in one pair cannot be independently dimmed; reducing max brightness to one is the ABI signal for this limitation. Duplicate or out-of-range child regs reject probe.

## Test Signals
Test child parsing for all six channels, duplicate rejection, paired LED max-brightness reduction, brightness register writes for single and paired LEDs, power bit updates, and cleanup on registration failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-bd2606mvv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-bd2802.c -->
# sources/distributed-fs/ceph-client/drivers/leds/leds-bd2802.c

## Purpose
Implements the ROHM BD2802GU RGB LED controller. It exposes six legacy LED class devices, one for each RGB component of two LEDs, plus driver-specific sysfs attributes for waveform/current and an advanced direct-register configuration mode.

## Important APIs, Types, And Functions
`struct bd2802_led` stores platform data, client, reset GPIO, rwsem, software state for two RGB LEDs, six classdevs, advanced-configuration flag, selected LED/color/state, wave pattern, and RGB current. Macros generate per-color brightness/blink callbacks and direct register sysfs stores. Key helpers include `bd2802_set_on`, `bd2802_set_blink`, `bd2802_turn_off`, `bd2802_enable_adv_conf`, `bd2802_register_led_classdev`, suspend/resume helpers, and probe/remove.

## Control Flow
Probe allocates state, requests reset GPIO, detects the chip by writing clock setup, resets the chip to save power, initializes defaults, creates device attributes, and registers all six classdevs. Brightness callbacks map nonzero to steady-on and zero to off. Blink callbacks reject zero on/off delays and set hardware blink using the current `wave_pattern`.

When the first channel turns on, reset is deasserted and common timing is configured. Turning off a component clears current registers, updates cached RGB state, and if all outputs are off and advanced mode is disabled, asserts reset. Advanced mode dynamically exposes raw register sysfs files and keeps the chip out of reset.

## State And Persistence
Software tracks two-bit state for each color of each LED, default wave/current settings, and whether advanced mode owns direct register access. Suspend asserts reset; resume reinitializes and restores cached LED states or advanced mode.

## Dependencies And Integration Points
Depends on I2C SMBus, reset GPIO, platform data `leds-bd2802.h`, LED class, PM sleep, and custom device sysfs attributes. It does not use modern fwnode LED naming.

## Risks
The driver has a broad custom sysfs ABI and direct register access that can conflict with LED class operations. Many hardware writes ignore errors after logging through `bd2802_write_byte`. Six separate classdev fields avoid `container_of` arrays but create repetitive error paths. Advanced mode changes reset behavior and persistence assumptions.

## Test Signals
Test registration/unregistration of all six LEDs, steady and blink modes, reset assertion when all LEDs off, advanced configuration on/off and raw register files, wave/current attributes, suspend/resume state restoration, and cleanup if classdev registration fails mid-sequence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-bd2802.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-blinkm.c -->
# sources/distributed-fs/ceph-client/drivers/leds/leds-blinkm.c

## Purpose
Implements support for BlinkM RGB smart LEDs over a simple nonstandard I2C command protocol. Depending on configuration, it registers either three separate red/green/blue LED class devices or one multicolor LED class device, and it also exposes a legacy `blinkm` sysfs group.

## Important APIs, Types, And Functions
`struct blinkm_data` stores I2C client, mutex, LED objects, current/next RGB and HSB values, command argument buffer, address/version/script fields, and mode flags. `struct blinkm_led` stores the client, union of normal/multicolor classdev, and color ID.

Important functions are `blinkm_write`, `blinkm_read`, `blinkm_transfer_hw`, per-color sysfs show/store, `blinkm_set_mc_brightness`, separate color callbacks, `blinkm_detect`, `register_separate_colors`, `register_multicolor`, `blinkm_probe`, and `blinkm_remove`.

## Control Flow
Probe allocates state, initializes defaults and mutex, creates the `blinkm` sysfs group, registers either separate RGB classdevs or one multicolor classdev, and sends stop-script/go-RGB initialization commands. The transfer helper locks the device, prepares command arguments from cached next values, writes commands and optional arguments as byte writes, performs byte reads for read commands, and updates cached current values.

Separate color classdevs update one next color and issue `BLM_GO_RGB`. Multicolor brightness first calls `led_mc_calc_color_components`, copies subLED brightness into next RGB values, and issues `BLM_GO_RGB`. Detect scans address 0x09 and repeatedly balances command/read sequences to avoid confusing the device.

## State And Persistence
The driver maintains shadow current and next RGB/HSB/script fields. Hardware state is inside the BlinkM firmware and command sequencer. Remove unregisters LEDs, fades/resets colors through several I2C commands, and removes sysfs.

## Dependencies And Integration Points
Depends on I2C SMBus byte operations, LED class, optional multicolor LED class, sysfs, runtime PM headers, and I2C legacy detection using `I2C_CLASS_HWMON`.

## Risks
The BlinkM protocol requires balanced sequences; incomplete write/read pairs can leave the device confused. In multicolor mode, `blinkm_remove` still unregisters three union members as plain classdevs, which is a risk area because only one multicolor classdev is registered. `register_multicolor` returns zero even after a registration error path, which can mask failures. Several advanced commands are explicitly unimplemented.

## Test Signals
Test detection at address 0x09, sysfs RGB show/store, test sequence, separate-color registration, multicolor registration with `multi_intensity`, I2C error handling for command sequences, remove fade/reset behavior, and configuration differences with `CONFIG_LEDS_BLINKM_MULTICOLOR`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-blinkm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-cht-wcove.c -->
# sources/distributed-fs/ceph-client/drivers/leds/leds-cht-wcove.c

## Purpose
Implements LEDs connected to the Intel Cherry Trail Whiskey Cove PMIC. It exposes charging and indicator LEDs with brightness, hardware blink, breathing pattern support, model-specific default charging triggers, and suspend/resume register preservation.

## Important APIs, Types, And Functions
`struct cht_wc_led` stores classdev, register descriptor, regmap, mutex, and saved registers. `struct cht_wc_leds` contains two LEDs and saved initial LED1 registers. Important callbacks are `cht_wc_leds_brightness_set/get`, `cht_wc_leds_blink_set`, `cht_wc_leds_pattern_set/clear`, register save/restore helpers, probe/remove/shutdown, and PM suspend/resume.

## Control Flow
Probe obtains the parent `intel_soc_pmic`, skips a model where LED1 drives haptics, saves LED1 initial registers, assigns a model-specific charging trigger when known, initializes two classdevs with names `platform::charging` and `platform::indicator`, and registers them. Brightness writes PWM and on/off control bits, disabling hardware blinking when turning off. Blink chooses the closest supported frequency or returns `-EINVAL` for software fallback. For a default charging trigger, blink is translated into slow breathing. Pattern support accepts exactly two-step off/on breathing patterns with supported delta times.

Remove or shutdown disables LEDs and restores initial LED1 registers if LED1 was originally hardware-controlled. Suspend saves all LED registers, disables LEDs, and resume restores saved values.

## State And Persistence
Register snapshots preserve PMIC state across remove/shutdown/suspend. Per-LED mutexes serialize regmap operations. Hardware settings persist because the PMIC is battery-powered, so restoration is part of correctness.

## Dependencies And Integration Points
Depends on `intel_soc_pmic`, PM sleep, regmap, LED class, trigger names for battery chargers, and platform alias `cht_wcove_leds`.

## Risks
Register changes are persistent across reboots/removal on battery-powered PMIC hardware. Model-specific trigger names must match charger drivers. Hardware blink supports only four frequencies; unsupported patterns must fall back cleanly. LED1 may be non-LED hardware on some models and is explicitly skipped.

## Test Signals
Test on supported model IDs, verify default trigger assignment, brightness and PWM writes, blink frequency quantization, breathing pattern acceptance/rejection, suspend/resume restoration, shutdown disable, and initial LED1 hardware-control restoration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-cht-wcove.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-clevo-mail.c -->
# sources/distributed-fs/ceph-client/drivers/leds/leds-clevo-mail.c

## Purpose
Implements the mail LED found on selected older Clevo laptops through i8042 controller commands. It registers one LED class device named `clevo::mail` after DMI detection or with the `nodetect` module parameter.

## Important APIs, Types, And Functions
The static classdev `clevo_mail_led` provides `brightness_set`, `blink_set`, and `LED_CORE_SUSPENDRESUME`. Key functions are the DMI callback/table, `clevo_mail_led_set`, `clevo_mail_led_blink`, platform probe/remove, module init, and module exit.

## Control Flow
Module init checks the DMI table unless `nodetect` is set, registers a simple platform device, and probes a platform driver that registers the LED. Brightness off sends `CLEVO_MAIL_LED_OFF`; brightness up to `LED_HALF` sends 0.5 Hz blink; higher brightness sends 1 Hz blink. Blink supports default 0/0 by selecting 0.5 Hz, exact 500/500 for 1 Hz, and exact 1000/1000 for 0.5 Hz; other delays return `-EINVAL`.

Exit unregisters platform objects and explicitly turns the LED off.

## State And Persistence
No private state is stored except the global platform device pointer and module parameter. Hardware state is the laptop controller LED mode. i8042 access is protected with `i8042_lock_chip`.

## Dependencies And Integration Points
Depends on DMI, platform devices, i8042 command locking, and LED class. It integrates with known Clevo DMI identities and allows risky forced probing with `nodetect`.

## Risks
i8042 commands are platform-specific; false-positive probing can affect keyboard-controller behavior. Brightness maps to blink modes rather than steady intensity. Only two blink rates are supported. The `nodetect` parameter intentionally bypasses safety checks.

## Test Signals
On matched hardware, registration should create `clevo::mail`; brightness values should issue off/slow/fast commands; supported blink delays should update returned delays and succeed; unsupported delays should fall back through `-EINVAL`; module exit should turn the LED off.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-clevo-mail.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-cobalt-qube.c -->
# sources/distributed-fs/ceph-client/drivers/leds/leds-cobalt-qube.c

## Purpose
Implements the front LED for Cobalt Qube systems using one memory-mapped byte port. It exposes a single LED classdev named `qube::front` with the `default-on` trigger.

## Important APIs, Types, And Functions
Global `led_port` stores the mapped MMIO address and `led_value` stores the byte written. `qube_front_led_set` is the LED callback; `cobalt_qube_led_probe` maps the resource and registers the classdev.

## Control Flow
Probe obtains the first memory resource, maps it, sets both front LED bits on, writes the byte, and registers the LED through devm. Brightness on writes both front LED bits; brightness off writes the inverse of both bits.

## State And Persistence
State is global and single-instance. Hardware state is the byte written to the mapped port. The classdev starts at `LED_FULL`.

## Dependencies And Integration Points
Depends on platform memory resources, MMIO byte access, and LED class. Platform alias is `cobalt-qube-leds`.

## Risks
The off value is `~(LED_FRONT_LEFT | LED_FRONT_RIGHT)` assigned to `u8`, which sets all other bits high and assumes that is safe for the port. Global state prevents multiple instances. There is no locking because only one LED is exposed.

## Test Signals
Probe should map the resource, write the initial on byte, and create `qube::front`. Brightness toggles should write expected bytes and default trigger should keep the LED on unless userspace changes it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-cobalt-qube.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-cobalt-raq.c -->
# sources/distributed-fs/ceph-client/drivers/leds/leds-cobalt-raq.c

## Purpose
Implements LED support for Cobalt RaQ systems using a memory-mapped byte port. It exposes a web LED and a power-off LED, the latter using the `power-off` default trigger.

## Important APIs, Types, And Functions
Global `led_port`, `led_value`, and `led_value_lock` manage the shared byte register. `raq_web_led_set` and `raq_power_off_led_set` update individual bits. `cobalt_raq_led_probe` maps the resource and registers both classdevs.

## Control Flow
Probe maps the first memory resource, registers `raq::power-off`, then registers `raq::web`; on failure it unregisters the first LED and clears the port pointer. Each brightness callback takes the spinlock, sets or clears its bit in `led_value`, writes the byte, and releases the lock.

## State And Persistence
Shared `led_value` is the software shadow for both LED bits. Hardware state is the mapped byte port. The driver is built in via `builtin_platform_driver`, so it is expected as platform support rather than a removable module.

## Dependencies And Integration Points
Depends on platform memory resources, MMIO byte writes, spinlocks, and LED class. Platform driver name is `cobalt-raq-leds`.

## Risks
There is no remove path because the driver is builtin. Initial `led_value` defaults to zero until a LED is changed. All shared port writes depend on the spinlock and software shadow staying coherent with hardware.

## Test Signals
Probe should register both LED class devices, power-off trigger should bind to `raq::power-off`, toggling either LED should preserve the other bit in `led_value`, and registration failure should unregister the already-created LED.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-cobalt-raq.c -->
