# sources/distributed-fs/ceph-client/drivers/net/netdevsim/Makefile

## Purpose
This Makefile builds the `netdevsim` kernel module and conditionally includes simulator feature objects based on kernel configuration. It defines the base object list for the network device simulator and adds optional capability files for BPF, XFRM, psample, PSP, and MACsec.

## Important APIs, Types, and Functions
The important build variables are `obj-$(CONFIG_NETDEVSIM) += netdevsim.o` and `netdevsim-objs := ...`. The base object list includes `netdev.o`, `dev.o`, `ethtool.o`, `fib.o`, `bus.o`, `health.o`, `hwstats.o`, `udp_tunnels.o`, and `tc.o`. Conditional blocks append `bpf.o` when `CONFIG_BPF_SYSCALL=y`, `ipsec.o` when `CONFIG_XFRM_OFFLOAD` is set, `psample.o` when `CONFIG_PSAMPLE` is set, `psp.o` when `CONFIG_INET_PSP` is set, and `macsec.o` when `CONFIG_MACSEC` is set.

## Control Flow
Kbuild evaluates the Makefile at build time. If `CONFIG_NETDEVSIM` is disabled, no module is built. If it is enabled as built-in or module, Kbuild links `netdevsim.o` from the base object list plus any optional feature objects whose configs are enabled.

## State and Persistence
There is no runtime state. The file persists only build composition, determining which C files contribute symbols to the final module.

## Dependencies and Integration Points
This file integrates with kernel Kbuild and the configuration system. Its conditional object inclusion must match preprocessor declarations and function calls in `netdevsim.h` and the base files. For example, BPF entry points in `bpf.c` are only linked when `CONFIG_BPF_SYSCALL=y`, and XFRM/psample/PSP/MACsec support is linked only when the relevant subsystems are configured.

## Risks and Edge Cases
Incorrect conditionals can produce unresolved symbols or silently omit test features. The `ifneq ($(CONFIG_*),)` form includes objects for both built-in and module-valued options, while the BPF block specifically requires `y`; that distinction matters when dependencies cannot be modular or when a feature is unavailable for module builds. The base object list must include files needed for module init/exit and common simulator lifecycle.

## Test Signals
Build tests should exercise `CONFIG_NETDEVSIM=y`, `CONFIG_NETDEVSIM=m`, and feature combinations with BPF, XFRM offload, psample, PSP, and MACsec enabled or disabled. The expected signal is a linked `netdevsim` module with no unresolved references and feature-specific debugfs/devlink behavior only when corresponding objects are present.
