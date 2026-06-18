# sources/distributed-fs/eos/mgm/auth/AccessChecker.hh

Purpose: declares the stateless `eos::mgm::AccessChecker` authorization helper for containers, files, and public path access.

Important APIs and types: two `checkContainer` overloads accept either linked attributes or an already built `Acl`. `checkFile` checks a file with requested mode and parent directory mode. `checkPublicAccess` checks anonymous/public access for a full path and virtual identity.

Control flow: callers are expected to gather all required metadata and xattrs before invoking these methods; the header notes that no external information should be needed by the overload that accepts `Acl`.

State and persistence: no instance or static state is declared; methods are static and read-only over supplied metadata/identity.

Dependencies and integration points: includes namespace macros, identity mapping, and `IContainerMD`; forward-declares file/container metadata and `Acl`. Used by authorization-sensitive MGM paths that need reusable POSIX+ACL checks.

Risks: the API takes raw metadata pointers and does not express nullability. `checkFile` requires the parent directory to be checked separately; callers can accidentally use it alone and miss directory permissions.

Test signals: compile tests should verify callers can pass prebuilt ACLs without pulling path lookup dependencies. Unit tests should exercise null handling expectations if callers may pass missing metadata.
