# sources/distributed-fs/ceph-client/lib/debug_info.c

## Purpose
Forces debug information for selected core kernel data structures into the final image when reduced debug information is configured.

## APIs, Types, and Functions
The file intentionally defines no functions or variables. Its API surface is the collection of included headers: credentials, crypto, dcache, device, filesystem, fscache, I/O, kallsyms, kobject, memory-management, module, networking, scheduler, slab, stdarg, core types, IPv6 address configuration, sockets, and TCP.

## Control Flow
There is no runtime control flow. The compiler sees the type declarations from the included headers, allowing debug-info generation to retain their type metadata.

## State and Persistence
No runtime state is created. The lasting effect is build artifact metadata in the kernel image's debug information sections.

## Dependencies and Integration Points
Depends on the headers it includes and on build configurations such as `CONFIG_DEBUG_INFO_REDUCED`. It integrates with debuggers, crash dump analysis, BPF tooling, and postmortem inspection workflows that need type definitions for common kernel structures.

## Risks and Test Signals
Risks are build bloat, accidental addition of executable code contrary to the file's comment, and stale include choices that omit important reduced-debug types. Test signals include debug-info size checks, `pahole`/BTF or debugger visibility for included structures, and build tests under reduced and full debug-info configurations.
