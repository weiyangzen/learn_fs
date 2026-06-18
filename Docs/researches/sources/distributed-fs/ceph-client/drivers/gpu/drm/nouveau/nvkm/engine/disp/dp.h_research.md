<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/dp.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/dp.h

Purpose: DisplayPort private header exposing DP output constructors/control helpers and local DPCD address/bit definitions used by `dp.c` and output/IOR code.

Important APIs and definitions: declares `nvkm_dp_new()`, `nvkm_dp_disable()`, and `nvkm_dp_enable()`. Defines DPCD receiver capability offsets, link configuration fields, link/sink status bits, sink power control, and LTTPR addresses for training repeaters.

Control flow: no runtime control flow. The constants drive read/write decisions in link training and AUX power paths.

State and persistence: none directly; the constants describe sink-side state accessed over AUX.

Dependencies and integration points: includes `outp.h` and complements DRM DP definitions. Generation-specific IOR DP callbacks rely on the training code using these DPCD constants consistently.

Risks: wrong bit definitions can break link training in non-obvious ways. Some constants overlap with external DRM headers, so future cleanup must avoid conflicting semantics.

Test signals: successful DP link training, DPCD capability parsing, LTTPR support, and sink power transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/dp.h -->
