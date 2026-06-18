# Research: subset-b-005438 thermal drivers

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/k3_bandgap.c -->
# sources/distributed-fs/ceph-client/drivers/thermal/k3_bandgap.c

Purpose: TI K3 AM654 VTM bandgap thermal driver. It maps the VTM register block, discovers the hardware sensor count from `K3_VTM_DEVINFO_PWR0_OFFSET`, enables each temperature sensor, registers one OF thermal zone per sensor, and exposes hwmon sysfs for userspace monitoring.

Important APIs/types/functions: `struct k3_bandgap` stores the MMIO base; `struct k3_thermal_data` stores per-sensor offsets and thermal-zone state. `vtm_get_best_value()` implements the silicon erratum workaround by averaging the closest pair of three consecutive ADC samples. `k3_bgp_read_temp()` masks the 10-bit `DTEMP` field, validates it against `K3_VTM_ADC_BEGIN_VAL..K3_VTM_ADC_END_VAL`, and indexes `k3_adc_to_temp[]`. `k3_thermal_get_temp()` is the thermal framework callback. `k3_bandgap_probe()` allocates state, maps resources, enables runtime PM, programs sensor control bits, registers zones, and adds hwmon.

Control flow: probe validates lookup-table length, maps MMIO, powers the device with `pm_runtime_get_sync()`, reads the sensor count, allocates per-sensor data, sets `SOC`, `CLRZ`, and `CLKON_REQ`, clears `CBIASSEL`, then calls `devm_thermal_of_zone_register()` for each ID. Runtime reads go thermal zone -> `k3_thermal_get_temp()` -> `k3_bgp_read_temp()` -> MMIO samples -> table conversion.

State/persistence: only MMIO enable bits and runtime PM usage persist while the driver is bound; per-sensor state is devm-managed. Remove drops runtime PM. Dependencies/integration: platform driver matched by `ti,am654-vtm`, thermal OF trip parsing, `thermal_hwmon.h`, MMIO resources, runtime PM.

Risks: invalid hardware ADC codes return `-EINVAL`; sensor count is trusted from hardware; no explicit IRQ/trip programming is present. Table consistency is guarded at probe. Test signals include successful zone registration for all sensor IDs, valid hwmon entries, boundary ADC-code handling, runtime PM failure cleanup, and stable readings under the erratum workaround.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/k3_bandgap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/k3_j72xx_bandgap.c -->
# sources/distributed-fs/ceph-client/drivers/thermal/k3_j72xx_bandgap.c

Purpose: TI J72xx/J721E/J7200 VTM thermal driver. It builds a calibrated ADC-to-temperature table, optionally applies J721E errata i2128 software trimming from fuse registers, programs high-temperature shutdown/alert thresholds, registers one thermal zone per sensor, and restores hardware state across suspend/resume.

Important APIs/types/functions: `struct k3_j72xx_bandgap` owns device, two MMIO windows, per-sensor pointers, and sensor count. `struct k3_thermal_data` stores control/status offsets. `compute_value()` and `init_table()` generate polynomial reference tables from `golden_factors` or `pvt_wa_factors`. `get_efuse_values()`, `create_table_segments()`, and `prep_lookup_table()` derive the calibrated table from trim errors. `k3_bgp_read_temp()` samples three times and indexes `derived_table`. `k3_j72xx_bandgap_temp_to_adc_code()` binary-searches the table for threshold programming. `k3_j72xx_bandgap_init_hw()` enables sensors and configures `MAX_TEMP`/`COOL_DOWN_TEMP` alert limits.

Control flow: probe maps the VTM and config windows, checks match data for errata, maps fuses if needed, uses runtime PM, reads sensor count, allocates per-sensor state plus a temporary reference table and devm `derived_table`, fills calibration tables, initializes hardware, registers each thermal zone, adds hwmon, and frees the temporary table. Runtime reads go through the thermal callback to `derived_table`. Suspend disables runtime PM; resume re-enables PM and reruns hardware initialization.

State/persistence: `derived_table` is global but allocated during probe and shared by all sensors on the device; per-sensor offsets live in devm arrays. Hardware threshold and control registers are reprogrammed on resume. Dependencies: OF compatibles `ti,j721e-vtm` and `ti,j7200-vtm`, three MMIO resources for errata devices, runtime PM, thermal OF, hwmon.

Risks: lookup-table derivation can silently leave interpolated regions if fuse data is malformed; `derived_table` global state limits assumptions about multiple devices; threshold search depends on monotonic table content. Test signals include errata and non-errata probe paths, fuse skip bits, sensor-count handling, suspend/resume reinitialization, alert threshold register values, and invalid ADC code behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/k3_j72xx_bandgap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/khadas_mcu_fan.c -->
# sources/distributed-fs/ceph-client/drivers/thermal/khadas_mcu_fan.c

