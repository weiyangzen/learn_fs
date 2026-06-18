# subset-b-003904 research

Grouped research for the requested source set. Each section preserves the original source path and is bounded for automated reconciliation.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/temperature/mlx90614.c -->
# sources/distributed-fs/ceph-client/drivers/iio/temperature/mlx90614.c

Purpose: IIO direct-mode I2C driver for Melexis MLX90614 and MLX90615 contactless IR thermopile sensors. It exposes ambient and object temperature channels, object emissivity calibration, and low-pass filter frequency controls.

Important APIs/types/functions: `struct mlx_chip_info` abstracts MLX90614 vs MLX90615 command layout, emissivity limits, filter masks, and wake timings. `struct mlx90614_data` stores the I2C client, EEPROM mutex, optional wakeup GPIO, chip info, and post-wakeup readiness timestamp. Core entry points are `mlx90614_read_raw()`, `mlx90614_write_raw()`, `mlx90614_read_avail()`, `mlx90614_probe()`, and PM callbacks. `mlx90614_write_word()` performs PEC-protected EEPROM erase/write cycles using `i2c_smbus_xfer()`. `mlx90614_iir_search()` validates and programs IIR/FIR config bits.

Control flow: probe checks SMBus word support, allocates an IIO device, resolves chip match data, optionally acquires a wakeup GPIO, wakes the chip, detects single vs dual IR object sensors, and registers two or three channels. Temperature reads select the correct RAM command, resume runtime PM if needed, read a word, reject the MSB error flag, and return raw units with shared offset/scale. Emissivity and filter writes power the device, lock EEPROM access, write erased-then-programmed EEPROM words, and release runtime PM. Runtime suspend issues the sleep command; runtime resume toggles the wakeup GPIO while holding the I2C root adapter lock.

State and persistence: emissivity and filter settings are written to sensor EEPROM and survive resets. Runtime PM autosleeps after `MLX90614_AUTOSLEEP_DELAY` only when wakeup GPIO support exists. `ready_timestamp` protects the first measurement after wake. The driver has no buffered scan path and no filesystem persistence.

Dependencies/integration: depends on I2C SMBus word operations, optional SMBus write-byte for sleep, optional `wakeup` GPIO, IIO direct mode/sysfs, and runtime PM. Device binding uses I2C IDs and OF compatibles `melexis,mlx90614` and `melexis,mlx90615`.

Risks: EEPROM writes require PEC for writes but not reads, so the driver bypasses normal client PEC flags; regressions here can corrupt calibration/configuration. Wakeup toggles the bus line and locks the adapter, so bad GPIO wiring can disturb other clients. Filter index math differs by chip and MLX90615 forbids index zero. MLX90614 dual-channel detection is configuration-register dependent.

Test signals: compile with the driver enabled, probe against both compatibles, verify sysfs raw/scale/offset/emissivity/filter attributes, test runtime autosuspend/resume with and without wakeup GPIO, and confirm EEPROM writes survive reprobe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/temperature/mlx90614.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/temperature/mlx90632.c -->
# sources/distributed-fs/ceph-client/drivers/iio/temperature/mlx90632.c

Purpose: IIO direct-mode I2C driver for the Melexis MLX90632 IR temperature sensor. It reports processed ambient/object temperatures and supports emissivity, reflected/object ambient calibration, sampling frequency discovery, measurement type switching, regulator control, and runtime PM.

Important APIs/types/functions: `struct mlx90632_data` stores regmap, regulator, emissivity, measurement type, object ambient temperature, power status, and interaction timestamp. The driver uses a 16-bit big-endian regmap with volatile/read/write access tables. Main paths are `mlx90632_read_raw()`, `mlx90632_write_raw()`, `mlx90632_calc_object_dsp105()`, `mlx90632_calc_ambient_dsp105()`, `mlx90632_read_all_channel()`, `mlx90632_read_all_channel_extended()`, `mlx90632_set_meas_type()`, `mlx90632_wakeup()`, and PM callbacks.

Control flow: probe creates the regmap, enables the `vdd` regulator, wakes the chip into continuous mode, registers sleep cleanup, reads EEPROM version, chooses medical/consumer/extended behavior, initializes emissivity and reflected ambient defaults, enables runtime autosuspend, and registers two IIO temperature channels. Reads resume runtime PM, optionally switch from sleep-step to continuous mode if accesses are close together, collect a consistent dataset under mutex, read calibration coefficients from EEPROM, run fixed-point preprocessing and iterative Stefan-Boltzmann style calculations, and return processed milli-C values. Extended object reads switch measurement type and poll for cycle 19 before using extended RAM result locations.

State and persistence: emissivity and object ambient calibration are RAM-only driver state exposed through IIO write_raw and reset on reprobe. EEPROM calibration and measurement definitions are read from the sensor. `mtyp`, `powerstatus`, and `interaction_ts` govern power/performance behavior. Regmap cache is marked dirty and synchronized around suspend/resume.

Dependencies/integration: depends on I2C regmap, regulator framework, runtime PM, IIO direct mode, math64 helpers, and `read_poll_timeout()`/`regmap_read_poll_timeout()`. OF compatible is `melexis,mlx90632`.

Risks: fixed-point math uses large intermediate values and many shifts/divisions; overflow or sign-extension mistakes affect temperature accuracy. `pm_runtime_get_sync()` return handling is minimal. The normal measurement polling predicate waits on `DATA_RDY` clearing after explicitly clearing it, so timing regressions are subtle. Changing measurement type resets the chip and must restore prior power mode. Extended-mode thresholds and RAM channel selection are easy to break.

