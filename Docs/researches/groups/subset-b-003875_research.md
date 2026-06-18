# Research Report: subset-b-003875

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/palmas_gpadc.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/palmas_gpadc.c

## Purpose
TI Palmas/TWL603x GPADC IIO driver exposing 16 PMIC ADC channels as voltage or temperature channels, with software-triggered conversions and two hardware auto-conversion threshold event slots. It supports platform data and device-tree current source settings, processed calibrated voltage output for most voltage channels, raw temperature-like channels, and wake-capable threshold IRQs.

## Important APIs, Types, And Functions
`struct palmas_gpadc` is the driver state: parent `struct palmas`, IRQs, current-source settings, calibration table, threshold state, two `struct palmas_adc_event` slots, completion, and mutex. `palmas_gpadc_info[]` stores ideal points and trim registers per channel. IIO entry points are `palmas_gpadc_read_raw`, `read_event_config`, `write_event_config`, `read_event_value`, and `write_event_value`. Conversion helpers are `palmas_gpadc_enable`, `palmas_gpadc_read_prepare`, `palmas_gpadc_start_conversion`, and `palmas_gpadc_get_calibrated_code`. Event programming is centralized in `palmas_adc_configure_events` and `palmas_adc_reset_events`.

## Control Flow
Probe obtains parent Palmas data, parses optional DT properties, requests the software EOC IRQ plus two auto-conversion IRQs, registers the IIO device, then calibrates all trimmed channels by reading trim registers. Direct reads take `adc->lock`, enable realtime GPADC unless the channel is already freerunning for an event, unmask the EOC interrupt, start conversion, wait up to five seconds on `conv_completion`, bulk-read the 12-bit result, optionally calibrate it, then mask/disable again. Auto IRQs disable auto conversion using the documented force/shutdown workaround and push IIO threshold events.

## State And Persistence
State is runtime-only: event enable/channel/direction slots, per-channel threshold values, calibration gains/offsets loaded from PMIC trim registers, and current source choices. Hardware GPADC registers are programmed per read or event update. Suspend/resume only toggles wake on auto IRQs when device wakeup is enabled.

## Dependencies And Integration Points
Depends on the Palmas MFD register and IRQ APIs, IIO direct/event interfaces, platform IRQ layout, and DT bindings such as `ti,palmas-gpadc`, `ti,channel0-current-microamp`, `ti,channel3-current-microamp`, and `ti,enable-extended-delay`. It integrates with system wake through `device_set_wakeup_capable` and IRQ wake.

## Risks
Only two auto-conversion event slots exist, so more threshold users return `-EBUSY`. Threshold conversion relies on fixed datasheet tolerances with TODOs for OF-provided error parameters. If trim reads fail, calibration fields may stay at default values for that channel. Direct read cleanup always disables SW conversion, which is skipped only logically for freerunning channels in prepare; event/read interleavings depend on the mutex discipline. Hardware lockup workaround is critical when disabling AUTO mode.

## Test Signals
Exercise raw and processed reads for calibrated and uncalibrated channels, timeout behavior with missing EOC IRQ, event enable/disable with both rising and falling thresholds, third event rejection, threshold update while enabled, wakeup suspend/resume, and DT current-source boundary mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/palmas_gpadc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/qcom-pm8xxx-xoadc.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/qcom-pm8xxx-xoadc.c

## Purpose
Qualcomm PM8xxx XOADC IIO driver for older PM8018/PM8038/PM8058/PM8921 PMICs. It exposes DT-selected housekeeping ADC channels, performs variant-specific mux/prescale programming, measures mandatory reference channels, and scales raw ADC codes through the common Qualcomm VADC scaling helpers.

## Important APIs, Types, And Functions
`struct xoadc_channel` describes hard-coded hardware muxing, prescale, IIO type, scale function, and RSV reference selector. `struct xoadc_variant` selects channel tables and variant quirks, notably PM8058 broken ratiometric behavior. `struct pm8xxx_xoadc` stores regmap, regulator, parsed channels, calibration graphs, completion, and mutex. Core functions are `pm8xxx_read_channel_rsv`, `pm8xxx_calibrate_device`, `pm8xxx_read_raw`, `pm8xxx_fwnode_xlate`, and `pm8xxx_xoadc_parse_channel`.

