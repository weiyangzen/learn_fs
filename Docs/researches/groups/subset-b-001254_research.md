# subset-b-001254 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/dw/regs.h -->
## sources/distributed-fs/ceph-client/drivers/dma/dw/regs.h

### Purpose
`regs.h` is the shared private register, descriptor, and state definition header for the Synopsys DesignWare AHB DMA driver family. It describes the classic DW DMA register map, iDMA32 extensions, linked-list item layout, channel state, and engine-level callbacks used by the implementation files under `drivers/dma/dw/`.

### Important APIs, Types, And Functions
The main hardware-facing types are `struct dw_dma_chan_regs`, `struct dw_dma_irq_regs`, `struct dw_dma_regs`, and `struct dw_lli`. Driver state is represented by `struct dw_dma_chan`, `struct dw_dma`, and `struct dw_desc`. Important enums and flags include `enum dw_dma_fc`, `enum dw_dma_msize`, `enum idma32_msize`, and `enum dw_dmac_flags`. The header also provides access helpers such as `channel_readl()`, `channel_writel()`, `dma_readl()`, `dma_writel()`, `idma32_readq()`, `idma32_writeq()`, `channel_set_bit()`, `channel_clear_bit()`, `to_dw_dma_chan()`, `to_dw_dma()`, and `txd_to_dw_desc()`.

### Control Flow, State, And Persistence
The header itself has no runtime control flow, but it defines how runtime code persists DMA state in memory. A `dw_dma` owns the DMAengine device, MMIO base, descriptor pool, tasklet, channel array, platform data, and variant callbacks for channel initialization, suspend/resume, CTL encoding, block-size conversion, device naming, and global enable/disable. Each `dw_dma_chan` tracks active and queued descriptors under a spinlock, soft-LLP state, slave configuration, burst and block limits, and bit flags for cyclic, paused, initialized, or software-linked-list operation. `struct dw_desc` places the hardware LLI first so descriptors can be DMA-visible while still carrying Linux DMAengine bookkeeping.

### Dependencies, Integration Points, Risks, And Test Signals
This header depends on Linux DMAengine types, interrupt/tasklet infrastructure, MMIO accessors, endian conversion, nonatomic 64-bit IO helpers, and local DW platform definitions in `internal.h`. It integrates with platform-specific DesignWare DMA implementations and iDMA32 variants through callback fields and register-layout macros. Risks are mostly ABI-like: bitfield shifts must match silicon manuals, `DW_REG()` padding assumes the controller's register spacing, and descriptor layout/endian conversions must stay compatible with hardware linked-list fetches. Test signals include successful probing across classic DW and iDMA32 controllers, memcpy/slave/cyclic transfers, linked-list chaining, pause/resume, residue reporting, and interrupt mask/clear behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/dw/regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/dw/rzn1-dmamux.c -->
## sources/distributed-fs/ceph-client/drivers/dma/dw/rzn1-dmamux.c

### Purpose
`rzn1-dmamux.c` implements the Renesas RZ/N1 DMA router that maps device-tree DMA requests through the SoC system-controller DMAMUX into one of the supported DesignWare DMA masters. It lets client DMA specifiers select a request line and mux value while the DMA router framework rewrites the phandle target to the underlying DMAC.

### Important APIs, Types, And Functions
Important state is `struct rzn1_dmamux_data`, which embeds `struct dma_router` and a bitmap of allocated mux request lines, and `struct rzn1_dmamux_map`, which remembers the request index for release. Key functions are `rzn1_dmamux_probe()`, `rzn1_dmamux_route_allocate()`, and `rzn1_dmamux_free()`. The driver registers through `of_dma_router_register()` and uses `r9a06g032_sysctrl_set_dmamux()` to program mux bits.

### Control Flow, State, And Persistence
Probe validates that the first `dma-masters` phandle is a supported `"renesas,rzn1-dma"` node, initializes the router, and registers an OF DMA router callback. Allocation requires a six-cell DMA specifier, consumes the last two cells as mux request index and value, validates the channel/request relationship, switches `dma_spec->np` to DMAC0 or DMAC1, marks the request line busy in `used_chans`, and programs the sysctrl mux bit. Release clears the allocation bitmap and frees the route data. Runtime state is held only in the device driver data and the sysctrl DMAMUX register state.

### Dependencies, Integration Points, Risks, And Test Signals
The file depends on OF DMA router APIs, platform devices, device-tree `dma-masters`, and the RZ/N1 sysctrl driver. It integrates with DesignWare DMA by retargeting the DMA specifier to a DMAC node before normal DMA channel lookup. Risks include invalid device-tree cell counts, leaking OF node references on error paths, double allocation of mux lines, mismatched `req_idx % 16` validation, and global sysctrl state that must match the bitmap. Test signals include two-DMAC routing, busy-line rejection, invalid channel/request handling, route release and reallocation, and functional peripheral DMA after mux programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/dw/rzn1-dmamux.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/ep93xx_dma.c -->
## sources/distributed-fs/ceph-client/drivers/dma/ep93xx_dma.c

