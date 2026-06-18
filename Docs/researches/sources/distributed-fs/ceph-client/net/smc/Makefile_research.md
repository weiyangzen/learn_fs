# sources/distributed-fs/ceph-client/net/smc/Makefile

## Purpose
Defines Kbuild object composition for the SMC protocol implementation, optional diagnostics, sysctl support, and optional handshake BPF integration.

## Important APIs, Types, And Functions
Build targets include `obj-$(CONFIG_SMC) += smc.o`, `obj-$(CONFIG_SMC_DIAG) += smc_diag.o`, and composite `smc-y` object lists covering AF_SMC, pnet, RDMA/ISM, CLC, core, work requests, LLC, CDC, TX/RX, close, netlink, stats, tracepoints, and inet integration. Conditional additions are `smc-$(CONFIG_SYSCTL) += smc_sysctl.o` and `smc-$(CONFIG_SMC_HS_CTRL_BPF) += smc_hs_bpf.o`.

## Control Flow
Kbuild links all `smc-y` members into the `smc.o` composite when `CONFIG_SMC` is enabled. Diagnostic support builds separately as `smc_diag.o`. Include path `ccflags-y += -I$(src)` lets local generated or sibling headers be included consistently.

## State And Persistence
No runtime state. It defines build-time module/built-in composition.

## Dependencies And Integration Points
Tied directly to symbols from `Kconfig` and to source files implementing the SMC stack. Parent networking Makefiles consume this directory's objects.

## Risks
Risks are missing an object when new SMC subsystems are added, stale conditional symbols, incorrect include assumptions, and link failures if `Kconfig` permits combinations not reflected here.

## Test Signals
Build `CONFIG_SMC=y/m`, `CONFIG_SMC_DIAG=y/m`, with and without `CONFIG_SYSCTL`, and with BPF handshake support enabled/disabled; inspect resulting module symbols and run modpost for unresolved references.