Test signals: build with regmap and PM enabled, validate version rejection paths, compare ambient/object output against known calibration vectors or hardware, test rapid reads vs slow reads for continuous/sleep-step transitions, verify runtime/system suspend resumes with regcache sync, and inspect sampling frequency availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/temperature/mlx90632.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/temperature/mlx90635.c -->
# sources/distributed-fs/ceph-client/drivers/iio/temperature/mlx90635.c

Purpose: IIO direct-mode I2C driver for the Melexis MLX90635 contactless IR sensor. It provides processed ambient/object temperatures, emissivity calibration, selectable sample frequency, EEPROM coefficient caching, regulator management, and runtime PM.

Important APIs/types/functions: `struct mlx90635_data` holds the I2C client, register regmap, EEPROM regmap, mutex, emissivity, regulator, power status, and interaction timestamp. Important routines include `mlx90635_read_raw()`, `mlx90635_write_raw()`, `mlx90635_read_ee_ambient()`, `mlx90635_read_ee_object()`, `mlx90635_read_all_channel()`, `mlx90635_calc_ambient()`, `mlx90635_calc_object()`, `mlx90635_wakeup()`, and `mlx90635_pm_*()`.

Control flow: probe initializes separate regmaps for volatile registers and EEPROM, enables `vdd`, wakes the sensor, activates and caches EEPROM coefficients, validates DSP version bits, initializes emissivity, enables runtime autosuspend, and registers ambient/object temperature channels. Reads resume the device, use interaction timing to select continuous mode for rapid access, optionally trigger a burst in sleep-step mode, read result registers under mutex, combine calibration coefficients with raw PTAT/IR values using fixed-point math, and return processed milli-C. Sample-frequency writes map requested IIO values to refresh-rate bits in `CTRL1`.

State and persistence: EEPROM is read into a cache and then made cache-only; calibration coefficients are sensor persistent, while emissivity is driver RAM state. `powerstatus` tracks sleep-step vs continuous and is updated only after successful register writes. Runtime/system suspend moves the device to sleep-step and may disable the regulator; resume re-enables power and refills the EEPROM cache.

Dependencies/integration: uses I2C regmap, regulator consumer API, runtime PM, IIO direct mode, math64, and OF/I2C matching for `melexis,mlx90635`.

Risks: the EEPROM cache is central; stale or failed cache synchronization leads to incorrect processed temperatures. Fixed-point fourth-root math and coefficient scaling are overflow-sensitive. `pm_runtime_get_sync()` return is not checked before accesses. The write to start burst measurement uses mask/value composition that must match regmap bit semantics. Sample-frequency writes do not explicitly take the measurement mutex.

Test signals: probe with valid and invalid DSP EEPROM values, check EEPROM cache refill on resume, compare processed temperatures to datasheet vectors/hardware, write each advertised sample frequency and read it back, test runtime autosuspend transitions, and run sparse/build coverage for regmap access tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/temperature/mlx90635.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/temperature/tmp006.c -->
# sources/distributed-fs/ceph-client/drivers/iio/temperature/tmp006.c

Purpose: IIO driver for TI TMP006 IR thermopile sensors. It exposes thermopile voltage, ambient temperature, sampling frequency control, optional data-ready trigger, and triggered-buffer sampling.

Important APIs/types/functions: `struct tmp006_data` stores the I2C client, cached config register, and optional data-ready trigger. Key functions are `tmp006_read_measurement()`, `tmp006_read_raw()`, `tmp006_write_raw()`, `tmp006_trigger_handler()`, `tmp006_set_trigger_state()`, `tmp006_probe()`, and suspend/resume helpers.

Control flow: probe verifies SMBus word support and manufacturer/device IDs, reads and caches CONFIG, powers the sensor if needed, registers cleanup, optionally creates an IIO trigger from `client->irq`, installs the generic data-ready IRQ poller, sets up a triggered buffer, and registers the IIO device. Direct raw reads claim direct mode, poll CONFIG.DRDY up to 50 times, then read voltage or ambient registers. Buffer handler reads both channels and pushes a timestamped scan. Sampling-frequency writes update conversion-rate bits in CONFIG.

State and persistence: the cached `config` mirrors conversion-rate, mode, and data-ready enable bits. Powerdown cleanup and PM suspend clear mode bits; resume restores active mode using cached config. No persistent writes are performed.

Dependencies/integration: depends on I2C SMBus word transactions, IIO direct mode, IIO triggers, `devm_iio_triggered_buffer_setup()`, and optional platform IRQ wiring.

Risks: direct reads can block for up to about five seconds while polling data-ready. Trigger-buffer reads use `i2c_smbus_read_word_data()` while direct paths use swapped reads, so endian expectations must be reviewed carefully. CONFIG cache updates are not mutex-protected. IRQ trigger registration is not devm-managed for the trigger object after explicit register, so teardown order relies on devm allocations and parent lifetime.

Test signals: verify ID detection, read both raw channels and scale, write all advertised sampling frequencies, test direct read while buffer is active for `-EBUSY`, exercise IRQ-triggered buffer capture, and run suspend/resume with CONFIG state checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/temperature/tmp006.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/temperature/tmp007.c -->
# sources/distributed-fs/ceph-client/drivers/iio/temperature/tmp007.c

Purpose: IIO direct-mode driver for TI TMP007 IR thermopile sensors with integrated object-temperature math. It exposes ambient/object raw temperatures, scale, sampling frequency, and threshold events for high/low object and die temperature limits.

Important APIs/types/functions: `struct tmp007_data` holds client, mutex, cached config, and cached status mask. Main functions are `tmp007_read_temperature()`, `tmp007_read_raw()`, `tmp007_write_raw()`, `tmp007_interrupt_handler()`, event config/value callbacks, `tmp007_probe()`, and PM callbacks.

