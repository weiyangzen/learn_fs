# subset-b-004249 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/tps65010.c -->
## sources/distributed-fs/ceph-client/drivers/mfd/tps65010.c

### Purpose
`tps65010.c` is the legacy MFD-style I2C driver for the TPS65010/TPS65011/TPS65012/TPS65013/TPS65014 portable-device PMIC family. It covers charger and regulator status monitoring, USB VBUS draw programming, GPIO/LED/vibrator control, optional debugfs inspection, board setup/teardown callbacks, and a small gpiochip exposing four GPIOs plus LED/vibrator outputs. Unlike newer PMIC drivers in this set, it does not use regmap or `mfd_add_devices`; it exports direct helper APIs around a single global device instance.

### Important APIs, Types, And Functions
The central state is `struct tps65010`, which stores the `i2c_client`, mutex, delayed work item, debugfs file, chip model, cached charger/regulator status, IRQ masks, requested VBUS current, GPIO output mask, `gpio_chip`, and flags `FLAG_VBUS_CHANGED`/`FLAG_IRQ_ENABLE`. Public exported APIs are `tps65010_set_vbus_draw()`, `tps65010_set_gpio_out_value()`, `tps65010_set_led()`, `tps65010_set_vib()`, `tps65010_set_low_pwr()`, `tps65010_config_vregs1()`, `tps65010_config_vdcdc2()`, and `tps65013_set_low_pwr()`. Probe/remove are `tps65010_probe()` and `tps65010_remove()`. IRQ and polling paths are `tps65010_irq()`, `tps65010_work()`, and `tps65010_interrupt()`. GPIO callbacks are `tps65010_gpio_set()`, `tps65010_output()`, and `tps65010_gpio_get()`.

### Control Flow
The driver is registered from `subsys_initcall(tps_init)` so early regulator/board users can call its exported helpers. Probe rejects a second instance through the global `the_tps`, checks SMBus byte-data support, allocates state, requests a falling-edge IRQ with `IRQF_NO_AUTOEN` when present, determines POR/AUA semantics from the model, reads initial charger/regulator registers, unmasks selected PMIC interrupt sources, masks GPIO IRQs, runs `tps65010_work()` once synchronously, creates a debugfs file, and optionally registers a gpiochip plus board `setup()`. Hardware IRQs disable the parent IRQ, set `FLAG_IRQ_ENABLE`, and schedule delayed work. The work function serializes through `tps->lock`, polls status, updates charger state, applies pending VBUS draw changes to `TPS_CHGCONFIG`, and re-enables the parent IRQ.

### State, Persistence, And Dependencies
State is mostly mutable register state and cached shadows inside `struct tps65010`. `chgstatus`, `regstatus`, and `chgconf` track last-observed PMIC state for edge/change detection. `nmask1`/`nmask2` are unmasked status bits, and `vbus` persists the requested USB charging current until an actual USB-present update can be written. The driver depends on SMBus byte reads/writes, `system_power_efficient_wq`, Linux IRQ APIs, debugfs/seq_file, gpiolib, platform board data from `struct tps65010_board`, and public constants from `linux/mfd/tps65010.h`.

### Integration Points
Consumers call the exported TPS65010 helper functions directly, so this file is both core driver and service API. Board files can provide GPIO output masks plus setup/teardown callbacks. Debugfs exposes register snapshots and may acknowledge status by reading status registers. Optional USB gadget builds default VBUS draw to 100 mA. The gpiochip maps offsets 0-3 to GPIO1-4, offsets 4-5 to LED1/LED2, and offset 6 to the vibrator driver.

### Risks
The global singleton prevents multiple chips and makes exported helpers fail with `-ENODEV` when probe has not completed. Several I2C reads in debug and initialization paths do not validate negative return values before formatting. `tps65010_set_vbus_draw()` uses local IRQ disabling and comments that it assumes non-SMP, which is fragile by modern standards. IRQ and polling logic depend on status reads that may acknowledge PMIC interrupts, so debugfs reads can perturb event state. `tps65010_remove()` sets `the_tps = NULL` but devm memory and external users may still hold stale assumptions if they race removal.

### Test Signals
Useful tests include probe for each model ID, single-instance rejection, absent IRQ warning behavior, VBUS draw changes while USB is present and absent, charger state transitions for USB/AC/timeout/temp errors, gpiochip output/input readback, LED ON/OFF/BLINK writes, vibrator toggling, low-power mode for TPS65010/12 and AUA low-power for TPS65011/13/14, board setup/teardown callbacks, debugfs reads, and remove with pending delayed work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/tps65010.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/tps6507x.c -->
## sources/distributed-fs/ceph-client/drivers/mfd/tps6507x.c

### Purpose
`tps6507x.c` is a small I2C MFD core for the TPS6507x PMIC family. It allocates a shared `struct tps6507x_dev`, installs low-level I2C read/write callbacks, and creates two child devices: `tps6507x-pmic` and `tps6507x-ts`.

### Important APIs, Types, And Functions
The file's main data is `tps6507x_devs[]`, listing the PMIC and touchscreen child cells. `tps6507x_i2c_read_device()` performs register-address write plus data read using two `i2c_msg`s. `tps6507x_i2c_write_device()` sends register byte plus payload with `i2c_master_send()`. `tps6507x_i2c_probe()` allocates state and calls `devm_mfd_add_devices()`. Matching is by I2C ID `"tps6507x"` and OF compatible `"ti,tps6507x"`.

### Control Flow
Registration happens at `subsys_initcall()` so dependent devices can appear early. Probe allocates state, stores it as I2C client data, fills `dev`, `i2c_client`, `read_dev`, and `write_dev`, then registers child MFD cells. The read helper returns `0` only if the adapter completes exactly two messages; partial positive transfers become `-EIO`. The write helper rejects payloads larger than `TPS6507X_MAX_REGISTER`, builds a stack buffer with register plus payload, and treats short sends as `-EIO`.

### State, Persistence, And Dependencies
This driver owns no cached register state. Persistent behavior is limited to child drivers using the callback pointers to read/write PMIC registers. It depends on Linux I2C, OF matching, `mfd/core`, and `linux/mfd/tps6507x.h`.

### Integration Points
The child PMIC and touchscreen drivers receive their parent device and access the chip through the shared `struct tps6507x_dev`. The MFD registration is devm-managed, so child removal follows parent lifetime. There is no IRQ, regmap, power-off, or regulator policy in this file.

### Risks
The write-size guard compares payload length to `TPS6507X_MAX_REGISTER`, which is a register maximum rather than an explicit buffer payload limit, so header definitions must keep that value sensible. The driver provides no locking around read/write callbacks, leaving serialization to child users or I2C core behavior. No fallback exists for adapters without full I2C transfer support.

### Test Signals
Probe should create both child devices from I2C ID and OF matches. I2C fault injection should cover partial read transfers, partial writes, oversized writes, and adapter errors. Child-driver smoke tests should validate PMIC register writes and touchscreen register reads through the callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/tps6507x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/tps65086.c -->
## sources/distributed-fs/ceph-client/drivers/mfd/tps65086.c

### Purpose
`tps65086.c` is the I2C MFD core for the TPS65086 PMIC. It creates a regmap, reads device/OTP/revision IDs, registers a regmap IRQ chip when an interrupt line is provided, and adds regulator, GPIO, and reset child devices.

