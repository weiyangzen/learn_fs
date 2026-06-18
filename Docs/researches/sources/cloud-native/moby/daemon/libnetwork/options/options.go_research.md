## sources/cloud-native/moby/daemon/libnetwork/options/options.go

Purpose: reflection-based utility for converting unstructured option maps into strongly typed configuration structs while reporting typed errors for unknown, unsettable, or mismatched fields.

Important APIs/types/functions: error types `NoSuchFieldError`, `CannotSetFieldError`, and `TypeMismatchError`; `Generic map[string]any`; generic function `GenerateFromModel[T any](options Generic) (T, error)`.

Control flow: `GenerateFromModel` determines whether `T` is a pointer, allocates a new value of the target struct type, iterates map entries, locates fields by exact name, validates settable/exported status and exact type equality, sets values through reflection, then returns either the pointer or value form matching `T`.

State and persistence behavior: stateless conversion. The returned object is freshly allocated/populated; the input map is not mutated.

Dependencies and integration points: uses Go `reflect` and `fmt`. It is a generic helper likely used by libnetwork components accepting loose option bags while wanting typed internal models.

Risks: requires exact Go field names and exact dynamic value types, so aliases, assignable-but-not-identical types, pointer/value mismatch, and numeric widening are rejected. Map iteration order means when multiple invalid options exist, the reported first error is nondeterministic. It assumes `T` or `*T` is a struct-like target; non-struct use may panic or fail unexpectedly.

Test signals: `options_test.go` covers value and pointer models plus all three error classes.
