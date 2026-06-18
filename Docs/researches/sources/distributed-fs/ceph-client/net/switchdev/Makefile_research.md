# sources/distributed-fs/ceph-client/net/switchdev/Makefile

## Purpose
This Makefile wires the switchdev core into the networking build.

## Important APIs, Types, And Functions
It contains a single build rule: `obj-y += switchdev.o`.

## Control Flow
Kbuild includes `switchdev.o` in the built-in object list whenever this directory is entered by the parent networking build.

## State And Persistence
There is no runtime state. The persistent effect is the built kernel object composition.

## Dependencies And Integration Points
The Makefile depends on parent Kbuild selection, normally controlled by `NET_SWITCHDEV`. It integrates `switchdev.c` with the rest of the kernel networking tree.

## Risks And Test Signals
The main risk is unconditional directory-level inclusion if parent Kbuild enters this directory unexpectedly. Test signals are build logs showing `switchdev.o` compiled and linked when switchdev support is configured.
