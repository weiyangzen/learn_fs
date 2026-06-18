# sources/distributed-fs/ceph-client/drivers/gpu/host1x/bus.c

## Purpose

`host1x/bus.c` implements the host1x logical bus, composite device/client matching, host1x driver registration, client lifecycle, debugfs device listing, suspend/resume reference counting, and host1x buffer-object pin/unpin caching.

## Important APIs, Types, And Functions

Important globals are `clients`, `drivers`, and `devices` lists with mutexes. Internal `struct host1x_subdev` maps DT nodes to clients. Exported APIs include `host1x_device_init()`, `host1x_device_exit()`, `host1x_register()`, `host1x_unregister()`, `host1x_driver_register_full()`, `host1x_driver_unregister()`, `__host1x_client_init()`, `host1x_client_exit()`, `__host1x_client_register()`, `host1x_client_unregister()`, `host1x_client_suspend()`, `host1x_client_resume()`, `host1x_bo_pin()`, and `host1x_bo_unpin()`.

## Control Flow

Host1x controller registration adds the controller to the global list, attaches already registered host1x drivers, and creates debugfs `devices`. Host1x driver registration adds the driver, creates one logical host1x device per controller, parses DT subdevices recursively from driver match tables, and registers the bus driver. Client registration tries to match the client OF node against pending subdevices; when all subdevices are active the logical device is added to the `host1x` bus and the host1x driver can probe. Device init calls each client's `early_init` then `init`, with reverse teardown on failure; exit calls `exit` then `late_exit` in reverse order. Buffer pinning reuses cache entries by BO/direction, otherwise calls BO ops and tracks mappings in BO and cache lists with krefs.

## State And Persistence Behavior

Persistent state includes global idle client/driver/controller lists, per-controller logical devices, per-device idle/active subdevice lists, per-device client lists, `registered` flag, client `host` pointer and `usecount`, and BO mapping cache entries. Device release removes subdevices, returns clients to idle lists, and frees the logical device. Suspend/resume recursively walks parent clients and uses `usecount` to only call ops on first resume/last suspend.

## Dependencies And Integration Points

It depends on Linux driver core bus registration, OF matching and uevents, debugfs/seq_file, DMA mask/segment helpers, host1x public headers, and BO ops supplied by host1x clients. It integrates host1x controller drivers, logical subsystem drivers such as Tegra DRM, and individual engine clients.

## Risks And Test Signals

Risks include complex list movement under multiple locks, partial DT recursion cleanup FIXME, adding logical devices with no subdevices, lifecycle races between client unregister and device deletion, suspend/resume underflow if callers mismatch references, and BO mapping cache stale entries if krefs are wrong. Test registration ordering permutations, missing/disabled DT subdevices, probe failure teardown, client unregister while bound, debugfs output, recursive parent suspend/resume, BO pin cache reuse, and unpin last-reference cleanup.
