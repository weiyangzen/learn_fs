# subset-b-004251 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/wm5110-tables.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/wm5110-tables.c

## Purpose
`wm5110-tables.c` is the data-table companion for the Arizona/WM5110 MFD core. It supplies revision-specific register patches, regmap IRQ-chip descriptors for always-on and main interrupt banks, the large reset-default table, readable/volatile register predicates, ADSP-memory window predicates, and exported I2C/SPI regmap configurations.

## Important APIs, Types, and Functions
- `wm5110_patch(struct arizona *arizona)` selects a `struct reg_sequence` patch using `arizona->rev`: revision 0 uses `wm5110_reva_patch`, revision 1 uses `wm5110_revb_patch`, revision 3 uses `wm5110_revd_patch`, and all other revisions use `wm5110_reve_patch`.
- `wm5110_aod`, `wm5110_irq`, and `wm5110_revd_irq` are exported `struct regmap_irq_chip` instances. The Rev D descriptor expands the main IRQ chip from 5 to 6 status registers and uses V2 masks for several IRQs.
- `wm5110_spi_regmap` and `wm5110_i2c_regmap` are exported `struct regmap_config` objects with 32-bit big-endian register addresses, 16-bit big-endian values, Maple cache, defaults from `wm5110_reg_default`, and `WM5110_MAX_REGISTER` set to `0x4a9fff`. SPI also uses 16 pad bits.
- `wm5110_readable_register()` and `wm5110_volatile_register()` enumerate ordinary readable and volatile Arizona registers, then delegate unknown ranges to `wm5110_is_adsp_memory()`.
- `wm5110_is_rev_b_adsp_memory()` and `wm5110_is_rev_d_adsp_memory()` encode revision-dependent DSP memory ranges for four DSP cores.

## Control Flow
Probe-time Arizona code consumes this file by registering the bus-specific regmap config, applying `wm5110_patch()`, and installing one of the exported IRQ chips. At runtime regmap consults `wm5110_readable_register()` and `wm5110_volatile_register()` before bus access and cache decisions. IRQ dispatch itself is handled by regmap-irq; this file only maps logical `ARIZONA_IRQ_*` lines to status-register offsets and masks.

## State and Persistence
State is almost entirely static, read-only table data. The only persistent behavior comes from regmap cache state initialized from `wm5110_reg_default` and from silicon registers modified by the selected revision patch. ADSP memory ranges are treated as readable and volatile, keeping firmware/DSP memory interactions out of normal cache assumptions.

## Dependencies and Integration Points
The file depends on `linux/mfd/arizona/core.h`, `linux/mfd/arizona/registers.h`, local `arizona.h`, regmap, and regmap-irq. Exports are consumed by Arizona bus/core glue and codec/MFD subdrivers that rely on consistent register defaults, readable/volatile policy, and IRQ numbering.

## Risks and Edge Cases
- Revision mapping is compact: any revision other than 0, 1, or 3 gets the Rev E patch. If a later incompatible revision appears, this fallback could silently apply the wrong patch.
- The copied source contains repeated table entries in several patch arrays and IRQ entries; if intentional they are harmless repeated writes, but if introduced by tree corruption they can hide real table drift.
- Readable/volatile switch lists are large and manual, so omitted registers can fail regmap access or be cached incorrectly.
- ADSP memory predicates are revision-sensitive; wrong `arizona->rev` means wrong memory windows.

## Test Signals
- Build coverage should compile this file with Arizona MFD support and catch malformed initializer tables.
- Probe logs should show successful patch registration on supported revisions and no regmap access-denied errors for expected audio, DSP, IRQ, and AOD registers.
- Runtime tests should exercise main IRQs, AOD wake IRQs, DSP memory reads, and cache reinitialization paths over both I2C and SPI configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/wm5110-tables.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/wm831x-auxadc.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/wm831x-auxadc.c

## Purpose
`wm831x-auxadc.c` implements AUXADC read support for WM831x PMICs. It exposes raw ADC reads and microvolt conversion, choosing an interrupt-driven queued conversion path when a chip IRQ is available and falling back to a synchronous polled conversion path otherwise.

## Important APIs, Types, and Functions
- `struct wm831x_auxadc_req` tracks an input channel, result value, list linkage, and completion for IRQ-backed callers.
- `wm831x_auxadc_read_irq()` queues a request on `wm831x->auxadc_pending`, enables the converter/source, starts conversion at the fastest rate, waits up to 500 ms, removes the request, and returns the completed value or `-ETIMEDOUT`.
- `wm831x_auxadc_irq()` reads `WM831X_AUXADC_DATA`, decodes the source, disables the completed source, powers off the ADC when idle, and completes all pending requests for that input.
- `wm831x_auxadc_read_polled()` serializes access, starts one source, sleeps 20 ms, checks `WM831X_INTERRUPT_STATUS_1`, acknowledges `WM831X_AUXADC_DATA_EINT`, validates source identity, and returns raw data.
- `wm831x_auxadc_read()` and `wm831x_auxadc_read_uv()` are exported helpers; the latter multiplies raw data by 1465.
- `wm831x_auxadc_init()` initializes lock/list state and installs the IRQ or polled read method.

