# sources/distributed-fs/ceph-client/drivers/dma/idxd/defaults.c

## Purpose
`defaults.c` applies default configuration for configurable Intel IAA/IAX devices so a kernel crypto work queue can bind without manual setup.

## Important APIs, Types, And Functions
The file defines `idxd_load_iaa_device_defaults()`, which updates WQ 0, group 0, and engine 0.

## Control Flow
If the device is not configurable it exits. Otherwise it requires WQ 0 disabled, makes it dedicated kernel type, assigns full WQ size, priority 10, group 0, name `iaa_crypto`, driver name `crypto`, and assigns engine 0 to group 0.

## State And Persistence Behavior
It mutates in-memory configuration shadows. Hardware is programmed later by `idxd_device_config()`.

## Dependencies And Integration Points
It is referenced by the IAX driver-data entry in `init.c` and prepares binding for crypto users.

## Risks And Test Signals
Only WQ 0 and engine 0 are configured; enabled WQ 0 returns `-EPERM`. Verify IAA probe defaults and crypto driver binding.
