# Research: subset-b-001253

This grouped report covers the DMA test, Synopsys DesignWare AXI DMA, DesignWare eDMA/HDMA, and classic DesignWare AHB DMA sources listed for `subset-b-001253`. Each file section is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/dmatest.c -->
## sources/distributed-fs/ceph-client/drivers/dma/dmatest.c

Purpose: Kernel DMAengine self-test module that exercises DMA_MEMCPY, DMA_MEMSET, DMA_XOR, and DMA_PQ capabilities across requested channels with configurable module parameters.

Important APIs/types/functions: `struct dmatest_params`, `struct dmatest_info`, `struct dmatest_thread`, `struct dmatest_chan`, module parameters `run`, `channel`, `device`, `iterations`, `timeout`, `polled`, `noverify`, and test helpers `dmatest_func()`, `dmatest_add_channel()`, `dmatest_run_set()`, `dmatest_chan_set()`. It uses DMAengine entry points such as `dma_request_channel()`, `device_prep_dma_memcpy()`, `device_prep_dma_memset()`, `device_prep_dma_xor()`, `device_prep_dma_pq()`, `dma_async_issue_pending()`, `dma_sync_wait()`, and `dmaengine_terminate_sync()`.

Control flow: module parameters are copied into `test_info.params`, channels are requested by capability, and per-operation kernel threads are created in pending state. Setting `run=1` starts pending threads; each thread allocates source/destination test buffers, maps them with the DMA API, prepares a transfer, waits by callback or polling, unmaps, verifies patterns, and loops until stopped or `iterations` is reached. `wait` blocks userspace until finite tests complete.

State and persistence: all runtime state is in memory under `test_info` plus per-thread buffers and DMA descriptors. Channel/thread lists are protected by `test_info.lock`; per-transfer completion uses wait queues and a callback flag. No persistent storage is used.

Dependencies and integration: integrates with the DMAengine framework, kernel module parameter infrastructure, kthreads, freezer support, DMA mapping, wait queues, and logging. It is a consumer used to validate provider drivers such as the DW drivers in this subset.

Risks and test signals: timeout paths warn about possible memory corruption if a DMA provider lacks proper terminate support. Useful signals are kernel log summaries, data mismatch warnings, timeout/error result lines, and dmatest success counts under interrupt and polling modes, random and fixed offsets, and all advertised capabilities.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/dmatest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/dw-axi-dmac/Makefile -->
## sources/distributed-fs/ceph-client/drivers/dma/dw-axi-dmac/Makefile

Purpose: Kbuild fragment for the DesignWare AXI DMAC platform driver.

Important APIs/types/functions: no C APIs are declared here. The only build rule maps `CONFIG_DW_AXI_DMAC` to `dw-axi-dmac-platform.o`.

Control flow: when the Kconfig symbol is enabled, this object is linked into the kernel or module according to the symbol mode.

State and persistence: no runtime state.

Dependencies and integration: depends on the parent DMA Kbuild and the `CONFIG_DW_AXI_DMAC` symbol defined elsewhere. It integrates the platform implementation with the DMA driver build.

Risks and test signals: build regressions show up as missing object linkage when `CONFIG_DW_AXI_DMAC=y/m`. A minimal test signal is a kernel build with the symbol enabled and module autoload/probe for compatible device-tree nodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/dw-axi-dmac/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/dw-axi-dmac/dw-axi-dmac-platform.c -->
## sources/distributed-fs/ceph-client/drivers/dma/dw-axi-dmac/dw-axi-dmac-platform.c

Purpose: Platform DMAengine provider for Synopsys DesignWare AXI DMA controllers, including SoC quirks for APB handshake registers, reset controls, alternate CFG2 layout, and channel-number phandle semantics.

Important APIs/types/functions: registers `struct platform_driver dw_driver`; implements DMAengine callbacks `device_alloc_chan_resources`, `device_free_chan_resources`, `device_prep_dma_memcpy`, `device_prep_slave_sg`, `device_prep_dma_cyclic`, `device_issue_pending`, `device_tx_status`, `device_config`, `device_pause`, `device_resume`, `device_terminate_all`, and `device_synchronize`. Core helpers include `dw_probe()`, `parse_device_properties()`, `axi_req_irqs()`, `dw_axi_dma_of_xlate()`, `axi_chan_block_xfer_start()`, `dw_axi_dma_set_hw_desc()`, and `dw_axi_dma_interrupt()`.

Control flow: probe maps registers, applies compatible flags, enables clocks/resets, parses device properties, allocates channel structures, requests IRQs, initializes virt-dma channels, registers the DMAengine device, and registers the OF DMA controller. Transfer prep creates DMA-pool LLIs, configures SAR/DAR/control fields, links descriptors, and queues via virt-dma. `issue_pending` starts the first queued descriptor by programming channel CFG/LLP/interrupt registers and enabling the channel. IRQ handling clears channel status, completes descriptors or cyclic periods, and restarts queued work.

State and persistence: `struct axi_dma_chan` stores current slave config, direction, cyclic flag, pause state, allocated descriptor count, and virt-dma state. `struct dw_axi_dma_hcfg` stores probed hardware shape. State is volatile and register-backed only; runtime PM gates clocks.

Dependencies and integration: integrates with platform resources, device properties, OF DMA lookup, runtime PM, reset/clock APIs, DMA pools, DMA mapping limits, and `../virt-dma.h`.