## Control Flow
Initialization sets `wm831x->auxadc_read`. Callers enter through the exported wrapper, which dispatches through that function pointer. In IRQ mode, multiple callers can wait on the same input conversion and all are completed by one IRQ. In polled mode, `auxadc_lock` forces single-source conversion and polling.

## State and Persistence
Persistent driver state lives in `wm831x`: `auxadc_lock`, `auxadc_pending`, `auxadc_active`, and `auxadc_read`. Hardware state is the AUXADC control/source registers and interrupt status. No values are persisted beyond a single conversion request.

## Dependencies and Integration Points
This code depends on WM831x core register helpers, IRQ mapping through `wm831x_irq()`, `request_threaded_irq()`, Linux completions and lists, and PMIC AUXADC register definitions. Consumer subdrivers call the exported raw or microvolt helpers.

## Risks and Edge Cases
- The local source uses `kzalloc_obj(*req)`, which is not a normal kernel allocator macro in many trees; build configuration must provide it or this is a compile failure.
- IRQ mode waits 500 ms but does not check the timeout return directly; timeout is represented by the request's initial `-ETIMEDOUT`.
- IRQ handler ignores errors from cleanup writes while holding the AUXADC lock.
- Polled mode depends on a fixed 20 ms delay and can return `-EBUSY` if conversion timing differs.

## Test Signals
- Compile with WM831x MFD and AUXADC consumers enabled.
- Exercise reads with and without a physical IRQ line and verify raw and microvolt conversion results.
- Stress concurrent reads of the same and different channels to confirm list completion, source disable, and `auxadc_active` behavior.
- Inject regmap read/write failures to verify error propagation and cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/wm831x-auxadc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/wm831x-core.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/wm831x-core.c

## Purpose
`wm831x-core.c` is the central MFD core for WM8310/WM8311/WM8312/WM8320/WM8321/WM8325/WM8326 PMICs. It defines register access policy, exported register helpers, keyed-register locking, child-device tables, OF match data, device initialization, suspend cleanup, and soft-shutdown behavior.

## Important APIs, Types, and Functions
- `wm831x_isinkv_values[]` exports current-sink current values used by multiple child drivers.
- `wm831x_reg_lock()` and `wm831x_reg_unlock()` update `WM831X_SECURITY_KEY` and maintain `wm831x->locked` under `io_lock`.
- `wm831x_reg_readable()`, `wm831x_reg_writeable()`, and `wm831x_reg_volatile()` define regmap access/cache policy. `wm831x_reg_writeable()` also blocks writes to protected registers while locked.
- Exported helpers include `wm831x_reg_read()`, `wm831x_bulk_read()`, `wm831x_reg_write()`, and `wm831x_set_bits()`.
- MFD cell arrays (`wm8310_devs`, `wm8311_devs`, `wm8312_devs`, `wm8320_devs`) describe regulators, GPIO, power, RTC, watchdog, status LEDs, current sinks, touch, backlight, and other children with register and IRQ resources.
- `wm831x_device_init()` validates IDs, identifies variant/revision, applies platform callbacks/default GPIOs, initializes IRQ and AUXADC support, registers child devices, initializes OTP, and runs post-init.
- `wm831x_device_suspend()` acknowledges masked charger IRQs that might otherwise wake immediately.
- `wm831x_device_shutdown()` clears `WM831X_CHIP_ON` when platform data requests soft shutdown.

## Control Flow
Bus drivers allocate `struct wm831x`, initialize regmap, copy platform data, and call `wm831x_device_init()`. The core validates parent/device IDs, reconciles engineering samples and registered type, locks keyed registers, applies platform pre-init and GPIO defaults, initializes IRQ and AUXADC, then adds variant-specific MFD cells. Optional RTC registration depends on `WM831X_XTAL_ENA`; optional backlight depends on platform data. Error paths remove children and tear down IRQs.

## State and Persistence
Persistent state includes `io_lock`, `key_lock`, `locked`, platform data copy, variant feature flags (`num_gpio`, `has_gpio_ena`, `has_cs_sts`, `charger_irq_wake`), IRQ state, AUXADC state, and child platform devices registered through MFD. Hardware persistence is in PMIC registers, especially security key, GPIO defaults, masks, clocks, and power-state registers.

