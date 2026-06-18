# sources/distributed-fs/ceph-client/drivers/net/ethernet/natsemi/xtsonic.c

## Purpose
`xtsonic.c` is the Xtensa XT2000 platform wrapper for the shared SONIC Ethernet core. It probes a memory-mapped onboard SONIC controller, validates the silicon revision, reads the MAC address from CAM initialized by firmware, configures 32-bit SONIC operation, allocates shared descriptors, registers netdevice operations, and binds to a platform driver named `xtsonic`.

## Important APIs, types, and functions
`SONIC_READ()` and `SONIC_WRITE()` access 32-bit memory-mapped registers through `dev->base_addr`. `xtsonic_open()` and `xtsonic_close()` wrap IRQ request/free around `sonic_open()` and `sonic_close()`. `sonic_probe1()` performs MMIO region reservation, silicon revision validation against `known_revisions`, reset/DCR setup, MAC extraction, descriptor allocation, and netdev operation setup. `xtsonic_probe()` obtains platform memory and IRQ resources, allocates the netdev, fills `struct sonic_local`, calls `sonic_probe1()`, initializes messages, and registers the netdev. Removal unregisters and frees descriptors, releases the region, and frees the netdev.

## Control flow
The module platform driver calls `xtsonic_probe()`. Probe requires one memory resource and one IRQ resource, then delegates hardware validation to `sonic_probe1()`. Open requests the IRQ first, then starts shared SONIC initialization. Close stops the shared core and frees the IRQ. `sonic.c` is included after the wrapper's register macros, so all common RX/TX/interrupt/statistics logic is compiled into this wrapper.

## State and persistence
Runtime state is stored in `struct sonic_local`: 32-bit DMA mode, descriptor memory, DMA addresses, rings, stats, and lock. Hardware state comes from the platform resources and SONIC CAM. The code declares external XT board NVRAM helpers but does not use them; MAC state is assumed to be in CAM from the bootloader. There is no disk persistence.

## Dependencies and integration points
The file depends on platform device resources, request/release memory regions, IRQ APIs, DMA coherent allocation, Xtensa IO headers, and the shared SONIC core. It integrates with the netdevice stack through `xtsonic_netdev_ops`.

## Risks and edge cases
The code assumes only 32-bit SONIC operation and a known revision of `0x101`. `sonic_probe1()` reserves the memory region before revision validation; the not-found path returns `-ENODEV` without releasing that region, which is a cleanup risk. MAC extraction assumes firmware initialized CAM entry 0. Register access uses volatile pointer arithmetic on `dev->base_addr`, so resource mapping expectations are architecture-specific. `request_mem_region()` uses a hardcoded `0x100`, while removal releases `SONIC_MEM_SIZE`, currently also `0x100`.

## Test signals
Useful tests include platform resource absence paths, successful probe with revision `0x101`, failure probe with unknown revision and region cleanup auditing, IRQ request failure, descriptor allocation failure, register_netdev failure, RX/TX traffic through shared SONIC code, MAC correctness from CAM, and module unload after open/close cycles.
