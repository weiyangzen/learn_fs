<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/catpt/dsp.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/catpt/dsp.c

## Purpose
Low-level DSP, DMA, power, clock, SRAM power-gating, register-default, and coredump support for the CATPT driver. It bridges Linux DMAEngine/DW DMA with the AudioDSP memory map and programs platform PCI/SHIM controls for D0/D3 and low-power clock transitions.

## APIs, Types, and Functions
Exports `catpt_dma_request_config_chan()`, `catpt_dma_memcpy_todsp()`, `catpt_dma_memcpy_fromdsp()`, `catpt_dmac_probe()`, `catpt_dmac_remove()`, `catpt_dsp_update_srampge()`, `catpt_dsp_stall()`, `lpt_dsp_pll_shutdown()`, `wpt_dsp_pll_shutdown()`, `catpt_dsp_update_lpclock()`, `catpt_dsp_power_down()`, `catpt_dsp_power_up()`, and `catpt_coredump()`. Internal helpers include DMA channel filtering/configuration, `catpt_dma_memcpy()`, SRAM-gate register updates, DSP reset, low-power clock selection, register default writes, and dump-section construction.

## Control Flow, State, and Persistence
DMA requests select a memory-copy channel whose device matches `cdev->dev`, configure 4-byte bus widths and 16-beat bursts, then use demand-mode HMDC bits around synchronous `dmaengine_prep_dma_memcpy()` transfers. SRAM power gating derives active blocks from child resources, inverts hardware ON-as-zero masks, disables core clock gating while changing SRAM gates, and performs a dummy read on newly enabled blocks. Power down resets/stalls the DSP, selects 24 MHz SSP clocks, moves to low-power clock, disables MCLK, restores SHIM/SSP defaults, gates clocks/SRAM, and sets PCI D3hot. Power up reverses that sequence, ungates SRAM, restores defaults/MCLK/high clock, releases reset, and unmasks IPC interrupts. Coredump snapshots firmware hash, IRAM, DRAM, SHIM, SSP, and DMA registers into a structured `dev_coredumpv()` payload.

## Dependencies and Integration
Uses Linux DMAEngine, DW DMA, firmware/coredump APIs, PCI PM bits, PXA SSP register offsets, CATPT register macros, and CATPT resource trees. Called by probe/remove, firmware loader, suspend/resume, stream allocation/free, and IPC core-dump notification handling.

## Risks and Test Signals
Risks include hard-coded DMA engine `CATPT_DMA_DEVID = 1`, address masking with `CATPT_DMA_DSP_ADDR_MASK`, clock-gate/SRAM sequencing sensitivity, unchecked return values in some power paths, dummy-read dependence after SRAM enable, and coredump size/hash parsing assumptions. Test signals are DMA transfer success in firmware load and Dx store/restore, correct SRAM gating when streams and scratch regions are allocated, stable D0/D3 transitions, low-power clock toggling when streams prepare/pause, and usable devcoredump payloads after firmware core-dump request.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/catpt/dsp.c -->