## Control Flow
Probe matches a variant, parses child nodes into IIO channels and private channel metadata, fetches the parent regmap and `xoadc-ref` regulator, requests the EOC IRQ, registers the IIO device, then calibrates absolute and ratiometric graphs. A read locates the channel, serializes hardware access, writes AMUX and RSV selections, programs analog/digital parameters and decimation, enables the arbiter twice, requests conversion, waits for completion, reads DATA0/DATA1, and shuts the arbiter down twice. Processed reads call `qcom_vadc_scale`; raw reads return the ADC code.

## State And Persistence
Persistent-in-driver state consists of parsed channel descriptors, calibration graph points generated at probe, and the enabled VREF regulator. Hardware configuration is transient per conversion. No suspend/resume hooks are implemented; regulator lifetime is managed by probe/remove.

## Dependencies And Integration Points
Uses parent PMIC `regmap`, IIO direct mode, fwnode child channel definitions with two-cell `reg`, optional `qcom,ratiometric` and `qcom,decimation`, regulator framework, IRQ completion, and `qcom-vadc-common.c` for scaling and DT decimation parsing.

## Risks
Several channel tables are reconstructed from vendor trees and marked incomplete/untested. Calibration requires 1.25 V, 0.625 V/internal, and MUXOFF channels to be present in DT, so incomplete DTs fail probe. PM8058 ratiometric handling is explicitly a workaround. The wait timeout uses a microsecond conversion constant as jiffies, which is sensitive to HZ and may be shorter than intended on some builds. Register knowledge is best-effort and variant-dependent.

## Test Signals
Probe each compatible with mandatory references present and absent, verify fwnode xlate exact premux/amux matching, compare raw and processed output for absolute/ratiometric channels, test PM8058 RSV quirk paths, regulator error handling, EOC timeout, and channel table coverage for reserved channels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/qcom-pm8xxx-xoadc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/qcom-spmi-adc5-gen3.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/qcom-spmi-adc5-gen3.c

## Purpose
Qualcomm SPMI ADC5 Gen3 driver for PMIC ADC measurements and thermal-monitor sharing. It exposes immediate ADC conversions through IIO, exports helper APIs for an auxiliary ADC thermal-monitor device, and handles SDAM-based handshakes, conversion status clearing, and threshold interrupt dispatch.

## Important APIs, Types, And Functions
`struct adc5_chip` combines IIO state, `struct adc5_device_data` SDAM base/IRQ metadata, channel properties, completion, mutex, ADC data tables, and auxiliary TM linkage. `struct adc5_channel_prop` wraps common ADC/TM channel properties plus a TM flag. Exported namespace APIs include `adc5_gen3_read`, `adc5_gen3_write`, `adc5_gen3_update_dig_param`, `adc5_gen3_poll_wait_hs`, `adc5_gen3_status_clear`, `adc5_gen3_mutex_lock/unlock`, `adc5_gen3_get_scaled_reading`, `adc5_gen3_therm_code_to_temp`, and `adc5_gen3_register_tm_event_notifier`. IIO callbacks are `adc5_gen3_read_raw`, `adc5_gen3_read_label`, and `adc5_gen3_fwnode_xlate`.

## Control Flow
Probe reads multiple `reg` entries as SDAM bases, collects per-SDAM IRQs, requests the VADC SDAM IRQ, parses child channel nodes, optionally creates an auxiliary `adc5_tm_gen3` device for `qcom,adc-tm` channels, then registers IIO. A read waits for handshake readiness, writes SID/channel/timing/digital/average/settle configuration, requests conversion, waits up to 501 ms for completion, reads little-endian channel data, scales through `qcom_adc5_hw_scale`, and clears EOC status. The ISR completes immediate conversions for channel 0, clears conversion faults, and forwards TM high/low status to the registered auxiliary handler.

## State And Persistence
Runtime state includes parsed channel properties, TM channel count, auxiliary device pointer, callback pointer, and SDAM base/IRQ descriptors. Hardware SDAM registers hold per-conversion configuration and status until cleared. No persistent storage exists beyond DT-provided channel definitions.

## Dependencies And Integration Points
Depends on parent SPMI regmap, IIO, auxiliary bus, `qcom-adc5-gen3-common.h`, `qcom-vadc-common.c`, device-tree channel properties (`reg`, labels, decimation, prescale, settle time, averaging, ratiometric, `qcom,adc-tm`), and namespace consumers for ADC TM.

