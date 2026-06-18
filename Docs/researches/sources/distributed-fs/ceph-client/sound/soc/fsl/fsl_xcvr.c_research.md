# sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_xcvr.c

## Purpose
`fsl_xcvr.c` is the NXP Audio Transceiver ASoC DAI driver for S/PDIF, ARC receive, and eARC modes on i.MX8MP/i.MX93/i.MX95-family hardware. It manages the main XCVR register block, optional PHY/PLL access through an AI sideband interface, firmware loading into XCVR RAM, PCM constraints per mode, IEC958 channel status controls, capabilities data, DMA datapath start/stop, IRQ handling, RX reset work, and runtime PM.

## Important APIs, Types, And Functions
The platform driver is `fsl_xcvr_driver`, matched by `fsl_xcvr_dt_ids`. Important types are `struct fsl_xcvr_soc_data`, `enum fsl_xcvr_pll_verison`, and `struct fsl_xcvr`. The ASoC DAI callbacks are in `fsl_xcvr_dai_ops`: `fsl_xcvr_dai_probe`, `fsl_xcvr_prepare`, `fsl_xcvr_startup`, `fsl_xcvr_shutdown`, and `fsl_xcvr_trigger`.

Mode/control functions include `fsl_xcvr_mode_get/put`, `fsl_xcvr_arc_mode_get/put`, `fsl_xcvr_capds_get/put`, `fsl_xcvr_activate_ctl`, `fsl_xcvr_rx_cs_get`, `fsl_xcvr_tx_cs_get/put`, and timestamp controls built with `fsl_utils`. Hardware access helpers include `fsl_xcvr_ai_read/write`, `fsl_xcvr_phy_reg_read/write`, `fsl_xcvr_pll_reg_read/write`, `fsl_xcvr_en_phy_pll`, `fsl_xcvr_en_aud_pll`, `fsl_xcvr_load_firmware`, `irq0_isr`, `reset_rx_work`, `fsl_xcvr_runtime_suspend`, and `fsl_xcvr_runtime_resume`.

## Control Flow
Probe gets IPG, PHY, SPBA, PLL-IPG, and optional PLL-family clocks, constrains SPDIF rates for SPDIF-only SoCs, maps RAM and registers, initializes main and optional PHY/PLL regmaps, gets reset control, requests IRQ0, records FIFO DMA resources, enables runtime PM, puts regmaps into cache-only state, registers DMAEngine PCM and the ASoC component, and initializes reset work and a spinlock.

DAI probe attaches DMA params, sets mode to SPDIF for SPDIF-only hardware, or adds mode/ARC/CAPDS controls for multi-mode hardware, then adds IEC958 playback/capture controls. Startup rejects duplicate same-direction streams, applies EDMA period constraints, applies channel/rate constraints based on current mode, marks the stream active, and disables mode controls while a stream runs. Prepare configures the PHY/PLL and datapath for SPDIF, ARC, or eARC: SPDIF TX sets audio PLL and frame format, SPDIF/ARC RX configures RX datapath and 175 MHz PHY PLL, eARC configures CMDC mode, RX FIFO, and EXT_CTRL mode/reset bits. Trigger uses a spinlock to set datapath reset, start/stop TX data and CMDC TX bits, enable/disable DMA, enable/disable eARC IRQs, and clear reset. Shutdown clears stream state, reenables controls when idle, disables eARC IRQs, clears SPDIF mode as needed, and asserts CMDC reset for eARC.

Runtime resume asserts reset, enables clocks, deasserts reset, syncs regmaps, releases AI reset, syncs PHY/PLL regmaps, loads optional firmware into 10 RAM pages, writes capabilities data, releases the M0+ core, and waits for firmware initialization. Runtime suspend optionally asserts M0+ core reset for eARC, switches regmaps to cache-only, and disables clocks.

The IRQ handler reads external ISR bits, captures new channel-status blocks either from firmware-managed RAM buffers or direct RX CS registers, bit-reverses each 32-bit word, acknowledges received channel status, logs and clears other status bits, and schedules `reset_rx_work` on preamble mismatch errors. The work item temporarily disables DMA read, toggles RX datapath reset, and reenables DMA read under the same spinlock as trigger.

## State And Persistence
`struct fsl_xcvr` holds SoC data, regmaps, clocks, reset, active stream mask, current mode and ARC mode, mapped firmware RAM, DMA params, RX/TX IEC958 status, 256-byte eARC capabilities data, reset work, spinlock, and constrained SPDIF rate storage. Regmap caches persist hardware register intent across runtime PM. Firmware and capabilities data are rewritten to RAM on resume. IEC958 status and CAPDS controls are software state visible through ALSA controls.

## Dependencies And Integration Points
The driver integrates with ALSA ASoC, DMAEngine PCM, regmap MMIO and custom bus regmaps, reset controller, firmware loader, runtime PM, Linux clocks, i.MX PCM helpers, `fsl_utils` PLL/rate/control helpers, and register definitions from `fsl_xcvr.h`.

## Risks And Edge Cases
Mode controls mutate PCM substream availability and are disabled while streams are active; userspace mode changes must therefore be sequenced before opening streams. Firmware size is limited to 16 KiB code RAM and assumes IPG clock is running before `memcpy_toio`. AI sideband accesses poll toggle/done bits and can timeout if PHY/PLL clock or reset state is wrong. PLL configuration supports a fixed table of output frequencies and rejects rates that do not divide them. Trigger and reset work share register bits, making the spinlock important. Channel-status access uses casts to `u32 *` over byte arrays, so alignment and endian/bit-reversal behavior are part of the hardware contract.

## Test Signals
Test probe/runtime resume with and without firmware, SPDIF-only i.MX93 and PHY-backed i.MX8MP/i.MX95 data, all modes where available, playback disable in ARC/eARC modes, rate/channel constraints for SPDIF vs eARC, IEC958 status get/put, CAPDS read/write and firmware RAM copy, suspend/resume with firmware reload, IRQ-driven channel-status updates, preamble-error reset work, and concurrent trigger/IRQ reset races under stress.
