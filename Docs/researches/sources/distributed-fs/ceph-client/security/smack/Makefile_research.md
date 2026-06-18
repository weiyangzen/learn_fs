# sources/distributed-fs/ceph-client/security/smack/Makefile

## Purpose
`security/smack/Makefile` defines how the Smack LSM object is built from its component source files.

## Important APIs, Types, and Functions
`obj-$(CONFIG_SECURITY_SMACK) := smack.o` builds Smack only when the main Kconfig symbol is enabled. `smack-y` includes `smack_lsm.o`, `smack_access.o`, and `smackfs.o`; `smack-$(CONFIG_SECURITY_SMACK_NETFILTER)` conditionally adds `smack_netfilter.o`.

## Control Flow
Kbuild aggregates the listed objects into `smack.o`. The netfilter object is linked only for secmark/netfilter mode, matching Kconfig dependencies and feature macros.

## State and Persistence
No runtime state is stored here. The file controls which compiled code is present in the kernel image/module.

## Dependencies and Integration Points
It is directly driven by `security/smack/Kconfig` and integrates with kernel Kbuild. The listed objects divide Smack into LSM hooks, access/label logic, smackfs policy interface, and optional netfilter integration.

## Risks
Adding source files without updating this Makefile causes missing symbols or dead code. Incorrect conditional linkage can break builds for configurations without netfilter support.

## Test Signals
Build Smack enabled/disabled and Smack netfilter enabled/disabled. Linker errors and missing hook behavior are the main regression signals.
