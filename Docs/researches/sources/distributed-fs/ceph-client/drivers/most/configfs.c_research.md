# sources/distributed-fs/ceph-client/drivers/most/configfs.c

## Purpose
This file implements the configfs control plane for the MOST stack. It lets users create named links between MOST interface channels and components, set channel configuration values, and create sound-card groupings before asking the component to complete configuration.

## Important APIs, types, and functions
- `struct mdev_link` represents one configfs item/link. It stores link lifecycle flags, channel config values, device/channel/component names, component parameters, and a list node for deferred reapplication.
- `set_config_and_add_link()` pushes all stored configuration values into MOST core setters and then calls `most_add_link()`.
- Attribute store/show functions implement configfs fields: `device`, `channel`, `comp`, `comp_params`, `num_buffers`, `buffer_size`, `subbuffer_size`, `packets_per_xact`, `datatype`, `direction`, `dbr_size`, `create_link`, and `destroy_link`.
- `struct most_common` and static instances `most_cdev`, `most_net`, and `most_video` create component-specific configfs subsystems whose new items default `comp` to the subsystem component.
- `struct most_sound`, `struct most_snd_grp`, and related operations model sound-card groups and gate creation of a new sound group until the previous one is complete.
- Exported functions `most_register_configfs_subsys()`, `most_deregister_configfs_subsys()`, and `most_interface_register_notify()` are used by MOST core/components.

## Control flow
Component registration calls `most_register_configfs_subsys()`, which selects a static subsystem by component name and registers it with configfs. Creating an item under `most_cdev`, `most_net`, or `most_video` allocates `mdev_link`, takes a module reference for the component, initializes the config item, defaults the component name, and records the link name. User writes validate and store attributes. Writing true to `create_link` invokes `set_config_and_add_link()`, adds the link to `mdev_link_list`, and marks the link created. Writing true to `destroy_link` removes the link through `most_remove_link()` and deletes it from the list.

On config item release, a link that was not explicitly destroyed is removed from MOST core before the item is freed. For sound, configfs creates nested groups; writing true to `create_card` calls `most_cfg_complete("sound")`. `most_interface_register_notify()` iterates stored links when a matching interface appears, reapplies config/link creation, and triggers sound config completion if needed.

## State and persistence
Runtime state is in static configfs subsystem objects, `mdev_link_list`, and `most_sound_subsys.soundcard_list`. Configfs items persist only while mounted/configured in memory; there is no disk persistence. Module references keep component modules loaded while configfs items exist.

## Dependencies and integration points
The file depends on configfs, module refcounting, and MOST core exported configuration/link APIs. It integrates with cdev/net/video/sound components by name and with interface registration notifications from `core.c`.

## Risks and edge cases
- `mdev_link_list` is global and not visibly protected by a dedicated lock; configfs serialization may be relied upon.
- `destroy_link_store()` calls `list_del()` when the global list is non-empty, not when this item is known linked; double delete or wrong-list assumptions are risk points.
- Direction/datatype stores use `strcpy()` after validation against short literals, while other string stores use `strscpy()`.
- `set_config_and_add_link()` ignores `-ENODEV` from individual setters but still attempts link creation, supporting deferred interface appearance but making error interpretation nuanced.

## Test signals
Exercise configfs item creation/removal for cdev/net/video/sound, each attribute parser, invalid direction/datatype values, create/destroy link sequencing, module unload with live configfs items, deferred link reapplication when interfaces register after configfs setup, and sound group `create_card` ordering.
