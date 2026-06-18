# sources/distributed-fs/ceph-client/net/smc/Kconfig

## Purpose
Defines configuration options for the SMC socket protocol family, SMC diagnostic monitoring, and an eBPF hook for SMC handshake control.

## Important APIs, Types, And Functions
Configuration symbols are `CONFIG_SMC`, `CONFIG_SMC_DIAG`, and `CONFIG_SMC_HS_CTRL_BPF`. `SMC` is tristate and depends on `INET`, `INFINIBAND`, and `DIBS`; diagnostics depend on `SMC`; handshake BPF depends on `SMC`, `BPF_JIT`, and `BPF_SYSCALL` and defaults to enabled.

## Control Flow
Kconfig dependency resolution determines which SMC objects are built by the Makefile. Enabling base SMC permits the socket family implementation; enabling diagnostics adds netlink/socket monitoring; enabling handshake BPF compiles the BPF hook integration.

## State And Persistence
No runtime state directly. Selected symbols persist in kernel build configuration and control compiled feature surface.

## Dependencies And Integration Points
Integrates SMC with the INET stack, InfiniBand/RDMA support, diagnostic tooling such as `smcss`, and kernel BPF infrastructure.

## Risks
The visible typo in the help text ("filtring") is documentation-only. Functional risks include dependency churn making SMC unavailable unexpectedly, default-on BPF hook widening build/test matrix, and mismatch between Kconfig symbols and Makefile object lists.

## Test Signals
Run randconfig/allmodconfig build coverage across dependencies, verify SMC is hidden when prerequisites are absent, ensure `SMC_DIAG` cannot build without `SMC`, and compile with BPF prerequisites toggled.
