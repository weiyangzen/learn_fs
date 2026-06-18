# subset-b-005439 research

This grouped report covers Linux thermal drivers and build glue under `sources/distributed-fs/ceph-client/drivers/thermal`. Each section is bounded by `BEGIN_FILE_RESEARCH` and `END_FILE_RESEARCH` markers for deterministic reconciliation into per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/qcom/tsens.c -->
# sources/distributed-fs/ceph-client/drivers/thermal/qcom/tsens.c

Purpose: shared Qualcomm TSENS platform driver core. It binds `qcom,*-tsens` device-tree compatibles, initializes TSENS register maps, reads calibration data, registers each TSENS sensor as a thermal zone, handles upper/lower/critical threshold IRQs, and exposes optional debugfs and hwmon views.

Important APIs, types, and functions: `qfprom_read()`, `tsens_read_calibration()`, `tsens_read_calibration_legacy()`, `compute_intercept_slope()`, `init_common()`, `get_temp_tsens_valid()`, `get_temp_common()`, `tsens_set_trips()`, `tsens_register_irq()`, `tsens_register()`, `tsens_probe()`, and `tsens_resume_common()`. The implementation consumes `struct tsens_priv`, `struct tsens_sensor`, `struct tsens_ops`, `struct tsens_features`, and `enum regfield_ids` from `tsens.h`.

Control flow: probe selects `struct tsens_plat_data` from the OF match table, optionally overrides the sensor count from `#qcom,sensors`, allocates a flexible `tsens_priv`, assigns hardware sensor IDs, and calls the SoC-specific `ops->init()` callback. `init_common()` maps split or legacy SROT/TM register spaces, creates `regmap_field` handles for status, valid, threshold, mask, clear, watchdog, and control fields, enables TSENS where required, and globally enables interrupts for modern IP. Calibration then runs through the SoC callback, and `tsens_register()` creates per-sensor thermal zones and requests either one combined IRQ or separate `uplow` and `critical` IRQs.

Temperature path: `get_temp_tsens_valid()` waits for a per-sensor valid bit on v0.1+ hardware, then uses `tsens_hw_to_mC()` to convert either ADC code or deci-Celsius register data to milli-Celsius. `get_temp_common()` is used for older ADC-code hardware and polls the `TRDY` bit on version 0 before converting with `code_to_degc()`.

Calibration and conversion: modern NVMEM calibration is read from named cells such as `mode`, `base1`, `base2`, `sN_p1`, and `sN_p2`; legacy calibration reads packed QFPROM blobs described by `struct tsens_legacy_calibration_format`. One-point and two-point modes feed `compute_intercept_slope()`, which derives per-sensor slope and offset for threshold and reading conversion. Calibrationless fallback uses synthetic `p1=500`, `p2=780`.

Trip and IRQ behavior: `tsens_set_trips()` clamps requested low/high trips to hardware limits, converts to ADC or deci-Celsius register values, writes per-sensor threshold fields, and enables lower/upper interrupts under `ul_lock`. IRQ handling first checks threshold status fields; upper/lower IRQs update the thermal zone, critical IRQs clear watchdog bark and mask unused critical interrupts. Pre-v0.1 hardware has shared threshold/interrupt registers and special handling for sensor 0.

State and persistence: persistent state lives in hardware registers, NVMEM calibration cells, per-sensor `slope`, `offset`, `tzd`, and debugfs dentries. `tsens_remove()` removes debugfs, disables global TSENS IRQs, and calls optional SoC disable logic. Suspend/resume delegates to SoC callbacks; `tsens_resume_common()` re-enables watchdog/interrupt state after suspend-to-RAM on v2+.

Dependencies and integration points: Linux thermal OF registration, hwmon sysfs helper, debugfs, platform resources, NVMEM, regmap/regmap_field, syscon for legacy GCC-backed TSENS, PM sleep hooks, DT compatibles, and SoC data exported by `tsens-v0_1.c`, `tsens-v1.c`, `tsens-v2.c`, and `tsens-8960.c`.

Risks: the enum ordering in `regfield_ids` is assumed by `init_common()` allocation loops; bad DT resource layouts can map the wrong SROT/TM region; missing or malformed NVMEM cells abort calibration; legacy shared IRQ/threshold hardware cannot reliably interrupt on multiple sensors; critical IRQ masking is intentionally conservative because Linux does not use TSENS critical interrupts directly.

Test signals: probe each compatible with split and legacy register layouts; verify NVMEM modes including no calibration, one-point, two-point, and backup cells; exercise thermal-zone `get_temp` and `set_trips`; confirm `uplow`, `critical`, and `combined` IRQs update zones and clear masks; check suspend-to-RAM resume reinitializes watchdog and interrupts; inspect debugfs `version` and `sensors` plus hwmon attributes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/qcom/tsens.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/qcom/tsens.h -->
# sources/distributed-fs/ceph-client/drivers/thermal/qcom/tsens.h

Purpose: internal interface and data model for the Qualcomm TSENS driver family. It defines calibration modes, IP versions, register-field IDs, per-sensor and per-controller state, SoC operation callbacks, and exported platform data names used by `tsens.c` and version-specific implementation files.

Important APIs and types: `enum tsens_ver`, `enum tsens_irq_type`, `struct tsens_sensor`, `struct tsens_ops`, `enum regfield_ids`, `struct tsens_features`, `struct tsens_plat_data`, `struct tsens_context`, `struct tsens_priv`, `struct tsens_single_value`, and `struct tsens_legacy_calibration_format`. It declares shared helpers including `tsens_read_calibration_legacy()`, `tsens_read_calibration()`, `tsens_calibrate_nvmem()`, `compute_intercept_slope()`, `init_common()`, `get_temp_tsens_valid()`, and `get_temp_common()`.

Control flow role: version-specific files populate `struct tsens_plat_data` with sensor count, hardware IDs, feature flags, bitfield arrays, and `struct tsens_ops` callbacks. `tsens.c` consumes those declarations to run init, calibration, temperature reads, enable/disable, and PM callbacks without embedding per-SoC register layouts.

State model: `struct tsens_priv` owns register maps for TM and SROT spaces, `regmap_field *rf[MAX_REGFIELDS]`, SoC feature pointers, operations, debugfs dentries, a threshold lock, and a flexible array of `struct tsens_sensor`. Each sensor tracks its thermal zone, hardware ID, slope, offset, and optional calibration offsets.

