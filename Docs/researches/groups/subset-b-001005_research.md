# subset-b-001005 Research

Grouped research for HabanaLabs Goya/MMU/PCI headers and Intel ivpu accelerator driver files. Each section preserves the original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/goya_coresight.h -->
## sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/goya_coresight.h

### Purpose
`goya_coresight.h` names the Goya debug/trace fabric instances used by the HabanaLabs driver. It provides stable enum indexes for CoreSight-style STM, ETF, funnel, bus monitor, and SPMU register tables.

### Important APIs, Types, And Functions
The exported types are `enum goya_debug_stm_regs_index`, `enum goya_debug_etf_regs_index`, `enum goya_debug_funnel_regs_index`, `enum goya_debug_bmon_regs_index`, and `enum goya_debug_spmu_regs_index`. Each enum includes `FIRST` and `LAST` sentinels plus per-block names for CPU, DMA channels/macros, MME subblocks, MMU, PCIe, PSOC, and TPC EML/RTR blocks.

### Control Flow
There is no executable flow. Consumers use these enum values as array indexes into Goya debug register metadata or iteration bounds when enabling, reading, or dumping trace components.

### State, Persistence, And Dependencies
The header stores no state. Persistent effects occur only when caller code uses the indexes to program hardware trace registers. It depends only on consumers maintaining register arrays in the same order as these enums.

### Integration Points
The definitions integrate with HabanaLabs debugfs, coresight/trace collection, performance monitoring, and diagnostics paths for Goya. They bind logical block names to hardware-specific register descriptions.

### Risks
The main risk is index drift: changing enum order without updating the matching register tables would program or read the wrong debug block. Range loops must include `LAST` correctly and not assume all enum families have the same count.

### Test Signals
Useful signals include debug dumps naming the expected blocks, successful trace capture from CPU/DMA/TPC/MMU/PCIe sources, and bounds tests that iterate from `FIRST` through `LAST` without accessing past the matching table.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/goya_coresight.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/goya_fw_if.h -->
## sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/goya_fw_if.h

### Purpose
`goya_fw_if.h` defines small but critical Goya firmware interface constants: the MSI-X event queue index, CPU boot address, firmware image offsets, and low PLL frequency.

### Important APIs, Types, And Functions
The macros are `GOYA_EVENT_QUEUE_MSIX_IDX`, `CPU_BOOT_ADDR`, `UBOOT_FW_OFFSET`, `LINUX_FW_OFFSET`, and `GOYA_PLL_FREQ_LOW`. They describe firmware placement in SRAM/DDR and the low clock used during boot or safe configuration.

### Control Flow
There is no code flow. Boot and interrupt setup code consumes these constants while programming firmware load addresses, CPU reset vectors, and event queue interrupt routing.

### State, Persistence, And Dependencies
State lives in hardware registers and firmware memory regions programmed by callers. The header depends on matching Goya firmware layout assumptions: U-Boot starts at 1 MiB in SRAM and Linux firmware starts at 8 MiB in DDR.

### Integration Points
It integrates with Goya firmware loading, CPU bring-up, event queue setup, and PLL configuration paths in the HabanaLabs driver.

### Risks
Incorrect offsets or boot address values can make firmware boot fail or overwrite reserved memory. Changing the MSI-X queue index without matching device/firmware changes can break event delivery.

### Test Signals
Boot logs should show firmware copied to expected offsets, firmware ready events arriving on MSI-X index 5, and low-frequency PLL programming succeeding before normal device bring-up.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/goya_fw_if.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/goya_packets.h -->
## sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/goya_packets.h

### Purpose
`goya_packets.h` describes Goya command packet IDs, shared packet header fields, control-bit masks, and packed little-endian packet payload layouts understood by the command processor.

### Important APIs, Types, And Functions
`enum packet_id` enumerates `PACKET_WREG_32`, `PACKET_WREG_BULK`, message packets, DMA packets, `PACKET_FENCE`, `PACKET_NOP`, and `PACKET_STOP`. `struct goya_packet` provides the common 64-bit header plus flexible contents. Specific layouts include `packet_wreg32`, `packet_wreg_bulk`, `packet_msg_long`, `packet_msg_short`, `packet_msg_prot`, `packet_fence`, `packet_lin_dma`, and `packet_cp_dma`. Header/control macros expose packet ID, opcode, EB/RB/MB, register offset, and linear-DMA mode bits.

### Control Flow
The file has no executable flow. Submission validation reads `goya_packet.header`, extracts `packet_id`, casts the following bytes to the matching packet struct, validates command size and control bits, and then passes the packet buffer to hardware.

### State, Persistence, And Dependencies
The persistent state is the command buffer submitted to the device and any resulting hardware register or DMA side effect. The header depends on Linux fixed-width and little-endian types, and on firmware/hardware matching this ABI exactly.

### Integration Points
It is part of the Goya command submission ABI between userspace, the kernel driver, and the command processor. DMA packet fields integrate with memory manager address validation, while message packets integrate with firmware doorbells/queues.

### Risks
Packet structs are hardware ABI: changing field size, endian type, or control masks breaks existing command buffers. Flexible arrays require separate size validation. DMA direction, memset, completion, and write-only bits are security-sensitive because malformed packets can target unintended memory or registers.

### Test Signals
Tests should validate every packet ID, malformed headers, short command buffers, register-offset bounds, DMA address ranges, fence behavior, stop/nop handling, and endian-correct decoding on little-endian command streams.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/goya_packets.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/goya_reg_map.h -->
## sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/goya_reg_map.h

### Purpose
`goya_reg_map.h` aliases Goya PSOC scratchpad and global configuration registers to semantic CPU/firmware names used by the driver.

### Important APIs, Types, And Functions
The macros map queue base/length/consumer-index fields (`mmCPU_PQ_*`, `mmCPU_EQ_*`, `mmCPU_CQ_*`), boot/update/version status (`mmCPU_BOOT_DEV_STS*`, `mmCPU_BOOT_ERR*`, `mmUPD_*`, `mmPREBOOT_VER_OFFSET`, `mmUBOOT_VER_OFFSET`), command/status exchange (`mmCPU_CMD_STATUS_TO_HOST`, `mmPSOC_GLOBAL_CONF_KMD_MSG_TO_CPU`), and hardware state (`mmHW_STATE`) onto underlying `mmPSOC_GLOBAL_CONF_*` registers.

### Control Flow
There is no runtime flow. Driver code reads and writes the semantic aliases while performing firmware boot, queue setup, update coordination, and status polling.

### State, Persistence, And Dependencies
State is stored in PSOC scratchpad/global registers that survive long enough for host-firmware coordination, with `mmUPD_PENDING_STS` using non-reset flop storage. The header depends on generated ASIC register macros being included before use.

### Integration Points
The aliases integrate Goya firmware interface code, boot diagnostics, event/command queue setup, and update flows with the generated register map.

### Risks
Scratchpads are shared firmware/driver ABI. Reusing an index for a different purpose or including this header without the underlying register definitions causes silent misprogramming or build failures.

### Test Signals
Boot should report sane firmware version/status values, queue base/length registers should match allocated queues, update status should survive intended resets, and read/write test scratchpads should round-trip.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/goya_reg_map.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/hw_ip/mmu/mmu_general.h -->
## sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/hw_ip/mmu/mmu_general.h

### Purpose
`mmu_general.h` defines shared HabanaLabs MMU page sizes, PTE flag masks, hop counts, hop table geometry, and common hop-number identifiers.

### Important APIs, Types, And Functions
It exports page shift/size macros from 4 KiB through 1 GiB, PTE flag masks (`PAGE_PRESENT_MASK`, `SWAP_OUT_MASK`, `LAST_MASK`, `FLAGS_MASK`), hop architecture constants from 3 to 6 hops, `HOP_PHYS_ADDR_MASK`, `HL_PTE_SIZE`, 512-entry hop table sizing, HOP0 physical-address register shifts, `MMU_CONFIG_TIMEOUT_USEC`, and `enum mmu_hop_num`.

### Control Flow
No executable flow exists. MMU code uses these constants to allocate page tables, encode/decode PTEs, walk address hops, program HOP0 roots, and poll MMU configuration completion.

### State, Persistence, And Dependencies
Persistent state is hardware page table memory and MMU configuration registers built using these masks. The header assumes `u64`, `_BITUL`, and `MAX_ASID` are available from surrounding driver headers.

### Integration Points
The file is shared by MMU implementations for multiple HabanaLabs ASIC generations and underpins virtual-memory mapping, ASID setup, page-table allocation, and PTE flag handling.

