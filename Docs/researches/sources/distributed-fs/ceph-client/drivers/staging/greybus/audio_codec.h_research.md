# sources/distributed-fs/ceph-client/drivers/staging/greybus/audio_codec.h

## Purpose

`audio_codec.h` is the shared Greybus audio codec/module/topology header. It defines runtime state structures, device masks, codec stream states, module descriptors, and prototypes for codec, topology, Greybus audio, and APBridgeA helper functions.

## Important APIs, Types, and Functions

Key definitions include `NAME_SIZE`, `MAX_DAIS`, device masks such as `GBAUDIO_DEVICE_OUT_SPEAKER`, jack masks, `enum gbaudio_codec_state`, `struct gbaudio_stream_params`, `struct gbaudio_codec_dai`, `struct gbaudio_codec_info`, `struct gbaudio_widget`, `struct gbaudio_control`, `struct gbaudio_data_connection`, `struct gbaudio_jack`, and `struct gbaudio_module_info`. It declares topology parse/release, module register/update/unregister, Greybus protocol wrappers, and APBridgeA wrappers.

## Control Flow

The Greybus module driver fills `gbaudio_module_info`, fetches topology, parses it, and registers the module with the codec. The codec and topology code share lists and function prototypes from this header to dynamically add ASoC objects and drive protocol operations.

## State and Persistence Behavior

The structures represent volatile kernel state for connected Greybus audio modules, runtime PCM state, topology-derived controls/widgets/routes, jack status, manager IDs, and Greybus connections. No persistent storage is defined.

## Dependencies and Integration Points

The header depends on Greybus, ASoC, and sound jack APIs. It is included by the codec, module, topology, APBridgeA, Greybus protocol, and helper files.

## Risks and Edge Cases

Many structure fields point into firmware topology memory or devm allocations, so lifetime depends on module disconnect ordering. `data_cport` is stored both as little-endian and through `connection` fields, so callers must consistently convert. Device masks mirror Android audio definitions, which can drift from upstream sound semantics.

## Test Signals

Compile all audio modules together and with optional sysfs. Validate lifetime of topology-backed strings, state transitions for both stream directions, and consistency between `MAX_DAIS`, `NUM_CODEC_DAIS`, actual DAI arrays, and data connection IDs.