Purpose: cooling-device driver for Khadas boards where an MCU controls fan speed. It exposes four cooling states, 0 through `MAX_LEVEL` 3, and writes the selected level to the parent Khadas MCU regmap.

Important APIs/types/functions: `struct khadas_mcu_fan_ctx` stores the parent `struct khadas_mcu`, cached fan level, and registered cooling device. `khadas_mcu_fan_set_level()` writes `KHADAS_MCU_CMD_FAN_STATUS_CTRL_REG` through regmap and updates the cache only on success. `khadas_mcu_fan_get_max_state()`, `get_cur_state()`, and `set_cur_state()` implement `thermal_cooling_device_ops`. Probe gets parent driver data, allocates context, and registers a named cooling device with `devm_thermal_of_cooling_device_register()`.

Control flow: thermal governors call `set_cur_state()`, which bounds-checks the state, avoids duplicate writes, and forwards changes to the MCU. Shutdown unconditionally requests level 0. Suspend saves the current level, stops the fan, then restores the cached level so resume can reapply it. Resume writes the cached level.

State/persistence: the only software state is `ctx->level`; actual persistence is in MCU state after regmap writes. Suspend deliberately leaves the cached level unchanged while forcing hardware off. Dependencies/integration: parent MFD `khadas-mcu`, regmap, thermal cooling-device framework, platform ID `khadas-mcu-fan-ctrl`, and the parent OF node for cooling maps.

Risks: if regmap writes fail during shutdown the error is ignored; the cached level can diverge if firmware changes fan state out-of-band; there is no locking around `level`, relying on thermal framework serialization and simple word writes. Test signals include registration under the parent OF node, state bounds, duplicate-state no-op, suspend/resume restore, shutdown level 0 write, and regmap error propagation for governor requests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/khadas_mcu_fan.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/kirkwood_thermal.c -->
# sources/distributed-fs/ceph-client/drivers/thermal/kirkwood_thermal.c

Purpose: Marvell Kirkwood thermal sensor driver. It maps a single sensor register, registers a tripless thermal zone named `kirkwood_thermal`, and converts a valid raw register field into millidegrees Celsius.

Important APIs/types/functions: `struct kirkwood_thermal_priv` stores the MMIO sensor pointer. `kirkwood_get_temp()` reads the register with `readl_relaxed()`, checks the valid bit at offset 9, extracts the 9-bit temperature field at offset 10, and applies the documented formula `Celsius = (322 - reg) / 1.3625`, scaled to millidegrees. `kirkwood_thermal_probe()` maps resource 0, registers and enables the tripless zone, and stores it as platform driver data. `kirkwood_thermal_exit()` unregisters it.

Control flow: probe is linear: allocate private data, map MMIO, register thermal zone, enable it, and store the handle. Thermal reads fail with `-EIO` if the valid bit is clear; otherwise the converted temperature is returned. Remove unregisters the non-devm thermal zone.

State/persistence: only the thermal-zone handle and MMIO pointer are retained. The driver does not program thresholds, clocks, resets, or persistent hardware state. Dependencies/integration: OF compatible `marvell,kirkwood-thermal`, platform MMIO, thermal core tripless zone API.

Risks: invalid-bit handling means early or transient hardware reads surface as `-EIO`; arithmetic uses unsigned long constants and assumes the raw field stays in documented range; no hwmon sysfs is added. Test signals include valid/invalid register reads, formula spot checks, enable failure cleanup, and remove-time unregister.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/kirkwood_thermal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/loongson2_thermal.c -->
# sources/distributed-fs/ceph-client/drivers/thermal/loongson2_thermal.c

Purpose: Loongson-2 thermal driver for LS2K1000 and LS2K2000. It registers a thermal zone, reads temperature through SoC-specific formulas, programs low/high hardware trip registers from thermal framework set-trips callbacks, and services thermal interrupts.

Important APIs/types/functions: `struct loongson2_thermal_chip_data` supplies selected sensor index and flags, notably `LS2K2000_THSENS_OUT_FLAG` for a separate output register resource. `struct loongson2_thermal_data` stores control/temp MMIO and chip data. `loongson2_set_ctrl_regs()` writes threshold registers with Celsius offset by `HECTO` and optional enable bit. `loongson2_2k1000_get_temp()` reads `LOONGSON2_THSENS_OUT_REG`; `loongson2_2k2000_get_temp()` reads the separate temp resource and applies `(raw * 820 / 0x4000 - 311) * KILO`. `loongson2_thermal_irq_thread()` acknowledges interrupts and updates the thermal zone.