Control flow: probe validates SMBus support and device IDs, enables conversion, ALERT, and transient correction bits, registers powerdown cleanup, enables all relevant threshold mask bits, optionally requests a falling-edge threaded IRQ, and registers the IIO device. Object raw reads poll conversion-ready/data-valid status before reading object temperature; ambient reads use the die register directly. Event IRQ reads status and pushes IIO threshold events by channel and direction. Event config and threshold callbacks update status mask and high/low limit registers.

State and persistence: `config` and `status_mask` mirror hardware registers and are restored/used across PM paths. Threshold registers are device state and can persist only as long as chip power/register retention allows. No driver filesystem state is stored.

Dependencies/integration: depends on I2C SMBus word operations, IIO events/sysfs, optional IRQ, and simple PM sleep ops. OF compatible is `ti,tmp007`.

Risks: object reads can block up to about five seconds while polling. The data-valid predicate is easy to misread because it waits for conversion ready and data-valid bit clear. Event mask writes take a mutex only around the read, not the following write. Threshold write ignores `val2` and supports integer 0.5 C units via bit shift. IRQ handler returns `IRQ_NONE` for reads without event bits, which can expose noisy interrupt wiring.

Test signals: validate ID probe, read both temperature channels and sampling frequency, write sampling frequencies, configure threshold enables and values, simulate or trigger all four event bits, and suspend/resume to confirm conversion enable restoration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/temperature/tmp007.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/temperature/tmp117.c -->
# sources/distributed-fs/ceph-client/drivers/iio/temperature/tmp117.c

Purpose: IIO direct-mode I2C driver for TI TMP116/TMP117 digital temperature sensors. TMP117 exposes temperature offset calibration; TMP116 exposes raw temperature and scale only.

Important APIs/types/functions: `struct tmp117_data` stores the client and cached calibration bias. `struct tmp11x_info` selects name/channel table. Core functions are `tmp117_read_raw()`, `tmp117_write_raw()`, and `tmp117_probe()`.

Control flow: probe checks SMBus word support, enables the `vcc` regulator, waits for startup, reads the device ID, selects TMP116/TMP117 channel info from hardware ID or compatible fallback, allocates the IIO device, and registers it. Reads return signed raw temperature, calibration-bias register, or fixed scale derived from 7.8125 mC LSB. Writes clamp calibration bias to s16, skip unchanged values, cache it, and write TMP117 temperature-offset register.

State and persistence: calibration bias is cached in driver RAM and written to the sensor offset register. Power is enabled through a devm regulator helper. There are no explicit PM callbacks or buffered state.

Dependencies/integration: I2C SMBus word data, regulator framework, device properties/OF match data, and IIO direct mode. Compatibles are `ti,tmp116` and `ti,tmp117`.

Risks: if hardware ID is unknown, fallback match data may expose the wrong channel capabilities. Cached `calibbias` starts at zero and may not reflect pre-existing offset until read. The driver does not serialize offset writes, which is acceptable for simple direct mode but relevant under concurrent sysfs access.

Test signals: probe both IDs, test unknown-ID fallback with compatible data, read raw/scale, read/write TMP117 calibbias including clamp edges, and verify regulator-enable startup delay.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/temperature/tmp117.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/temperature/tsys01.c -->
# sources/distributed-fs/ceph-client/drivers/iio/temperature/tsys01.c

Purpose: IIO driver for Measurement Specialties TSYS01 temperature sensor. It reads PROM coefficients, performs conversion, and exposes processed temperature in milli-C.

Important APIs/types/functions: `struct tsys01_dev` stores client pointer, conversion mutex, transport callbacks, and PROM coefficients. Main functions are `tsys01_read_temperature()`, `tsys01_read_raw()`, `tsys01_crc_valid()`, `tsys01_read_prom()`, `tsys01_probe()`, and `tsys01_i2c_probe()`.

Control flow: I2C probe verifies required SMBus/I2C block functionality, allocates the IIO device, binds common Measurement Specialties helper callbacks, resets the chip, reads eight PROM words, validates CRC, and registers one processed temperature channel. Reads lock during conversion, call the common convert-and-read helper with conversion/read commands and delay, shift the ADC result, run the polynomial coefficient algorithm, and return milli-C.

State and persistence: PROM coefficients are cached in `prom[]` for later calculations. There is no writable configuration or PM state. The only persistent data is factory PROM on the sensor.

Dependencies/integration: depends on `../common/ms_sensors/ms_sensors_i2c.h` helpers and imports namespace `IIO_MEAS_SPEC_SENSORS`. Uses IIO direct mode and I2C client matching/OF compatible `meas,tsys01`.

Risks: `tsys01_crc_valid()` sums `n_prom[0]` repeatedly rather than each PROM word, which looks suspicious and can reject or accept devices incorrectly. The polynomial uses large signed intermediate values and depends on exact scaling. Reads block for conversion delay under mutex.

Test signals: hardware probe should log PROM coefficients, CRC failure should reject probe, processed temperature should match datasheet examples, and conversion helper error propagation should be validated.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/temperature/tsys01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/temperature/tsys02d.c -->
# sources/distributed-fs/ceph-client/drivers/iio/temperature/tsys02d.c

Purpose: IIO direct-mode driver for Measurement Specialties TSYS02D temperature sensors. It exposes processed temperature, sampling-frequency/resolution control, and a battery-low sysfs attribute.

Important APIs/types/functions: Uses common `struct ms_ht_dev` from Measurement Specialties helpers. Main functions are `tsys02d_read_raw()`, `tsys02d_write_raw()`, `tsys02_read_battery_low()`, and `tsys02d_probe()`.

