# sources/cloud-native/nydus/upgrade/src/backend/mod.rs

Purpose: defines the storage-backend abstraction for saving/restoring daemon device fds and serialized state during online upgrade.

Important APIs/types/functions: module exports `unix_domain_socket`. `StorageBackendErr` enumerates `CreateUnixStream`, `SendFd`, `RecvFd`, and `NoEnoughFds`. `Result<T>` aliases the backend error result. `StorageBackend` requires `Send + Sync` and defines `save(&mut self, fds, data) -> Result<usize>` plus `restore(&mut self) -> Result<(Vec<RawFd>, Vec<u8>)>`.

Control flow: concrete backends implement the trait to persist raw fds plus byte state. The included test backend copies fds and state into memory and returns clones on restore.

State and persistence: the trait describes persistence but owns no state itself. Implementations decide whether state is in memory, socket-mediated, or elsewhere.

Dependencies and integration points: uses `std::os::fd::RawFd` and `thiserror`. The Unix-domain-socket implementation in the child module is the primary concrete integration. Higher-level upgrade code can depend on trait objects.

Risks: raw fd ownership semantics are not explicit in the trait; implementors and callers must agree whether returned fds are borrowed, duplicated, or ownership-transferred. `NoEnoughFds` grammar is minor but part of error display.

Test signals: unit test validates trait-object save/restore round trip with a simple in-memory backend and fixed fd/data arrays.
