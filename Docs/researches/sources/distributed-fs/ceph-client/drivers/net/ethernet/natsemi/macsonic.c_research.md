# sources/distributed-fs/ceph-client/drivers/net/ethernet/natsemi/macsonic.c

## Purpose
`macsonic.c` is the Macintosh platform and NuBus glue for the shared DP83932 SONIC Ethernet core. It identifies onboard, comm-slot, DuoDock, Apple, Dayna, and DaynaLink SONIC variants, selects the correct register offset and 16-bit versus 32-bit DMA descriptor layout, obtains a MAC address from PROM or CAM, and binds the shared `sonic.c` netdevice operations to platform and NuBus driver models.

## Important APIs, types, and functions
Key local types are `enum macsonic_type` and the `macsonic_netdev_ops` table. `SONIC_READ()` and `SONIC_WRITE()` are defined before including `sonic.c`, so the shared core uses NuBus word access through `dev->base_addr` and `lp->reg_offset`. `macsonic_open()` requests the primary IRQ and, for onboard A/UX remapping, also `IRQ_NUBUS_9`; `macsonic_close()` unwinds both. `mac_onboard_sonic_probe()` handles built-in and comm-slot probing. `mac_sonic_nubus_probe_board()` handles card-specific register bases, PROM bases, DCR values, DMA bit mode, and IRQ mapping. `mac_sonic_platform_probe()` and `mac_sonic_nubus_probe()` allocate `struct net_device`, initialize `struct sonic_local`, call shared setup, then register the netdev.

## Control flow
Module init registers both platform and NuBus drivers. Platform probe allocates an Ethernet device, stores `lp->device`, sets platform drvdata, performs onboard probing, initializes debug messaging, and registers the netdev. NuBus probe skips PDS/comm-slot cases, scans functional resources for a recognized network card, allocates a netdev, configures the board, and registers it. Open acquires IRQs before delegating to `sonic_open()`. Close delegates to `sonic_close()` before freeing IRQs. Removal unregisters the netdev, frees coherent descriptor memory allocated by `sonic_alloc_descriptors()`, and frees the netdev.

## State and persistence
Persistent hardware state comes from NuBus resources, PROM bytes, CAM contents left by firmware/MacOS, Macintosh model metadata, and the SONIC register set. Runtime state is held in `struct sonic_local`: register offset, DMA bit mode, descriptor memory, DMA addresses, rings, stats, and lock. The driver has no disk persistence. It may randomize the MAC address if PROM and CAM contents are invalid.

## Dependencies and integration points
This file depends on classic Macintosh platform data, NuBus APIs, `hwreg_present()`, VIA interrupt mapping, DMA coherent allocation, and the shared `sonic.h`/`sonic.c` core. It integrates with the kernel netdevice stack via `net_device_ops`, platform driver registration, NuBus driver registration, and standard Ethernet address helpers.

## Risks and edge cases
Register access macros depend on `dev` and `lp` local variable names being in scope when shared `sonic.c` code is compiled into this translation unit. MAC discovery is fragile: PROM bytes may be bit-reversed, absent, or invalid, and CAM fallback only works if earlier firmware initialized it. The onboard probe uses model-specific assumptions and direct hardware presence checks. The dual-IRQ path must remain re-entrant; the shared interrupt handler relies on `lp->lock` for that. Descriptor memory is freed only after successful probe paths allocate it, so cleanup labels must stay aligned with setup order.

## Test signals
Useful signals are successful platform and NuBus probe logs, correct MAC extraction for each supported board family, `register_netdev()` success, interrupt delivery on both onboard IRQ mappings, RX/TX traffic through shared SONIC paths, multicast CAM reload behavior, suspend-free removal, and leak-free failure paths when descriptor allocation or registration fails. Build coverage requires Macintosh/NuBus configurations that compile this file and the included `sonic.c` core.
