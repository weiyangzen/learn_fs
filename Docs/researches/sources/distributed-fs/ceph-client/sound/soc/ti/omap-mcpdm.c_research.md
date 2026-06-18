<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/ti/omap-mcpdm.c -->
# sources/distributed-fs/ceph-client/sound/soc/ti/omap-mcpdm.c

## Purpose
ASoC CPU DAI driver for OMAP4 McPDM, used primarily with TWL6040/Phoenix codec PDM audio. It handles playback/capture channel masks, FIFO/DMA thresholds, IRQ diagnostics, PM QoS latency, suspend/resume, and downlink offset cancellation.

## APIs, Types, and Functions
`struct omap_mcpdm` stores device/MMIO/IRQ, PM QoS, mutex, per-direction `mcpdm_link_config`, downlink RX offsets, restart flag, suspend runtime-PM active count, and DMA data. Important functions are `omap_mcpdm_open_streams()`, `omap_mcpdm_close_streams()`, `omap_mcpdm_start()`, `omap_mcpdm_stop()`, DAI startup/shutdown/hw_params/prepare/probe/remove, component suspend/resume, exported `omap_mcpdm_configure_dn_offsets()`, and platform probe.

## Control Flow, State, and Persistence
Probe maps `mpu`, uses `dma` resource plus DN/UP data offsets for DMA, gets IRQ, registers the component, and registers sDMA channels `dn_link` and `up_link`. DAI probe enables runtime PM, clears CTRL, requests IRQ, sets default thresholds, and initializes DMA data. Startup opens streams on first active substream, enabling watchdog, IRQs, offsets, thresholds, and DMA. `hw_params` maps 1-5 playback or 1-3 capture channels to PDM link masks, sets peer defaults when the other direction is idle, computes DMA maxburst and latency, and marks restart when channel masks change. Prepare applies PM QoS and starts or restarts hardware. Suspend closes active hardware and records runtime PM references; resume restores them and restarts active streams.

## Dependencies and Integration
Depends on McPDM register macros, runtime PM, IRQs, CPU latency QoS, DMAengine PCM, TI sDMA helper, and ASoC DAI/component APIs. Machine drivers such as ABE/TWL6040 call the exported offset function using TWL6040 trim data.

## Risks and Test Signals
Risks include IRQ requested from DAI probe rather than platform probe, `pm_runtime_get_sync()` ignored, peer link-mask defaults creating implicit stereo channels, restart needed for runtime channel changes, limited rates to 88.2/96 kHz S32_LE, and no explicit trigger op. Test signals are 1-5 channel playback, 1-3 channel capture, duplex startup/shutdown, offset cancellation writes, IRQ logs, suspend/resume with active streams, DMA thresholds/latency, and channel-mask restart behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/ti/omap-mcpdm.c -->
