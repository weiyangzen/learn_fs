# sources/cloud-native/cri-o/internal/storage/registry_reference.go

Purpose: re-exports `references.RegistryImageReference` from the parent `internal/storage` package so storage callers can use the concept without importing the dependency-breaking subpackage directly.

Important APIs/types/functions: defines `type RegistryImageReference = references.RegistryImageReference`, an alias rather than a new type.

Control flow: none beyond compile-time aliasing.

State and persistence: no state; all value semantics and persistence behavior are owned by `internal/storage/references`.

Dependencies/integration: imports the references subpackage. Comments explain this split breaks a dependency loop while keeping the type conceptually part of storage, especially alongside `StorageImageID`.

Risks: because this is an alias, method sets and zero-value panic behavior are exactly the subpackage behavior. Any future encapsulation change must preserve mockgen and package-cycle constraints.

Test signals: indirect tests come from storage runtime and references tests; this alias itself has no dedicated test need beyond compilation.