## Dependencies and Integration Points
The file integrates with regmap, MFD core, WM831x IRQ/AUXADC/OTP modules, platform data hooks (`pre_init`, `post_init`, `soft_shutdown`, `gpio_defaults`, `backlight`, `disable_touch`), and child drivers for regulators, GPIO, power, RTC, watchdog, status LEDs, touch, hardware monitor, backup, clock, and current sinks. `wm831x_of_match` is shared by I2C/SPI bus drivers.

## Risks and Edge Cases
- The copied source contains duplicate declarations (`unsigned int val;`, `enum wm831x_parent parent;`) that would be compile errors in a normal C build unless this tree is intentionally non-buildable research input.
- Register access tables are long manual switch statements; missing entries affect regmap behavior broadly.
- `mfd_add_devices()` calls for optional touch devices do not check return values, so touch registration failures are non-fatal and quiet.
- Security-key state must remain synchronized with hardware; direct writes outside the helper can desynchronize `wm831x->locked`.
- Error cleanup calls `mfd_remove_devices()` after some partial-init failures, but OTP sysfs cleanup is not explicitly paired in the visible failure paths after `wm831x_otp_init()`.

## Test Signals
- Build all WM831x variants over both I2C and SPI bus frontends.
- Probe with each supported ID/revision, including engineering-sample ID fallback, and verify expected child devices/resources.
- Validate locked-register writes return `-EPERM` when locked and succeed after unlock.
- Suspend with masked charger IRQ status set and verify the code acknowledges those bits.
- Boot with and without 32.768 kHz crystal and confirm RTC child registration behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/wm831x-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/wm831x-i2c.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/wm831x-i2c.c

## Purpose
`wm831x-i2c.c` is the I2C bus frontend for WM831x PMICs. It matches supported WM831x/WM832x device IDs or OF compatibles, creates the shared `struct wm831x`, initializes an I2C regmap, copies platform data, and delegates all device setup to the WM831x core.

## Important APIs, Types, and Functions
- `wm831x_i2c_probe()` obtains match data, allocates `struct wm831x` with devres, sets client data and type, initializes `devm_regmap_init_i2c()` with `wm831x_regmap_config`, copies `wm831x_pdata`, and calls `wm831x_device_init()`.
- `wm831x_i2c_suspend()` calls `wm831x_device_suspend()`.
- `wm831x_i2c_poweroff()` calls `wm831x_device_shutdown()`.
- `wm831x_i2c_id[]` maps `"wm8310"` through `"wm8326"` names to enum parent IDs.
- `wm831x_i2c_driver` binds name `"wm831x"`, PM ops, OF match table, probe, and ID table.
- `wm831x_i2c_init()` registers the driver at `subsys_initcall()` time.

## Control Flow
Kernel I2C matching triggers probe. Probe validates `i2c_get_match_data()`, creates regmap, copies platform configuration if present, and enters `wm831x_device_init(wm831x, i2c->irq)`. PM callbacks later flow directly into core suspend/shutdown helpers.

## State and Persistence
This file owns no long-lived state beyond devres-managed allocation and client driver data. Persistent PMIC state is managed by the core and children after probe.

## Dependencies and Integration Points
It depends on I2C, OF match data exported by `wm831x-core.c`, regmap I2C bus support, platform data, and the WM831x core initializer. It suppresses bind attributes, preventing manual unbind/rebind through sysfs.

## Risks and Edge Cases
- Probe fails if match data is absent, so every ID/OF path must provide enum data.
- There is no remove path in this file; cleanup relies on devres and lack of manual unbind support.
- Suspend callback is `.suspend`; SPI also wires `.freeze`, so hibernation behavior differs between bus frontends.

## Test Signals
- I2C modalias and OF-compatible matching should both produce nonzero type data.
- Probe should show regmap allocation success and expected MFD children.
- Suspend and poweroff paths should call into core helpers without bus-specific state loss.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/wm831x-i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/wm831x-irq.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/wm831x-irq.c

## Purpose
`wm831x-irq.c` implements nested interrupt-controller support for WM831x PMICs. It maps PMIC interrupt bits to Linux IRQs, handles mask synchronization, supports GPIO IRQ trigger-type configuration, creates an IRQ domain, and services the chip's top-level threaded interrupt.

