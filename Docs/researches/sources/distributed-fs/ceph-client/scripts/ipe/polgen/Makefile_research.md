# sources/distributed-fs/ceph-client/scripts/ipe/polgen/Makefile

## Purpose
Defines the IPE boot policy generator as an always-built host program.

## APIs, Control Flow, and State
The Makefile sets `hostprogs-always-y := polgen` and adds host extra include paths for kernel and UAPI headers. It has no runtime state.

## Dependencies and Integration
It depends on kbuild host program rules and includes from `$(srctree)/include` and `$(srctree)/include/uapi`, matching the generated C output from `polgen.c`.

## Risks and Test Signals
Risks are limited to missing include paths or the host tool not being built when IPE build rules need it. Test signals are successful host build and generated boot policy C compiling against included headers.