Control flow: probe checks I2C capabilities, allocates IIO device/private state, initializes resolution index and mutex, resets the sensor, reads and logs serial number, and registers a single temperature channel. Processed temperature reads delegate to `ms_sensors_ht_read_temperature()`. Sampling-frequency writes map 20/40/70/140 Hz-style values to resolution index and call `ms_sensors_write_resolution()` under mutex.

State and persistence: `res_index` tracks current resolution/sampling setting in RAM and hardware. Serial number is read once for logging. No persistent driver storage exists.

Dependencies/integration: depends on Measurement Specialties I2C helpers, IIO sysfs attributes, and namespace `IIO_MEAS_SPEC_SENSORS`. Device IDs match `tsys02d`.

Risks: sampling-frequency labels are tightly coupled to helper resolution indexes; changing one without the other breaks user ABI. The driver has no OF table here. Battery-low output fully depends on helper semantics.

Test signals: probe/reset/read-serial success, processed temperature reads, valid/invalid sampling-frequency writes, `sampling_frequency_available`, and `battery_low` sysfs output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/temperature/tsys02d.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/test/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/iio/test/Kconfig

Purpose: Kconfig menu entries for IIO unit tests covering gain-time-scale helpers, rescale conversion functions, formatting functions, and multiply helpers.

Important APIs/types/functions: Defines `IIO_GTS_KUNIT_TEST`, `IIO_RESCALE_KUNIT_TEST`, `IIO_FORMAT_KUNIT_TEST`, and `IIO_MULTIPLY_KUNIT_TEST`. Each is tristate, depends on KUnit, defaults to `KUNIT_ALL_TESTS`, and selects or depends on the helper code it tests.

Control flow: no runtime flow; it controls build inclusion. Entries are intended to remain alphabetical, though the current order places RESCALE before FORMAT/MULTIPLY after GTS.

State and persistence: Kconfig selections persist only in kernel build configuration.

Dependencies/integration: integrates with the kernel KUnit framework and the IIO test Makefile. `IIO_GTS_KUNIT_TEST` selects `IIO_GTS_HELPER`; `IIO_RESCALE_KUNIT_TEST` depends on `IIO_RESCALE`.

Risks: dependency mistakes can build tests without the target helper or hide tests from `KUNIT_ALL_TESTS`. Ordering comments are easy to violate when new tests are added.

Test signals: `kunit.py run` or equivalent configs should list the four suites when enabled; all options should build as built-in or module according to tristate selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/test/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/test/Makefile -->
# sources/distributed-fs/ceph-client/drivers/iio/test/Makefile

Purpose: Builds IIO KUnit test objects according to the corresponding Kconfig symbols.

Important APIs/types/functions: Maps `CONFIG_IIO_RESCALE_KUNIT_TEST`, `CONFIG_IIO_FORMAT_KUNIT_TEST`, `CONFIG_IIO_GTS_KUNIT_TEST`, and `CONFIG_IIO_MULTIPLY_KUNIT_TEST` to `iio-test-*.o`. Adds `$(DISABLE_STRUCTLEAK_PLUGIN)` to `iio-test-format.o`.

Control flow: standard kbuild object selection; no runtime logic.

State and persistence: build-system only.

Dependencies/integration: integrates with Kconfig in the same directory and kbuild/KUnit module or built-in test execution.

Risks: object ordering does not match the "alphabetical" comment. Missing CFLAGS for other tests may matter if compiler plugins interfere with stack buffers, but only format currently opts out.

Test signals: enabling each Kconfig symbol should compile the matching object and register its KUnit suite.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/test/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/test/iio-test-format.c -->
# sources/distributed-fs/ceph-client/drivers/iio/test/iio-test-format.c

Purpose: KUnit suite for `iio_format_value()` string formatting across IIO value encodings.

Important APIs/types/functions: `IIO_TEST_FORMAT_EXPECT_EQ()` checks return length and output string. Test cases cover `IIO_VAL_INT`, `IIO_VAL_INT_PLUS_MICRO`, `IIO_VAL_INT_PLUS_MICRO_DB`, `IIO_VAL_INT_PLUS_NANO`, `IIO_VAL_FRACTIONAL`, `IIO_VAL_FRACTIONAL_LOG2`, `IIO_VAL_INT_MULTIPLE`, and `IIO_VAL_INT_64`.

Control flow: each test allocates a PAGE_SIZE buffer with KUnit allocation, sets sample values, calls `iio_format_value()`, and asserts exact strings. `kunit_test_suite()` registers the `iio-format` suite.

State and persistence: no persistent state; allocations are KUnit-managed per test.

Dependencies/integration: depends on KUnit and IIO core formatting. Built by `CONFIG_IIO_FORMAT_KUNIT_TEST`.

Risks: exact string tests are intentionally brittle for ABI regressions; any intended formatting change must update many expected strings. Large integer edge coverage protects sign handling, but buffer-size behavior is not directly stress-tested.

Test signals: KUnit suite `iio-format` should pass all six cases and catch formatting regressions for sysfs ABI text.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/test/iio-test-format.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/test/iio-test-gts.c -->
# sources/distributed-fs/ceph-client/drivers/iio/test/iio-test-gts.c

Purpose: KUnit suite for IIO gain-time-scale helper logic used by light sensors with gain and integration-time combinations.