### Risks
Mask and size errors corrupt address translation. `HOP0_512_PTE_TABLES_TOTAL_SIZE` depends on `MAX_ASID`; mismatches can underallocate root tables. Flag masking must stay consistent with hardware-defined low PTE bits.

### Test Signals
Tests should cover PTE encoding/decoding, hop table allocation sizes, ASID root programming, page sizes at each supported granularity, and timeout behavior when MMU config busy bits do not clear.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/hw_ip/mmu/mmu_general.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/hw_ip/mmu/mmu_v1_0.h -->
## sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/hw_ip/mmu/mmu_v1_0.h

### Purpose
`mmu_v1_0.h` provides address-bit masks, shifts, and root/busy register offsets for the first HabanaLabs MMU generation.

### Important APIs, Types, And Functions
It defines HOP0 through HOP4 masks/shifts for a five-level 4 KiB-style walk and register offsets `MMU_HOP0_PA43_12`, `MMU_HOP0_PA49_44`, and `MMU_ASID_BUSY`.

### Control Flow
The header has no functions. MMU v1.0 code extracts hop indexes from virtual addresses using these masks/shifts, writes the split HOP0 physical address registers, and polls ASID busy state.

### State, Persistence, And Dependencies
State persists in MMU registers and page tables. This file depends on v1.0 hardware using the documented virtual-address layout and register addresses.

### Integration Points
It integrates with HabanaLabs MMU setup and map/unmap operations for devices using MMU v1.0.

### Risks
A wrong mask shifts the page-table walk to the wrong PTE. Root-address split fields are especially sensitive because an invalid HOP0 base breaks all translations for the ASID.

### Test Signals
Validate virtual-address-to-hop index calculations, root register programming for low/high physical bits, ASID busy polling, and translation of mappings that exercise each hop boundary.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/hw_ip/mmu/mmu_v1_0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/hw_ip/mmu/mmu_v1_1.h -->
## sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/hw_ip/mmu/mmu_v1_1.h

### Purpose
`mmu_v1_1.h` defines the v1.1 HabanaLabs MMU virtual-address hop layout and register offsets.

### Important APIs, Types, And Functions
The HOP0-HOP4 masks and shifts mirror the v1.0 five-hop layout. Register offsets differ: `MMU_ASID`, `MMU_HOP0_PA43_12`, `MMU_HOP0_PA49_44`, and `MMU_BUSY` live at the v1.1 MMU register block.

### Control Flow
No runtime code is present. Driver MMU code selects these constants for v1.1 devices, programs ASID/root registers, and waits for `MMU_BUSY` to clear after configuration.

### State, Persistence, And Dependencies
Persistent state is the configured ASID/root page table in hardware. The header depends on the v1.1 register map and common MMU flag/page definitions.

### Integration Points
It is used by HabanaLabs MMU v1.1 configuration paths and shares page-table format expectations with `mmu_general.h`.

### Risks
The layout similarity to v1.0 can hide register-base mistakes. Using `MMU_ASID_BUSY` from v1.0 on v1.1 or vice versa would poll the wrong hardware location.

### Test Signals
Tests should check ASID programming, HOP0 physical-address splits, busy polling, and mappings across hop boundaries on v1.1 ASICs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/hw_ip/mmu/mmu_v1_1.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/hw_ip/mmu/mmu_v2_0.h -->
## sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/hw_ip/mmu/mmu_v2_0.h

### Purpose
`mmu_v2_0.h` defines HabanaLabs MMU v2.0 hop masks and shifts for 4 KiB and 64 KiB page modes, plus a compact DMA-hop layout.

### Important APIs, Types, And Functions
It exports `HOP0_MASK_4K` through `HOP5_MASK_4K`, `HOP0_MASK_64K` through `HOP5_MASK_64K`, matching shift macros, and DMA aliases `DHOP0_MASK` through `DHOP4_MASK`/`DHOP*_SHIFT`.

### Control Flow
The file has no functions. MMU v2 code chooses the appropriate mask/shift set based on page size and extracts indexes for up to six hops; DMA mappings use the DHOP layout.

### State, Persistence, And Dependencies
State persists in page tables programmed by users of these constants. The header depends on hardware supporting distinct 4 KiB, 64 KiB, and DMA walk encodings.

### Integration Points
It integrates with v2 MMU map/unmap, contiguous-page optimization, and DMA address-space mapping logic in the HabanaLabs driver.

### Risks
Mixed page-size modes can be error-prone because HOP indexes shift by different amounts. DHOP4 uses a nonstandard mask/shift, so generic six-hop code must not accidentally reuse full 4 KiB HOP4 constants.

### Test Signals
Verify 4 KiB and 64 KiB mappings at each hop boundary, DMA-hop translations, large/contiguous mapping paths, and fault reports that decode the same virtual address indexes used during mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/hw_ip/mmu/mmu_v2_0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/hw_ip/pci/pci_general.h -->
## sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/hw_ip/pci/pci_general.h

### Purpose
`pci_general.h` defines common HabanaLabs PCI configuration access registers, status bits, and revision IDs.

### Important APIs, Types, And Functions
Macros identify ELBI PCI config address/data/control/status registers, the write bit, done/error status bits, and a status mask. `enum hl_revision_id` names legal PCI revision IDs `REV_ID_A` through `REV_ID_D`, with zero reserved as invalid.

### Control Flow
No executable code exists. PCI helper code writes config address/data/control, waits for done or error in status, and decodes PCI revision IDs through the enum.

### State, Persistence, And Dependencies
State is PCI configuration space and ELBI access status. The header depends on hardware exposing the config proxy at the fixed offsets.

### Integration Points
It is used by HabanaLabs PCI bring-up, revision-specific workarounds, config-space reads/writes, and diagnostics.

### Risks
Polling the wrong done/error bits can hang config access or miss failures. Treating `REV_ID_INVALID` as a real stepping could apply unsafe workarounds.

### Test Signals
Exercise config reads/writes through the ELBI window, error injection or invalid-address behavior, status mask clearing, and revision-based code paths for every supported stepping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/hw_ip/pci/pci_general.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/Kconfig -->
## sources/distributed-fs/ceph-client/drivers/accel/ivpu/Kconfig

### Purpose
`Kconfig` declares the Intel NPU/ivpu DRM accelerator driver and its optional debug mode.

### Important APIs, Types, And Functions
`DRM_ACCEL_IVPU` is a tristate depending on `DRM_ACCEL`, `X86_64 && !UML`, `PCI`, and `PCI_MSI`; it selects firmware loading, shmem GEM helpers, generic allocator, and device coredumps. `DRM_ACCEL_IVPU_DEBUG` enables extra debug behavior and unsafe module parameters.

### Control Flow
Kconfig controls whether the `intel_vpu` module is built and whether debug-only code paths are compiled. It also pulls in required subsystems through `select`.

### State, Persistence, And Dependencies
There is no runtime state. Build-time state determines module availability and debug feature exposure. The dependencies tie the driver to x86 PCI/MSI-capable systems.

### Integration Points
It integrates with the kernel DRM accel menu, firmware loader, GEM shmem infrastructure, generic allocator, devcoredump, debug module parameters, and the `drivers/accel/ivpu/Makefile`.

### Risks
Missing dependency selections would produce link/build failures or runtime feature gaps. Enabling debug mode exposes unsafe knobs such as firmware override and hardware fault injection paths.

### Test Signals
Build tests should cover built-in, module, disabled, and debug configurations; runtime tests should verify the module name `intel_vpu` and that firmware/debug/coredump features are present only when configured.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/Makefile -->
## sources/distributed-fs/ceph-client/drivers/accel/ivpu/Makefile

### Purpose
The `ivpu` Makefile defines the `intel_vpu` composite object and conditionally includes debugfs and coredump support.

### Important APIs, Types, And Functions
`intel_vpu-y` lists core objects for driver entry, firmware, logs, GEM, userptr, hardware, IPC, jobs, JSM, MMU, PM, sysfs, and tracing. `intel_vpu-$(CONFIG_DEBUG_FS)` adds `ivpu_debugfs.o`; `intel_vpu-$(CONFIG_DEV_COREDUMP)` adds `ivpu_coredump.o`; `obj-$(CONFIG_DRM_ACCEL_IVPU)` builds the module. Debug builds add `-DDEBUG`, and `ivpu_trace_points.o` gets an include path.

### Control Flow
There is no runtime flow. Kbuild uses the object list to link `intel_vpu.o` with optional instrumentation objects based on configuration.

### State, Persistence, And Dependencies
Build output state is the generated module or built-in object. The file depends on the object list matching source files and Kconfig symbols.

### Integration Points
It ties the Kconfig option to the ivpu driver implementation and ensures tracing, PM, MMU, job scheduling, sysfs, debugfs, and coredump objects are linked.