### Purpose
`ep93xx_dma.c` is the DMAengine driver for Cirrus Logic EP93xx DMA controllers. It supports memory-to-peripheral M2P channels for fixed peripheral request lines, memory-to-memory M2M channels for memcpy and selected peripheral modes, scatter-gather through software descriptor chaining, and cyclic audio-style transfers.

### Important APIs, Types, And Functions
Core types are `struct ep93xx_dma_desc`, `struct ep93xx_dma_chan_cfg`, `struct ep93xx_dma_chan`, and `struct ep93xx_dma_engine`. Hardware abstraction callbacks in `struct ep93xx_dma_engine` split M2P and M2M operations: `m2p_hw_setup()`, `m2p_hw_submit()`, `m2p_hw_interrupt()`, `m2p_hw_synchronize()`, `m2p_hw_shutdown()`, `m2m_hw_setup()`, `m2m_hw_submit()`, `m2m_hw_interrupt()`, and `m2m_hw_shutdown()`. DMAengine entry points include `ep93xx_dma_alloc_chan_resources()`, `ep93xx_dma_free_chan_resources()`, `ep93xx_dma_prep_dma_memcpy()`, `ep93xx_dma_prep_slave_sg()`, `ep93xx_dma_prep_dma_cyclic()`, `ep93xx_dma_tx_submit()`, `ep93xx_dma_issue_pending()`, `ep93xx_dma_terminate_all()`, `ep93xx_dma_synchronize()`, and `ep93xx_dma_tx_status()`.

### Control Flow, State, And Persistence
Probe creates either an M2P engine with ten channels or an M2M engine with two channels, maps each per-channel register region, obtains per-channel IRQs and clocks, initializes descriptor queues, registers the DMAengine device, and registers OF DMA translation callbacks. Channel resource allocation enables the clock, requests the IRQ, initializes hardware, and preallocates up to 32 software descriptors. Prepared transfers split data into hardware-sized pieces, chain them via `tx_list`, and mark the first descriptor with a pending cookie. Submit either starts immediately when the active list is empty or queues the chain. Interrupts advance the active list according to the controller's double-buffer state, then tasklets complete cookies, invoke callbacks, recycle descriptors, and start queued work.

### Dependencies, Integration Points, Risks, And Test Signals
The driver depends on DMAengine, OF DMA, platform resources, per-channel clocks, IRQs, scatterlist DMA mappings, and legacy EP93xx channel numbering. M2P channels have fixed directions based on channel parity, while M2M channels accept runtime slave configuration for SSP/IDE or memcpy. Risks include double-buffer state-machine quirks, M2M DONE interrupts that can arrive before the channel is actually idle, cyclic descriptors that intentionally never complete cookies, maximum segment limits of `0xffff`, `BUG_ON()` assumptions during resource release, and untested IDE mode parameters. Test signals include M2P TX/RX direction filtering, M2M memcpy, SSP slave transfers with width config, cyclic callbacks, terminate/synchronize behavior, descriptor exhaustion, OF xlate rejection paths, and handling of error or spurious interrupts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/ep93xx_dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/fsl-dpaa2-qdma/Kconfig -->
## sources/distributed-fs/ceph-client/drivers/dma/fsl-dpaa2-qdma/Kconfig

### Purpose
This Kconfig entry exposes the NXP DPAA2 QDMA driver as `CONFIG_FSL_DPAA2_QDMA`. It restricts the driver to ARM64 systems with the Freescale Management Complex bus and DPIO services, and it selects the DMAengine and virtual-channel support needed by the implementation.

### Important APIs, Types, And Functions
The single symbol is `FSL_DPAA2_QDMA`, a tristate menuconfig labeled `"NXP DPAA2 QDMA"`. It depends on `ARM64`, `FSL_MC_BUS`, and `FSL_MC_DPIO`, and selects `DMA_ENGINE` plus `DMA_VIRTUAL_CHANNELS`.

### Control Flow, State, And Persistence
There is no runtime state. Build-time selection controls whether `dpaa2-qdma.o` and `dpdmai.o` are compiled and whether the DPAA2 QDMA MC-bus driver can register at late init.

### Dependencies, Integration Points, Risks, And Test Signals
The entry integrates the driver with the kernel configuration system and prevents builds without MC bus or DPIO notification APIs. Risks are mostly configuration drift: missing dependencies would produce link errors, while overly narrow dependencies would hide the driver from valid platforms. Test signals include allmodconfig/allyesconfig coverage on ARM64, disabled dependency builds, module and built-in builds, and successful selection of virtual DMA channel helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/fsl-dpaa2-qdma/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/fsl-dpaa2-qdma/Makefile -->
## sources/distributed-fs/ceph-client/drivers/dma/fsl-dpaa2-qdma/Makefile

### Purpose
The Makefile wires the DPAA2 QDMA driver into kbuild. When `CONFIG_FSL_DPAA2_QDMA` is enabled, it builds both the DMAengine driver and the DPDMAI Management Complex command wrapper.

### Important APIs, Types, And Functions
The only build rule is `obj-$(CONFIG_FSL_DPAA2_QDMA) += dpaa2-qdma.o dpdmai.o`.

