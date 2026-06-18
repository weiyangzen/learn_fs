# sources/distributed-fs/ceph-client/drivers/char/Makefile

## Purpose
This Makefile maps character-device Kconfig symbols to build objects and always descends into the AGP subdirectory.

## Important APIs, Types, and Functions
Key build entries include core `mem.o`, `random.o`, `misc.o`, optional TTY/parallel/HPET/NVRAM/hw_random/TPM/xillybus objects, `obj-y += agp/`, and `obj-$(CONFIG_ADI) += adi.o`.

## Control Flow
Kbuild includes always-on char core objects, then conditionally builds driver objects based on config symbols. The AGP subdirectory is always visited, but its own Makefile gates actual AGP objects.

## State and Persistence Behavior
No runtime state. It controls object inclusion in the kernel or modules.

## Dependencies and Integration Points
It connects `drivers/char/Kconfig` symbols to source files and subdirectories such as `agp/`, `hw_random/`, `tpm/`, and `xillybus/`.

## Risks
Because `agp/` is always descended into, AGP Makefile gating must remain correct. Symbol/object drift causes missing drivers or unexpected build attempts on unsupported architectures.

## Test Signals
Build matrix with common char options as built-in/module/off, especially `CONFIG_ADI=m/y` and `CONFIG_AGP` disabled/enabled.
