# sources/distributed-fs/ceph-client/drivers/iio/trigger/stm32-timer-trigger.c

Purpose: STM32 general-purpose timer IIO trigger and legacy IIO counter driver. It registers timer TRGO/TRGO2/channel triggers, exposes sampling-frequency and master-mode controls for TRGO triggers, and optionally creates an IIO_COUNT device for validating timer trigger inputs.

Important APIs/types/functions: `struct stm32_timer_trigger` stores regmap, clock, trigger/valid tables, state lock, registered trigger list, and suspend backup registers. `struct stm32_timer_trigger_cfg` selects valid trigger tables. Key functions include `stm32_timer_start()`, `stm32_timer_stop()`, frequency/master-mode sysfs callbacks, `stm32_register_iio_triggers()`, counter read/write/validate callbacks, enum setters/getters, `stm32_setup_counter_device()`, exported `is_stm32_timer_trigger()`, probe/remove, and PM callbacks.

Control flow: probe reads timer index, obtains STM32 MFD regmap/clock/max ARR, optionally registers an IIO counter if valid trigger inputs exist, detects TRGO2 support by write/readback, initializes lock, and registers all trigger names for the timer. Frequency writes start or stop the timer: start calculates prescaler/ARR from clock rate and requested frequency, refuses use if capture/compare channels are active, enables the clock, programs PSC/ARR/CR2 master mode, forces update, and enables CEN. Counter operations expose CNT, CEN enable, quadrature scale, preset, enable mode, and trigger mode. Suspend backs up timer registers and disables clock if this driver enabled it; resume restores registers and clock.

State and persistence: `enabled` tracks clock ownership for this child driver; hardware timer registers store current frequency, master/slave mode, count, and preset. Suspend backup is in RAM only. Registered trigger list is runtime state.

Dependencies/integration: depends on STM32 timers MFD (`struct stm32_timers`), regmap, clk framework, IIO trigger and IIO device APIs, sysfs attributes, device properties, and OF compatibles `st,stm32-timer-trigger`, `st,stm32h7-timer-trigger`, and `st,stm32mp25-timer-trigger`.

Risks: timer hardware is shared with PWM/counter/capture users; checks for `TIM_CCER_CCXE` reduce but do not eliminate coordination risks. Prescaler loop can exceed max PSC for low frequencies. Master-mode writes can enable clock without a later automatic disable unless users clear state. Ops-pointer identity is used by validation. The MP25 config intentionally omits legacy valid tables, so behavior differs by compatible.

Test signals: probe trigger lists for each timer index/compatible, set and read sampling frequency, test zero frequency stop, write master modes and available list, validate counter trigger acceptance/rejection, suspend/resume with active timer, and test coexistence with capture/compare users returning `-EBUSY`.
