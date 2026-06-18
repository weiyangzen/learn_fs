# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/libeth/Makefile

## Purpose
The `libeth` Makefile maps Kconfig symbols to kernel modules and object files.

## Important APIs, Types, and Symbols
`libeth.o` is built from `rx.o` and `tx.o` when `CONFIG_LIBETH` is enabled. `libeth_xdp.o` is built from `xdp.o` and `xsk.o` when `CONFIG_LIBETH_XDP` is enabled.

## Control Flow
No runtime flow. Build flow separates base Rx/Tx helpers from optional XDP/XSk infrastructure.

## State and Persistence Behavior
No runtime state; it controls module composition and exported symbol grouping.

## Dependencies and Integration Points
The separation matches code-level static-call attachment: base `tx.o` can exist without XDP code, while `xdp.o` module init attaches XDP completion operations.

## Risks and Edge Cases
Object split must stay synchronized with symbol namespaces. Moving helpers between base and XDP modules without updating exports/imports can break modular builds.

## Test Signals
Build `LIBETH=y/m`, `LIBETH_XDP=y/m`, and consumer drivers using only base helpers versus XDP helpers.