## Risks
The TM handler pointer is called when status bits are present; it assumes auxiliary driver initialization and notifier registration are coordinated. TM channel count is bounded by SDAM capacity minus one. Gen3 immediate conversions currently do not support polling mode. Handshake and conversion timeouts are long because PBS may be busy; failures can delay callers. Exported lock helpers expose internal serialization to auxiliary code, so lock ordering with TM consumers matters.

## Test Signals
Validate multi-SDAM probe, missing IRQ/base failures, channel DT parsing including unsupported channel and invalid timing values, IIO reads under concurrent TM operations, conversion fault handling, EOC clearing, auxiliary creation only when TM channels exist, exported helper scaling, and timeout paths for handshake and conversion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/qcom-spmi-adc5-gen3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/qcom-spmi-adc5.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/qcom-spmi-adc5.c

## Purpose
Qualcomm PMIC ADC5/ADC7 IIO driver for SPMI ADC peripherals. It parses DT-defined channels, programs ADC5 or ADC7 conversion registers, waits by IRQ or polling fallback, and returns processed physical values using hardware-calibrated scaling tables from the common Qualcomm ADC code.

## Important APIs, Types, And Functions
`struct adc5_channel_prop` stores channel number, calibration method/value, SID for ADC7, prescale, decimation, settle time, averaging, scale function, and label. `struct adc5_chip` stores regmap/base, IIO arrays, completion, mutex, polling flag, and `struct adc5_data`. Key functions are `adc5_configure`, `adc7_configure`, `adc5_do_conversion`, `adc7_do_conversion`, `adc_read_raw_common`, `adc5_get_fw_channel_data`, `adc5_get_fw_data`, and `adc5_probe`.

## Control Flow
Probe obtains the parent regmap and base `reg`, initializes completion and mutex, matches ADC data for `qcom,spmi-adc5`, `qcom,spmi-adc7`, or `qcom,spmi-adc-rev2`, parses child channels, requests the EOC IRQ if present, otherwise enables polling for ADC5, and registers IIO. ADC5 conversion writes a block from digital parameter through conversion request and then waits for IRQ or polls status. ADC7 first writes the application SID, writes channel/timing configuration, explicitly writes conversion request, waits briefly, checks conversion-fault status, and reads voltage data. Processed reads call `qcom_adc5_hw_scale`.

## State And Persistence
The driver keeps parsed DT properties and selected static data tables. ADC register programming is per conversion. Calibration is hardware-provided through ADC5/ADC7 register modes rather than probe-time graph measurement. No stored state persists over unload.

## Dependencies And Integration Points
Uses SPMI parent regmap, platform IRQs, fwnode child nodes, DT bindings from `dt-bindings/iio/qcom,spmi-vadc.h`, IIO direct mode, and common helpers for prescale, decimation, average samples, settle time, and scaling. ADC7 fwnode translation uses virtual channel numbers combining SID and channel.

## Risks
ADC7 has no polling support; missing or broken IRQ can make reads time out or silently proceed to status checks. Channel validity is bounded by `ADC5_PARALLEL_ISENSE_VBAT_IDATA`, while table support depends on `info_mask` and static arrays. Digital-version detection controls which settle-time table is valid for ADC5, so revision read failures break channel parsing. ADC5 timeout fallback from IRQ to polling is useful but may hide IRQ wiring issues.

## Test Signals
Test all compatibles, IRQ and polling modes, ADC7 virtual SID fwnode translation, invalid channel/prescale/decimation/settle/average DT values, conversion fault status, invalid data sentinel, scaling for voltage and thermistor channels, and concurrent read serialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/qcom-spmi-adc5.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/qcom-spmi-iadc.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/qcom-spmi-iadc.c

## Purpose
Qualcomm SPMI PMIC current ADC driver exposing internal and external current-sense channels through IIO. It calibrates gain and offsets at probe, reads sense resistor values from hardware/DT, and converts ADC codes into current values.

