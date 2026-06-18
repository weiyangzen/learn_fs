# sources/distributed-fs/ceph-client/sound/soc/intel/atom/sst-mfld-platform.h

## Purpose
This header defines the public interface between the Atom SST ASoC platform driver, compressed-audio adapter, control implementation, and low-level SST DSP driver. It declares global registration objects, PCM limits, stream status enums, stream parameter structures, low-level operation tables, runtime stream state, device registration functions, and the platform private `struct sst_data`.

## Important APIs, types, and functions
The global integration points are `extern struct sst_device *sst`, `sst_register_dsp()`, and `sst_unregister_dsp()`. PCM/compress hardware limits include `SST_MAX_BUFFER`, `SST_MIN_PERIOD_BYTES`, and period count constraints. `struct pcm_stream_info` carries firmware stream ID, period callback, buffer pointer, delay, and sample rate. `struct sst_ops` and `struct compress_sst_ops` are the low-level driver callback contracts used by platform PCM and compressed operations.

Runtime and device state is represented by `struct sst_runtime_stream`, `struct sst_device`, and `struct sst_data`. Public helpers from other files include `sst_dsp_init_v2_dpcm()`, `sst_send_pipe_gains()`, `send_ssp_cmd()`, `sst_handle_vb_timer()`, `sst_set_stream_status()`, and `sst_fill_stream_params()`.

## Control flow
The header has no executable flow. At runtime, the low-level SST driver registers an `sst_device`; the ASoC platform stores its ops in per-stream runtime state and invokes them for PCM/compress operations. Control code uses `struct sst_data` for locking, byte-stream storage, and SSP command caching.

## State and persistence behavior
All defined state is in-memory runtime state. Stream status is protected by `status_lock` in `sst_runtime_stream`; control and SSP state is protected by `sst_data.lock`. No persistent filesystem state is defined.

## Dependencies and integration points
It includes `sst-mfld-dsp.h` and `sst-atom-controls.h`, making the firmware IPC ABI and DAPM/control ABI visible to platform files. It integrates with ALSA compressed APIs through `struct snd_compress_ops` and with low-level platform data from `struct sst_platform_data`.

## Risks and edge cases
The global `sst` pointer serializes all platform users onto one registered DSP. Operation table callbacks must be present for any path that invokes them; most callers do not defensively check all PCM callbacks. Buffer constants force a fixed 800 KiB min/max PCM buffer, which can expose firmware assumptions to user-space behavior.

## Test signals
Build tests catch callback signature drift. Runtime checks include successful DSP registration/unregistration, module reference balance, stream status transitions under concurrent callbacks, platform stream parameter filling, and both PCM and compressed paths using the same low-level DSP registration.
