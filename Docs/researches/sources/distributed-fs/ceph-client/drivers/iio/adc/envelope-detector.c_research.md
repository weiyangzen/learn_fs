# sources/distributed-fs/ceph-client/drivers/iio/adc/envelope-detector.c

## Purpose
This is a synthetic IIO ADC-like driver for an envelope detector built from an external DAC and comparator interrupt. It estimates the peak level of an alternating input signal by binary-searching DAC output levels and observing whether the comparator trips during a configurable interval. It exposes a single `IIO_ALTVOLTAGE` raw channel and forwards scale from the DAC.

## Important APIs, Types, And Functions
`struct envelope` holds comparator latch state protected by a spinlock, a read mutex, comparator IRQ and trigger polarities, the consumed DAC IIO channel, delayed work for compare timeout, `compare_interval`, `invert`, DAC maximum, binary-search bounds, and completion. `envelope_detector_comp_isr()` latches comparator events and disables the IRQ. `envelope_detector_comp_latch()` reads/clears the latch and carefully reenables/synchronizes IRQ state. `envelope_detector_setup_compare()` and `envelope_detector_timeout()` implement the binary search. `envelope_detector_read_raw()` exposes raw/scale reads. Extended attributes `invert` and `compare_interval` are implemented through sysfs ext_info.

## Control Flow
Probe allocates an IIO device, initializes locks/completion/delayed work, obtains the `dac` IIO channel, requests named IRQ `comp`, derives inverse IRQ trigger polarity, validates that the DAC channel type is voltage, reads the DAC raw maximum, and registers the IIO device. A raw read locks `read_lock`, initializes binary-search bounds based on invert mode, starts comparison setup, waits for completion, returns either a negative error latched into `level` or the found raw value adjusted for inversion. Each search step writes a safe DAC extreme, clears comparator latch, writes the candidate DAC level, schedules delayed work, and after the interval adjusts low/high based on latch state until adjacent bounds complete the search.

## State And Persistence
There is no persistent state. Runtime tunables are `invert` and `comp_interval`; both are mutable through IIO extended attributes and protected by `read_lock`. The comparator latch is one-bit state in `env->comp`; the ISR disables IRQs until the latch is consumed to avoid interrupt floods. The completion is reused across reads; the binary search completes when bounds differ by one or a DAC write fails.

## Dependencies And Integration Points
The driver depends on a DAC exposed as an IIO consumer channel named `dac`, a platform IRQ named `comp`, IRQ trigger configuration support for inversion, delayed work, completions, and IIO core. OF compatible is `axentia,tse850-envelope-detector`. The output scale is delegated to `iio_read_channel_scale()` on the DAC.

## Risks And Test Signals
Risks include waiting indefinitely because `wait_for_completion()` has no timeout, stale completion state if consecutive reads start after an error, IRQ polarity inversion not available on some interrupt controllers, DAC write failures being encoded through `env->level`, and comparator signals changing faster than `compare_interval`. Test signals include successful rejection of non-voltage DAC channels, presence of DAC max raw value, raw reads converging within `log2(dac_max)` delayed-work steps, invert toggling changing IRQ type and output mapping, compare interval rejecting values above 1000 ms, and no IRQ flood while reads are idle.
