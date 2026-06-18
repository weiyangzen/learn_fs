# sources/distributed-fs/ceph-client/drivers/misc/uacce/Makefile

## Purpose
`uacce/Makefile` wires the UACCE framework object into the kernel build when `CONFIG_UACCE` is enabled.

## Important APIs, Types, and Functions
The file contains one build rule: `obj-$(CONFIG_UACCE) += uacce.o`.

## Control Flow
There is no runtime flow. Kbuild includes `uacce.o` as built-in or module according to the tristate value of `CONFIG_UACCE`.

## State and Persistence
No runtime state is defined.

## Dependencies and Integration Points
The Makefile is paired with `uacce/Kconfig` and the implementation in `uacce.c`. It integrates with standard Linux Kbuild object selection.

## Risks and Edge Cases
The file has no subobject composition; any future split of the framework would require adding composite object rules.

## Test Signals
Verify `CONFIG_UACCE=y` links `uacce.o` into vmlinux, `CONFIG_UACCE=m` produces the module, and disabled builds omit the object.
