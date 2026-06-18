# sources/distributed-fs/eos/namespace/ns_quarkdb/NsQuarkdbPlugin.hh

Purpose: declares C ABI plugin entry points and the static factory/destroy wrapper for the QuarkDB namespace plugin.

Important APIs/types/functions: `extern "C" int32_t ExitFunc()`, `extern "C" PF_ExitFunc PF_initPlugin(...)`, `NsQuarkdbPlugin::CreateGroup`, and `DestroyGroup`.

Control flow: declarations only.

State and persistence: none.

Dependencies and integration: includes `Plugin.hh` and `Namespace.hh`; consumed by the plugin implementation and plugin manager.

Risks: ABI signatures must remain stable with the plugin framework. Returned `void*` requires correct cast in destroy path.

Test signals: plugin loading/registration tests cover this interface indirectly.