Risks and test signals: risks include block-size/alignment rejection, channel enable polling assumptions, cyclic LLP accounting, shared IRQ masking, APB handshake locking, and register layout quirks. Test with dmatest memcpy/slave/cyclic clients, OF phandle lookup, runtime suspend/resume, pause/resume/terminate, and SoC compatibles using CFG2/APB/reset variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/dw-axi-dmac/dw-axi-dmac-platform.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/dw-axi-dmac/dw-axi-dmac.h -->
## sources/distributed-fs/ceph-client/drivers/dma/dw-axi-dmac/dw-axi-dmac.h

Purpose: Private definitions for the DesignWare AXI DMAC platform driver, including hardware config structures, channel/descriptor types, LLI layout, register offsets, and bit definitions.

Important APIs/types/functions: defines `struct dw_axi_dma_hcfg`, `struct axi_dma_chip`, `struct dw_axi_dma`, `struct axi_dma_chan`, `struct axi_dma_desc`, `struct axi_dma_hw_desc`, `struct axi_dma_lli`, and `struct axi_dma_chan_config`. Inline helpers convert `dma_chan`/`virt_dma_chan`/`virt_dma_desc` to AXI driver types. Enums define AXI burst lengths, transfer widths, multiblock modes, flow-control modes, handshake selection, and interrupt bits.

Control flow: no executable flow beyond type conversion helpers. The platform source uses these offsets and masks to program common registers, channel registers, APB handshake controls, interrupt masks, and LLIs.

State and persistence: documents the in-memory and hardware-backed state shape. Persistent behavior is limited to hardware register/descriptor semantics while the driver is loaded.

Dependencies and integration: includes Linux DMAengine, device, clock, and `virt-dma` headers. The LLI layout is packed to match hardware fetch format, so structure field order is an ABI with the controller.

Risks and test signals: incorrect bit definitions can corrupt transfers or interrupt handling across all platform code. Test signals are successful descriptor fetches, correct IRQ decoding, compatible behavior on <=8 and >=16 channel register maps, and validation across 32/64-bit register accesses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/dw-axi-dmac/dw-axi-dmac.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/dw-edma/Kconfig -->
## sources/distributed-fs/ceph-client/drivers/dma/dw-edma/Kconfig

Purpose: Configuration entries for the Synopsys DesignWare eDMA core and the PCIe reference/glue driver.

Important APIs/types/functions: defines `CONFIG_DW_EDMA` and `CONFIG_DW_EDMA_PCIE`. `DW_EDMA` depends on PCI and PCI_MSI and selects DMAengine and virtual channels; `DW_EDMA_PCIE` depends on the parent feature and PCI/MSI support.

Control flow: build-time selection controls whether the common eDMA core and PCIe glue are compiled.

State and persistence: no runtime state.

Dependencies and integration: the dependency on PCI/MSI reflects that this eDMA implementation is normally exposed through PCIe endpoint/root-port designs and MSI/MSI-X interrupts.

Risks and test signals: wrong dependencies can produce compile failures or a driver with missing interrupt prerequisites. Test with all combinations `DW_EDMA=n`, `DW_EDMA=m/y`, and `DW_EDMA_PCIE=m/y` on PCI-enabled configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/dw-edma/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/dw-edma/Makefile -->
## sources/distributed-fs/ceph-client/drivers/dma/dw-edma/Makefile

Purpose: Kbuild rules for the DesignWare eDMA core, versioned register implementations, optional debugfs files, and PCIe glue.

Important APIs/types/functions: links `dw-edma-core.o`, `dw-edma-v0-core.o`, and `dw-hdma-v0-core.o` into `dw-edma.o`; conditionally adds v0 and HDMA debugfs objects under `CONFIG_DEBUG_FS`; builds `dw-edma-pcie.o` under `CONFIG_DW_EDMA_PCIE`.

Control flow: object composition determines which implementation files are linked into the core module and whether debugfs entry points are present.

State and persistence: no runtime state.

Dependencies and integration: mirrors the `dw_edma_core_ops` dispatch architecture: common core plus eDMA v0 and HDMA v0 register back ends.

Risks and test signals: missing debugfs object linkage would break debug builds; missing core objects would break symbol resolution for `dw_edma_probe()`. Test by building with and without `CONFIG_DEBUG_FS` and with PCIe glue enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/dw-edma/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/dw-edma/dw-edma-core.c -->
## sources/distributed-fs/ceph-client/drivers/dma/dw-edma/dw-edma-core.c

Purpose: Common DMAengine core for Synopsys DesignWare eDMA/HDMA controllers. It owns channel setup, descriptor/chunk/burst allocation, DMAengine callbacks, IRQ routing, transfer progression, and exported probe/remove entry points for bus glue.

Important APIs/types/functions: exports `dw_edma_probe()` and `dw_edma_remove()`. Key functions include `dw_edma_device_transfer()`, prep callbacks for slave SG/cyclic/interleaved, `dw_edma_device_config()`, `dw_edma_device_issue_pending()`, `dw_edma_start_transfer()`, done/abort interrupt handlers, IRQ allocation helpers, `dw_edma_channel_setup()`, and emulated interrupt helpers. It dispatches register work through `struct dw_edma_core_ops`.

