# sources/distributed-fs/ceph-client/sound/pci/lola/lola_clock.c

## Purpose
This file implements Lola clock-list discovery, clock selection, sample-rate conversion, granularity configuration, and unsolicited external-clock updates.

## Important APIs, Types, and Functions
`lola_sample_rate_convert()` decodes Lola clock codes into Hz using base frequency, multiplier/divisor, and 1000/1001 adjustments. `lola_set_granularity()` validates and sends `LOLA_VERB_SET_GRANULARITY_STEPS`. `lola_init_clock_widget()` validates the clock widget, reads the clock list in groups of four, filters internal/video clocks below `sample_rate_min`, and builds `idx_lookup`. `lola_enable_clock_events()` enables unsolicited clock responses. `lola_set_clock_index()`, `lola_set_clock()`, and `lola_set_sample_rate()` select valid internal/current clocks. `lola_update_ext_clock_freq()` updates external clock validity/frequency from IRQ-delivered unsolicited responses.

## Control Flow
During probe, `lola_parse_tree()` calls `lola_init_clock_widget()` if hardware advertises a clock widget, then enables events. PCM prepare calls `lola_set_sample_rate()` to lock the stream rate to a valid internal clock. IRQ-side RIRB handling calls `lola_update_ext_clock_freq()` for unsolicited clock status changes.

## State and Persistence
The file maintains `chip->clock.items`, `cur_index`, `cur_freq`, `cur_valid`, `sample_clock[]`, and `idx_lookup[]`; it also writes `chip->granularity`. These are in-memory mirrors of codec clock/granularity hardware state and are replayed by `lola_reset_setups()`.

## Dependencies and Integration Points
It depends on `lola_codec_read/write/flush()`, clock constants and widget structures from `lola.h`, ALSA PCM rate expectations through `lola_pcm.c`, and interrupt-driven unsolicited response delivery from `lola.c`.

## Risks
Clock validity rules reject non-current external clocks unless the current external source reports a valid frequency. Granularity limits are tied to max sample rate, so wrong compatibility checks can allow unstable high-rate streaming. `lola_set_clock_index()` assumes caller-provided `idx` is valid for `idx_lookup`; external callers should validate through `lola_set_clock()` or clock item bounds. A missing clock widget would leave clock fields mostly zero, making later sample-rate selection fail.

## Test Signals
Clock-list proc/debug output should decode expected internal, video, and external clocks. Opening PCM at supported rates should select a matching internal clock; unsupported rates should fail with `-EINVAL`. External clock connect/disconnect should update `cur_valid` and `cur_freq` through unsolicited events. Granularity changes should reject incompatible 96/192 kHz combinations and should survive warm reset.