### Control Flow, State, And Persistence
There is no runtime behavior. The object list ensures `dpaa2-qdma.c` can call the exported DPDMAI functions in `dpdmai.c` within the same built-in or module unit.

### Dependencies, Integration Points, Risks, And Test Signals
This file must stay aligned with the Kconfig symbol and source filenames. Risks include omitting `dpdmai.o`, which would break MC command symbols, or renaming files without updating kbuild. Test signals are module link success, built-in link success, and `modinfo` showing the DPAA2 QDMA module when built as `m`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/fsl-dpaa2-qdma/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/fsl-dpaa2-qdma/dpaa2-qdma.c -->
## sources/distributed-fs/ceph-client/drivers/dma/fsl-dpaa2-qdma/dpaa2-qdma.c

### Purpose
`dpaa2-qdma.c` implements the DMAengine driver for NXP Layerscape DPAA2 QDMA, using DPDMAI objects on the Freescale Management Complex bus and DPIO queue notifications. It primarily exposes DMA memcpy capability through DPAA2 frame descriptors, frame lists, and source/destination descriptors.

### Important APIs, Types, And Functions
Key DMAengine operations are `dpaa2_qdma_alloc_chan_resources()`, `dpaa2_qdma_free_chan_resources()`, `dpaa2_qdma_prep_memcpy()`, and `dpaa2_qdma_issue_pending()`. Descriptor helpers include `dpaa2_qdma_request_desc()`, `dpaa2_qdma_populate_fd()`, `dpaa2_qdma_populate_first_framel()`, `dpaa2_qdma_populate_frames()`, `dpaa2_qdma_free_desc()`, and `dpaa2_dpdmai_free_comp()`. Device setup and teardown are handled by `dpaa2_qdma_probe()`, `dpaa2_qdma_setup()`, `dpaa2_qdma_dpio_setup()`, `dpaa2_dpdmai_bind()`, `dpaa2_qdma_fqdan_cb()`, `dpaa2_qdma_remove()`, and `dpaa2_qdma_shutdown()`.

### Control Flow, State, And Persistence
Probe allocates private state, detects whether an IOMMU domain is present to decide BMT handling, allocates an MC portal, opens and validates the DPDMAI object, fetches RX/TX FQIDs, registers DPIO notification contexts and stores, binds RX queues to DPIO destinations, enables the DPDMAI, creates eight virtual DMA channels, and registers the DMAengine device. Per channel resource allocation creates DMA pools for frame descriptors, frame lists, and source/destination descriptors. A memcpy prepare path allocates or reuses a completion object, fills a frame descriptor pointing at a three-entry frame list, and returns a virtual DMA descriptor. Issue-pending removes the next virtual descriptor, places it on `comp_used`, and enqueues the frame descriptor to the TX FQID. FQDAN callbacks pull response frames, match completions by frame-list address, complete cookies, and rearm notifications.

### Dependencies, Integration Points, Risks, And Test Signals
The driver depends on `virt-dma`, DPDMAI MC commands, DPIO enqueue/pull/rearm services, DPAA2 frame descriptor helpers, DMA pools, IOMMU domain detection, and SoC matching for the LX2160 write-transaction workaround. Integration points include the MC bus object type `"dpdmai"`, DPIO notification routing, DMAengine clients, and shutdown-time DPDMAI destroy. Risks include global `smmu_disable` shared across devices, completion matching by descriptor address, queue-lock and vchan-lock ordering, missing cleanup of in-flight hardware work during remove, version checks that reject newer minor revisions, and error enqueue paths that silently recycle descriptors without completing cookies. Test signals include MC probe deferral, DPDMAI version mismatch handling, IOMMU and no-IOMMU operation, memcpy completion callbacks, queue errors in FD status, descriptor reuse, remove/shutdown paths, and LX2160 coherent-write fixup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/fsl-dpaa2-qdma/dpaa2-qdma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/fsl-dpaa2-qdma/dpaa2-qdma.h -->
## sources/distributed-fs/ceph-client/drivers/dma/fsl-dpaa2-qdma/dpaa2-qdma.h

### Purpose
`dpaa2-qdma.h` defines the private data structures, descriptor command bits, pool sizing, and helper prototypes shared by the DPAA2 QDMA driver. It captures how Linux virtual DMA channels map to DPAA2 DPDMAI queues and how command/frame-list buffers are tracked.

### Important APIs, Types, And Functions
Important types are `struct dpaa2_qdma_sd_d`, `struct dpaa2_qdma_chan`, `struct dpaa2_qdma_comp`, `struct dpaa2_qdma_engine`, `struct dpaa2_qdma_priv`, and `struct dpaa2_qdma_priv_per_prio`. It defines `NUM_CH`, `DPAA2_QDMA_STORE_SIZE`, coherent read/write command encodings, QMan frame descriptor flags, frame-list flags, `FD_POOL_SIZE`, and the `soc_fixup_tuning` table for LX2160A. Static prototypes declare component/channel cleanup helpers used across the C file.

### Control Flow, State, And Persistence
The header has no executable control flow, but it defines persistent runtime ownership. `dpaa2_qdma_priv` owns MC/DPIO resources, queue attributes, the DPDMAI handle context, and per-priority notification stores. `dpaa2_qdma_engine` owns the DMAengine device and fixed channel array. Each channel owns DMA pools plus used/free completion lists, while each completion object owns one frame descriptor, one frame-list block, one source/destination descriptor block, DMA addresses, and the virtual descriptor.

