<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/sound/snd_sst_tokens.h -->
# sources/distributed-fs/ceph-client/include/uapi/sound/snd_sst_tokens.h

Purpose: defines Intel SST/Skylake topology token numbers for module UUIDs, pin/queue metadata, resources, formats, pipeline config, manifest module resources, A-state tables, and format config indices.

Important APIs and types: `enum SKL_TKNS` is the ABI. It includes tuple/block tokens, pin type and dynamic-pin flags, module resource fields (`MAX_MCPS`, pages, IBS/OBS), pipe and format tokens, module parameter/capability tokens, library names, power/D0i3/DMA tokens, pipeline config tokens, manifest module resource/interface tokens, A-state tokens, and `SKL_TKN_U32_FMT_CFG_IDX`. The misspelled `SKL_TKL_U32_D0I3_CAPS` is intentionally kept and aliased for ABI compatibility.

Control flow: topology private data is parsed into Skylake DSP pipeline and module descriptors; direction/pin-count tokens scope subsequent format tokens, while manifest tokens describe firmware module capabilities available for graph creation.

State and persistence: no state is stored in this header. Numeric tokens are persistent topology ABI values and may be embedded in shipped firmware/topology files.

Dependencies and integration points: ties to `skl-tplg-interface.h`, Intel SST/Skylake ASoC topology code, firmware manifests, and userspace topology compilers.

Risks and test signals: risks include changing enum order, removing the typo alias, parser ambiguity around direction-scoped format tokens, and old topology blobs with retired token expectations. Test multiple topology versions, manifest resource tables, D0i3 tokens, bad block sizes, and 32/64-bit topology-tool compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/sound/snd_sst_tokens.h -->
