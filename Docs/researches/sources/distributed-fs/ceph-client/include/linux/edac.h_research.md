# sources/distributed-fs/ceph-client/include/linux/edac.h

## Purpose
This header defines the Error Detection and Correction core interfaces for memory controllers and newer RAS device features. It models memory topology, DIMMs/ranks/csrows, error counters, raw error reports, controller operations, scrub/ECS/memory-repair feature operations, and EDAC device registration.

## Important APIs, types, and functions
Global state includes `edac_op_state` and `edac_get_sysfs_subsys()`. `opstate_init()` normalizes unsupported operation states to polling. Enums define device width (`dev_type`), hardware memory-controller error severity (`hw_event_mc_err_type`), memory technology (`mem_type`), EDAC capability (`edac_type`), scrub capability (`scrub_type`), memory hierarchy layers (`edac_mc_layer_type`), RAS feature type (`edac_dev_feat`), memory repair type, and memory repair command.

Core topology structs are `edac_mc_layer`, `dimm_info`, `rank_info`, `csrow_info`, `errcount_attribute_data`, `edac_raw_error_desc`, and `mem_ctl_info`. `mem_ctl_info` holds device/sysfs identity, global list linkage, capabilities, scrub mode and callbacks, `edac_check`, page-to-physical translation, csrow and DIMM arrays, private driver data, no-info counters, completion, driver attributes, delayed work, raw error descriptor, debugfs state, fake injection fields, operation state, and flexible hierarchy layers. `mci_for_each_dimm()` iterates DIMMs, and `edac_get_dimm()` maps layer coordinates to a DIMM.

RAS feature APIs include `struct edac_scrub_ops`, `edac_scrub_get_desc()`, `struct edac_ecs_ops`, `edac_ecs_get_desc()`, `struct edac_mem_repair_ops`, `edac_mem_repair_get_desc()`, `struct edac_dev_data`, `struct edac_dev_feat_ctx`, `struct edac_dev_feature`, and `edac_dev_register()`.

## Control flow, state, and persistence
EDAC controller state persists in `mem_ctl_info` objects registered with the EDAC core. Error counters are stored at DIMM, rank/csrow, and controller levels. Polling, interrupt, and NMI operation modes determine how `edac_check()` is invoked by implementation code. Raw error details are staged in the controller-owned `edac_raw_error_desc`. Scrub, ECS, and memory repair operations expose driver callbacks through sysfs-style descriptors when configured.

## Dependencies and integration points
It depends on device model, completions, workqueues, debugfs, NUMA, atomics, and optional EDAC feature configs. It integrates with memory-controller drivers, firmware error reporting, sysfs/debugfs, RAS tools, CXL-like memory repair flows, and page offlining/poison handling in implementation layers.

## Risks and test signals
Risks include topology index mistakes in `edac_get_dimm()`, direct driver mutation of fields meant for the core, stale counters, unsafe fake injection, missing mandatory memory-repair callbacks, and inconsistent sysfs descriptors when feature configs are disabled. Tests should cover layer-to-DIMM indexing for one/two/three layers, error counter updates, poll work scheduling, scrub/ECS/memory-repair descriptor stubs, memory repair validation requiring `do_repair` and HPA/DPA setters, and controller registration/unregistration cleanup.