Register dependencies: the macro families `REG_FIELD_FOR_EACH_SENSOR11`, `REG_FIELD_FOR_EACH_SENSOR16`, `REG_FIELD_SPLIT_BITS_0_15`, and `REG_FIELD_SPLIT_BITS_16_31` help SoC files build `struct reg_field` arrays indexed by `enum regfield_ids`. The header explicitly warns that reordering the enum affects allocation loops in `init_common()`.

Integration points: relies on Linux regmap, interrupt, thermal, and allocation headers. It exports platform data symbols such as `data_8960`, `data_8226`, `data_8916`, `data_tsens_v1`, `data_8996`, `data_ipq8074`, and newer IPQ entries, making this header the contract between common and SoC-specific TSENS code.

Risks: enum ordering and field array completeness are high-risk maintenance points. The `MAX_SENSORS` limit constrains flexible allocation and NVMEM parsing. `tsens_resume_common` becomes `NULL` without `CONFIG_SUSPEND`, so SoC ops must tolerate that. Calibration constants and threshold ADC limits are shared assumptions across IP versions.

Test signals: compile all TSENS SoC files together; add static coverage for every `regfield_ids` range used by `init_common()`; validate that every exported `tsens_plat_data` has non-NULL mandatory ops and enough fields for `max_sensors`; test one v0, v0.1, v1, and v2 compatible path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/qcom/tsens.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/qoriq_thermal.c -->
# sources/distributed-fs/ceph-client/drivers/thermal/qoriq_thermal.c

Purpose: NXP/Freescale QorIQ and i.MX8MQ Thermal Monitoring Unit driver. It programs TMU range and calibration registers from device tree, exposes up to 16 monitoring sites as thermal zones, and polls immediate temperature registers.

Important APIs and functions: `tmu_get_temp()`, `qoriq_tmu_register_tmu_zone()`, `qoriq_tmu_calibration()`, `qoriq_tmu_init_device()`, `qoriq_tmu_probe()`, `qoriq_tmu_suspend()`, and `qoriq_tmu_resume()`. `struct qoriq_tmu_data` owns version, range registers, regmap, clock, and sensor array; `struct qoriq_sensor` supplies the thermal-zone private ID.

Control flow: probe maps the MMIO resource through a regmap with endian selected by the `little-endian` DT property, enables an optional clock, registers a devm action to disable monitoring, reads the IP block revision, initializes the TMU in disabled/polling mode, writes calibration/range data from `fsl,tmu-range` and `fsl,tmu-calibration`, then registers all thermal zones present in the OF thermal map.

Temperature path: `tmu_get_temp()` first checks that measurement is enabled in `REGS_TMR`, then polls `REGS_TRITSR(id)` until `TRITSR_V` is set. Version 1 returns an 8-bit Celsius value. Version 2 treats the value as Kelvin, with `TRITSR_TP5` adding half-Kelvin resolution before converting to milli-Celsius.

State and persistence: hardware registers hold range, calibration, monitor-site enablement, update interval, and measurement enable state. The driver keeps a copy of written range values in `ttrcr[]`, but calibration is not persisted outside hardware. Suspend clears measurement enable and disables the clock; resume reenables the clock, clears v2 command state, and re-enables measurement.

Dependencies and integration points: platform DT compatibles `fsl,qoriq-tmu` and `fsl,imx8mq-tmu`, regmap access tables for safe read/write ranges, optional clock, OF thermal zones, and hwmon sysfs helper.

Risks: DT calibration properties are mandatory and format-sensitive; endianness is DT-controlled and wrong settings corrupt register programming; v1/v2 monitor-site bit ordering differs; no Linux IRQ handler is used even though hardware has interrupt registers, so responsiveness depends on thermal framework polling plus enabled hardware overheat behavior.

Test signals: boot with v1 and v2 compatible hardware or emulation; verify invalid `fsl,tmu-range` lengths are rejected; check Celsius and Kelvin conversion paths; confirm only DT-described zones are registered; run suspend/resume while measurement is active; inspect hwmon exposure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/qoriq_thermal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/renesas/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/thermal/renesas/Kconfig

Purpose: Kconfig menu entries for Renesas thermal drivers. It exposes separate tristate options for legacy R-Car, R-Car Gen3/Gen4 and RZ/G2, RZ/G2L, RZ/G3E, and RZ/G3S thermal sensor drivers.

Important symbols: `RCAR_THERMAL`, `RCAR_GEN3_THERMAL`, `RZG2L_THERMAL`, `RZG3E_THERMAL`, and `RZG3S_THERMAL`. Most depend on `ARCH_RENESAS || COMPILE_TEST`; the RZ/G3S option specifically depends on `ARCH_R9A08G045 || COMPILE_TEST` plus `OF`, `IIO`, and `RZG2L_ADC`.

Control flow and integration: these symbols select whether the corresponding objects in `renesas/Makefile` are built. The options assume thermal OF integration from the driver side but do not select the thermal framework themselves, relying on parent menu context and build dependencies.

State and persistence: no runtime state. It controls build-time inclusion only.

Dependencies and risks: missing `HAS_IOMEM` or `OF` dependencies would produce bad compile or probe surfaces for MMIO/DT-only drivers; `RZG3E_THERMAL` lacks explicit `HAS_IOMEM` and `OF` dependencies compared with neighboring options, so compile-test coverage is important. `RZG3S_THERMAL` is tied to IIO and the RZ/G2L ADC because its temperature samples come through an IIO channel.

Test signals: run Kconfig dependency checks under Renesas and COMPILE_TEST configs; ensure every enabled symbol builds the object named in `Makefile`; verify RZ/G3S cannot be enabled without the IIO ADC dependency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/renesas/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/renesas/Makefile -->
# sources/distributed-fs/ceph-client/drivers/thermal/renesas/Makefile

Purpose: build mapping for Renesas thermal drivers.

Important entries: `CONFIG_RCAR_GEN3_THERMAL` builds `rcar_gen3_thermal.o`, `CONFIG_RCAR_THERMAL` builds `rcar_thermal.o`, `CONFIG_RZG2L_THERMAL` builds `rzg2l_thermal.o`, `CONFIG_RZG3E_THERMAL` builds `rzg3e_thermal.o`, and `CONFIG_RZG3S_THERMAL` builds `rzg3s_thermal.o`.

