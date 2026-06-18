# sources/distributed-fs/eos/namespace/ns_quarkdb/NsQuarkdbPlugin.cc

Purpose: implements the plugin entry points that register and create the QuarkDB namespace group.

Important APIs/types/functions: `ExitFunc`, `PF_initPlugin`, optional `plugin_coverage` for coverage builds, `NsQuarkdbPlugin::CreateGroup`, and `DestroyGroup`.

Control flow: `PF_initPlugin` constructs `PF_RegisterParams` for `"NamespaceGroup"`, registers it with platform services, and returns `ExitFunc` on success or `nullptr` on registration failure. `CreateGroup` returns `new QuarkNamespaceGroup`; `DestroyGroup` deletes the object or returns `-1` for null.

State and persistence: no persistent state; plugin registration only.

Dependencies and integration: depends on EOS plugin manager ABI, `NamespaceGroup.hh`, and standard streams for registration messages. The plugin manager calls these C-linkage entry points.

Risks: object type safety depends on plugin manager pairing create/destroy correctly. Registration prints to stdout/stderr, which may be undesirable in some daemon contexts. `services` is not null-checked.

Test signals: covered by plugin loading tests or runtime namespace backend selection; coverage builds can call `plugin_coverage`.
