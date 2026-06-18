# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dp/dp_drm.h

Purpose: This header is the DRM bridge interface for the MSM DP driver. It exposes the bridge wrapper type, connector creation, bridge initialization, and callbacks implemented across `dp_drm.c` and `dp_display.c`.

Important APIs and types: `struct msm_dp_bridge` embeds `struct drm_bridge` and points back to `struct msm_dp`. `to_dp_bridge()` performs `container_of` conversion. Declarations cover `msm_dp_drm_connector_init()`, `msm_dp_bridge_init()`, atomic enable/disable/post-disable, mode validation, mode set, HPD enable/disable, and HPD notify.

Control flow and integration: `dp_drm.c` allocates this bridge wrapper and installs either DP or eDP bridge functions. `dp_display.c` implements several declared callbacks because they require private display state and hardware sequencing. The header therefore forms a cross-file contract between generic DRM bridge glue and the DP display controller implementation.

Dependencies and state: It includes Linux types, DRM bridge, `msm_drv.h`, and `dp_display.h`. It does not own state but makes the `msm_dp` pointer reachable from DRM callbacks.

Risks and test signals: The main risk is signature drift between bridge funcs and exported implementations, especially as DRM bridge APIs evolve. Compile coverage is the primary signal, supplemented by runtime bridge attach, mode set, HPD callbacks, and eDP/DP split behavior.