## Important APIs, Types, and Functions
- `struct wm831x_irq_data` maps each logical IRQ to a primary interrupt bit, secondary status register index, and mask.
- `wm831x_irq_enable()` and `wm831x_irq_disable()` update cached secondary masks.
- `wm831x_irq_sync_unlock()` writes pending GPIO trigger updates and changed masks to hardware under `irq_lock`.
- `wm831x_irq_set_type()` supports GPIO IRQ trigger configuration for GPIO 1-11, tracking level-low/high emulation arrays and deferred register updates.
- `wm831x_irq_thread()` reads `WM831X_SYSTEM_INTERRUPTS`, handles optimized touch IRQs, reads secondary status registers lazily, masks disabled bits, acknowledges handled bits, and dispatches nested IRQs through the domain.
- `wm831x_irq_map()` installs `wm831x_irq_chip` and `handle_edge_irq` for child IRQs.
- `wm831x_irq_init()` masks all secondary sources, allocates legacy or linear domain, configures IRQ output mode, enables wake on parent IRQ, requests the threaded IRQ, and unmasks top-level interrupts.
- `wm831x_irq_exit()` frees the parent IRQ.

## Control Flow
Core init calls `wm831x_irq_init()`. Child MFD resources use logical IRQ numbers, resolved through `wm831x_irq()`. When the physical IRQ fires, the threaded handler reads the primary summary, optionally dispatches touch lines, then iterates descriptors to read only required secondary status registers and dispatch nested IRQs. Mask changes are batched by generic IRQ bus locking and committed on sync unlock.

## State and Persistence
Persistent state includes `irq_lock`, `irq_masks_cur`, `irq_masks_cache`, `gpio_update`, `gpio_level_low/high`, `irq_domain`, and parent IRQ number. Hardware state includes secondary mask registers, `WM831X_IRQ_CONFIG`, top-level mask, secondary status acknowledgements, and GPIO control registers.

## Dependencies and Integration Points
The file integrates with Linux genirq, irqdomain, nested threaded IRQs, WM831x core register helpers, WM831x GPIO register definitions, and MFD child resources. Platform data can request a base IRQ range and CMOS/open-drain output behavior.

## Risks and Edge Cases
- The copied source contains a duplicated `dev_err(` line in `wm831x_irq_thread()` and a duplicated mask initializer for `WM831X_IRQ_HC_DC1`; these should be treated as source-integrity/build risks.
- Level GPIO emulation polls `WM831X_GPIO_LEVEL` in a loop while the level remains active; stuck levels can cause repeated nested dispatch and bus traffic.
- Only GPIO 1-11 support `irq_set_type()` despite the table including GPIO 1-16.
- If parent IRQ request fails after domain creation, the domain is not removed in this file.
- No interrupt line is allowed but limits functionality and forces consumers that require IRQs to degrade.

## Test Signals
- Build with IRQ domain and nested IRQ support.
- Probe with and without `pdata->irq_base` and validate domain mappings.
- Trigger representative charger, RTC, regulator, touch, AUXADC, and GPIO IRQs and verify nested handlers run once per event.
- Test GPIO edge and level configurations, including mask/unmask synchronization.
- Suspend/wake tests should confirm `enable_irq_wake()` behavior and warning-only failure handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/wm831x-irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/wm831x-otp.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/wm831x-otp.c

## Purpose
`wm831x-otp.c` exposes the WM831x one-time-programmed unique ID through sysfs and contributes that ID to kernel randomness during device initialization.

## Important APIs, Types, and Functions
- `WM831X_UNIQUE_ID_LEN` defines a 16-byte ID.
- `wm831x_unique_id_read()` reads eight 16-bit registers starting at `WM831X_UNIQUE_ID_1` and packs them big-endian into a byte buffer.
- `unique_id_show()` reads the ID and formats it as a no-separator hex string with a newline.
- `DEVICE_ATTR_RO(unique_id)` creates a read-only sysfs attribute.
- `wm831x_otp_init()` creates the sysfs file, reads the UUID, and calls `add_device_randomness()` on success.
- `wm831x_otp_exit()` removes the sysfs file.

## Control Flow
The WM831x core calls `wm831x_otp_init()` after child-device registration. Userspace can then read `unique_id`; each read re-fetches the OTP registers. On driver teardown, core code can call `wm831x_otp_exit()` to remove the attribute.

## State and Persistence
The unique ID itself is persistent OTP hardware state. The driver stores no cached copy; it creates only a sysfs attribute and temporarily allocates stack buffers for reads.

## Dependencies and Integration Points
This file depends on WM831x register helpers and OTP register definitions, Linux device attributes, and `add_device_randomness()`. It integrates with the core init/exit lifecycle and exposes a device-level sysfs ABI.

## Risks and Edge Cases
- `unique_id_show()` returns 0 on read failure, making failures look like EOF rather than a negative error.
- `wm831x_otp_init()` logs sysfs creation failure but continues to read UUID; it returns the UUID read status, not the attribute creation status if UUID succeeds.
- No explicit permission or privacy filtering is applied; the hardware unique ID is exposed to userspace.

