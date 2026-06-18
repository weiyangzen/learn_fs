<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/bug.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/bug.rs

## Purpose
This file provides Rust support for kernel WARN/BUG metadata emission and a public `warn_on!` macro.

## Important APIs, Types, and Functions
Multiple cfg-specific `warn_flags!` macro definitions implement architecture/config-dependent warning emission. `bugflag_taint` shifts taint values into BUG flag position. `warn_on!` evaluates a condition, emits warning metadata when true, and returns the condition result.

## Control Flow and State
For normal `CONFIG_BUG` non-UML/non-LoongArch/non-ARM builds, `warn_flags!` emits inline assembly that includes generated architecture warn and reachable assembly snippets, optionally including verbose file metadata. UML calls `warn_slowpath_fmt`; LoongArch/ARM call `WARN_ON(true)`; builds without `CONFIG_BUG` emit nothing. `warn_on!` builds a file or detailed condition string depending on `CONFIG_DEBUG_BUGVERBOSE_DETAILED`.

## State and Persistence Behavior
The module stores no runtime state. Its effect is compile-time/static metadata emission and runtime warning reporting through architecture or C kernel helpers.

## Dependencies and Integration Points
It depends on generated `OBJTREE` assembly includes, `bindings::BUGFLAG_WARNING`, `TAINT_WARN`, `bug_entry`, `WARN_ON`, and `warn_slowpath_fmt`. It is a low-level macro facility for other Rust kernel code.

## Risks
Architecture cfg coverage must match kernel support. Inline assembly includes must exist and have the expected operands. Because `warn_on!` returns the condition, callers may rely on single evaluation; the macro stores `cond` first to preserve that. Builds without `CONFIG_BUG` suppress warning side effects.

## Test Signals
No local tests. Validation is primarily build coverage across configurations and architecture smoke tests that warning metadata appears or C warning helpers are called.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/bug.rs -->
