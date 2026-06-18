# sources/cloud-native/moby/daemon/internal/compat/compat_test.go

## Purpose
Documents and verifies compatibility JSON wrapper behavior.

## APIs, Control Flow, and Integration
Tests cover no-options passthrough, extra fields, omitted fields, combined add/omit, replacing nil pointer fields with extra values, nested wrapped structs as extra fields, and disabled HTML escaping for `&` and `<...>`. Assertions compare exact JSON strings.

## State, Dependencies, and Risks
No external state. Exact string comparisons intentionally lock output ordering produced by map marshaling in the tested cases, which can make tests sensitive to future implementation changes. The suite does not cover invalid base JSON shapes, conflicting non-nil fields, or repeated option conflict ordering beyond comments.
