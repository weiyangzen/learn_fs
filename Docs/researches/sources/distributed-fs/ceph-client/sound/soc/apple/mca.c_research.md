# sources/distributed-fs/ceph-client/sound/soc/apple/mca.c

## Purpose
This is the Apple Silicon MCA ASoC platform driver. MCA hardware is organized as clusters containing clock/sync generation, SERDES units, DMA adapters, and I2S ports. The driver models cluster internals as front-end DAIs and physical I2S ports as back-end DAIs, letting machine-driver DAPM routes dynamically connect FEs to BEs through ASoC DPCM.

## Important APIs, Types, And Functions
Core state is `struct mca_data` and `struct mca_cluster`. Important DAI helpers include `mca_fe_startup()`, `mca_fe_set_tdm_slot()`, `mca_fe_set_fmt()`, `mca_fe_hw_params()`, `mca_fe_trigger()`, `mca_be_startup()`, `mca_be_prepare()`, `mca_be_hw_free()`, and `mca_be_shutdown()`. PCM component callbacks wrap DMAengine via `mca_pcm_open()`, `mca_hw_params()`, `mca_trigger()`, `mca_pointer()`, `mca_pcm_new()`, and `mca_pcm_free()`. Probe dynamically allocates `2 * nclusters` DAI drivers from MMIO resource size, attaches power domains, resets hardware, obtains per-cluster clocks, and registers the component.

## Control Flow
Probe maps cluster and switch resources, counts clusters, attaches global and per-cluster power domains, resets the block, and creates FE/BE DAI descriptors. FE hw_params computes/refines TDM slots, configures SERDES and DMA adapter padding/channel fields, and sets clock rates when the FE clock is idle. BE startup enforces one FE driving a port, programs port clock/data muxes, and records `port_driver`. BE prepare enables the driving FE's clock/power domain before codec unmute or DAPM power-up. PCM trigger calls `mca_fe_early_trigger()` before DMAengine trigger to reset/resync SERDES, and FE trigger then enables/disables SERDES.

## State And Persistence
State is per device and per cluster: port routing, started stream directions, clocks in use, power-domain links, TDM masks/widths, BCLK ratio, and DMA channels. Hardware state includes SERDES configs, slot masks, syncgen periods, MCLK settings, port muxes, and DMA adapter registers. Remove unregisters the component, releases clocks/domains, deletes links, and rearms reset.

## Dependencies And Integration Points
The driver depends on OF resources, OF DMA channel names (`tx%da`, `rx%db` when RXB capture is enabled), clocks indexed by cluster, power domains, reset controls, regmap-like raw MMIO, ASoC DPCM, and DMAengine PCM. Machine drivers provide routes and DAI references to backend ports.

## Risks And Test Signals
Risk areas include dynamic FE/BE ID mapping, one-FE-per-BE enforcement, clock/power ordering, undocumented SERDES bits, RXB-vs-RXA compile-time choice, and DMA channel naming. Test signals are successful probe on Apple DTs, DPCM routing between expected FE/BE pairs, playback/capture in I2S and TDM slot configurations, clean underrun-free DMAengine operation, and suspend/remove paths releasing power-domain links and DMA channels.