## Important APIs, Types, And Functions
`struct iadc_chip` holds regmap/base, sense resistor values, calibration offsets, gain code, completion, mutex, and polling flag. Important functions are `iadc_configure`, `iadc_do_conversion`, `iadc_read_raw`, `iadc_update_offset`, `iadc_rsense_read`, `iadc_version_check`, and `iadc_probe`. The IIO channel table exposes `INTERNAL_RSENSE` and `EXTERNAL_RSENSE` as `IIO_CURRENT`.

## Control Flow
Probe allocates IIO state, gets the parent regmap and base, checks peripheral type/subtype/revision, reads external resistor DT value and internal nominal resistor trim, obtains EOC IRQ or enables polling, performs a warm-reset follow configuration, requests IRQ/wakeup if available, measures gain and both offset channels, then registers IIO. A raw read locks the device, configures normal mode, channel, decimation, settle, averaging, enables ADC, requests conversion, waits by IRQ or polling, reads 16-bit data, disables ADC, subtracts channel offset, converts raw code to microvolts using gain, divides by sense resistance, and returns microamps.

## State And Persistence
Gain and offset calibration codes plus internal/external sense resistances are held in memory after probe. Hardware conversion state is transient. Wakeup is enabled for IRQ mode; polling mode initializes device wakeup instead. There is no remove-time persistent state.

## Dependencies And Integration Points
Requires parent SPMI regmap, platform `reg`, optional `qcom,external-resistor-micro-ohms`, IRQ infrastructure, completion, and IIO. It reads PMIC trim register `IADC_NOMINAL_RSENSE` for internal shunt deviation.

## Risks
If external resistor is omitted, the driver defaults to ideal internal sense value for the external channel, which may be physically wrong. Zero external resistor is rejected. Gain equal to offset is a hard calibration failure. `adc_raw - offset` is unsigned through `u16` storage, so low raw readings can wrap before signed conversion. Conversion reads are serialized but calibration conversions in probe are not under the external read path because the device is not yet registered.

## Test Signals
Check revision rejection, missing/zero resistor DT, trim sign handling, IRQ and polling conversion paths, gain-offset equality failure, current math with internal and external shunts, timeout diagnostics, and scale output (`0 + 1000 micro`) expected by consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/qcom-spmi-iadc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/qcom-spmi-rradc.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/qcom-spmi-rradc.c

## Purpose
Qualcomm Round Robin ADC driver for PM660/PMI8998 PMICs. It exposes battery ID/thermistor, skin/die/charger temperatures, USB/DC voltage/current, and GPIO voltage channels as IIO channels, using mostly continuously updated PMIC ADC registers plus per-channel trigger handling where required.

## Important APIs, Types, And Functions
`struct rradc_channel` describes label, data/status registers, size, optional trigger register/mask, and post-process function. `struct rradc_chip` stores regmap/base, PMIC revision data, conversion mutex, battery ID settle/current metadata, and device pointer. Core helpers include `rradc_read` with coherent double-read retry, `rradc_read_status_in_cont_mode`, `rradc_prepare_batt_id_conversion`, `rradc_do_conversion`, `rradc_read_scale`, `rradc_read_offset`, `rradc_read_raw`, and `rradc_get_fab_coeff`.

## Control Flow
Probe gets parent regmap, base, optional battery-ID settle delay, PMIC subtype/fab information, selects an IIO name, and registers a fixed channel array. Reads dispatch by mask: scale and offset are computed from constants and PMIC fab coefficients; raw and processed reads call `rradc_do_conversion`. Conversion takes `conversion_lock`, enables special battery-ID conversion or trigger/continuous mode for channels that need it, checks readiness for continuously sampled channels, coherent-reads channel data, selects the valid battery-ID range when needed, and returns raw code or post-processed resistance.

## State And Persistence
The driver stores the PMIC revision pointer, optional battery ID delay programmed at probe, and the last battery-ID current range used for resistance calculation. Hardware continuous/log/trigger bits are toggled around some reads and restored. No suspend/resume or persistent storage is present.

## Dependencies And Integration Points
Depends on SPMI parent regmap, `qcom_pmic_get` from `soc/qcom/qcom-spmi-pmic.h`, IIO direct mode, and fixed PMIC register layout for `qcom,pm660-rradc` and `qcom,pmi8998-rradc`. It uses Linux units helpers and unaligned little-endian conversions.

