# sources/control-plane/rook/pkg/operator/ceph/object/json_helpers_test.go

## Purpose
`json_helpers_test.go` verifies the behavior and error surfaces of the unstructured JSON helper functions.

## Important APIs, Types, and Functions
`Test_getObjPropertyStr` tests nested string retrieval and wrong-type/missing-key failures. `Test_getObjPropertyObjArr` tests retrieval of `[]interface{}` object arrays and rejects other terminal types. `Test_deepCopyJson` confirms copied arrays do not alias the original. `Test_updateObjProperty`, `Test_updateObjPropertyObj`, and `Test_updateObjPropertyArr` verify replacement of existing nested fields and preservation of input JSON on missing paths.

## Control Flow, State, and Persistence
Tests decode JSON strings into maps, call helpers, and compare returned values plus marshaled output JSON. All state is in-memory; mutation checks focus on whether `updateObjProperty()` changes only existing terminal properties.

## Dependencies and Integration Points
The tests use Go JSON decoding, `reflect.DeepEqual`, and `stretchr/testify`. They protect helper behavior used by higher-level object-store JSON patching, where malformed Ceph JSON should produce actionable errors instead of silent mutation.

## Risks and Test Signals
Signals are strong for common string/object-array/map/array paths and deep copy behavior. Gaps include numeric conversions, empty path errors, non-object intermediate paths in `updateObjProperty()`, `toObj()`, `castJson()` failure cases, and generic `[]string` fallback conversion.
