# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/sf/dev/dev.c

## Purpose

`sf/dev/dev.c` discovers active mlx5 subfunctions and represents each active SF as a Linux auxiliary device. It listens for VHCA state events, creates/removes auxiliary devices as SFs become active or inactive, and probes externally created active SFs during table creation.

## Important APIs, Types, and Functions

The main private type is `struct mlx5_sf_dev_table`, containing an xarray of `mlx5_sf_dev` objects indexed by SF index, BAR base/length information, optional active-scan workqueue, a stop flag, and the parent core device. `struct mlx5_sf_dev_active_work_ctx` carries queried active-state data to per-function VHCA workqueues.

Public functions are `mlx5_sf_dev_allocated()`, `mlx5_sf_dev_notifier_init()`, `mlx5_sf_dev_table_create()`, `mlx5_sf_dev_notifier_cleanup()`, and `mlx5_sf_dev_table_destroy()`. Local helpers create and remove auxiliary devices, arm VHCA events for every SF function, scan active SFs, and handle state-change notifications.

## Control Flow

Table creation checks `sf` and VHCA-event support, allocates a table, computes each SF BAR length from `log_min_sf_size`, records BAR2 base, initializes the device xarray, optionally starts an active-SF scan workqueue for non-eswitch-manager devices, and arms VHCA change events for all local SF function IDs. Active-scan work queries every function's VHCA state and, for active entries, queues add work onto a VHCA event worker selected by function id modulo `MLX5_DEV_MAX_WQS`.

Runtime state changes enter `mlx5_sf_dev_state_change_handler()`. It filters function IDs into the SF range, maps function ID to xarray index, and deletes devices for INVALID, ALLOCATED, or TEARDOWN_REQUEST states. For ACTIVE, it creates an auxiliary device if one does not already exist. Creation allocates an auxiliary id, fills `struct mlx5_sf_dev` with parent mdev, function id, SF number, and BAR base, initializes and adds the auxiliary device, then stores it in the xarray. Removal erases the xarray entry, deletes the auxiliary device, and uninitializes it so the release callback frees memory and auxiliary id.

## State and Persistence Behavior

Driver state is `dev->priv.sf_dev_table`, its xarray of auxiliary devices, each `mlx5_sf_dev`'s parent pointer, function id, SF number, auxiliary id, and BAR address. Firmware state is only observed via VHCA query/events and event arming. The table destroy path stops active scanning, removes all auxiliary devices after notifiers are cleaned up, warns if the xarray remains non-empty, and clears the priv pointer.

## Dependencies and Integration Points

The file depends on VHCA event APIs, auxiliary bus APIs, PCI BAR resources, SF capability helpers, ECPF/eswitch-manager tests, tracepoints in `dev_tracepoint.h`, and the auxiliary driver implemented in `sf/dev/driver.c`. It also relies on `mlx5_vhca_events_work_enqueue()` ordering to serialize add work per function hash.

## Risks and Edge Cases

There is an acknowledged race between querying an externally active SF and the SF becoming inactive before probe completes; the code accepts that probe may later fail or be removed after init. `mlx5_sf_dev_add()` stores the auxiliary device in the xarray only after `auxiliary_device_add()`, so a very early state event could observe no device and attempt another add. Destroy must run after notifier cleanup to avoid event/remove races. Failure after `auxiliary_device_add()` but before xarray insert calls remove/uninit, which should trigger proper release.

## Test Signals

Test local and external SF creation, active-state scan with many SFs, VHCA active/allocated/teardown events, auxiliary device sysfs `sfnum`, BAR address calculation, table destroy with live devices, and repeated SF enable/disable under lockdep/KASAN. Tracepoints `mlx5_sf_dev_add` and `mlx5_sf_dev_del` should match xarray contents.