### Dependencies, Integration Points, Risks, And Test Signals
The definitions depend on DPAA2 frame descriptor types, DPDMAI attributes, DMA pools, `virt_dma_chan`, Management Complex devices, IOMMU domains, and SoC device matching. Risks include packed bitfield layout assumptions in `struct dpaa2_qdma_sd_d`, fixed eight-channel scaling, typo-prone hardware flag names, and the header-local static SoC table being included only by the implementation. Test signals include descriptor layout validation on hardware, channel-to-FQID assignment for multiple priorities, DMA pool alignment, and LX2160A command selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/fsl-dpaa2-qdma/dpaa2-qdma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/fsl-dpaa2-qdma/dpdmai.c -->
## sources/distributed-fs/ceph-client/drivers/dma/fsl-dpaa2-qdma/dpdmai.c

### Purpose
`dpdmai.c` is a thin Management Complex command wrapper for DPAA2 Data Path DMA Interface objects. It opens, closes, enables, disables, resets, destroys, queries attributes, and configures or queries DPDMAI RX/TX queues for the QDMA driver.

### Important APIs, Types, And Functions
Exported APIs are `dpdmai_open()`, `dpdmai_close()`, `dpdmai_destroy()`, `dpdmai_enable()`, `dpdmai_disable()`, `dpdmai_reset()`, `dpdmai_get_attributes()`, `dpdmai_set_rx_queue()`, `dpdmai_get_rx_queue()`, and `dpdmai_get_tx_queue()`. Internal packed command/response layouts include `struct dpdmai_cmd_open`, `struct dpdmai_cmd_destroy`, `struct dpdmai_rsp_get_attributes`, `struct dpdmai_cmd_queue`, and `struct dpdmai_rsp_get_tx_queue`.

### Control Flow, State, And Persistence
Each function creates a zeroed `struct fsl_mc_command`, encodes the command header with the relevant command ID and token, writes little-endian command parameters into `cmd.params`, calls `mc_send_command()`, and decodes returned parameters on success. `dpdmai_open()` returns the MC token stored in the response header; all later calls use that token to authenticate the DPDMAI session. Queue setters pass destination type, destination ID, priority, user context, options, queue index, and priority selection to the MC firmware. Queue getters decode FQIDs and destination attributes for use by enqueue/dequeue paths.

### Dependencies, Integration Points, Risks, And Test Signals
The file depends on `linux/fsl/mc.h`, MC command header helpers, endian conversion, and public structures from `dpdmai.h`. It integrates directly with `dpaa2-qdma.c` probe, bind, enable, notification routing, reset, and shutdown. Risks include packed layout drift against MC firmware ABI, incorrect queue/priority union use, versioned command IDs for queue operations, and `DEST_TYPE_MASK` truncation if firmware expands destination encoding. Test signals include MC command success/failure injection, token lifecycle, attribute version decoding, RX queue destination programming, TX/RX FQID retrieval, and endian correctness on big- and little-endian builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/fsl-dpaa2-qdma/dpdmai.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/fsl-dpaa2-qdma/dpdmai.h -->
## sources/distributed-fs/ceph-client/drivers/dma/fsl-dpaa2-qdma/dpdmai.h

### Purpose
`dpdmai.h` defines the DPDMAI Management Complex ABI constants and public data structures used by the DPAA2 QDMA driver and `dpdmai.c` command wrapper.

### Important APIs, Types, And Functions
It defines supported DPDMAI version `3.3`, command ID formatting helpers, command IDs, maximum queue and priority counts, queue option bits, and MC command token bit positions. Main types are `struct dpdmai_cfg`, `struct dpdmai_attr`, `enum dpdmai_dest`, `struct dpdmai_dest_cfg`, `struct dpdmai_rx_queue_cfg`, `struct dpdmai_rx_queue_attr`, and `struct dpdmai_tx_queue_attr`. It declares all DPDMAI control and queue APIs implemented in `dpdmai.c`.

### Control Flow, State, And Persistence
The header has no runtime control flow. It establishes the firmware contract used to open a token-bound DPDMAI control session, read immutable object attributes, and configure queue state in MC firmware. Queue attributes persist in the DPDMAI object rather than in the Linux wrapper.

### Dependencies, Integration Points, Risks, And Test Signals
This file depends on FSL MC IO types and fixed-width kernel integer types. It integrates with MC firmware, DPAA2 QDMA setup, DPIO destination programming, and FQID discovery. Risks are firmware ABI mismatch, command-version skew for queue commands, stale supported version constants, and assuming no more than eight queues or two priorities. Test signals include compile coverage for callers, successful DPDMAI open/get-attributes across firmware versions, queue option combinations, and FQID consistency with DPIO notifications.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/fsl-dpaa2-qdma/dpdmai.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/fsl-edma-common.c -->
## sources/distributed-fs/ceph-client/drivers/dma/fsl-edma-common.c