Control flow: bus glue fills `struct dw_edma_chip`, then `dw_edma_probe()` chooses eDMA v0 or HDMA v0 ops, clamps hardware channel counts to linked-list region counts, requests IRQs, allocates optional emulated doorbell IRQ, initializes channels, registers DMAengine callbacks, and enables debugfs. Transfer prep validates direction against local/remote topology, creates chunks and bursts from SG/cyclic/interleaved input, and queues a virt-dma descriptor. Issue starts the first chunk; each done IRQ frees the completed chunk, starts the next chunk, pauses, stops, or completes the cookie.

State and persistence: volatile state lives in `struct dw_edma`, `struct dw_edma_chan`, `struct dw_edma_desc`, `struct dw_edma_chunk`, and `struct dw_edma_burst`. Channel status/request/configured flags gate operations. Linked-list memory regions are supplied by the platform and used as hardware-visible state; no file persistence.

Dependencies and integration: depends on DMAengine, virt-dma, MSI, IRQ descriptors, `linux/dma/edma.h`, and versioned core files. Bus glue must provide IRQ vector, optional PCI address translation, register base, LL/data regions, and map format.

Risks and test signals: direction inversion for local versus remote eDMA is easy to misuse; chunk accounting drives residue and completion; non-LL HDMA only supports one burst per chunk. Test with SG, cyclic, interleaved DMA, pause/resume/terminate, abort IRQs, single and multiple MSI vectors, callback-result residue, and local/remote address translation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/dw-edma/dw-edma-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/dw-edma/dw-edma-core.h -->
## sources/distributed-fs/ceph-client/drivers/dma/dw-edma/dw-edma-core.h

Purpose: Shared private interface for DesignWare eDMA/HDMA common core and register-version back ends.

Important APIs/types/functions: defines direction/request/status/xfer enums, `struct dw_edma_burst`, `struct dw_edma_chunk`, `struct dw_edma_desc`, `struct dw_edma_chan`, `struct dw_edma_irq`, `struct dw_edma`, `struct dw_edma_core_ops`, transfer wrapper structs, and inline dispatch helpers such as `dw_edma_core_start()`, `dw_edma_core_handle_int()`, `dw_edma_core_ch_config()`, and `dw_edma_core_ack_emulated_irq()`.

Control flow: the common core calls inline wrappers that dereference `dw->core`, allowing eDMA v0 or HDMA v0 implementations to supply register-specific behavior without conditional logic in most of the core.

State and persistence: lays out all in-memory state. Channel state (`request`, `status`, `configured`, `non_ll`) persists only while the driver is loaded. `ll_region` and MSI messages bridge in-memory descriptor state to hardware.

Dependencies and integration: includes `linux/msi.h`, `linux/dma/edma.h`, and `virt-dma`. It is consumed by all eDMA files and is the contract bus glue indirectly depends on through `dw_edma_chip`.

Risks and test signals: changes here have high blast radius because layout and ops signatures bind all eDMA variants. Test signals include successful compilation of eDMA and HDMA back ends, correct dispatch for both map formats, and no NULL optional op dereferences except where guarded.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/dw-edma/dw-edma-core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/dw-edma/dw-edma-pcie.c -->
## sources/distributed-fs/ceph-client/drivers/dma/dw-edma/dw-edma-pcie.c

Purpose: PCIe glue/reference driver that discovers DW eDMA/HDMA resources, maps BARs, allocates MSI/MSI-X vectors, fills `struct dw_edma_chip`, and starts the common eDMA core.

Important APIs/types/functions: `dw_edma_pcie_probe()`, `dw_edma_pcie_remove()`, PCI ID table entries for Synopsys EDDA and Xilinx/AMD MDB, static platform data (`snps_edda_data`, `xilinx_mdb_data`), VSEC parsers `dw_edma_pcie_get_synopsys_dma_data()` and `dw_edma_pcie_get_xilinx_dma_data()`, `dw_edma_set_chan_region_offset()`, and platform ops `irq_vector`/`pci_address`.

Control flow: probe enables PCI, copies default layout data, optionally overrides map format, BAR, register offset, and channel counts from vendor-specific capabilities, maps all required BARs, sets DMA mask, allocates IRQ vectors, fills register/LL/data regions for write and read channels, validates MSI, invokes `dw_edma_probe()`, and stores driver data. Remove delegates to `dw_edma_remove()` and frees PCI IRQ vectors.

State and persistence: per-device state is in devm-allocated `dw_edma_chip` plus copied probe-time layout data. Mapped BAR pointers and physical/bus addresses remain valid for driver lifetime only.

Dependencies and integration: integrates PCI core, VSEC parsing, MSI/MSI-X, PCI bus address translation, and the common eDMA core. For Xilinx MDB it supports native HDMA and falls back to non-linked-list mode when device memory offset is unavailable.

Risks and test signals: resource map correctness is critical; wrong BAR/offset/channel count can corrupt device memory. Test with Synopsys and Xilinx IDs, VSEC-present and default layouts, MSI and MSI-X vector allocation, non-LL fallback, DMA transfers in both directions, and remove after active/inactive probe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/dw-edma/dw-edma-pcie.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/dw-edma/dw-edma-v0-core.c -->
## sources/distributed-fs/ceph-client/drivers/dma/dw-edma/dw-edma-v0-core.c

Purpose: Register back end for eDMA v0, covering legacy viewport and unrolled register maps, interrupt handling, linked-list writing, channel configuration, doorbell start, debugfs enablement, and emulated interrupt acknowledgement.