## Test Signals
- Verify the sysfs `unique_id` file appears after probe and contains 32 hex characters plus newline.
- Inject register read failure and confirm init logs and sysfs-read behavior.
- Confirm entropy contribution path runs once during init when UUID read succeeds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/wm831x-otp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/wm831x-spi.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/wm831x-spi.c

## Purpose
`wm831x-spi.c` is the SPI bus frontend for WM831x PMICs. It performs device matching, allocates the shared WM831x state object, initializes SPI regmap access, copies platform data, and delegates to the WM831x core.

## Important APIs, Types, and Functions
- `wm831x_spi_probe()` gets enum match data, allocates `struct wm831x`, forces `SPI_MODE_0`, initializes `devm_regmap_init_spi()` with `wm831x_regmap_config`, copies platform data, and calls `wm831x_device_init(wm831x, spi->irq)`.
- `wm831x_spi_suspend()` calls `wm831x_device_suspend()`.
- `wm831x_spi_poweroff()` calls `wm831x_device_shutdown()`.
- `wm831x_spi_pm` wires `.freeze`, `.suspend`, and `.poweroff`.
- `wm831x_spi_ids[]` maps supported part names to enum parent IDs.
- `wm831x_spi_driver` binds the `"wm831x"` SPI driver with OF match data from the core.
- `wm831x_spi_init()` registers the driver at `subsys_initcall()`.

## Control Flow
SPI probe sets up bus mode and regmap before entering the common core path. Later suspend/freeze/poweroff callbacks are thin wrappers around core functionality.

## State and Persistence
Only devres-managed allocation, SPI driver data, and `spi->mode` are bus-local. All persistent PMIC, IRQ, AUXADC, and child-device state is established by `wm831x_device_init()`.

## Dependencies and Integration Points
The file depends on SPI, regmap SPI support, OF match data, platform data, and WM831x core APIs. It shares the same `wm831x_regmap_config` as I2C despite transport differences.

## Risks and Edge Cases
- `wm831x_spi_init()` logs registration failure but returns 0 unconditionally, which can hide driver registration failure from initcall status.
- Probe requires valid match data; unsupported IDs fail with `-ENODEV`.
- Forcing `SPI_MODE_0` may override board-provided mode assumptions.

## Test Signals
- Confirm SPI modalias and OF matching provide correct enum data.
- Probe should initialize regmap and create expected MFD children.
- Test suspend, freeze, and poweroff callbacks.
- Verify initcall failure handling in logs if SPI driver registration is forced to fail.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/wm831x-spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/wm8350-core.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/wm8350-core.c

## Purpose
`wm8350-core.c` is the common MFD core for WM8350/WM8351/WM8352 PMICs. It provides exported register helpers, security lock/unlock support, AUXADC reads, IRQ initialization integration, chip identification, platform initialization, and registration of child platform devices.

## Important APIs, Types, and Functions
- Register helpers: `wm8350_clear_bits()`, `wm8350_set_bits()`, `wm8350_reg_read()`, `wm8350_reg_write()`, `wm8350_block_read()`, and `wm8350_block_write()` wrap regmap operations and export symbols.
- `wm8350_reg_lock()` and `wm8350_reg_unlock()` write `WM8350_SECURITY` with lock/unlock keys and track `wm8350->unlocked` under a global `reg_lock_mutex`.
- `wm8350_read_auxadc()` validates channel/scale/vref, enables AUXADC power, programs source/readback options, starts a conversion, waits briefly for `auxadc_done`, reads result, powers down ADC, and returns masked data.
- `wm8350_auxadc_irq()` completes the AUXADC conversion completion.
- `wm8350_client_dev_register()` allocates and registers named child platform devices with the WM8350 object as driver data.
- `wm8350_device_init()` validates chip IDs/revisions, sets PMIC capability limits, initializes AUXADC state and IRQs, requests AUXADC IRQ when available, runs platform init, unmasks system interrupts, and registers codec, GPIO, hwmon, power, RTC, and watchdog children.

## Control Flow
The I2C frontend initializes regmap then calls `wm8350_device_init()`. Core init reads ID/revision registers, rejects unsupported customer IDs and unknown revisions, initializes IRQ/AUXADC infrastructure, allows board-specific setup via `pdata->init`, unmasks top-level interrupts, and registers children. AUXADC reads are synchronous and optionally accelerated by an IRQ completion.

## State and Persistence
Persistent state includes `unlocked`, `auxadc_mutex`, `auxadc_done`, `irq_base`, `chip_irq`, revision/capability fields under `pmic` and `power`, and child platform-device pointers. Hardware state includes security lock, interrupt masks, AUXADC power/control/readback registers, and platform-initialized PMIC registers.

