# sources/cloud-native/cri-o/internal/registrar/registrar.go

Purpose: provides an in-memory concurrent name registry mapping unique names to keys and keys to their reserved names.

Important APIs/types/functions: `ErrNameReserved`, `ErrNameNotReserved`, `ErrNoSuchKey`, `Registrar`, `NewRegistrar`, `Reserve`, `Release`, `Delete`, `GetNames`, `Get`, and `GetAll`.

Control flow: `Reserve` is idempotent for the same name/key but rejects name reuse by a different key. `Release` removes one name from both indexes. `Delete` removes every name for a key. Getters lock around map access and return direct or shallow-copied structures.

State and persistence behavior: all state is process-local in two maps protected by a mutex. No persistence exists. `GetNames` returns the underlying slice, and `GetAll` shallow-copies the map but not the slices.

Dependencies and integration points: uses `sync.Mutex`, `errors`, and `maps.Copy`. Suitable for runtime name reservation where names must be globally unique.

Risks: callers mutating slices returned by `GetNames` or `GetAll` can mutate registry internals. There is no context cancellation or durable conflict recovery.

Test signals: tests cover idempotent reserve, conflict detection, release idempotence, delete, lookup failures, and map retrieval.
