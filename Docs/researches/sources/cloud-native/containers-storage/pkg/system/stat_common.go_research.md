# sources/cloud-native/containers-storage/pkg/system/stat_common.go

Purpose: common non-FreeBSD fallback for file flags in `StatT`.

Important APIs/types/functions: defines empty `platformStatT` and `StatT.Flags() uint32`, returning zero.

Control flow: `Flags` references the embedded field only to silence unused warnings and returns zero.

State/persistence: none.

Dependencies/integration: embedded by `StatT` on non-FreeBSD platforms so callers can use a uniform `Flags` method.

Risks: callers must treat zero as either no flags or unsupported flags depending on platform.

Test signals: compile coverage across all non-FreeBSD platforms; behavior is intentionally trivial.
