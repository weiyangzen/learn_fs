# sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/libwx/wx_lib.h

## Purpose
`wx_lib.h` declares the shared datapath, interrupt, resource, statistics, feature, ring, and service-timer API implemented by `wx_lib.c`. Device-specific WangXun drivers include it to reuse common netdev operations and lifecycle helpers.

## Important APIs, types, and functions
The declarations cover packet type decoding, RX buffer refill, descriptor accounting, transmit entry point, NAPI enable/disable, interrupt scheme reset/init/clear, MSI-X clean handler, IRQ free, ISB resource management, EITR writes, vector configuration, ring cleanup/resource setup/free, stats64 collection, netdev feature set/fix/check, ring resizing, and service event/timer helpers.

## Control flow and behavior
The header has no executable flow. Its exported functions imply the lifecycle used by consumers: initialize interrupt scheme, setup resources, configure hardware vectors, enable NAPI, transmit and poll, collect stats, handle feature changes, schedule service work, then disable NAPI and free resources/interrupts during close or reset.

## State and persistence
The header owns no state. All operations mutate `struct wx`, `struct wx_ring`, `struct wx_q_vector`, SKB/DMA resources, netdev features, or timer/workqueue state in the implementation.

## Dependencies and integration points
It relies on libwx core type definitions and Linux netdevice, IRQ, SKB, and feature types being visible to includers. It is a common boundary between the hardware layer (`wx_hw.c`), PTP layer (`wx_ptp.c`), VF helpers, and device-specific netdev ops.

## Risks and edge cases
Because the API exposes lifecycle-sensitive operations, consumers can misuse it by freeing resources while NAPI is enabled, resizing rings while queues are live, or configuring vectors before interrupt allocation. Kernel prototype changes for `ndo_features_check`, stats64, timer, or IRQ handlers would require matching updates here.

## Test signals
Build tests should catch prototype drift. Runtime validation should confirm each consumer calls setup/free pairs in the right order and that netdev ops wired to these prototypes survive reset, feature toggles, and close/open cycles.
