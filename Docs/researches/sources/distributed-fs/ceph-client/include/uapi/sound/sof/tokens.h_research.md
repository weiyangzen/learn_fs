<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/sound/sof/tokens.h -->
# sources/distributed-fs/ceph-client/include/uapi/sound/sof/tokens.h

Purpose: assigns SOF topology token IDs and kcontrol IDs for buffers, DAIs, schedulers, controls, audio-processing components, vendor DAI blocks, CAVS formats, copier options, and platform-specific endpoints.

Important APIs and types: the ABI is a set of `SOF_TKN_*` constants and `SOF_TPLG_KCTL_*` IDs. Token groups include buffer size/caps/flags, DAI type/index/direction, scheduler period/priority/core/domain/memory/direction, gain/volume/SRC/ASRC fields, component format/UUID/CPC/pins/bindings, Intel SSP/DMIC/HDA/ALH/CAVS/copier, i.MX SAI/ESAI/MICFIL, MediaTek AFE, AMD ACPDMIC/ACP I2S/ACP SoundWire, stream D0i3/pause flags, mute LED, and mixer type.

Control flow: topology compilers write these token IDs into ALSA topology private data; SOF topology parsers translate them into IPC3/IPC4 component, pipeline, DAI, scheduler, and kcontrol configuration before firmware graph creation.

State and persistence: no state is stored here. Token values are persistent ABI embedded in topology files and must remain stable. Some token IDs are intentionally retired or overlapping for backward compatibility/platform-specific scopes.

Dependencies and integration points: integrates with SOF topology tooling, ALSA ASoC topology, SOF IPC message construction, Intel/AMD/i.MX/MediaTek endpoint drivers, and firmware graph parsers.

Risks and test signals: risks include token collisions such as mixer/AMD ACPI2S ranges, retired token reuse, parser disagreement with topology configuration files, and platform token additions without ABI discipline. Test all supported platform topology blobs, unknown token handling, old ABI 3.x topologies, and generated IPC payload validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/sound/sof/tokens.h -->
