# sources/distributed-fs/ceph-client/include/linux/mfd/ti-lmu-register.h

## Purpose

This 212-line header defines register maps and bit masks for TI LMU lighting/display-bias devices LM3631, LM3632, LM3633, LM3695, and LM36274.

## Important APIs, Types, and Functions

It exports per-chip register addresses for device control, brightness LSB/MSB, backlight configuration, modes, slopes, LDO/bias enables, boost/positive/negative output voltages, enable timing, LED mappings, ramps, current limits, patterns, OVP, PWM, fault status, monitor enable, and max-register values.

## Control Flow

No local flow exists. Backlight, LED, regulator, and monitor drivers select the register set by chip ID and program brightness, channel mode, bias supplies, OVP, PWM, ramp, and fault-monitor fields through regmap.

## State and Persistence Behavior

Hardware registers persist backlight brightness, LED bank/channel mapping, bias regulator output voltages, enable state, ramp timing, PWM mode, pattern generator values, and fault/monitor status.

## Dependencies and Integration Points

It includes bitops and integrates TI LMU MFD core with backlight, LED, regulator, and hwmon/fault-monitor consumers.

## Risks and Edge Cases

Different LMU chips reuse similar concepts at different addresses. Brightness width and channel mapping differ, so generic code must branch by chip. Voltage and current masks are hardware-limited.

## Test Signals

Per-chip regmap table tests, brightness encode tests, regulator voltage selector tests, LED channel mapping tests, OVP/fault status tests, and build coverage for each LMU ID.
