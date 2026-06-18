# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_configfs.c

## Purpose
This file implements the Xe configfs subsystem. It lets administrators create per-PCI-device configfs groups before driver bind and set probe-time policies such as survivability mode, allowed GT types, allowed engines, PSMI enablement, context-restore batch buffers, and SR-IOV PF limits.

## Important APIs, Types, and Functions
Key types are `struct xe_config_group_device`, nested `struct xe_config_device`, and `struct wa_bb`. Public getters include `xe_configfs_check_device`, `xe_configfs_get_survivability_mode`, `xe_configfs_primary_gt_allowed`, `xe_configfs_media_gt_allowed`, `xe_configfs_get_engines_allowed`, `xe_configfs_get_psmi_enabled`, context-restore BB getters, `xe_configfs_admin_only_pf`, and `xe_configfs_get_max_vfs`. Init/exit functions register and unregister the `xe` configfs subsystem.

## Control Flow
`xe_config_make_device_group` validates canonical PCI BDF names, resolves PF/VF relationships, matches Xe PCI IDs, allocates a config group, seeds defaults, and conditionally creates an `sriov` subgroup. Attribute stores parse user text, take the device mutex, reject changes if the PCI device is already bound, then update in-memory config. Engine parsing accepts class names with instance numbers or `*`; context-restore BB parsing counts dwords first, allocates a single command buffer, then reparses to store MI commands or register-write sequences.

## State and Persistence Behavior
Configuration lives only in configfs kernel objects and is consumed during probe. It is not persistent across module unload or configfs object deletion. The `lock` serializes attributes, while `config_group_find_item` and `config_group_put` manage lookup lifetimes. Custom values are reported during probe by `xe_configfs_check_device`.

## Dependencies and Integration Points
It depends on Linux configfs, PCI lookup, Xe PCI descriptor data, module parameters, GT/engine enumerations, SR-IOV mode helpers, and MI command encodings. Consumers include PCI probe, survivability mode, HW engine filtering, PSMI/RTP/GUC setup, LRC context restore programming, and SR-IOV PF initialization.

## Risks
Input parsing is security-sensitive because it accepts root-provided strings that alter probe behavior and context restore commands. Bound-device detection is best effort through PCI drvdata and must prevent late mutation. Incorrect PF/VF resolution could configure the wrong device. Context restore BB allocation uses shared per-class storage, so length/pointer consistency matters.

## Test Signals
Configfs create/remove tests, invalid BDF/name tests, pre-bind vs post-bind attribute writes, engine mask parsing, GT type disabling, PSMI and survivability probe behavior, context-restore BB programming, SR-IOV max_vfs/admin_only_pf combinations, and module unload cleanup are useful signals.
