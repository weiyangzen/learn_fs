# sources/distributed-fs/ceph-client/include/linux/mfd/sun4i-gpadc.h

## Purpose

This 97-line header defines Allwinner sun4i/sun6i/sun8i GPADC/touchscreen register offsets, bitfields, IRQ IDs, autosuspend delay, and parent state.

## Important APIs, Types, and Functions

It exports control/status/data register addresses, macro builders for ADC delays, clock dividers, touch/ADC channel selection, filter, temperature period, FIFO control/status, IRQ IDs for FIFO and temperature data, `SUN4I_GPADC_AUTOSUSPEND_DELAY`, and `struct sun4i_gpadc_dev`.

## Control Flow

No executable flow. ADC, thermal, and touchscreen children use regmap/base access to configure sampling, channel selection, FIFO interrupts, and temperature conversion while sharing the MFD parent and IRQ chip.

## State and Persistence Behavior

Hardware persists ADC/touch control, FIFO status, temperature enable/period, interrupt enable/status, and sample data. Parent runtime state stores device, regmap, IRQ chip data, and MMIO base.

## Dependencies and Integration Points

It integrates the sun4i GPADC MFD core with IIO ADC, thermal, touchscreen, regmap-irq, runtime PM, and MMIO access.

## Risks and Edge Cases

Channel selection macros differ between sun4i and sun6i layouts. FIFO overrun/flush and interrupt bits must be handled carefully to avoid stale touch or temperature samples.

## Test Signals

ADC channel selection tests per SoC variant, thermal sample tests, touchscreen FIFO interrupt tests, runtime autosuspend tests, and regmap IRQ mapping checks.
