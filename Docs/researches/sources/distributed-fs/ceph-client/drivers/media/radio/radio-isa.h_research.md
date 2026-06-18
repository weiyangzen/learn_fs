# Research: sources/distributed-fs/ceph-client/drivers/media/radio/radio-isa.h

Purpose: shared interface for ISA radio board drivers. It defines the generic card structure, board callback table, top-level driver descriptor, and exported framework entry points.

Important types: `struct radio_isa_card` contains driver pointer, V4L2 device/control/video objects, lock, ops pointer, mute/volume controls, I/O port, stereo flag, and current frequency. `struct radio_isa_ops` contains board callbacks for allocation, probe, init, mute/volume, frequency, stereo, rxsubchans, and signal. `struct radio_isa_driver` wraps an `isa_driver`, optional `pnp_driver`, module parameter arrays, probe/port metadata, region size, card name, stereo flag, and max volume.

Control flow/state is implemented in `radio-isa.c`; board drivers instantiate a static `radio_isa_driver` and call `isa_register_driver`. Dependencies include ISA, optional PnP, V4L2 device/control headers.

Risks: callback contracts are not type-enforced beyond signatures; required callbacks such as `s_mute_volume` and `s_frequency` must be present for the framework paths. Test signals are compile coverage for all board users and runtime board probe/remove.
