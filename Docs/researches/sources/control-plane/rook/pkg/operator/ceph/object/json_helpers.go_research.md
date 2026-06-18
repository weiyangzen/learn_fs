# sources/control-plane/rook/pkg/operator/ceph/object/json_helpers.go

## Purpose
`json_helpers.go` provides generic utilities for reading, updating, copying, and converting JSON-like `map[string]interface{}` objects used by object-store multisite/admin command logic.

## Important APIs, Types, and Functions
`getObjProperty[T]()` walks a required path and returns a typed terminal value. `updateObjProperty[T]()` walks a required path, replaces an existing terminal value, and returns the previous value, with JSON marshal/unmarshal fallback for typed slices such as `[]string`. `castJson()` converts arbitrary JSON-compatible values by marshaling and unmarshaling. `toObj()` converts a Go struct into a JSON object map. `deepCopyJson()` performs a JSON round-trip to produce an independent copy.

## Control Flow, State, and Persistence
The helpers are pure in-memory transformations except `updateObjProperty()`, which mutates the input map only after the full path exists. They return detailed errors for empty paths, missing keys, non-object intermediate nodes, and type mismatches.

## Dependencies and Integration Points
They depend only on `encoding/json`, `fmt`, and `strings`, and support higher-level code that patches decoded Ceph JSON structures before sending admin commands.

## Risks and Test Signals
Risks include the constrained generic type sets, JSON round-trip lossiness for numbers and custom types, update-only semantics that cannot create missing paths, and runtime type assertions on unstructured data. Tests cover successful and failing string/array reads, updates for strings/maps/arrays, missing paths, and deep-copy independence.