### Important APIs, Types, And Functions
Important static objects are `tps65086_cells[]`, `tps65086_yes_ranges[]`, `tps65086_volatile_table`, `tps65086_regmap_config`, `tps65086_irqs[]`, and `tps65086_irq_chip`. The driver entry points are `tps65086_probe()` and `tps65086_remove()`. The regmap uses 8-bit registers/values, `REGCACHE_MAPLE`, volatile ranges for IRQ/status/GPO/power-good/over-current registers, and `max_register = TPS65086_OC_STATUS`.

### Control Flow
Probe allocates `struct tps65086`, stores device and IRQ fields, initializes the I2C regmap, reads `TPS65086_DEVICEID1` into `chip_id`, reads `TPS65086_DEVICEID2` for part/OTP/revision logging, and installs a regmap IRQ chip for DIETEMP, SHUTDN, and FAULT interrupts if `client->irq > 0`. It then calls `mfd_add_devices()` with the regmap IRQ domain. If child creation fails after IRQ setup, it removes the IRQ chip. Remove removes the regmap IRQ chip when present.

### State, Persistence, And Dependencies
Persistent state includes the regmap cache, `chip_id`, `irq_data`, and children. Hardware state is changed mainly through child drivers. Dependencies include I2C, regmap, regmap-irq, MFD core, and `linux/mfd/tps65086.h`.

### Integration Points
The regulator child uses the stored chip ID to select the correct regulator configuration for the IC variant. GPIO and reset children share the parent regmap through the MFD parent. Regmap IRQ domain supplies nested IRQs to child devices. OF matching uses `"ti,tps65086"` and I2C matching uses `"tps65086"`.

### Risks
If no IRQ is provided, children are still created with a NULL IRQ domain; child drivers must tolerate absent IRQ resources. `mfd_add_devices()` is non-devm and removal only deletes the IRQ chip, so the surrounding MFD core must clean children through normal device removal behavior. Volatile-range omissions could lead to stale fault or power-good status in cache.

### Test Signals
Tests should cover regmap initialization failure, ID read failures, version log formatting, probe with and without IRQ, regmap IRQ delivery for DIETEMP/SHUTDN/FAULT, child-device creation failure unwinding, and representative reads of volatile status registers across suspend/resume or cache sync.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/tps65086.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/tps65090.c -->
## sources/distributed-fs/ceph-client/drivers/mfd/tps65090.c

### Purpose
`tps65090.c` is the core I2C MFD driver for the TPS65090 PMIC. It defines PMIC and charger child cells, exposes a charger VAC-status IRQ resource, configures a two-register regmap IRQ chip, and uses a mostly volatile regmap because status bits are mixed into many registers.

### Important APIs, Types, And Functions
Key structures include `charger_resources[]`, `tps65090s[]`, `tps65090_irqs[]`, `tps65090_irq_chip`, and `tps65090_regmap_config`. `is_volatile_reg()` marks all registers volatile except interrupt masks and charger-control registers `CG_CTRL0` through `CG_CTRL5`. The main entry point is `tps65090_i2c_probe()`.

### Control Flow
Probe requires platform data or an OF node, derives an IRQ base from platform data, allocates `struct tps65090`, initializes an I2C regmap, and adds a regmap IRQ chip when `client->irq` exists using `IRQF_ONESHOT | IRQF_TRIGGER_LOW`. If no IRQ exists, it clears the charger cell's resources so children are not told about a non-firing IRQ. It then registers the PMIC and charger cells. On MFD add failure it deletes the IRQ chip when installed.

### State, Persistence, And Dependencies
The file persists `rmap` and `irq_data` in parent state, plus a global mutation of the charger cell's `num_resources` in no-IRQ systems. It depends on Linux I2C, OF, regmap, regmap-irq, and MFD core definitions from `linux/mfd/tps65090.h`.

### Integration Points
The `tps65090-pmic` child handles regulators and PMIC functions, while `tps65090-charger` receives a named IRQ resource and OF compatible `"ti,tps65090-charger"` when IRQ support exists. The regmap IRQ chip maps VAC, VSYS, BAT, charging status/complete, DCDC overloads, and FET overloads across INT1/INT2.

### Risks
`tps65090s[CHARGER].num_resources` is a static global modified at probe when no IRQ exists; if multiple devices were ever supported, one no-IRQ instance would affect later instances. There is no explicit remove callback for `regmap_del_irq_chip()`. The IRQ mask constants are bit positions, not `BIT()` values, but `regmap_irq.mask` convention expects mask bits; this relies on historical header/driver semantics and should be verified against regmap behavior. Broad volatile classification avoids stale status but reduces cache effectiveness.

### Test Signals
Validation should include OF and platform-data probe, no-platform-data rejection, no-IRQ resource removal, regmap IRQ delivery for both INT registers, charger child receiving VAC IRQ only when available, cache behavior for nonvolatile mask/control registers, and MFD failure cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/tps65090.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/tps65217.c -->
## sources/distributed-fs/ceph-client/drivers/mfd/tps65217.c

### Purpose
`tps65217.c` is the MFD core for the TPS65217 PMIC family. It supplies protected register access helpers, a custom IRQ domain/chip, child devices for PMIC/backlight/charger/power-button, and optional shutdown-controller setup.

### Important APIs, Types, And Functions
Exported helpers are `tps65217_reg_read()`, `tps65217_reg_write()`, `tps65217_set_bits()`, and `tps65217_clear_bits()`. Protected writes support `TPS65217_PROTECT_NONE`, `TPS65217_PROTECT_L1`, and `TPS65217_PROTECT_L2`; L2 writes issue the password/write sequence twice. IRQ logic is implemented by `tps65217_irq_chip`, `tps65217_irq_thread()`, `tps65217_irq_map()`, and `tps65217_irq_init()`. Child resources expose AC/USB charger IRQs and power-button IRQ.

### Control Flow
Probe reads the `ti,pmic-shutdown-controller` property, allocates state, initializes an 8-bit regmap with only `TPS65217_REG_INT` volatile, and either initializes an IRQ domain/threaded IRQ or strips child IRQ resources when no parent IRQ exists. It registers children with `devm_mfd_add_devices()`, reads `TPS65217_REG_CHIPID`, optionally sets `TPS65217_STATUS_OFF`, and logs chip/revision. The threaded IRQ reads `TPS65217_REG_INT`, maps each set bit to a nested IRQ, and returns handled only if at least one bit was dispatched.

### State, Persistence, And Dependencies
State includes `irq_lock`, `irq_mask`, `irq_domain`, parent IRQ, and regmap. Register writes can persist PMIC protection/password-controlled settings. The shutdown-controller property persists by setting the PMIC status OFF bit. Dependencies are I2C, regmap, irqdomain, threaded IRQs, MFD core, and `linux/mfd/tps65217.h`.

### Integration Points
Children consume the parent regmap and nested IRQ domain. The PMIC child handles regulators, the backlight child controls LED/backlight hardware, the charger child receives AC/USB IRQs, and the power-button child receives PB IRQ. Device tree compatible is `"ti,tps65217"`.

### Risks
`tps65217_irq_init()` return is ignored in probe, so IRQ initialization failures can leave `tps->irq_domain` NULL while probe continues. The no-IRQ path mutates static `tps65217s[]` resource counts globally. Remove assumes `tps->irq_domain` exists and iterates/removes it, which is risky after no-IRQ or failed-IRQ probe paths. IRQ masking writes are best-effort in initialization and bus sync.

### Test Signals
Tests should cover protected write sequences for none/L1/L2, invalid protection level, IRQ mask/unmask sync writes, threaded IRQ dispatch for AC/USB/PB and empty status, probe without IRQ, IRQ-domain failure behavior, shutdown-controller property setting, child resources, and remove on all probe variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/tps65217.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/tps65218.c -->
## sources/distributed-fs/ceph-client/drivers/mfd/tps65218.c

