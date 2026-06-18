<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/ease_bindings/volume.h -->
# sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/ease_bindings/volume.h

## Purpose
Declares the OCF volume type ID, cache media parameter bundle, and volume registration helpers.

## Important APIs, Types, And Functions
`ease_ocf_volume_params` carries cache line/block size, media file size, Photon media file pointer, and logging flag. `volume_init` registers `EASE_OCF_VOLUME_TYPE`; `volume_cleanup` unregisters it.

## Control Flow
Provider startup fills `ease_ocf_volume_params`, registers this volume type with the OCF context, and passes the params as cache-device volume params.

## State And Persistence
The struct points at externally owned cache media. `enable_logging` is mutable runtime state toggled by provider start/stop.

## Dependencies And Integration Points
Includes Photon `IFile` and C OCF headers. Used by `provider.cpp` and `volume.cpp`.

## Risks And Test Signals
The struct does not own `media_file`, so lifetime is controlled by the cache filesystem. Invalid `blk_size` is caught in namespace/provider initialization. Source size reviewed: 20 lines.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/ease_bindings/volume.h -->
