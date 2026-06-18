# sources/distributed-fs/ceph-client/include/linux/arm_ffa.h

## Purpose
Defines Arm Firmware Framework for Arm A-profile (FF-A) function IDs, error/version encoding, FF-A bus/driver structures, partition information, direct/indirect messaging payloads, memory-sharing descriptors, and operation tables.

## Important APIs, Types, And Functions
`FFA_SMC_32()`/`FFA_SMC_64()` build SMCCC function IDs for FF-A calls such as version/features, RX/TX map/unmap, partition info, direct messaging, memory donate/lend/share/retrieve/reclaim, notifications, secondary entry registration, memory permissions, console log, and direct request2/response2. `FFA_FN_NATIVE()` selects 64-bit or 32-bit IDs by kernel word size. `struct ffa_device`, `struct ffa_driver`, `struct ffa_device_id`, `ffa_register()`, `ffa_unregister()`, and `module_ffa_driver()` implement the FF-A bus contract. Memory structures include `ffa_mem_region_addr_range`, `ffa_composite_mem_region`, `ffa_mem_region_attributes`, `ffa_mem_region`, and `ffa_mem_ops_args`. Ops tables are split into `ffa_info_ops`, `ffa_msg_ops`, `ffa_mem_ops`, `ffa_cpu_ops`, `ffa_notifier_ops`, and aggregate `ffa_ops`.

## Control Flow, State, And Persistence
The transport registers discovered partitions as `ffa_device` instances. Drivers bind by UUID and call ops for version/partition info, direct or indirect messages, memory share/lend/reclaim, vCPU run, and notifications. Memory descriptor helper flow computes endpoint memory access descriptor sizes and offsets depending on FF-A version, preserving pre-1.1 and 1.2 layout differences.

## Dependencies And Integration Points
Depends on bitfield/device/module/types/uuid helpers and SMCCC constants from `arm-smccc.h`. Integrates with the ARM FF-A transport driver, secure partitions, hypervisors/SPM, scatterlists, Linux driver core, module registration, notifications, and memory-sharing users.

## Risks And Test Signals
Descriptor layout is version-sensitive: wrong EMAD size, offsets, handle packing, or native-width function choice can break secure memory transactions. Tests should cover FF-A 1.0/1.1/1.2 negotiation, 32-bit partition restrictions for direct request2, RX/TX buffer mapping, partition registration/unregistration, UUID binding, direct and indirect messages, memory share/lend/reclaim, notification callbacks, and stub returns without `CONFIG_ARM_FFA_TRANSPORT`.
