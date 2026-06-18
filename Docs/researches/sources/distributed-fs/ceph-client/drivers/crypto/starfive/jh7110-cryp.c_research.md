# sources/distributed-fs/ceph-client/drivers/crypto/starfive/jh7110-cryp.c

## Purpose
This file is the platform and device-lifetime layer for the StarFive JH7110 crypto engine. It probes the hardware, maps registers, enables clocks and reset, requests DMA channels, creates the shared crypto engine, maintains a global list of devices for algorithm transform init, registers AES/hash/RSA algorithms, and tears everything down on remove.

## Important APIs, types, and functions
`struct starfive_dev_list` wraps the global `dev_list` and a spinlock. `starfive_cryp_find_dev()` is exported to sibling algorithm files and returns the first registered device, caching it in the transform context. `side_chan` is a module parameter that enables AES side-channel mitigation and is copied into `cryp->side_chan` at probe. `starfive_dma_init()` requests `tx` and `rx` DMA channels; `starfive_dma_cleanup()` releases them. `starfive_cryp_probe()` and `starfive_cryp_remove()` own platform lifecycle. The OF match table binds `starfive,jh7110-crypto`.

## Control flow
Probe allocates `struct starfive_cryp_dev`, maps the MMIO resource while recording `phys_base`, sets `dma_maxburst`, reads the side-channel parameter, obtains `hclk`, `ahb`, and shared reset control, enables clocks, deasserts reset, adds the device to the global list, requests DMA channels, allocates and starts a one-slot crypto engine, then registers AES, hash, and RSA algorithms in that order. Failure unwinds registered algorithms, engine, DMA channels, list membership, clocks, and reset.

Remove unregisters AES/hash/RSA algorithms, exits the crypto engine, releases DMA channels, removes the device from the global list, disables clocks, and asserts reset.

## State and persistence behavior
Runtime state is entirely in memory. The global device list persists for the module lifetime and allows transform initialization to find hardware after algorithm registration. Each transform caches a `struct starfive_cryp_dev *` once found. No runtime PM is used here, so clocks remain enabled from probe until remove. The side-channel parameter is read at probe and is not dynamically re-applied to existing devices.

## Dependencies and integration points
This file integrates with Linux platform driver infrastructure, OF matching, reset controller, common clock framework, DMAengine channel lookup, crypto engine, and the sibling StarFive AES/hash/RSA modules through register/unregister function calls declared in `jh7110-cryp.h`.

## Risks
The global list selection returns the first device and does not load-balance across multiple JH7110 crypto engines. Clock enable and reset calls are not fully checked after `clk_prepare_enable()` and `reset_control_deassert()`, so failures there could be missed. Algorithm registration is global; if multiple devices were ever supported, duplicate registration would need handling. The engine has queue length 1, making request serialization simple but limiting concurrency.

## Test signals
Probe tests should cover missing MMIO, missing clocks, missing reset, missing `tx`/`rx` DMA channels, engine allocation failure, and partial algorithm registration failure. Remove tests should verify unregister ordering and resource release. Runtime tests should confirm transform init fails with `-ENODEV` before a device is listed and succeeds after probe.