### Purpose
`tps65218.c` is the MFD core for TPS65218 PMICs. It provides protected regmap write helpers, a regmap IRQ chip for two interrupt registers, child devices for power-button/GPIO/regulators, and optional device-tree configuration for strict voltage supervision, UVLO threshold, and undervoltage hysteresis.

### Important APIs, Types, And Functions
Exported helpers are `tps65218_reg_write()`, `tps65218_set_bits()`, and `tps65218_clear_bits()`. `tps65218_update_bits()` performs read-modify-write under `tps->tps_lock` for the protected write part. `tps65218_regmap_config` uses 8-bit registers/values, `REGCACHE_MAPLE`, and volatile ranges for `INT1`, `INT2`, and `STATUS`. `tps65218_irq_chip` maps PRGC, CC_AQC, HOT, PB, AC, VPRG, load-switch rise/fall, and invalid placeholders.

### Control Flow
Probe allocates state, initializes regmap and mutex, registers a devm regmap IRQ chip using the client IRQ, reads the chip ID to store the revision, applies optional voltage-supervision DT properties through protected L1 writes, then registers the three child cells. The property helpers validate accepted values before writing config bits and return `-EINVAL` on invalid DT input.

### State, Persistence, And Dependencies
Persistent state includes revision, IRQ data, regmap cache, and the configured voltage-supervision bits in PMIC config registers. The helper API depends on the TPS65218 password protocol: L1 writes first write `reg ^ 0x7d` to `TPS65218_REG_PASSWORD`. Dependencies include I2C, regmap, regmap-irq, MFD core, mutexes, OF properties, and `linux/mfd/tps65218.h`.

### Integration Points
The `tps65218-pwrbutton`, `tps65218-gpio`, and `tps65218-regulator` children share the parent regmap and IRQ domain. Device tree compatible is `"ti,tps65218"`. Regulator and GPIO children can use the exported protected bit helpers for passworded registers.

### Risks
The update helper reads before taking `tps_lock`, so concurrent protected updates to the same register can lose changes between read and write. The return value from `tps65218_update_bits()` is ignored in the voltage property helpers after validation, so a failed register write would not abort probe. Probe always attempts `devm_regmap_add_irq_chip()` with `tps->irq`; no explicit no-IRQ fallback is present.

### Test Signals
Test strict/UVLO/hysteresis DT values, invalid property rejection, L1 passworded write sequencing, concurrent set/clear behavior, IRQ mapping across both INT registers, child creation and IRQ domain propagation, chip ID read failure, and probe with missing or invalid IRQ.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/tps65218.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/tps65219.c -->
## sources/distributed-fs/ceph-client/drivers/mfd/tps65219.c

### Purpose
`tps65219.c` supports the TPS65214, TPS65215, and TPS65219 PMIC family through one I2C MFD driver. It selects variant-specific regulator IRQ resources, GPIO/regulator child cells, regmap IRQ chips with main/sub-IRQ mapping, optional power-button child creation, and system restart/power-off handlers.

### Important APIs, Types, And Functions
Reset/power helpers are `tps65219_warm_reset()`, `tps65219_cold_reset()`, `tps65219_soft_shutdown()`, `tps65219_restart()`, and their `sys_off_data` callbacks. Variant data is in `tps65214_cells[]`, `tps65215_cells[]`, `tps65219_cells[]`, `tps65219_pwrbutton_cell`, `tps65214_irq_chip`, `tps65215_irq_chip`, `tps65219_irq_chip`, and `chip_info_table[]`. IRQ definitions are large `regmap_irq` arrays built with `TPS65219_REGMAP_IRQ_REG()`. `tps65219_probe()` is the sole probe path.

### Control Flow
Probe allocates state, obtains the chip ID from OF match data, initializes an 8-bit regmap, unlocks TPS65214 registers with `TPS65214_LOCK_ACCESS_CMD` when needed, adds the selected regmap IRQ chip, adds variant-specific regulator/GPIO children, optionally adds a power-button child if DT has `ti,power-button`, then registers restart and power-off handlers. Restart chooses warm reset only for `REBOOT_WARM`; all other modes use cold reset. Power-off sets the PMIC I2C off-request bit.

### State, Persistence, And Dependencies
State is the regmap, selected variant data, IRQ domain, and registered sys-off handlers. Persistent hardware effects include TPS65214 unlock, soft shutdown requests, warm/cold reset requests, and MFP control bit writes. Dependencies include I2C, regmap, regmap-irq main/sub IRQ support, reboot/sys-off handlers, MFD core, OF match data, and `linux/mfd/tps65219.h`.

### Integration Points
Regulator resources enumerate named fault IRQs for each variant, with TPS65214/TPS65215 having fewer LDO resources than TPS65219. GPIO child names are variant-specific. The optional `tps65219-pwrbutton` child receives falling/rising power-button IRQs. OF compatibles are `"ti,tps65214"`, `"ti,tps65215"`, and `"ti,tps65219"`.

### Risks
The driver assumes OF match data is present and indexes `chip_info_table` directly. Restart and power-off callbacks ignore register-write return values in the wrapper paths and return `NOTIFY_DONE`, so failed resets may be silent. IRQ maps are dense and variant-specific; wrong register positions or resources would route child IRQs incorrectly. TPS65214 unlock failure aborts probe, but later lock-state handling is not represented here.

### Test Signals
Tests should probe all three compatibles, verify selected child names/resources, exercise main-status-to-sub-register IRQ decoding, verify power-button optional child creation, inject TPS65214 unlock failures, test warm/cold restart bit writes, soft-shutdown bit writes, and validate regulator fault IRQ names against child requests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/tps65219.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/tps6586x.c -->
## sources/distributed-fs/ceph-client/drivers/mfd/tps6586x.c

### Purpose
`tps6586x.c` is the core I2C MFD driver for TPS6586x PMICs. It wraps regmap access in exported legacy helper functions, implements a custom irqdomain/irq_chip for five interrupt mask registers and four ack/status bytes, registers GPIO/regulator/RTC/onkey children, handles optional platform-data subdevices, and can register system power-off/restart handlers.

### Important APIs, Types, And Functions
Exported register helpers are `tps6586x_write()`, `tps6586x_writes()`, `tps6586x_read()`, `tps6586x_reads()`, `tps6586x_set_bits()`, `tps6586x_clr_bits()`, `tps6586x_update()`, `tps6586x_irq_get_virq()`, and `tps6586x_get_version()`. State is `struct tps6586x`, containing regmap, version, IRQ state, cached mask registers, enabled IRQ bitmap, and irqdomain. IRQ functions include `tps6586x_irq_enable()`, `tps6586x_irq_disable()`, `tps6586x_irq_sync_unlock()`, `tps6586x_irq()`, and `tps6586x_irq_init()`.

### Control Flow
Probe obtains platform data directly or from OF, reads `VERSIONCRC` before regmap initialization, allocates state, initializes an 8-bit maple regmap, initializes the custom IRQ controller if a parent IRQ exists, adds fixed MFD cells, then adds platform-data subdevices. If `pm_off` is set, it registers sys-off handlers. The IRQ thread bulk-reads four ACK bytes, converts from little endian, and dispatches nested IRQs only for bits present in `irq_en`. Suspend disables the parent IRQ and resume re-enables it.

### State, Persistence, And Dependencies
The driver caches interrupt mask bytes and writes them to hardware during IRQ bus unlock. Regmap treats mask registers as nonvolatile and all other registers as volatile. Persistent effects include child-driver register writes, subdevice registration, wakeup enablement, sleep-mode power-off sequence, and soft-reset restart sequence. Dependencies include I2C, regmap, irqdomain, MFD core, platform data from `linux/mfd/tps6586x.h`, reboot/sys-off handlers, and OF parsing.