Important APIs/types/functions: Defines unsorted test gain/time tables, global `struct iio_gts gts`, and helper `__test_init_iio_gain_scale()`. Tests cover invalid init, `iio_gts_find_gain_sel_for_scale_using_time()`, `iio_gts_find_new_gain_sel_by_old_gain_time()`, `iio_find_closest_gain_low()`, `iio_gts_total_gain_to_scale()`, `iio_gts_avail_times()`, `iio_gts_all_avail_scales()`, and `iio_gts_avail_scales_for_time()`.

Control flow: tests create a KUnit device, initialize GTS tables through devm helper APIs, assert successful and failing lookups, then verify generated available-time and available-scale tables. The suite is registered as `iio-gain-time-scale`.

State and persistence: no persistent state; KUnit devices and devm allocations are test-lifetime resources. The global `gts` is reused but reinitialized per test path.

Dependencies/integration: depends on KUnit device helpers, `linux/iio/iio-gts-helper.h`, and namespace `IIO_GTS_HELPER`. Built by `CONFIG_IIO_GTS_KUNIT_TEST`.

Risks: global `gts` reuse could hide issues if tests ever run concurrently. Expected values encode the helper's sorting and duplicate-time behavior, so helper behavior changes need careful ABI review. Coverage focuses on selected helper branches, not every possible table shape.

Test signals: KUnit suite should pass six cases, including invalid negative/overflow tables and exact available-list contents.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/test/iio-test-gts.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/test/iio-test-multiply.c -->
# sources/distributed-fs/ceph-client/drivers/iio/test/iio-test-multiply.c

Purpose: KUnit suite for `iio_multiply_value()`, validating conversion of IIO encoded values multiplied by signed 64-bit multipliers into integer results.

Important APIs/types/functions: Helper test functions cover integer, fixed-point micro/nano, fractional, and fractional-log2 formats for positive, negative, and zero values. Uses `div_s64()` for expected fixed/fractional results.

Control flow: public KUnit cases call internal helpers twice, once with positive multiplier and once with negative multiplier. The suite registers as `iio-multiply`.

State and persistence: no persistent state.

Dependencies/integration: depends on KUnit, `linux/iio/consumer.h`, math64 helpers, and namespace `IIO_UNIT_TEST`. Built by `CONFIG_IIO_MULTIPLY_KUNIT_TEST`.

Risks: tests assert integer truncation behavior, so changes in rounding semantics will fail. Very large overflow boundaries are not deeply covered despite use of s64 multipliers.

Test signals: all four KUnit cases should pass for positive and negative multipliers across supported IIO value encodings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/test/iio-test-multiply.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/test/iio-test-rescale.c -->
# sources/distributed-fs/ceph-client/drivers/iio/test/iio-test-rescale.c

Purpose: KUnit suite for IIO analog-front-end rescale conversion helpers, covering scale and offset calculations across IIO value encodings and difficult numeric cases.

Important APIs/types/functions: `struct rescale_tc_data` defines parameterized cases. `scale_cases` and `offset_cases` cover typical, small fractional, negative, decimal-overflow, and 32-bit-overflow scenarios. Helpers include `case_to_desc()`, `iio_str_to_nano()`, `iio_test_relative_error_ppm()`, `iio_rescale_test_scale()`, and `iio_rescale_test_offset()`.

Control flow: KUnit array parameters feed scale and offset tests. The scale test calls `rescale_process_scale()`, formats the result with `iio_format_value()`, parses expected and actual strings into nano units, and requires zero ppm relative error. The offset test calls `rescale_process_offset()` and compares trimmed formatted output to expected integer strings.

State and persistence: no persistent state; each test allocates buffers and local `struct rescale`.

Dependencies/integration: depends on `linux/iio/afe/rescale.h`, IIO formatting/parsing helpers, gcd/overflow utilities, KUnit, and namespace `IIO_RESCALE`. Built by `CONFIG_IIO_RESCALE_KUNIT_TEST`.

Risks: string parsing with nano precision can lose precision for very long decimal expected values, but the cases are selected to match helper outputs. The suite is large and exact, so intentional arithmetic changes need synchronized expected updates.

Test signals: KUnit suite `iio-rescale` should pass all parameterized scale and offset cases and is the primary regression signal for rescale arithmetic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/test/iio-test-rescale.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/trigger/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/iio/trigger/Kconfig

Purpose: Kconfig menu for standalone IIO trigger drivers: hrtimer, generic interrupt, STM32 low-power timer, STM32 timer, tight-loop kthread, and sysfs triggers.

Important APIs/types/functions: Defines `IIO_HRTIMER_TRIGGER`, `IIO_INTERRUPT_TRIGGER`, `IIO_STM32_LPTIMER_TRIGGER`, `IIO_STM32_TIMER_TRIGGER`, `IIO_TIGHTLOOP_TRIGGER`, and `IIO_SYSFS_TRIGGER` with dependencies on `IIO_SW_TRIGGER`, STM32 MFD support, SYSFS, or COMPILE_TEST as appropriate.

Control flow: build-time selection only.

State and persistence: kernel configuration state only.

Dependencies/integration: these options map to objects in the trigger Makefile and gate trigger types available to IIO devices/userspace.

Risks: wrong dependencies can expose non-buildable drivers under COMPILE_TEST or hide triggers from platforms. User-facing module names in help text must stay aligned with Makefile object names.

Test signals: `allmodconfig`/COMPILE_TEST builds should cover each option, and selected modules should appear with the names documented in help text.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/trigger/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/trigger/Makefile -->
# sources/distributed-fs/ceph-client/drivers/iio/trigger/Makefile

Purpose: kbuild mapping for standalone IIO trigger driver objects.

Important APIs/types/functions: Maps each trigger Kconfig symbol to its object: hrtimer, interrupt, STM32 LPTIM, STM32 TIM, sysfs, and tight-loop.

