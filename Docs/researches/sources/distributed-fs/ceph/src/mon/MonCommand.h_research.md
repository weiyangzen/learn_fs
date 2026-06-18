# sources/distributed-fs/ceph/src/mon/MonCommand.h

## Purpose

`MonCommand.h` defines the serializable monitor command descriptor used for command help, compatibility checks, manager-provided command registration, forwarding behavior, and permissions. It is a small but persistent wire/store contract for command metadata.

## Important APIs, Types, and Functions

`MonCommand` contains `cmdstring`, `helpstring`, `module`, `req_perms`, and `flags`. Flags include `FLAG_NOFORWARD`, `FLAG_OBSOLETE`, `FLAG_DEPRECATED`, `FLAG_MGR`, `FLAG_POLL`, `FLAG_HIDDEN`, and combined `FLAG_TELL`. Methods include flag helpers, `encode()/decode()`, `dump()`, `generate_test_instances()`, `encode_bare()/decode_bare()`, compatibility comparison, semantic predicates (`is_tell`, `is_noforward`, `is_obsolete`, `is_deprecated`, `is_mgr`, `is_hidden`), array/vector encoders with uint16 counts, and `requires_perm()`.

## Control Flow and State

The normal encoder wraps the bare command fields plus flags. Bare encoding includes a removed `availability` string for backward compatibility. Array/vector encoders write all bare records first and then all flags for struct version 2; older decoders default flags to zero. `requires_perm()` tests whether a command requires a permission character from `req_perms`.

## Dependencies and Integration Points

Dependencies are minimal: strings, formatter, and Ceph encoding. `MgrMonitor` stores manager command descriptions using this type and marks active mgr commands with `FLAG_MGR`. Monitor command routing and help generation use the flags to hide commands, block forwarding, mark deprecation, and distinguish tell/asok command behavior.

## Risks and Test Signals

Risks are count truncation above `uint16_t`, losing the backward-compatible availability field, flag loss when decoding older structures, and compatibility comparisons ignoring help text and flags intentionally. Tests should cover single and vector encode/decode, old struct decode default flags, `FLAG_TELL` predicate behavior, permission checks, and command compatibility matching.
