# File Research: sources/block-storage/parted/libparted/device.c

This file implements libparted’s common `PedDevice` API and delegates platform-specific work through `ped_architecture->dev_ops`.

Global device cache:
- Maintains a process-global linked list `devices`.
- `_device_register()` appends a device to the list.
- `_device_unregister()` removes a device and tolerates repeated unregister calls.
- `ped_device_get_next()` iterates the cached list.
- `ped_device_free_all()` destroys all cached devices.
- `ped_device_cache_remove()` removes a device from the cache without destroying it.

Device lookup and probing:
- `_ped_device_probe()` calls `ped_device_get()` while suppressing uncaught probe exceptions.
- `ped_device_probe_all()` delegates to the active architecture backend.
- `ped_device_get()` canonicalizes paths except `/dev/mapper/` and `/dev/md/`, returns a cached device when present, otherwise calls the architecture `_new` operation and registers the result.

Open/close and external access:
- `ped_device_open()` enforces non-external mode and uses `open` for first open or `refresh_open` for nested opens, incrementing `open_count` on success.
- `ped_device_close()` decrements `open_count` and uses `refresh_close` or final `close`.
- `ped_device_begin_external_access()` marks external mode and closes the backend fd if the device is currently open.
- `ped_device_end_external_access()` clears external mode and reopens the backend if the open count is nonzero.

I/O and sync dispatch:
- `ped_device_read()`, `ped_device_write()`, `ped_device_check()`, `ped_device_sync()`, and `ped_device_sync_fast()` assert the device is open and not in external mode, then delegate to architecture operations.

Constraints and alignment:
- `ped_device_get_constraint()` returns a whole-device constraint without alignment requirements.
- `_ped_device_get_aligned_constraint()` constructs start and end alignment constraints over the whole device.
- `ped_device_get_minimal_aligned_constraint()` uses minimum hardware alignment.
- `ped_device_get_optimal_aligned_constraint()` uses optimal hardware alignment.
- `ped_device_get_minimum_alignment()` asks the architecture backend first, then falls back to `phys_sector_size / sector_size`.
- `ped_device_get_optimum_alignment()` asks the backend first, then falls back to 1 MiB alignment via `PED_DEFAULT_ALIGNMENT / sector_size`.

Research notes:
- This file is the central abstraction boundary: all common libparted users call here, while Linux/GNU/BeOS details live behind `PedDeviceArchOps`.
- The global cache is simple and unsynchronized.
- The path canonicalization exceptions for `/dev/mapper` and `/dev/md` preserve names that tests and Linux device semantics depend on.
