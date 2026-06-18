# sources/distributed-fs/ceph-client/drivers/regulator/qcom_rpm-regulator.c

## Purpose
This legacy Qualcomm RPM regulator driver supports pre-SMD RPM PMIC regulators. It encodes regulator state into RPM request words for PM8018, PM8058, PM8901, PM8921, and SMB208 resources and exposes voltage regulators, switches, and NCP resources through the regulator framework.

## Important APIs, Types, and Functions
`struct request_member` describes a bitfield inside an RPM request word. `struct rpm_reg_parts` groups bitfields for voltage, currents, pull-down, force mode, pin control, frequency, enable, and other PMIC-specific controls. `struct qcom_rpm_reg` holds the RPM handle, mutable request words, regulator descriptor, resource id, cached voltage and enable state, and force-mode capability flags. Key functions are `rpm_reg_write()`, `rpm_reg_set_mV_sel()`, `rpm_reg_set_uV_sel()`, the enable/disable variants, `rpm_reg_set_load()`, `rpm_reg_of_parse_freq()`, `rpm_reg_of_parse()`, and `rpm_reg_probe()`.

## Control Flow
Probe obtains the parent `qcom_rpm` handle, selects the compatible-specific regulator table, clones each template with `devm_kmemdup()`, fills resource id/name/supply/of_match, and registers the descriptor. The OF parse callback preloads request-word bits for pull-down, switch-mode frequency, hysteretic/PWM power mode, and force mode. Voltage setters update cached `uV` and write to RPM only if already enabled. Enable paths write voltage first for voltage regulators, then write enable/current fields; disable paths clear enable-related fields. Switch regulators only program enable state.

## State and Persistence
State is a mutex-protected pair of RPM request words plus cached `uV` and `is_enabled`. The cache is authoritative for `get_voltage()` and `is_enabled()` and is updated only after successful RPM writes. DT-derived options are packed into the same request words before registration. No persistent storage exists; RPM/PMIC hardware state outlives the driver only until reset or later RPM requests.

## Dependencies and Integration Points
The file depends on the regulator core, OF regulator parsing, `linux/mfd/qcom_rpm.h`, `dt-bindings/mfd/qcom-rpm.h`, and parent RPM MFD/platform setup. It integrates with DT compatibles such as `qcom,rpm-pm8921-regulators` and regulator child nodes named by the static tables. It registers during `subsys_initcall()` so consumers can resolve supplies early.

## Risks and Test Signals
Risk areas include bitfield packing overflow, unsupported force-mode values, mandatory frequency properties for regulators with frequency fields, cache divergence if RPM rejects a write, and template-table supply/resource mistakes. Test signals include bitfield boundary tests, probe against each compatible, DT parse errors for invalid force mode or frequency, enable/disable sequencing, voltage selection on disabled and enabled regulators, load programming, and RPM write fault injection.
