# sources/distributed-fs/ceph-client/sound/soc/sof/control.c

Purpose: generic ALSA kcontrol callbacks that delegate SOF mixer/switch/enum/bytes operations to IPC/topology-specific control handlers.

Important APIs/types/functions: `snd_sof_volume_get/put/info`, `snd_sof_switch_get/put`, `snd_sof_enum_get/put`, `snd_sof_bytes_get/put`, `snd_sof_bytes_ext_put`, `snd_sof_bytes_ext_volatile_get`, and `snd_sof_bytes_ext_get`.

Control flow: each get/put callback extracts `snd_sof_control` from topology private data, fetches `sdev`, gets topology ops via `sof_ipc_get_ops(sdev, tplg)`, and calls the matching control callback when present. Volume info computes type/count/min/max from `soc_mixer_control` and `num_channels`. Volatile ext get resumes the device, boots DSP if needed, calls the IPC-specific volatile getter, and autosuspends.

State and persistence: kcontrol values are held in `snd_sof_control` and firmware/topology-specific backing stores; this file mostly passes through. Runtime PM state is touched for volatile reads.

Dependencies and integration points: ALSA SoC control structures, SOF topology IPC ops, runtime PM, and DSP boot helper.

Risks: missing topology control callbacks silently return no change/zero for most operations, which can hide incomplete IPC implementations. `bytes_ext_put` only validates minimum TLV header size before delegation. Runtime PM errors are rate-limited but returned for volatile gets.

Test signals: mixer/switch/enum/bytes control get/put under IPC3 and IPC4 topology implementations, volatile read with runtime suspend, and volume-info type/range behavior.
