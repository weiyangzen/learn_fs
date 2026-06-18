# sources/distributed-fs/eos/mgm/proc/user/TokenCmd.hh

Purpose: declares `TokenCmd`, the protobuf-backed token command.

Important APIs and types: derives from `IProcCommand`, includes `ConsoleRequest.pb.h`, constructs from `RequestProto&&` and `VirtualIdentity&`, overrides `ProcessRequest()`, and exposes helper methods `StoreToken()` and `GetTokenPrefix()`.

Control flow: public helpers show that token persistence is part of the command contract, not hidden entirely inside `ProcessRequest`.

State and persistence: no direct member fields are declared. Helper signatures reveal persisted token path generation and storage are keyed by token string, voucher ID, UID, and GID.

Dependencies and integration: command participates in the async proc framework and relies on implementation-level integration with `EosTok`, key stores, and namespace metadata.

Risks: helper methods are public, so other code can store tokens without going through `ProcessRequest()` authorization unless call sites are controlled. Tests should prefer end-to-end `ProcessRequest` coverage and include direct helper tests for prefix creation, ownership correction, and duplicate voucher behavior.