### Integration Points
Fixed children are `tps6586x-gpio`, `tps6586x-regulator`, `tps6586x-rtc` with RTC alarm IRQ, and `tps6586x-onkey`. Board/platform data can add arbitrary subdevices with their own platform data and OF nodes. Child drivers can map virtual IRQs through `tps6586x_irq_get_virq()`.

### Risks
The IRQ domain allocation path can leak allocated descriptors if later IRQ setup fails. `tps6586x_irq_init()` ignores write/read errors while masking and clearing initial interrupts. `tps6586x_get_version()` uses `dev_get_drvdata(dev)` while other helpers convert from an I2C client device; callers must pass the expected device. OF parsing creates no subdevices, so older board-data paths may be required for full functionality. Power-off/restart handlers intentionally delay and return timeout if hardware does not remove power/reboot.

### Test Signals
Test version detection names, platform-data and OF probe, no-platform-data rejection, exported read/write/update helpers, IRQ mask caching and nested dispatch, RTC alarm IRQ mapping, suspend/resume IRQ disable/enable, subdevice add failure cleanup, power-off sleep bit sequence, restart soft-reset bit sequence, and wakeup behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/tps6586x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/tps65910.c -->
## sources/distributed-fs/ceph-client/drivers/mfd/tps65910.c

### Purpose
`tps65910.c` is the I2C MFD core for TPS65910 and TPS65911 PMICs. It creates GPIO/PMIC/RTC/power child devices, initializes regmap and regmap IRQ support with chip-specific IRQ tables, parses board or device-tree configuration, configures 32 kHz/sleep behavior, and can install a global `pm_power_off` callback.

### Important APIs, Types, And Functions
Static child data is `tps65910s[]` with RTC alarm resource. IRQ data is split into `tps65910_irqs[]`, `tps65911_irqs[]`, `tps65910_irq_chip`, and `tps65911_irq_chip`. `is_volatile_reg()` caches regulator registers except non-existing TPS65911 VDDCTRL registers on TPS65910. Setup helpers include `tps65910_irq_init()`, `tps65910_ck32k_init()`, `tps65910_sleepinit()`, `tps65910_parse_dt()`, and `tps65910_power_off()`.

### Control Flow
Probe accepts platform data or parses OF match/properties. It allocates platform init data and `struct tps65910`, performs a dummy I2C transfer for silicon erratum SWCZ010, initializes regmap, initializes IRQs if platform data has IRQ information, applies ck32k and sleep options, optionally sets power-off mode and assigns `pm_power_off`, then registers MFD children with the regmap IRQ domain.

### State, Persistence, And Dependencies
State includes chip ID, OF platform data, regmap, IRQ data, and a static `tps65910_i2c_client` for power-off. Persistent hardware effects include DEVCTRL sleep bits, SLEEP_KEEP_RES_ON bits, CK32K control, power-off mode, and eventual DEV_OFF transition. Dependencies include I2C, regmap, regmap-irq, OF/property APIs, MFD core, and `linux/mfd/tps65910.h`.

### Integration Points
Children are `tps65910-gpio`, `tps65910-pmic`, `tps65910-rtc`, and `tps65910-power`. The RTC child receives alarm IRQ. Device tree properties control voltage-monitor thresholds, clock crystal, sleep enablement, keep-on resources, and system power controller behavior. The companion `tps65911-comparator.c` child relies on parent platform data and regmap.

### Risks
`tps65910_irq_init()`, ck32k init, and sleep init return values are ignored in probe, so failures can be logged but not abort initialization. `pm_power_off` uses a global I2C client pointer and is not cleared here. The regmap IRQ chip selection uses a static local pointer. Volatile classification depends on valid driver data being installed before regmap queries. Device-tree parsing requires match data; missing platform data returns `-EINVAL`.

### Test Signals
Test TPS65910 and TPS65911 OF matches, dummy-transfer tolerance, regmap volatile behavior for existing and non-existing regulator registers, IRQ mapping for both chip variants, DT sleep/keep-on/ck32k/power-controller properties, power-off DEVCTRL writes, child creation, and ignored-error paths for IRQ/sleep initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/tps65910.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/tps65911-comparator.c -->
## sources/distributed-fs/ceph-client/drivers/mfd/tps65911-comparator.c

### Purpose
`tps65911-comparator.c` is a small platform child driver for the TPS65911 voltage comparators. It programs comparator thresholds from parent board data and exposes read-only sysfs files reporting the selected threshold for comparator 1 and comparator 2.

### Important APIs, Types, And Functions
The comparator table is `tps_comparators[]`, with `COMP1` using `TPS65911_VMBCH` and `COMP2` using `TPS65911_VMBCH2`. `COMP_VSEL_TABLE[]` maps register selector values to millivolt thresholds. `comp_threshold_set()` chooses the first table value at or above the requested threshold and writes selector bits. `comp_threshold_get()` reads the register and returns the table value. Sysfs show path is `comp_threshold_show()`. Probe/remove are `tps65911_comparator_probe()` and `tps65911_comparator_remove()`.

### Control Flow
Probe obtains the parent `struct tps65910` and parent platform data, writes COMP1 and COMP2 thresholds from `vmbch_threshold` and `vmbch2_threshold`, then creates `comp1_threshold` and `comp2_threshold` sysfs files. Remove deletes both files. The driver registers at `subsys_initcall()`.

### State, Persistence, And Dependencies
The driver keeps no private state. Persistent effects are threshold register writes through the parent regmap. It depends on parent platform data being present and populated, `dev_get_drvdata(pdev->dev.parent)`, regmap, sysfs device attributes, and `linux/mfd/tps65910.h`.

### Integration Points
It is intended as a child of the TPS65910/TPS65911 MFD parent, even though the parent child table in the inspected source does not list this cell directly. It relies on the parent regmap and threshold board data parsed or supplied by `tps65910.c`.

### Risks
Probe dereferences `pdata` without checking for NULL, so OF-only systems must ensure the parent has compatible board data if this child is instantiated. `comp_threshold_set()` does not bounds-check the table index before reading, relying on reaching `uV_max`; malformed tables could overrun. If creating the first sysfs file succeeds and the second fails, probe returns the second error without removing the first. The sysfs attributes are read-only; thresholds cannot be changed after probe.

### Test Signals
Test threshold selection around duplicate 2500 mV entries, maximum and over-maximum inputs, regmap read/write failures, missing parent platform data, sysfs content for both attributes, and cleanup after probe failure or remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/tps65911-comparator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/tps65912-core.c -->
## sources/distributed-fs/ceph-client/drivers/mfd/tps65912-core.c

### Purpose
`tps65912-core.c` provides bus-independent MFD initialization for TPS65912 PMICs. It defines child devices, IRQ mappings, volatile regmap policy, exports the shared regmap config, and exports `tps65912_device_init()` for I2C and SPI transport drivers.

### Important APIs, Types, And Functions
Key exported symbols are `tps65912_regmap_config` and `tps65912_device_init()`. Static data includes `tps65912_cells[]` for regulator and GPIO children, `tps65912_irqs[]` covering power/thermal/GPIO/power-good IRQs across four status registers, `tps65912_irq_chip`, and `tps65912_volatile_table`.

