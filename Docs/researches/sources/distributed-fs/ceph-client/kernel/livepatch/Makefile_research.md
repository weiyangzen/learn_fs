# sources/distributed-fs/ceph-client/kernel/livepatch/Makefile

## Purpose
The Makefile wires livepatch source files into the kernel build when `CONFIG_LIVEPATCH` is enabled.

## Important APIs, Types, And Functions
It sets `obj-$(CONFIG_LIVEPATCH) += livepatch.o` and defines `livepatch-objs := core.o patch.o shadow.o state.o transition.o`.

## Control Flow
During kbuild, enabling `CONFIG_LIVEPATCH` builds a composite `livepatch.o` from the listed objects; disabling the config omits the directory's livepatch implementation.

## State And Persistence
There is no runtime state. The persistent effect is the build artifact composition for livepatch support.

## Dependencies And Integration Points
This file is driven by the sibling Kconfig and kbuild's composite object rules. The component objects represent livepatch core registration, patch application, shadow variables, state, and transitions.

## Risks And Edge Cases
Missing an object here would compile out part of livepatch behavior despite Kconfig enablement. Adding objects requires keeping this list synchronized with source files and dependency expectations.

## Test Signals
Signals include `CONFIG_LIVEPATCH=y` builds producing `livepatch.o` from all five objects and disabled builds omitting the object.
