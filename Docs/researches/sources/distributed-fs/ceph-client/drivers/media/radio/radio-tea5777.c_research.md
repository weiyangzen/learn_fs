# sources/distributed-fs/ceph-client/drivers/media/radio/radio-tea5777.c

Purpose: provides a reusable V4L2 helper for Philips TEA5777 AM/FM tuner chips. Bus-specific drivers supply 6-byte write and 3-byte read register callbacks while this file implements V4L2 frequency, tuner, seek, mute, and band behavior.

Important APIs and functions: exported functions are `radio_tea5777_init`, `radio_tea5777_exit`, and `radio_tea5777_set_freq`. Core helpers include `tea5777_freq_to_v4l2_freq`, `radio_tea5777_update_read_reg`, V4L2 ioctl handlers, hardware seek implementation, and `tea575x_s_ctrl` for mute. Static band descriptors cover FM and AM.

Control flow: initialization builds the default write register, tunes 90.5 MHz FM, initializes the embedded video device and mutex, creates a mute control, applies control defaults, and registers a radio node. Frequency setting selects AM for low frequencies when `has_am` is set, otherwise FM, converts V4L2 units to chip PLL values including IF offsets, writes the callback register, invalidates cached read status, and stores the rounded actual frequency. Tuner get reads status, reports mono/stereo and signal, then invalidates read status for freshness. Hardware seek optionally programs bounded limits by writing bottom/top frequencies with `PROGBLIM`, starts a search, polls read status until station found, band limit, timeout, or signal interruption, then clears search and restores original frequency on failure.

State and persistence: state lives in caller-owned `struct radio_tea5777`: current band/frequency/audmode, seek range cache, read and write register cache, quirk flags, V4L2 objects, callbacks, card/bus strings, and mutex. No persistent storage exists; register state is restored by reprogramming.

Dependencies and integration points: depends on V4L2 device/dev/fh/ioctl/control/event APIs and bus-specific implementations of `radio_tea5777_ops`. `radio-shark2.c` is a direct consumer in this subset.

Risks: the file retains `tea575x_*` names for TEA5777 operations, which can confuse maintainers. In AM setup it clears `TEA5777_W_AM_AGCRF_MASK` twice, likely intending one clear for AGCIF. Seek is blocking and uses `schedule_timeout_interruptible`, so nonblocking callers are rejected. The helper assumes caller has initialized card/bus strings and stable callbacks. `write_before_read` can trigger writes during status reads.

Test signals: unit-like callback fakes for register values, FM/AM frequency conversion round trips, mono/stereo changes, mute bit writes, bounded seek success/failure/timeout, write-before-read behavior with radioSHARK2, V4L2 compliance, and module unload freeing controls after video unregister.