Important APIs/types/functions: registers ops through `dw_edma_v0_core_register()`. Key functions are `dw_edma_v0_core_off()`, `dw_edma_v0_core_ch_count()`, `dw_edma_v0_core_ch_status()`, `dw_edma_v0_core_handle_int()`, `dw_edma_v0_core_start()`, `dw_edma_v0_core_ch_config()`, `dw_edma_v0_core_ack_emulated_irq()`, and helpers for viewport-safe channel register reads/writes.

Control flow: common core calls `start()` with a chunk; this back end writes LLI entries and the loopback LLP, enables engine and interrupts on first chunk, writes MSI target/data registers, sets channel LLP, synchronizes remote LL memory with a dummy read when needed, and rings the direction-specific doorbell. IRQ handling reads done/abort status, masks by assigned IRQ channel mask, clears per-channel bits, and calls common done/abort callbacks.

State and persistence: hardware state includes engine enable, interrupt masks/clears/status, per-channel context, MSI programming, and LL memory contents. Legacy channel access is serialized by `dw->lock` because all channels share a viewport selector.

Dependencies and integration: uses `dw-edma-v0-regs.h`, `dw-edma-v0-debugfs.h`, `bitfield`, 64-bit MMIO helpers, and `dw_edma_core_ops`.

Risks and test signals: legacy viewport races, CB/TCB toggling, remote LL write ordering, MSI data packing, and HDMA-compatible power-enable special cases are sensitive. Test with legacy and unroll map formats, done/abort IRQs, remote engine mode, multiple channels, and debugfs register reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/dw-edma/dw-edma-v0-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/dw-edma/dw-edma-v0-core.h -->
## sources/distributed-fs/ceph-client/drivers/dma/dw-edma/dw-edma-v0-core.h

Purpose: Minimal declaration header for the eDMA v0 register back end.

Important APIs/types/functions: declares `dw_edma_v0_core_register(struct dw_edma *dw)`, which installs the eDMA v0 `dw_edma_core_ops` table into the common core object.

Control flow: common probe calls this function unless the chip map format selects native HDMA.

State and persistence: no standalone state; registration mutates `dw->core`.

Dependencies and integration: includes `linux/dma/edma.h` for the forward-visible eDMA types. Used by `dw-edma-core.c`.

Risks and test signals: low-risk header, but prototype drift breaks linkage. Test with normal `CONFIG_DW_EDMA` builds and probe paths selecting eDMA v0.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/dw-edma/dw-edma-v0-core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/dw-edma/dw-edma-v0-debugfs.c -->
## sources/distributed-fs/ceph-client/drivers/dma/dw-edma/dw-edma-v0-debugfs.c

Purpose: Optional debugfs register exposure for eDMA v0 legacy/unroll/compatible hardware.

Important APIs/types/functions: exports `dw_edma_v0_debugfs_on()`. Defines debugfs entry descriptors, `dw_edma_debugfs_u32_get()`, register array builders for global write/read registers, per-channel context registers, and legacy viewport-aware access.

Control flow: when debugfs is initialized, the function creates `mf`, `wr_ch_cnt`, `rd_ch_cnt`, and a `registers` tree under the DMAengine debug root. It creates write/read subdirectories and channel directories, with read-only files that return MMIO register values. Legacy channel register reads program the viewport selector under `dw->lock`.

State and persistence: debugfs entries are devm-allocated and mirror live MMIO state; they do not store values independently.

Dependencies and integration: compiled only when `CONFIG_DEBUG_FS` through the Makefile. Integrates with DMAengine debug roots and eDMA v0 register layouts.

Risks and test signals: unsafe debugfs files expose live register reads; legacy viewport must remain locked to avoid racing hardware access. Test by mounting debugfs, probing eDMA v0, reading global and channel files in legacy and unroll formats, and verifying no probe failure when debugfs is disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/dw-edma/dw-edma-v0-debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/dw-edma/dw-edma-v0-debugfs.h -->
## sources/distributed-fs/ceph-client/drivers/dma/dw-edma/dw-edma-v0-debugfs.h

Purpose: Debugfs interface wrapper for eDMA v0.

Important APIs/types/functions: declares `dw_edma_v0_debugfs_on()` under `CONFIG_DEBUG_FS` and provides an empty inline stub otherwise.

Control flow: register back end calls this unconditionally through its debugfs op; the header makes that call compile away when debugfs is disabled.

State and persistence: no state in the header.

Dependencies and integration: includes `linux/dma/edma.h`; consumed by `dw-edma-v0-core.c` and implemented by `dw-edma-v0-debugfs.c`.

Risks and test signals: main risk is build consistency across debugfs-enabled and disabled configs. Test both build modes and verify no missing symbol when `CONFIG_DEBUG_FS=n`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/dw-edma/dw-edma-v0-debugfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/dw-edma/dw-edma-v0-regs.h -->
## sources/distributed-fs/ceph-client/drivers/dma/dw-edma/dw-edma-v0-regs.h

Purpose: Packed MMIO and linked-list register definitions for eDMA v0 hardware.

Important APIs/types/functions: defines masks for channel counts, viewport, done/abort interrupts, channel status, doorbell channel, linked-list errors, MSI data packing, and `EDMA_V0_MAX_NR_CH`. Structures include `dw_edma_v0_ch_regs`, `dw_edma_v0_ch`, `dw_edma_v0_unroll`, `dw_edma_v0_legacy`, `dw_edma_v0_regs`, `dw_edma_v0_lli`, and `dw_edma_v0_llp`.

