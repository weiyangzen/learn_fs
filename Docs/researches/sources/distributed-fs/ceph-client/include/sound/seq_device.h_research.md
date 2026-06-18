<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/seq_device.h -->
# sources/distributed-fs/ceph-client/include/sound/seq_device.h

## Purpose
`seq_device.h` defines ALSA sequencer device and driver registration for kernel-side sequencer clients such as MIDI synth, OPL3 synth, and UMP sequencer clients.

## Important APIs, types, and functions
`struct snd_seq_device` represents a sequencer device bound to a sound card and Linux device, with driver ID, argument storage, caller and driver private data, and optional private cleanup. `struct snd_seq_driver` wraps probe/remove callbacks, an embedded `device_driver`, ID, and argument size. APIs include `snd_seq_device_new()`, `__snd_seq_driver_register()`, `snd_seq_driver_unregister()`, `snd_seq_device_load_drivers()`, `module_snd_seq_driver()`, and `SNDRV_SEQ_DEVICE_ARGPTR()`.

## Control flow
Card code creates a sequencer device with an ID and argument payload. Sequencer drivers register against matching IDs, probe the device, allocate or register low-level resources, and store implementation state in `driver_data`. Removal frees the registered device resources and private payload.

## State and persistence behavior
State lives in the device and driver structures registered with the driver core. Argument data is embedded immediately after `snd_seq_device`. It is runtime-only and removed with the ALSA card or module.

## Dependencies and integration points
It integrates ALSA card/device lifetime with Linux driver binding and module autoloading. ID strings define common sequencer device classes.

## Risks and test signals
Risks include wrong `argsize`, stale private data, missing `private_free`, module autoload failures, and probe/remove ordering around card teardown. Test signals include module and built-in builds, device creation for each ID string, driver unbind during active clients, and argument payload validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/seq_device.h -->
