# sources/cloud-native/cri-o/pkg/annotations/annotations.go

Purpose: backwards-compatible annotation facade that re-exports deprecated v1 constants and the v2 lookup helper from `pkg/annotations/v2`.

Important APIs/types/functions: `GetAnnotationValue`; deprecated constants such as `UsernsModeAnnotation`, `UnifiedCgroupAnnotation`, `SeccompProfileAnnotation`, `DisableFIPSAnnotation`, and many CPU/runtime annotations; `AllAllowedAnnotations`.

Control flow: `GetAnnotationValue` delegates directly to `v2.GetAnnotationValue`. Constants are compile-time aliases to v2 package constants.

State and persistence: no runtime state. The constants define allowed pod/container/image annotation keys that can appear in Kubernetes metadata and runtime config allowlists.

Dependencies/integration: imports `pkg/annotations/v2`. Existing callers can keep importing `pkg/annotations` while new code moves to v2 names.

Risks: deprecated names remain a compatibility surface. Because this package re-exports v1 constants from v2, any v2 mapping error propagates to legacy users. New v2 annotations not re-exported here may be invisible to old importers.

Test signals: annotations tests check fallback lookup and allowed-list inclusion for v1 and v2 keys.
