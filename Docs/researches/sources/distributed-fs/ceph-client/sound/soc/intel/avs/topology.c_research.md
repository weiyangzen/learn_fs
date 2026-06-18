# sources/distributed-fs/ceph-client/sound/soc/intel/avs/topology.c

Purpose: Parses Intel AVS ASoC topology firmware into driver-owned topology dictionaries and path templates, wires topology callbacks into ASoC, loads/removes topology firmware, and attaches control/widget/link behavior.

Important APIs/functions: Token parsing framework (`avs_parse_tokens`, dictionary helpers, pointer parsers), manifest parser `avs_manifest()`, object parsers for libraries, audio formats, base/ext module configs, pin formats, pipeline configs, bindings, path/conditional path templates, initial configs, and NHLT configs. ASoC callbacks include route/widget/dai/link/control load handlers. Public functions are `avs_tplg_new()`, `avs_load_topology()`, and `avs_remove_topology()`.

Control flow: The manifest is parsed in a fixed dictionary order: header, libraries, audio formats, base configs, extended configs, pipeline configs, bindings, conditional path templates, optional initial configs, and optional NHLT configs. Widget load parses path templates from DAPM widget private data and stores the template in `w->priv`. DAI load assigns FE ops. Link load adjusts trigger ordering and merged format behavior. Controls parse private IDs and seed inverted values.

State and persistence: Parsed objects are devm-managed under the card device and stored in `struct avs_tplg`. Path templates are list-linked for later PCM lookup. Raw initial config and NHLT blobs are copied into managed allocations.

Dependencies and integration: Consumes UAPI AVS topology tokens, ALSA topology/DAPM/DAI/control APIs, machine data from `snd_soc_acpi_mach`, utility naming helpers, `control.h`, and structures from `topology.h`/`messages.h`.

Risks: Parser correctness depends on tuple order, entry boundary tokens, and little-endian size fields. The local snapshot contains duplicated lines in `modcfg_ext_parsers` and `parse_path_template()`, which are build/test signals. Several pointer parsers trust dictionary indices but require complete manifest ordering. Dynamic SSP/TDM name substitution only works for singular SSP/TDM machines. Raw data sections for initial/NHLT configs require precise length accounting.

Test signals: Load real topology files for HDA/DMIC/I2S, malformed tuple size/order fuzzing, singular and multi-SSP naming, conditional path parsing, controls with inverted defaults, NHLT blobs with raw payload, and build validation for duplicated-source corruption.