## Dependencies and Integration Points
The core depends on regmap, platform devices, WM8350 headers for audio/comparator/GPIO/PMIC/RTC/supply/watchdog, the IRQ module, and platform data. Child drivers bind to manually registered platform devices rather than `mfd_add_devices()`.

## Risks and Edge Cases
- The copied source contains a duplicated `platform_device_alloc()` assignment in `wm8350_client_dev_register()`, leaking the first allocation and signaling possible source corruption.
- `wm8350_reg_read()` returns `data` even after read failure; `data` may be undefined if regmap_read fails.
- AUXADC waits only 5 ms and then checks the poll bit; slow conversions log a timeout and return zero-masked result.
- Child device registration failures are non-fatal, so the PMIC can probe with missing subdevices.
- IRQ init returning 0 when IRQ allocation fails means the core can continue without nested IRQs.

## Test Signals
- Probe WM8350/WM8351/WM8352 supported revision combinations and verify unsupported IDs fail.
- Validate child platform devices bind and expose expected functions.
- Exercise register lock/unlock around GPIO and charger protected registers.
- Test AUXADC reads with a working IRQ, without IRQ, and with forced conversion timeout.
- Inject regmap failures to inspect error propagation from read/write helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/wm8350-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/wm8350-gpio.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/wm8350-gpio.c

## Purpose
`wm8350-gpio.c` provides an exported helper for configuring WM8350 GPIO pins. It programs direction, function mux, polarity/type, pull-up/pull-down state, interrupt inversion, and debounce settings.

## Important APIs, Types, and Functions
- `gpio_set_dir()` unlocks protected registers, updates `WM8350_GPIO_CONFIGURATION_I_O`, then relocks.
- `wm8350_gpio_set_debounce()` updates `WM8350_GPIO_DEBOUNCE`.
- `gpio_set_func()` unlocks protected registers and writes one of `WM8350_GPIO_FUNCTION_SELECT_1` through `_4`, packing a 4-bit function for GPIO 0-12.
- `gpio_set_pull_up()` and `gpio_set_pull_down()` update pull control registers.
- `gpio_set_polarity()` updates `WM8350_GPIO_PIN_POLARITY_TYPE`.
- `gpio_set_invert()` updates `WM8350_GPIO_INT_MODE`.
- `wm8350_gpio_config()` sequences pull selection, invert, polarity, debounce, direction, and function selection, returning `-EIO` on intermediate failures.

## Control Flow
Callers invoke `wm8350_gpio_config()` with all desired settings. The helper first ensures pull-up and pull-down are not both active, then applies interrupt/polarity/debounce/direction, and finally programs the mux function. Protected direction/function operations temporarily unlock and relock the PMIC.

## State and Persistence
There is no local software state. Configuration persists in WM8350 GPIO registers until changed or reset. Security lock state is modified through core lock helpers.

## Dependencies and Integration Points
The file depends on WM8350 core register helpers, security-lock helpers, GPIO constants, and PMIC definitions. It is exported for board code or child GPIO-related drivers that configure pin muxing.

## Risks and Edge Cases
- `wm8350_gpio_config()` does not validate the GPIO number up front; invalid numbers can shift beyond intended register bits in several helpers before `gpio_set_func()` returns `-EINVAL`.
- Unlock/lock return values are not checked in `gpio_set_dir()` or `gpio_set_func()`, so protected-write failures can be masked.
- If a later step fails, earlier GPIO settings are not rolled back.
- Function mux supports only GPIO 0-12 in this code.

## Test Signals
- Configure each supported GPIO function and verify expected register fields.
- Test pull none/up/down transitions to confirm mutual exclusion.
- Exercise invalid GPIO/function inputs and ensure callers handle `-EIO` or `-EINVAL`-derived failures.
- Verify protected-register lock state is restored after direction/function updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/wm8350-gpio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/wm8350-i2c.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/wm8350-i2c.c

## Purpose
`wm8350-i2c.c` is the I2C bus frontend for WM8350-family PMICs. It allocates the core state, creates the regmap over I2C, records driver data, and calls the common WM8350 initializer.

## Important APIs, Types, and Functions
- `wm8350_i2c_probe()` allocates `struct wm8350`, initializes `devm_regmap_init_i2c()` with `wm8350_regmap`, sets client data and `wm8350->dev`, then calls `wm8350_device_init(wm8350, i2c->irq, pdata)`.
- `wm8350_i2c_id[]` lists `"wm8350"`, `"wm8351"`, and `"wm8352"`.
- `wm8350_i2c_driver` binds driver name `"wm8350"` with suppressed bind attributes.
- `wm8350_i2c_init()` registers the I2C driver at `subsys_initcall()` time so consumers can complete boot.