Control flow: probe maps control registers and, for LS2K2000, temp registers; gets IRQ; acknowledges current interrupt status; disables thresholds initially; scans thermal OF zone IDs 0..3 until registration succeeds; registers a threaded IRQ; and adds hwmon. Runtime `set_trips()` converts millidegree inputs to degrees and enables hardware thresholds.

State/persistence: threshold register state persists in hardware; software stores only MMIO pointers and match data. Dependencies: OF compatibles `loongson,ls2k1000-thermal` and `loongson,ls2k2000-thermal`, threaded IRQs, thermal OF, hwmon.

Risks: the probe loop treats `-ENODEV` as fatal but continues on other errors, which is unusual and should be checked against thermal OF semantics; threshold clamping uses `clamp(-40, low, high)` and `clamp(125, low, high)` ordering that deserves tests; no remove/suspend path reprograms thresholds. Test signals include both chip formulas, IRQ acknowledge/update, thermal-zone ID probing, set-trip register encoding, and hwmon creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/loongson2_thermal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/max77620_thermal.c -->
# sources/distributed-fs/ceph-client/drivers/thermal/max77620_thermal.c

Purpose: Maxim MAX77620 PMIC junction temperature thermal driver. The PMIC exposes threshold status rather than a continuous die temperature, so the driver reports nominal 100 C, alarm1 120 C, or alarm2 140 C based on status bits and updates the thermal framework from alarm IRQs.

Important APIs/types/functions: `struct max77620_therm_info` stores the parent regmap, thermal zone, IRQs, and device pointer. `max77620_thermal_read_temp()` reads `MAX77620_REG_STATLBT` and maps `MAX77620_IRQ_TJALRM1_MASK`/`TJALRM2_MASK` to fixed millidegree temperatures. `max77620_thermal_irq()` logs warning/critical messages depending on which shared IRQ fired, then calls `thermal_zone_device_update()`. Probe obtains two IRQs, parent regmap, inherits parent OF node, registers thermal zone 0, and requests both threaded IRQs.

Control flow: thermal reads are pure regmap status reads. IRQs are asynchronous hints that status changed; the framework rereads via the zone callback. All allocations and registrations are devm-managed.

State/persistence: no mutable driver state beyond handles; hardware status and parent PMIC interrupt controller provide persistence. Dependencies/integration: MAX77620 MFD definitions and regmap, platform ID `max77620-thermal`, thermal OF, two shared threaded IRQs.

Risks: temperatures are coarse estimates, not measurements; missing either IRQ fails probe with `-EINVAL`; `device_set_of_node_from_dev()` ties thermal-zone configuration to parent node lifetime. Test signals include status-bit priority when both alarms are set, IRQ-triggered updates, parent regmap absence, missing IRQs, and OF thermal trip registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/max77620_thermal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/mediatek/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/thermal/mediatek/Kconfig

Purpose: Kconfig menu for MediaTek thermal drivers. It gates the MediaTek submenu on `THERMAL_OF` and exposes legacy AUXADC, LVTS, and LVTS debugfs options.

Important entries: `MTK_THERMAL` is the parent tristate and documents MediaTek software thermal solutions. `MTK_SOC_THERMAL` enables the AUXADC controller driver and depends on `HAS_IOMEM`. `MTK_LVTS_THERMAL` enables the Low Voltage Thermal Sensor driver and depends on `HAS_IOMEM`. `MTK_LVTS_THERMAL_DEBUGFS` is a bool depending on `MTK_LVTS_THERMAL && DEBUG_FS`.

Control flow/integration: selecting the parent makes the child symbols visible. The Makefile maps the two implementation objects to `CONFIG_MTK_SOC_THERMAL` and `CONFIG_MTK_LVTS_THERMAL`; debugfs affects conditional code inside `lvts_thermal.c`.

State/persistence: no runtime state; build-time configuration only. Dependencies: thermal OF framework and MMIO support; LVTS debugfs additionally depends on debugfs.

Risks: the help text has a typo in "mechaisms"; the parent symbol can be enabled without selecting either concrete driver. Test signals are Kconfig visibility, module/built-in combinations, debugfs code exclusion when disabled, and successful allmodconfig-style dependency resolution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/mediatek/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/mediatek/Makefile -->
# sources/distributed-fs/ceph-client/drivers/thermal/mediatek/Makefile

Purpose: build mapping for MediaTek thermal drivers.

Important entries: `obj-$(CONFIG_MTK_SOC_THERMAL) += auxadc_thermal.o` builds the legacy AUXADC thermal driver. `obj-$(CONFIG_MTK_LVTS_THERMAL) += lvts_thermal.o` builds the LVTS driver.

Control flow/integration: this file is consumed by Kbuild under `drivers/thermal/mediatek`. It matches the symbols declared in the adjacent Kconfig and contains no composite objects or conditional subdirectories.

