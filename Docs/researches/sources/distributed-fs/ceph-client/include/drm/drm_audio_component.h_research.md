# sources/distributed-fs/ceph-client/include/drm/drm_audio_component.h

## Purpose
This header defines the component interface used for direct cooperation between DRM display drivers and HDA audio drivers, especially for HDMI/DisplayPort audio power, ELD reporting, clock/rate synchronization, and hotplug notification.

## Important APIs, types, and functions
`struct drm_audio_component_ops` is implemented by the DRM side and exposes module ownership, audio power well get/put, codec wake override, CDCLK query, audio rate synchronization, and ELD retrieval. `struct drm_audio_component_audio_ops` is implemented by the audio side and exposes ELD notification, pin-to-port mapping, and optional component master bind/unbind callbacks. `struct drm_audio_component` binds the DRM device, both ops tables, and a `master_bind_complete` completion.

## Control Flow
The HDA driver calls DRM ops when it needs display power, current clocking, sample-rate programming, or ELD bytes. The DRM driver calls audio ops when display hotplug or pipeline setup/teardown changes pin sense or ELD. Component binding uses the completion to coordinate master availability.

## State and Persistence
Persistent state lives in the participating DRM and audio drivers; this header stores only cross-driver pointers and a binding completion. ELD bytes and enabled state are snapshots supplied on demand.

## Dependencies and Integration Points
It depends on Linux component binding, completion, module pinning, and HDMI/DP audio conventions. It integrates display hotplug, audio codec power management, and audio stream setup across independent drivers.

## Risks and Test Signals
Risks include dangling ops during module unload, unbalanced power-well wakerefs, stale ELD after hotplug, mismatched pin-to-port mapping, and races while binding or unbinding the component master. Tests should cover hotplug while HDA is power-saving, partial ELD buffer copies, invalid ELD return paths, rate changes during modeset, and driver unload with active audio clients.
