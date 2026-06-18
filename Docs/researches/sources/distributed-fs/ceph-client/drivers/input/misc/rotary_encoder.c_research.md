# sources/distributed-fs/ceph-client/drivers/input/misc/rotary_encoder.c

## Purpose
`rotary_encoder.c` is a generic GPIO rotary encoder input driver. It decodes gray or binary encoded GPIO phases and reports movement as either a relative axis or bounded absolute position.

## Important APIs, Types, and Functions
`enum rotary_encoder_encoding` selects gray or binary. `struct rotary_encoder` stores input, mutex, step count, axis, relative/rollover flags, encoding, current position, GPIO array, IRQ list, and decoder state. `rotary_encoder_get_state()` samples GPIOs and converts gray encoding. `rotary_encoder_report_event()` reports relative or absolute movement. Three IRQ handlers implement full-period, half-period, and quarter-period decoding. Probe parses device properties and registers IRQs for all GPIOs.

## Control Flow
Probe reads `rotary-encoder,steps`, `rotary-encoder,steps-per-period` or legacy `half-period`, rollover, encoding, `linux,axis`, and relative-axis properties. It obtains a GPIO array, creates an input device, chooses the IRQ handler based on steps-per-period adjusted for the number of GPIOs, registers both-edge threaded IRQs for every GPIO, registers input, and sets wakeup from `wakeup-source`. Runtime IRQs take `access_mutex`, sample state, update decoder state, and report movement when a valid state transition is complete.

## State and Persistence Behavior
The driver persists position for absolute mode, last stable phase, armed flag, direction, and IRQ numbers. Input core stores current absolute/relative state. Wakeup state persists in device and IRQ core; suspend/resume enable or disable IRQ wake on every GPIO IRQ when configured.

## Dependencies and Integration Points
It depends on GPIO descriptor arrays, IRQ conversion, platform/OF/property APIs, input core, and PM wakeup helpers. Device-tree binding properties define axis, encoding, step granularity, rollover, and wake behavior.

## Risks and Edge Cases
If `rotary-encoder,steps` is missing for absolute mode, max may be zero and movement semantics become poor. Multi-GPIO encoders shift `steps_per_period` by `ndescs - 2`; invalid combinations fail probe. GPIO reads are `cansleep` inside a threaded IRQ, which is expected but latency-sensitive. Contact bounce can create extra transitions unless hardware debounce is present. Position clamping in non-rollover mode silently drops movement beyond endpoints.

## Test Signals
Test gray and binary encoders, relative and absolute axes, rollover versus clamped movement, 1/2/4 steps per period, multiple GPIO counts, bounce/noise behavior, wakeup suspend/resume, GPIO-to-IRQ failures, and property validation failures.
