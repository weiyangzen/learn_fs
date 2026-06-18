<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/hsr/Makefile -->
# sources/distributed-fs/ceph-client/net/hsr/Makefile

## Purpose
Builds the HSR/PRP networking implementation and optional PRP duplicate-discard KUnit test.

## APIs, Types, and Functions
Defines `obj-$(CONFIG_HSR) += hsr.o`, composes `hsr-y` from main, frame registry, device, netlink, slave, and forwarding objects, adds `hsr_debugfs.o` when `CONFIG_DEBUG_FS` is set, and builds `prp_dup_discard_test.o` under `CONFIG_PRP_DUP_DISCARD_KUNIT_TEST`.

## Control Flow, State, and Persistence
No runtime behavior is present. The file controls which implementation units are linked into the HSR module/object based on configuration.

## Dependencies and Integration
Integrates with kbuild and the Kconfig symbols in this directory. The object list shows that this subset is partial: `hsr_netlink.c`, `hsr_slave.c`, and the PRP test are required integration peers even though they are not part of this work item.

## Risks and Test Signals
Risks include missing objects from `hsr-y`, debugfs helper stubs not matching the optional object, and test object linkage drift. Test signals are successful modular and built-in HSR builds with and without debugfs, and KUnit test discovery when configured.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/hsr/Makefile -->