State/persistence: build-time only. Dependencies are exactly the Kconfig symbols.

Risks/test signals: risk is low; failures would be missing object inclusion, stale symbol names, or module build errors. Test with built-in and module configurations for both symbols and with `CONFIG_MTK_LVTS_THERMAL_DEBUGFS` toggled to ensure it only changes `lvts_thermal.o` contents.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/mediatek/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/mediatek/auxadc_thermal.c -->
# sources/distributed-fs/ceph-client/drivers/thermal/mediatek/auxadc_thermal.c

Purpose: legacy MediaTek SoC thermal driver using thermal controller hardware to trigger AUXADC conversions through AHB-programmed register addresses. It supports multiple SoCs, calibration formats, banked sensor groups, thermal OF registration, and hwmon export.

Important APIs/types/functions: `struct mtk_thermal_data` describes each SoC: sensor counts, bank layouts, AUXADC channel, mux values, controller offsets, calibration version, and APMIXED buffer controls. `struct mtk_thermal` stores MMIO, clocks, calibration fields, banks, lock, and raw conversion function. `raw_to_mcelsius_v1/v2/v3()` implement version-specific conversion. `mtk_thermal_get_bank()`/`put_bank()` serialize bank selection through `PTPCORESEL`. `mtk_thermal_bank_temperature()` reads measurement registers and validates ranges. `mtk_thermal_init_bank()` programs AUXADC/PNP mux addresses, polling, valid masks, and sensor enables. `mtk_thermal_get_calibration_data()` reads `calibration-data` nvmem and dispatches efuse decoders.

Control flow: probe selects match data, maps thermal MMIO, loads calibration defaults/efuse, resolves `mediatek,auxadc` and `mediatek,apmixedsys` phandles and physical addresses, resets hardware, enables `auxadc` and `therm` clocks, configures analog buffer/periodic TS release, selects conversion function, initializes every controller/bank combination, registers thermal zone 0, and adds hwmon. Runtime reads compute the maximum valid temperature across banks.

State/persistence: calibration values, bank lock, conversion function, and clock handles live in devm state; hardware polling/mux configuration persists while powered. Dependencies: OF match table for MT2701/2712/7622/7986/8173/8183/8365, nvmem, clocks, reset, phandles to AUXADC/APMIXEDSYS, thermal OF, hwmon.

Risks: many SoC tables must remain consistent in sensor count, mux arrays, and register offsets; `of_iomap()` mappings are not explicitly unmapped; invalid calibration falls back silently to defaults after info logging; first samples can be invalid for up to about 60 ms. Test signals include calibration-valid and fallback paths per version, bank switching lock behavior, DT phandle failures, clock/reset errors, invalid temperature filtering, and per-SoC table bounds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/mediatek/auxadc_thermal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/mediatek/lvts_thermal.c -->
# sources/distributed-fs/ceph-client/drivers/thermal/mediatek/lvts_thermal.c

Purpose: MediaTek LVTS thermal driver for newer SoCs. It supports multiple LVTS controllers per thermal domain, up to four sensors per controller, efuse calibration byte layouts, immediate/filtered/ATP measurement modes, thermal-zone registration per sensor, threshold interrupts, suspend/resume, optional debugfs, and many platform data tables.

Important APIs/types/functions: `struct lvts_data` captures platform commands, controller tables, calibration layout, coefficients, offsets, and conversion ops. `struct lvts_ctrl_data` and `struct lvts_sensor_data` map DT thermal IDs to sensor slots and efuse byte offsets. `lvts_sensor`, `lvts_ctrl`, and `lvts_domain` hold runtime sensor, controller, and domain state. Conversion is provided through platform ops such as MT7988 and MT8196 raw/temp functions. `lvts_calibration_read()` concatenates all named nvmem cells; `lvts_calibration_init()` decodes per-sensor calibration and default fallback; `lvts_golden_temp_init()` derives global golden temperature offset. `lvts_ctrl_initialize()`, `lvts_ctrl_calibrate()`, `lvts_ctrl_configure()`, and `lvts_ctrl_start()` bring hardware up. `lvts_set_trips()` writes low/high offset thresholds; `lvts_irq_handler()` maps interrupt status bits back to sensor thermal zones.

Control flow: probe gets match data, maps MMIO, acquires reset/clock, reads calibration, allocates controllers, initializes each controller's sensor slots and calibration, resets/connects/configures/starts hardware, registers each valid sensor as a thermal zone with hwmon, requests the domain IRQ, creates debugfs when enabled, and stores driver data. Interrupts scan all controllers, update affected zones, and clear W1C status. Suspend disables monitoring/controllers and clock; resume re-enables them.

