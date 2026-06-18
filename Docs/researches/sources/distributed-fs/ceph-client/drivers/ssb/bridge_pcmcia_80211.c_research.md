# sources/distributed-fs/ceph-client/drivers/ssb/bridge_pcmcia_80211.c

## Purpose
PCMCIA host bridge for Broadcom 43xx wireless cards that expose an SSB bus through a PCMCIA memory window.

## Important APIs, Types, and Functions
Defines `ssb_host_pcmcia_tbl`, `ssb_host_pcmcia_probe`, remove, suspend/resume, and public init/exit helpers `ssb_host_pcmcia_init`/`ssb_host_pcmcia_exit`. Probe allocates `struct ssb_bus`, requests/maps a 16-bit memory window, enables IRQ/device, and calls `ssb_bus_pcmciabus_register`.

## Control Flow
Module init registers the PCMCIA driver. Probe configures `CONF_ENABLE_IRQ`, requests resource window 2 sized to `SSB_CORE_SIZE`, maps page zero, verifies IRQ, enables the PCMCIA device, and registers the SSB bus. Error paths disable the device and free the bus. Remove unregisters the SSB bus, disables PCMCIA, frees memory, and clears `dev->priv`. PM hooks delegate to `ssb_bus_suspend/resume`.

## State and Persistence
State is the allocated `struct ssb_bus` stored in `pcmcia_device->priv` and the active PCMCIA window/device configuration. No persistent storage is touched.

## Dependencies and Integration Points
Depends on PCMCIA core, CIS IDs, SSB PCMCIA host registration, and SSB bus suspend/resume.

## Risks
The probe uses legacy PCMCIA resource window semantics; incorrect window flags, missing IRQ, or failed map/enable prevents bus registration. Suspend/resume assumes `dev->priv` remains valid.

## Test Signals
Matching cards should register an SSB bus and devices; failure logs include both PCMCIA result and SSB error. Suspend/resume should preserve SSB operation and cleanup should release the window without leaks.
