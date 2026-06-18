# sources/distributed-fs/ceph-client/net/nsh/Makefile

## Purpose

This Makefile wires the NSH protocol implementation into the kernel build.

## Important APIs, Types, and Functions

The only build rule is `obj-$(CONFIG_NET_NSH) += nsh.o`, which compiles and links `nsh.c` when `NET_NSH` is built-in or modular.

## Control Flow

Kbuild evaluates `CONFIG_NET_NSH` and includes `nsh.o` in the corresponding built-in or module object list. Runtime init is handled by `nsh.c`.

## State and Persistence

The file has no runtime state. It reflects build configuration state only.

## Dependencies and Integration Points

It depends directly on the Kconfig symbol defined in the same directory and indirectly supports Open vSwitch's NSH actions by building exported helper functions.

## Risks and Edge Cases

There are no conditional sub-objects or flags, so all NSH behavior is bundled into one object. Build failures in `nsh.c` affect the entire `NET_NSH` option.

## Test Signals

Build matrix signals are sufficient: `CONFIG_NET_NSH=n` omits `nsh.o`; `m` produces a module object; `y` links the code built-in.