Control flow: standard kbuild object inclusion.

State and persistence: build-system only.

Dependencies/integration: must stay aligned with `drivers/iio/trigger/Kconfig` symbols and module names.

Risks: mismatched symbols silently omit trigger drivers from builds. Ordering comments require maintenance when new triggers are added.

Test signals: enabling each Kconfig symbol should compile exactly the matching object.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/trigger/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/trigger/iio-trig-hrtimer.c -->
# sources/distributed-fs/ceph-client/drivers/iio/trigger/iio-trig-hrtimer.c

Purpose: Software IIO trigger type that uses a high-resolution timer to poll attached IIO devices periodically at a configurable sampling frequency.

Important APIs/types/functions: `struct iio_hrtimer_info` embeds `iio_sw_trigger`, `hrtimer`, sampling-frequency pair, and period. Key functions are sampling-frequency show/store callbacks, `iio_hrtimer_trig_handler()`, `iio_trig_hrtimer_set_state()`, `iio_trig_hrtimer_probe()`, and remove.

Control flow: creating a software trigger allocates an IIO trigger, attaches sysfs attributes, initializes a monotonic hrtimer, sets default 100 Hz, registers it, and exposes it through configfs sw-trigger infrastructure. Enabling starts the hrtimer in hard relative mode; each expiry forwards the timer and calls `iio_trigger_poll()`. Disabling cancels the timer.

State and persistence: sampling frequency and period are in-memory trigger state. No persistence outside configfs-created trigger lifetime.

Dependencies/integration: depends on IIO software trigger framework, hrtimer, configfs item type, and IIO formatting/parsing helpers.

Risks: very high frequencies can create heavy interrupt context load. Store path updates frequency/period without explicit locking against an active timer. Fraction parsing uses centi-style multiplier then converts to mHz/uHz, so unit mistakes can affect ABI.

Test signals: create hrtimer trigger via configfs, read/write `sampling_frequency`, attach a buffered IIO device, verify poll cadence, and remove while active to ensure timer cancellation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/trigger/iio-trig-hrtimer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/trigger/iio-trig-interrupt.c -->
# sources/distributed-fs/ceph-client/drivers/iio/trigger/iio-trig-interrupt.c

Purpose: Platform driver that turns an arbitrary platform IRQ resource into an IIO trigger.

Important APIs/types/functions: `struct iio_interrupt_trigger_info` stores IRQ number. `iio_interrupt_trigger_probe()` allocates trigger state, requests the IRQ, and registers the trigger. `iio_interrupt_trigger_poll()` calls `iio_trigger_poll()`.

Control flow: probe obtains IRQ resource 0, combines resource trigger flags with `IRQF_SHARED`, allocates trigger named `irqtrig%d`, requests IRQ with trigger as private data, registers the trigger, and stores it as platform data. Remove unregisters the trigger, frees IRQ, state, and trigger object.

State and persistence: only runtime trigger object and IRQ binding.

Dependencies/integration: platform-device resources, Linux IRQ subsystem, and IIO trigger core.

Risks: shared IRQs can generate polls from unrelated interrupt sources if hardware does not filter. No `validate_device` callback limits consumers. Manual allocation/unwind paths must remain ordered.

Test signals: platform device with IRQ resource should create `irqtrigN`, interrupt should poll attached buffers, and remove should free shared IRQ cleanly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/trigger/iio-trig-interrupt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/trigger/iio-trig-loop.c -->
# sources/distributed-fs/ceph-client/drivers/iio/trigger/iio-trig-loop.c

Purpose: Experimental IIO software trigger that polls continuously from a kthread as fast as possible.

Important APIs/types/functions: `struct iio_loop_info` embeds `iio_sw_trigger` and the active task pointer. Core functions are `iio_loop_thread()`, `iio_loop_trigger_set_state()`, `iio_trig_loop_probe()`, and remove.

Control flow: probe allocates and registers a software trigger. Enabling starts a freezable kthread that repeatedly calls `iio_trigger_poll_nested()` until stopped. Disabling stops the task. Remove unregisters and frees the trigger state.

State and persistence: task pointer exists only while enabled. No persisted configuration.

Dependencies/integration: IIO software trigger framework, kthreads, freezer support, and platform alias `iio-trig-loop`.

Risks: intentionally high CPU usage; unsafe for consumers needing top-half behavior. Disable assumes a valid task exists. Remove does not explicitly stop an active task, relying on trigger disable ordering.

Test signals: create loop trigger, attach a lower-half-only buffered device, observe high-rate sampling, freeze/thaw behavior, and clean disable/remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/trigger/iio-trig-loop.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/trigger/iio-trig-sysfs.c -->
# sources/distributed-fs/ceph-client/drivers/iio/trigger/iio-trig-sysfs.c

Purpose: Sysfs-controlled IIO trigger provider. Userspace creates numbered triggers and manually fires them by writing to per-trigger sysfs attributes.

Important APIs/types/functions: `struct iio_sysfs_trig` holds trigger, hard irq_work, numeric ID, and list link. Global `iio_sysfs_trig_list` is protected by `iio_sysfs_trig_list_mut`. Key functions are add/remove sysfs stores, `iio_sysfs_trigger_probe()`, `iio_sysfs_trigger_remove()`, `iio_sysfs_trigger_poll()`, and init/exit.

Control flow: module init registers a device on `iio_bus_type` with `add_trigger` and `remove_trigger`. Adding validates uniqueness, allocates `sysfstrig%d`, attaches `trigger_now`, registers it, lists it, and pins the module. Writing `trigger_now` queues hard irq_work, which calls `iio_trigger_poll()`. Removing unregisters the trigger, syncs irq_work, frees state, removes list entry, and drops the module reference.

