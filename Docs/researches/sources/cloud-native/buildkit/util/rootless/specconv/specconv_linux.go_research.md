<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/rootless/specconv/specconv_linux.go -->
# sources/cloud-native/buildkit/util/rootless/specconv/specconv_linux.go

Purpose: mutates an OCI runtime spec to be usable with rootless runc on Linux.

Important APIs and types: `ToRootless`.

Control flow: filters out mounts whose destination starts with `/sys`, then clears Linux resource settings and cgroup path to avoid cgroup operations that rootless runc cannot perform.

State and persistence: in-place mutation of the supplied `*specs.Spec`; no external state.

Dependencies and integration: depends on OCI runtime spec types. Integrated where BuildKit configures rootless executors.

Risks: assumes `spec.Linux` is non-nil; a nil Linux section would panic. Removing all `/sys*` mounts may affect workloads that expect sysfs, but comments document this as an intentional rootless workaround.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/rootless/specconv/specconv_linux.go -->
