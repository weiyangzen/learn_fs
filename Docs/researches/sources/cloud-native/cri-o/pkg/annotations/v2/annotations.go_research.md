# sources/cloud-native/cri-o/pkg/annotations/v2/annotations.go

Purpose: authoritative v2 annotation key registry and migration lookup logic for CRI-O annotations.

Important APIs/types/functions: v2 constants for cgroups, devices, FIPS, logs, platform runtime, seccomp, shm, spoofing, SELinux relabel skip, umask, userns, CPU tuning, IRQ, OCI seccomp hook, and stop signal; deprecated v1 constants; `SeccompNotifierActionStop`; `reverseAnnotationMigrationMap`; `GetAnnotationValue`; `GetAnnotationValueWithKey`; `findV1KeyForContainerSpecific`; `AllAnnotations`; `AllV1Annotations`; `AllAllowedAnnotations`.

Control flow: lookup first checks the requested v2 key, then exact v2-to-v1 fallback, then detects container-specific slash or dot suffixes by matching known v2 bases and appending the suffix to the v1 base. Allowed annotations are built by appending external/runtime prefixes, all v2 annotations, and all v1 annotations.

State and persistence: constants are metadata contract keys used in pod annotations, image annotations, and runtime-handler `allowed_annotations`. No mutable runtime state except package-level slices/maps.

Dependencies/integration: imported by config runtime validation to validate allowed annotations and by callers extracting annotation values. Runtime config comments document these v2 names as recommended while supporting v1 fallback.

Risks: `reverseAnnotationMigrationMap` omits v2 annotations without v1 equivalents; fallback is intentionally unavailable for those. Container-specific matching iterates over a map, but because it returns only after exact prefix+separator matches, ambiguous bases would be risky if introduced. `AllAllowedAnnotations` includes prefix-like strings such as `org.systemd.property.`; consumers must know whether they treat entries as exact keys or prefixes.

Test signals: package-level tests verify v2 precedence, exact fallback, slash/dot container suffix fallback, and inclusion of migrated v1/v2 annotations in the allowed list.
