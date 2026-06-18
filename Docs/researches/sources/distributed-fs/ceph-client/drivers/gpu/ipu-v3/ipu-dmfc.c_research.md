# sources/distributed-fs/ceph-client/drivers/gpu/ipu-v3/ipu-dmfc.c

## Purpose
Configures the Display Multi FIFO Controller, which allocates FIFO behavior for IPU display/DP channels and controls wait-for-end-of-transfer behavior.

## Important APIs, Types, and Functions
`struct dmfc_channel_data` maps IPU channel numbers to DMFC register offsets and shift positions. `struct dmfc_channel` stores per-channel mapping and in-use state; `struct ipu_dmfc_priv` stores base MMIO, mutex, IPU pointer, and channel array. Exported APIs are `ipu_dmfc_enable_channel()`, `ipu_dmfc_disable_channel()`, `ipu_dmfc_config_wait4eot()`, `ipu_dmfc_get()/put()`, `ipu_dmfc_init()/exit()`.

## Control Flow
Initialization maps the DMFC register page, initializes the known channel mappings, and writes default FIFO allocation/control values. Display clients get the DMFC channel matching their IPU channel, enable or disable it by setting per-channel bits under the mutex, and may configure wait-for-EOT based on frame width.

## State and Persistence
State is the in-use bit per channel plus DMFC hardware registers. The mutex protects all register read-modify-write operations and allocation state. No disk persistence exists.

## Dependencies and Integration Points
Depends on IPU channel constants from `<video/imx-ipu-v3.h>` and common module lifetime managed by `ipu-common.c`. It integrates with DC/DP/DI display scanout paths by ensuring display channels have appropriate FIFO behavior.

## Risks
Only a fixed set of channel mappings is supported; invalid channel requests fail. Incorrect FIFO defaults or wait4eot thresholds can cause display underflow, tearing, or latency. Because it is shared by display flows, unbalanced get/put or enable/disable affects other clients.

## Test Signals
Display underflow counters, stable scanout under high memory load, channel get failure tests, and register checks after init/enable/disable are relevant. Mode changes across narrow and wide frame widths should exercise wait4eot programming.
