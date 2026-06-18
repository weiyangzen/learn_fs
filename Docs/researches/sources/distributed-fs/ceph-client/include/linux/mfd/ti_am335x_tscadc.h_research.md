# sources/distributed-fs/ceph-client/include/linux/mfd/ti_am335x_tscadc.h

## Purpose

This 196-line header defines the TI AM335x touchscreen/ADC MFD register map, bitfield macros, timing constants, parent state, inline helpers, and sequencer management APIs.

## Important APIs, Types, and Functions

It exports IRQ, DMA, control, step, FIFO, and sequencer register offsets; bitfields for IRQ wake/enable, step config, delay, charge config, control, FIFO read, DMA, status, timing constants, cell count, `struct ti_tscadc_data`, `struct ti_tscadc_dev`, inline `ti_tscadc_dev_get()` and `ti_adc_with_touchscreen()`, and sequencer cache/update/done prototypes.

## Control Flow

Child drivers obtain the parent pointer from platform data, check whether touchscreen is present, coordinate access to the step-enable sequencer cache, and use wait queues/spinlock fields to arbitrate ADC versus touchscreen access.

## State and Persistence Behavior

`struct ti_tscadc_dev` stores regmap/MMIO/physical base, feature data, IRQ, MFD cells, control cache, sequencer enable cache, ADC wait/in-use flags, wait queue, spinlock, clock divider, and child pointers. Hardware persists sequencer, FIFO, IRQ, DMA, and control state.

## Dependencies and Integration Points

It integrates AM335x TSCADC MFD parent with IIO ADC, touchscreen input, MAGADC variants, DMA, IRQ, platform devices, and clock-rate configuration.

## Risks and Edge Cases

ADC and touchscreen share the sequencer, so cache synchronization and wait completion are critical. Timing macros encode hardware field widths; overflow can stall conversions. `IDLE_TIMEOUT_MS` is derived from worst-case conversion timing.

## Test Signals

Sequencer arbitration tests, ADC/touchscreen concurrent-use tests, FIFO/IRQ tests, timeout tests, compatible-specific clock-rate tests, and build coverage for MAGADC and TSCADC variants.
