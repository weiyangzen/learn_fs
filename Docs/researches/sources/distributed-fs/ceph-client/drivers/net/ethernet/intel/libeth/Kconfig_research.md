# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/libeth/Kconfig

## Purpose
`libeth/Kconfig` defines configuration symbols for the common Ethernet library and its XDP/XSk companion module.

## Important APIs, Types, and Symbols
`CONFIG_LIBETH` is a tristate common library, visible under `COMPILE_TEST`, and selects `PAGE_POOL`. `CONFIG_LIBETH_XDP` is a tristate XDP/XSk helper library, also visible under `COMPILE_TEST`, and selects `LIBETH`.

## Control Flow
There is no runtime flow. Kconfig selection determines which objects in the Makefile build and which namespaces/exported helpers are available to drivers.

## State and Persistence Behavior
No runtime state. Build configuration persists as kernel config and module availability.

## Dependencies and Integration Points
`LIBETH` underpins Intel Ethernet drivers that share hotpath helpers. `LIBETH_XDP` depends on `LIBETH` so XDP helpers can patch static calls into the base Tx completion path.

## Risks and Edge Cases
Because symbols are only prompt-visible for `COMPILE_TEST`, production drivers likely select them indirectly. Missing selects in a consumer driver would surface as unresolved symbols or missing helper availability.

## Test Signals
Kconfig dependency checks, allyesconfig/allmodconfig builds, and builds with `LIBETH_XDP=m` while `LIBETH=m/y`.
