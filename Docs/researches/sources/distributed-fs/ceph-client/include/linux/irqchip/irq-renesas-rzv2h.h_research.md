# sources/distributed-fs/ceph-client/include/linux/irqchip/irq-renesas-rzv2h.h

## Purpose
`irq-renesas-rzv2h.h` exposes Renesas RZ/V2H(P) ICU support for registering DMAC request-number routing.

## Important APIs, types, and functions
It defines `RZV2H_ICU_DMAC_REQ_NO_DEFAULT` and conditionally declares `rzv2h_icu_register_dma_req`, with a no-op stub when `CONFIG_RENESAS_RZV2H_ICU` is disabled.

## Control flow
Client code tells the ICU driver which DMAC index/channel should receive a given request number. The ICU implementation owns hardware programming.

## State and persistence
State is runtime hardware/request routing; no header-owned state exists.

## Dependencies and integration points
It depends on platform devices and integrates Renesas ICU and DMA request routing for RZ/V2H(P) SoCs.

## Risks and test signals
Risks include disabled-config silent no-op, platform-device mismatch, and incorrect request/channel encoding. Tests should cover valid and default request values, all channels, disabled build coverage, and DMA functionality after ICU setup.
