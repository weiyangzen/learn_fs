# sources/distributed-fs/ceph-client/security/landlock/limits.h

## Purpose

`limits.h` defines Landlock internal limits and masks derived from UAPI access bits.

## Important APIs, Types, and Functions

The file sets `LANDLOCK_MAX_NUM_LAYERS` to 16 and `LANDLOCK_MAX_NUM_RULES` to `U32_MAX`. It derives last, mask, and count constants for filesystem access, network access, scopes, and restrict-self flags: `LANDLOCK_MASK_ACCESS_FS`, `LANDLOCK_NUM_ACCESS_FS`, `LANDLOCK_MASK_ACCESS_NET`, `LANDLOCK_NUM_ACCESS_NET`, `LANDLOCK_MASK_SCOPE`, `LANDLOCK_NUM_SCOPE`, and `LANDLOCK_MASK_RESTRICT_SELF`.

## Control Flow

There is no runtime control flow. Other code uses these constants for validation, static assertions, array sizes, and mask clipping.

## State and Persistence Behavior

No state exists. The constants define ABI-related in-kernel capacity.

## Dependencies and Integration Points

It depends on UAPI Landlock constants. It feeds access masks, ruleset allocation, audit string tables, and syscall validation.

## Risks and Test Signals

When new UAPI bits are added, failing to update `LANDLOCK_LAST_*` constants breaks validation and static assertions. Test new ABI selftests, audit string array sizes, and compile-time checks.
