# sources/distributed-fs/ceph-client/include/linux/irqchip/arm-gic-v4.h

## Purpose
`arm-gic-v4.h` defines the Linux/KVM-facing structures and APIs for GICv4 virtual LPIs, virtual processing elements, doorbells, and vSGI/vPE management.

## Important APIs, types, and functions
Important types include `struct its_vm`, `struct its_vpe`, `struct its_vlpi_map`, `enum its_vcpu_info_cmd_type`, and `struct its_cmd_info`. APIs include vCPU IRQ allocation/free, VPE resident/nonresident/commit/invalidate operations, VLPI map/get/unmap/property update, vSGI property update, `its_init_v4`, and `gic_cpuif_has_vsgi`.

## Control flow
KVM embeds VM/VPE structures, allocates doorbell LPIs, maps physical IRQs to VLPIs through `irq_set_vcpu_affinity` command info, schedules VPEs resident/nonresident around vCPU execution, and updates virtual interrupt properties or invalidates state through ITS commands.

## State and persistence
Runtime state includes VM fwnode/domain, virtual property page, VPE array, doorbell bitmap/counts, per-VPE VPT page, residency/ready flags, VLPI counts, vSGI config, collection ID, and locks for VMAPP/VPE/VMOVP ordering.

## Dependencies and integration points
It integrates KVM, GICv3 ITS, irqdomain ops, raw spinlocks, pages, and virtual interrupt affinity APIs.

## Risks and test signals
Risks include lock-order violations, stale VPE residency, doorbell LPI leaks, property-update races, and GICv4.0/v4.1 union misuse. Tests should cover VM create/destroy, vCPU schedule/deschedule, VLPI map/unmap under load, vSGI injection, doorbell enable/disable, and CPU migration.