Control flow: no executable flow; these layouts are used by the v0 core and debugfs code to compute MMIO addresses and linked-list element format.

State and persistence: represents hardware-visible state in registers and LL memory. Structures are packed because offsets must match the hardware programming model.

Dependencies and integration: includes DMAengine definitions and is private to the eDMA v0 implementation.

Risks and test signals: any offset, padding, or mask error can break channel count discovery, interrupts, MSI setup, descriptor fetch, or debugfs output. Test by comparing offsets against hardware docs, reading debugfs registers, and running transfers on legacy and unroll variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/dw-edma/dw-edma-v0-regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/dw-edma/dw-hdma-v0-core.c -->
## sources/distributed-fs/ceph-client/drivers/dma/dw-edma/dw-hdma-v0-core.c

Purpose: Register back end for native DesignWare HDMA v0 hardware, supporting linked-list and non-linked-list modes.

Important APIs/types/functions: registers ops through `dw_hdma_v0_core_register()`. Key functions are `dw_hdma_v0_core_off()`, `dw_hdma_v0_core_ch_count()`, `dw_hdma_v0_core_ch_status()`, `dw_hdma_v0_core_handle_int()`, `dw_hdma_v0_core_start()`, `dw_hdma_v0_core_ll_start()`, `dw_hdma_v0_core_non_ll_start()`, and `dw_hdma_v0_core_ch_config()`.

Control flow: `off()` masks/clears stop and abort interrupts and disables all channels. Start writes LL entries and a looping LLP, or in non-LL mode directly programs SAR/DAR/transfer size for a single burst. It enables channel interrupts, programs LL pointer/cycle bits for LL mode, and rings the per-channel doorbell. IRQ handling iterates channels in the assigned mask and invokes common done/abort callbacks based on per-channel interrupt status.

State and persistence: per-channel MMIO holds enable, doorbell, LLP, cycle sync, transfer registers, MSI addresses, status, and interrupt setup. Non-LL mode uses only the first burst in a chunk. No persistent state beyond hardware while loaded.

Dependencies and integration: uses `dw-hdma-v0-regs.h`, `dw-hdma-v0-debugfs.h`, and common eDMA core ops. It is selected when `dw_edma_chip.mf == EDMA_MF_HDMA_NATIVE`.

Risks and test signals: risks include swapped argument order in register helper calls, non-LL single-burst assumptions, interrupt mask polarity, remote LL ordering, and unknown doorbell offset reporting. Test native HDMA with SG/cyclic/interleaved paths, non-LL fallback, abort/stop IRQs, local and remote modes, and debugfs reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/dw-edma/dw-hdma-v0-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/dw-edma/dw-hdma-v0-core.h -->
## sources/distributed-fs/ceph-client/drivers/dma/dw-edma/dw-hdma-v0-core.h

Purpose: Minimal declaration header for the native HDMA v0 register back end.

Important APIs/types/functions: declares `dw_hdma_v0_core_register(struct dw_edma *dw)`, which installs HDMA v0 operations into the common eDMA core.

Control flow: common probe calls this when the map format is `EDMA_MF_HDMA_NATIVE`.

State and persistence: no standalone state; registration changes `dw->core`.

Dependencies and integration: includes `linux/dma/edma.h`; consumed by `dw-edma-core.c`.

Risks and test signals: prototype drift breaks builds or probe selection. Test with native HDMA-capable configs and PCI IDs that select HDMA.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/dw-edma/dw-hdma-v0-core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/dw-edma/dw-hdma-v0-debugfs.c -->
## sources/distributed-fs/ceph-client/drivers/dma/dw-edma/dw-hdma-v0-debugfs.c

Purpose: Optional debugfs register exposure for native HDMA v0 channels.

Important APIs/types/functions: exports `dw_hdma_v0_debugfs_on()`. Builds read-only files for per-channel write/read register blocks via `dw_hdma_debugfs_regs_ch()`, `dw_hdma_debugfs_regs_wr()`, and `dw_hdma_debugfs_regs_rd()`.

Control flow: when debugfs is initialized, creates `mf`, `wr_ch_cnt`, `rd_ch_cnt`, then a `registers/write/channel:N` and `registers/read/channel:N` tree. Each file reads a live 32-bit MMIO register such as `ch_en`, `doorbell`, `llp`, `sar`, `dar`, `ch_stat`, `int_stat`, MSI registers, and control fields.

State and persistence: debugfs entries are devm-allocated views onto live hardware registers. They do not persist data or modify device state.

Dependencies and integration: compiled under `CONFIG_DEBUG_FS`; depends on `dw-hdma-v0-regs.h` and the common eDMA debug root.

Risks and test signals: read-only MMIO is low-impact but still tied to correct offsets and live device lifetime. Test with debugfs enabled, native HDMA probe, register file reads during idle and active transfers, and disabled debugfs builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/dw-edma/dw-hdma-v0-debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/dw-edma/dw-hdma-v0-debugfs.h -->
## sources/distributed-fs/ceph-client/drivers/dma/dw-edma/dw-hdma-v0-debugfs.h

Purpose: Debugfs interface wrapper for native HDMA v0.

