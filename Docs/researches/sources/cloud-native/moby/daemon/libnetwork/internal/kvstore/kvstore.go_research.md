# Research: sources/cloud-native/moby/daemon/libnetwork/internal/kvstore/kvstore.go

Purpose: defines the storage abstraction used by libnetwork datastore backends. Important pieces are errors `ErrKeyModified`, `ErrKeyNotFound`, `ErrPreviousNotSpecified`, `ErrKeyExists`, interface `Store`, and struct `KVPair`.

Control flow: there is no implementation logic; the interface requires plain put/delete/list/exists plus compare-and-swap style `AtomicPut` and `AtomicDelete`, and a `Close` method. `KVPair` carries key, raw value, and last modification index used by atomic methods.

State/dependencies: no state in this file. Dependencies are standard errors. Integration points include the bbolt backend and higher-level libnetwork datastore object persistence. Risks are contract-level: backends must consistently map missing keys, modified indices, and create-vs-update behavior to these sentinel errors, or datastore CAS logic may mis-handle concurrent updates. Test signal is indirect through backend/datastore tests.