State and persistence: in-memory list of created triggers; no persistence across module unload/reboot.

Dependencies/integration: SYSFS, IRQ_WORK, IIO bus/trigger core, and module reference counting.

Risks: trigger IDs are user-chosen and duplicate handling returns `-EINVAL`. Exit unregisters the control device but does not itself iterate remaining triggers, so userspace should remove triggers or lifetime ordering must guarantee cleanup. Manual module refcounting is critical to avoid unloading with active triggers.

Test signals: create/remove triggers through sysfs, fire `trigger_now` and observe buffer poll, test duplicate/remove-missing IDs, and unload after all triggers are removed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/trigger/iio-trig-sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/trigger/stm32-lptimer-trigger.c -->
# sources/distributed-fs/ceph-client/drivers/iio/trigger/stm32-lptimer-trigger.c

Purpose: STM32 low-power timer IIO trigger provider for ADC/DAC style hardware-triggered IIO devices.

Important APIs/types/functions: `struct stm32_lptim_cfg` selects trigger-name tables by SoC, and `struct stm32_lptim_trigger` stores device plus trigger list. Main functions are `stm32_lptim_validate_device()`, exported `is_stm32_lptim_trigger()`, `stm32_lptim_setup_trig()`, and probe.

Control flow: probe reads `reg` index, selects match-data trigger table, validates index, and registers each trigger name for that LPTIM instance. Trigger validation accepts only IIO devices with `INDIO_HARDWARE_TRIGGERED`.

State and persistence: no runtime configuration state beyond registered trigger objects.

Dependencies/integration: STM32 LPTIM MFD bindings, device properties, IIO trigger core, exported helper used by other STM32 drivers, and OF compatibles for STM32/STM32MP25 LPTIM trigger variants.

Risks: trigger tables are SoC-specific and index-sensitive; bad `reg` values fail probe. Validation only checks IIO mode, not a specific peripheral relationship. Exported identity check depends on exact ops pointer.

Test signals: probe each supported compatible/index, confirm expected trigger names appear, attach hardware-triggered consumers, reject non-hardware-triggered consumers, and build-test exported symbol users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/trigger/stm32-lptimer-trigger.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/trigger/stm32-timer-trigger.c -->
# sources/distributed-fs/ceph-client/drivers/iio/trigger/stm32-timer-trigger.c

Purpose: STM32 general-purpose timer IIO trigger and legacy IIO counter driver. It registers timer TRGO/TRGO2/channel triggers, exposes sampling-frequency and master-mode controls for TRGO triggers, and optionally creates an IIO_COUNT device for validating timer trigger inputs.

Important APIs/types/functions: `struct stm32_timer_trigger` stores regmap, clock, trigger/valid tables, state lock, registered trigger list, and suspend backup registers. `struct stm32_timer_trigger_cfg` selects valid trigger tables. Key functions include `stm32_timer_start()`, `stm32_timer_stop()`, frequency/master-mode sysfs callbacks, `stm32_register_iio_triggers()`, counter read/write/validate callbacks, enum setters/getters, `stm32_setup_counter_device()`, exported `is_stm32_timer_trigger()`, probe/remove, and PM callbacks.

Control flow: probe reads timer index, obtains STM32 MFD regmap/clock/max ARR, optionally registers an IIO counter if valid trigger inputs exist, detects TRGO2 support by write/readback, initializes lock, and registers all trigger names for the timer. Frequency writes start or stop the timer: start calculates prescaler/ARR from clock rate and requested frequency, refuses use if capture/compare channels are active, enables the clock, programs PSC/ARR/CR2 master mode, forces update, and enables CEN. Counter operations expose CNT, CEN enable, quadrature scale, preset, enable mode, and trigger mode. Suspend backs up timer registers and disables clock if this driver enabled it; resume restores registers and clock.

State and persistence: `enabled` tracks clock ownership for this child driver; hardware timer registers store current frequency, master/slave mode, count, and preset. Suspend backup is in RAM only. Registered trigger list is runtime state.

Dependencies/integration: depends on STM32 timers MFD (`struct stm32_timers`), regmap, clk framework, IIO trigger and IIO device APIs, sysfs attributes, device properties, and OF compatibles `st,stm32-timer-trigger`, `st,stm32h7-timer-trigger`, and `st,stm32mp25-timer-trigger`.

Risks: timer hardware is shared with PWM/counter/capture users; checks for `TIM_CCER_CCXE` reduce but do not eliminate coordination risks. Prescaler loop can exceed max PSC for low frequencies. Master-mode writes can enable clock without a later automatic disable unless users clear state. Ops-pointer identity is used by validation. The MP25 config intentionally omits legacy valid tables, so behavior differs by compatible.

Test signals: probe trigger lists for each timer index/compatible, set and read sampling frequency, test zero frequency stop, write master modes and available list, validate counter trigger acceptance/rejection, suspend/resume with active timer, and test coexistence with capture/compare users returning `-EBUSY`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/trigger/stm32-timer-trigger.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/infiniband/Kconfig

Purpose: Top-level Kconfig for Linux InfiniBand/RDMA support in this source tree.

Important APIs/types/functions: Defines `INFINIBAND` menuconfig and major options including userspace MAD, userspace verbs/CM, user memory, on-demand paging, address translation (`INFINIBAND_ADDR_TRANS`), address-translation configfs, and virtual DMA. It sources hardware, software, and ULP subdirectory Kconfig files.

Control flow: build-time feature selection only. Nested blocks include hardware providers when appropriate and always include software RXE/SIW and ULP protocols under `INFINIBAND`.

