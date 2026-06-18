# sources/distributed-fs/ceph-client/net/smc/smc_netns.h

## Purpose
`smc_netns.h` defines SMC per-network-namespace private data. It lets the SMC subsystem keep namespace-local PNET configuration and network-device PNET ID tracking.

## Important APIs, Types, and Functions
The header declares external `smc_net_id` and defines `struct smc_net` with `struct smc_pnettable pnettable` and `struct smc_pnetids_ndev pnetids_ndev`.

## Control Flow
The header has no executable flow. Net namespace initialization code elsewhere allocates or looks up `struct smc_net` by `smc_net_id`, then PNET and device-notifier code uses the embedded tables for namespace-local SMC path selection.

## State and Persistence
State is per-netns and in-memory. It persists for the lifetime of the network namespace and is destroyed with that namespace. It does not write durable data.

## Dependencies and Integration Points
It includes `smc_pnet.h` and is consumed by SMC namespace, PNET, and device handling code. The state influences SMC-R and SMC-D device selection through PNET IDs.

## Risks
Namespace isolation depends on all PNET lookups using the correct `struct net` and `smc_net_id`. Cross-namespace leakage would cause wrong device selection or expose configuration. Cleanup ordering must ensure device notifier state is gone before namespace memory is freed.

## Test Signals
Create multiple network namespaces with different PNET tables and devices, verify SMC path selection remains isolated, and tear namespaces down under SMC traffic while checking for use-after-free reports.
