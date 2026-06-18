<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/control.h -->
# sources/distributed-fs/ceph-client/sound/soc/intel/avs/control.h

Purpose: header for AVS topology control private data and ALSA control callbacks.

Important APIs, types, and functions: defines `struct avs_control_data` with topology control ID and per-channel cached values up to `SND_SOC_TPLG_MAX_CHAN`; declares volume and mute get/put/info callbacks.

Control flow: topology parsing and control registration can reference these callbacks; runtime operations are implemented in `control.c`.

State and persistence: `avs_control_data.values` is the persistent cache for inactive or last-known DSP control values.

Dependencies and integration points: includes ALSA control and UAPI ASoC topology limits. Used by topology/control registration code and by `control.c`.

Risks: value array size is fixed to topology maximum; callers must not copy more DSP channels than that. The ID must match module template `ctl_id` for live lookup to work.

Test signals: topology controls allocate private data of this shape and callback function pointers resolve during build/link.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/control.h -->
