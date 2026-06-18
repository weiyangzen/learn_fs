# sources/distributed-fs/ceph-client/drivers/edac/edac_device.h

## Purpose
This header defines the public and internal data model for EDAC generic devices, which represent ECC/error-reporting blocks that are not memory controllers. It declares the allocation, registration, deletion, index allocation, and error reporting APIs used by low-level EDAC device drivers.

## Important APIs, Types, And Functions
Core types include `struct edac_device_counter`, `struct edac_dev_sysfs_attribute`, `struct edac_dev_sysfs_block_attribute`, `struct edac_device_block`, `struct edac_device_instance`, and `struct edac_device_ctl_info`. The hierarchy is controller -> instances -> blocks, with CE/UE counters at every level.

Public APIs are `edac_device_alloc_ctl_info()`, `edac_device_free_ctl_info()`, `edac_device_add_device()`, `edac_device_del_device()`, `edac_device_handle_ce_count()`, `edac_device_handle_ue_count()`, `edac_device_handle_ce()`, `edac_device_handle_ue()`, and `edac_device_alloc_index()`. The header also declares `edac_layer_name[]` and sysfs helper structures used by `edac_device_sysfs.c`.

## Control Flow
Low-level drivers allocate a populated `edac_device_ctl_info`, fill device/module/controller metadata and optionally `edac_check`, register it with `edac_device_add_device()`, report errors through handle helpers, unregister with `edac_device_del_device()`, and free with `edac_device_free_ctl_info()`. Inline wrappers convert single CE/UE reports into count-based calls.

## State And Persistence
`struct edac_device_ctl_info` contains list linkage, owner module, index, logging/panic flags, poll interval/delay, driver sysfs attributes, EDAC bus pointer, op state, delayed work, parent device pointer, names, private data, start time, instances/blocks, counters, and main kobject. Instances and blocks embed their own kobjects and counters.

## Dependencies And Integration Points
The header depends on Linux device, kobject, list, sysfs, workqueue, and EDAC types. It is included by EDAC core code and by hardware drivers such as Armada Aurora L2 and CPC925 CPU/HT-link support.

## Risks
The header exposes many fields for direct low-level driver mutation, so lifecycle ordering and field initialization are caller-sensitive. The `BLOCK_OFFSET_VALUE_OFF` sentinel casts `-1` to unsigned, which makes generated block names dependent on caller intent. The private free helper frees `pvt_info`, `blocks`, `instances`, and controller memory and should only be reached through the intended kobject/free path.

## Test Signals
Compile-time coverage should ensure drivers can allocate expected topologies. Runtime tests should check instance/block naming, counter hierarchy behavior, inline CE/UE wrappers, and safe free after sysfs unregister.