### Risks
Omitting an object causes unresolved symbols or missing runtime features. Conditional objects must match the stub headers, so debugfs/coredump disabled builds still compile through inline fallbacks.

### Test Signals
Build all relevant configs: `CONFIG_DRM_ACCEL_IVPU=m/y`, with and without `CONFIG_DEBUG_FS`, `CONFIG_DEV_COREDUMP`, and `CONFIG_DRM_ACCEL_IVPU_DEBUG`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_coredump.c -->
## sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_coredump.c

### Purpose
`ivpu_coredump.c` creates an Intel NPU device coredump containing a short header, firmware version, and firmware log buffers.

### Important APIs, Types, And Functions
`ivpu_dev_coredump()` computes a dump size from fixed header space, firmware version header size, and critical/verbose log BO sizes; fills a vmalloc buffer through a DRM coredump printer; prints firmware logs with `ivpu_fw_log_print()`; and submits the buffer through `dev_coredumpv()`.

### Control Flow
On failure paths such as firmware boot failure, callers invoke `ivpu_dev_coredump()`. It allocates the dump buffer, writes metadata/logs sequentially via `drm_printf()`, and hands ownership to devcoredump. Allocation failure silently skips dump generation.

### State, Persistence, And Dependencies
The dump is persistent through the devcoredump interface until consumed or expired. It depends on firmware BOs already existing and on firmware log buffer headers being parseable by `ivpu_fw_log_print()`.

### Integration Points
It integrates with firmware boot diagnostics, `CONFIG_DEV_COREDUMP`, DRM printers, firmware metadata, and log BOs allocated by `ivpu_fw_mem_init()`.

### Risks
The dump size is a worst-case allocation; log printer output may be smaller than allocated. If firmware log buffers are corrupted, log parsing can omit sections. Coredump generation must not be called after firmware BOs are freed.

### Test Signals
Force boot failure or recovery paths and verify devcoredump contains the header, firmware version, critical log, and verbose log without overrun or null dereference.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_coredump.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_coredump.h -->
## sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_coredump.h

### Purpose
`ivpu_coredump.h` declares the ivpu coredump hook and provides a logging-only fallback when devcoredump support is disabled.

### Important APIs, Types, And Functions
With `CONFIG_DEV_COREDUMP`, it declares `ivpu_dev_coredump(struct ivpu_device *vdev)`. Without it, the inline fallback creates a DRM info printer and dumps firmware logs with `ivpu_fw_log_print()`.

### Control Flow
Callers can invoke `ivpu_dev_coredump()` unconditionally. The compile-time branch either emits a devcoredump artifact or logs firmware buffers to the kernel log.

### State, Persistence, And Dependencies
No state is stored in the header. The fallback has no persistent coredump artifact, only log output. It depends on `ivpu_drv.h`, `ivpu_fw_log.h`, and DRM printer types.

### Integration Points
The header is included by driver boot/recovery code and hides `CONFIG_DEV_COREDUMP` from those callers.

### Risks
The fallback may produce less discoverable diagnostics than devcoredump. Both branches require valid firmware log buffers at call time.

### Test Signals
Compile with and without `CONFIG_DEV_COREDUMP`; trigger a failure and verify either a devcoredump file appears or firmware logs are printed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_coredump.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_debugfs.c -->
## sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_debugfs.c

### Purpose
`ivpu_debugfs.c` exposes ivpu debugfs files for BO listing, firmware identity and tracing, reset/recovery control, DVFS/profiling controls, dynamic clock throttling, hardware scheduler priority bands, and fault injection.

### Important APIs, Types, And Functions
Read-only show callbacks include `bo_list_show`, `fw_name_show`, `fw_version_show`, trace capability/config readers, boot mode and reset counters. Writable file ops update firmware dynamic debug, mark firmware logs read, drive profiling frequency, set trace masks/level via JSM, force recovery, reset/resume engines, configure DCT, and update HWS priority-band timings. `ivpu_debugfs_init()` registers the files.

### Control Flow
Initialization attaches standard DRM debugfs entries and custom files under the device root. Read paths pull data from `vdev`, firmware state, JSM queries, BO list, PM counters, or hardware counters. Write paths parse user input, mutate driver state, often send a JSM command or trigger PCI reset/recovery, and return the consumed byte count on success.

### State, Persistence, And Dependencies
Debugfs writes can persist in `vdev->fw` trace/DVFS fields, `vdev->hw->hws` priority-band arrays, PM DCT state, and hardware/firmware settings until reset or later writes. Dependencies include debugfs, DRM debugfs helpers, firmware log/JSM APIs, PM runtime/recovery, hardware helpers, and optional fault injection.

### Integration Points
This file is the main operator-facing diagnostic/control surface for the ivpu driver. It integrates with firmware trace configuration, DCT PM behavior, recovery work, hardware scheduler setup, and BO introspection.

### Risks
Several files are write-only control surfaces that can reset hardware or change scheduler timing. Trace config writes update cached driver state even if the JSM command fails because return values are not propagated. Priority-band parsing uses a compact text format and should reject partial input. Debug features are powerful and should remain gated by debugfs permissions/configuration.

### Test Signals
Mount debugfs and verify all files appear under the DRM device. Exercise reads, invalid writes, trace setting changes, `fw_log` mark-read behavior, `force_recovery`, DCT enable/disable on 40xx+, and priority-band updates with valid and invalid band IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_debugfs.h -->
## sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_debugfs.h

### Purpose
`ivpu_debugfs.h` declares debugfs initialization and provides a no-op stub when debugfs is disabled.

### Important APIs, Types, And Functions
The only API is `ivpu_debugfs_init(struct ivpu_device *vdev)`, either declared for `CONFIG_DEBUG_FS` or defined inline as an empty function.

### Control Flow
Driver probe calls `ivpu_debugfs_init()` unconditionally. Compile-time configuration decides whether files are registered.

### State, Persistence, And Dependencies
The header stores no state. When enabled, state is created in debugfs by the implementation; when disabled, no state is created. It depends only on a forward declaration of `struct ivpu_device`.

### Integration Points
It decouples `ivpu_drv.c` from debugfs configuration and matches the Makefile conditional object.

### Risks
The stub must remain signature-compatible with the real function so disabled-debugfs builds continue to compile.

### Test Signals
Build with and without `CONFIG_DEBUG_FS`; probe should succeed in both cases, with debugfs files present only in the enabled build.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_debugfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_drv.c -->
## sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_drv.c

### Purpose
`ivpu_drv.c` is the main Intel NPU DRM accelerator PCI driver. It owns module parameters, per-user/per-file context lifetime, DRM ioctls, firmware boot/shutdown orchestration, PCI/IRQ setup, device initialization/finalization, probe/remove, and PM/error-handler registration.

### Important APIs, Types, And Functions
Module parameters include debug mask, optional test mode, PLL ratio bounds, scheduler mode, contiguous-page disable, and forced snoop. File/context APIs include `ivpu_file_priv_get()`, `ivpu_file_priv_put()`, `ivpu_open()`, `ivpu_postclose()`, and user-limit helpers. Public lifecycle APIs are `ivpu_boot()`, `ivpu_prepare_for_reset()`, and `ivpu_shutdown()`. IOCTL handlers include get/set param and BO/job/metric/cmdq/userptr registrations. Probe paths include `ivpu_pci_init()`, `ivpu_irq_init()`, `ivpu_dev_init()`, `ivpu_dev_fini()`, `ivpu_probe()`, and `ivpu_remove()`.

### Control Flow
Probe allocates a managed DRM device, initializes core structs and xarrays, maps BAR0/BAR4, sets DMA mask, allocates MSI/MSI-X, initializes hardware from buttress registers, powers up, initializes global/reserved MMU contexts, firmware, IPC, PM, boots firmware, enables job-done consumption and PM, then registers DRM/debugfs/sysfs. Open enforces per-UID context limits, allocates an SSID from `context_xa`, initializes an MMU context, and stores `file_priv`. Close cleans metric streamer state and releases the context asynchronously through krefs. Boot writes firmware boot params, starts firmware, waits for a boot IPC message, enables IRQ/IPCs, and initializes DCT/HWS on cold boot. Teardown aborts jobs, disables PM/recovery, disables IRQ/IPC/MMU, shuts down hardware, cleans contexts and BOs, and destroys xarrays.

### State, Persistence, And Dependencies
Persistent driver state is in `struct ivpu_device`, `struct ivpu_file_priv`, xarrays for contexts/doorbells/jobs, BO lists, PM/firmware/MMU/IPC substructures, module parameters, and PCI power state. Hardware state includes BAR mappings, DMA mask, MSI vector, power/D0i3 state, firmware execution, and MMU contexts. Dependencies include DRM accel/GEM/PRIME, PCI/MSI/PM runtime, firmware loading, ivpu MMU/FW/IPC/job/JSM/PM/sysfs/debugfs helpers, and UAPI `ivpu_accel.h`.

