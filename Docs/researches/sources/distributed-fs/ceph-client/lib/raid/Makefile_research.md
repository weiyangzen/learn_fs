# sources/distributed-fs/ceph-client/lib/raid/Makefile

## Purpose
Routes RAID library builds into the XOR subdirectory.

## APIs, Control Flow, and State
The build rule `obj-y += xor/` always descends into `lib/raid/xor`. There is no runtime logic or persistent state.

## Dependencies, Integration, Risks, and Tests
Depends on Kbuild traversal and the XOR directory's own config-conditional object rules. Risks are minimal: incorrect directory traversal would omit all XOR objects and tests. Test signals are Kbuild coverage with `CONFIG_XOR_BLOCKS`, `CONFIG_XOR_KUNIT_TEST`, and architecture optimized XOR configs.
