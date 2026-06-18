<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/control.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/avs/control.c

Purpose: ALSA control callbacks for topology-defined AVS volume and mute controls backed by active DSP peak-volume/gain modules.

Important APIs, types, and functions: `avs_control_volume_get/put/info()`, `avs_control_mute_get/put/info()`, helper `avs_get_kcontrol_adev()`, and `avs_get_volume_module()`.

Control flow: get callbacks find the AVS device from the DAPM kcontrol, lock `path_mutex`, search active AVS paths/pipelines/modules for a peakvol or gain module with the topology control ID, fetch current DSP volume/mute through IPC when active, update cached `avs_control_data.values`, and copy values to userspace. Put callbacks validate inputs against mixer min/max, compare with cached values, lock path construction, update the active DSP module when present, cache the new values, and return `1` for changed controls. Info callbacks describe integer/boolean ranges and channel counts.

State and persistence: `struct avs_control_data` attached to topology dobj stores control ID and last values. If a module is inactive, get/put operate on cached values only, preserving desired state until the path exists.

Dependencies and integration points: depends on topology private data, `path.c` runtime module lists, `messages.c` IPC wrappers for peak-volume get/set, and ALSA SoC mixer control structures.

Risks: `avs_get_volume_module()` drops `path_list_lock` before returning a module pointer; `path_mutex` is intended to protect construction/destruction, but misuse elsewhere could invalidate pointers. Mute values are inverted relative to DSP mute booleans (`values[i] = !mute`), so UI semantics must stay consistent. Validation loop handles `num_channels == 0` by checking one value.

Test signals: mixer get reflects live DSP state while streams run, put updates active streams immediately, cached values survive inactive paths, invalid ranges return `-EINVAL`, and topology controls expose correct counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/control.c -->
