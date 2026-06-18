<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/radio/tea575x.c -->
# sources/distributed-fs/ceph-client/drivers/media/radio/tea575x.c

Purpose: reusable V4L2 radio support library for Philips TEA5757/TEA5759 AM/FM tuner chips, historically used by sound-card radio devices. It bit-bangs or delegates the 25-bit tuner protocol, exposes V4L2 tuner/frequency/seek ioctls, and registers/unregisters a `video_device` for parent drivers.

Important APIs and functions: exported APIs are `snd_tea575x_set_freq`, `snd_tea575x_enum_freq_bands`, `snd_tea575x_g_tuner`, `snd_tea575x_s_hw_freq_seek`, `snd_tea575x_hw_init`, `snd_tea575x_init`, and `snd_tea575x_exit`. Internal helpers include `snd_tea575x_write`, `snd_tea575x_read`, `snd_tea575x_val_to_freq`, `snd_tea575x_get_freq`, V4L2 ioctl handlers, `tea575x_s_ctrl`, and the file/ioctl/control templates.

Control flow: init validates readback if supported, programs default FM frequency 90.5 MHz, copies a video-device template, sets device caps and file ops, optionally creates a mute control, runs parent `ext_init`, sets controls, and registers a radio node. Frequency set chooses AM, Japanese FM, or standard FM band, clamps to band limits, computes tuner PLL bits with IF offsets, writes the 25-bit word, and updates cached frequency. Hardware seek starts the chip seek bit, polls until search clears or times out, filters wrong-direction/too-small moves, and stops on signal interruption or success.

State and persistence: parent-owned `struct snd_tea575x` holds current 25-bit value, frequency, band, stereo/tuned flags, mute state, capabilities, V4L2 device/video/control state, and chip-specific ops. Hardware state is updated by serial writes and can be read back only if the board supports data reads.

Dependencies and integration points: depends on `media/drv-intf/tea575x.h` for board ops and constants, V4L2 device/dev/fh/ioctl/event APIs, and low-level parent callbacks `set_direction`, `set_pins`, `get_pins`, or direct `read_val`/`write_val`. It integrates as a library, not a standalone bus driver.

Risks: boards with `cannot_read_data` cannot support bounded hardware seek and may expose less state fidelity. Bit-banged timing uses small `udelay` intervals and depends on parent GPIO/IO callbacks. Seek blocks for up to 10 seconds and refuses nonblocking file handles. `snd_tea575x_init` frees the control handler on some errors, so parent drivers must not double-free it.

Test signals: parent-driver builds, readback probe on hardware that supports it, FM/AM band enumeration and clamping, mute control, hardware seek timeout/signal paths, and unload/reload leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/radio/tea575x.c -->
