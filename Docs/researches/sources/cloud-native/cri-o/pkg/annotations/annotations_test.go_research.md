# sources/cloud-native/cri-o/pkg/annotations/annotations_test.go

Purpose: plain Go tests for annotation migration lookup and allowed annotation inventory.

Important APIs/types/functions: tests `v2.GetAnnotationValue`, deprecated v1 constants, v2 constants, and package-level `AllAllowedAnnotations`.

Control flow: table-driven tests verify v2 precedence, v1 fallback, missing keys, slash and dot container-specific suffix fallback, and specific annotations like DisableFIPS and LinkLogs. Additional tests iterate expected v2-to-v1 mappings and ensure allowed-list presence.

State and persistence: in-memory annotation maps only.

Dependencies/integration: imports `testing` and `pkg/annotations/v2`. The tests live in package `annotations`, so they also validate the legacy facade's `AllAllowedAnnotations` variable.

Risks: expected reverse mapping list is duplicated in tests and can drift when new migrated annotations are added. Tests call `v2.GetAnnotationValue` directly in the main table rather than the wrapper, so wrapper delegation has only indirect coverage.

Test signals: good migration coverage for base and container-specific keys, plus allowed-list regression detection for migrated annotations.