### Control Flow
Bus drivers allocate `struct tps65912`, initialize `tps->regmap`, set `tps->dev` and `tps->irq`, then call `tps65912_device_init()`. The core adds a devm regmap IRQ chip with `IRQF_ONESHOT`, then registers regulator and GPIO children with the resulting IRQ domain.

### State, Persistence, And Dependencies
The core persists `irq_data` in parent state and the regmap cache policy. Volatile registers span `TPS65912_INT_STS` through `TPS65912_GPIO5`. Dependencies include regmap, regmap-irq, MFD core, module exports, and `linux/mfd/tps65912.h`.

### Integration Points
`tps65912-i2c.c` and `tps65912-spi.c` consume the exported regmap config and device init function. Child drivers consume the parent regmap and IRQ domain for regulator and GPIO functionality.

### Risks
`tps65912_device_init()` always attempts IRQ-chip registration; probe on systems without a usable IRQ may fail unless regmap-irq tolerates the supplied value. The volatile range is broad and includes GPIO registers, which preserves correctness but limits caching. There is no chip revision detection or variant-specific behavior here.

### Test Signals
Test I2C and SPI callers, regmap IRQ registration failure, child creation failure, each mapped IRQ register offset, volatile-table behavior for INT/GPIO ranges, and child IRQ domain requests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/tps65912-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/tps65912-i2c.c -->
## sources/distributed-fs/ceph-client/drivers/mfd/tps65912-i2c.c

### Purpose
`tps65912-i2c.c` is the I2C transport wrapper for TPS65912 PMICs. It allocates parent state, initializes an I2C regmap from the shared core config, and delegates bus-independent setup to `tps65912_device_init()`.

### Important APIs, Types, And Functions
The main function is `tps65912_i2c_probe()`. Matching uses OF compatible `"ti,tps65912"` and I2C ID `"tps65912"`. It consumes `tps65912_regmap_config` and `tps65912_device_init()` from the core file.

### Control Flow
Probe allocates `struct tps65912`, stores it with `i2c_set_clientdata()`, fills `dev` and `irq`, creates the regmap with `devm_regmap_init_i2c()`, logs and returns regmap errors, then returns the result of core initialization.

### State, Persistence, And Dependencies
State is the parent `struct tps65912` and devm-managed I2C regmap. It depends on I2C, regmap, module tables, and the core TPS65912 MFD header/API.

### Integration Points
This file enables TPS65912 devices on I2C buses and has no child-device or IRQ policy of its own. All child creation and IRQ mapping come from `tps65912-core.c`.

### Risks
There is no transport-specific validation beyond regmap initialization. Probe behavior with absent `client->irq` depends entirely on core IRQ setup. The same driver name `"tps65912"` is shared with the SPI module, so module aliases and bus matching must disambiguate by bus type.

### Test Signals
Test OF and I2C ID binding, regmap init failure, propagation of core init errors, IRQ value propagation, and successful child registration through the core.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/tps65912-i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/tps65912-spi.c -->
## sources/distributed-fs/ceph-client/drivers/mfd/tps65912-spi.c

### Purpose
`tps65912-spi.c` is the SPI transport wrapper for TPS65912 PMICs. It mirrors the I2C wrapper but initializes the shared TPS65912 core over `devm_regmap_init_spi()`.

### Important APIs, Types, And Functions
The main function is `tps65912_spi_probe()`. Matching uses OF compatible `"ti,tps65912"` and SPI ID `"tps65912"`. It consumes `tps65912_regmap_config` and `tps65912_device_init()`.

### Control Flow
Probe allocates `struct tps65912`, stores it with `spi_set_drvdata()`, fills device and IRQ pointers, initializes a SPI regmap, returns regmap errors after logging, then calls the core device initialization.

### State, Persistence, And Dependencies
State is limited to the parent object and devm-managed SPI regmap. Dependencies are SPI, regmap, module matching, and the shared TPS65912 MFD core.

### Integration Points
This file lets the same regulator/GPIO/IRQ core operate on SPI-connected PMICs. It owns no child cells, IRQ definitions, or power policy.

### Risks
All no-IRQ and child-creation behavior is delegated to the core. SPI mode, word size, and bus constraints are not validated here, so the board description and SPI core must provide compatible defaults.

### Test Signals
Test OF/SPI ID binding, regmap init failure, successful call into core init, IRQ propagation from `spi->irq`, and SPI read/write behavior through child drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/tps65912-spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/tps6594-core.c -->
## sources/distributed-fs/ceph-client/drivers/mfd/tps6594-core.c

### Purpose
`tps6594-core.c` is the bus-independent MFD core for LP8764, TPS65224, TPS652G1, TPS6593, and TPS6594 PMICs. It defines variant-specific child cells, IRQ resources, regmap IRQ chips, volatile access tables, CRC enable/synchronization policy, ACTIVE-state setup, optional power-button and RTC child registration, and system power-off integration.

### Important APIs, Types, And Functions
The exported API is `tps6594_device_init(struct tps6594 *tps, bool enable_crc)`, plus exported volatile tables `tps6594_volatile_table` and `tps65224_volatile_table`. IRQ resources are grouped for regulators, pinctrl, PFSM, ESM, RTC, ADC, and power button. Variant IRQ tables include `tps6594_irqs[]`, `tps65224_irqs[]`, and `tps652g1_irqs[]`. `tps6594_handle_post_irq()` clears communication-address/error fallout after regmap IRQ ack when CRC is enabled. CRC helpers are `tps6594_check_crc_mode()`, `tps6594_set_crc_feature()`, and `tps6594_enable_crc()`.

### Control Flow
Bus drivers initialize `struct tps6594` and call `tps6594_device_init()`. If requested, CRC enablement either triggers PFSM/I2C CRC on a primary PMIC and completes a global completion, or waits for a primary PMIC before checking secondary CRC mode. The core sets `NSLEEP1B` and `NSLEEP2B` to keep the PMIC active, chooses the correct IRQ chip and child-cell array for TPS65224/TPS652G1 versus TPS6594-class devices, assigns a dynamic IRQ chip name and driver data, registers the regmap IRQ chip, adds common children, optionally adds a TPS65224/TPS652G1 power-button child based on pin configuration, optionally adds RTC for supported chips, and registers a power-off handler when the node is a system power controller.

### State, Persistence, And Dependencies
State includes `tps->chip_id`, `reg`, `irq`, `regmap`, `irq_data`, and `use_crc`. Persistent hardware effects include CRC enablement, active-state trigger bits, interrupt acks, optional power-off trigger writes, and child-visible register state. Dependencies include regmap-irq with custom register lookup, completions, OF properties, bitfield helpers, sys-off, MFD core, and `linux/mfd/tps6594.h`.

### Integration Points
I2C and SPI bus wrappers supply regmap implementations and CRC framing. Children include `tps6594-regulator`, `tps6594-pinctrl`, `tps6594-pfsm`, `tps6594-esm`, `tps6594-rtc`, `tps65224-adc`, and `tps6594-pwrbutton` depending on variant and configuration. The IRQ domain carries named fault, GPIO, PFSM, ESM, RTC, ADC, and power-button interrupts to children.

### Risks
The static regmap IRQ chip objects are mutated per probe (`irq_drv_data` and `name`), which would be unsafe for multiple concurrently probed devices using the same chip object. CRC synchronization uses a single global completion, so multi-primary or reprobe scenarios need scrutiny. CRC post-IRQ cleanup writes error bits after each regmap IRQ pass; wrong chip ID selection could clear the wrong register. Variant IRQ/resource tables are large and hand-maintained, increasing drift risk. The MODULE_AUTHOR line for Bhargav is missing a closing angle bracket in the source string.