Control flow and integration: the file is direct Kbuild glue. It does not aggregate objects or define composite modules; each source becomes its own module or built-in object based on the Kconfig symbol.

State, dependencies, and risks: no runtime state. The risk is simple drift between Kconfig symbols, source filenames, and module names. New Renesas thermal files must be added here and to Kconfig together.

Test signals: compile all five symbols as built-in and as modules; verify module aliases in each source still match DT compatibles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/renesas/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/renesas/rcar_gen3_thermal.c -->
# sources/distributed-fs/ceph-client/drivers/thermal/renesas/rcar_gen3_thermal.c

Purpose: Renesas R-Car Gen3, Gen4, and RZ/G2 THS thermal sensor driver. It supports multiple TSC MMIO blocks, reads fused or fallback calibration points, computes piecewise linear conversion coefficients, registers OF thermal zones, and optionally handles threshold IRQs.

Important functions and types: `struct rcar_gen3_thermal_priv`, `struct rcar_gen3_thermal_tsc`, `struct rcar_thermal_info`, fuse descriptor types, `rcar_gen3_thermal_get_temp()`, `rcar_gen3_thermal_set_trips()`, `rcar_gen3_thermal_irq()`, `rcar_gen3_thermal_read_fuses()`, `rcar_gen3_thermal_init()`, `rcar_gen3_thermal_request_irqs()`, `rcar_gen3_thermal_probe()`, and `rcar_gen3_thermal_resume()`.

Control flow: probe installs the OF match data, tries to request two optional IRQs, enables runtime PM, maps up to five TSC resources, reads fuses or default pseudo calibration values, calculates shared and per-TSC coefficients, initializes each hardware block, registers one thermal zone per TSC, and adds hwmon sysfs with a devm cleanup action.

Temperature and trip conversion: the current `REG_GEN3_TEMP` value is compared with `thcode[1]` to choose below or above coefficient sets. Conversion uses datasheet-derived `PTAT` and `THCODE` values and reports milli-Celsius. The inverse conversion programs low and high threshold registers for `set_trips()`.

IRQ behavior: two optional IRQs are requested with a shared threaded handler. The handler checks each TSC `IRQSTR`, clears it, and calls `thermal_zone_device_update()` for zones with nonzero status. If IRQ request fails, `set_trips` is disabled and the driver falls back to thermal framework polling.

State and persistence: persistent state is in fuses and THS registers. Driver state holds per-TSC bases, zones, `thcode[]`, coefficients, shared `ptat[]`, threshold split `tj_t`, and SoC-specific scale/adjust constants. Resume re-runs hardware initialization for every TSC but does not re-read calibration.

Dependencies and integration points: platform MMIO resources, optional IRQs, runtime PM, Linux thermal OF, hwmon sysfs, Renesas DT compatibles from RZ/G2 and R-Car Gen3/Gen4, and hardware fuse monitor registers.

Risks: fallback defaults are essential on unfused parts but can reduce accuracy; coefficient math assumes nonzero denominators from calibration data; `platform_get_irq_optional()` errors disable interrupt trip handling; Gen4 fuse address differences are captured in match data and must be kept aligned with compatibles.

Test signals: boot fused and unfused devices; compare reported temperatures against known calibration points; set high and low trips and verify IRQ updates; suspend/resume and ensure THS blocks restart; test each compatible group with correct number of MMIO resources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/renesas/rcar_gen3_thermal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/renesas/rcar_thermal.c -->
# sources/distributed-fs/ceph-client/drivers/thermal/renesas/rcar_thermal.c

Purpose: legacy Renesas R-Car THS/TSC thermal sensor driver for older R-Car and some Gen2/Gen3-compatible thermal blocks. It supports both OF thermal-zone registration and a legacy tripless registration path, with optional shared or per-channel interrupt support.

Important functions and types: `struct rcar_thermal_common`, `struct rcar_thermal_chip`, `struct rcar_thermal_priv`, `rcar_thermal_update_temp()`, `rcar_thermal_get_current_temp()`, `rcar_thermal_irq()`, `rcar_thermal_work()`, `rcar_thermal_probe()`, `rcar_thermal_suspend()`, and `rcar_thermal_resume()`.

Control flow: probe creates common state, enables runtime PM, maps common IRQ registers if IRQ resources exist, registers IRQ handlers, maps each sensor MMIO resource, stabilizes a comparator reading, registers either an OF thermal zone or a legacy `thermal_zone_device_register_with_trips()` zone, enables hwmon for OF zones, enables per-sensor IRQs, and finally writes the common enable bits.

Temperature path: `rcar_thermal_update_temp()` sets `CPCTL`, repeatedly reads `THSSR` until two consecutive `CTEMP` values match, then programs rising/falling comparator thresholds around the current code. `rcar_thermal_get_current_temp()` converts the code with either a single linear band or a two-band Gen3 formula.

IRQ behavior: the shared IRQ handler masks and clears common status, identifies per-sensor rising/falling status, disables that sensor IRQ, and schedules delayed work. The work item waits for comparator stabilization, re-enables IRQs, and updates the thermal zone. This avoids repeatedly firing on unstable threshold crossings.

State and persistence: common state holds base, device pointer, sensor list, and spinlock. Per-sensor state holds base, chip feature flags, delayed work, thermal zone, and ID. Runtime hardware state includes comparator offsets, interrupt masks, and ENR bits. Suspend/resume only performs special handling for chips marked `needs_suspend_resume`.

Dependencies and integration points: platform resources, OF match data, system freezable workqueue, PM runtime, thermal framework, hwmon, IRQ subsystem, and legacy critical-trip registration for non-OF mode.

Risks: no sensor resource means probe can succeed with zero sensors unless later paths catch it through logged count; interrupt support depends on resource ordering because common registers consume the first MMIO resource only when IRQs exist; Gen3 suspend/resume uses the first list entry and writes hard-coded ENR `0x03`; temperature conversion is coarse and comparator-stability dependent.

