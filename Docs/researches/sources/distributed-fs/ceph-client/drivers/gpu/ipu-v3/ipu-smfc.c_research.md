# sources/distributed-fs/ceph-client/drivers/gpu/ipu-v3/ipu-smfc.c

## Purpose

`ipu-smfc.c` implements the Sensor Multi-FIFO Controller helper for IPUv3. It configures SMFC channel-to-CSI/MIPI mapping, burst size, FIFO watermarks, module gating, and channel ownership for four SMFC channels feeding capture paths.

## Important APIs, Types, And Functions

Private state is split between `struct ipu_smfc_priv`, which owns the MMIO base, spinlock, IPU pointer, channel array, and module `use_count`, and `struct ipu_smfc`, which tracks a channel number and `inuse` flag. Exported functions are `ipu_smfc_set_burstsize()`, `ipu_smfc_map_channel()`, `ipu_smfc_set_watermark()`, `ipu_smfc_enable()`, `ipu_smfc_disable()`, `ipu_smfc_get()`, and `ipu_smfc_put()`. Lifecycle is `ipu_smfc_init()` and empty `ipu_smfc_exit()`.

## Control Flow

Initialization allocates `ipu_smfc_priv`, stores it in `ipu->smfc_priv`, maps the SMFC register page, initializes the lock, and pre-populates four channel descriptors. Clients call `ipu_smfc_get()` to reserve a channel, configure mapping, burst, and watermarks under the shared spinlock, then call `ipu_smfc_enable()`. The first enable turns on `IPU_CONF_SMFC_EN`; later enables only increment the count. Disable decrements and turns the module off when the count reaches zero.

## State And Persistence Behavior

Software state persists in the devm-managed `ipu_smfc_priv` and per-channel `inuse` flags. `use_count` tracks active users but is not tied to channel ownership. Hardware state persists in `SMFC_MAP`, `SMFC_WMC`, and `SMFC_BS` until reprogrammed. The mapped MMIO region is devm-managed; `ipu_smfc_exit()` performs no explicit cleanup.

## Dependencies And Integration Points

It depends on `ipu-prv.h`, `ipu_module_enable()`, `ipu_module_disable()`, Linux MMIO, export symbols, and spinlocks. Capture drivers integrate through the exported SMFC API to connect CSI/MIPI inputs to IDMAC capture channels.

## Risks And Test Signals

Risks include accepting unchecked burst, watermark, CSI, and MIPI field values, a disable-underflow path that clamps after temporarily going negative, no validation that an enabled channel was reserved, and empty explicit teardown. Test by reserving all four channels, checking `-EBUSY` and `-EINVAL` paths, programming each register field, running concurrent get/put/configure calls, and verifying SMFC module enable/disable balance across multiple capture streams.