State/persistence: calibration arrays, threshold caches, sensor register pointers, and global `golden_temp`/offset drive conversions. Hardware monitor enable, threshold, and ASIF command state persists while powered but is restored on resume. Dependencies: nvmem, clocks, resets, thermal OF, IRQs, dt-bindings thermal IDs, optional debugfs, hwmon.

Risks: platform tables are dense and easy to misalign with efuse layouts or DT IDs; global golden-temperature state assumes compatible device usage; threshold programming must respect raw conversion direction; interrupt masks must match sensor slots. Test signals include per-compatible probe, missing/invalid nvmem fallback, raw/temp round trips, trip programming, IRQ-to-zone mapping, suspend/resume restoration, and debugfs register visibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/mediatek/lvts_thermal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/pcie_cooling.c -->
# sources/distributed-fs/ceph-client/drivers/thermal/pcie_cooling.c

Purpose: PCIe cooling-device helper that throttles a PCIe port by lowering target link speed. It exposes thermal cooling states as inverse PCIe speed levels.

Important APIs/functions: `pcie_cooling_get_max_level()` returns the number of throttling steps from 2.5 GT/s up to the subordinate bus maximum. `pcie_cooling_get_cur_level()` maps current bus speed to cooling state, where state 0 means maximum speed. `pcie_cooling_set_cur_level()` converts a requested cooling state back to `enum pci_bus_speed` and calls `pcie_set_target_speed(port, speed, true)`. `pcie_cooling_device_register()` creates a named cooling device with `kasprintf()` and `thermal_cooling_device_register()`. `pcie_cooling_device_unregister()` unregisters it.

Control flow: users of the helper pass a PCIe port with a subordinate bus. Thermal governors operate on cooling states; the helper maps those states to PCIe bandwidth-control requests. Static assertions verify that enum speed values are contiguous for arithmetic.

State/persistence: no private state beyond `cdev->devdata` pointing to the PCI device; target speed persists through PCIe bandwidth-control machinery. Dependencies: PCI core, `pci-bwctrl`, thermal cooling-device framework.

Risks: assumes `port->subordinate` is valid and bus speed enum values remain contiguous; cooling-state semantics are inverse of performance, which can cause mistakes in callers; registration is non-devm and caller must unregister. Test signals include state/speed mapping for every supported speed, set-target errors, subordinate absence protection by callers, and unregister on caller teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/pcie_cooling.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/qcom/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/thermal/qcom/Kconfig

Purpose: Kconfig entries for Qualcomm thermal drivers: TSENS, SPMI ADC thermal monitor, SPMI PMIC temperature alarm, and LMh.

Important entries: `QCOM_TSENS` depends on `NVMEM_QCOM_QFPROM` and `ARCH_QCOM || COMPILE_TEST`; it builds the multi-version TSENS thermal sysfs driver. `QCOM_SPMI_ADC_TM5` depends on `OF && SPMI && IIO`, selects `REGMAP_SPMI` and `QCOM_VADC_COMMON`, and enables ADC threshold monitor support. `QCOM_SPMI_TEMP_ALARM` has similar OF/SPMI/IIO dependencies and selects `REGMAP_SPMI`. `QCOM_LMH` depends on `ARCH_QCOM || COMPILE_TEST` and selects `QCOM_SCM`.

Control flow/integration: symbols are consumed by the adjacent Makefile. The dependencies align with each driver's required firmware, bus, IIO, regmap, or SCM interfaces.

State/persistence: build-time only. Risks: enabling TSENS requires QFPROM even for platforms whose calibration path may be different; LMh depends on secure monitor calls, so build coverage differs from runtime availability. Test signals include dependency resolution, module builds for each option, and compile-test coverage outside ARCH_QCOM.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/qcom/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/qcom/Makefile -->
# sources/distributed-fs/ceph-client/drivers/thermal/qcom/Makefile

Purpose: Kbuild mapping for Qualcomm thermal drivers.

Important entries: `obj-$(CONFIG_QCOM_TSENS) += qcom_tsens.o` and `qcom_tsens-y += tsens.o tsens-v2.o tsens-v1.o tsens-v0_1.o tsens-8960.o` compose the TSENS core plus version backends. Other mappings build `qcom-spmi-adc-tm5.o`, `qcom-spmi-temp-alarm.o`, and `lmh.o` from their matching Kconfig symbols.

Control flow/integration: TSENS version files are not standalone modules; they link into `qcom_tsens`. The SPMI and LMh drivers build as independent objects.

State/persistence: build-time only. Risks/test signals: stale object lists would break compatible data references in the TSENS core; test by building `QCOM_TSENS=m/y` and each independent symbol as module and built-in.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/qcom/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/qcom/lmh.c -->
# sources/distributed-fs/ceph-client/drivers/thermal/qcom/lmh.c

