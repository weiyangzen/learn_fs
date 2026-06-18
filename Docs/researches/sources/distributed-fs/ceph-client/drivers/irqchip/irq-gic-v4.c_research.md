# sources/distributed-fs/ceph-client/drivers/irqchip/irq-gic-v4.c

## Purpose

`irq-gic-v4.c` provides the public, hypervisor-facing GICv4/GICv4.1 helper layer. It hides the ITS-specific command details behind irqchip APIs and gives KVM-style users functions to allocate VPE doorbell IRQs, map and unmap guest VLPIs, schedule and deschedule VPEs, update VLPI or VSGI properties, and commit/invalidate VPE state.

## Important APIs, Types, And Functions

Static state consists of `gic_domain`, `vpe_domain_ops`, and `sgi_domain_ops`, installed by `its_init_v4()`. `gic_cpuif_has_vsgi()` checks ARM64 CPU feature registers for GICv4.1 virtual SGI support. `has_v4_1()` and `has_v4_1_sgi()` summarize initialized capabilities.

The main exported helpers are `its_alloc_vcpu_irqs()`, `its_free_vcpu_irqs()`, `its_make_vpe_non_resident()`, `its_make_vpe_resident()`, `its_commit_vpe()`, `its_invall_vpe()`, `its_map_vlpi()`, `its_get_vlpi()`, `its_unmap_vlpi()`, `its_prop_update_vlpi()`, `its_prop_update_vsgi()`, and `its_init_v4()`. `its_alloc_vcpu_sgis()` is the internal GICv4.1 virtual SGI-domain allocator.

## Control Flow

`its_init_v4()` is called by the ITS driver after it has created the VPE irq-domain operations. It records the root GIC domain and VPE/SGI domain ops and enables the public GICv4 path. A VM calls `its_alloc_vcpu_irqs()` with an `its_vm` containing VPE pointers. The helper creates a named fwnode, creates a hierarchical domain over the GIC domain using `vpe_domain_ops`, initializes each VPE's VM pointer and IDAI default, allocates one VPE doorbell IRQ per VPE, records the Linux IRQ numbers, and optionally creates a 16-entry virtual SGI domain per VPE when GICv4.1 vSGI is available.

Residency helpers build `struct its_cmd_info` values and pass them through `irq_set_vcpu_affinity(vpe->irq, info)`, relying on the ITS VPE irq_chip to interpret command types. Non-resident transitions either request GICv4.1 doorbell behavior or re-enable a masked doorbell IRQ for GICv4.0. Resident transitions disable the doorbell for GICv4.0 before guest entry, or pass group enable bits for GICv4.1. VLPI mapping, query, unmapping, pending-state, and property updates similarly use `irq_set_vcpu_affinity()` on the physical LPI IRQ, with command types such as `MAP_VLPI`, `GET_VLPI`, `PROP_UPDATE_VLPI`, and `PROP_UPDATE_AND_INV_VLPI`.

## State And Persistence Behavior

This file stores only the global domain operation pointers. VM and VPE state lives in caller-provided `struct its_vm` and `struct its_vpe` objects, plus the irq domains and fwnodes allocated here. Allocation persists until `its_free_vcpu_irqs()` frees SGI domains, frees VPE IRQs, removes the VM domain, and releases the fwnode. Runtime state transitions update VPE flags such as `resident` and `ready`, but hardware state is programmed by the ITS irq_chip implementation in `irq-gic-v3-its.c`.

## Dependencies And Integration Points

The file depends on `linux/irqchip/arm-gic-v4.h`, irqdomain APIs, generic IRQ APIs, PID naming for fwnodes, and ARM64 CPU feature access when built for ARM64. It is intentionally a thin layer over the irqchip callbacks implemented by the ITS driver. Its consumers are hypervisor code paths that know about `struct its_vm`, `struct its_vpe`, and `struct its_vlpi_map`.

## Risks

The main risk is that the API multiplexes many GICv4 operations through `irq_set_vcpu_affinity()`. Incorrect command types, null maps, or calls before `its_init_v4()` has installed domain ops result in failures that can be hard to distinguish from hardware errors. GICv4.0 doorbell masking uses nested enable/disable balancing, so residency ordering matters. Partial allocation failures must remove fwnodes and domains; SGI allocation failure after VPE IRQ allocation can leave cleanup paths sensitive to missing mappings.

## Test Signals

Tests should allocate and free VPE IRQs for VMs with multiple VPEs, verify domain and fwnode cleanup on injected failures, schedule/deschedule VPEs with and without doorbell requests, map/get/unmap VLPIs, update VLPI properties with and without invalidation, update VSGI priority/group on GICv4.1 systems, and confirm `resident` and `ready` fields track successful irqchip operations.
