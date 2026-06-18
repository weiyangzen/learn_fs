# sources/distributed-fs/ceph-client/drivers/iommu/iommu-sysfs.c

## Purpose
This file provides the common sysfs representation for registered IOMMU hardware devices. It creates the global `iommu` device class, gives every IOMMU instance an initially empty `devices/` attribute group, and lets IOMMU drivers add/remove bidirectional sysfs links between an IOMMU device and the devices it manages.

## Important APIs, Types, And Functions
`iommu_class` is a static `struct class` named `iommu`; its `dev_release` frees the dynamically allocated `struct device`, and its class device groups include a `devices` subdirectory.

`iommu_dev_init()` registers that class through `postcore_initcall`, so other IOMMU core and driver code can add IOMMU sysfs devices later in boot.

`iommu_device_sysfs_add()` allocates `iommu->dev`, initializes it, assigns class, parent, and driver-provided attribute groups, sets the kobject name from a format string, adds the device, and stores the `struct iommu_device` as driver data. It is exported GPL.

`iommu_device_sysfs_remove()` clears driver data, unregisters the device, and nulls `iommu->dev`. It is exported GPL.

`iommu_device_link()` adds `devices/<managed-device-name>` under the IOMMU device and creates a reverse `iommu` symlink under the managed device. `iommu_device_unlink()` removes both links.

## Control Flow
Boot registers the `iommu` class before most device probing. A concrete IOMMU driver calls `iommu_device_sysfs_add()` while registering its `struct iommu_device`; later, when the core probes a managed device, `iommu_init_device()` in `iommu.c` calls `iommu_device_link()` to expose the relationship. Device release paths call `iommu_device_unlink()`, and IOMMU driver teardown calls `iommu_device_sysfs_remove()`.

The add path is failure-safe: if name assignment or `device_add()` fails, it drops the initialized device with `put_device()`, causing the release callback to free it.

## State And Persistence
Persistent kernel state is limited to the `iommu_class` registration, `iommu->dev`, kobject names, sysfs links, and driver data. There is no on-disk persistence. Lifetime is kobject/device-model managed: `device_unregister()` eventually invokes `release_device()`.

## Dependencies And Integration Points
This file depends on the Linux driver core, sysfs kobjects, `struct iommu_device`, and exported IOMMU core APIs used by hardware IOMMU drivers. Its links are consumed by userspace tools inspecting `/sys/class/iommu/...` and by the IOMMU group/device sysfs topology produced in `iommu.c`.

## Risks
`iommu_device_link()` assumes `iommu->dev` has already been added; callers must preserve that ordering. Symlink names use `dev_name(link)`, so name collisions or late device renames would surface as sysfs errors. Error handling for the reverse symlink correctly removes the forward link, but callers still need to unwind device probe if link creation fails.

## Test Signals
Useful signals include booting with an IOMMU driver and verifying `/sys/class/iommu/<name>/devices/` links, reverse `iommu` links on managed devices, and clean removal during driver unbind or hotplug. KASAN/kmemleak should see no leak from failed `iommu_device_sysfs_add()` paths.