Purpose: Qualcomm Limits Management Hardware initialization and IRQ bridge driver. It programs secure firmware LMh thermal/current/reliability/BCL thresholds and exposes a child IRQ domain so cpufreq can handle LMh mitigation interrupts.

Important APIs/types/functions: `struct lmh_hw_data` stores MMIO base, parent IRQ, and IRQ domain. `lmh_handle_irq()` maps hardware event 0 into the child IRQ and calls `generic_handle_irq()`. `lmh_enable_interrupt()` clears DCVS interrupt status and enables the parent IRQ; `lmh_disable_interrupt()` disables it. `lmh_irq_map()` installs the simple IRQ chip and lockdep class. `lmh_probe()` validates SCM availability, maps MMIO, resolves the associated CPU phandle, reads three threshold properties, maps CPU IDs to LMh cluster node IDs, optionally enables LMh algorithms for SDM845, programs thresholds through `qcom_scm_lmh_dcvsh()`, creates a one-cell IRQ domain, and requests the parent IRQ with no auto-enable.

Control flow: firmware programming happens before IRQ setup. The parent IRQ remains disabled until a consumer enables the mapped child IRQ. On interrupt, the handler forwards to the child domain rather than doing thermal policy locally.

State/persistence: thresholds and algorithm enablement persist in LMh firmware/hardware; driver state is MMIO/IRQ-domain handles. Dependencies: QCOM SCM, OF CPU phandle and properties, IRQ domains, platform MMIO/IRQ. Compatibles include `qcom,sc8180x-lmh`, `qcom,sdm845-lmh`, and `qcom,sm8150-lmh`.

Risks: CPU ID to cluster mapping is hard-coded to 0 and 4; failures after `irq_domain_create_linear()` require cleanup only on request-IRQ failure; SCM availability causes probe deferral or failure depending on call. Test signals include missing threshold properties, CPU phandle mapping, SCM error propagation, child IRQ enable/disable, parent IRQ forwarding, and SDM845 algorithm enable path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/qcom/lmh.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/qcom/qcom-spmi-adc-tm5.c -->
# sources/distributed-fs/ceph-client/drivers/thermal/qcom/qcom-spmi-adc-tm5.c

Purpose: Qualcomm SPMI PMIC ADC thermal monitor driver for ADC_TM5, ADC_TM high-current, and ADC_TM5 gen2 peripherals. It binds PMIC ADC threshold channels to thermal zones, converts trip temperatures into ADC threshold codes, programs recurring measurements, and reports threshold IRQs.

Important APIs/types/functions: `struct adc_tm5_data` abstracts generation-specific full-scale value, decimation/hw-settle tables, configure/disable/init/isr operations, and IRQ name. `struct adc_tm5_channel` stores DT channel number, ADC channel, calibration/prescale/timing, IIO channel, flags, and thermal zone. `struct adc_tm5_chip` stores regmap, base, channel array, global sampling settings, and gen2 mutex. `adc_tm5_get_temp()` reads processed IIO temperatures. `adc_tm5_configure()` programs gen1 channel blocks; `adc_tm5_gen2_configure()` serializes shared gen2 programming and performs conversion handshake. `adc_tm5_isr()` and `adc_tm5_gen2_isr()` decode low/high status and update affected zones.

Control flow: probe obtains parent regmap and base address, gets IRQ, parses child channel DT nodes, initializes hardware for the selected generation, registers thermal zones for available channels, adds hwmon, and requests the threaded IRQ. Thermal `set_trips()` disables a channel when both bounds are unbounded or calls the generation-specific configure routine. High temperatures map to low voltage thresholds for thermistors; low temperatures map to high voltage thresholds.

State/persistence: channel flags mirror programmed measurement and interrupt enables, especially for gen2 status handling. Hardware register blocks hold thresholds and conversion configuration. Dependencies: SPMI regmap, IIO channels, Qualcomm VADC scaling helpers, OF child nodes, thermal OF, hwmon.

Risks: DT parsing must keep PMIC ADC and thermal monitor channel numbers consistent; gen2 shared register programming relies on mutex and handshake timeout; threshold polarity is easy to invert; unavailable thermal zones are skipped but channels remain parsed. Test signals include gen1/gen2 init, child DT validation, IIO read errors, trip-to-code conversion, low/high IRQ updates, gen2 status clear, and conversion handshake timeout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/qcom/qcom-spmi-adc-tm5.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/qcom/qcom-spmi-temp-alarm.c -->
# sources/distributed-fs/ceph-client/drivers/thermal/qcom/qcom-spmi-temp-alarm.c

