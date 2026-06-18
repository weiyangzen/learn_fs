<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/sound/skl-tplg-interface.h -->
# sources/distributed-fs/ceph-client/include/uapi/sound/skl-tplg-interface.h

Purpose: defines Intel Skylake DSP topology private-data constants and small ABI structs used by topology blobs to describe channel formats, module types, device/link kinds, scheduling pins, and algorithm parameters.

Important APIs and types: constants include private control types, max copier config size, queue limits, and UUID string size. Enums cover event types, channel configurations, module types, core affinity, pipe connection types, hardware connection, device type, interleaving, sample type, pin homogeneity, module parameter type, token direction, and tuple/data block type. `skl_dfw_algo_data` is a packed flexible-parameter blob for module algorithm data.

Control flow: ALSA topology private data carries these values; the Skylake ASoC topology parser decodes tuple/data blocks, configures module graphs, and passes packed parameter blobs to firmware during initialization, set, or bind phases.

State and persistence: no state lives in the header. Topology files persist these numeric values, and the kernel translates them into runtime DSP pipeline/module state.

Dependencies and integration points: depends on Linux types and integrates with `snd_sst_tokens.h`, Skylake/HDA DSP firmware, ALSA topology controls, and machine-driver topology files.

Risks and test signals: risks include ABI drift in enum numeric values, flexible-array bounds in `skl_dfw_algo_data`, channel-config aliases, and topology/parser mismatch for heterogeneous pins. Test old and new topology loads, invalid block sizes, module init/set/bind transitions, and firmware rejection paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/sound/skl-tplg-interface.h -->
