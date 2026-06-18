
# sources/distributed-fs/ceph-client/sound/pci/oxygen/xonar_dg.h

Purpose: internal header for Xonar DG/DGX support shared between low-level codec code and mixer/model definition.

Important definitions: GPIO masks for magic/HP detect/input route/HP rear/output enable; capture source enum values for mic/front mic/line/aux; playback destination enum values for headphones/front-panel headphones/multichannel; CS4245 shadow operation enum; `struct dg` model data with CS4245 shadow, output selection, per-source input volumes, and selected input.

Integration: `xonar_dg.c` provides codec/routing operations, `xonar_dg_mixer.c` defines controls and `model_xonar_dg`, and `oxygen.c` selects that model. The model_data layout is the persistence boundary for controls and resume.

Risks: enum values are directly stored in mixer state and used for routing decisions; changing them can break userspace-visible control values. Test signals include compile linkage, all DG ALSA controls, GPIO routing, shadow save/load, and model selection.
