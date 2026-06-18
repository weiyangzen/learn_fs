# sources/cloud-native/moby/daemon/internal/usergroup/add_linux.go

## Purpose
Creates a Linux system user/group for user namespace remapping and ensures subordinate UID/GID ranges exist.

## Important APIs, Types, And Functions
`AddNamespaceRangesUser` calls `addUser`, runs `id`, parses uid/gid with `idOutRegexp`, then calls `createSubordinateRanges`. `addUser` selects `adduser` or `useradd` once using `resolveBinary`. `createSubordinateRanges` checks `/etc/subuid` and `/etc/subgid`, finds non-overlapping defaults with `findNextUIDRange`/`findNextGIDRange`, and applies ranges with `usermod -v` and `-w`. `wouldOverlap` detects range conflicts.

## Control Flow
The flow shells out to distro tools, parses results, then fills subordinate ranges only when absent. Existing ranges are preserved.

## State And Persistence
Mutates system accounts and `/etc/subuid`/`/etc/subgid` via system utilities. This is privileged host state.

## Dependencies And Integration Points
Used by daemon user namespace remap setup. Depends on `adduser` or `useradd`, `id`, `usermod`, and `github.com/moby/sys/user` parsers.

## Risks And Test Signals
Command availability and distro output format are external risks. `once` caches the selected user command for process lifetime. Root-only tests create and delete a temp user, load identity mapping, and verify mapped-user filesystem access.
