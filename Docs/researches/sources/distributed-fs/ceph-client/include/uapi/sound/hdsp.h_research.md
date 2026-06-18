# sources/distributed-fs/ceph-client/include/uapi/sound/hdsp.h

## Purpose
`hdsp.h` defines the ALSA hwdep UAPI for RME Hammerfall DSP cards. It exposes ioctl structures for peak/RMS meters, configuration status, firmware upload, hardware version, mixer matrix, and HDSP 9632 expansion board detection.

## Important APIs, Types, and Constants
`HDSP_MATRIX_MIXER_SIZE` fixes the mixer matrix array length. `enum HDSP_IO_Type` identifies Digiface, Multiface, H9652, H9632, RPM, and Undefined variants. `struct hdsp_peak_rms` returns input/playback/output peaks and RMS values. `struct hdsp_config_info` reports sync status, SPDIF settings, sample rates, clocking, gain, passthrough, and expansion-board configuration.

`struct hdsp_firmware` carries a userspace firmware pointer. `struct hdsp_version` reports IO type and firmware revision. `struct hdsp_mixer` returns a 2048-entry matrix. `struct hdsp_9632_aeb` reports analog expansion input/output boards. Ioctls are `GET_PEAK_RMS`, `GET_CONFIG_INFO`, `UPLOAD_FIRMWARE`, `GET_VERSION`, `GET_MIXER`, and `GET_9632_AEB`.

## Control Flow and State
Userspace opens the HDSP hwdep device, queries version/config/meters/mixer, optionally uploads firmware via a firmware-data pointer, and checks AEB expansion status on 9632 devices. Meter and config ioctls are snapshot queries; firmware upload mutates device state.

## State and Persistence Behavior
The card/driver maintains firmware load state, clock/sync configuration, mixer matrix, meter counters, and expansion-board detection. The header itself is a binary ABI with fixed arrays plus a pointer for firmware upload.

## Dependencies and Integration Points
It conditionally includes `<linux/types.h>` and integrates with ALSA hwdep, RME HDSP drivers, mixer applications, firmware loaders, and metering tools.

## Risks and Test Signals
Risks include pointer-size compat handling in `hdsp_firmware`, hard-coded firmware size expectations, fixed meter/mixer array sizing, and hardware-specific meaning of config bytes. Tests should check ioctl number stability, compat firmware upload, meter/config/mixer snapshot sizes, firmware upload error handling, and variant-specific version/AEB behavior.