### Integration Points
This file binds the driver to PCI IDs for MTL, ARL, LNL, PTL-P, WCL, and NVL. It is the UAPI entry point for params, BOs, submissions, metric streamer, cmd queues, and userptr BOs. It coordinates hardware and firmware subsystems through the boot/shutdown and reset paths.

### Risks
Initialization order is strict because later firmware/IPC/MMU code needs powered hardware and mapped BOs. Error unwinds must destroy xarrays and free contexts exactly once. `pm_runtime_get_sync()` in file release must be balanced with autosuspend. Per-UID limits use kref counts, so leaks can deny future opens. Boot timeout or invalid boot message triggers diagnostics and coredump; missing flushes/workqueue drains during reset can race with IRQ work.

### Test Signals
Test probe/remove across all PCI IDs, open/close under per-user context limits, all param queries, boot timeout/coredump path, runtime/system suspend-resume, PCI reset callbacks, PRIME import/export restrictions, device unplug with open files, and error unwind by injecting failures at PCI, IRQ, HW, MMU, FW, IPC, and boot stages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_drv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_drv.h -->
## sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_drv.h

### Purpose
`ivpu_drv.h` defines the central ivpu driver constants, debug macros, workaround table, device/file-private structures, module parameters, test-mode bits, lifecycle prototypes, and hardware-generation helpers.

### Important APIs, Types, And Functions
It defines PCI device IDs, hardware IP and buttress generations, SSID/doorbell/cmdq/job ID limits, platform IDs, debug masks, logging macros, `struct ivpu_wa_table`, `struct ivpu_user_limits`, `struct ivpu_device`, and `struct ivpu_file_priv`. Inline helpers include `ivpu_revision()`, `ivpu_device_id()`, `ivpu_hw_ip_gen()`, `ivpu_hw_btrs_gen()`, `to_ivpu_device()`, context/doorbell count helpers, platform predicates, and `ivpu_is_force_snoop_enabled()`.

### Control Flow
The inline generation helpers branch on PCI device ID to select hardware IP and buttress implementations. Platform helpers validate `vdev->platform` and classify silicon, Simics, FPGA, or HSLE.

### State, Persistence, And Dependencies
This header defines the in-memory state layout for the full driver. `ivpu_device` persists from probe to remove and owns BAR pointers, IRQ, subsystem pointers, MMU contexts, xarrays, work items, BO/job lists, counters, and timeouts. `ivpu_file_priv` persists per open DRM file and owns context, cmd queues, metric streamer state, limits, and abort/fault flags. Dependencies include DRM, PCI, xarray, hash table, MMU context, IPC, and ivpu UAPI headers.

### Integration Points
Nearly every ivpu source file includes this header. It is the contract between the PCI/DRM front end and firmware, MMU, IPC, PM, job, GEM, debugfs, and hardware layers.

### Risks
Structure layout and lock comments document ownership boundaries; violating them risks races in context/BO/job lists. Unknown PCI IDs return generation zero after logging/dump_stack, which downstream code must not treat as valid. Debug/test module parameters can change hardware behavior and should remain configuration-gated.

### Test Signals
Compile coverage across all source files, generation mapping tests for every PCI ID, lockdep on context/user-limit/BO/job locks, open/close stress, forced-snoop behavior, and platform predicate coverage after hardware platform init.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_drv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_fw.c -->
## sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_fw.c

### Purpose
`ivpu_fw.c` requests, validates, loads, and describes Intel NPU firmware. It parses firmware headers, chooses scheduler mode, allocates firmware/runtime/log/shave BOs, applies firmware-version-dependent workarounds, copies the image, and populates boot parameters for cold and warm boots.

### Important APIs, Types, And Functions
Public APIs are `ivpu_is_within_range()`, `ivpu_fw_init()`, `ivpu_fw_fini()`, `ivpu_fw_load()`, and `ivpu_fw_boot_params_setup()`. Key internal helpers include firmware request/name selection, API compatibility checks, scheduler selection, preemption-buffer parsing, firmware header parsing, workaround init, firmware BO allocation/free, and boot-parameter debug printing.

### Control Flow
Initialization requests a debug-override firmware or the first matching production firmware for the hardware IP generation. Parsing validates file size, header version, boot-parameter/version/runtime/image/read-only address ranges, entry point, SHAVE NN size, API major versions, scheduler mode, trace defaults, and preemption buffer sizes. Memory init creates runtime BOs at firmware-provided addresses, sets read-only pages in the global context, allocates critical/verbose log buffers, and optionally allocates SHAVE NN firmware memory. Loading zeros the image-load prefix, copies the firmware image, optionally clears the rest of runtime memory, and issues a write memory barrier. Boot-param setup either updates warm-boot variable fields or fills the full cold-boot structure.

### State, Persistence, And Dependencies
Persistent state is stored in `struct ivpu_fw_info`, firmware BOs mapped in the global MMU context, firmware log BOs, scheduler/trace/preemption/DVFS fields, entry points, and cached firmware version/name. Dependencies include Linux firmware loading, ivpu GEM/runtime BOs, hardware ranges/frequencies/telemetry, MMU context page protections, IPC buffer addresses, PM timestamps, boot/JSM API headers, and module parameters.

### Integration Points
`ivpu_dev_init()` calls firmware init before IPC boot. `ivpu_boot()` calls boot-param setup and hardware boot. Debugfs reads and updates trace/DVFS fields. Coredump/log paths consume firmware logs. JSM/HWS setup depends on selected scheduler mode and preemption buffer sizes.

### Risks
Firmware header validation is the security boundary for device-visible runtime addresses. `runtime_size = fw_hdr->runtime_size - boot_params_size - fw_version_size` relies on unsigned arithmetic and must be guarded by range checks. Trace and scheduler mode choices depend on API version. BO allocation unwind must free partially allocated resources. Warm-boot setup updates only variable fields, so stale cold-boot fields must remain valid.

### Test Signals
Use valid and malformed firmware images: small file, bad header version, invalid ranges, oversized image/SHAVE NN, incompatible API, old/new JSM versions, HW/OS scheduler selection, preemption buffer limits, read-only section validation, cold and warm boot parameter contents, and log buffer allocation sizes for each log level.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_fw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_fw.h -->
## sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_fw.h

### Purpose
`ivpu_fw.h` defines firmware metadata/state and declares firmware lifecycle and boot-parameter APIs.

### Important APIs, Types, And Functions
`struct ivpu_fw_info` stores the firmware file/name/version, BOs for boot params/version/runtime/SHAVE/logs, firmware-provided addresses and sizes, image offsets, entry points, boot modes, trace config, DVFS mode, preemption buffer sizes, read-only section, scheduler mode, and heartbeat. It declares `ivpu_is_within_range()`, `ivpu_fw_init()`, `ivpu_fw_fini()`, `ivpu_fw_load()`, and `ivpu_fw_boot_params_setup()`. Inline helpers are `ivpu_fw_is_warm_boot()` and `ivpu_fw_preempt_buf_size()`.

### Control Flow
The header itself has only inline checks. Runtime code uses `next_boot_mode` to choose warm versus cold boot and sums primary/secondary preemption buffer sizes for UAPI capability reporting.

### State, Persistence, And Dependencies
Firmware state persists in `vdev->fw` from init to fini and is updated across resets/boots. Dependencies are firmware boot and JSM API definitions plus ivpu BO/device declarations.

### Integration Points
The struct is consumed by driver boot, hardware CPU entry-point programming, debugfs, firmware log/coredump, PM warm boot, and UAPI param handling.

### Risks
All address/size fields are device-visible ABI from firmware; users must validate before allocation/use. Boot mode fields must be updated consistently or warm boot may jump to an invalid entry point.

### Test Signals
Check firmware state after init, after cold boot, after warm boot, after fini, and through debugfs/UAPI paths that read version, scheduler mode, capabilities, and preemption buffer size.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_fw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_fw_log.c -->
## sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_fw_log.c

### Purpose
`ivpu_fw_log.c` parses and prints firmware tracing ring buffers stored in ivpu BOs, and tracks read positions for incremental debugfs reads.

### Important APIs, Types, And Functions
The module parameter `ivpu_fw_log_level` sets the default firmware log level. Public APIs are `ivpu_fw_log_print()`, `ivpu_fw_log_mark_read()`, and `ivpu_fw_log_reset()`. Internal helpers validate tracing buffer headers, split printable lines, handle wrap-around, and walk all log buffers in a BO.