## Control Flow
I2C probe performs only bus setup and immediately enters the core device-init path. There is no bus-local PM callback or remove callback in this file.

## State and Persistence
Bus-local state is limited to devres-managed `struct wm8350`, regmap, and I2C client data. Core and child drivers own all persistent PMIC state after initialization.

## Dependencies and Integration Points
It depends on the I2C subsystem, regmap I2C support, WM8350 core/regmap exports, and optional platform data. Suppressed bind attributes prevent manual sysfs unbind/rebind.

## Risks and Edge Cases
- No OF match table is present in this file, so binding relies on I2C IDs/board data in this source version.
- No explicit remove path means teardown depends on driver model/devres assumptions and suppressed manual unbind.
- Probe failure in core init must leave no child devices behind; that is handled mostly by core paths.

## Test Signals
- I2C device IDs should trigger probe for all three names.
- Regmap allocation failures should return the underlying error and log.
- Successful probe should show WM8350 core identification and child platform device registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/wm8350-i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/wm8350-irq.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/wm8350-irq.c

## Purpose
`wm8350-irq.c` implements nested IRQ support for WM8350-family PMICs. It maps primary and secondary PMIC interrupt status bits onto Linux IRQ descriptors, handles mask updates, configures parent IRQ polarity, and dispatches nested child interrupts from a threaded parent handler.

## Important APIs, Types, and Functions
- `struct wm8350_irq_data` maps a child IRQ to primary summary bit, secondary register offset, mask, and a `primary_only` flag that is present in data but not used by the handler.
- `wm8350_irq()` reads `WM8350_SYSTEM_INTERRUPTS` and its mask, lazily reads needed secondary status registers, applies cached masks, and dispatches nested IRQs using `wm8350->irq_base + i`.
- `wm8350_irq_enable()` and `wm8350_irq_disable()` update `wm8350->irq_masks`.
- `wm8350_irq_sync_unlock()` writes all cached masks back to `WM8350_INT_STATUS_1_MASK + i` under `irq_lock`.
- `wm8350_irq_init()` masks top-level and secondary sources, allocates IRQ descriptors, configures parent IRQ polarity from platform data, installs nested edge handlers, requests the threaded parent IRQ, and unmasks top-level interrupts.
- `wm8350_irq_exit()` frees the parent IRQ.

## Control Flow
The core calls `wm8350_irq_init()` during probe. If no parent IRQ exists, initialization returns success with a warning and no nested IRQs. With a parent IRQ, all sources are masked, child descriptors are allocated and configured, the physical IRQ is requested, then top-level interrupts are enabled. The threaded handler dispatches child IRQs for unmasked secondary status bits.

## State and Persistence
Persistent state includes `irq_lock`, `irq_masks[]`, `chip_irq`, and `irq_base`. Hardware state includes system interrupt masks, secondary interrupt masks, parent IRQ polarity, and clear-on-read/secondary status registers.

## Dependencies and Integration Points
The file integrates with Linux genirq nested-thread APIs, WM8350 core register helpers, platform IRQ base/polarity data, and child drivers that request IRQs by offsets from `wm8350->irq_base`.

## Risks and Edge Cases
- `primary_only` is defined in descriptors but ignored by dispatch; primary-only interrupts still index and read `sub_reg[data->reg]`.
- If `irq_alloc_descs()` fails, the function logs and returns 0, leaving the device probed without child IRQs.
- The copied source includes a duplicated `.primary = WM8350_CODEC_INT` line in one descriptor, indicating table integrity should be checked.
- `wm8350_irq_exit()` calls `free_irq()` unconditionally on `chip_irq`; no-IRQ init paths should avoid calling it or ensure `chip_irq` is valid.
- Mask sync writes all mask registers every unlock rather than only changed ones.

## Test Signals
- Probe with no IRQ, low-trigger IRQ, and high-trigger IRQ platform data.
- Verify child IRQ descriptor allocation and nested handler installation across the full descriptor table.
- Trigger charger, RTC, AUXADC, GPIO, comparator, codec, UV, and OC interrupts and check nested dispatch.
- Force `irq_alloc_descs()` or parent `request_threaded_irq()` failure and confirm caller behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/wm8350-irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/wm8350-regmap.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/wm8350-regmap.c

## Purpose
`wm8350-regmap.c` contains the WM8350 register access policy table and exported `regmap_config`. It tells regmap which registers/bits are readable, writable, volatile, and precious, including extra write protection for locked GPIO function and charger-control registers.

