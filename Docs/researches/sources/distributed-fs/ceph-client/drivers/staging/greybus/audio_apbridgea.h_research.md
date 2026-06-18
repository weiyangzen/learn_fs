# sources/distributed-fs/ceph-client/drivers/staging/greybus/audio_apbridgea.h

## Purpose

`audio_apbridgea.h` defines the APBridgeA audio-control protocol ABI used by the helper library. It documents fixed I2S assumptions for the MSM8994 DSP to APBridgeA path and declares packed request structures.

## Important APIs, Types, and Functions

It defines request type constants, PCM format/rate bit masks, TX/RX direction bits, `struct audio_apbridgea_hdr`, and packed request structures for set config, register/unregister CPort, TX/RX data size, prepare, start, stop, and shutdown.

## Control Flow

Callers create one of these request structures, fill `hdr.type` and `hdr.i2s_port`, then send it as an APB audio-control request. TX start carries a 64-bit timestamp; most other phase requests carry only the header.

## State and Persistence Behavior

The header owns no state. It defines firmware-visible message layout, so field sizes, packing, and endian annotations are part of the protocol contract.

## Dependencies and Integration Points

It uses Linux/UAPI integer and endian types and is consumed by `audio_apbridgea.c` and higher-level audio codec code.

## Risks and Edge Cases

Because structures are `__packed`, any field changes are ABI changes. The comments say I2S port and CPort map to USB request index/value, but the implementation sends a packed payload through Greybus host-device output, so documentation should be kept current. `mclk_freq` is marked for possible removal.

## Test Signals

Check `sizeof()` and field offsets against firmware expectations. Validate all PCM rate/format masks accepted by firmware and ensure endian conversion occurs at callers.
