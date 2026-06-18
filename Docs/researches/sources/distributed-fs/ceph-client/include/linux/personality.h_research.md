<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/personality.h -->
# sources/distributed-fs/ceph-client/include/linux/personality.h

## Purpose
Provides kernel-side wrappers around UAPI process personality constants and simple helpers for reading and setting the current task personality.

## Important APIs, Types, And Functions
- Includes `<uapi/linux/personality.h>` for personality flags and masks.
- `personality(pers)` masks a personality value with `PER_MASK`.
- `get_personality` aliases `current->personality`.
- `set_personality(pers)` writes `current->personality`.

## Control Flow
Callers read the current task personality through `get_personality`, mask personality domains with `personality()`, or set the current task value with `set_personality()`. There are no functions or validation paths in this header.

## State And Persistence
State is the `personality` field in `current`/`task_struct`, which persists for the task and influences execution-domain behavior, ABI quirks, address layout, and related process semantics.

## Dependencies And Integration Points
Depends on UAPI personality definitions and the implicit `current` task pointer. It integrates with exec, binfmt loaders, compatibility modes, address-space randomization policy, and process-control syscalls.

## Risks And Edge Cases
Risks include setting personality flags without preserving required bits, failing to mask with `PER_MASK` when comparing domains, and changing `current->personality` in contexts where another task was intended.

## Test Signals
Exercise `personality(2)`, exec of compatibility binaries, ASLR/personality flag interactions, domain masking, and build coverage where `current` is available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/personality.h -->
