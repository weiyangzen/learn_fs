# sources/distributed-fs/ceph-client/drivers/edac/sifive_edac.c

## Purpose
Registers a small EDAC device for SiFive platform cache/ECC errors delivered by the SiFive ccache notifier. It translates notifier event types into EDAC CE and UE device events.

## Important APIs, Types, And Functions
- `struct sifive_edac_priv` stores the notifier block and EDAC device control pointer.
- `ecc_err_event` maps `SIFIVE_CCACHE_ERR_TYPE_UE` to `edac_device_handle_ue` and `SIFIVE_CCACHE_ERR_TYPE_CE` to `edac_device_handle_ce`.
- `ecc_register` allocates private state and EDAC device state, registers the EDAC device, then registers the ccache notifier.
- `ecc_unregister` reverses notifier and EDAC registration.
- `sifive_edac_init` creates a synthetic platform device and registers the EDAC notifier path.

## Control Flow
Module init creates a simple platform device named `sifive_edac`, calls `ecc_register`, and unregisters the platform device if registration fails. Registration allocates state, creates one EDAC device instance/block, fills names, adds it to EDAC, and subscribes to ccache errors. Notifier callbacks pass the ccache-provided message directly to EDAC. Exit unregisters the notifier, removes the EDAC device, frees control info, and unregisters the platform device.

## State And Persistence
Persistent module state is the global `sifive_pdev`. Per-device state is `sifive_edac_priv`, devm-allocated against the synthetic platform device. Hardware error state is owned by the SiFive ccache subsystem, not this driver.

## Dependencies And Integration Points
Depends on `soc/sifive/sifive_ccache.h` notifier APIs, EDAC device APIs, and platform-device registration. It has no OF match table; it creates its own platform device during module init.

## Risks And Edge Cases
Notifier registration happens after EDAC device registration and must be undone before freeing EDAC state. Unknown event values are ignored but still return `NOTIFY_OK`. Because the platform device is synthetic, module load depends on the ccache notifier symbols being meaningful on the running platform.

## Test Signals
Trigger CE and UE ccache notifier events, unknown event values, EDAC add failure cleanup, module unload ordering, and message propagation into EDAC event text.