Important APIs/types/functions: declares `dw_hdma_v0_debugfs_on()` when `CONFIG_DEBUG_FS` is enabled and provides an empty stub otherwise.

Control flow: HDMA core invokes this through its debugfs op without surrounding ifdefs.

State and persistence: no state.

Dependencies and integration: includes `linux/dma/edma.h`; connects `dw-hdma-v0-core.c` to optional `dw-hdma-v0-debugfs.c`.

Risks and test signals: build-mode consistency is the main concern. Test `CONFIG_DEBUG_FS=y` and `n` with `CONFIG_DW_EDMA` enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/dw-edma/dw-hdma-v0-debugfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/dw-edma/dw-hdma-v0-regs.h -->
## sources/distributed-fs/ceph-client/drivers/dma/dw-edma/dw-hdma-v0-regs.h

Purpose: Packed MMIO and linked-list definitions for native HDMA v0 hardware.

Important APIs/types/functions: defines channel count, enable, interrupt mask/enable bits, link-list enable, consumer cycle bits, doorbell start bit, and channel status mask. Structures include `dw_hdma_v0_ch_regs`, `dw_hdma_v0_ch`, `dw_hdma_v0_regs`, `dw_hdma_v0_lli`, and `dw_hdma_v0_llp`.

Control flow: no executable logic; consumed by the HDMA core and debugfs code for register offsets and LLI layout.

State and persistence: represents live hardware register state and hardware-fetched LL entries. Packed layout is part of the device programming ABI.

Dependencies and integration: includes DMAengine headers and is private to the HDMA v0 implementation.

Risks and test signals: incorrect offsets or bit definitions can break start, stop, abort, MSI, LL mode, or non-LL mode. Test with debugfs offset inspection, successful HDMA transfers, stop/abort interrupts, and comparison against vendor register documentation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/dw-edma/dw-hdma-v0-regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/dw/Kconfig -->
## sources/distributed-fs/ceph-client/drivers/dma/dw/Kconfig

Purpose: Configuration entries for classic Synopsys DesignWare AHB DMA core, platform driver, PCI driver, and Renesas RZ/N1 DMAMUX frontend.

Important APIs/types/functions: defines `CONFIG_DW_DMAC_CORE`, `CONFIG_DW_DMAC`, `CONFIG_RZN1_DMAMUX`, and `CONFIG_DW_DMAC_PCI`. Platform and PCI drivers select the shared core; the Renesas DMAMUX depends on the platform driver.

Control flow: build-time symbols determine which bus glue and support modules are compiled.

State and persistence: no runtime state.

Dependencies and integration: declares PCI, HAS_IOMEM, architecture, and DMAengine dependencies needed by the DW AHB driver family.

Risks and test signals: dependency errors can cause unmet symbols or unusable driver selections. Test with platform-only, PCI-only, both, and compile-test DMAMUX configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/dw/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/dw/Makefile -->
## sources/distributed-fs/ceph-client/drivers/dma/dw/Makefile

Purpose: Kbuild rules for the classic DesignWare AHB DMA core, variant implementations, platform/PCI glue, optional ACPI/OF helpers, and RZ/N1 DMAMUX.

Important APIs/types/functions: builds `dw_dmac_core.o` from `core.o`, `dw.o`, and `idma32.o`, optionally adding `acpi.o`. Builds platform module from `platform.o` plus `of.o` under `CONFIG_OF`, and PCI module from `pci.o`.

Control flow: object composition wires shared core logic with register-variant operations and bus glue based on configuration.

State and persistence: no runtime state.

Dependencies and integration: matches the source architecture: bus glue calls variant probe functions, which install operation callbacks and delegate to `do_dma_probe()`.

Risks and test signals: build regressions show as unresolved variant/core symbols. Test with ACPI and OF toggled independently and with platform and PCI symbols as modules or built-in.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/dw/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/dw/acpi.c -->
## sources/distributed-fs/ceph-client/drivers/dma/dw/acpi.c

Purpose: ACPI DMA controller registration and channel filter for classic DW DMA devices.

Important APIs/types/functions: `dw_dma_acpi_controller_register()`, `dw_dma_acpi_controller_free()`, and internal `dw_dma_acpi_filter()`. Uses `acpi_dma_controller_register()`, `acpi_dma_simple_xlate()`, and `dw_dma_filter()`.

Control flow: registration checks for an ACPI companion, allocates `acpi_dma_filter_info`, sets a DMA_SLAVE capability mask and filter callback, and registers the controller. The filter translates `acpi_dma_spec` slave ID into a `dw_dma_slave` with memory/peripheral master IDs from driver match data, then delegates channel suitability to `dw_dma_filter()`.

State and persistence: devm-allocated filter info lives for device lifetime. No persistent state beyond ACPI registration.

Dependencies and integration: compiled under `CONFIG_ACPI`; used by both platform and PCI glue after successful core probe.

Risks and test signals: incorrect match data master IDs can bind clients to wrong bus masters; missing ACPI companion should be a no-op. Test ACPI DMA client lookup, removal cleanup, and systems without ACPI companions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/dw/acpi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/dw/core.c -->
## sources/distributed-fs/ceph-client/drivers/dma/dw/core.c

Purpose: Shared DMAengine core for classic Synopsys DesignWare AHB DMA variants. It manages descriptors, queues, interrupt/tasklet completion, transfer preparation, pause/resume/terminate, resource allocation, hardware parameter probing, and DMAengine registration.