## Risks
Coherency retry logs an error after retry exhaustion but still returns the last regmap return code, which may be zero. Some channels return `-ENODATA` when not physically attached. Fabric coefficients are required for charger temperature scale/offset and may reject unknown subtype/fab combinations. Battery ID handling depends on empirical settle delays and range selection among 5/15/150 current sources. The GPIO channel advertises processed plus scale, but processed path requires a `scale_fn`; without one it returns `-EINVAL`.

## Test Signals
Test PM660 and PMI8998 coefficient selection, unknown fab handling, batt-id delay DT values, coherent-read mismatch retries, no-cable `-ENODATA`, trigger cleanup on errors, scale/offset sysfs reads, battery ID resistance selection, and concurrent channel reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/qcom-spmi-rradc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/qcom-spmi-vadc.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/qcom-spmi-vadc.c

## Purpose
Qualcomm SPMI PMIC voltage ADC driver for older VADC peripherals. It parses DT channel children, validates mandatory reference channels, measures calibration graphs at probe, and exposes raw or processed IIO readings for voltage and temperature inputs.

## Important APIs, Types, And Functions
`struct vadc_channel_prop` stores channel number, calibration type, decimation, prescale, settle time, averaging, scale function, and label. `struct vadc_priv` holds regmap/base, parsed channels, reference calibration graphs, completion, mutex, and polling flag. Main functions are `vadc_configure`, `vadc_do_conversion`, `vadc_measure_ref_points`, `vadc_get_fw_channel_data`, `vadc_get_fw_data`, `vadc_read_raw`, `vadc_check_revision`, and `vadc_probe`.

## Control Flow
Probe reads parent regmap and base, checks peripheral type/subtype/revision, parses child channels, requests an EOC IRQ or enables polling, sets follow-warm-reset behavior, measures absolute and ratiometric reference points, then registers IIO. A read configures mode/channel/decimation/settle/averaging, enables the ADC, requests conversion, waits by IRQ or polling and double-checks EOC, reads a clamped 16-bit result, disables the ADC, then either returns raw code or calls `qcom_vadc_scale` with the measured graph and prescale ratio.

## State And Persistence
Probe-time calibration graphs remain in memory and are reused for processed conversions. Per-channel properties are parsed once from DT. Hardware state is reset/configured per conversion and disabled afterwards. No explicit suspend/resume or persistent state is used.

## Dependencies And Integration Points
Uses SPMI parent regmap, fwnode child channels, IIO labels and fwnode xlate, platform IRQs, and `qcom-vadc-common.c` for scaling and decimation parsing. Mandatory DT reference channels are `VADC_REF_1250MV`, `VADC_REF_625MV`, `VADC_VDD_VADC`, and `VADC_GND_REF`.

## Risks
Probe fails if any mandatory reference channel is absent or reference readings are equal. Timeout length derives from average sample setting and conversion constants; high averaging increases wait. Some channel entries intentionally expose raw-only with no scale function. DT validation is strict for prescale, decimation, settle time, and average power-of-two values. Calibration is only measured once, so large runtime reference drift is not remeasured.

## Test Signals
Validate revision checks, mandatory reference handling, IRQ and polling paths, raw-only vs processed channels, fwnode xlate, label output, invalid DT properties, equal reference failure, ADC reset errors, and processed scaling for thermistor, die temperature, charger temperature, and default voltage channels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/qcom-spmi-vadc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/qcom-vadc-common.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/qcom-vadc-common.c

## Purpose
Shared Qualcomm VADC/ADC5 scaling and DT conversion helper library. It converts raw ADC codes into microvolts or millicelsius, maps temperatures to ADC codes for thermal-monitor thresholds, and validates DT prescale, settle, averaging, and decimation values used by multiple Qualcomm ADC drivers.

## Important APIs, Types, And Functions
Internal `struct vadc_map_pt` tables encode thermistor and die-temperature curves. Exported APIs are `qcom_vadc_scale`, `qcom_adc_tm5_temp_volt_scale`, `qcom_adc_tm5_gen2_temp_res_scale`, `qcom_adc5_hw_scale`, `qcom_adc5_prescaling_from_dt`, `qcom_adc5_hw_settle_time_from_dt`, `qcom_adc5_avg_samples_from_dt`, `qcom_adc5_decimation_from_dt`, and `qcom_vadc_decimation_from_dt`. Internal scale helpers include `qcom_vadc_scale_calib`, `qcom_vadc_scale_volt`, `qcom_vadc_scale_therm`, hardware-calibrated ADC5 voltage/therm/die/SMB/charger functions, and table interpolation helpers.

