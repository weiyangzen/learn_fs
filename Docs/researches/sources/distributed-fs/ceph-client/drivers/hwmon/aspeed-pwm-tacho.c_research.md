# sources/distributed-fs/ceph-client/drivers/hwmon/aspeed-pwm-tacho.c

## Purpose
This older Aspeed AST2400/AST2500 PWM/tach platform driver exposes PWM duty controls, fan tachometer inputs, and optional thermal cooling devices from device-tree fan child nodes. It uses direct regmap-backed MMIO register programming rather than the generic PWM framework.

## Important APIs, Types, And Functions
`struct aspeed_pwm_tacho_data` stores the regmap, reset, clock frequency, present bitmaps for eight PWM ports and sixteen tach channels, per-type PWM/tach timing fields, port-to-type/source mappings, cooling devices, sysfs groups, and `tach_lock` for the shared result register. Static `type_params[]` and `pwm_port_params[]` tables describe register layout for PWM types M/N/O and ports A-H.

Hardware helpers configure clocks, PWM port enable/type/duty, tach type values, tach channel enable/source, and fan-control duty. Sysfs handlers `pwm_show()/pwm_store()` expose `pwm1`-`pwm8`; `rpm_show()` exposes `fan1_input`-`fan16_input`. Cooling callbacks map thermal states to configured PWM levels.

## Control Flow And State
Probe maps MMIO, allocates state, initializes a regmap wrapper around relaxed MMIO accessors, deasserts reset with a devm cleanup action, clears tach source registers, reads clock rate, enables clock source, creates the default type-M timing, then walks each child node. `aspeed_create_fan()` reads `reg` for PWM port, enables that PWM at `INIT_FAN_CTRL`, optionally registers a thermal cooling device from `cooling-levels`, reads `aspeed,fan-tach-ch`, and enables tach channels sourced from that PWM port. Finally it registers hwmon with two attribute groups whose visibility depends on present bitmaps.

Persistent state is in hardware registers for port duty, type timing, tach source, and channel enables. In-memory state mirrors current PWM values, mappings, cooling levels/states, and present channels. Tach reads serialize trigger/result access with `tach_lock`, trigger one channel, poll `ASPEED_PTCR_RESULT`, and compute RPM from raw count, edge mode, clock divisor, and clock frequency.

## Dependencies And Integration Points
The driver integrates with platform resources, device tree compatibles `aspeed,ast2400-pwm-tacho` and `aspeed,ast2500-pwm-tacho`, reset and clock frameworks, regmap, hwmon legacy group registration, and optional thermal cooling APIs.

## Risks
The regmap has no cache and all synchronization is manual. Tach polling timeout depends on computed measurement period; invalid timing could make reads slow or fail. PWM sysfs values are not the generic PWM API and are fixed to 0-255. Device-tree mistakes in `reg`, `cooling-levels`, or `aspeed,fan-tach-ch` abort probe. RPM calculation assumes the configured source/type mapping remains consistent with hardware.

## Test Signals
Test child parsing for valid and invalid PWM/tach channels, sysfs visibility for present ports only, PWM writes outside 0-255, duty register behavior for 0 and 255, cooling-device state transitions, tach result timeout, tach RPM math for both-edge and single-edge modes, reset cleanup, clock-rate dependency, and malformed device-tree failure paths.
