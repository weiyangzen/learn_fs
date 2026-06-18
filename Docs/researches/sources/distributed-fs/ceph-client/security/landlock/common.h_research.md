# sources/distributed-fs/ceph-client/security/landlock/common.h

## Purpose

`common.h` centralizes the Landlock LSM name, printk prefix, and a helper for converting single-bit values to bit indices.

## Important APIs, Types, and Functions

`LANDLOCK_NAME` is `"landlock"`. `pr_fmt` is reset to prefix Landlock log messages. `BIT_INDEX(bit)` uses `HWEIGHT(bit - 1)` to convert a power-of-two UAPI access bit to a zero-based table index.

## Control Flow

The header affects compile-time string formatting and table indexing. There is no runtime control flow.

## State and Persistence Behavior

No runtime state is stored.

## Dependencies and Integration Points

It is included by most Landlock source files and must stay consistent with `setup.c`'s `lsm_id`.

## Risks and Test Signals

`BIT_INDEX()` assumes a single-bit mask. Misuse with multi-bit masks would index string tables incorrectly. Compile warnings and audit string tests are useful signals.
