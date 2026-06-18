# sources/distributed-fs/ceph-client/drivers/gpio/gpio-sloppy-logic-analyzer.c

## Purpose
This debug-oriented platform driver samples an array of GPIO inputs as a simple software logic analyzer. It exposes debugfs controls for sampling delay, buffer size, trigger pattern, capture start, metadata, and captured sample data.

## Important APIs, Types, and Functions
`struct gpio_la_poll_priv` stores the GPIO descriptor array, sample buffer blob, metadata blob, trigger data, measured acquisition delay, requested delay, and debugfs dentries. `gpio_la_get_array()` reads all probe GPIOs and treats fatal signals as interruption. `fops_capture_set()` performs the capture. Other debugfs handlers manage buffer size and trigger data.

## Control Flow
Late init creates the top-level debugfs directory and registers the platform driver. Probe allocates state, initializes the default 256 KiB buffer, obtains `probe` GPIO array as inputs, rejects sleep-capable lines and more than eight probes, reads `probe-names`, sets consumer names, builds metadata, and creates debugfs files. Writing nonzero to `capture` removes prior data, disables local IRQs and preemption, measures GPIO-read overhead, waits for trigger mask/value pairs, samples one byte per state into the buffer, then recreates the `sample_data` blob.

## State and Persistence
The sample buffer is vmalloc-backed and resized through debugfs. Trigger data is allocated from userspace writes and freed after capture. Captured data persists as a debugfs blob until the next capture/removal. There is no PM state.

## Dependencies and Integration Points
The driver depends on GPIO consumer arrays, debugfs, platform DT compatible `gpio-sloppy-logic-analyzer`, property `probe-names`, and non-sleeping GPIO providers. It uses `late_initcall()` to claim GPIOs early enough for non-strict pinctrl cases.

## Risks
Capture disables local IRQs and preemption for the full buffer duration, so large buffers or small delays can harm system latency. Sampling is explicitly non-deterministic and unsuitable for precise timing. Trigger writes accept raw byte pairs and replace prior trigger data without a lock. Buffer data stores only up to eight probes because each sample is one byte.

## Test Signals
Test non-sleeping GPIO enforcement, max-probe rejection, `probe-names` count validation, buffer resize and allocation failure, delay below acquisition returning `-ERANGE`, trigger matching, fatal signal interruption, sample blob recreation, and debugfs removal while serialized by `blob_lock`.
