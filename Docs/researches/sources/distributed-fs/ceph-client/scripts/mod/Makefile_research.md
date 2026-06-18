<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/mod/Makefile -->
# sources/distributed-fs/ceph-client/scripts/mod/Makefile

## Purpose

`scripts/mod/Makefile` defines host-side build products for module postprocessing: `modpost`, `mk_elfconfig`, `empty.o`, generated `elfconfig.h`, and generated `devicetable-offsets.h`.

## Important APIs, Types, and Functions

Key variables are `hostprogs-always-y`, `always-y`, `modpost-objs`, `devicetable-offsets-file`, and `targets`. Explicit dependencies force `modpost.o`, `file2alias.o`, `sumversion.o`, and `symsearch.o` to include generated ELF configuration, while `file2alias.o` also depends on device-table offsets.

## Control Flow

Kbuild first builds `empty.o` without LTO flags, runs `mk_elfconfig` over it to produce target ELF-class/endian configuration, assembles `devicetable-offsets.s`, filters it through `filechk offsets` to produce the offsets header, and then builds host `modpost` from its object list.

## State and Persistence Behavior

Persistent generated files are under the build object directory: `elfconfig.h`, `devicetable-offsets.h`, `devicetable-offsets.s`, `empty.o`, `mk_elfconfig`, and `modpost`.

## Dependencies and Integration Points

It depends on Kbuild host-program rules, `filechk`, generated-offset conventions, and the target compiler output for `empty.o`. It integrates directly with module builds and `vmlinux` export generation.

## Risks and Edge Cases

Stale generated headers can cause host tools to parse target ELF or device tables incorrectly. LTO must be removed from `empty.o` so ELF probing remains stable. Adding new device-table structures requires synchronized changes in `devicetable-offsets.c` and `file2alias.c`.

## Test Signals

Build host tools for 32-bit and 64-bit targets, big and little endian, with and without LTO. Verify regenerated headers change when target ABI or mod device-table layouts change.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/mod/Makefile -->
