# sources/distributed-fs/ceph-client/include/linux/mfd/mxs-lradc.h

## Purpose

This header defines the shared Freescale/NXP MXS low-resolution ADC register contract and parent state used by IIO, touchscreen, and touch-button child drivers. It covers i.MX23 and i.MX28 differences.

## Important APIs, Types, and Functions

The macro API includes channel limits, delay timer rate, control/status/channel/delay register offsets, touch plate switch bits for MX23 and MX28, IRQ enable/status masks, ADC channel sample/value fields, delay trigger/loop/kick helpers, LRADC channel selection helpers, resolution and sample masks, buffer virtual-channel masks, and reserved channel masks for touchbutton and 4/5-wire touchscreen use. `enum mxs_lradc_id` identifies IMX23 vs IMX28. `enum mxs_lradc_ts_wires` identifies touchscreen wiring. `struct mxs_lradc` stores SoC type, delay clock, available buffered channels, touchscreen mode, and touchbutton usage. `mxs_lradc_irq_mask()` returns the SoC-specific IRQ bit mask.

## Control Flow

There is only one inline control path: `mxs_lradc_irq_mask()` switches on `lradc->soc` and returns the correct IRQ mask. Runtime child drivers use the macros to program touch detection, map virtual channels, configure sample accumulation, set delay triggers, clear IRQs, and read raw channel values.

## State and Persistence Behavior

`struct mxs_lradc` is runtime parent state shared by MFD children. The hardware state consists of ADC control registers, virtual channel mappings, delay timers, pending IRQs, and touch plate switch configuration. No file-backed persistence is involved. Channel availability is stateful at runtime because touchscreen or touchbutton use reserves channels from generic buffered sampling.

## Dependencies and Integration Points

The header includes bit operations, MMIO helpers, and STMP register helper declarations. It is consumed by LRADC MFD core code, IIO ADC support, and `drivers/input/touchscreen/mxs-lradc-ts.c`, whose touch state machine uses the plate masks, delay registers, channel mappings, and `mxs_lradc_irq_mask()`.

## Risks and Edge Cases

MX23 and MX28 bit layouts differ; using the wrong plate or IRQ mask can short or misdrive touchscreen lines. Shared channel masks are important because generic ADC sampling must not use channels currently reserved for touch hardware. Delay fields are limited-width, so unmasked values would corrupt adjacent trigger bits. The default branch in `mxs_lradc_irq_mask()` returns zero, which makes an unknown SoC fail quietly by ignoring IRQs.

## Test Signals

Build MXS LRADC MFD/IIO/touchscreen drivers for IMX23 and IMX28; probe with device tree touchscreen and touchbutton modes; verify generic ADC channels reject reserved touch channels; exercise touch IRQs and coordinate/pressure reads; test delay-triggered sampling; and inspect register writes on both SoC variants if hardware tracing is available.