## Important APIs, Types, and Functions
- `struct wm8350_reg_access` stores per-register readable, writable, and volatile bit masks.
- `wm8350_reg_io_map[]` is a 256-entry table for registers R0-R255.
- `wm8350_readable()` returns the readable mask as a boolean access decision.
- `wm8350_writeable()` blocks protected GPIO function-select and battery charger control registers when `wm8350->unlocked` is false, otherwise returns the writable mask.
- `wm8350_volatile()` returns the volatile mask as a boolean.
- `wm8350_precious()` marks system and interrupt status registers precious so debug/cache paths do not casually read clear-on-read state.
- `wm8350_regmap` configures 8-bit register addresses, 16-bit values, Maple cache, max register, and access callbacks.

## Control Flow
The I2C frontend passes `wm8350_regmap` to `devm_regmap_init_i2c()`. All later core and child register accesses flow through regmap, which invokes these callbacks to validate access and decide cache behavior. The writeability callback observes security-lock state maintained by `wm8350-core.c`.

## State and Persistence
The access table is static. Dynamic behavior depends on `wm8350->unlocked`, which controls whether protected registers are writeable. Hardware state is not modified here, but regmap cache behavior is shaped by volatile and precious declarations.

## Dependencies and Integration Points
The file depends on WM8350 core definitions for register numbers and `struct wm8350`. It integrates tightly with core security lock/unlock helpers, GPIO configuration, charger controls, IRQ handling, and regmap cache semantics.

## Risks and Edge Cases
- Access callbacks index `wm8350_reg_io_map[reg]` directly; regmap must not call them with an out-of-range register.
- Returning bit masks as booleans loses bit-granular detail at regmap's callback boundary, so partial-bit policy is advisory only unless higher layers enforce masks.
- If `wm8350->unlocked` gets out of sync with the hardware lock, regmap writeability decisions diverge from actual PMIC behavior.
- Precious interrupt registers must stay accurate because accidental reads can clear interrupt state.

## Test Signals
- Regmap debugfs/read-write tests should confirm invalid/unreadable registers are blocked and volatile registers bypass stale cache.
- Lock and unlock tests should verify protected GPIO function and charger registers transition writeability.
- IRQ tests should confirm precious status registers are not consumed by diagnostic reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/wm8350-regmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/wm8400-core.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/wm8400-core.c

## Purpose
`wm8400-core.c` is the core and I2C frontend for the WM8400 device. It validates chip identity, sets up regmap caching, registers the codec child device, runs optional platform initialization, and provides a helper to reset the codec register cache.

## Important APIs, Types, and Functions
- `wm8400_volatile()` marks interrupt status, interrupt levels, and shutdown reason as volatile.
- `wm8400_register_codec()` registers one devm-managed MFD child named `"wm8400-codec"` with the core data as platform data.
- `wm8400_init()` reads `WM8400_RESET_ID`, verifies `0x6172`, reads revision from `WM8400_ID`, registers the codec, and invokes `pdata->platform_init` if supplied.
- `wm8400_regmap_config` uses 8-bit register addresses, 16-bit values, max register `WM8400_REGISTER_COUNT - 1`, Maple cache, and the volatile callback.
- `wm8400_reset_codec_reg_cache()` exports a cache reinitialization helper for codec-side reset handling.
- `wm8400_i2c_probe()` allocates `struct wm8400`, initializes I2C regmap, stores client data, and calls `wm8400_init()`.
- `wm8400_driver_init()` registers the I2C driver under `subsys_initcall()` when I2C is enabled.

## Control Flow
I2C probe sets up state/regmap and calls generic init. Generic init validates the hardware ID before registering the codec child, then optionally runs board platform initialization. Codec code can later call `wm8400_reset_codec_reg_cache()` to rebuild cache defaults after reset-like events.

## State and Persistence
Persistent state is the devres-managed `struct wm8400`, regmap cache, and registered codec child. Hardware identity/revision is read-only. Platform initialization may program board-specific persistent register state.

## Dependencies and Integration Points
This file depends on I2C, regmap, MFD core, WM8400 private/audio headers, and optional platform data. It exposes only the codec child in this source, so audio integration is the main consumer.

## Risks and Edge Cases
- If no platform initialization is supplied, the driver only warns and continues; board-required setup may be missing.
- There is no explicit remove path; devm-managed MFD registration and regmap allocation handle normal device lifetime.
- Only I2C support is compiled in this file despite the generic-init comment mentioning SPI.
- Cache reinitialization must use the same config or codec/cache state can diverge.

## Test Signals
- Probe should reject non-`0x6172` reset IDs and report revision for valid hardware.
- Codec child registration should produce a `"wm8400-codec"` device.
- Platform-init success/failure paths should be tested.
- After codec reset/cache reset, regmap reads should reflect default/cache policy and volatile status should remain uncached.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/wm8400-core.c -->