### Control Flow
Printing walks critical and verbose log BOs from offset zero, repeatedly validates a `vpu_tracing_buffer_header`, and prints either all data or only unread data. Ring-buffer wrap handling compares firmware `write_index`/`wrap_count` with driver `read_index`/`read_wrap_count`. Mark-read advances read fields to current write positions; reset clears read positions.

### State, Persistence, And Dependencies
Persistent state is in firmware-owned tracing buffer headers inside cached/mappable BOs, including write/read indexes and wrap counts. The driver writes read indexes back to shared memory. Dependencies include firmware boot tracing ABI, ivpu GEM virtual mappings, DRM printers, and ctype filtering.

### Integration Points
Debugfs `fw_log`, coredump generation, fallback coredump logging, and firmware boot diagnostics all call this file. Firmware boot params point firmware at the log BO addresses and sizes.

### Risks
Corrupted log headers must not cause overreads; size and canary checks guard this. Read-index writes are shared with firmware and need memory-order expectations. Line splitting drops nonprintable characters except control characters and can emit partial lines at 255 characters.

### Test Signals
Test empty logs, single and multiple tracing buffers, wrap/no-wrap cases, only-new reads, corrupted canary/header size/size bounds, mark-read/reset behavior, and coredump/debugfs output formatting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_fw_log.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_fw_log.h -->
## sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_fw_log.h

### Purpose
`ivpu_fw_log.h` defines firmware log levels, firmware log buffer sizes, and firmware log helper prototypes.

### Important APIs, Types, And Functions
It exports log-level constants from default through fatal, verbose buffer sizes of 1 MiB and 8 MiB, critical buffer size of 512 KiB, `ivpu_fw_log_level`, and prototypes for print/mark-read/reset functions.

### Control Flow
There is no executable flow except consumers passing `only_new_msgs` to the print API to choose full versus incremental reads.

### State, Persistence, And Dependencies
The header stores no state beyond the extern module parameter declaration. Buffer size macros affect persistent BO allocation in firmware init.

### Integration Points
It is included by firmware allocation, debugfs, coredump, and fallback diagnostics.

### Risks
Changing buffer sizes changes firmware boot-parameter expectations and memory footprint. Log-level constants must match firmware API values.

### Test Signals
Verify BO sizes allocated for critical/verbose logs, module parameter parsing, boot params carrying log addresses/sizes, and debugfs/coredump compilation with this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_fw_log.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_gem.c -->
## sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_gem.c

### Purpose
`ivpu_gem.c` implements ivpu GEM/shmem buffer objects, VPU virtual-address allocation, DMA/IOMMU mapping, MMU binding/unbinding, PRIME import, BO creation/info/wait ioctls, and BO diagnostics.

### Important APIs, Types, And Functions
Core APIs include `ivpu_bo_bind()`, `ivpu_bo_unbind_all_bos_from_context()`, `ivpu_gem_create_object()`, `ivpu_gem_prime_import()`, `ivpu_bo_create()`, `ivpu_bo_create_runtime()`, `ivpu_bo_create_global()`, `ivpu_bo_free()`, `ivpu_bo_create_ioctl()`, `ivpu_bo_info_ioctl()`, `ivpu_bo_wait_ioctl()`, `ivpu_bo_list()`, and `ivpu_bo_list_print()`. The GEM object funcs implement free/open/status plus shmem pin/vmap/mmap helpers.

### Control Flow
Allocation validates cache flags, creates a shmem GEM object, marks WC mapping when requested, and adds it to `vdev->bo_list`. GEM open allocates a VPU VA in the file context using user, shave, or DMA range based on flags. Bind obtains an sg_table from shmem or dma-buf import, maps it into the ivpu MMU context at `bo->vpu_addr`, and records `mmu_mapped`. Free removes the BO from the list, unmaps MMU and DMA/sg resources under reservation lock, and releases shmem. Runtime/global helpers allocate device-internal BOs, bind them immediately, and vmap mappable buffers. Wait ioctl waits on the reservation object and returns command-buffer job status.

### State, Persistence, And Dependencies
BO state is split across DRM GEM/shmem fields, `struct ivpu_bo`, `drm_mm_node` VPU VA allocation, sg_table/DMA mappings, MMU page tables, and the global BO list. Dependencies include DRM shmem/GEM/PRIME, dma-buf, dma-resv, ivpu MMU context, hardware address ranges, and UAPI BO flags.

### Integration Points
Firmware, IPC, jobs, command queues, user allocations, PRIME import, debugfs BO listing, and MMU context cleanup all use this BO layer.

### Risks
Unbind order is delicate: MMU unmap, address range removal, DMA unmap, sg free, and imported attachment unmap differ by BO origin. BOs can belong to only one context; re-opening in another context returns `-EALREADY`. Imported objects are not re-exportable in `ivpu_drv.c`. Missing reservation locking can race map/free. User-visible flags select security-sensitive address ranges.

### Test Signals
Test BO creation with all valid/invalid flags, mmap/vmap paths, context close unbinds, PRIME import and no re-export, bind failures, wait timeout and completion status, runtime/global BO allocation, list output, and fault/unwind paths under MMU map or DMA map failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_gem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_gem.h -->
## sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_gem.h

### Purpose
`ivpu_gem.h` defines the ivpu buffer-object structure and declares BO/GEM creation, binding, ioctl, and diagnostic helpers.

### Important APIs, Types, And Functions
`struct ivpu_bo` embeds `drm_gem_shmem_object`, tracks the owning MMU context, BO list node, VPU VA `drm_mm_node`, flags, job status, context ID, and MMU-mapped state. Inline helpers convert GEM to ivpu BO, get CPU VADDR/size/cache mode/device, determine snooping/read-only/resident/mappable state, and convert between CPU and VPU addresses within a BO.

### Control Flow
The inline address conversion helpers validate that the address lies within the BO range before returning a translated pointer/address. Snooping depends on global forced snoop or cached BO mode.

### State, Persistence, And Dependencies
The structure persists for each GEM object until final put. It depends on DRM GEM shmem, DRM MM, ivpu driver structures, and UAPI flags.

### Integration Points
Every firmware, IPC, job, and memory path that allocates or translates device-visible memory uses this header.

### Risks
`cpu_to_vpu_addr()` returns `u32`, so callers must be aware of address ranges and truncation expectations. `ivpu_bo_vaddr()` is valid only for vmapped/mappable BOs. `job_status` is meaningful only for command buffers.

### Test Signals
Compile and runtime tests should verify address conversion boundaries, cache/snoop flag behavior, read-only mapping propagation, BO residency status, and safe use of unmapped BO virtual addresses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_gem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_gem_userptr.c -->
## sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_gem_userptr.c

### Purpose
`ivpu_gem_userptr.c` implements the UAPI path that turns page-aligned userspace memory into an ivpu BO by long-term pinning pages, exporting them as a dma-buf, and importing that dma-buf through the normal GEM path.

### Important APIs, Types, And Functions
The exported ioctl is `ivpu_bo_create_from_userptr_ioctl()`. Internal pieces include custom dma-buf ops for map/unmap/release, `ivpu_create_userptr_dmabuf()` to pin pages and build an sg_table, and `ivpu_bo_create_from_userptr()` to import the dma-buf and assign ivpu flags.

### Control Flow
The ioctl validates flags, nonzero pointer/size, page alignment, and `access_ok()`. Creation pins pages with `FOLL_LONGTERM` and `FOLL_WRITE` unless read-only, creates an sg_table over all pages, exports it as a dma-buf, imports it via `ivpu_gem_prime_import()`, creates a GEM handle, and returns the VPU address. Release unpins pages and frees the sg_table when the dma-buf is destroyed.

### State, Persistence, And Dependencies
Persistent state includes long-term pinned user pages, a dma-buf carrying the sg_table, the imported GEM object, VPU VA allocation, and eventual MMU mapping. Dependencies include GUP, dma-buf, sg tables, DRM GEM, ivpu PRIME import, and UAPI userptr flags.

### Integration Points
This provides `DRM_IVPU_BO_CREATE_FROM_USERPTR`, allowing userspace to submit existing memory to the NPU through the same BO/MMU path as shmem and imported dma-buf objects.

### Risks
Long-term pins can affect memory migration and must be released on every error path. Read-only flags control whether `FOLL_WRITE` is used and whether later MMU mappings are read-only. Only aligned full-page ranges are supported. The exported dma-buf uses `DMA_ATTR_SKIP_CPU_SYNC`, so cache coherency assumptions must match ivpu snooping/cache mode.

