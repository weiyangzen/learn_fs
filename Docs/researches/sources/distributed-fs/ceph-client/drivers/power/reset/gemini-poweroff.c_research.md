# sources/distributed-fs/ceph-client/drivers/power/reset/gemini-poweroff.c

## Purpose
Cortina Gemini power controller poweroff and power-button driver.

## Important APIs, Types, and Functions
`struct gemini_powercon`, power-button IRQ handler, `gemini_poweroff()`, probe, and sys-off registration.

## Control Flow
probe maps power controller, requests power-button IRQ if present, registers poweroff; IRQ acknowledges/clears status and calls `orderly_poweroff()`, while poweroff writes the shutdown command and delays.

## State and Persistence Behavior
MMIO base and IRQ state persist in driver; hardware power-controller status/command bits persist until poweroff.

## Dependencies and Integration Points
OF, MMIO, IRQ, input-less power button handling, sys-off poweroff.

## Risks and Edge Cases
power button path relies on controller status semantics; built-in driver has no module unload; poweroff failure can only log after timeout.

## Test Signals
Gemini DT probing, IRQ press handling, status clear, orderly poweroff invocation, and final power cut.
