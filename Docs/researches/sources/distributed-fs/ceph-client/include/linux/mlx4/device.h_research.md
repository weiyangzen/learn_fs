# sources/distributed-fs/ceph-client/include/linux/mlx4/device.h

## Purpose
Primary mlx4 public device contract. It describes ConnectX-3 capabilities, resources, queue objects, event formats, flow steering, memory registration, SR-IOV state, and core service APIs for Ethernet, RDMA, and auxiliary drivers.

## Important APIs/Types
Defines device/capability/steering flags, limits, port/resource enums, opcodes, events, permissions, rate-limit caps, `mlx4_caps`, `mlx4_phys_caps`, DMA buffer/MTT/MR/MW/UAR/BF/DB/HWQ types, CQ/QP/SRQ objects, address vectors, counters, quotas, persistent device state, auxiliary device wrappers, EQE layouts, MAD IFC, flow-steering software and hardware rule structures, and active-port/slave bitmap helpers.

APIs cover buffer/resource allocation, memory registration, doorbells, hardware queues, CQ/QP/SRQ lifecycle, port init/close, unicast/multicast attach, flow steering/promisc rules, MAC/VLAN registration, SET_PORT variants, EQ assignment, diagnostics, WOL, counters, admin GUIDs, slave events/state, RoCE GIDs, VXLAN/RoCEv2 config, port mapping, VF SMI, MR reregistration, module info, and clock parameters.

## Control Flow
mlx4 core populates `mlx4_dev` from firmware, then upper layers allocate resources and issue commands. Queue users allocate buffers/MTTs, create CQ/QP/SRQ objects, register callbacks, and handle EQE-driven events. Flow steering builds software specs and serializes hardware rules. SR-IOV paths translate slaves and synthesize events.

## State And Persistence
Persistent state includes hardware/software/PPCI state, current port types, catastrophic-error workqueue, crash-dump regions, flags/caps/quotas/radix tree, refcounted resources, registered MAC/VLAN/flow IDs, active-port maps, and DMA-visible tables.

## Dependencies And Integration Points
Depends on auxiliary bus, PCI, completions, radix tree, CPU rmap, crash dump, refcount, timecounter, and Ethernet constants. Integrates with mlx4_core/en/ib, devlink, ethtool, RDMA core, SR-IOV, flow steering, EQs, and firmware commands.

## Risks
Capability drift, one-based port arrays, SR-IOV mapping mistakes, resource leaks, endian packing errors, reserved QP/QKey violations, bonding races, and kdump low-memory behavior.

## Test Signals
Capability parsing, HCA/port bring-up, aux driver attach, PD/MR/CQ/QP/SRQ lifecycle, flow steering, MAC/VLAN registration, VF mappings/events/config, RoCE GIDs, EQ assignment, WOL/module info, counters, catastrophic error handling, and teardown leak checks.