### Test Signals
Test invalid flags, null/unaligned/inaccessible ranges, partial GUP failure, sg allocation/export/import failure unwind, read-only versus writable pin flags, handle creation failure, context close/free releasing pins, and actual NPU access to userptr BOs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_gem_userptr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_hw.c -->
## sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_hw.c

### Purpose
`ivpu_hw.c` provides generation-independent hardware orchestration for platform detection, workarounds, timeouts, memory ranges, power up/down, firmware boot, IRQ dispatch, profiling clock choice, and ECC MCA signaling.

### Important APIs, Types, And Functions
Public functions include `ivpu_hw_init()`, `ivpu_hw_range_init()`, `ivpu_hw_power_up()`, `ivpu_hw_power_down()`, `ivpu_hw_reset()`, `ivpu_hw_boot_fw()`, `ivpu_hw_profiling_freq_drive()`, `ivpu_irq_handlers_init()`, `ivpu_hw_irq_enable()`, `ivpu_hw_irq_disable()`, `ivpu_hw_irq_handler()`, and `ivpu_hw_uses_ecc_mca_signal()`. Internal helpers initialize platform, workarounds, timeouts, priority bands, and memory ranges.

### Control Flow
Hardware init reads buttress info/fuses/frequencies, sets HWS priority defaults, initializes VPU address ranges by IP generation, reads platform, initializes workarounds and timeouts, and prepares optional fault injection. Power-up disables D0i3, enables workpoint/PLL, applies LNL clock/profiling/ATS setup, configures host SS, disables idle generation, waits clock ownership, powers the IP domain, enables AXI and top NoC, and writes LNL arbitration weights. Power-down saves D0i3 timestamps, warns if not idle, resets IP, disables workpoint, and enters D0i3. IRQ handling globally masks buttress interrupts, dispatches buttress then IP handlers, reenables global interrupts, and marks PM activity.

### State, Persistence, And Dependencies
Hardware state includes PLL/workpoint, power islands, D0i3 timestamps, platform, workarounds, timeout values, address ranges, IRQ handler function pointers, and firewall IRQ counter. Dependencies include buttress/IP helper layers, PM runtime, MSR reads for ECC, DMI/fault injection headers, and module test parameters.

### Integration Points
`ivpu_drv.c` calls this during device init, boot, shutdown, and IRQ handling. Firmware boot params consume ranges, PLL ratios, telemetry, and ECC signaling. Debugfs can alter profiling frequency and fault injection.

### Risks
Power sequencing is strict and generation-sensitive. Workarounds can be forced by test mode and may change power/clock behavior. IRQ dispatch skips IP handling when hardware is idle and buttress handled the interrupt, which relies on accurate idle status. Memory range differences between 37xx and newer generations affect every BO mapping.

### Test Signals
Test hardware init on each PCI ID/revision/platform, range boundaries, power-up/power-down/reset error injection, IRQ paths for buttress/IP/no interrupt, profiling frequency toggles, D0i3 timestamp propagation to warm boot, and ECC MCA MSR behavior on 50xx+.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_hw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_hw.h -->
## sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_hw.h

### Purpose
`ivpu_hw.h` defines shared ivpu hardware state, address ranges, hardware lifecycle APIs, and inline adapters over buttress/IP-specific helpers.

### Important APIs, Types, And Functions
`struct ivpu_addr_range` stores `[start,end)` ranges. `struct ivpu_hw_info` stores IRQ callbacks, runtime/global/user/shave/dma ranges, PLL data, HWS priority-band parameters, tile fuse, SKU, config, DMA address width, D0i3 timestamps, and firewall IRQ counter. The header declares hardware init/power/reset/boot/IRQ APIs and provides inline wrappers for frequency, IRQ clear, diagnostics, telemetry, idle checks, IPC TX/RX, and doorbells.

### Control Flow
Inline wrappers route generic callers to buttress or IP functions. IRQ handler pointers installed at runtime select 37xx/40xx IP and MTL/LNL buttress behavior.

### State, Persistence, And Dependencies
`ivpu_hw_info` persists for the device lifetime. State maps directly to hardware registers and firmware boot-parameter inputs. Dependencies are ivpu driver, buttress, and IP headers.

### Integration Points
The header is the generic hardware contract used by driver init, firmware, PM, IPC, MMU, debugfs, and job submission code.

### Risks
Ranges use `end` as exclusive size calculations; off-by-one misuse can expose memory outside intended VPU VA windows. Inline wrappers assume function pointers and sublayers were initialized before use.

### Test Signals
Verify range size calculations, wrapper calls after hardware init, all function-pointer selections, telemetry/frequency values, idle/wait-for-idle behavior, and doorbell/IPC access through generic APIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_hw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_hw_37xx_reg.h -->
## sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_hw_37xx_reg.h

### Purpose
`ivpu_hw_37xx_reg.h` is the register and bit-mask map for ivpu 37xx IP blocks used by the hardware IP implementation.

### Important APIs, Types, And Functions
It defines host subsystem clock/reset, NoC QREQ/QACCEPT/QDENY, firewall IRQ enable, ICB status/clear/enable, IPC FIFO, AON power/isolation/idle/DPU-active registers, firmware loading address, workpoint mirror, TCU/TBU MMU/snoop override registers, CPU debug/timer/watchdog registers, performance counter, and doorbell registers with masks.

### Control Flow
There is no code flow. `ivpu_hw_ip.c` uses these macros through `REGV_*` and `REG_*` helpers for 37xx-specific power, boot, IRQ, watchdog, IPC, and doorbell sequences.

### State, Persistence, And Dependencies
Persistent state is hardware register state. The header depends on Linux bit macros and on register offsets matching BAR0 RegV layout for 37xx devices.

### Integration Points
It integrates with 37xx host SS bring-up, firmware boot entry, NPU IRQ dispatch, MMU TBU setup, IPC FIFO access, and doorbell ringing.

### Risks
Register maps are low-level hardware ABI. Wrong offsets/masks can power the wrong island, fail to clear interrupts, corrupt TBU snoop settings, or ring the wrong doorbell. Similar names across 37xx/40xx require generation-correct selection.

### Test Signals
Validate register read/write traces during 37xx probe/boot, IRQ status decoding, watchdog disable, IPC FIFO drain, doorbell stride, power-island status polling, and TBU MMU valid bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_hw_37xx_reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_hw_40xx_reg.h -->
## sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_hw_40xx_reg.h

### Purpose
`ivpu_hw_40xx_reg.h` maps ivpu 40xx and later host/IP registers used by generic 40xx/50xx/60xx hardware code.

### Important APIs, Types, And Functions
It defines host SS clock/reset enables, NoC handshakes, firewall IRQ enable, ICB status/clear/enable, IPC FIFO/status, AON power/isolation/idle registers, 50xx power-island delay/fabric override registers, firmware verification address, workpoint mirror, TCU/TBU overrides, CPU NoC handshakes, watchdog/timer/perf counter, and doorbell offsets/masks.

### Control Flow
No executable logic is present. `ivpu_hw_ip.c` selects this map for hardware IP 40xx and above for host SS, power island, top NoC, snoop/TBU, CPU boot, IRQ, IPC, and doorbell operations.

### State, Persistence, And Dependencies
State lives in hardware registers. The header depends on Linux bit macros and BAR0 RegV layout for 40xx+ devices, including 50xx-only delay registers.

### Integration Points
It underpins power/boot/IRQ handling for LNL/PTL/WCL/NVL-class devices and shares many helper flows with the 37xx map through generation-specific wrappers.

### Risks
Some masks differ subtly from 37xx, such as hostif L2 cache bit positions and CSS/MSS naming. 50xx delay/fabric registers must not be used on older IP generations.

### Test Signals
Test boot/power sequencing on 40xx, 50xx, and 60xx devices, register traces for NoC and CPU handshakes, 50xx power delay programming, IRQ decode/clear, IPC FIFO fill-level reads, and doorbell writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_hw_40xx_reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_hw_btrs.c -->
## sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_hw_btrs.c

### Purpose
`ivpu_hw_btrs.c` implements buttress-side hardware control for fuses, PLL/workpoint requests, D0i3, IP reset, LNL arbitration and profiling settings, idle/frequency queries, buttress IRQ handling, dynamic clock throttling mailbox, telemetry registers, global/local interrupt masks, diagnostics, and platform reading.

### Important APIs, Types, And Functions
Public functions match `ivpu_hw_btrs.h`: info/frequency init, interrupt clear workaround detection, workpoint drive, D0i3 enable/disable, clock ownership wait, idle checks, IP reset, profiling/ATS/clock-relinquish controls, frequency getters, MTL/LNL IRQ handlers, DCT request/status, telemetry getters, IRQ mask controls, diagnostics, and platform read. Internal helpers split MTL and LNL register programming.

