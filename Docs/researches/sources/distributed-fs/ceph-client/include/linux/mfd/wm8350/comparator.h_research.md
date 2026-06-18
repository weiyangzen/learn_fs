<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/wm8350/comparator.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/wm8350/comparator.h

## Purpose
`comparator.h` describes the WM8350 AUXADC and generic digital comparator block. It defines digitiser controls, AUX channel readback fields, USB/line/battery/chip-temperature readback fields, comparator threshold/source fields, comparator IRQ numbers, and the public AUXADC read helper.

## Important APIs, types, and functions
The public function is `wm8350_read_auxadc(struct wm8350 *wm8350, int channel, int scale, int vref)`. Register macros cover digitiser controls `WM8350_AUXADC_CTC`, `WM8350_AUXADC_POLL`, channel select bits, conversion rate/mask/calibration/wait bits, 12-bit readback masks, comparator enable bits `WM8350_DCMP1_ENA` through `WM8350_DCMP4_ENA`, comparator source/greater-than/threshold masks, channel IDs `WM8350_AUXADC_*`, and coefficient `WM8350_AUX_COEFF`.

## Control flow
The AUXADC implementation serializes conversions, selects a channel and scale/reference, starts or polls conversion, waits for data-ready IRQ or status, then reads the appropriate readback register and masks 12-bit data. Comparator users program source, threshold, and comparison direction, then consume comparator IRQs.

## State and persistence behavior
Conversion setup and comparator thresholds are hardware register state. `core.h` provides `auxadc_mutex` and `auxadc_done` for runtime coordination; conversion results are transient readback values.

## Dependencies and integration points
This header depends on `struct wm8350`, WM8350 core register access, IRQ definitions in `core.h`, and hardware monitor/power-supply users that read voltage or temperature channels.

## Risks and test signals
Risks include concurrent AUXADC conversions without the mutex, wrong scale/reference conversion math, stale data-ready completion, and threshold source mismatch. Test signals include channel-by-channel readback, timeout paths, IRQ completion, comparator threshold interrupts, and voltage conversion checks using `WM8350_AUX_COEFF`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/wm8350/comparator.h -->