Important APIs/types/functions: `do_dma_probe()`, `do_dma_remove()`, `do_dw_dma_on/off()`, `do_dw_dma_enable/disable()`, `dw_dma_filter()`, prep callbacks `dwc_prep_dma_memcpy()` and `dwc_prep_slave_sg()`, status/config callbacks, interrupt handler `dw_dma_interrupt()`, tasklet `dw_dma_tasklet()`, and descriptor helpers `dwc_desc_get()`, `dwc_dostart()`, `dwc_scan_descriptors()`, `dwc_descriptor_complete()`.

Control flow: variant probe installs operation callbacks and calls `do_dma_probe()`. The core obtains platform data or auto-configures from hardware registers, allocates channels, creates a DMA pool for hardware descriptors, requests IRQ, registers DMAengine capabilities, and exposes DMA callbacks. Transfer prep builds linked descriptor chains; submit queues them; issue-pending starts the first queued chain using hardware LLP or software LLP emulation. IRQ disables masks and schedules a tasklet; tasklet scans transfer/error bits, completes descriptors, advances queued work, or handles bad descriptors.

State and persistence: `struct dw_dma` owns device state, channel array, descriptor pool, tasklet, all-channel mask, and in-use mask. Each channel owns active/queued descriptor lists, lock, direction, slave config, flags for paused/soft-LLP/cyclic, residue, and hardware capability data. All state is volatile and register/DMA-pool backed.

Dependencies and integration: used by `dw.c` and `idma32.c` variants plus platform/PCI glue. Depends on DMAengine, DMA pools, IRQ/tasklet, runtime PM, and register definitions from `regs.h`.

Risks and test signals: descriptor list manipulation, soft LLP fallback, residue accounting, pause drain behavior, bad descriptor recovery, and auto-configuration parsing are high-risk. Test with dmatest memcpy and slave SG, channels with and without LLP, pause/resume/terminate, shared IRQ behavior, runtime PM probe/remove, and invalid DMA address error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/dw/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/dw/dw.c -->
## sources/distributed-fs/ceph-client/drivers/dma/dw/dw.c

Purpose: Register-variant implementation for the standard DesignWare AHB DMA controller.

Important APIs/types/functions: exports `dw_dma_probe()` and `dw_dma_remove()`. Installs callbacks `dw_dma_initialize_chan()`, `dw_dma_suspend_chan()`, `dw_dma_resume_chan()`, `dw_dma_prepare_ctllo()`, `dw_dma_bytes2block()`, `dw_dma_block2bytes()`, `dw_dma_set_device_name()`, `dw_dma_disable()`, and `dw_dma_enable()`.

Control flow: probe allocates `struct dw_dma`, assigns channel and device operation callbacks, stores it in `chip->dw`, and delegates to `do_dma_probe()`. Channel initialization programs CFG_LO/HI with priority, FIFO mode, handshakes, polarity, peripheral IDs, and protection control. Transfer prep callbacks in the core call `prepare_ctllo()` and block conversion helpers to build descriptor CTL fields.

State and persistence: no independent persistent state; it provides behavior used by the shared `struct dw_dma` state. Register writes persist only while hardware is powered and configured.

Dependencies and integration: integrates with `internal.h`, `regs.h`, shared core, DMAengine direction helpers, and exported probe/remove symbols for platform/PCI glue.

Risks and test signals: wrong burst encoding or master selection can cause broken transfers on slave paths. Test standard DW controllers with memory copy and peripheral SG, different master IDs, handshake polarity, suspend/resume, and block-size boundary transfers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/dw/dw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/dw/idma32.c -->
## sources/distributed-fs/ceph-client/drivers/dma/dw/idma32.c

Purpose: Register-variant implementation for Intel iDMA32 controllers, including optional crossbar programming for newer PSE DMA devices.

Important APIs/types/functions: exports `idma32_dma_probe()` and `idma32_dma_remove()`. Provides channel init callbacks `idma32_initialize_chan_generic()` and `idma32_initialize_chan_xbar()`, suspend/resume with drain support, byte/block conversion, CTL_LO preparation, FIFO partitioning, and enable/disable wrappers.

Control flow: probe allocates `struct dw_dma`, selects xbar or generic channel initialization based on platform-data quirks, installs iDMA32-specific callbacks, and delegates to `do_dma_probe()`. Xbar initialization programs channel ID access, transfer mode, snoop bits, PCI devfn selection, RX/TX selection, request-line extensions, and channel CFG registers. Enable/disable partition FIFOs before/after core enable state changes.

State and persistence: modifies iDMA32-specific MMIO registers for channel control, source/destination fill-in, xbar selection, register access channel ID, and FIFO partition. Runtime state remains in shared `struct dw_dma`.

Dependencies and integration: used by internal platform data for Merrifield and Elkhart Lake/PSE PCI/ACPI IDs. Depends on PCI device identity for xbar slave devfn selection.

Risks and test signals: xbar mode depends on correct slave PCI device association and direction mapping; FIFO partition programming affects all channels. Test Intel iDMA32 devices with MEM_TO_DEV and DEV_TO_MEM clients, xbar and non-xbar paths, drain terminate, maxburst encoding, and repeated enable/disable cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/dw/idma32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/dw/internal.h -->
## sources/distributed-fs/ceph-client/drivers/dma/dw/internal.h

Purpose: Private shared header for classic DesignWare AHB DMA core, variants, and bus glue.

