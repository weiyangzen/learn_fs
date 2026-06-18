<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/ti_am335x_tsc.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/ti_am335x_tsc.c

## Purpose
`ti_am335x_tsc.c` is the touchscreen child driver for TI AM335x TSC/ADC MFD hardware. It configures sequencer steps for 4/5/8-wire resistive panels, reads averaged coordinates and pressure from FIFO0, shares an IRQ with the ADC function, and supports wakeup from pen-down.

## Important APIs, Types, And Functions
`struct titsc` stores the MFD pointer, input device, IRQ, DT wiring/plate/charge settings, decoded pin/input mapping, step mask, pen state, and wake device. `titsc_parse_dt()` reads `ti,wires`, `ti,x-plate-resistance`, `ti,coordinate-readouts` (plus legacy misspelling), `ti,charge-delay`, and `ti,wire-config`. `titsc_config_wires()` decodes analog line/wire order. `titsc_step_config()` programs sequencer steps for Y samples, Z samples, X samples, charge config, FIFO threshold, and cached step enable bits. `titsc_irq()` handles pen down/up, end-of-sequence, and FIFO0 threshold data.

## Control Flow
Probe obtains the parent `ti_tscadc_dev`, allocates state/input manually, parses DT, requests the shared IRQ, enables wakeup, sets wake IRQ, clears/enables IRQ bits, configures wires/steps/FIFO threshold, creates an ABS_X/ABS_Y/ABS_PRESSURE plus `BTN_TOUCH` input device, and registers it. IRQ processing marks pen-down on hardware pen IRQ, confirms pen-up only when ADC FSM is at `ADCFSM_STEPID`, reads coordinates when FIFO0 threshold fires, computes pressure from X, Z1/Z2, and X-plate resistance, reports only pressure values within 12-bit range, acknowledges IRQs, and refreshes the sequencer cache after EOS.

## State And Persistence
State is runtime-only but hardware sequencer configuration persists while the MFD block remains powered. Remove clears step-enable bits for this driver's steps, unregisters input, frees IRQ, and clears wake IRQ. Suspend enables hardware pen wake if allowed; resume disables wake bits and reprograms steps/FIFO threshold.

## Dependencies And Integration Points
It depends on the TI TSCADC MFD header/functions, OF bindings, shared IRQ handling, PM wake IRQ helpers, input core, MMIO register access, and sorting helpers for coordinate filtering.

## Risks
Manual allocation/free paths have more cleanup surface than devm drivers. Pressure formula uses unsigned arithmetic with `z = z1 - z2`; unexpected Z ordering can underflow and be filtered only if above `MAX_12BIT`. DT wire configuration is strict and can fail probe. ADC and touchscreen share IRQ and sequencer resources, so step masks must remain coordinated with the MFD/ADC users.

## Test Signals
Test 4/5/8-wire DT configurations, coordinate-readout bounds and legacy property warning, pressure across light/heavy touches, shared ADC IRQ behavior, suspend wake from pen, remove step-mask cleanup, and resume reprogramming after power loss.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/ti_am335x_tsc.c -->