Test signals: run with no IRQs and with shared/per-channel IRQ layouts; verify delayed work reprograms thresholds after a crossing; check OF and legacy zone registration paths; test Gen3 suspend/resume; inject unstable `THSSR` reads and expect error handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/renesas/rcar_thermal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/renesas/rzg2l_thermal.c -->
# sources/distributed-fs/ceph-client/drivers/thermal/renesas/rzg2l_thermal.c

Purpose: Renesas RZ/G2L TSU thermal sensor driver. It powers the TSU, reads OTP calibration or fallback values, averages ADC samples, applies curvature correction, registers one thermal zone, and exposes hwmon.

Important functions and types: `struct rzg2l_thermal_priv`, `rzg2l_thermal_get_temp()`, `rzg2l_thermal_init()`, `rzg2l_thermal_probe()`, `rzg2l_thermal_remove()`, and reset/runtime-PM cleanup helper `rzg2l_thermal_reset_assert_pm_disable_put()`.

Control flow: probe maps the MMIO resource, gets an exclusive reset, deasserts it, enables runtime PM, reads calibration registers `OTPTSUTRIM_REG(0/1)` with fallback to software constants, initializes TSU normal mode and conversion start, registers thermal zone 0, and adds hwmon sysfs.

Temperature path: each read samples `TSU_SAD` eight times at roughly 20 us intervals, averages the 12-bit codes, applies a scaled curvature correction, converts using `(dsensor - calib1) * 165 / (calib0 - calib1) - 40`, and rounds up to 500 mC.

State and persistence: persistent calibration lives in OTP trim registers. Driver state holds `calib0`, `calib1`, MMIO base, reset, and thermal zone. The remove path removes hwmon, drops runtime PM, and asserts reset.

Dependencies and integration points: platform MMIO, reset controller, runtime PM, OF thermal, hwmon, and `renesas,rzg2l-tsu` compatible.

Risks: if both calibration values are fallback or malformed, conversion accuracy changes; denominator `calib0 - calib1` is assumed nonzero; readl polling for conversion state must match hardware semantics; no explicit system sleep PM hooks are present beyond remove-time cleanup.

Test signals: verify OTP and fallback calibration paths; compare temperature rounding to 0.5 C; check reset assertion on remove/error; test thermal-zone registration and hwmon creation; fault conversion-start polling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/renesas/rzg2l_thermal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/renesas/rzg3e_thermal.c -->
# sources/distributed-fs/ceph-client/drivers/thermal/renesas/rzg3e_thermal.c

Purpose: Renesas RZ/G3E and RZ/T2H TSU thermal sensor driver. It uses runtime PM to power the sensor on demand, reads calibration either from a syscon phandle or secure monitor calls, performs single averaged conversions, programs comparator trips, and handles compare interrupts.

Important functions and types: `struct rzg3e_thermal_info`, `struct rzg3e_thermal_priv`, `rzg3e_thermal_power_on()`, `rzg3e_thermal_power_off()`, `rzg3e_thermal_code_to_temp()`, `rzg3e_thermal_temp_to_code()`, `rzg3e_thermal_get_temp()`, `rzg3e_thermal_set_trips()`, `rzg3e_thermal_irq()`, `rzg3e_thermal_get_syscon_trim()`, `rzg3e_thermal_get_smc_trim()`, and PM callbacks.

Control flow: probe allocates state, initializes a mutex, maps MMIO, obtains match data, reads trim values through the match-specific `get_trim`, validates calibration, verifies the TSU clock rate, gets an optional deasserted reset, requests named IRQ `adcmpi`, enables autosuspend runtime PM, registers thermal zone 0, registers the threaded IRQ, and adds hwmon.

Temperature path: `get_temp` resumes the device, locks hardware access, clears old conversion status, starts one conversion, polls for the averaged-data flag, reads 12-bit `TSU_SCRR`, clears the flag, converts code to milli-Celsius using two calibration points and match-specific temperature endpoints, then autosuspends.

Trip and IRQ behavior: `set_trips()` requires `low < high`, converts both trips to 12-bit codes, disables compare, clears pending compare flags, writes low/high limit registers, enables averaged-data compare mode, unmasks compare IRQ, and starts a conversion. The hard IRQ clears compare status and disables interrupts until the threaded handler updates the thermal zone with `THERMAL_TRIP_VIOLATED`.

State and persistence: trim values are stored in `trmval0`/`trmval1`; runtime state includes power mode, comparison registers, pending status, and reset line. Runtime suspend powers down and clears interrupts; system suspend powers off if active and asserts reset; resume deasserts reset and powers on if runtime-active.

Dependencies and integration points: ARM SMCCC for RZ/T2H trim reads, syscon regmap for RZ/G3E trim reads, clocks, resets, runtime PM, named IRQ, thermal OF, hwmon, and compatibles `renesas,r9a09g047-tsu` and `renesas,r9a09g077-tsu`.

Risks: trim reads are security/firmware or DT dependent; invalid equal or saturated trims fail probe; clock rate below 24 MHz is rejected; compare hardware requires low less than high, so callers passing sentinel extremes incorrectly can fail; autosuspend means every temp/trip path must balance runtime PM references.

Test signals: test syscon and SMC trim variants; verify invalid trim rejection; exercise get-temp under autosuspend; set low/high trips and trigger compare IRQ; suspend/resume while runtime-active and runtime-suspended; validate hwmon warning path does not fail probe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/renesas/rzg3e_thermal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/renesas/rzg3s_thermal.c -->
# sources/distributed-fs/ceph-client/drivers/thermal/renesas/rzg3s_thermal.c

Purpose: Renesas RZ/G3S TSU thermal driver. Unlike RZ/G2L, temperature samples are read through an IIO channel named `tsu`, while TSU control and OTP trim registers are managed through MMIO.

Important functions and types: `struct rzg3s_thermal_priv`, `rzg3s_thermal_get_temp()`, `rzg3s_thermal_set_mode()`, `rzg3s_thermal_change_mode()`, `rzg3s_thermal_read_calib()`, `rzg3s_thermal_probe()`, `rzg3s_thermal_suspend()`, and `rzg3s_thermal_resume()`.

Control flow: probe maps TSU MMIO, acquires the IIO channel, gets and deasserts reset, enables runtime PM with autosuspend, reads OTP calibration or fallback constants, registers thermal zone 0 with `get_temp` and `change_mode`, and adds hwmon sysfs. Initial mode is disabled until the thermal framework enables the zone.

