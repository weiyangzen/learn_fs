# sources/cloud-native/buildkit/util/winlayers/apply_nydus.go

## Purpose
implementation file in the adjacent Go package, contributing the symbols and behavior listed below.

## Important APIs, Types, Functions, Or Configuration
build constraints: nydus; package winlayers; functions/methods isNydusBlob, apply.

## Control Flow And Integration Points
The file is 73 lines in winlayers and participates in this package role: Windows layer compatibility code. It converts between OCI filesystem diffs and Windows layer tar layout when a context flag enables that mode. Control flow should be read through the listed functions and methods; notable exported or lifecycle symbols are included above. Integration points include containerd diff appliers/comparers, content store writers/readers, archive.Apply/WriteDiff, compression, optional nydus unpacking, and Windows PAX/security metadata. Risks include stream cancellation, descriptor/digest correctness, and fidelity of synthetic Windows metadata.

## State, Persistence, Dependencies, Risks, And Test Signals
State and persistence are inferred from symbols and dependencies: globals/types/functions listed above, filesystem/process/network state where the APIs call external daemons or stores, and in-memory closure/mutex/channel state where concurrency helpers are present. Dependencies: external packages: context, io, github.com/containerd/containerd/v2/core/diff, github.com/containerd/containerd/v2/core/mount, github.com/containerd/containerd/v2/pkg/archive, github.com/opencontainers/go-digest, github.com/opencontainers/image-spec/specs-go/v1, github.com/pkg/errors, github.com/containerd/nydus-snapshotter/pkg/converter. Primary risks are package-specific integration coupling, platform/build-tag behavior where present, cleanup and cancellation boundaries for daemon/executor/tracing code, and stale assumptions in tests or constants. This is production/helper code; test signal comes from adjacent package tests and integration users.
