# sources/distributed-fs/ceph-client/drivers/hwmon/da9052-hwmon.c

Purpose: platform hwmon driver for the Dialog DA9052 PMIC/MFD. It exposes PMIC ADC channels for voltages, charge current, battery and junction temperatures, optional touchscreen-interface ADC channels, and labels through static sysfs attributes.

Important APIs, types, and functions: `da9052_hwmon` stores the parent `da9052`, a hwmon mutex, `tsi_as_adc` mode, TSI reference millivolts, and a completion for TSI conversion. Conversion helpers map ADC register values to millivolts or millidegrees. Channel show functions call parent MFD ADC/register helpers (`da9052_adc_manual_read()`, `da9052_adc_read_temp()`, `da9052_reg_read()`, `da9052_group_read()`). `da9052_request_tsi_read()`, `__da9052_read_tsi()`, and `da9052_tsi_datardy_irq()` manage TSI manual conversions. `da9052_channel_is_visible()` hides TSI ADC attributes unless configured.

Control flow: probe allocates state, gets the parent MFD pointer, reads the parent property `dlg,tsi-as-adc`, optionally enables and validates `tsiref`, disables touchscreen features, configures ADC mode, and requests the DA9052 TSI ready IRQ. It then registers the static `da9052` hwmon groups. Reads are direct register/ADC operations; VDDOUT temporarily enables/disables an automatic channel under `hwmon_lock`, while TSI reads request conversion and wait up to 500 ms for completion.

State and persistence: most values are live reads with no cache. Probe may persistently reconfigure the PMIC touchscreen/ADC mode when `tsi_as_adc` is true. TSI reference voltage is stored in driver state for scaling. The TSI IRQ is explicitly freed on remove or registration failure.

Dependencies and integration points: depends on the DA9052 MFD core, DA9052 register definitions, regulator API for `tsiref`, platform devices, hwmon sysfs attributes, and parent device properties. It uses the legacy static attribute-group hwmon registration style.

Risks: static channel numbers are sparse (`in70`..`in73`) for TSI channels and may surprise userspace. Some register writes in probe (`TSI_CONT_A`, ADC mode) do not check errors. VDDOUT enable/disable has careful cleanup, but failure to disable is surfaced only as read error. TSI conversion depends on the PMIC interrupt; timeout returns `-ETIMEDOUT`. `da9052_tjunc_show()` uses trim register math that must match hardware calibration.

Test signals: test with and without `dlg,tsi-as-adc`, valid and invalid `tsiref` voltages, TSI IRQ completion and timeout, VDDOUT enable/disable cleanup, ADC channel scaling, label visibility, and remove/error-path IRQ freeing. Compare PMIC voltage/temp readings to known rails and battery data.