### Test Signals
Test all supported chip IDs over both bus wrappers, CRC disabled/enabled primary/secondary flows and timeout, ACTIVE-state write failure, IRQ chip naming, regmap IRQ dispatch for regulator/GPIO/PFSM/ESM/RTC/ADC groups, TPS65224/TPS652G1 power-button pin-detection paths, RTC omission for LP8764/TPS65224/TPS652G1, system-power-controller power-off trigger, and multiple-device probe behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/tps6594-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/tps6594-i2c.c -->
## sources/distributed-fs/ceph-client/drivers/mfd/tps6594-i2c.c

### Purpose
`tps6594-i2c.c` is the I2C transport driver for LP8764, TPS65224, TPS652G1, TPS6593, and TPS6594 PMICs. It implements custom paged I2C regmap access, optional protocol CRC for single-register transactions, variant matching, and delegation to the TPS6594 core.

### Important APIs, Types, And Functions
Key functions are `tps6594_i2c_transfer()`, `tps6594_i2c_reg_read_with_crc()`, `tps6594_i2c_reg_write_with_crc()`, `tps6594_i2c_read()`, `tps6594_i2c_write()`, and `tps6594_i2c_probe()`. `enable_crc` is a read-only module parameter. `tps6594_i2c_regmap_config` uses 16-bit logical registers, 8-bit values, custom read/write callbacks, and a volatile table selected by variant.

### Control Flow
Regmap passes two register bytes where byte 0 is register and byte 1 is page. Non-CRC reads write the register to I2C address `base + page`, then read a bulk payload. Non-CRC writes allocate a buffer omitting the page byte and send register plus data to `base + page`. CRC mode converts bulk reads/writes into loops of single-register operations because auto-increment does not support CRC. Probe allocates state, reads OF match data for chip ID, selects the TPS65224 volatile table for TPS65224/TPS652G1, initializes the custom regmap, populates the CRC8 table, and calls `tps6594_device_init(tps, enable_crc)`.

### State, Persistence, And Dependencies
State includes the parent `struct tps6594`, selected chip ID, I2C base address in `tps->reg`, IRQ, regmap, and `use_crc` set later by the core. Dependencies include I2C, crc8, regmap custom bus callbacks, OF match data, MFD core header, and the shared volatile tables/core init.

### Integration Points
OF compatibles include `"ti,tps6594-q1"`, `"ti,tps6593-q1"`, `"ti,lp8764-q1"`, `"ti,tps65224-q1"`, and `"ti,tps652g1"`. The core consumes the resulting regmap and creates children/IRQ domains. CRC framing must match the core's CRC enable state.

### Risks
The static `tps6594_i2c_regmap_config` is modified at probe for TPS65224/TPS652G1, which can affect later probes of other variants. Non-CRC writes allocate memory for each write and decrement `count` before use; regmap call sizes must remain as expected. CRC mode does not support auto-increment and can be slower for bulk operations. CRC read/write failures return `-EIO`, so tests need to distinguish bus errors from CRC mismatches.

### Test Signals
Test custom page-addressed reads/writes, CRC byte calculation for reads and writes, CRC mismatch handling, bulk-to-single conversion in CRC mode, all OF compatible chip IDs, volatile table switching, regmap init failure, and handoff to core with `enable_crc` true and false.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/tps6594-i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/tps6594-spi.c -->
## sources/distributed-fs/ceph-client/drivers/mfd/tps6594-spi.c

### Purpose
`tps6594-spi.c` is the SPI transport driver for LP8764, TPS65224, TPS652G1, TPS6593, and TPS6594 PMICs. It implements custom single-register SPI regmap access with page bits, read/write command bits, optional CRC, variant matching, and core initialization.

### Important APIs, Types, And Functions
Key functions are `tps6594_spi_reg_read()`, `tps6594_spi_reg_write()`, and `tps6594_spi_probe()`. The module parameter `enable_crc` controls whether the core should enable CRC. `tps6594_spi_regmap_config` uses 16-bit registers, 8-bit values, custom `reg_read`/`reg_write`, `use_single_read`, and `use_single_write`.

### Control Flow
SPI read builds a two-byte command of register and page/read-bit, reads one data byte plus optional CRC, verifies CRC over the command and data when enabled, and returns the data. SPI write builds register, page, value, plus optional CRC and sends it. Probe allocates state, stores chipselect in `tps->reg`, stores IRQ and chip ID from OF match data, selects the TPS65224 volatile table for TPS65224/TPS652G1, initializes the regmap, populates the CRC table, and calls the shared core.

### State, Persistence, And Dependencies
State includes parent object, chip select, IRQ, chip ID, regmap, and CRC state set by the core. Dependencies include SPI, crc8, custom regmap callbacks, OF match data, and `linux/mfd/tps6594.h`.

### Integration Points
The SPI wrapper supports the same OF compatibles and core children as the I2C wrapper. The core decides CRC enablement, IRQ chips, MFD cells, RTC, power button, and power-off behavior.

### Risks
The static regmap config is modified by variant, creating the same multi-device cross-probe risk as the I2C wrapper. SPI access is forced to single reads/writes, which avoids unsupported bulk protocol but may reduce throughput. CRC mismatch returns `-EIO` after a successful SPI transfer. Correct behavior relies on `TPS6594_REG_TO_PAGE()` and command bit definitions matching the PMIC SPI protocol.

### Test Signals
Test read/write command byte formation, page selection, CRC generation and mismatch detection, all OF match variants, volatile table switching, regmap init errors, and successful child creation through the core for CRC and non-CRC modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/tps6594-spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/tqmx86.c -->
## sources/distributed-fs/ceph-client/drivers/mfd/tqmx86.c

### Purpose
`tqmx86.c` is the MFD core for TQ-Systems x86 module PLDs discovered through DMI. It maps LPC I/O registers, identifies board and PLD revisions, configures optional GPIO and I2C interrupt routing, creates watchdog/GPIO child devices, and conditionally creates an `ocores-i2c` child plus onboard EEPROM description when a soft I2C controller is detected.

### Important APIs, Types, And Functions
Module parameters are `gpio_irq` and `i2c1_irq`, accepting IRQ 7, 9, 12, or 0. Resource arrays are `tqmx_i2c_soft_resources[]`, `tqmx_watchdog_resources[]`, and `tqmx_gpio_resources[]`. Child cells are `tqmx86_i2c_soft_dev[]` and `tqmx86_devs[]`. Helpers include `tqmx86_board_id_to_name()`, `tqmx86_board_id_to_clk_rate()`, `tqmx86_setup_irq()`, `tqmx86_probe()`, and `tqmx86_create_platform_device()`.

### Control Flow
Module init checks DMI vendor/product matches and creates a platform device from the DMI callback before registering the platform driver. Probe maps I/O base `0x180`, reads board ID, SAUC, and revision, logs a human-readable board name, reads the I2C soft-controller detect register via `inb()`, optionally programs GPIO IRQ selection and fills the GPIO IRQ resource, sets the ocores clock rate based on board ID, optionally programs I2C1 IRQ and registers the ocores child, then registers watchdog and GPIO cells.

### State, Persistence, And Dependencies
Persistent effects include PLD interrupt routing register writes and child platform devices. Static resource arrays are mutated at probe to add IRQ resources and update clock rate. Dependencies include DMI, I/O port mapping/accessors, platform devices, MFD core, ocores I2C platform data, I2C board info for a 24c32 EEPROM, and module parameters.

### Integration Points
Child drivers are `tqmx86-wdt`, `tqmx86-gpio`, and optionally `ocores-i2c`. The ocores child receives I/O and optional IRQ resources plus platform data describing the onboard EEPROM. Resource conflicts are ignored for watchdog/GPIO cells because the PLD I/O range overlaps.

