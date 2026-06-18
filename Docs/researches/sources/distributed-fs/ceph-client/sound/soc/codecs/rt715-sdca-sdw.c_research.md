# sources/distributed-fs/ceph-client/sound/soc/codecs/rt715-sdca-sdw.c

Purpose: Provides the SoundWire bus driver for RT715/RT714 SDCA microphone-array codecs. It defines regmaps and defaults, SoundWire source-port properties, attach-time initialization, and PM cache handling for the RT715 SDCA core implemented in neighboring files outside this subset.

Important APIs and functions: `rt715_sdca_sdw_probe()` initializes MBQ and SDCA regmaps and calls `rt715_sdca_init()`. `rt715_sdca_read_prop()` advertises source ports 4 and 6, no sink ports, paging support, and clock-stop timeout. `rt715_sdca_update_status()` calls `rt715_sdca_io_init()` on first attached status. `rt715_dev_suspend()` and `rt715_dev_resume()` control regcache cache-only/dirty state and synchronize selected SDCA/MBQ ranges after resume.

Control flow: Probe binds SDW IDs for parts `0x715` and `0x714`. On attach, the core initialization is run unless `hw_init` is already true. Suspend marks both regmaps cache-only and dirty. Resume exits early before first hardware init, otherwise waits for SoundWire enumeration when `unattach_request` is set, clears that flag, and syncs the SDCA control range plus MBQ vendor/control ranges.

State and persistence: The bus file depends on `struct rt715_sdca_priv` fields `regmap`, `mbq_regmap`, `hw_init`, and `first_hw_init` from `rt715-sdca.h`. Register defaults and regcache synchronization preserve mic-array mute/volume/VAD control state over runtime and system PM.

Dependencies and integration: Uses SoundWire slave ops, regmap SoundWire/MBQ helpers, runtime PM, ASoC, and `rt715-sdca.h`/`rt715-sdca-sdw.h`. Driver name is `rt715-sdca`; license metadata says GPL v2.

Risks and test signals: There is no interrupt callback in this wrapper, so behavior depends on polling/control paths in the core. Risks include incomplete cache sync ranges, source port property mismatches, and resume timeout after unattach. Tests should verify port discovery, capture path registration, RT714/RT715 matching, autosuspend/resume, unattach/reattach initialization, and regcache replay of VAD/mic controls.
