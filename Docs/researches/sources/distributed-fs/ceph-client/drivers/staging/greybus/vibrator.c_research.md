# sources/distributed-fs/ceph-client/drivers/staging/greybus/vibrator.c

## Purpose
Provides a Greybus vibrator class driver that exposes each remote vibrator bundle as `/sys/class/vibrator/vibratorN/timeout`. Writing a timeout turns the remote vibrator on and schedules automatic turn-off.

## Important APIs, Types, and Functions
`struct gb_vibrator_device` holds the Greybus connection, sysfs device, allocated minor, and delayed work. `turn_on()` runtime-resumes the bundle, cancels a prior delayed off, sends `GB_VIBRATOR_TYPE_ON`, and schedules `gb_vibrator_worker()`. `turn_off()` sends `GB_VIBRATOR_TYPE_OFF` and autosuspends the bundle. `timeout_store()` parses the sysfs value and calls on or off. Probe registers the connection and sysfs device; disconnect cancels work, turns off if needed, unregisters the device, frees the minor, and destroys the connection.

## Control Flow, State, and Persistence
State is in-memory only: minor allocation through `IDA`, delayed off work, and runtime PM usage. There is no persisted timeout or intensity. Probe validates a single vibrator CPort, enables the connection, creates a class device, initializes delayed work, and releases runtime PM autosuspend.

## Dependencies and Integration Points
Depends on Greybus bundle drivers rather than gbphy, device class/sysfs, IDA, delayed work, and runtime PM. It intentionally uses a custom class because no generic vibrator subsystem is used here.

## Risks and Test Signals
Risks include truncating user timeouts to `u16`, runtime PM imbalance if `turn_on()` cancels active work and `turn_off()` fails, and class lifecycle around module unload. Test signals include writing nonzero and zero timeout values, repeated timeout writes, disconnect while delayed work is pending, invalid input parsing, and ensuring the remote off operation runs before resource teardown.