### Risks
Static mutable resources make multiple-device support unsafe. Invalid IRQ module parameters fail setup but do not abort probe for GPIO/I2C; the corresponding resource is simply not filled. `tqmx86_create_platform_device()` allocates a platform device from a DMI callback without retaining a pointer for explicit unregister. Unknown board IDs assume a 24 MHz LPC clock, which may be wrong. Direct `inb()` is used outside the mapped range by design.

### Test Signals
Test DMI match/no-match behavior, board ID name and clock-rate mapping, GPIO/I2C IRQ parameter validation and readback mismatch handling, soft I2C detect path, ocores child resources and EEPROM info, watchdog/GPIO child creation, and unknown-board fallback logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/tqmx86.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/twl-core.c -->
## sources/distributed-fs/ceph-client/drivers/mfd/twl-core.c

### Purpose
`twl-core.c` is the central built-in I2C MFD core for TWL4030/TWL5030/TWL6030/TWL6032/TPS659x0 companion PMIC/audio chips. It creates regmaps for multiple I2C slave addresses, maps logical TWL module IDs to slave/base offsets, exports module-relative I2C read/write helpers, initializes clocks and IDCODE state, initializes chip IRQ handling, populates OF child devices, and supports TWL6030-class power-off.

### Important APIs, Types, And Functions
Private state is `struct twl_private`, containing readiness, IDCODE, class ID, module map, and per-slave `struct twl_client` regmaps. Exported functions are `twl_rev()`, `twl_i2c_write()`, `twl_i2c_read()`, `twl_set_regcache_bypass()`, `twl_get_type()`, `twl_get_version()`, and `twl_get_hfclk_rate()`. Major helpers are `twl_get_regmap()`, `twl_read_idcode_register()`, `clocks_init()`, `twl_remove()`, `twl6030_power_off()`, `twl_probe()`, `twl_suspend()`, and `twl_resume()`.

### Control Flow
The built-in I2C driver probes only with an OF node and only one global instance. Probe creates a platform device named `"twl"`, checks I2C functionality, allocates global state, selects TWL4030 or TWL6030 maps/configs from the I2C ID, creates dummy I2C clients for additional slave addresses, initializes each regmap, marks the core ready, programs clock configuration based on the `fck` clock, reads IDCODE on TWL4030-class chips, initializes the appropriate IRQ subsystem if the parent IRQ exists, applies TWL4030 pull-up/SmartReflex register tweaks, creates TWL6030/TWL6032 clock MFD cells and optional power-off callback, and calls `of_platform_populate()`.

### State, Persistence, And Dependencies
Global singleton `twl_priv` gates exported helper availability. Persistent hardware effects include PM master clock boot configuration, IDCODE unlock/relock, TWL4030 pull-up disable, SmartReflex enable, TWL6030 power-off writes, and child-driver register writes through exported helpers. Dependencies include I2C, regmap, clock framework, OF platform population, IRQ subsystems declared in `twl-core.h`, MFD core, and `linux/mfd/twl.h`.

### Integration Points
TWL child drivers use module IDs and exported helpers rather than direct I2C clients. `twl4030-irq.c` and TWL6030 IRQ support are called from here. `twl4030-audio.c` consumes `twl_get_hfclk_rate()` and module I/O helpers. `twl4030-power.c` uses PM master/receiver writes. OF auxdata maps `"ti,twl4030-gpio"` to `twl4030-gpio`.

### Risks
The singleton blocks multiple TWL devices. `twl_get_type()` and `twl_get_version()` assume `twl_priv` is valid, unlike safer read/write helpers. The platform device allocated in probe is not stored for normal successful removal. Probe error paths call `twl_remove()` and unregister the platform device, but successful remove does not unregister the platform device here. Exported read/write helpers return `-EPERM` before ready, so early child use must be ordered correctly.

### Test Signals
Test TWL4030/TWL5031/TWL6030/TWL6032 ID matching, dummy-client creation failure unwinding, exported read/write offset mapping for every module, regcache bypass, IDCODE read/unlock/relock, clock rates for 19.2/26/38.4 MHz and missing clock, IRQ init for both chip classes, OF child population, suspend/resume IRQ disable/enable, and TWL6030 power-off callback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/twl-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/twl-core.h -->
## sources/distributed-fs/ceph-client/drivers/mfd/twl-core.h

### Purpose
`twl-core.h` is the local private interface between `twl-core.c` and TWL IRQ implementation files. It declares initialization and teardown functions for TWL6030 and TWL4030 IRQ support plus TWL4030 chip-specific IRQ table selection.

### Important APIs, Types, And Functions
The declarations are `twl6030_init_irq()`, `twl6030_exit_irq()`, `twl4030_init_irq()`, `twl4030_exit_irq()`, and `twl4030_init_chip_irq()`. The header has a conventional include guard and includes no other headers.

### Control Flow
There is no executable control flow in this header. `twl-core.c` includes it and calls the declared functions during probe and remove according to chip class and IRQ availability.

### State, Persistence, And Dependencies
The header owns no state. It depends on `struct device` being declared before prototypes are consumed by compiling C files through their included Linux headers.

### Integration Points
It keeps TWL IRQ implementation symbols private to the MFD directory rather than exposing them through public `include/linux/mfd/twl.h`. `twl4030-irq.c` implements the TWL4030 declarations; TWL6030 support is expected from a sibling file outside this work item.

### Risks
Because no forward declaration for `struct device` appears in this header, it relies on include order in users. Any new C file including only this header would need to include a device declaration first. The API is narrow and class-specific, so adding new TWL IRQ variants requires updating this private contract.

### Test Signals
Build coverage is the main signal: compile `twl-core.c`, `twl4030-irq.c`, and TWL6030 IRQ implementation together with warnings enabled, and verify prototypes match definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/twl-core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/twl4030-audio.c -->
## sources/distributed-fs/ceph-client/drivers/mfd/twl4030-audio.c

### Purpose
`twl4030-audio.c` is an MFD child driver for the TWL4030 audio/voice block. It configures the audio PLL input frequency, tracks shared audio resources with reference counts, exports resource enable/disable and MCLK query helpers, and creates codec and/or vibra child devices based on platform data or device tree.

### Important APIs, Types, And Functions
State is `struct twl4030_audio`, containing `audio_mclk`, a mutex, resource descriptors for power/APLL, and two child cells. A global `twl4030_audio_dev` lets exported helpers find state. Exported APIs are `twl4030_audio_enable_resource()`, `twl4030_audio_disable_resource()`, and `twl4030_audio_get_mclk()`. Helpers include `twl4030_audio_set_resource()`, `twl4030_audio_get_resource()`, `twl4030_audio_has_codec()`, `twl4030_audio_has_vibra()`, and probe/remove.

### Control Flow
Probe requires platform data or an OF node, allocates state, reads the TWL HFCLK rate via `twl_get_hfclk_rate()`, maps it to an APLL input-frequency value, writes `TWL4030_REG_APLL_CTL`, configures resource register/mask metadata for codec power and APLL, conditionally creates `twl4030-codec` and `twl4030-vibra` cells, stores global device state, and adds children. Resource enable increments a reference count and only sets the hardware bit on the first request. Resource disable decrements and only clears the bit when the count reaches zero.

### State, Persistence, And Dependencies
Resource request counts are in-memory state protected by a mutex. Hardware state is the codec power bit, APLL enable bit, and APLL input-frequency register. Dependencies include the TWL core exported I2C helpers, `twl_get_hfclk_rate()`, MFD core, OF child/property parsing, and `linux/mfd/twl4030-audio.h`.