Purpose: Qualcomm QPNP SPMI PMIC temperature alarm driver. It handles GEN1, GEN2 revisions, and TEMP_ALARM_LITE blocks, optionally reads a real ADC channel, otherwise estimates temperature from over-temperature stages, configures PMIC shutdown/threshold registers from thermal trips, and updates the thermal framework on alarm IRQs.

Important APIs/types/functions: `struct spmi_temp_alarm_data` holds variant ops, stage maps, threshold sync/config callbacks, and stage reader. `struct qpnp_tm_chip` stores regmap/base, thermal zone, variant data, current temp/stage, threshold map, lock, ADC, and revision flags. `qpnp_tm_get_temp()` returns default temperature before init, ADC value when available, or stage-estimated temperature with hysteresis. `qpnp_tm_update_critical_trip_temp()` selects GEN1/GEN2 threshold sets and optional stage2 shutdown override. GEN2 rev2 uses `TEMP_DAC_STG*` via `qpnp_tm_gen2_rev2_set_temp_thresh()`. LITE uses warning/shutdown maps via `qpnp_tm_lite_set_temp_thresh()`.

Control flow: probe gets parent regmap, base, IRQ, optional IIO ADC, validates PMIC type/subtype/revision, selects variant data, syncs hardware thresholds and initial stage, registers thermal zone before hardware init so trip data is available, configures trip thresholds, force-enables the alarm block, adds hwmon, requests IRQ, and triggers an initial update. IRQ handling simply updates the thermal zone; reads and set-trip paths perform detailed register work under `chip->lock`.

State/persistence: `temp_thresh_map`, `stage`, `temp`, `initialized`, and `require_stage2_shutdown` mirror hardware state and revision constraints. Hardware threshold, DAC, LITE, and alarm enable registers persist in the PMIC. Dependencies: SPMI regmap, optional IIO channel named `thermal`, thermal OF trips, hwmon.

Risks: no-ADC mode reports estimates with hysteresis rather than real temperature; stage2 shutdown override is revision-sensitive; LITE trip 1 is software-only; trip ordering validation is critical for programmable variants. Test signals include subtype/revision selection, ADC and no-ADC reads, critical trip programming, TEMP_DAC bounds, LITE thresholds, IRQ update, default pre-init temperature, and lock-protected concurrent trip/read paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/qcom/qcom-spmi-temp-alarm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/qcom/tsens-8960.c -->
# sources/distributed-fs/ceph-client/drivers/thermal/qcom/tsens-8960.c

Purpose: Qualcomm TSENS backend for MSM8960/APQ8064-era hardware. It supplies version-specific register fields, calibration, enable/disable, and suspend/resume operations to the shared TSENS core.

Important APIs/functions: `tsens_msm8960_slope[]` provides per-sensor slopes. `calibrate_8960()` reads `calib` or `calib_backup` QFPROM data, copies one-point calibration values, assigns slopes, and calls `compute_intercept_slope()`. `enable_8960()` sets sensor enable bits, sleep clock, measurement period, reset, and main enable; for IDs above 5 it enables sensors 6..10 together due to a hardware bug. `disable_8960()` clears sensor enables and sleep clock. `suspend_8960()` saves threshold/control registers and disables measurement; `resume_8960()` resets, restores config/threshold/control. `tsens_8960_regfields[]` maps legacy registers into common field IDs.

Control flow: the TSENS core uses `data_8960` to initialize common regmaps, call calibration, enable sensors, read temperatures through `get_temp_common()`, and manage PM callbacks. Threshold fields are shared for all sensors on this hardware.

State/persistence: calibration intercept/slope is stored in core sensor structs; suspend context stores threshold/control registers. Hardware enable and threshold registers persist until suspend/disable. Dependencies: shared `tsens.h` core, regmap, QFPROM helpers.

Risks: only one-point calibration is available; 8660/8960 sensor-count comments differ from platform data, requiring care; sensors greater than 5 must be enabled as a group. Test signals include primary/backup calibration reads, grouped high-sensor enable, suspend/resume register restoration, threshold field mapping, and temperature reads through common core.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/qcom/tsens-8960.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/qcom/tsens-v0_1.c -->
# sources/distributed-fs/ceph-client/drivers/thermal/qcom/tsens-v0_1.c

Purpose: Qualcomm TSENS v0.1 backend for early SoCs such as 8226, 8909, 8916, 8939, 8974, and 9607. It defines legacy nvmem layouts, calibration fixups, init quirks, register fields, ops, and platform data.