### Purpose
`fsl-edma-common.c` contains shared DMAengine operations and transfer-control-descriptor handling for Freescale/NXP eDMA variants. It prepares cyclic, slave scatter-gather, and memcpy transfers, manages TCD pools, handles virtual-channel completion, controls request enable/disable, configures DMAMUX slots, computes residue, and provides common resource cleanup.

### Important APIs, Types, And Functions
Important exported-to-driver functions include `fsl_edma_tx_chan_handler()`, `fsl_edma_disable_request()`, `fsl_edma_chan_mux()`, `fsl_edma_free_desc()`, `fsl_edma_terminate_all()`, `fsl_edma_pause()`, `fsl_edma_resume()`, `fsl_edma_slave_config()`, `fsl_edma_tx_status()`, `fsl_edma_prep_dma_cyclic()`, `fsl_edma_prep_slave_sg()`, `fsl_edma_prep_memcpy()`, `fsl_edma_xfer_desc()`, `fsl_edma_issue_pending()`, `fsl_edma_alloc_chan_resources()`, `fsl_edma_free_chan_resources()`, `fsl_edma_cleanup_vchan()`, and `fsl_edma_setup_regs()`. Core helpers include `fsl_edma_enable_request()`, `fsl_edma3_enable_request()`, `fsl_edma_fill_tcd()`, `fsl_edma_set_tcd_regs()`, `fsl_edma_alloc_desc()`, and `fsl_edma_desc_residue()`.

### Control Flow, State, And Persistence
Prepared transfers allocate a flexible `struct fsl_edma_desc` plus one DMA-pool TCD per segment or period. TCDs are filled in little-endian memory format for hardware scatter-gather, then copied into endian-aware MMIO registers when a descriptor is started. `fsl_edma_issue_pending()` refuses submission while suspended, otherwise starts the next virtual descriptor when no descriptor is active. TX IRQ handling calls `fsl_edma_tx_chan_handler()`, which completes non-cyclic descriptors or invokes cyclic callbacks, then starts the next descriptor. Terminate/pause/resume disable or re-enable hardware requests under the vchan lock. Slave peripheral resources are mapped with `dma_map_resource()` and cached until configuration changes or resources are freed.

### Dependencies, Integration Points, Risks, And Test Signals
The file depends on `virt-dma`, DMA pools, DMA mapping, runtime PM, clocks, endian-aware accessors and tracepoints from `fsl-edma-common.h`, and variant flags supplied by `fsl-edma-main.c`. Integration points include DMAMUX programming, eDMA v2/v3/v4 split-register layouts, 32-bit and 64-bit TCD formats, power domains, and DMAengine clients. Risks include TCD endian/layout mistakes, 64-bit address residue reads racing with non-atomic MMIO, minor-loop offset programming for multi-FIFO or port windows, pause/terminate races with IRQ completion, and mismatched `dma_map_resource()` direction naming. Test signals include cyclic audio transfers, SG chains, memcpy with alignment constraints, residue during in-progress transfers, suspend refusal, pause/resume, resource-free unmapping, DMAMUX enable/disable, TCD64 operation, and dynamic tracepoint output for TCD fills.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/fsl-edma-common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/fsl-edma-common.h -->
## sources/distributed-fs/ceph-client/drivers/dma/fsl-edma-common.h

### Purpose
`fsl-edma-common.h` is the shared private interface for the Freescale/NXP eDMA driver. It defines register bits, TCD layouts, channel and engine state, variant capability flags, endian-aware MMIO helpers, TCD access macros, and prototypes implemented by `fsl-edma-common.c`.

### Important APIs, Types, And Functions
Important hardware types are `struct fsl_edma_hw_tcd`, `struct fsl_edma_hw_tcd64`, `struct fsl_edma3_ch_reg`, and `struct edma_regs`. Runtime state is in `struct fsl_edma_chan`, `struct fsl_edma_desc`, `struct fsl_edma_drvdata`, and `struct fsl_edma_engine`. Variant flags include `FSL_EDMA_DRV_SPLIT_REG`, `FSL_EDMA_DRV_EDMA64`, `FSL_EDMA_DRV_HAS_PD`, `FSL_EDMA_DRV_HAS_CHCLK`, `FSL_EDMA_DRV_HAS_CHMUX`, `FSL_EDMA_DRV_TCD64`, and grouped `FSL_EDMA_DRV_EDMA3`/`FSL_EDMA_DRV_EDMA4`. Inline helpers include `edma_readl()`, `edma_writel()`, `edma_readw()`, `edma_writew()`, `edma_readq()`, `edma_writeq()`, `to_fsl_edma_chan()`, `to_fsl_edma_desc()`, and TCD field read/write/copy macros.

### Control Flow, State, And Persistence
The header has no standalone runtime flow, but its macros determine how common code reads and writes both memory TCDs and MMIO TCD registers. It preserves per-channel state such as active descriptor, DMA slave config, mapped peripheral resource, source ID, IRQ names, power-domain devices, channel clocks, priority, hardware channel ID, direction flags, and multi-FIFO/remote flags. The engine persists global MMIO bases, DMAMUX bases and clocks, a variant data pointer, channel masks, endianness, and the flexible channel array.

