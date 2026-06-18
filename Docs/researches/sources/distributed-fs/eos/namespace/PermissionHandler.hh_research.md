## sources/distributed-fs/eos/namespace/PermissionHandler.hh

Purpose: Declares permission conversion and filtering helpers for namespace metadata access checks.

Important APIs and types: defines `CANREAD`, `CANWRITE`, `CANENTER` bit macros and static `PermissionHandler` methods, including a templated xattr-map overload for `filterWithSysMask`.

Control flow: callers convert stored mode and requested access into internal flags, then call `checkPerms`; xattr-aware callers pass maps containing optional `sys.mask`.

State and persistence: stateless helper. It interprets persisted `sys.mask` xattr values.

Dependencies and integration: includes namespace macros and `IFileMD.hh` for mode/metadata context. Template works with `std::map` and protobuf-like maps exposing `find` and `second`.

Risks: macros can collide in global preprocessor scope. The template assumes mapped values are string-like. Permission behavior must remain consistent with POSIX expectations and EOS `enter` semantics.

Test signals: compile test with both std and protobuf map types, plus behavior tests matching `PermissionHandler.cc`.
