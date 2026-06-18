# sources/distributed-fs/ceph-client/scripts/gendwarfksyms/Makefile

## Purpose
The `gendwarfksyms/Makefile` builds the host-side `gendwarfksyms` utility used for DWARF-derived symbol version generation.

## Important APIs, Types, and Functions
It defines `hostprogs-always-y += gendwarfksyms` and lists component objects: `gendwarfksyms.o`, `cache.o`, `die.o`, `dwarf.o`, `kabi.o`, `symbols.o`, and `types.o`.

## Control Flow
Kbuild host tooling compiles the listed C files and links them into the host program whenever this script directory is built.

## State and Persistence Behavior
Build outputs are host binaries/objects managed by Kbuild. The Makefile itself has no runtime state.

## Dependencies and Integration Points
The component sources depend on elfutils/libdw/libdwfl, libelf, zlib, and kernel host helper headers such as `hash.h` and `hashtable.h`.

## Risks and Test Signals
Missing host libraries or Kbuild host flags will fail the build. Test by invoking the scripts host build and running the resulting binary on example objects.
