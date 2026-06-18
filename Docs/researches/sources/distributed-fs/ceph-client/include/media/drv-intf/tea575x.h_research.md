# sources/distributed-fs/ceph-client/include/media/drv-intf/tea575x.h

Purpose: Shared V4L2/ALSA helper interface for Philips TEA5757/5759 AM/FM tuner chips.

Important APIs/types/functions: Defines IF constants, pin bits, `snd_tea575x_ops` for either direct value read/write or three-pin bit control, and `snd_tea575x` device state containing V4L2 device/file/video objects, chip capabilities, mute/stereo/tuned flags, hardware value, band/frequency, mutex, ops, private data, labels, control handler, and optional external init. APIs enumerate bands, get tuner state, perform hardware seek, initialize hardware, register/unregister helper, and set frequency.

Control flow: A card driver fills ops and state, calls `snd_tea575x_init`, and the helper exposes a radio video device. Tuning writes chip serial value via either direct or bit-level ops; status reads update stereo/tuned flags where possible.

State and persistence: `snd_tea575x` owns all runtime tuner state for the device lifetime. Hardware frequency/mute state persists in chip registers until reprogrammed or powered down.

Dependencies and integration: Depends on V4L2 controls, video device, V4L2 device, and file operations; often used by ALSA sound-card drivers with radio tuners.

Risks and test signals: Risks include incomplete ops combinations, unreadable data pin, mute capability mismatches, frequency unit mistakes, and AM/FM band errors. Test init/exit, FM/AM/Japan bands, mute, seek, direct and pin-based ops, and concurrent tuner ioctls under the mutex.
