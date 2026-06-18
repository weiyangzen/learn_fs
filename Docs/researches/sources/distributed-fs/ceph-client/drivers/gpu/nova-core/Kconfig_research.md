# sources/distributed-fs/ceph-client/drivers/gpu/nova-core/Kconfig

## Purpose

`Kconfig` declares the `NOVA_CORE` kernel configuration option for the Rust Nova Core NVIDIA GPU driver. It controls whether the core GSP-based driver is built and advertises the driver as work in progress.

## Important APIs, Types, And Functions

The single symbol is `config NOVA_CORE`, a tristate named "Nova Core GPU driver". It depends on `64BIT`, `PCI`, and `RUST`, selects `AUXILIARY_BUS` and `RUST_FW_LOADER_ABSTRACTIONS`, defaults to `n`, and documents the module name `nova_core`.

## Control Flow

There is no runtime flow. At configuration time, selecting `NOVA_CORE=y` or `m` allows the Makefile to build `nova_core.o`; dependency and select clauses ensure PCI, Rust, auxiliary device registration, and firmware-loader abstractions are available.

## State And Persistence Behavior

The file stores no runtime state. Its persistent effect is the generated kernel config symbol, which controls compilation and module availability.

## Dependencies And Integration Points

It integrates with the kernel Kconfig system, Rust-for-Linux support, PCI driver infrastructure, auxiliary bus, and firmware loading. The help text scopes support to NVIDIA GPUs based on GSP, Turing and later.

## Risks And Test Signals

Risks include missing dependencies for Rust DMA/PCI/debugfs features elsewhere in the module, selecting firmware abstractions while leaving other required Rust symbols implicit, and users enabling a non-functional work-in-progress driver. Test signals are `allmodconfig`/targeted Rust kernel builds, `modinfo nova_core`, dependency resolution with `CONFIG_RUST=n`, and module load attempts on supported NVIDIA PCI display devices.
