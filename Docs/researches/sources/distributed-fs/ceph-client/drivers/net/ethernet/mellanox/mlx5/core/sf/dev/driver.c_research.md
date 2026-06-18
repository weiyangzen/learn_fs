# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/sf/dev/driver.c

## Purpose

`sf/dev/driver.c` is the auxiliary bus driver for mlx5 subfunction devices. It turns an `mlx5_sf_dev` auxiliary device into a child `mlx5_core_dev`, maps the SF BAR, links peer devlink state to the parent SF devlink port, and runs the normal or lightweight mlx5 probe path.

## Important APIs and Functions

The auxiliary driver callbacks are `mlx5_sf_dev_probe()`, `mlx5_sf_dev_remove()`, and `mlx5_sf_dev_shutdown()`, registered by `mlx5_sf_driver_register()` and unregistered by `mlx5_sf_driver_unregister()`. `mlx5_core_peer_devlink_set()` notifies the parent mdev with `MLX5_DRIVER_EVENT_SF_PEER_DEVLINK` so the parent devlink port can point to the child devlink.

## Control Flow

Probe allocates a devlink/core device, initializes core fields from the parent SF device, marks local eswitch-manager SFs as lightweight, initializes the mlx5 mdev profile, ioremaps the SF BAR segment, sets peer devlink before registration, then calls `mlx5_init_one_light()` for local lightweight SFs or `mlx5_init_one()` for externally managed SFs. On success it initializes VHCA debugfs. Every error path unwinds in reverse.

Remove sets `MLX5_BREAK_FW_WAIT`, drains the health workqueue, runs light or full uninit, unmaps BAR, uninitializes mdev, and frees devlink. Shutdown similarly breaks firmware waits, drains health work, and unloads the device without freeing all probe objects.

## State and Persistence Behavior

The driver stores the child mdev pointer in `sf_dev->mdev`; the child mdev records the parent mdev, auxiliary index, PCI device, BAR address, coredev type `MLX5_COREDEV_SF`, and possibly lightweight mode. Firmware/device state is established by the ordinary mlx5 init path.

## Dependencies and Integration Points

It integrates with the Linux auxiliary bus, mlx5 devlink allocation, mdev init/uninit, health workqueue, ESwitch manager detection, peer devlink notifier in `sf/devlink.c`, and VHCA debugfs.

## Risks and Test Signals

Peer devlink setup must happen before child devlink registration, so notifier failures abort probe. Remove assumes `sf_dev->mdev` is valid after successful probe; partial probe failures must not leave it exposed. Test local lightweight SFs, external full SFs, probe failure at mdev init, ioremap, peer devlink, and init-one stages, plus shutdown during firmware wait.
