# sources/cloud-native/moby/daemon/internal/compat/compat.go

## Purpose
Provides JSON response compatibility wrappers that can add legacy fields or omit newer fields without mutating source structs.

## APIs, Control Flow, and Integration
`Wrapper.MarshalJSON` marshals `Base` with HTML escaping disabled, optionally unmarshals into a map, deletes omitted fields, recursively merges extra fields, and marshals again. `WithExtraFields` accumulates additive-only fields; existing output values win except nil values may be replaced. `WithOmittedFields` records top-level fields to delete. `Wrap` constructs the wrapper.

## State, Dependencies, and Risks
State is per-wrapper maps/slices. Risks include map-based JSON reordering, top-level-only omit semantics, type erasure through `map[string]any`, and marshal failure for non-object base JSON when options are present. Tests cover add/omit, nil field replacement, nested wrapped values, and no HTML escaping.