### Control Flow
Init reads fuses and PLL ratios, clamps them with module parameters, and records tile/SKU/config data. Workpoint drive syncs the request command, writes generation-specific payloads, polls PLL lock/status ready, and on disable waits for CDYN deassertion on LNL. D0i3 drive polls in-progress, toggles the I3 bit, and polls completion. IRQ handlers read status, log frequency/error details, clear source error registers, clear local status, and trigger PM recovery for fatal errors or queue DCT work for survivability interrupts.

### State, Persistence, And Dependencies
Buttress state includes PLL ratios, workpoint, D0i3 state, tile fuse/SKU, telemetry registers, port weights, interrupt masks/status, PCODE mailbox status, and error logs. Dependencies include MTL/LNL buttress register headers, generic reg I/O helpers, PM recovery/DCT work, units constants, and ivpu generation helpers.

### Integration Points
`ivpu_hw.c` uses this layer for platform/frequency info, power transitions, reset, idle checks, telemetry boot params, IRQ dispatch, and diagnostics. Debugfs/PM use DCT and profiling-related hooks.

### Risks
MTL and LNL semantics differ: interrupt clear behavior, PLL lock, CDYN, tile fuse, and platform registers are generation-specific. The diagnostic LNL helper reads `VPU_HW_BTRS_MTL_INTERRUPT_STAT` while using LNL masks, which is suspicious and should be reviewed against intended register offset. Workpoint request timeouts prevent boot. Fatal IRQ handling must clear sources before status to avoid retrigger storms.

### Test Signals
Test fuse parsing, PLL clamp parameters, workpoint enable/disable, D0i3 transitions, IP reset, idle polling, MTL interrupt-clear workaround detection, ATS/UFI/CFI/IMR/SURV IRQ handling, DCT mailbox parsing, telemetry reads, and PM recovery triggers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_hw_btrs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_hw_btrs.h -->
## sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_hw_btrs.h

### Purpose
`ivpu_hw_btrs.h` declares the buttress hardware API and shared constants for profiling frequency and DCT defaults.

### Important APIs, Types, And Functions
It exposes `PLL_PROFILING_FREQ_DEFAULT`, `PLL_PROFILING_FREQ_HIGH`, `DCT_DEFAULT_ACTIVE_PERCENT`, `DCT_PERIOD_US`, and prototypes for buttress info/frequency/power/reset/idle/IRQ/DCT/telemetry/diagnostic/platform functions.

### Control Flow
The header has no logic. Callers invoke these APIs through `ivpu_hw.c` or inline wrappers in `ivpu_hw.h` to perform generation-specific buttress work.

### State, Persistence, And Dependencies
State is maintained in hardware registers and `vdev->hw` by the implementation. The header depends on driver, 37xx/40xx register maps, and register I/O helpers.

### Integration Points
This is the interface boundary between common hardware orchestration and MTL/LNL buttress register programming.

### Risks
The API assumes callers have selected the correct buttress generation and that BAR4 is mapped. Constants must match firmware/PM expectations for profiling clock and DCT behavior.

### Test Signals
Compile coverage for every prototype, runtime tests of each public hook through common hardware/PM/debugfs flows, and generation selection checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_hw_btrs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_hw_btrs_lnl_reg.h -->
## sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_hw_btrs_lnl_reg.h

### Purpose
`ivpu_hw_btrs_lnl_reg.h` maps Lunar Lake/newer buttress registers and bit masks.

### Important APIs, Types, And Functions
It defines interrupt status/masks for frequency, ATS, CFI, IMR, and survivability errors; local/global interrupt masks; ATS and error log/clear registers; port arbitration weights; PCODE mailbox status/shadow; workpoint payload/command; PLL/CDYN; tile fuse; VPU status; IP reset; D0i3; telemetry; and FMIN/FMAX fuses.

### Control Flow
No executable code exists. `ivpu_hw_btrs.c` uses these constants to implement LNL-class PLL, reset, D0i3, IRQ, telemetry, tile-fuse, DCT, and platform operations.

### State, Persistence, And Dependencies
State persists in BAR4 buttress registers. The header depends on Linux bit macros and accurate LNL register offsets.

### Integration Points
It supports LNL, PTL-P, WCL, and NVL buttress flows selected by `ivpu_hw_btrs_gen()`.

### Risks
Masks are used with generic field macros; any typo changes hardware behavior. Platform, clock relinquish, and telemetry fields are consumed by firmware boot and PM, so wrong decoding propagates outside buttress code.

### Test Signals
Validate interrupt decoding, tile-fuse valid/config fields, PLL ratio reads, D0i3/IP reset polling, PCODE DCT command/status exchange, telemetry boot-param values, and platform field decoding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_hw_btrs_lnl_reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_hw_btrs_mtl_reg.h -->
## sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_hw_btrs_mtl_reg.h

### Purpose
`ivpu_hw_btrs_mtl_reg.h` maps Meteor Lake/Arrow Lake buttress registers and bit masks.

### Important APIs, Types, And Functions
It defines interrupt type/status, workpoint payload/command/download/current PLL, PLL enable/status, FMIN/FMAX fuses, tile fuse/SKU, local/global interrupt masks, VPU ready/idle status, D0i3 control, IP reset, telemetry registers, ATS error logs/clear, and UFI error log/clear fields.

### Control Flow
No executable logic exists. MTL buttress implementation uses these constants for PLL workpoints, D0i3, reset, idle/frequency queries, interrupt handling, telemetry, and diagnostics.

### State, Persistence, And Dependencies
State lives in BAR4 buttress registers. The header depends on Linux bit macros and MTL register layout.

### Integration Points
It supports MTL and ARL devices selected by `ivpu_hw_btrs_gen() == IVPU_HW_BTRS_MTL`.

### Risks
MTL has an interrupt-clear-with-zero workaround detection path; status semantics must be exact. UFI/ATS error fields feed recovery decisions, so incorrect masks reduce diagnostics or miss fatal errors.

### Test Signals
Test workpoint payload programming, PLL lock/status polling, interrupt status clearing behavior, ATS/UFI error log decode, telemetry fields, and D0i3/IP reset transitions on MTL-class hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_hw_btrs_mtl_reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_hw_ip.c -->
## sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_hw_ip.c

### Purpose
`ivpu_hw_ip.c` implements IP-side register programming for host subsystem configuration, idle generation, power islands, clocks/resets, NoC handshakes, snoop/TBU setup, firmware CPU boot, watchdog disable, IRQ enable/clear/dispatch/diagnostics, IPC FIFO access, doorbells, and 50xx fabric/power-delay controls.

### Important APIs, Types, And Functions
Public APIs include `ivpu_hw_ip_host_ss_configure()`, idle-gen enable/disable, `ivpu_hw_ip_pwr_domain_enable()`, `ivpu_hw_ip_host_ss_axi_enable()`, `ivpu_hw_ip_top_noc_enable()`, perf timer read, snoop disable, TBU MMU enable, SOC CPU boot, watchdog disable, diagnostics, IPC RX count/address and TX write, IRQ enable/disable/clear/handlers, and doorbell set. Internal helpers are split into 37xx and 40xx/50xx/60xx variants.

### Control Flow
Host SS configuration checks BAR readiness on 37xx, clears resets, and verifies NoC handshake lines are idle. Power-domain enable programs 50xx delay registers when needed, enables trickle/main power island bits, waits status, enables host clocks, disables isolation, asserts resets, and marks 37xx DPU active. AXI and top NoC enable set QREQN bits and verify QACCEPTN/QDENY. Firmware boot disables snoop, enables TBU SSID valid bits, drives SOC CPU/sets entry point by generation, and logs warm/cold mode. IRQ handlers clear status, dispatch MMU event/global errors, IPC FIFO handling, watchdog recovery, and NOC firewall accounting.

### State, Persistence, And Dependencies
State persists in BAR0 RegV registers: clocks, resets, power islands, NoC handshakes, snoop/TBU overrides, CPU entry point, watchdog, IPC FIFO, doorbells, and IRQ masks/status. Dependencies include 37xx/40xx register maps, reg I/O helpers, firmware entry points, MMU IRQ handlers, IPC IRQ handler, PM recovery, and hardware generation helpers.

### Integration Points
`ivpu_hw.c` calls this during power-up and firmware boot. `ivpu_ipc.c` uses the IPC FIFO wrappers. Job/cmdq code uses doorbells through `ivpu_hw_db_set()`. MMU and PM recovery receive IRQ callbacks from this layer.

