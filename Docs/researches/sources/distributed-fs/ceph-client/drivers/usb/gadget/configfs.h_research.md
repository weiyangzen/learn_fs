# sources/distributed-fs/ceph-client/drivers/usb/gadget/configfs.h

## Purpose
`configfs.h` is the local header that exposes configfs gadget helpers shared between `configfs.c` and USB function implementations. It declares gadget unregistration through a config item, declares OS descriptor interface directory creation, and provides a typed conversion helper for OS descriptor config groups.

## Important APIs, Types, and Functions
The exported declarations are `unregister_gadget_item(struct config_item *item)` and `usb_os_desc_prepare_interf_dir(struct config_group *parent, int n_interf, struct usb_os_desc **desc, char **names, struct module *owner)`. The inline `to_usb_os_desc()` converts a config item for an interface OS descriptor group back to `struct usb_os_desc` using `container_of()`.

## Control Flow
Function drivers that need OS descriptor configfs support call `usb_os_desc_prepare_interf_dir()` with their parent function group, number of interfaces, descriptor objects, names, and module owner. Configfs release or external helper paths can call `unregister_gadget_item()` to unbind a gadget represented by a root config item. `to_usb_os_desc()` is used by attribute handlers in `configfs.c` for compatible IDs and extended properties.

## State and Persistence
The header owns no state. It defines access to state allocated and managed by `configfs.c`: gadget root objects and per-interface `usb_os_desc` groups.

## Dependencies and Integration Points
It depends on `<linux/configfs.h>` and assumes `struct usb_os_desc` is visible to includers through surrounding USB gadget headers. It is a narrow integration point between configfs gadget infrastructure and function drivers that expose Microsoft OS descriptor metadata.

## Risks
The conversion helper assumes the item is a config group embedded in `struct usb_os_desc`; using it on the wrong item type will corrupt type interpretation. Callers of `usb_os_desc_prepare_interf_dir()` must provide descriptor and name arrays that remain valid for the created groups.

## Test Signals
Compile coverage from OS-descriptor-capable functions, configfs creation of `os_desc/interface.*` groups, compatible/sub-compatible ID stores, extended property make/drop, and gadget unregistration through a config item.