## Control Flow
Legacy VADC callers pass a scale type, measured calibration graph, prescale ratio, absolute/ratiometric flag, and raw code to `qcom_vadc_scale`; it selects voltage, thermistor, PMIC die, or charger scaling. ADC5 callers pass a hardware-calibrated scale type and prescale index to `qcom_adc5_hw_scale`, which dispatches through `scale_adc5_fn`. DT helper functions scan fixed tables or validate powers of two. Thermal-monitor helpers invert thermistor maps to produce ADC threshold codes.

## State And Persistence
The file has no mutable device state. It contains static lookup tables and prescale arrays. All exported functions are pure calculations except for error logging on invalid scale type.

## Dependencies And Integration Points
Used by `qcom-spmi-vadc.c`, `qcom-pm8xxx-xoadc.c`, `qcom-spmi-adc5.c`, Gen3 ADC/TM code, and likely ADC thermal-monitor drivers. Depends on kernel fixed-point interpolation, 64-bit division helpers, units conversion, and public header constants in `linux/iio/adc/qcom-vadc-common.h`.

## Risks
Lookup tables must remain sorted in the direction expected by `qcom_vadc_map_voltage_temp` and `qcom_vadc_map_temp_voltage`; wrong ordering silently mis-scales values. `qcom_adc5_hw_scale` indexes `adc5_prescale_ratios` without checking prescale index bounds, relying on prior DT validation/static channel tables. ADC5 code clamps codes above `VADC5_MAX_CODE` to zero for low-voltage cases. Several formulas use integer arithmetic and lose precision by design.

## Test Signals
Unit-test interpolation boundaries and midpoints, inverse temperature-to-code conversions, invalid scale types, all DT parsing helpers with valid/invalid values, prescale index coverage, ADC5 full-scale variants, thermistor maps for PM5/PM7, die temperature maps, and monotonicity across lookup tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/qcom-vadc-common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/rcar-gyroadc.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/rcar-gyroadc.c

## Purpose
Renesas R-Car GyroADC IIO driver for an on-SoC ADC interface connected to external ADC devices. It supports multiple child ADC models/modes, per-channel VREF regulators, runtime PM, debug register access, and direct raw/scale/sample-frequency reads.

## Important APIs, Types, And Functions
`struct rcar_gyroadc` stores MMIO base, clock, VREF regulators, mode, model, channel count, and sample width. Hardware helpers are `rcar_gyroadc_hw_init`, `hw_start`, `hw_stop`, and `set_power`. IIO callbacks are `rcar_gyroadc_read_raw` and `rcar_gyroadc_reg_access`. DT parsing and lifecycle are handled by `rcar_gyroadc_parse_subdevs`, `rcar_gyroadc_init_supplies`, `probe`, `remove`, and runtime PM suspend/resume.

## Control Flow
Probe maps MMIO, gets the interface clock, parses child ADC nodes to choose a single mode and channel table, enables VREF regulators, enables the clock, starts runtime PM, initializes hardware timing from clock rate and mode, starts sampling, registers IIO, then autosuspends. Raw reads claim direct mode, resume runtime PM, read the realtime data register for the channel masked to sample width, then autosuspend. Scale reads use the channel regulator voltage; sample frequency returns a fixed 800 Hz.

## State And Persistence
Selected mode/sample width/channel table and regulator pointers are derived from DT and retained. Hardware sampling continues while runtime-active and is stopped in runtime/system suspend or remove. Regulator enable state is managed for the lifetime of the driver.

## Dependencies And Integration Points
Depends on platform MMIO resources, `fck` clock, child DT compatible strings for Fujitsu/TI/ADI/Maxim ADCs, `vref` supplies on child nodes, IIO direct mode, runtime PM, and optional R8A7792 interrupt register layout. Debugfs register access is exposed via IIO.

## Risks
All child ADCs must use the same mode; mixed modes fail probe. MB88101 is special and consumes all channels with one regulator. `dev->of_node` is temporarily switched while fetching child regulators, which is delicate. Raw reads require direct-mode claim and can return `-EBUSY`. Probe starts sampling before registration; cleanup paths must stop hardware and disable supplies in the right order.