State and persistence: kernel configuration state only.

Dependencies/integration: depends on networking, INET, DMA/IOMEM, and not ALPHA. Selects shared DMA buffer, IRQ polling, and DIMLIB. Integrates with rdma-core userspace expectations described in help text.

Risks: broad `select`s affect kernel footprint. `INFINIBAND_ADDR_TRANS` default y pulls RDMA CM support into many builds. Source ordering determines visible provider options. Dependency expressions around configfs and modules are subtle.

Test signals: config builds for core-only, userspace access, ODP, configfs, software providers, and representative hardware providers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/Makefile -->
# sources/distributed-fs/ceph-client/drivers/infiniband/Makefile

Purpose: Top-level kbuild dispatcher for InfiniBand/RDMA subdirectories.

Important APIs/types/functions: Adds `core/`, `hw/`, `ulp/`, and `sw/` when `CONFIG_INFINIBAND` is enabled.

Control flow: build-system only.

State and persistence: none beyond build configuration.

Dependencies/integration: aligns with top-level InfiniBand Kconfig and subordinate Makefiles.

Risks: any subdirectory omitted here cannot build even if its Kconfig is enabled.

Test signals: enabling `CONFIG_INFINIBAND` should descend into all four subtrees.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/Makefile -->
# sources/distributed-fs/ceph-client/drivers/infiniband/core/Makefile

Purpose: kbuild definitions for RDMA core modules and optional core components.

Important APIs/types/functions: Builds `ib_core.o`, `ib_cm.o`, `iw_cm.o`, `rdma_cm.o`, `rdma_ucm.o`, `ib_umad.o`, and `ib_uverbs.o` based on Kconfig. `ib_core-y` includes core files such as `addr.o`, `verbs.o`, `device.o`, `cache.o`, `netlink.o`, `sa_query.o`, and more. Optional objects are added for security, RDMA cgroups, user memory, and ODP.

Control flow: build-time object aggregation only.

State and persistence: none beyond module composition.

Dependencies/integration: maps `CONFIG_INFINIBAND_ADDR_TRANS` to RDMA CM/UCMA, and userspace features to `ib_umad`/`ib_uverbs`. Adds include path for `cma_trace.o`.

Risks: object membership affects exported symbols and module dependencies. `addr.o` is always in `ib_core-y`, so address resolution is part of core whenever InfiniBand is enabled.

Test signals: representative configs should link built-in and modular core variants, including address translation on/off and user access on/off.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/addr.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/core/addr.c

Purpose: RDMA core address-resolution service. It maps IP/GID/socket destinations to RDMA device addressing, source L2 addresses, destination hardware addresses, hop limits, and RoCE network type, using routing tables, neighbor discovery, netlink path records, and asynchronous work.

Important APIs/types/functions: `struct addr_req` represents an async resolve request with source/destination sockaddr copies, `rdma_dev_addr`, callback/context, timeout, delayed work, status, netlink sequence, and optional GID-attribute namespace resolution. Exported APIs include `rdma_addr_size()`, `rdma_addr_size_in6()`, `rdma_addr_size_kss()`, `rdma_copy_src_l2_addr()`, `rdma_translate_ip()`, `rdma_resolve_ip()`, `roce_resolve_route_from_path()`, `rdma_addr_cancel()`, `rdma_addr_find_l2_eth_by_grh()`, `addr_init()`, and `addr_cleanup()`.

Control flow: `rdma_resolve_ip()` allocates a request, copies addresses, assigns a netlink sequence, calls `addr_resolve()` immediately, and queues delayed work for success callback or neighbor/netlink retry. `addr_resolve()` derives the network namespace if requested from `sgid_attr`, performs IPv4/IPv6 route lookup, fills source L2 address and network type, optionally resolves destination hardware address, then releases route references. Destination resolution uses local-copy fast path, neighbor cache lookup with `neigh_event_send()` retry on incomplete entries, or RDMA netlink LS multicast for IB gateways. `process_one_req()` retries `-ENODATA` until timeout, invokes callback, cancels work, removes the request, and frees it. Netlink responses match sequence numbers and fill DGID. Netevent neighbor updates wake all pending requests.

State and persistence: global `req_list` is protected by `lock`; `addr_wq` is an ordered workqueue; `ib_nl_addr_request_seq` provides netlink sequence numbers. Request state is transient and callback-owned after completion. `rdma_dev_addr` is mutated with net namespace, ifindex, source/destination L2 addresses, network type, hoplimit, and DGID.

Dependencies/integration: depends on IPv4/IPv6 routing, neighbour/ARP, netevent notifier, RDMA netlink LS, RDMA GID cache attributes, SA path records, workqueues, spinlocks, RCU, and RDMA CM/core private init. Integrates with RoCE path validation and GRH-to-Ethernet address lookup.

Risks: asynchronous lifetime is delicate: list removal, delayed work cancellation, callback invocation, and `rdma_addr_cancel()` must not race. Namespace derivation from `sgid_attr` relies on RCU and resets defaults afterward. If no RDMA netlink listener exists, IB gateway resolution fails with `-EADDRNOTAVAIL`. Neighbor resolution can time out under ARP/ND loss. `addr_resolve()` assumes valid address-family sizes from callers. Netlink response validation only accepts non-request kernel-origin messages.

Test signals: unit/integration tests should cover IPv4 and IPv6 route resolution, bound-device lookup, local destination handling, gateway RoCE v2 network type selection, neighbor retry and timeout, cancellation before and during work, netlink DGID response matching, GRH-to-Ethernet lookup, RoCE route type validation, and cleanup with empty request list.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/addr.c -->