Temperature path: `get_temp()` returns `-EAGAIN` while disabled. When enabled, it reads eight raw IIO samples with required inter-sample delay, averages them in milli units, applies the datasheet formula `(ts_code_ave - calib1) * 165 / (calib0 - calib1) - 40`, and rounds to 500 mC.

Mode and PM behavior: `change_mode()` toggles TSU hardware only when the mode changes. Enable writes `TSU_SM_EN`, waits at least 30 us, then writes output enable plus enable and waits at least 50 us. Disable writes zero. System suspend disables TSU and asserts reset; resume deasserts reset and restores the previous non-disabled mode.

State and persistence: persistent calibration comes from OTP trim registers. Runtime state tracks current `thermal_device_mode`, reset state, IIO channel, calibration values, and thermal-zone handle.

Dependencies and integration points: IIO consumer API, RZ/G2L ADC dependency, reset controller, runtime PM autosuspend, thermal OF, hwmon, and `renesas,r9a08g045-tsu`.

Risks: the driver stores `priv->mode` after calling `rzg3s_thermal_set_mode()` even if runtime PM resume failed inside the setter; denominator `calib0 - calib1` is assumed nonzero; thermal reads depend on the external IIO provider timing and availability; suspend disables hardware but preserves logical mode for resume.

Test signals: verify disabled reads return `-EAGAIN`; enable/disable through thermal zone mode; test IIO read failure propagation; boot with OTP and fallback calibration; suspend/resume with enabled and disabled modes; check hwmon registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/renesas/rzg3s_thermal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/rockchip_thermal.c -->
# sources/distributed-fs/ceph-client/drivers/thermal/rockchip_thermal.c

Purpose: Rockchip TSADC thermal driver for many Rockchip SoCs. It abstracts multiple TSADC hardware generations through chip-data callbacks, registers one thermal zone per channel, programs software alarm trips and hardware TSHUT thresholds, applies optional eFuse trim, and supports suspend/resume reinitialization.

Important types and functions: `struct rockchip_tsadc_chip`, `struct chip_tsadc_table`, `struct rockchip_thermal_data`, `struct rockchip_thermal_sensor`, ADC conversion helpers `rk_tsadcv2_temp_to_code()` and `rk_tsadcv2_code_to_temp()`, generation-specific initialize/control/IRQ/alarm/TSHUT functions, `rockchip_configure_from_dt()`, `rockchip_get_trim_configuration()`, `rockchip_thermal_register_sensor()`, `rockchip_thermal_probe()`, and PM callbacks.

Control flow: probe gets IRQ, chip match data, sensor array, MMIO, reset, `tsadc` and `apb_pclk` clocks, resets the controller, parses DT TSHUT temperature/mode/polarity and optional `rockchip,grf`, initializes hardware through the chip callback, attaches child-node trim data by channel, registers every sensor thermal zone, requests threaded IRQ, enables automatic conversion, enables zones, and adds hwmon sysfs.

Temperature path: per-sensor `get_temp` calls the chip-specific register read, converts raw ADC code through a piecewise linear table with interpolation, then subtracts sensor trim temperature. Conversion tables may be ADC-incrementing or ADC-decrementing and use different masks for v2/v3/v4 data widths.

Trip and shutdown behavior: `set_trips()` programs only the high alarm threshold and adds sensor trim before converting to ADC code. Hardware TSHUT is configured at registration and resume through `set_tshut_mode()` and `set_tshut_temp()`, clamped to `RK_MAX_TEMP`, and can target CRU reset or GPIO/PMIC depending on DT or chip defaults. The IRQ thread acknowledges hardware status and updates all thermal zones.

Calibration and trim: newer chips can provide `get_trim_code()`, with controller-level `trim_base`, `trim_base_frac`, and fallback `trim`, plus per-channel child-node `trim`. Trim code is converted to a temperature offset using a chip `trim_slope`.

State and persistence: state lives in clocks, reset, GRF settings, conversion registers, alarm registers, TSHUT registers, and per-sensor trim offsets. Suspend disables zones and controller, turns off clocks, and selects sleep pinctrl state. Resume re-enables clocks, resets and reinitializes hardware, reprograms TSHUT for every channel, restarts auto conversion, reenables zones, and restores default pinctrl.

Dependencies and integration points: OF compatibles for PX30, RV1108, RK3228, RK3288, RK3328, RK3366, RK3368, RK3399, RK3568, RK3576, and RK3588; syscon GRF; NVMEM cells; reset controller; clocks; pinctrl PM; thermal OF; hwmon.

Risks: conversion tables are hardware-specific and interpolation assumes monotonic order; missing required GRF fails probe on selected SoCs; child `reg` values outside channel count silently lose trim; alarm programming ignores the low trip; `rockchip_configure_from_dt()` ignores trim-configuration return value, which can hide trim-read errors; suspend uses `clk_disable()` rather than unprepare because devm enabled clocks were already prepared.

Test signals: compile all compatible chip data; test ADC increment and decrement conversion boundaries; set high trips and verify IRQ update; verify TSHUT programming for CRU and GPIO modes; boot with and without NVMEM trim cells; suspend/resume and confirm TSHUT/auto conversion are restored; check GRF-required platforms fail cleanly without `rockchip,grf`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/rockchip_thermal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/samsung/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/thermal/samsung/Kconfig

Purpose: Kconfig entry for the Samsung Exynos Thermal Management Unit driver.

Important symbol: `EXYNOS_THERMAL`, a tristate option depending on `THERMAL_OF` and `HAS_IOMEM`. Its help text describes TMU initialization, temperature reporting, and cooling action via supported Exynos SoC configuration data.

Control flow and integration: enabling this symbol causes `samsung/Makefile` to build the composite `exynos_thermal` object from `exynos_tmu.o`. The `THERMAL_OF` dependency matches the driver's use of `devm_thermal_of_zone_register()`.

State and persistence: no runtime state. It controls only build inclusion.

Risks and test signals: dependency drift would surface as missing OF thermal or MMIO APIs. Test with `CONFIG_EXYNOS_THERMAL=m`, `=y`, and COMPILE_TEST-style builds where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/samsung/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/samsung/Makefile -->
# sources/distributed-fs/ceph-client/drivers/thermal/samsung/Makefile

