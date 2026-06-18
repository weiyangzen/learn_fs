# sources/distributed-fs/ceph-client/net/dsa/Makefile

## Purpose
This Makefile builds the DSA core composite object, the always-present stubs object when DSA is enabled, and per-protocol tag driver modules.

## Important APIs, Types, And Functions
When `CONFIG_NET_DSA` is set, `stubs.o` is built into `obj-y` so built-in networking code can access the `dsa_stubs` pointer even if DSA is a module. `dsa_core-y` contains `conduit.o`, `devlink.o`, `dsa.o`, `netlink.o`, `port.o`, `switch.o`, `tag.o`, `tag_8021q.o`, `trace.o`, and `user.o`. Each `NET_DSA_TAG_*` symbol maps to a tag driver object. `CFLAGS_trace.o := -I$(src)` helps the trace framework locate `trace.h`.

## Control Flow
Kbuild links the listed core objects into `dsa_core.o` and separately builds tag drivers according to selected symbols. Stubs are built whenever DSA is configured so callers can test and invoke module-provided functionality indirectly.

## State And Persistence
No runtime state exists here.

## Dependencies And Integration Points
This is the build bridge between Kconfig symbols and runtime modules. It also ensures trace compilation has the expected include path.

## Risks And Edge Cases
New core files or tag drivers require Makefile updates. The stubs rule is important for built-in/module split safety; removing it would break built-in network stack calls to optional DSA functionality.

## Test Signals
Build tests should cover built-in DSA, modular DSA, and individual tag driver modules, plus tracing-enabled builds.
