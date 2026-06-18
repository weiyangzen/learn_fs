# sources/cloud-native/cri-o/internal/storage/image_id_test.go

Purpose: verifies `StorageImageID` parsing, formatting, and encapsulation behavior.

Important APIs/types/functions: tests `ParseStorageImageIDFromOutOfProcessData`, `IDStringForOutOfProcessConsumptionOnly`, and `fmt.Formatter` behavior.

Control flow: specs parse a valid SHA256-like full ID, iterate invalid inputs, assert zero-value use panics, and check `%s`/`%q` formatting while confirming the type is not a `fmt.Stringer`.

State and persistence behavior: no persistent state.

Dependencies and integration points: uses Ginkgo/Gomega and Go fmt interfaces.

Risks: test data assumes the identifier validation rules used by containers/image. It does not test `imageRef` against a real store.

Test signals: protects the type-safety contract that image IDs are full validated IDs and not general strings.