Important APIs/functions: `tsens_8916_nvmem`, `tsens_8974_nvmem`, and backup layout structures describe bit-level QFPROM extraction. `calibrate_8916()` and `calibrate_8974()` read calibration points and compute slopes/intercepts; `fixup_8974_points()` corrects known calibration-point encodings. Init helpers such as `init_8226()`, `init_8909()`, `init_8939()`, and `init_9607()` set sensor counts or mode quirks before common init. `tsens_v0_1_regfields[]` maps SROT/TM fields for the common core. `data_*` structures bind ops/features/fields to SoCs.

Control flow: the TSENS core selects the `data_*` object from its compatible table, then calls the backend init and calibration hooks before registering sensors and using common get-temp/interrupt helpers. This file does not register a platform driver itself; it links into `qcom_tsens`.

State/persistence: extracted calibration data becomes per-sensor slope/intercept in common state. Register layout and feature structures are static. Dependencies: shared TSENS core, nvmem/QFPROM extraction helpers, regmap fields.

Risks: bitfield layouts are SoC-specific and easy to break; backup calibration selection for 8974 is subtle; init quirks must match compatible data. Test signals include nvmem extraction for each layout, invalid calibration handling, 8974 fixups, per-SoC sensor counts, and common-core temperature conversion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/qcom/tsens-v0_1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/qcom/tsens-v1.c -->
# sources/distributed-fs/ceph-client/drivers/thermal/qcom/tsens-v1.c

Purpose: Qualcomm TSENS v1 backend for mid-generation SoCs including generic v1, 8937, 8956, 8976, QCS404-style nvmem, and IPQ5018. It provides calibration, register fields, optional no-RPM initialization, and platform data to the shared TSENS core.

Important APIs/functions: `tsens_qcs404_nvmem` describes legacy calibration format. `calibrate_v1()` delegates to common legacy calibration handling for v1 devices. `tsens_v1_feat` and `tsens_v1_no_rpm_feat` describe feature differences. `tsens_v1_regfields[]` defines common register fields. `init_8956()` and `init_tsens_v1_no_rpm()` handle platform-specific setup, including enabling sensors without RPM firmware involvement. Ops tables combine init/calibrate/get-temp behavior for generic, common, 8956, and IPQ5018 variants. `data_8937`, `data_8956`, `data_8976`, `data_ipq5018`, and generic `data_tsens_v1` expose those combinations.

Control flow: selected platform data drives core initialization; calibration populates sensor conversion state; no-RPM init writes enable/configuration fields where needed; temperature reads use common TSENS routines.

State/persistence: static feature/regfield data plus per-device calibration state owned by the core. Hardware enable bits may be programmed during init for no-RPM variants. Dependencies: shared `tsens.h`, regmap fields, nvmem calibration helpers.

Risks: no-RPM and RPM-managed variants must not share the wrong init path; feature flags determine interrupt and ADC behavior in the core; calibration format assumptions must match QFPROM cells. Test signals include each platform data object, no-RPM enable sequence, QCS404 calibration extraction, valid temperature reads, and suspend/resume behavior inherited from common ops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/qcom/tsens-v1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/qcom/tsens-v2.c -->
# sources/distributed-fs/ceph-client/drivers/thermal/qcom/tsens-v2.c

Purpose: Qualcomm TSENS v2 backend for newer SoCs including generic v2, IPQ8074, IPQ5332/IPQ5424, and MSM8996. It defines feature variants, register fields, calibration from mode/p1/p2 data, no-RPM initialization, and platform data.

Important APIs/functions: `tsens_v2_feat`, `ipq8074_feat`, and `ipq5332_feat` describe capabilities. `tsens_v2_regfields[]` maps v2 SROT/TM fields. `tsens_v2_calibrate_sensor()` calculates per-sensor calibration from two-point or fallback data; `tsens_v2_calibration()` reads calibration mode and sensor points and computes conversion parameters. `init_tsens_v2_no_rpm()` enables/configures TSENS without RPM. Ops tables cover generic v2 and IPQ5332-specific behavior. `data_tsens_v2`, `data_ipq8074`, `data_ipq5332`, `data_ipq5424`, and `data_8996` bind counts/features/ops/fields to platforms.

Control flow: the TSENS core loads the selected platform data, allocates regfields, runs init/calibration hooks, then uses common get-temp and threshold code. Calibration mode determines whether one-point, two-point, or default handling is used.

State/persistence: static data describes hardware; computed calibration is stored in core sensor state. No-RPM init programs enable/configuration bits. Dependencies: shared TSENS core, nvmem/QFPROM helpers, regmap fields.

Risks: per-sensor p1/p2 extraction and mode interpretation are correctness-critical; IPQ feature differences affect interrupts and sensor counts; default calibration can hide bad efuse data. Test signals include two-point calibration math, missing/invalid nvmem fallback, no-RPM init, per-compatible sensor counts, threshold field access, and common get-temp validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/qcom/tsens-v2.c -->
