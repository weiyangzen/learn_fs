# sources/distributed-fs/ceph-client/sound/soc/intel/avs/topology.h

Purpose: Declares the parsed AVS topology object model shared by topology parsing, PCM path lookup, and path instantiation.

Important APIs/types: `struct avs_tplg` owns manifest metadata and dictionaries for libraries, audio formats, module configs, pipeline configs, bindings, conditional path templates, init configs, and NHLT configs. Other key types include `avs_tplg_modcfg_ext`, `avs_tplg_pplcfg`, `avs_tplg_binding`, `avs_tplg_path_template`, `avs_tplg_path`, `avs_tplg_pipeline`, and `avs_tplg_module`. Public APIs create/load/remove topology.

Control flow role: `topology.c` fills these structures from firmware topology; `pcm.c` discovers path templates from widgets; `path.c` traverses templates to create live pipelines/modules and configure firmware.

State and persistence: Parsed topology is managed for the lifetime of the ASoC card/component. Runtime paths borrow pointers into these structures, so topology must not be removed while paths are active.

Dependencies and integration: Includes list support and `messages.h` for audio format, UUID, DMA, and module configuration definitions. Expects ALSA component/widget forward declarations.

Risks: Many members are borrowed pointers into dictionary arrays, making load order and lifetime critical. Unioned extended config fields depend on module UUID interpretation. Conditional path templates carry cross-topology names/IDs that must match registered components.

Test signals: Compile users, topology load/unload, active stream during component removal prevention, path creation across every supported module type, and conditional path cross-topology matching.
