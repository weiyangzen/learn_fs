# sources/cloud-native/nydus-snapshotter/pkg/converter/convert_windows.go

Purpose: Windows build-tag stub for converter APIs.

Important APIs and functions: declares Windows versions of `Pack`, `Merge`, `Unpack`, `IsNydusBlobAndExists`, `IsNydusBlob`, `IsNydusBootstrap`, `LayerConvertFunc`, `ConvertHookFunc`, and `MergeLayers`, all of which panic with `"not implemented"`.

Control flow: every function panics immediately.

State and persistence: none.

Dependencies and integration points: preserves package API shape on Windows builds while avoiding Unix-specific implementation. Imports containerd converter/content and OCI types for signature compatibility.

Risks: any Windows consumer that calls converter functionality will crash at runtime. This is acceptable only if Windows builds do not exercise nydus conversion.

Test signals: no Windows tests are listed.
