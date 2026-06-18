## sources/distributed-fs/ceph-client/include/linux/mfd/da9055/reg.h

Purpose: This header is the DA9055 register/bitfield map for system control, GPIO, regulators, ADC, sequencer, RTC, OTP, trim, configuration, and monitoring features.

Important APIs, types, and constants: Register constants define page control, status/fault/event/IRQ mask banks, controls A-E, power-down disable, GPIO control/mode, buck/LDO controls, ADC manual/continuous/result/thresholds, 32 kHz enable, buck current limits and modes, A/B voltage set registers, OTP count/address/data, RTC count/alarm/seconds, interface/config/trim registers, and general-purpose IDs. `DA9055_MAX_REGISTER_CNT` bounds the map. Bitfields define page write mode, status/fault/event/mask bits, debounce/reset/watchdog/system enable/shutdown/wakeup controls, GPIO pin/type/write-enable/mode, regulator enable/GPI/pulldown/voltage set selection, ADC mux/mode/result scaling, startup/reset timing, buck/LDO voltage ranges and sleep modes, OTP locks, RTC fields and alarm/tick bits, 32 kHz trim, IRQ type, VDD fault thresholds, shutdown modes, pull-up/down, monitor enables, and monitor index selection.

Control flow: No functions are present. DA9055 subdrivers use these definitions with regmap wrappers from `core.h` to program regulators, monitor ADC/VDD, configure GPIO, service events, and manage RTC/OTP/configuration.

State and persistence: Hardware state includes event latches, regulator A/B voltage sets, RTC counters, OTP/configuration, trim values, GP IDs, and monitor configuration. OTP and some config/trim data are persistent hardware state.

Dependencies and integration points: Included by DA9055 drivers for regulator, RTC, hwmon, GPIO, and core IRQ handling.

Risks: There are historical misspellings such as `VBMEM_SEL_SHIT`, `REGUALTOR`, and `ALARAM`; consumers must use exact names or clean up carefully. Some monitor index masks define values beyond the nominal two-bit mask (`DA9055_MON_A10_IDX_LDO6` is `0x4`), which needs datasheet confirmation.

Test signals: Register field encode/decode tests for regulator voltage ranges, A/B selection, GPIO modes, ADC scaling, RTC alarm/tick, OTP lock handling, VDD fault thresholds, and monitor index programming.
