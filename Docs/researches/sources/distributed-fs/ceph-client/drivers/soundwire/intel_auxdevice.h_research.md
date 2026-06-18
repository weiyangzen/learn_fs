# sources/distributed-fs/ceph-client/drivers/soundwire/intel_auxdevice.h

## Purpose

`intel_auxdevice.h` is the small local contract between Intel SoundWire controller setup and the auxiliary link driver. It declares link startup, wake processing, child resume, and the auxiliary-device container that carries per-link resources.

## Important APIs, types, and functions

- `intel_link_startup()` starts a probed auxiliary link after parent audio power is available.
- `intel_link_process_wakeen_event()` asks an auxiliary link to process a shared wake event.
- `intel_resume_child_device()` is used during cleanup/system prepare to resume probed child SoundWire slaves.
- `struct sdw_intel_link_dev` embeds `struct auxiliary_device` and `struct sdw_intel_link_res`.
- `auxiliary_dev_to_sdw_intel_link_dev()` converts an auxiliary device to the Intel link container.

## Control flow

`intel_init.c` allocates `sdw_intel_link_dev`, fills the embedded `link_res`, and registers the auxiliary device. `intel_auxdevice.c` receives that device in probe, accesses the resource through the container macro, and later services startup/wake/resume calls exported through this header.

## State and persistence behavior

The header defines ownership shape only. `sdw_intel_link_dev` lives for the auxiliary device lifetime and is freed by the release callback in `intel_init.c`. Its embedded `link_res` persists across probe, startup, PM, wake, and cleanup.

## Dependencies and integration points

It depends on Linux auxiliary-device types and the Intel link resource type from `intel.h`. Its only users in this subset are `intel_init.c` and `intel_auxdevice.c`.

## Risks and edge cases

- The container macro assumes the auxiliary device is embedded exactly as declared.
- The header does not include explicit type forward declarations; include order must provide `struct auxiliary_device`, `struct device`, and `struct sdw_intel_link_res`.
- Lifetime correctness depends on auxiliary device delete/uninit ordering and the release callback.

## Test signals

Build coverage should catch include-order problems. Probe/unbind tests should verify `sdw_intel_link_dev` is released exactly once and no caller uses the link resource after auxiliary uninit.