Purpose: Kbuild glue for Samsung thermal drivers.

Important entries: `obj-$(CONFIG_EXYNOS_THERMAL) += exynos_thermal.o` and `exynos_thermal-y := exynos_tmu.o`. This builds `exynos_tmu.c` as a composite object named `exynos_thermal`.

Control flow and integration: there are no conditional sub-objects or generated files. The composite object naming means module identity differs from the source basename but the platform driver name remains `exynos-tmu`.

State, risks, and test signals: no runtime state. Risks are limited to drift between Kconfig symbol and object names. Verify module and built-in builds and ensure the expected platform alias remains emitted by `exynos_tmu.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/samsung/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/samsung/exynos_tmu.c -->
# sources/distributed-fs/ceph-client/drivers/thermal/samsung/exynos_tmu.c

Purpose: Samsung Exynos TMU driver supporting Exynos3250, 4210, 4412, 5250, 5260, 5420, 5433, and Exynos7 variants. It maps SoC-specific register layouts to common thermal-zone operations for reading temperature, programming trips, handling interrupts, optional emulation, and PM.

Important types and functions: `enum soc_type`, `struct exynos_tmu_data`, `temp_to_code()`, `code_to_temp()`, `sanitize_temp_error()`, `exynos_tmu_initialize()`, `exynos_thermal_zone_configure()`, SoC-specific set-low/high/critical and initialize/control/read functions, `exynos_tmu_threaded_irq()`, `exynos_map_dt_data()`, `exynos_set_trips()`, `exynos_tmu_probe()`, and suspend/resume callbacks.

Control flow: probe allocates `exynos_tmu_data`, optionally enables the `vtmu` regulator, maps DT data and chooses callback functions based on compatible, prepares clocks including optional triminfo and special clocks, initializes hardware and trim data, registers thermal zone 0, configures critical trip threshold, requests a shared rising threaded IRQ, and enables TMU control.

Temperature and calibration: TMU raw codes convert to Celsius through one-point or two-point calibration using `temp_error1` at 25 C and `temp_error2` at 85 C. Trim values are sanitized against SoC-specific min/max fallback ranges. Exynos5433 reads sensor ID and calibration mode from trim info and can switch to two-point calibration.

Trip and IRQ behavior: `set_trips()` enables/disables low and high threshold interrupts via SoC callback methods. Critical trip setup is performed once from the thermal zone's critical trip. IRQ handling updates the zone, clears pending interrupts through the selected register layout, and leaves detailed interrupt cause handling as a TODO.

State and persistence: driver state stores base addresses, clocks, calibration values, selected callbacks, thermal zone, and enabled flag. Hardware state includes control register, threshold registers, interrupt enables/pending state, and optional emulation registers. Remove disables TMU and unprepares clocks. Suspend disables TMU; resume reinitializes and enables it.

Dependencies and integration points: DT compatibles, OF address and IRQ mapping, thermal OF, regulator API, multiple clocks, optional thermal emulation, Exynos thermal DT binding calibration constants, and IRQ subsystem.

Risks: callback selection in `exynos_map_dt_data()` is dense and SoC-specific; missing critical trips fail most SoCs except Exynos5433 special case; Exynos5420 external triminfo requires a second MMIO resource and clock; some SoCs lack true hardware critical handling and use normal interrupts; clock enable/disable is manually paired inside locks.

Test signals: boot one representative for 4210, 4412/5420, 5433, and Exynos7 paths; verify one-point and two-point calibration; set low/high trips and confirm interrupt enables; trigger IRQ and ensure pending bits clear; test thermal emulation when enabled; suspend/resume and confirm TMU reinitialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/samsung/exynos_tmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/spear_thermal.c -->
# sources/distributed-fs/ceph-client/drivers/thermal/spear_thermal.c

Purpose: simple ST SPEAr thermal sensor driver for `st,thermal-spear1340`. It enables the sensor register block and clock, registers a tripless thermal zone, and reports the low 7 bits of the sensor register as Celsius.

Important functions and types: `struct spear_thermal_dev`, `thermal_get_temp()`, `spear_thermal_probe()`, `spear_thermal_exit()`, `spear_thermal_suspend()`, and `spear_thermal_resume()`.

Control flow: probe requires DT property `st,thermal-flags`, maps MMIO, gets and enables the clock, writes the flags to enable the sensor, registers `spear_thermal` as a tripless thermal zone, enables it, and stores the thermal-zone pointer as driver data. Remove unregisters the zone, clears enable flags, and disables the clock.

Temperature path: `thermal_get_temp()` reads the MMIO register, masks `0x7f`, multiplies by 1000, and returns milli-Celsius. There is no calibration or threshold logic in this driver.

State and persistence: driver state is only base address, clock, and enable flags. Suspend clears the flags and disables the clock; resume enables the clock and rewrites the flags.

Dependencies and integration points: platform MMIO, clock API, DT property `st,thermal-flags`, tripless thermal-zone API, and PM sleep ops.

Risks: no `clk_prepare()` is called, only `clk_enable()`, so it assumes the clock is already prepared or provider permits this path; no OF thermal binding integration or trips; the required post-enable data-ready delay is documented but not enforced at probe or resume; temperature conversion is raw and uncalibrated.

Test signals: verify DT property validation; test clock-enable failure paths; read thermal zone after enable and after resume; ensure remove/suspend clears configured flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/spear_thermal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/sprd_thermal.c -->
# sources/distributed-fs/ceph-client/drivers/thermal/sprd_thermal.c

Purpose: Spreadtrum/Unisoc thermal controller driver for UMS512. It configures monitoring periods, reads efuse calibration, initializes child sensors, exposes each as an OF thermal zone, and enables hardware overheat protection.

Important types and functions: `struct sprd_thermal_data`, `struct sprd_thermal_sensor`, `struct sprd_thm_variant_data`, `sprd_thm_cal_read()`, `sprd_thm_sensor_calibration()`, `sprd_thm_rawdata_to_temp()`, `sprd_thm_temp_to_rawdata()`, `sprd_thm_set_ready()`, `sprd_thm_sensor_init()`, `sprd_thm_probe()`, PM helpers, and `sprd_thm_remove()`.

Control flow: probe gets match data, maps MMIO, validates child sensor count, enables the `enable` clock, writes monitor/detection periods, reads global calibration sign and ratio, iterates child sensor nodes, reads each `reg`, derives per-sensor calibration from `sen_delta_cal`, programs overheat/hot thresholds, registers a thermal zone for each sensor, sets controller ready/enabled state, waits for first temperature data, enables all zones, and stores driver data.

Temperature path: each `get_temp` reads a 10-bit raw value from `SPRD_THM_TEMP(id)`, clamps it, and applies `T = cal_slope * raw - cal_offset`. Inverse conversion programs OTP and hot thresholds. The only variant currently has ideal slope `262` and ideal offset `66400`.

State and persistence: persistent calibration is in NVMEM cells `thm_sign_cal`, `thm_ratio_cal`, and per-sensor `sen_delta_cal`. Runtime state includes sensor pointers indexed by ID, ratio sign/offset, clock, and MMIO registers for thresholds, monitor periods, sensor enables, and interrupt bits.

Dependencies and integration points: OF child sensor nodes, NVMEM cells, enabled clock, thermal OF zones, system sleep PM, and hardware PMIC shutdown interrupt path. The driver intentionally enables hardware interrupt bits without registering a Linux IRQ handler because hardware can notify PMIC automatically.

Risks: `sprd_thm_sensor_calibration()` comments mention default calibration but returns error if `sen_delta_cal` is missing; child sensor IDs are used as indexes and must be contiguous for later loops over `nr_sensors`; `sprd_thm_wait_temp_ready()` polls for `!(val & SPRD_THM_TEMPER_RDY)`, which depends on hardware's inverted-ready semantics; overheat IRQ is hardware-only from Linux's perspective.

Test signals: validate NVMEM cell presence and bad length handling; boot with multiple child sensors and non-contiguous IDs to catch indexing assumptions; compare raw/temp conversions; test suspend/resume reprograms enables and waits for data; verify hardware overheat thresholds are written.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/sprd_thermal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/st/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/thermal/st/Kconfig

Purpose: Kconfig entries for STMicroelectronics thermal drivers.

Important symbols: `ST_THERMAL` enables the shared STi thermal core; `ST_THERMAL_MEMMAP` selects `ST_THERMAL` and builds memory-mapped STi sensor support; `STM32_THERMAL` builds the STM32 thermal framework driver and depends on `MACH_STM32MP157`, defaulting to yes for that machine.

Control flow and integration: symbols map to objects in `st/Makefile`. `ST_THERMAL_MEMMAP` uses the shared exported functions from `st_thermal.c`, while `STM32_THERMAL` is independent and implemented in `stm_thermal.c`.

State and persistence: build-time only.

Risks and test signals: `ST_THERMAL_MEMMAP` selects rather than depends on the shared core, which is correct for its exported helpers. Test all three symbols as modules and built-ins, especially the composite dependency between `st_thermal.o` and `st_thermal_memmap.o`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/st/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/st/Makefile -->
# sources/distributed-fs/ceph-client/drivers/thermal/st/Makefile

Purpose: Kbuild mapping for ST thermal drivers.

Important entries: `CONFIG_ST_THERMAL` builds `st_thermal.o`, `CONFIG_ST_THERMAL_MEMMAP` adds `st_thermal_memmap.o`, and `CONFIG_STM32_THERMAL` builds `stm_thermal.o`.

Control flow and integration: the shared STi core is built as its own object and exports registration/PM helpers for the memory-mapped variant. STM32 is separate.

State, risks, and test signals: no runtime state. Risks are limited to Kconfig/object drift and module dependency between memmap and core. Compile with `ST_THERMAL_MEMMAP=m` and ensure exported symbols resolve.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/st/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/st/st_thermal.c -->
# sources/distributed-fs/ceph-client/drivers/thermal/st/st_thermal.c

Purpose: shared core for STi thermal sensor drivers. It provides common regmap-field allocation, clock/power sequencing, calibration, thermal-zone registration, hwmon exposure, unregister logic, and PM callbacks for backend-specific ST thermal implementations.

Important APIs and functions: exported `st_thermal_register()`, `st_thermal_unregister()`, and `st_thermal_pm_ops`; internal `st_thermal_alloc_regfields()`, `st_thermal_sensor_on()`, `st_thermal_sensor_off()`, `st_thermal_calibration()`, and `st_thermal_get_temp()`.

Control flow: backend probe calls `st_thermal_register()` with its OF match table. The core allocates `struct st_thermal_sensor`, resolves compatible data, initializes a backend regmap, allocates common and backend-specific regfields, gets the `thermal` clock, optionally registers/enables IRQs, powers the sensor, writes default calibration if bootloader did not, registers OF thermal zone 0, stores driver data, and adds hwmon sysfs.

Temperature path: `st_thermal_get_temp()` checks overflow through a regmap field, reads raw temperature data, applies `temp_adjust_val`, multiplies by 1000, and returns milli-Celsius.

State and persistence: backend compatible data supplies regfields, calibration value, adjustment, critical temperature, and ops. Runtime state includes regmap fields, clock, thermal zone, and backend private MMIO or syscon state. Calibration is written to hardware only if the register field is empty.

Dependencies and integration points: regmap/regmap_field, backend `st_thermal_sensor_ops`, OF match data, clock API, thermal OF, hwmon, platform driver data, and exported PM ops used by `st_thermal_memmap.c`.

Risks: `devm_thermal_add_hwmon_sysfs()` return is ignored; unregister mixes devm thermal unregister with manual hwmon removal; backend `register_enable_irq()` runs before power-on, so backend IRQ enable must tolerate that ordering; missing compatible data or ops fails probe.

Test signals: backend probe/remove with MMIO regmap; overflow bit returns `-EIO`; calibration already present versus default write; suspend/resume powers off/on and reenables IRQs; symbol resolution when built as modules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/st/st_thermal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/st/st_thermal.h -->
# sources/distributed-fs/ceph-client/drivers/thermal/st/st_thermal.h

Purpose: internal header for STi thermal core and backend drivers. It defines common register-field IDs, power states, backend operation callbacks, compatible data, runtime sensor state, and exported registration/PM symbols.

Important types: `enum st_thermal_regfield_ids`, `enum st_thermal_power_state`, `struct st_thermal_sensor_ops`, `struct st_thermal_compat_data`, and `struct st_thermal_sensor`.

Control flow role: backend drivers fill `st_thermal_compat_data` and `st_thermal_sensor_ops`; the shared core consumes them in `st_thermal_register()`. The header's `MAX_REGFIELDS` sets the size contract for backend regfield arrays.

State model: `struct st_thermal_sensor` carries the device, thermal zone, ops, compatible data, clock, regmap, common fields (`dcorrect`, `overflow`, `temp_data`), backend fields (`pwr`, `int_thresh_hi`, `int_enable`), IRQ, and optional MMIO base.

Dependencies and integration points: Linux platform, interrupt, regmap, and thermal APIs. Exports `st_thermal_register()`, `st_thermal_unregister()`, and `st_thermal_pm_ops` for backend modules.

Risks: `INT_THRESH_HI` and `TEMP_PWR` both use enum value 0 because they are mutually exclusive backend field meanings; careless backend arrays can allocate the wrong field. The closing comment names `__STI_RESET_SYSCFG_H` rather than the actual guard, a harmless but confusing documentation drift.

Test signals: compile core and memmap backends; verify backend regfield arrays cover all common IDs; inspect suspend/resume symbol linkage in module builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/st/st_thermal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/st/st_thermal_memmap.c -->
# sources/distributed-fs/ceph-client/drivers/thermal/st/st_thermal_memmap.c

Purpose: memory-mapped STi thermal backend for the shared ST thermal core, currently matching `st,stih407-thermal`. It defines register fields, power control, IRQ threshold programming, regmap initialization, and platform driver glue.

Important functions and types: `st_mmap_thermal_regfields`, `st_mmap_thermal_trip_handler()`, `st_mmap_power_ctrl()`, `st_mmap_alloc_regfields()`, `st_mmap_enable_irq()`, `st_mmap_register_enable_irq()`, `st_mmap_regmap_init()`, `st_mmap_sensor_ops`, and `st_407_cdata`.

Control flow: probe delegates to `st_thermal_register()` with the memmap match table. The backend maps MMIO, creates a regmap, allocates high-threshold and interrupt-enable regfields in addition to common fields, registers a threaded rising IRQ, writes the critical threshold adjusted for raw sensor offset, and enables the interrupt.

Temperature and trip behavior: actual temperature reads are handled by `st_thermal.c`; this backend only programs the hardware interrupt high threshold to `crit_temp - temp_adjust_val`. The IRQ handler updates the thermal zone.

State and persistence: compatible data defines default calibration `16`, temperature adjustment `-95`, and critical threshold `120` raw C. Runtime hardware state includes power bits `THERMAL_PDN | THERMAL_SRSTN`, threshold register, and interrupt-enable bit.

Dependencies and integration points: shared ST core exports, platform MMIO, regmap MMIO, IRQ subsystem, thermal zone update, OF compatible `st,stih407-thermal`, and shared PM ops.

Risks: IRQ enable can occur before the shared core powers the sensor; the critical threshold is fixed from compatible data rather than thermal-zone trips; register-field index 0 depends on the header's mutually exclusive enum convention; power control writes both PDN and soft reset bits simultaneously as required by hardware.

Test signals: probe with valid MMIO and IRQ; trigger rising IRQ and verify thermal zone update; suspend/resume through shared PM and ensure threshold IRQ is reenabled; verify raw threshold accounts for `temp_adjust_val`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/st/st_thermal_memmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/st/stm_thermal.c -->
# sources/distributed-fs/ceph-client/drivers/thermal/st/stm_thermal.c

Purpose: STM32 digital temperature sensor driver for `st,stm32-thermal`. It configures DTS calibration, reads factory values, converts frequency samples to temperature, supports thermal trip interrupts, and handles PM.

Important functions and types: `struct stm_thermal_sensor`, `stm_enable_irq()`, `stm_thermal_irq_handler()`, `stm_sensor_power_on()`, `stm_sensor_power_off()`, `stm_thermal_calibration()`, `stm_thermal_read_factory_settings()`, `stm_thermal_calculate_threshold()`, `stm_thermal_set_trips()`, `stm_thermal_get_temp()`, `stm_register_irq()`, `stm_thermal_prepare()`, `stm_thermal_probe()`, and PM callbacks.

Control flow: probe maps MMIO, gets `pclk`, disables and clears IRQs, prepares the sensor by reading factory settings and configuring calibration/prescaler, powers on continuous measurement, registers thermal zone 0, requests a threaded IRQ, enables IRQs, and adds hwmon sysfs.

Temperature path: factory settings provide calibration temperature `t0`, frequency `fmt0`, and ramp coefficient. `get_temp()` requires enabled mode, polls `DTS_DR` for nonzero period sample count, computes measured PTAT frequency from `pclk * sampling_time / periods`, and derives milli-Celsius from `(freqM - fmt0) * 1000 / ramp_coeff + t0`.

Trip and IRQ behavior: `set_trips()` converts low and high trip temperatures to threshold sample counts and writes `DTS_ITR1`. Sentinel values disable low/high tracking. The IRQ handler updates the thermal zone, re-enables IRQs based on current low/high flags, and acknowledges all DTS interrupt flags.

State and persistence: runtime state tracks mode, clock, threshold enable flags, IRQ, base, and factory calibration values. Suspend disables IRQs, stops/turns off sensor, and disables the clock. Resume repeats preparation, powers on, updates the zone, and reenables IRQs.

Dependencies and integration points: STM32 PCLK, MMIO registers, thermal OF, threaded IRQ, hwmon sysfs, and PM sleep ops.

Risks: `stm_enable_irq()` appears to map low-enabled to `HIGH_THRESHOLD` and high-enabled to `LOW_THRESHOLD`, which may be intentional hardware polarity but is easy to regress; threshold calculation divides by computed frequency and can fail if calibration is invalid; hwmon add is manual and removal only removes hwmon, relying on devm for zone; factory settings must be nonzero.

Test signals: validate factory calibration read on hardware; call `get_temp` before and after power state changes; set low/high trips and verify register bit placement; trigger IRQ and confirm ack/update; suspend/resume and check continuous measurement restarts; test invalid factory values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/st/stm_thermal.c -->
