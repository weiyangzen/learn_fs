# File Research: sources/cow-pools/openzfs/module/os/linux/zfs/zfs_sysfs.c

## Purpose

Builds the ZFS sysfs interface under `/sys/module/zfs` so userland can discover supported kernel features, pool features, dataset properties, vdev properties, and pool properties from the loaded module.

## Kobject Framework

`zfs_mod_kobj_t` wraps a Linux `kobject`, `kobj_type`, `sysfs_ops`, allocated attributes, default group, child object table, and child count.

Core helpers:

- `zfs_kobj_init()` allocates attribute tables/default groups/children, wires show and release ops, and supports both `default_groups` and older `default_attrs` kernels.
- `zfs_kobj_add_attr()` initializes one read-only attribute and places it in the default group.
- `zfs_kobj_add()` initializes and adds a kobject under a parent.
- `zfs_kobj_fini()` recursively finalizes children, deletes the kobject, and drops the reference.
- `zfs_kobj_release()` frees allocated attributes, default group arrays, children, and resets counts.

## Property Sysfs

The common property attributes are `type`, `readonly`, `setonce`, `visible`, `values`, `default`, and for dataset properties `datasets`.

`zprop_sysfs_show()` renders one property attribute: property type, booleans, values string, numeric/string/index default, or applicable dataset types. `dataset_property_show()`, `vdev_property_show()`, and `pool_property_show()` map kobject names to property descriptors and call the common renderer.

`zprop_to_kobj()` creates one child kobject per property and attaches the appropriate attributes. `zfs_sysfs_properties_init()` creates one top-level property directory for pool, vdev, or dataset properties and populates children using `zprop_iter_common()`.

## Feature Sysfs

Kernel features are hard-coded as:

- `com.delphix:vdev_initialize`
- `org.zfsonlinux:vdev_trim`
- `org.openzfs:l2arc_persistent`

Each has a `supported` attribute that returns `yes`.

Pool features use `spa_feature_table` and expose `description`, `guid`, `uname`, `readonly_compatible`, `required_for_mos`, `activate_on_enable`, and `per_dataset`. `pool_feature_show()` looks up features by GUID and renders strings or flag-derived booleans.

`zfs_kernel_features_init()` and `zfs_pool_features_init()` create top-level feature directories and child kobjects.

## Initialization And Cleanup

`zfs_sysfs_init()` chooses the parent kobject depending on built-in versus module build, then initializes kernel features, pool features, pool properties, vdev properties, and dataset properties. On failure it finalizes previously created top-level kobjects.

`zfs_sysfs_fini()` finalizes all top-level kobjects and their children.