## Test Signals
Test each child compatible/mode, mixed-mode rejection, invalid child `reg`, missing VREF supplies, R8A7792 debug register range, runtime PM raw reads after autosuspend, scale values from regulators, remove cleanup, and clock-rate-derived timing including odd clock-length rounding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/rcar-gyroadc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/rn5t618-adc.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/rn5t618-adc.c

## Purpose
Ricoh RN5T618 PMIC ADC IIO driver exposing eight current/voltage channels with raw, averaged raw, and scale attributes. It uses the parent MFD regmap and ADC-end interrupt to perform single conversions.

## Important APIs, Types, And Functions
`struct rn5t618_adc_data` stores device, parent `struct rn5t618`, conversion completion, and IRQ. `rn5t618_ratios[]` provides channel scale ratios. Core functions are `rn5t618_read_adc_reg`, `rn5t618_adc_irq`, `rn5t618_adc_read`, and `rn5t618_adc_probe`. `rn5t618_maps[]` maps VADP/VUSB channels to the RN5T618 power driver.

## Control Flow
Probe gets parent MFD data, resolves the ADC virtual IRQ from regmap-irq data, initializes IIO channels, stops any auto-conversion by clearing `ADCCNT3`, requests the threaded ADC IRQ, registers IIO maps, and registers the IIO device. Reads of scale return reference voltage times ratio over 4095. Raw and averaged reads select a channel, enable ADC-end IRQ, set or clear average mode, initialize completion, set `GODONE`, wait up to 500 ms for the IRQ, read the two-register 12-bit result, and return it.

## State And Persistence
Only completion and IRQ identity are kept. The driver deliberately disables automatic conversion at probe and uses single-conversion mode for every read. Hardware IRQ status registers are cleared in the IRQ handler. No suspend/resume hooks are present.

## Dependencies And Integration Points
Depends on RN5T618 MFD definitions, parent regmap, regmap IRQ domain, IIO direct mode, and IIO machine maps for the PMIC power block. Channels correspond to PMIC ADC data register layout starting at `RN5T618_ILIMDATAH`.

## Risks
There is no mutex around conversion setup, so concurrent sysfs reads could race channel selection, average mode, completion reinitialization, and result registers. Probe requires a valid ADC IRQ and does not provide polling fallback. IRQ handler clears threshold IRQ status as well as ADC-end status, which may interact with future threshold users. The channel macro uses an unusual `.indexed = 1.` initializer spelling that deserves compile coverage.

## Test Signals
Run concurrent raw/average reads, IRQ timeout tests, scale verification for all ratios, auto-conversion disabled state after probe, IIO map registration for VADP/VUSB consumers, invalid/missing IRQ path, and register read endianness/12-bit assembly checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/rn5t618-adc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/rockchip_saradc.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/rockchip_saradc.c

## Purpose
Rockchip SARADC IIO driver supporting several SoC variants with v1 and v2 register layouts, direct reads, triggered-buffer sampling, regulator-based scale, clock/reset management, and suspend/resume.

## Important APIs, Types, And Functions
`struct rockchip_saradc_data` selects channel table, clock rate, and variant operations for start/read/power-down. `struct rockchip_saradc` stores MMIO, clocks, completion, VREF regulator, mutex, reset, last conversion value/channel, and regulator notifier. Core paths are `rockchip_saradc_start_v1/v2`, `rockchip_saradc_read_v1/v2`, `rockchip_saradc_conversion`, `rockchip_saradc_read_raw`, `rockchip_saradc_isr`, `rockchip_saradc_trigger_handler`, `rockchip_saradc_probe`, and PM ops.

## Control Flow
Probe matches variant data, maps MMIO, obtains optional reset and IRQ, enables VREF and clocks, sets ADC clock rate, installs a triggered buffer, registers a regulator voltage-change notifier, initializes mutex, and registers IIO. Direct raw reads lock, start a conversion for the requested channel, wait up to 100 ms for ISR completion, return `last_val`, and power down on error via ISR or explicit path. ISR reads and masks the conversion result, powers down, and completes. Triggered buffer scans active channels sequentially under the same mutex and pushes timestamped samples.

