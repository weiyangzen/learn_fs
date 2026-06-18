# sources/distributed-fs/ceph-client/drivers/extcon/extcon-adc-jack.c

## Purpose
`extcon-adc-jack.c` reports external connector state by reading an IIO ADC channel and mapping configured ADC ranges to extcon cable IDs.

## Important APIs, types, and functions
`struct adc_jack_data` stores the extcon device, ADC conditions, IRQ, delay, IIO channel, work item, and wakeup flag. `adc_jack_handler()` reads ADC and sets matching cable state. `adc_jack_irq_thread()` schedules delayed work. `adc_jack_probe()` consumes platform data, allocates/registers extcon state, gets the IIO channel, requests IRQ, and runs initial detection. Suspend/resume manage delayed work and IRQ wake.

## Control flow
Probe requires platform data with `cable_names` and `adc_conditions`, counts conditions until `EXTCON_NONE`, gets the named IIO channel, registers the extcon device, requests an IRQ, enables wakeup if requested, and performs initial ADC detection. IRQs queue delayed work to let the signal settle. Work reads the ADC, marks the first matching condition true, or marks all configured conditions false if no range matches.

## State and persistence behavior
State is runtime-only in platform data references and `adc_jack_data`. Extcon state persists only in the extcon core until the next detection/removal.

## Dependencies and integration points
The driver depends on platform devices, IIO consumers, extcon provider APIs, IRQs, workqueues, and board/platform data from `linux/extcon/extcon-adc-jack.h`.

## Risks and edge cases
The code assumes `dev_get_platdata()` is non-NULL before dereferencing `pdata`. Only one matching ADC range is set true; it does not clear other cables when a new range matches, so overlapping or changing conditions can leave stale states. It uses unmanaged `request_any_context_irq()` and explicit `free_irq()`, so remove ordering matters. `cancel_work_sync(&data->handler.work)` targets delayed-work internals rather than `cancel_delayed_work_sync()`.

## Test signals
Test ADC ranges including no-match and overlapping ranges, IRQ debounce delay, initial state detection, missing platform data, IIO read errors, wakeup suspend/resume, and remove while work is pending.