### Integration Points
Codec and vibra children use the exported resource helpers to coordinate shared power/APLL resources. Device tree can add a `codec` child node and `ti,enable-vibra` property. Platform data can pass codec/vibra sub-platform data into child cells.

### Risks
The exported helpers assume `twl4030_audio_dev` is non-NULL; calls before probe or after remove can dereference NULL. TWL I2C read/write return values are ignored inside resource get/set and APLL setup. Probe stores global state before `mfd_add_devices()` and clears it only if child creation fails. Underflow protection on disable returns `-EPERM`, but unbalanced users can still disturb shared resource availability.

### Test Signals
Test all accepted MCLK rates and invalid rate rejection, codec/vibra child creation from platform data and OF, resource reference counting with multiple users, invalid resource IDs, disable without enable, I2C failure injection around register writes, remove cleanup, and exported helper calls after child driver bind/unbind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/twl4030-audio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/twl4030-irq.c -->
## sources/distributed-fs/ceph-client/drivers/mfd/twl4030-irq.c

### Purpose
`twl4030-irq.c` implements two-stage interrupt support for TWL4030/TWL5030/TPS659x0-class chips. It demultiplexes the primary interrupt handler (PIH) status into secondary interrupt handler (SIH) modules, configures nested Linux IRQs for core and power interrupts, supports SIH mask and edge-trigger programming over sleeping I2C operations, and selects TWL4030 versus TWL5031 SIH tables.

### Important APIs, Types, And Functions
Important structures are `struct sih`, describing hardware SIH modules, and `struct sih_agent`, tracking a Linux nested IRQ bank. Static SIH tables are `sih_modules_twl4030[]` and `sih_modules_twl5031[]`. Main functions are `twl4030_init_chip_irq()`, `twl4030_init_irq()`, `twl4030_sih_setup()`, `handle_twl4030_pih()`, `handle_twl4030_sih()`, `twl4030_init_sih_modules()`, and `twl4030_exit_irq()`. IRQ-chip methods are `twl4030_sih_mask()`, `twl4030_sih_unmask()`, `twl4030_sih_set_type()`, and bus lock/sync-unlock.

### Control Flow
`twl-core.c` first calls `twl4030_init_chip_irq()` to choose the SIH table. `twl4030_init_irq()` allocates descriptors for PIH plus PWR_INT, creates a legacy domain, masks and clears SIH modules, installs dummy handlers for core PIH-level IRQs, sets up the PWR_INT SIH bank, requests a threaded parent IRQ, and enables wake. The parent handler reads PIH ISR and dispatches nested PIH IRQs. For SIH modules, threaded handlers read ISR bytes, acknowledge via clear-on-read where configured, and dispatch nested child IRQs.

### State, Persistence, And Dependencies
Global state includes `irq_line`, `sih_modules`, `nr_sih_modules`, and `twl4030_irq_base`. Each `sih_agent` stores mask bits, pending mask changes, pending edge changes, and a mutex. Persistent hardware effects include SIH mask writes, SIH control COR configuration, EDR edge-trigger writes, and pending interrupt clearing. Dependencies include TWL core I2C helpers, Linux irqdomain/nested IRQ APIs, threaded IRQs, and register/module constants from `linux/mfd/twl.h`.

### Integration Points
The TWL core invokes this file for TWL4030-class parent IRQ setup and teardown. Other TWL child drivers can call `twl4030_sih_setup()` to configure a SIH bank such as GPIO. The initial core setup always configures PWR_INT after the PIH bank.

### Risks
`twl4030_exit_irq()` is effectively unimplemented and logs inability to clean up. `twl4030_sih_setup()` allocates `sih_agent` and `irq_name` without a corresponding teardown path. IRQ descriptor/domain cleanup is incomplete on several failure paths. Edge registers are shared across interrupt lines and are read-modify-written without cross-line coordination. Only line 0 is used (`twl_irq_line`). Some SIH modules such as USB are skipped because they do not follow the standard organization.

### Test Signals
Test TWL4030 and TWL5031 table selection, initial mask/COR/clear writes, parent PIH dispatch for each module bit, PWR_INT nested dispatch, SIH mask/unmask bus sync, rising/falling/both edge programming, invalid trigger rejection, I2C error handling, wake enable, and cleanup/reprobe behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/twl4030-irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/twl4030-power.c -->
## sources/distributed-fs/ceph-client/drivers/mfd/twl4030-power.c

### Purpose
`twl4030-power.c` programs TWL4030 PM master/receiver power scripts and resource configuration. It loads sleep/wakeup/warm-reset scripts into PM memory, maps resources to device groups/types/remap states, supplies several OMAP3 default power configurations from device tree match data, and can install the TWL4030 system power-off callback.

### Important APIs, Types, And Functions
Script-writing helpers are `twl4030_write_script_byte()`, `twl4030_write_script_ins()`, and `twl4030_write_script()`. Sequence config helpers are `twl4030_config_wakeup3_sequence()`, `twl4030_config_wakeup12_sequence()`, `twl4030_config_sleep_sequence()`, and `twl4030_config_warmreset_sequence()`. Resource logic is in `twl4030_configure_resource()`, `twl4030_patch_rconfig()`, and `twl4030_power_configure_resources()`. Public functions are `twl4030_remove_script()` and `twl4030_power_off()`. Probe is `twl4030_power_probe()`.

### Control Flow
Probe requires platform data or an OF node, unlocks PM master protected registers, obtains match data for OF configurations, loads all scripts sequentially starting at `twl4030_start_script_address`, configures resources, optionally verifies/sets `SEQ_OFFSYNC` and assigns `pm_power_off`, then relocks protected registers. Script loading checks memory bounds, writes each instruction as four bytes, and updates sequence-address registers according to script flags. Wakeup12 configuration can clear charger start triggers for known charger quirks or legacy OMAP machines.

### State, Persistence, And Dependencies
Persistent hardware state is central: PM script memory, sequence address registers, P1/P2/P3 software events, transition start masks, resource group/type/remap registers, and power-off/start behavior. Static default OMAP3 script/resource configurations are used as OF match data and may be patched by board-specific resource overrides. Dependencies include TWL core I2C helpers, PM master protected-key protocol, platform data structures from `linux/mfd/twl.h`, OF match data, machine type checks, and global `pm_power_off`.

### Integration Points
This platform driver is populated beneath the TWL core. OF compatibles select generic, reset-only, idle, idle-osc-off, and OMAP3 board quirk configurations. `twl4030_power_off()` is installed when platform data or DT indicates a system power controller and no existing `pm_power_off` is set.

### Risks
The script `order` variable in `load_twl4030_script()` is static, so previous loads can affect later warnings. `twl4030_patch_rconfig()` mutates the common resource config array in place, and OF match data points at static arrays; a board override can permanently modify shared defaults. `twl4030_starton_mask_and_set()` always attempts relock and can mask an earlier unlock error path. Power-off disables start on charger/VBUS before setting DEVOFF, so incorrect wiring/properties can make the board hard to restart. Many paths program protected PM state, making partial failures risky.

### Test Signals
Test script memory bounds, instruction byte ordering and END_OF_SCRIPT linkage, each script flag path, wakeup/sleep/warm-reset sequence-address writes, resource group/type/remap writes, board-config patching side effects, protected unlock/relock failure injection, power-off STARTON mask and DEVOFF writes, OF compatible selection, charger quirk behavior, and repeated probe/remove/reprobe with static configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/twl4030-power.c -->
