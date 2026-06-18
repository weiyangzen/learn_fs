<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/rootless/mountopts/mountopts_others.go -->
# sources/cloud-native/buildkit/util/rootless/mountopts/mountopts_others.go

Purpose: non-Linux stub implementation for rootless mount option fixup.

Important APIs and types: `UnprivilegedMountFlags`, `FixUp`, and `FixUpOCI` mirror the Linux API.

Control flow: returns an empty flag list and leaves mount slices unchanged.

State and persistence: none.

Dependencies and integration: keeps cross-platform callers compiling for containerd and OCI mount types.

Risks: rootless mount flag preservation is only meaningful on Linux; non-Linux behavior is explicitly a no-op.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/rootless/mountopts/mountopts_others.go -->