Important APIs/types/functions: declares `do_dma_probe/remove()`, core enable/disable helpers, variant probes/removes, `dw_dma_filter()`, ACPI/OF registration helpers, `struct dw_dma_chip_pdata`, and built-in platform-data instances for standard DW, iDMA32, and xbar iDMA32.

Control flow: bus glue selects a `dw_dma_chip_pdata` from OF/ACPI/PCI match data, fills `struct dw_dma_chip`, then calls the selected `probe()` callback. Variant probe installs callbacks and delegates to core probe.

State and persistence: static platform data encodes channel count, allocation order, priority, block size, masters, data width, multiblock support, and quirks. Runtime state itself is outside this header.

Dependencies and integration: includes public `linux/dma/dw.h` and private `regs.h`. Provides CONFIG_ACPI and CONFIG_OF stubs so callers can be unconditional.

Risks and test signals: static pdata mistakes affect entire hardware families. Test that each match path selects the intended pdata, that OF/ACPI stubs compile out cleanly, and that variant probe/remove linkage remains valid.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/dw/internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/dw/of.c -->
## sources/distributed-fs/ceph-client/drivers/dma/dw/of.c

Purpose: Device-tree parsing and OF DMA controller registration for classic DW DMA.

Important APIs/types/functions: `dw_dma_parse_dt()`, `dw_dma_of_controller_register()`, `dw_dma_of_controller_free()`, and internal `dw_dma_of_xlate()`.

Control flow: DT parsing reads `dma-masters`, `dma-channels`, allocation order, priority, block size, deprecated `data_width`, preferred `data-width`, `multi-block`, `snps,max-burst-len`, and protection-control properties into platform data. OF xlate expects 3 or 4 arguments: request line, memory master, peripheral master, and optional channel mask; it validates ranges, creates `dw_dma_slave`, and requests a DMA_SLAVE channel through `dw_dma_filter()`.

State and persistence: parsed platform data is devm-allocated for device lifetime. OF controller registration exists while the driver is bound.

Dependencies and integration: integrates with OF DMA bindings, platform driver probe, and shared channel filter.

Risks and test signals: binding argument/range errors can silently prevent clients from obtaining channels; deprecated and current data-width handling must remain compatible. Test DT probe, DMA client phandles with and without channel masks, invalid property rejection, and OF unregister on remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/dw/of.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/dw/pci.c -->
## sources/distributed-fs/ceph-client/drivers/dma/dw/pci.c

Purpose: PCI bus glue for classic DesignWare AHB DMA and Intel iDMA32 variants.

Important APIs/types/functions: `dw_pci_probe()`, `dw_pci_remove()`, system sleep callbacks, PCI ID table mapping Intel device IDs to `dw_dma_chip_pdata`, `idma32_chip_pdata`, or `xbar_chip_pdata`, and `module_pci_driver()`.

Control flow: probe enables the PCI device, maps BAR0, sets bus master/MWI, configures a 32-bit DMA mask, duplicates match data, allocates `dw_dma_chip`, fills device/id/register/IRQ/pdata fields, invokes the selected variant probe, stores driver data, and registers ACPI DMA lookup. Remove unregisters ACPI lookup and calls variant remove. Suspend/resume disable/enable the core through shared helpers.

State and persistence: per-device match-data copy holds the chip pointer and variant metadata. Mapped PCI BAR and IRQ remain owned during driver binding.

Dependencies and integration: integrates PCI, ACPI DMA helpers, shared core, and variant-specific pdata for Intel SoCs.

Risks and test signals: wrong PCI ID mapping selects wrong register variant or master IDs; 32-bit DMA mask limits clients; suspend/resume assumes registers are accessible. Test all listed Intel IDs, ACPI client lookup, DMA transfer after resume, remove cleanup, and BAR/IRQ failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/dw/pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/dw/platform.c -->
## sources/distributed-fs/ceph-client/drivers/dma/dw/platform.c

Purpose: Platform bus glue for classic DesignWare AHB DMA controllers.

Important APIs/types/functions: `dw_probe()`, `dw_remove()`, `dw_shutdown()`, OF and ACPI match tables, late suspend/resume callbacks, and subsys init/module exit registration.

Control flow: probe obtains match data, duplicates it, allocates `dw_dma_chip`, gets IRQ and MMIO resource, coerces a 32-bit DMA mask, obtains platform data from match, platform data, or DT parser, enables optional `hclk`, enables runtime PM, invokes variant probe, stores driver data, and registers OF/ACPI DMA controllers. Remove unregisters lookup providers, calls variant remove, disables runtime PM, and disables clock. Shutdown runtime-resumes unconditionally before disabling the DMA core to stop active transfers, then disables clock.

State and persistence: per-device `dw_dma_chip_pdata` and `dw_dma_chip` are devm-managed. Clock/runtime-PM state and OF/ACPI registration live for binding lifetime only.

Dependencies and integration: integrates platform resources, clocks, runtime PM, OF, ACPI, shared core, and static match data for standard DW and xbar iDMA32 variants.

Risks and test signals: shutdown/power sequencing is sensitive because registers may be inaccessible if powered off; DT fallback can fail if required pdata is absent; clock errors abort probe. Test platform probe/remove, OF and ACPI DMA client lookup, runtime/system suspend/resume, shutdown with active transfers, and optional clock absence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/dw/platform.c -->
