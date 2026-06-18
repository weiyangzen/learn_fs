# sources/distributed-fs/ceph-client/drivers/net/ethernet/fungible/funeth/Makefile

## Purpose
Builds the Fungible Ethernet driver module and sets include paths for the shared funcore headers and local funeth headers.

## Important APIs, Types, And Functions
`ccflags-y` adds `../funcore` and the current directory. `funeth-y` links `funeth_main.o`, `funeth_rx.o`, `funeth_tx.o`, `funeth_devlink.o`, and `funeth_ethtool.o`; `funeth-$(CONFIG_TLS_DEVICE)` conditionally adds `funeth_ktls.o`.

## Control Flow
kbuild compiles these objects into `funeth.o` when `CONFIG_FUN_ETH` is enabled. TLS offload code is included only when kernel TLS device support is configured.

## State And Persistence
Build metadata only.

## Dependencies And Integration Points
Integrates funeth with funcore headers, local Tx/Rx/ethtool/devlink modules, and optional kTLS support.

## Risks
Any source file added to the driver must be included here or it will be omitted. Include paths make local and funcore headers easy to include but can hide accidental header name collisions.

## Test Signals
Module builds with and without `CONFIG_TLS_DEVICE`, link success against funcore exports, and expected object membership in `funeth.o`.
