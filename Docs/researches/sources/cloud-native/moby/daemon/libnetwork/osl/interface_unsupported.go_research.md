## sources/cloud-native/moby/daemon/libnetwork/osl/interface_unsupported.go

Purpose: non-Linux build stub defining `Interface` for platforms where Linux interface operations are unavailable.

Important APIs/types/functions: under `//go:build !linux`, it declares an empty `Interface` type.

Control flow: no runtime behavior. It exists to satisfy package type references when Linux-specific files are excluded.

State and persistence behavior: none.

Dependencies and integration points: pairs with platform-specific namespace/sandbox stubs so libnetwork can compile on unsupported platforms with reduced functionality.

Risks: code that assumes Linux `Interface` methods must be build-tagged or otherwise unavailable on non-Linux. The empty type intentionally provides no operations.

Test signals: no tests in this subset; build coverage on non-Linux is the relevant signal.
