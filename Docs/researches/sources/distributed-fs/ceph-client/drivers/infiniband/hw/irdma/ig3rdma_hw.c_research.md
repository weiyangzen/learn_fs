# sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/ig3rdma_hw.c

## Purpose
`ig3rdma_hw.c` provides Gen3 hardware capability defaults, statistics layout, interrupt enable/disable operations, and register-offset-to-MMIO-region resolution for IDPF-backed devices.

## Important APIs, types, and functions
The exported APIs are `ig3rdma_init_hw` and `ig3rdma_get_reg_addr`. Local helpers `ig3rdma_ena_irq`, `ig3rdma_disable_irq`, and `__ig3rdma_get_reg_addr` implement interrupt register selection and MMIO lookup.

## Control flow, state, and persistence
`ig3rdma_init_hw` installs Gen3 IRQ ops and stats map, sets WQE/SGE limits, enables 64-byte CQE, CQE timestamping, SRQ, RTS AE, and CQ resize features, configures page-size and push-page limits, and records Gen3 stat index bounds. Register lookup first checks the RDMA MMIO window, then extra IO regions exposed by the core device.

## Dependencies and integration points
It depends on Gen3 constants in `ig3rdma_hw.h`, common `irdma_hw` region fields configured by `ig3rdma_if.c`, and generic register-access helpers that can call `ig3rdma_get_reg_addr`.

## Risks and test signals
Risks include PF/VF interrupt stride mistakes, missing MMIO region coverage, WARNs on valid offsets after firmware layout changes, and feature flags advertised before all dependent paths are ready. Tests should cover PF and VF vector writes, register lookup across primary and auxiliary regions, stats reads through the Gen3 map, and capability exposure for SRQ and timestamped CQEs.
