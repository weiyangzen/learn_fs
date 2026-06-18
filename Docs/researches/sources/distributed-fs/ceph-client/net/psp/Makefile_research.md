# sources/distributed-fs/ceph-client/net/psp/Makefile

## Purpose
The Makefile maps `CONFIG_INET_PSP` to the PSP object aggregate.

## Important APIs, types, and functions
`obj-$(CONFIG_INET_PSP) += psp.o` enables PSP, and `psp-y := psp_main.o psp_nl.o psp_sock.o psp-nl-gen.o` links the core, netlink implementation, socket association implementation, and generated netlink tables.

## Control flow and state
There is no runtime flow. Object membership determines the built-in PSP subsystem composition; PSP is a bool option, not a module in this Makefile.

## Dependencies and integration points
The Makefile must stay aligned with `Kconfig`, `psp_main.c` initialization, generated netlink code, and non-listed implementation files (`psp_nl.c`, `psp_sock.c`) that provide declarations referenced by headers and generated ops.

## Risks and edge cases
Incorrect object ordering or missing objects would produce unresolved symbols for generated netlink callbacks, socket association helpers, or device registration APIs.

## Test signals
Build `CONFIG_INET_PSP=y`, confirm `psp_main.o`, `psp_nl.o`, `psp_sock.o`, and `psp-nl-gen.o` are linked, and check that disabling the option removes PSP symbols.