### Dependencies, Integration Points, Risks, And Test Signals
The header depends on DMAengine, platform-device, virt-dma, tracepoint infrastructure, endian conversion, and MMIO accessors. It integrates the main platform driver, common transfer code, and trace definitions. Risks include complex `_Generic` TCD macros that must compile for both 32- and 64-bit TCD structures, big-endian 8/16-bit register offset swizzling, variant flag combinations that imply different register layouts, and duplicate bus-width bits. Test signals include builds for all compatible variants, sparse/endian warnings, tracepoint compilation through `CREATE_TRACE_POINTS`, 64-bit TCD access, big-endian IO, and masked-channel probing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/fsl-edma-common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/fsl-edma-main.c -->
## sources/distributed-fs/ceph-client/drivers/dma/fsl-edma-main.c

### Purpose
`fsl-edma-main.c` is the platform driver for Freescale/NXP eDMA controllers across Vybrid, Layerscape, i.MX, and S32G variants. It handles device-tree matching, resource mapping, clocks, DMAMUX resources, channel creation, IRQ topology, power domains, OF DMA translation, DMAengine registration, and system suspend/resume.

### Important APIs, Types, And Functions
Probe and lifecycle functions are `fsl_edma_probe()`, `fsl_edma_remove()`, `fsl_edma_init()`, and `fsl_edma_exit()`. IRQ paths include `fsl_edma_tx_handler()`, `fsl_edma_err_handler()`, `fsl_edma_irq_handler()`, `fsl_edma2_tx_handler()`, `fsl_edma3_tx_handler()`, `fsl_edma3_err_handler_per_chan()`, `fsl_edma3_err_handler_shared()`, `fsl_edma3_or_tx_handler()`, and `fsl_edma3_or_err_handler()`. OF translation is done by `fsl_edma_xlate()` and `fsl_edma3_xlate()`. Variant-specific IRQ setup is selected through `struct fsl_edma_drvdata` entries such as `vf610_data`, `ls1028a_data`, `imx7ulp_data`, `imx8qm_data`, `imx8ulp_data`, `imx93_data3`, `imx93_data4`, `imx95_data5`, and `s32g2_data`.

### Control Flow, State, And Persistence
Probe reads `dma-channels`, allocates a flexible engine object, maps the controller, initializes register pointers for non-split layouts, enables block and DMAMUX clocks, reads optional channel masks and endianness, attaches per-channel power domains when needed, creates each unmasked virtual channel, computes channel TCD and mux addresses, clears initial CSR state, initializes IRQ routing through the variant callback, registers DMAengine operations from the common layer, registers the OF DMA controller, and enables round-robin arbitration on older layouts. OF translation assigns source IDs, channel priority, RX/remote/multi-FIFO flags, and DMAMUX routing while avoiding duplicate source IDs. Suspend late disables active channels and marks them suspended; resume early restores channel state, remuxes source IDs, and re-enables arbitration.

### Dependencies, Integration Points, Risks, And Test Signals
The file depends on device tree properties, platform IRQ/resource APIs, clocks, runtime PM domains, device links, DMAengine registration, OF DMA controller registration, and common eDMA operations. Integration points include many SoC compatible strings, DMAMUX resources, split and non-split eDMA register layouts, shared or per-channel IRQs, and client DMA specifier formats. Risks include variant flag mismatch, channel-mask bit handling above 32 channels, source-ID uniqueness false positives, missing optional error IRQs, autosuspend and device-link ordering, IRQ registration cleanup, and suspend while clients still have in-flight transfers. Test signals include probe for each compatible, masked-channel configurations, all IRQ topologies, OF xlate argument validation, duplicate srcid rejection, per-channel clocks, power-domain attach/detach, suspend/resume with idle and active channels, and memcpy/slave/cyclic operation through the common layer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/fsl-edma-main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/fsl-edma-trace.c -->
## sources/distributed-fs/ceph-client/drivers/dma/fsl-edma-trace.c

### Purpose
`fsl-edma-trace.c` instantiates the fsl-edma tracepoints declared in `fsl-edma-trace.h`. It is intentionally minimal and exists so tracepoint storage and registration are emitted exactly once.

### Important APIs, Types, And Functions
The file defines `CREATE_TRACE_POINTS` and includes `fsl-edma-common.h`, which in turn includes `fsl-edma-trace.h`. It does not define ordinary functions or runtime data structures itself.

### Control Flow, State, And Persistence
There is no direct control flow. At build and module load time, the tracepoint definitions become available to ftrace/perf tooling. Runtime trace state is managed by the kernel tracepoint subsystem, not by this file.

### Dependencies, Integration Points, Risks, And Test Signals
The file depends on the include ordering between `fsl-edma-common.h` and `fsl-edma-trace.h`. It integrates with the eDMA MMIO helpers and TCD fill helper that call `trace_edma_*` functions. Risks are build failures if trace definitions require types not visible through `fsl-edma-common.h`, or duplicate tracepoint instantiation if another file defines `CREATE_TRACE_POINTS`. Test signals include successful build with tracing enabled, presence of `fsl_edma:*` events in tracefs, and no duplicate symbol errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/fsl-edma-trace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/fsl-edma-trace.h -->
## sources/distributed-fs/ceph-client/drivers/dma/fsl-edma-trace.h

