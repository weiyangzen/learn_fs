# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/at91_udc.c

## Purpose
Implements the legacy Atmel AT91 full-speed USB Device Port controller as a PIO-only Linux USB gadget UDC driver. It manages six endpoints, FIFO reads/writes, EP0 control request handling, VBUS and pullup control, clock gating, suspend/resume/reset interrupts, chip-specific endpoint capacities, and OF platform binding for AT91RM9200 and AT91SAM926x variants.

## Important APIs, Types, And Functions
The driver uses `struct at91_udc`, `struct at91_ep`, and `struct at91_request` from `at91_udc.h`. Endpoint ops are `at91_ep_enable`, `at91_ep_disable`, `at91_ep_alloc_request`, `at91_ep_free_request`, `at91_ep_queue`, `at91_ep_dequeue`, and `at91_ep_set_halt`. Gadget ops are `at91_get_frame`, `at91_wakeup`, `at91_set_selfpowered`, `at91_vbus_session`, `at91_pullup`, `at91_start`, and `at91_stop`.

Transfer primitives are `read_fifo`, `write_fifo`, `done`, `nuke`, and `handle_ep`. EP0-specific control flow is in `handle_setup` and `handle_ep0`. Power and lifecycle helpers include `udc_reinit`, `reset_gadget`, `stop_activity`, `clk_on`, `clk_off`, `pullup`, VBUS IRQ/timer helpers, and PM suspend/resume. Chip-specific init/pullup is selected through `struct at91_udc_caps`.

## Control Flow
Probe allocates the controller, parses device tree GPIOs and compatible data, initializes endpoint objects/caps, maps UDP registers, applies chip-specific endpoint maxpacket setup, prepares clocks, disables the transceiver and interrupts, requests controller and optional VBUS IRQs or starts a VBUS polling timer, registers with the gadget core, enables wakeup, and creates an optional proc debug file.

The driver stays disconnected until both a gadget driver is bound and VBUS is present. `at91_start` records the gadget driver and marks the UDC enabled; `at91_pullup` and VBUS updates call `pullup`, which turns clocks/transceiver on or off and invokes chip-specific D+ pullup control. Endpoint queueing immediately tries to service an idle endpoint via PIO: IN requests write packet bytes into the FIFO and set TXPKTRDY; OUT requests pull bytes from RX banks and release banks. Ping-pong endpoints may rescan both banks before returning. Requests that cannot complete immediately are queued and endpoint interrupts are enabled.

The IRQ handler temporarily clocks the controller if needed, loops through pending masked IRQs up to five rescans, handles bus reset by resetting gadget state and enabling EP0, handles suspend/resume by toggling interrupt masks and invoking gadget callbacks, and dispatches endpoint IRQs. `handle_setup` reads an 8-byte setup packet, handles hardware-affecting standard requests such as SET_ADDRESS, SET_CONFIGURATION deferred config bit toggling, device/endpoint GET_STATUS, remote wakeup feature, and endpoint halt, otherwise delegates to the gadget driver. `handle_ep0` sequences setup, IN ACK, OUT data, status stages, deferred-address activation, and protocol stalls.

## State And Persistence Behavior
State is runtime-only and protected by a spinlock with IRQs disabled. It tracks VBUS, enabled, clocked, suspended, request pending, deferred address/config acknowledgements, current address, endpoint FIFO bank, endpoint direction/type/stopped state, and request queues. No data persists across unbind. Hardware state is deliberately reinitialized on reset, disconnect, clock-off, and endpoint enable/disable.

## Dependencies And Integration Points
Depends on Linux USB gadget, GPIO descriptor, clock, procfs debug, platform device, OF, regmap/syscon, and AT91 matrix definitions. It integrates with board wiring for VBUS and pullup GPIOs or SoC pullup registers, with two clocks (`pclk`, `hclk`), and with compatible-specific caps for at91rm9200, at91sam9260, at91sam9261, and at91sam9263.

## Risks
The CSR register has write-one/clear side effects, so the `SET_FX`/`CLR_FX` discipline is critical. PIO byte counts for IN completions are approximate because `req.actual` advances before host ACK; gadget drivers must tolerate this. Control-OUT deferred responses are explicitly unsupported and forced to stall if the gadget driver delays too long. VBUS polling uses timer/work and must be canceled by device lifetime management. Clocks are aggressively gated, so register access while unclocked is unsafe. Chip-specific endpoint size/ping-pong assumptions can break if compatible data or endpoint caps are changed. Several code paths unlock around callbacks and then resume touching driver state.

## Test Signals
Test full-speed enumeration, SET_ADDRESS timing, SET_CONFIGURATION, GET_STATUS, remote wakeup, endpoint halt/clear-halt, PIO IN/OUT transfers on each endpoint, ping-pong OUT buffering, disconnect/reconnect through VBUS GPIO, no-VBUS always-on mode, suspend/resume with wakeup enabled and disabled, and all compatible variants. Useful diagnostics are proc debug contents, endpoint interrupt masks, FIFO bank transitions, list-debug/KASAN around request completion, and gadget callback ordering during reset/disconnect.
