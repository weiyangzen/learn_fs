## sources/distributed-fs/ceph-client/include/linux/mfd/da9052/reg.h

Purpose: This is the DA9052 PMIC register and bitfield catalog used by the DA9052 core and child drivers.

Important APIs, types, and constants: Register definitions cover page selection, status, park, events, fault log, IRQ masks, system controls, power-down disable, interface/reset, GPIO pairs, power sequencer IDs/status/timers, buck/LDO/supply/pulldown controls, charger and backup battery, LED boost/current/dimming, ADC manual/continuous/result/threshold registers, TSI controls/results, RTC counters/alarms/seconds, and page configuration. Bit masks describe status and event bits, IRQ mask bits, fault-log causes, system control and shutdown/deepsleep/watchdog fields, interface polarity/type, GPIO pin/type/mode fields, sequencer steps, regulator enable/config/voltage fields, charger currents/timers, LED enable/ramp/current, ADC mux/conversion/auto channels, TSI mux and coordinate LSB packing, and RTC calendar/alarm fields.

Control flow: There is no code. Subdrivers use these constants in regmap updates and DA9052 wrapper calls to configure power rails, detect events, read ADC/TSI/RTC state, and handle charger/LED functions.

State and persistence: Hardware state includes event latches, fault logs, sequencer state, regulator voltages, charger state, ADC/TSI samples, and RTC counters. Some fault/RTC information persists across selected reset/power states.

Dependencies and integration points: Included by `da9052.h`; integrates with regulators, charger, LED, ADC/hwmon, touchscreen, RTC, GPIO, and IRQ logic.

Risks: Many masks use uppercase hex and plain constants rather than `BIT`/`GENMASK`, so field composition must be manual and carefully shifted. Typos such as `EALRAM` and repeated comments are historical ABI names that consumers may already rely on. Page selection matters for registers above page 0.

Test signals: Regmap field tests for status/event/IRQ banks, regulator voltage enable programming, charger current/threshold programming, ADC result packing, TSI coordinate unpacking, RTC BCD/range handling if applicable, and fault-log decoding.