### Purpose
`fsl-edma-trace.h` declares trace events for Freescale/NXP eDMA register IO and TCD construction. These events make low-level DMA programming visible through Linux tracing without changing normal driver behavior.

### Important APIs, Types, And Functions
The header declares event class `edma_log_io` and events `edma_readl`, `edma_writel`, `edma_readw`, `edma_writew`, `edma_readb`, and `edma_writeb`. It also declares event class `edma_log_tcd` and event `edma_fill_tcd`. Trace payloads include the eDMA engine pointer, register address, value, or decoded TCD fields such as source/destination addresses, offsets, attributes, nbytes, citer/biter, scatter-gather address, and CSR.

### Control Flow, State, And Persistence
When enabled by the tracepoint subsystem, calls from the eDMA MMIO accessors and TCD fill helper record register offsets relative to `membase` and TCD field snapshots. The header uses standard trace header guards plus `TRACE_HEADER_MULTI_READ`, and sets `TRACE_INCLUDE_PATH`/`TRACE_INCLUDE_FILE` so `trace/define_trace.h` can generate definitions from `fsl-edma-trace.c`.

### Dependencies, Integration Points, Risks, And Test Signals
The trace events depend on `struct fsl_edma_engine`, `struct fsl_edma_chan`, and TCD helper macros from `fsl-edma-common.h`, which is why the include relationship is tightly coupled. Integration points are the inline IO helpers and `fsl_edma_fill_tcd()`. Risks include pointer arithmetic on `void __iomem *` for offset printing, trace macros evaluating TCD helper logic for both TCD32 and TCD64, and excessive trace volume during high-throughput DMA. Test signals include enabling individual trace events, verifying decoded offsets and TCD fields, building with tracing disabled/enabled, and capturing IO sequences around a known transfer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/fsl-edma-trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/fsl-qdma.c -->
## sources/distributed-fs/ceph-client/drivers/dma/fsl-qdma.c

### Purpose
`fsl-qdma.c` implements the DMAengine driver for the older NXP/Freescale Layerscape Queue DMA controller, currently matching `"fsl,ls1021a-qdma"`. It exposes memcpy through command queues, status queues, compound command descriptors, and source/destination descriptor buffers.

### Important APIs, Types, And Functions
Key types are `struct fsl_qdma_format`, `struct fsl_pre_status`, `struct fsl_qdma_chan`, `struct fsl_qdma_queue`, `struct fsl_qdma_comp`, and `struct fsl_qdma_engine`. Main functions are `fsl_qdma_probe()`, `fsl_qdma_reg_init()`, `fsl_qdma_halt()`, `fsl_qdma_irq_init()`, `fsl_qdma_prep_memcpy()`, `fsl_qdma_issue_pending()`, `fsl_qdma_enqueue_desc()`, `fsl_qdma_queue_handler()`, `fsl_qdma_queue_transfer_complete()`, `fsl_qdma_error_handler()`, `fsl_qdma_alloc_chan_resources()`, `fsl_qdma_free_chan_resources()`, `fsl_qdma_terminate_all()`, `fsl_qdma_synchronize()`, and `fsl_qdma_remove()`. Inline helpers encode and decode 40-bit descriptor addresses, queue IDs, offsets, status bits, format bits, and S/G lengths.

### Control Flow, State, And Persistence
Probe reads channel, queue, block, status-size, and queue-size device-tree properties, limits blocks to online CPUs, allocates coherent command/status rings, maps controller/status/block register windows, initializes queue state, assigns channels round-robin across queues and blocks, initializes hardware registers, requests error and queue IRQs, sets a 40-bit DMA mask, and registers the DMAengine device. Channel resource allocation creates DMA pools for command and descriptor buffers and preallocates queue completion objects. A memcpy prepare path fills a compound descriptor with a frame descriptor, source/destination S/G entries, and source/destination command words. Issue-pending copies the descriptor to the circular command queue and kicks enqueue. Queue IRQs drain status entries, match them against `comp_used`, set per-transfer error results if needed, complete cookies, and advance the status ring.

### Dependencies, Integration Points, Risks, And Test Signals
The driver depends on `virt-dma`, endian wrappers from `fsldma.h`, platform resources, named IRQs, coherent DMA memory, DMA pools, OF properties, IRQ affinity hints, and DMAengine. Risks include ring pointer wrap logic, descriptor/status matching using per-CPU duplicate suppression, a likely invalid IRQ range condition using `id < 0 && id > block_number`, command queue full/XOFF handling that leaves descriptors pending, queue-size `ilog2()` assumptions, 40-bit address packing, lack of OF DMA controller registration despite freeing it in remove, and hardware halt timeouts. Test signals include memcpy completions under load, command/status ring wrap, status error mapping to DMA transaction results, multiple blocks and queues, big-endian register access, queue full behavior, interrupt affinity, halt/init after reset, and remove cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/fsl-qdma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/fsl_raid.c -->
## sources/distributed-fs/ceph-client/drivers/dma/fsl_raid.c

