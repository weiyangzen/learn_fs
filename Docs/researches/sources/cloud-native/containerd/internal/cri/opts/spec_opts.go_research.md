# sources/cloud-native/containerd/internal/cri/opts/spec_opts.go

## Purpose

This file contains common OCI spec options used across CRI container spec generation: root handling, process args, annotations, security settings, capabilities, labels, sysctls, groups, sandbox shares, and namespace wiring.

## Important APIs, Types, and Functions

Key options include `WithRelativeRoot`, `WithoutRoot`, `WithProcessArgs`, `WithAnnotation`, `WithWindowsAffinityCPUs`, `WithAdditionalGIDs`, `WithoutDefaultSecuritySettings`, `WithCapabilities`, `WithoutAmbientCaps`, `WithSelinuxLabels`, `WithSysctls`, `WithSupplementalGroups`, `WithDefaultSandboxShares`, `WithoutNamespace`, `WithNamespacePath`, and `WithPodNamespaces`. `orderedMounts` sorts mounts by destination depth. Namespace path helpers return `/proc/<pid>/ns/*` paths. `mergeGids` deduplicates/sorts GIDs.

## Control Flow

Most functions return `oci.SpecOpts` closures that initialize missing spec substructures and mutate fields. `WithProcessArgs` merges CRI command/args with image entrypoint/cmd using Docker-like override rules and errors if no command remains. `WithCapabilities` expands CRI capability add/drop entries, handling `ALL` specially. `WithPodNamespaces` joins sandbox network/IPC/UTS namespaces, optionally PID target namespace and pod user namespace mappings.

## State and Persistence Behavior

These options mutate in-memory OCI specs. Namespace helpers encode host `/proc` paths but do not open them. `WithAdditionalGIDs` may read image rootfs group data through containerd OCI helpers when applied.

## Dependencies and Integration Points

It depends on CRI runtime types, image specs, OCI runtime specs, containerd OCI helpers, CRI util, and container metadata. Linux/Windows/Darwin spec builders compose these options with platform-specific options.

## Risks and Edge Cases

Command override behavior is subtle around nil versus empty slices. Capability strings are normalized by prefixing `CAP_`; invalid names may be rejected later. Namespace path joins assume sandbox/target PIDs are valid and alive. `WithoutDefaultSecuritySettings` intentionally clears defaults only when no custom base spec is used by the caller.

## Test Signals

Existing tests cover mount ordering. Good coverage also includes process arg merge cases, GID merging, capability `ALL` add/drop order, namespace path mutation, user namespace modes, and annotation/sysctl merging.
