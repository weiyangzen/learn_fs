<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/plugingetter/getter.go -->
# sources/cloud-native/moby/pkg/plugingetter/getter.go

Purpose: defines compatibility interfaces that let daemon code work with legacy v1 plugins and managed v2 plugins through one getter abstraction. Important APIs are mode constants `Lookup`, `Acquire`, `Release`, interfaces `CompatPlugin`, `PluginWithV1Client`, `PluginAddr`, `CountedPlugin`, and `PluginGetter`. Control flow is not implemented here; the file defines contracts for lookup/reference-counting, scoped paths, direct v1 clients, socket addresses, and capability callbacks. State is owned by implementations. Dependencies include net/time and legacy `plugins.Client`. Risks include interface drift across plugin systems and misuse of reference-count modes. Test signal is compile-time integration across plugin consumers.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/plugingetter/getter.go -->