### Purpose
`fsl_raid.c` is the DMAengine/ASYNC driver for the Freescale RAID Engine. It offloads RAID5/RAID6-related XOR, P/Q parity, and memcpy operations using hardware job rings, compound frames, and command descriptor blocks.

### Important APIs, Types, And Functions
Major DMAengine operations are `fsl_re_alloc_chan_resources()`, `fsl_re_free_chan_resources()`, `fsl_re_tx_submit()`, `fsl_re_issue_pending()`, `fsl_re_tx_status()`, `fsl_re_prep_dma_xor()`, `fsl_re_prep_dma_pq()`, and `fsl_re_prep_dma_memcpy()`. Internal helpers include `fsl_re_prep_dma_genq()`, `fill_cfd_frame()`, `fsl_re_init_desc()`, `fsl_re_chan_alloc_desc()`, `fsl_re_isr()`, `fsl_re_dequeue()`, `fsl_re_cleanup_descs()`, `fsl_re_desc_done()`, `fsl_re_chan_probe()`, `fsl_re_probe()`, `fsl_re_remove_chan()`, and `fsl_re_remove()`.

### Control Flow, State, And Persistence
Probe maps the RAID Engine register region, puts the engine in non-DPAA mode, programs the Galois-field polynomial, initializes DMAengine capabilities, creates DMA pools for compound/CDB blocks and hardware descriptor rings, scans job-queue and job-ring device-tree nodes, and creates one DMA channel per job ring. Channel probe maps job-ring registers by offset, creates a child platform device, requests the IRQ, allocates inbound/outbound rings, programs ring base/size registers, preserves LIODN bits from firmware, configures the job ring, and enables it. Prepared descriptors fill a CDB plus compound frames for MOVE, GenQ/XOR, or GenQQ/PQ operations. Submit queues descriptors in software; issue-pending copies descriptors into the inbound ring while slots are available. IRQs clear job-ring interrupt status and schedule a tasklet, which matches outbound descriptors to active software descriptors, completes callbacks, moves descriptors to the ack queue, and recycles acked descriptors.

### Dependencies, Integration Points, Risks, And Test Signals
The driver depends on DMAengine async_tx, MD RAID clients, OF platform child nodes, big-endian register access, DMA pools, hardware job rings, tasklets, and 40-bit DMA addressing. Risks include weak error recovery that logs but cannot report rich failures to MD, descriptor matching by hardware address, resource cleanup only expecting descriptors on `free_q`, no explicit handling for active/submit descriptors during free, ignored return values from job-ring probe and DMA registration, fixed maximum data length of 1 MiB, source-count constraints, and special single-source PQ behavior. Test signals include RAID5 XOR, RAID6 PQ with and without `DMA_PREP_CONTINUE`, `DMA_PREP_PQ_DISABLE_P`, memcpy MOVE, ring wrap at 1024 entries, interrupt/error paths, descriptor reuse after async ack, multiple job rings, and remove after idle operation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/fsl_raid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/fsl_raid.h -->
## sources/distributed-fs/ceph-client/drivers/dma/fsl_raid.h

### Purpose
`fsl_raid.h` defines Freescale RAID Engine register layouts, command descriptor block formats, compound frame formats, hardware descriptor formats, driver-private state, channel state, and async descriptor state used by `fsl_raid.c`.

### Important APIs, Types, And Functions
Key register-layout structures are `struct fsl_re_ctrl` for global engine registers and `struct fsl_re_chan_cfg` for job-ring registers. Command and frame types include `struct fsl_re_move_cdb`, `struct fsl_re_dpi`, `struct fsl_re_xor_cdb`, `struct fsl_re_noop_cdb`, `struct fsl_re_pq_cdb`, `struct fsl_re_cmpnd_frame`, and `struct fsl_re_hw_desc`. Runtime state is captured by `struct fsl_re_drv_private`, `struct fsl_re_chan`, and `struct fsl_re_desc`. The header also defines opcodes, CDB bit masks, ring sizes, descriptor alignment and size constants, frame descriptor fields, and engine/job-ring control bits.

### Control Flow, State, And Persistence
The header has no executable flow. It defines persistent state layouts: global driver state owns the DMAengine device, mapped global registers, job-ring pointers, and DMA pools; each channel owns job-ring software queues, inbound/outbound rings and counters, IRQ tasklet, and allocation count; each descriptor owns the async descriptor, hardware frame descriptor, compound frame/CDB memory, DMA addresses, and status.

### Dependencies, Integration Points, Risks, And Test Signals
The header depends on DMAengine, list/spinlock/tasklet infrastructure, big-endian register semantics, and DMA address handling supplied by includers. It integrates the RAID Engine hardware ABI with the Linux async_tx DMA API. Risks include packed hardware format assumptions without explicit `__packed` on every CDB-like structure, 40-bit address high/low field conventions, fixed ring and descriptor pool sizes, endian correctness of bitfields stored in `__be32`, and license header dual-licensing context. Test signals include structure-size/alignment checks, hardware acceptance of CDB/compound frame layouts, ring base address programming, and successful XOR/PQ/MOVE operations using descriptors allocated from the declared pools.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/fsl_raid.h -->
