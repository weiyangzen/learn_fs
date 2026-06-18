# sources/distributed-fs/ceph-client/drivers/counter/ti-ecap-capture.c

Purpose: TI eCAP capture driver for AM62-class hardware, exposing a timestamp counter, four capture registers, overflow count, signal polarity array, clock frequency, enable control, and capture/overflow events.

Important APIs/types/functions: `struct ecap_cnt_dev` stores enabled flag, mutex, clock, regmap, atomic overflow count, and PM context. Helpers get/set event mode, enable/disable capture, and read/write count registers. Counter callbacks implement count read/write, fixed increase function/action, watch validation, clock frequency, polarity array, capture array, overflow count, ceiling, and enable.

Control flow: probe allocates a counter, enables the functional clock, verifies clock rate, maps MMIO, initializes regmap, requests IRQ, enables runtime PM, and registers. Enabling capture takes a runtime PM reference, enables event interrupts, and starts the timebase/capture loading. Disabling stops the counter, disables interrupts, and drops runtime PM. ISR reads event flags, pushes capture events for each capture slot, increments overflow count on CNTOVF, fans overflow events to all capture channels, and clears interrupt flags.

State and persistence: hardware stores time counter, capture registers, polarity/event mode, interrupt flags, and enable bits. Driver caches enabled and overflow count; PM suspend stores event mode and counter value when enabled, disables clock, and resume restores mode/counter and restarts capture if needed.

Dependencies and integration: uses platform MMIO, regmap, clocks, runtime PM, IRQs, OF compatible `ti,am62-ecap-capture`, and Generic Counter event/watch APIs.

Risks: `ecap_cnt_watch_validate()` allows overflow only for channels 0..3 even though overflow is a global event that the ISR fans to all capture channels. PM suspend calls helper functions that themselves use runtime PM, so ordering with system/runtime PM should be tested. Polarity writes are allowed while enabled and may affect capture semantics immediately.

Test signals: probe and clock-rate validation, sysfs reads/writes for count/capture/polarity/overflow/enable, enable toggling balances runtime PM, capture IRQ delivers per-channel capture events, overflow increments `num_overflows` and emits overflow events, suspend/resume restores event mode and running capture, and invalid watch channels/events are rejected.
