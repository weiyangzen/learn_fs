<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/sound/intel/avs/tokens.h -->
# sources/distributed-fs/ceph-client/include/uapi/sound/intel/avs/tokens.h

Purpose: defines Intel AVS topology token IDs used by ALSA topology blobs to describe firmware manifests, libraries, audio formats, module configurations, pipelines, bindings, path templates, pins, kcontrols, init configs, and NHLT configs.

Important APIs and types: `enum avs_tplg_token` is the ABI. Token ranges are grouped by logical structure: manifest tokens `1..11`, libraries `101..102`, audio formats `201..209`, module base config `301..305`, module extended config `401..443`, pipeline config `1401..1406`, bindings `1501..1509`, pipelines `1601..1604`, modules `1701..1710`, path templates/paths `1801..2103`, pin formats `2201..2203`, kcontrols `2301`, init configs `2401..2403`, and NHLT configs `2501..2502`.

Control flow: topology authoring tools emit these IDs into private topology tuples; the Intel AVS ASoC driver parses the tuple stream and populates in-kernel AVS topology objects before creating firmware pipelines and modules.

State and persistence: no runtime state is stored here. The token numbers are persistent ABI values embedded in topology files and must remain stable across kernel and userspace topology-tool versions.

Dependencies and integration points: the header has no type dependency beyond standard enum syntax. It integrates with ALSA topology parsers, Intel AVS firmware module descriptions, NHLT endpoint data, and user/distribution-provided topology binaries.

Risks and test signals: high risks are renumbering tokens, reusing IDs with incompatible meaning, token aliases for conditional path templates sharing base IDs, and parser drift between topology tools and kernel. Test by loading representative AVS topologies, fuzzing tuple order/counts, checking unknown token rejection, and validating old topology blobs across driver updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/sound/intel/avs/tokens.h -->
