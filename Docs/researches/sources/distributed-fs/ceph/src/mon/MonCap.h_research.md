# sources/distributed-fs/ceph/src/mon/MonCap.h

## Purpose

`MonCap.h` declares the monitor capability model used by Ceph auth to decide whether an entity may perform monitor service or command operations. It defines rwx bit constants, command argument constraints, grant structure, and the top-level `MonCap` container.

## Important APIs, Types, and Functions

`MON_CAP_R`, `MON_CAP_W`, `MON_CAP_X`, `MON_CAP_ALL`, and `MON_CAP_ANY` define monitor permission bits. `mon_rwxa_t` wraps the byte bitmask. `StringConstraint` supports none/equal/prefix/regex matching for command arguments. `MonCapGrant` stores service, profile, command, constrained command args, fs name, network string and parsed network, allow bits, and cached profile grants. `MonCap` stores original text plus grant vector and exposes parsing, merging, encoding, dumping, full capability checks, allow-all checks, allowed fs-name extraction, and `fs_name_capable()`.

## Control Flow and State

The header documents the five grant forms: blanket allow, service allow, profile, command with optional argument constraints, and fs-name restriction. `fs_name_capable()` handles direct fs-name grants, allow-all, and profile-expanded fs/mds grants for a requested mask. `allowed_fs_names()` returns a constrained list only when every grant is fs-name-specific; otherwise it returns an empty vector to signal unrestricted or mixed semantics.

## Dependencies and Integration Points

Dependencies include Ceph common forward declarations, entity names, address types, encoding macros, and buffer/formatter declarations. `WRITE_CLASS_ENCODER(MonCap)` makes the text capability persistable in auth records. Monitor command handling, session service checks, filesystem map filtering, and bootstrap key creation depend on these declarations.

## Risks and Test Signals

Any change to grants or matching semantics is security-sensitive. Tests should verify rwx masks, allow-all behavior, fs-name restriction behavior, mixed grant `allowed_fs_names()`, profile expansion through `fs_name_capable()`, network parsing fields, and encoding round trips through the text form.