## State And Persistence
Runtime state includes current VREF microvolts, last channel/value, clocks/regulator enabled state, and variant function table. VREF changes update `uv_vref` through notifier. Suspend disables clocks and regulator; resume reenables them. V2 conversions may reset the controller before each start if reset is present.

## Dependencies And Integration Points
Depends on platform MMIO/IRQ resources, `apb_pclk` and `saradc` clocks, `vref` regulator, optional `saradc-apb` reset, IIO triggered buffer framework, and DT compatibles for Rockchip SoCs from generic SARADC through RK3588.

## Risks
Triggered scans perform blocking sequential conversions for each active channel, so buffer latency scales with mask size. Resume does not restore ADC clock rate explicitly, relying on clock framework state. Regulator notifier assumes event data contains the new microvolt value. V2 has no explicit power-down callback, so hardware stop behavior differs from v1. Direct and buffered reads share `last_val` and `last_chan`, protected by mutex.

## Test Signals
Test each compatible channel count/resolution, v1/v2 start/read paths, timeout power-down, triggered buffer with multiple active channels, VREF notifier scale update, suspend/resume read recovery, optional reset behavior, max-channel guard, and clock/regulator failure unwinding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/rockchip_saradc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/rohm-bd79112.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/rohm-bd79112.c

## Purpose
ROHM BD79112 SPI ADC/GPIO driver for a 32-pin signal monitoring hub. It exposes selected pins as 12-bit voltage ADC channels through IIO and the remaining pins as GPIOs, using a custom regmap over SPI for ADC and IO register access.

## Important APIs, Types, And Functions
`struct bd79112_data` holds SPI/regmap/device state, GPIO chip, valid GPIO mask, VREF, optimized SPI messages, and DMA-aligned buffers. SPI/regmap callbacks are `bd79112_reg_read` and `bd79112_reg_write`. IIO path is `bd79112_read_raw`. GPIO path includes `bd79112_gpio_dir_get`, `gpio_get`, `gpio_set`, `gpio_set_multiple`, `bd79112_gpio_dir_set`, and valid-mask initialization. Probe uses `devm_iio_adc_device_alloc_chaninfo_se` to derive ADC channels from firmware.

## Control Flow
Probe initializes regmap with custom SPI read/write operations, enables `vdd` and `iovdd`, prepares optimized two-transfer reads and one-transfer writes, allocates IIO channel info from firmware, optionally registers all pins as GPIOs if no ADC channels are described, clears GPIO enable registers so described ADC pins are ADCs, registers IIO, computes the complement GPIO mask, defaults GPIO pins to input, and registers a GPIO chip. Raw reads call `regmap_read` on the channel number; scale returns VDD in mV over 12 bits. GPIO operations address banked enable/value registers derived from pin offset.

## State And Persistence
Regmap uses a Maple cache with volatile ADC and GPI value ranges. The ADC/GPIO mux is configured only at probe: ADC pins are not expected to become GPIOs later, and GPIO valid mask prevents operations on ADC pins. VREF is captured from enabled `vdd`; GPIO direction/value state lives in device registers and regmap cache.

## Dependencies And Integration Points
Depends on SPI, regmap custom bus callbacks, regulator framework, IIO ADC helper channel allocation, GPIO framework, firmware channel descriptions, and `MODULE_IMPORT_NS("IIO_DRIVER")`. The SPI protocol requires CS toggle between command and data phases for reads.

## Risks
Runtime mux changes are not supported; external register writes bypassing the driver can make valid-mask assumptions stale. ADC status flag indicates a pin configured as GPIO, but `bd79112_read_raw` returns the full register value without masking or checking it, so consumers may see status bits mixed with ADC data. GPIO bank helper returns `-EINVAL` as a register number for invalid offsets, relying on valid masks to prevent use. Early IIO registration is skipped when there are no ADC channels but GPIO registration still uses the allocated IIO object for channel count.

## Test Signals
Test SPI read/write framing, ADC channel allocation from firmware, no-ADC all-GPIO mode, mixed ADC/GPIO valid mask, GPIO direction/value/set_multiple across bank boundaries, raw ADC masking/status behavior, regulator voltage scale, regmap cache/volatile behavior, and invalid offset protection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/rohm-bd79112.c -->
