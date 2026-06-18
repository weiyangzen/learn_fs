# sources/distributed-fs/ceph-client/fs/xfs/xfs_globals.c

## Purpose
`xfs_globals.c` defines global tunable defaults and miscellaneous global XFS behavior switches.

## Important APIs, types, and functions
It defines `xfs_params`, whose fields provide min/default/max values for panic mask, error level, sync daemon timer, stats clearing, inherited inode flags, rotor step, filestream timer, and blockgc timer. It also defines `xfs_globals`, with defaults for log recovery delay, mount delay, assert behavior, debug-only parallel work and logged-attribute replay switches, and btree bulk-load slack.

## Control flow
There are no functions. Sysctl and mount/runtime code read these global structures to clamp tunables and initialize behavior.

## State and persistence
The values are runtime globals. They do not persist on disk, though they influence persistent operations such as inherited inode flags, log recovery timing, and repair/btree build behavior.

## Dependencies and integration points
It includes XFS platform and error definitions and is consumed by sysctl setup, mount code, blockgc, filestream, error reporting, assertions, and debug paths.

## Risks and test signals
Risks include invalid min/default/max ranges, changing defaults in ways that affect performance or error handling, and debug-only fields diverging from users. Test signals include sysctl registration, mount under DEBUG and non-DEBUG builds, assert-fatal builds, and tunable boundary tests.
