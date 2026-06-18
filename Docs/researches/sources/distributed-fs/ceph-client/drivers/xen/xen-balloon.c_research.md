# sources/distributed-fs/ceph-client/drivers/xen/xen-balloon.c

## Purpose
`xen-balloon.c` exposes the Xen balloon control device and xenstore target watcher. It lets userspace and xenstore adjust the guest memory target and exposes current balloon stats through sysfs.

## Important APIs, types, and functions
The public entry point is `xen_balloon_init`. Important functions are `watch_target`, `balloon_init_watcher`, `target_kb_show/store`, `target_show/store`, and `register_balloon`. It defines sysfs attributes for target, scheduling/retry controls, scrub-pages, and current/low/high memory information. Under memory hotplug it references `xen_saved_max_mem_size`.

## Control flow
`xen_balloon_init` registers a `xen_memory` bus/device with balloon sysfs groups and registers a xenstore notifier. Once xenstore is available, the notifier installs a watch on `memory/target`. Watch callbacks read the new target in KiB, compensate for static-max differences in HVM/non-dom0 cases, and call `balloon_set_new_target`. Sysfs stores require `CAP_SYS_ADMIN`, parse byte or KiB values, and update the target.

## State and persistence
State is mainly the global balloon stats from the Xen balloon subsystem plus static watch-local variables tracking first-fire adjustment. Sysfs changes and xenstore target updates affect runtime balloon target state; persistent policy is external to this file.

## Dependencies and integration points
It depends on Xen balloon core APIs, xenbus watches/notifiers, Linux device/bus/sysfs infrastructure, capability checks, memory hotplug globals, Xen page/features, and mem-reservation helpers. It integrates Xen memory policy with Linux sysfs and xenstore.

## Risks and test signals
Risks include target conversion mistakes, first-watch target adjustment for HVM guests, missing xenstore keys, permission enforcement, sysfs registration cleanup on failure, and interactions with memory hotplug max-memory restoration. Test signals include xenstore target changes, sysfs target writes with and without `CAP_SYS_ADMIN`, dom0/PV/HVM cases, memory hotplug-enabled boots, scrub/retry attribute reads, and balloon target convergence.