### Risks
Generation-specific helpers are easy to mix because 37xx and 40xx offsets often share names but not semantics. The `pwr_island_drive_37xx()`/`pwr_island_drive_40xx()` bodies reference opposite register-prefix names, which should be verified against shared offsets or corrected if unintended. Handshake polling returns `-EIO` on unexpected bits but does not retry except through higher-level sequencing. IRQ FIFO draining must purge all messages or future IPC interrupts may stop.

### Test Signals
Test host SS configuration, power island enable, NoC handshakes, firmware boot entry programming for cold/warm and 37xx/40xx/60xx, snoop override with and without forced snoop, TBU valid bits, watchdog recovery IRQs, MMU/IPC IRQ dispatch, NOC firewall counter, IPC FIFO drain, and doorbell stride/index writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_hw_ip.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_hw_ip.h -->
## sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_hw_ip.h

### Purpose
`ivpu_hw_ip.h` declares the IP-side hardware operations used by common hardware, IPC, PM, MMU, and job paths.

### Important APIs, Types, And Functions
The API covers host SS configuration, idle generation, power-domain and NoC enabling, perf timer read, snoop/TBU setup, SOC CPU boot, watchdog disable, diagnostics, IPC FIFO count/address/TX, IRQ clear/enable/disable and generation-specific IRQ handlers, doorbell set, and 50xx fabric request override.

### Control Flow
There is no implementation in the header. Callers select these functions through common wrappers or direct calls during power-up, boot, interrupt handling, and IPC/job operations.

### State, Persistence, And Dependencies
State lives in hardware registers touched by the implementation. The header depends on `ivpu_drv.h` and a valid `struct ivpu_device`.

### Integration Points
It forms the boundary between generic driver logic and RegV IP-specific programming in `ivpu_hw_ip.c`.

### Risks
Functions assume RegV is mapped and hardware is in the correct power state. 50xx fabric override hooks should only be used on supporting generations.

### Test Signals
Build/link coverage for all prototypes and runtime coverage through hardware init/boot/IPC/IRQ/job paths on each IP generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_hw_ip.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_hw_reg_io.h -->
## sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_hw_reg_io.h

### Purpose
`ivpu_hw_reg_io.h` provides register read/write/poll helpers and field manipulation macros for ivpu BAR register access with debug tracing and optional fault injection.

### Important APIs, Types, And Functions
Macros `REGB_*` and `REGV_*` wrap reads/writes against buttress and IP BARs. Field macros include `REG_FLD`, `REG_FLD_NUM`, `REG_GET_FLD`, `REG_CLR_FLD`, `REG_SET_FLD`, `REG_SET_FLD_NUM`, and tests. Poll macros call `ivpu_hw_reg_poll_fld()`. Inline functions implement 32/64-bit reads/writes, indexed writes, and polling.

### Control Flow
Callers invoke register macros with a local `vdev`. Polling logs start, uses `read_poll_timeout()` until `(value & mask) == expected`, optionally forces timeout through fault injection, logs completion, and returns status.

### State, Persistence, And Dependencies
State is hardware register state. The helper also depends on global fault attribute `ivpu_hw_failure` when fault injection is enabled. It requires mapped `vdev->regb`/`regv` and register/mask macro naming conventions.

### Integration Points
All hardware buttress and IP files use this header for register I/O, making it the common tracing and fault-injection point for hardware tests.

### Risks
Macros assume the caller has a variable named `vdev`; misuse can produce confusing compile errors. `REG_IO_ERROR` is `0xffffffff`, which can also be a valid raw register value for some registers, so callers should use it only where documented. Poll sleep/timeout values affect boot/recovery latency.

### Test Signals
Enable register debug mask and verify read/write traces, inject `ivpu_hw_failure` to force poll timeouts, test field set/get macros with known masks, and validate indexed doorbell writes produce expected offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_hw_reg_io.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_ipc.c -->
## sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_ipc.c

### Purpose
`ivpu_ipc.c` implements the host-firmware IPC transport over shared memory and hardware FIFOs. It allocates TX/RX buffers, sends JSM messages, receives synchronous and callback responses, drains IPC interrupts, and aborts consumers on shutdown.

### Important APIs, Types, And Functions
Public APIs include `ivpu_ipc_init()`, `ivpu_ipc_fini()`, `ivpu_ipc_enable()`, `ivpu_ipc_disable()`, `ivpu_ipc_reset()`, `ivpu_ipc_irq_handler()`, `ivpu_ipc_irq_work_fn()`, consumer add/delete, `ivpu_ipc_send()`, `ivpu_ipc_receive()`, `ivpu_ipc_send_receive_internal()`, `ivpu_ipc_send_receive()`, and `ivpu_ipc_send_and_wait()`. Internal helpers prepare/release TX buffers, mark RX buffers free, match consumers by channel/request ID, and queue received messages.

### Control Flow
Init allocates global WC/mappable TX and RX BOs, creates a 64-byte-aligned gen_pool over TX memory, initializes locks/lists, and resets shared memory. Send locks IPC state, rejects sends when disabled, allocates a TX buffer, fills IPC and JSM headers/payload/request ID, flushes with `wmb()`, and writes the TX VPU address to the hardware FIFO. IRQ handling drains all RX FIFO entries, translates VPU addresses into RX BO CPU pointers, validates JSM payloads, enforces a max queued RX count, matches a consumer, and either queues synchronous messages or callback work. Receive waits on the consumer queue, handles aborts/timeouts, copies headers/payloads, checks JSM result, traces, marks buffers free, and removes the queued message. High-level send/receive wraps runtime PM and probes firmware heartbeat on timeout to trigger recovery if the heartbeat also times out.

### State, Persistence, And Dependencies
State lives in `struct ivpu_ipc_info`: TX gen_pool, TX/RX BOs, consumer/callback lists, request counter, RX message count, lock, and on/off flag. Each `ivpu_ipc_consumer` stores channel, last TX address, request ID, abort state, callback, RX list, spinlock, and waitqueue. Shared memory status fields persist until firmware/driver marks them free. Dependencies include ivpu GEM global BOs, hardware IPC FIFO wrappers, PM runtime, JSM API/messages, tracepoints, genalloc, waitqueues, and spinlocks.

### Integration Points
Firmware boot waits for the boot IPC channel. JSM command helpers, debugfs trace/control, PM, jobs, and metric streamer use IPC send/receive. Hardware IRQ dispatch calls `ivpu_ipc_irq_handler()` on HOST_IPC_FIFO interrupts.

### Risks
IPC must drain the FIFO fully or future interrupts may not fire. TX buffers are freed when consumers are deleted, so long-lived consumers must be managed carefully. Callback messages are processed in workqueue context after IRQ. `data_size` is currently set to `sizeof(*req)` rather than the exact union payload, noted by a TODO. Timeouts can trigger PM recovery only after heartbeat also fails. Shared memory barriers are required for firmware visibility.

### Test Signals
Test boot message receive, synchronous request/response, async callback consumers, timeout and heartbeat recovery, IPC disable abort wakeups, RX FIFO out-of-range addresses, max RX queue drop, JSM result error propagation, consumer deletion freeing TX buffers, and concurrent consumers with same channel but distinct request IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_ipc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_ipc.h -->
## sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_ipc.h

### Purpose
`ivpu_ipc.h` defines the ivpu IPC shared-memory ABI, consumer/message structures, IPC state, and transport API.

### Important APIs, Types, And Functions
It defines boot channel constants, IPC alignment, header status values, `struct ivpu_ipc_hdr`, callback type `ivpu_ipc_rx_callback_t`, `struct ivpu_ipc_rx_msg`, `struct ivpu_ipc_consumer`, and `struct ivpu_ipc_info`. It declares IPC lifecycle, enable/disable/reset, IRQ, consumer, send, receive, and send/receive helper functions.

### Control Flow
The header itself has no flow. The structure design supports two receive paths: synchronous consumers wait on `rx_msg_wq`, while callback consumers queue messages for workqueue processing.

### State, Persistence, And Dependencies
`ivpu_ipc_hdr` is packed and 64-byte aligned because it is shared with firmware. IPC state persists in global BOs, gen_pool allocations, lists, locks, atomic counters, waitqueues, and the on/off flag. Dependencies include Linux interrupt/spinlock APIs and JSM firmware API types.

### Integration Points
It is included by the main driver, firmware boot, JSM message layer, PM, jobs, and any code that sends firmware commands or handles firmware responses.

### Risks
The shared header layout is firmware ABI and must not change without firmware coordination. Consumers must be removed to avoid stale list entries. The boot message uses a special channel and magic data address instead of a JSM payload.

### Test Signals
ABI tests should verify `ivpu_ipc_hdr` size/alignment/field offsets, boot message constants, consumer add/delete behavior, synchronous and callback receive paths, and disabled/reset state transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_ipc.h -->
