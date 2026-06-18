
# sources/distributed-fs/ceph-client/drivers/hwtracing/stm/core.c

Purpose: generic System Trace Module class infrastructure. It registers STM devices and STM source devices, manages character device writes/mmap/ioctls, allocates STP master/channel ranges from configfs policies, brokers framing protocol drivers, and provides source-to-device links.

Important APIs/types/functions: exported APIs include `stm_register_device()`, `stm_unregister_device()`, `stm_source_register_device()`, `stm_source_unregister_device()`, `stm_source_write()`, `stm_register_protocol()`, `stm_unregister_protocol()`, `stm_lookup_protocol()`, `stm_put_protocol()`, and `stm_data_write()`. Key structures are `struct stm_device`, `struct stm_source_device`, `struct stm_output`, `struct stm_file`, `struct stp_master`, and `struct stm_protocol_driver`.

Control flow: module init registers `stm` and `stm_source` classes, initializes configfs policy support, SRCU, and protocol list, then requests the basic protocol module when configured. Hardware drivers call `stm_register_device()` with `stm_data`; source modules call `stm_source_register_device()`. Users create configfs policies binding a device and protocol, then either open the STM char device or link a source. Writes auto-assign a policy by task name/default if needed, copy user data, runtime-resume the STM device, and call the active protocol's `write()` callback. Source writes use SRCU to safely dereference the linked STM device and protocol path.

State and persistence: state is volatile kernel memory plus configfs directory state created by users. STM devices maintain policy pointer, selected protocol, master/channel bitmaps, linked source list, char major, and runtime-PM autosuspend state. Source devices maintain an RCU-protected link pointer and one `stm_output`.

Dependencies and integration: depends on configfs policy helpers in `policy.c`, Linux char-device and mmap infrastructure, PM runtime, SRCU, `uapi/linux/stm.h` ioctls, and hardware-provided `stm_data` callbacks. Intel TH STH and Coresight STM are typical hardware providers; console/ftrace/heartbeat are source providers.

Risks: lock ordering across `policy_mutex`, configfs subsystem mutex, `mc_lock`, output locks, `link_mutex`, `link_lock`, and source `link_lock` is important. Master/channel allocation requires power-of-two widths via bitmap regions. Source unlink uses SRCU and retry on link changes; mistakes can produce use-after-free. Char-device mmap requires exact assigned width and hardware page-aligned MMIO. `stm_core_exit()` calls SRCU cleanup before class unregister/configfs exit, which should be checked for active users.

Test signals: register dummy and hardware STM devices, create/remove configfs policies with both protocols, char write/ioctl/mmap flows, source link/unlink races, module unload with active sources, master/channel exhaustion, runtime-PM autosuspend, and ftrace/console high-frequency writes.
