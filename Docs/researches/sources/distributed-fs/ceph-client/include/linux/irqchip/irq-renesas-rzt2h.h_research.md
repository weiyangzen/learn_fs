# sources/distributed-fs/ceph-client/include/linux/irqchip/irq-renesas-rzt2h.h

## Purpose
`irq-renesas-rzt2h.h` exposes Renesas RZ/T2H ICU support for registering DMAC request-number routing from client drivers.

## Important APIs, types, and functions
It defines `RZT2H_ICU_DMAC_REQ_NO_DEFAULT` and conditionally declares `rzt2h_icu_register_dma_req`, with a no-op stub when `CONFIG_RENESAS_RZT2H_ICU` is disabled.

## Control flow
DMAC or peripheral setup code passes the ICU platform device, DMAC index/channel, and request number so the ICU implementation can program routing.

## State and persistence
State is in ICU hardware routing registers and driver-private tables; disabled builds keep none.

## Dependencies and integration points
It depends on platform devices and integrates Renesas ICU interrupt/request routing with DMAC channels.

## Risks and test signals
Risks include no-op behavior in disabled builds, invalid channel/index values, and wrong default request number. Tests should cover enabled/disabled configs, each DMAC channel mapping, and reset/default routing.
