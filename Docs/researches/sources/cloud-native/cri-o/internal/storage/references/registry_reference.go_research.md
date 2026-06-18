# sources/cloud-native/cri-o/internal/storage/references/registry_reference.go

Purpose: defines `RegistryImageReference`, a strongly typed registry-qualified image reference that must include a tag or digest. The package exists to keep CRI-O storage code from passing arbitrary strings for images crossing CRI or registry boundaries.

Important APIs/types/functions: `RegistryImageReference` wraps a private `reference.Named`; `RegistryImageReferenceFromRaw` is an internal constructor for already-parsed references; `ParseRegistryImageReferenceFromOutOfProcessData` parses external strings with docker normalization and `:latest` defaulting; `StringForOutOfProcessConsumptionOnly`, `Format`, `Registry`, and `Raw` expose controlled views. `ensureInitialized` panics on zero values.

Control flow: external input is parsed with `reference.ParseNormalizedNamed`, normalized with `reference.TagNameOnly`, then sent through `RegistryImageReferenceFromRaw`. The raw constructor strips tags from tag+digest references so digest identity wins, rejects name-only references by panic, and stores the validated reference. Accessors all call `ensureInitialized`.

State and persistence: the type itself is immutable value state around containers/image reference data. It serializes only when callers deliberately use `StringForOutOfProcessConsumptionOnly`, mainly for CRI/status metadata or on-disk runtime metadata.

Dependencies/integration: depends on `go.podman.io/image/v5/docker/reference`. `pkg/config.ImageConfig.ParsePauseImage` validates configured pause images through this type, and `internal/storage/runtime.go` uses `Raw` to build storage transport references and uses the out-of-process string in container metadata.

Risks: invalid raw construction panics instead of returning an error, so only trusted internal code should call it. Zero values also panic, which enforces constructors but can surprise tests or structs with omitted fields. Tag stripping for tag+digest input is intentional but can hide user-supplied tag text after parsing.

Test signals: paired tests cover default docker.io/library/latest normalization, invalid parse errors, raw constructor panics, zero-value panics, `fmt.Formatter` behavior without `fmt.Stringer`, raw reference recovery, and registry extraction.
