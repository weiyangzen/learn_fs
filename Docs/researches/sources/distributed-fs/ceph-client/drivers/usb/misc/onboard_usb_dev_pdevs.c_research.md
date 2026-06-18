# sources/distributed-fs/ceph-client/drivers/usb/misc/onboard_usb_dev_pdevs.c

Purpose: Exported helper API for USB hub code to create and destroy platform devices for supported onboard USB children beneath a parent hub.

Important APIs and types: `struct pdev_list_entry`, `of_is_onboard_usb_dev()`, exported `onboard_dev_create_pdevs()`, and exported `onboard_dev_destroy_pdevs()`. It depends on USB/HCD OF helpers, `of_platform_device_create()`, and the shared `onboard_dev_match[]` table.

Control flow: creation returns early if the parent hub has no OF node or is a secondary root HCD. It iterates child ports, resolves each child OF node, skips unsupported nodes, handles `peer-hub` de-duplication so one physical dual-speed hub gets one platform device, creates the platform device with the parent hub as parent, and records it in the caller-owned list. Destruction walks the list, destroys each platform device, and frees the list entry.

State and persistence: only the caller-owned list persists created platform devices; no global state is kept. Risks include subtle primary/secondary HCD and peer-hub de-duplication logic, partial failure behavior that skips failed nodes but continues, and reliance on parent hub maxchild/OF mappings. Test signals include root hub primary/secondary cases, nested hubs, peer-hub duplicate prevention, destroy cleanup, and unsupported child-node skip behavior.
