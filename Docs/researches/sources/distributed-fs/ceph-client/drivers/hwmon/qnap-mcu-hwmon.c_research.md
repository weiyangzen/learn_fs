# sources/distributed-fs/ceph-client/drivers/hwmon/qnap-mcu-hwmon.c

Purpose: hwmon and thermal cooling driver for fan and temperature functions exposed by QNAP MCU MFD devices.

Important APIs/types/functions: `struct qnap_mcu_hwmon` stores MCU pointer, PWM bounds from variant data, fan cooling levels, fwnode, and hwmon info. `qnap_mcu_hwmon_get_rpm()`, `get_pwm()`, `set_pwm()`, and `get_temp()` issue small MCU command/reply transactions. Thermal callbacks map cooling state to PWM.

Control flow: probe obtains parent MCU and variant limits, sets fan PWM to max, parses optional `fan-0/cooling-levels`, registers hwmon, then registers a thermal cooling device only when valid cooling levels exist. Runtime reads poll MCU; writes clamp nonzero PWM into variant min/max.

State and persistence: fan state is tracked only when thermal cooling changes it; actual PWM is read live. Fan fwnode is retained until unbind via devm action.

Dependencies/integration: QNAP MCU MFD API, hwmon, thermal OF cooling, firmware node properties, platform data.

Risks: MCU reply validation checks only command echo bytes; protocol comments leave fan id semantics uncertain. Direct hwmon PWM writes do not update `fan_state`. Probe forces max PWM, which may surprise systems expecting firmware policy.

Test signals: MCU command/ack traces, RPM scaling by 30, PWM min/max clamping, temperature bit7 masking, optional cooling-device registration, and malformed cooling-level rejection.
