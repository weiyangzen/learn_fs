# sources/distributed-fs/openafs/src/afs/UKERNEL/afsincludes.h

## Purpose

`afsincludes.h` is the UKERNEL aggregation header for OpenAFS internal headers. It centralizes cache-manager, RX, volume, directory, stats, ACL, callback, and disconnected-mode declarations needed by UKERNEL source files.

## Important APIs, Types, and Functions

The file exports no functions of its own. It includes headers for `afs/stds.h`, `roken`, `opr`, `rx`, `afs_osi`, locks, volume errors/defs, `afsint`, exporter/NFS integration, VLDB, cache-manager core structures, chunk ops, rxkad, protection rights, directory handling, access cache, ICL tracing, stats, prototypes, and disconnected mode.

## Control Flow

There is no runtime control flow. It determines compile-time visibility and include order for UKERNEL files.

## State and Persistence Behavior

No state is defined. State comes from included subsystems such as vcache, dcache, cell config, RX, and disconnected-mode metadata.

## Dependencies and Integration Points

Almost every UKERNEL `.c` file includes this after `afs/sysincludes.h`. It must remain aligned with the symbols needed by `afs_usrops.c`, OSI shims, and VNOPS code compiled in the user-space kernel configuration.

## Risks and Edge Cases

As a broad include umbrella, it can mask missing direct dependencies and increase rebuild scope. Include-order regressions are likely because several OpenAFS headers define platform macros and type aliases.

## Test Signals

The main signal is successful UKERNEL/libuafs compilation across supported user platforms. Include hygiene tests can compile small files with only `afs/sysincludes.h` plus `afsincludes.h` to catch missing or conflicting definitions.
