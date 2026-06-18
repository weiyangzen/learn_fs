<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sync_core.h -->
# sources/distributed-fs/ceph-client/include/linux/sync_core.h

## Purpose

`sync_core.h` declares `sync_core_before_usermode()`, an architecture-sensitive helper used to ensure core instruction synchronization before returning to user mode after code or execution-context changes.

## Important APIs, types, and functions

The single exported API is `sync_core_before_usermode()`. Implementations are architecture-specific or generic depending on the kernel tree.

## Control flow

Kernel code calls the helper before user return when it needs guarantees that subsequent user execution observes updated instruction stream or CPU context state. The actual synchronization sequence is supplied elsewhere.

## State and persistence behavior

The header owns no state. The effect is transient CPU pipeline/core synchronization; it does not persist except by ordering execution.

## Dependencies and integration points

It integrates with architecture entry/exit paths, text patching or instruction-modifying mechanisms, signal/return-to-user flows, and CPU synchronization barriers.

## Risks and test signals

Risks include missing calls after modifying executable user-visible state, overuse on hot paths, and architecture implementations that do not provide sufficient serialization. Tests should cover architecture build coverage, self-modifying/JIT code scenarios where applicable, signal/return paths, and tracing or static analysis that confirms required callers invoke the helper before usermode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sync_core.h -->
