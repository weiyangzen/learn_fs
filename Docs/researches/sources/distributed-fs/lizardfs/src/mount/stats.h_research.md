## sources/distributed-fs/lizardfs/src/mount/stats.h

Purpose: declares the stats tree node layout and public counter-tree API.

Important APIs/types: `statsnode` stores counter, active/absolute flags, short and full names, name lengths, and child/sibling pointers. Functions create subnodes, fetch counter pointers, reset, show, lock/unlock, and terminate.

Integration: subsystems cache returned `uint64_t *` counter pointers and mutate them under `stats_lock`.

Risks and tests: raw pointers and global lock make lifetime/order important. Tests should ensure no subsystem uses counter pointers after `stats_term`.
