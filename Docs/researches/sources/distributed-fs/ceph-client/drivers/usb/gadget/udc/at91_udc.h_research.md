# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/at91_udc.h

## Purpose
Defines the AT91 USB Device Port register offsets, bit fields, endpoint count, minimal interrupt mask, core driver structures, request type, conversion helper, and debug macros used by `at91_udc.c`. It is the hardware and state contract for the full-speed PIO-only AT91 UDC driver.

## Important APIs, Types, And Functions
The header enumerates UDP registers such as `AT91_UDP_FRM_NUM`, `GLB_STAT`, `FADDR`, interrupt enable/disable/mask/status/clear, endpoint reset, endpoint CSR/FDR, and transceiver control. It defines CSR bits for TX completion, RX bank readiness, setup, stall, TX packet ready, endpoint type, direction, data toggle, endpoint enable, and RX byte count. `NUM_ENDPOINTS` fixes the driver at six endpoints. `MINIMUS_INTERRUPTUS` preserves reset/resume/suspend interrupts when most endpoint interrupts are disabled.

Driver structures are `struct at91_ep`, `struct at91_udc_caps`, `struct at91_udc_data`, `struct at91_udc`, and `struct at91_request`. `to_udc` maps a `usb_gadget` to the container. Debug macros `ERR`, `WARNING`, `INFO`, `DBG`, `VDBG`, and `PACKET` standardize driver logging.

## Control Flow
No executable control flow is implemented here beyond `to_udc`. The fields defined here directly drive `at91_udc.c`: endpoint queues and `int_mask` are used by queueing/IRQ dispatch; `is_pingpong`, `fifo_bank`, `is_in`, and `is_iso` guide FIFO service; UDC flags gate pullup, clocks, VBUS, suspend, and deferred EP0 status; chip-specific `caps` provide init and pullup callbacks; GPIO descriptors store board VBUS/pullup wiring.

## State And Persistence Behavior
All state described by the header is volatile in-memory kernel state. It models current USB controller state, endpoint queues, clocks, VBUS, and platform wiring, but nothing is persisted. Register definitions correspond to hardware state that is reprogrammed by probe, pullup, reset, endpoint enable/disable, and IRQ handling.

## Dependencies And Integration Points
Depends on Linux GPIO descriptors and USB gadget types included by the C file context. The register layout is based on the AT91RM9200 datasheet and shared by several AT91SAM variants with chip-specific differences supplied by `at91_udc_caps`. The matrix `regmap` pointer supports AT91SAM9261 pullup control.

## Risks
Bit definitions with side effects must remain accurate because endpoint CSR writes cannot simply echo read values. Changing `NUM_ENDPOINTS` without revisiting endpoint info, IRQ dispatch, and chip-specific maxpacket tables would corrupt assumptions. The `struct at91_udc` comment says the driver is non-SMP and protects chip registers by blocking IRQs; broader concurrency assumptions should be revisited before adding threaded or unlocked paths. The header's `ep_is_*` state fields are small bitfields, so updates must stay under lock.

## Test Signals
Header changes should be validated through build coverage and runtime enumeration on each compatible SoC. Exercise endpoint enable, FIFO reads/writes, bus reset, suspend/resume, VBUS changes, and chip-specific pullup logic. Compile errors in `at91_udc.c`, incorrect proc debug output, or broken endpoint IRQ masks indicate contract drift.
