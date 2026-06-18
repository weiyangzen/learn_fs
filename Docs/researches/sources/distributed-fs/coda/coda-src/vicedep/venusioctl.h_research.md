# sources/distributed-fs/coda/coda-src/vicedep/venusioctl.h

## Purpose

`sources/distributed-fs/coda/coda-src/vicedep/venusioctl.h` defines Venus-specific ioctl and pioctl command numbers used by Coda user tools, Venus cache manager code, and kernel interfaces.

## Important APIs, Types, and Functions

The file defines `CFS_PIOBUFSIZE`, file-descriptor ioctls such as `_VIOCCLOSEWAIT`, `_VIOCABORT`, and `_VIOCIGETCELL`, legacy and current pioctl command constants for ACLs, tokens, volume status, flushing, prefetch, group access, repair, hoard database, reintegration, mount points, write-disconnect, ASR, local/global repair, cache listing, kernel unload, and zone limits. It also defines consolidated repair command subcodes `REP_CMD_*`.

## Control Flow

There is no runtime code. Callers wrap the numeric `_VIOC*` constants with the platform pioctl/ioctl encoding macros and pass optional data buffers no larger than `CFS_PIOBUFSIZE`.

## State and Persistence Behavior

No state is owned. The constants select operations that may mutate Venus cache state, tokens, volume status, repair sessions, hoard database entries, mutation logs, or kernel/cache-manager behavior in the receiving subsystem.

## Dependencies and Integration Points

It includes `pioctl.h` and is shared by Venus, command-line tools, and kernel/user ABI code. The command numbers are ABI-facing and must stay synchronized with implementations in Venus and tools such as `cfs` and repair utilities.

## Risks and Edge Cases

The header documents ioctl-number wrap/collision risk because the `nr` component is 8-bit. Legacy repair commands are kept for compatibility while `_VIOC_REP_CMD` consolidates repair operations. Reusing or renumbering constants can break old tools or collide with low numbers.

## Test Signals

Build Venus and user tools together; run pioctl smoke tests for ACL/token/status/flush/repair commands; verify command numbers remain under the 8-bit limit; test backward compatibility for old repair commands and the consolidated `REP_CMD` interface.
