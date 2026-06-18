<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/text-patching.h -->
# sources/distributed-fs/ceph-client/include/linux/text-patching.h

## Purpose
provides a generic fallback `text_poke_copy()` helper for architectures without specialized live text patching support.

## Important APIs, Types, and Functions
The file is 16 lines and exports these visible symbol families: types/enums none; macros/constants `text_poke_copy`; function-like macros none; inline helpers none; external prototypes `memcpy`.

## Control Flow
Callers copy replacement bytes into an executable text area through `text_poke_copy()`, which defaults to `memcpy()` unless an architecture overrides the macro.

## State and Persistence Behavior
No state is held here; patched instruction state is in executable kernel text and architecture instruction-cache/TLB machinery.

## Dependencies and Integration Points
It depends on string/memory primitives and integrates with jump labels, alternatives, probes, static calls, or other text-patching users where an architecture permits plain copying. Direct includes are `asm/text-patching.h`.

## Risks and Edge Cases
Plain memcpy is not sufficient on architectures requiring synchronization, W^X transitions, cache maintenance, or stop-machine coordination. Callers must rely on architecture overrides where needed.

## Test Signals
Compile architectures with and without overrides, run jump-label/static-call/kprobe alternatives tests, and validate instruction cache coherency after patching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/text-patching.h -->
