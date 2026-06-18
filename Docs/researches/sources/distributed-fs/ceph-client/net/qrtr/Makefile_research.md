# sources/distributed-fs/ceph-client/net/qrtr/Makefile

## Purpose
The Makefile maps QRTR Kconfig symbols to kernel objects. It defines the composition of the core `qrtr` module and optional transport modules.

## Important APIs, Types, And Functions
`obj-$(CONFIG_QRTR) += qrtr.o` builds the core from `af_qrtr.o` and `ns.o`. `CONFIG_QRTR_SMD`, `CONFIG_QRTR_TUN`, and `CONFIG_QRTR_MHI` build `qrtr-smd.o`, `qrtr-tun.o`, and `qrtr-mhi.o` from `smd.o`, `tun.o`, and `mhi.o`.

## Control Flow
There is no runtime flow. The important build flow is that nameservice `ns.o` is linked into the core QRTR object, while each physical/userspace transport is a separate module/object.

## State And Persistence
The file affects build artifacts only. Runtime state is owned by the compiled source files.

## Dependencies And Integration Points
The object layout means transport modules depend on exported symbols from the core, primarily `qrtr_endpoint_register()`, `qrtr_endpoint_unregister()`, and `qrtr_endpoint_post()`.

## Risks
Because `ns.o` is part of the core object, QRTR core initialization includes nameservice setup and failure paths. Transport modules must handle core module unload and endpoint unregister ordering.

## Test Signals
Build tests should verify object composition for built-in and modular QRTR, and symbol resolution when SMD/TUN/MHI are built as modules against a modular or built-in core.
