# subset-b-003669 research

Grouped research for Nouveau NVHW class/register headers, NVIF client ABI/helper headers, and NVKM core interface headers under `sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/clc57e.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/clc57e.h

## Purpose
Defines the NVC57E display window-channel method interface used to build EVO/display pushbuffer commands for legacy Volta/Turing/Ampere-style window channels.

## Important APIs, Types, And Functions
This header exports only macros. Important method groups are `NVC57E_SET_SIZE`, `NVC57E_SET_STORAGE`, `NVC57E_SET_PARAMS`, planar storage/context/offset/point methods, `NVC57E_SET_PRESENT_CONTROL`, color-format conversion coefficients, and ILUT context/offset/control. Format constants cover RGB, packed YUV, planar/semi-planar YUV, 10/12/16-bit, and floating-point formats.

## Control Flow
There is no executable control flow. Callers sequence these method offsets through NVIF push helpers, usually writing surface size/storage, format parameters, source/destination rectangles, present control, and optional color conversion or ILUT state before kicking the display channel.

## State And Persistence
The file stores no C state. The values program display channel state in GPU context memory or display hardware; state persists until overwritten by a later pushbuffer update or channel teardown.

## Dependencies And Integration Points
Integrated by display code that emits pushbuffer methods through `nvif/push*.h` and class IDs from `nvif/class.h`. The bit ranges are consumed by `NVVAL`/`NVDEF` helpers from `nvhw/drf.h`.

## Risks
Method offsets and bitfields are hardware ABI. Incorrect format, storage layout, block height, pitch, or address handling can produce scanout corruption, invalid display flips, or GPU channel faults.

## Test Signals
Build coverage for macro references, successful modesets and plane updates, correct RGB/YUV formats, ILUT behavior, and absence of display channel method faults are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/clc57e.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/clc97b.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/clc97b.h

## Purpose
Defines the NVC97B DMA pushbuffer instruction encoding used by Blackwell-era display immediate/window channels.

## Important APIs, Types, And Functions
Exports `NVC97B_DMA_*` macros for opcode, method count, method offset, data payload, jump offset, and subdevice-mask values. Supported opcodes are method, jump, non-incrementing method, and set-subdevice-mask.

## Control Flow
No executable flow exists. The macros are used by `nvif/pushc97b.h` to encode pushbuffer words; the GPU command processor then interprets the stream.

## State And Persistence
No local state is stored. The encoded commands mutate display/object state when consumed by hardware.

## Dependencies And Integration Points
Depends on `nvhw/drf.h` accessors through consumers such as `PUSH_HDR`. It pairs with Blackwell display class IDs in `nvif/class.h`.

## Risks
The method offset and count fields are compact bitfields. Bad validation or shift math in consumers can emit malformed DMA words and wedge the display channel.

## Test Signals
Compile-time macro use, debug push traces, successful GB202 display channel submissions, and absence of DMA opcode faults validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/clc97b.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/clca7d.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/clca7d.h

## Purpose
Defines the NVCA7D GB202 display core-channel method interface. It is the central method map for core display updates, head timing, SOR ownership/protocol, window routing/usage limits, cursor, CRC, LUT, and tile programming.

## Important APIs, Types, And Functions
Exports macros for `NVCA7D_UPDATE`, notifier controls, cursor/window/core interlocks, notifier surface addresses, `NVCA7D_SOR_SET_CONTROL`, `NVCA7D_WINDOW_*`, `NVCA7D_HEAD_*`, CRC/OLUT/cursor surface methods, and `NVCA7D_TILE_SET_TILE_SIZE`. The head block includes procamp/color-space, output-resource pixel depth, progressive/stereo/lock controls, pixel clocks, dither, display IDs, viewport/raster timing, cursor composition, CRC target selection, and OLUT parameters.

## Control Flow
There is no C control flow. Nouveau display code emits method sequences using these offsets, then uses `NVCA7D_UPDATE` to commit pending state. Interlock flags and update special-handling bits affect whether hardware coordinates core/window/cursor changes and whether interrupts or mode-switch paths are triggered.

## State And Persistence
No software state is stored here. The methods describe persistent display channel state in GPU hardware/context until a later atomic commit, suspend/resume replay, or channel destruction changes it.

## Dependencies And Integration Points
Used by NVIF pushbuffer helpers and DRM atomic display code for GB202-class display. It depends conceptually on `nvhw/drf.h` field packing and on `nvif/class.h` for `GB202_DISP_CORE_CHANNEL_DMA`.

## Risks
Display core methods are order-sensitive. Incorrect head ownership, lock-pin selection, SOR protocol, timing dimensions, cursor format/address, CRC buffer target, or LUT size can cause failed modesets, underruns, incorrect scanout, or display engine faults. The large generated macro surface also makes copy/paste or class-version mismatch errors likely.

## Test Signals
Signals include GB202 modeset success, atomic plane/cursor updates, SOR protocol selection for DP/HDMI FRL, vblank/CRC tests, LUT/dither tests, debug push traces, and absence of EVO method/trap reports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/clca7d.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/clca7e.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/clca7e.h

## Purpose
Defines the NVCA7E GB202 display window-channel methods for scanout surface format, storage, rectangles, presentation, notifier, ISO surface addresses, and ILUT setup.

## Important APIs, Types, And Functions
Exports `NVCA7E_SET_NOTIFIER_CONTROL`, `SET_SIZE`, `SET_STORAGE`, `SET_PARAMS`, `SET_PLANAR_STORAGE`, `SET_POINT_IN`, `SET_SIZE_IN`, `SET_SIZE_OUT`, `SET_PRESENT_CONTROL`, `SET_ILUT_CONTROL`, notifier addresses, ISO surface addresses, and ILUT addresses. Supported formats include RGB, packed YUV, planar/semi-planar YUV, three-plane YUV additions, 10/12-bit formats, 16-bit, and FP16.

## Control Flow
No executable flow exists. Callers write a coherent set of methods to describe one window plane and then rely on the display core update path to latch it.

## State And Persistence
No local state is stored. Surface parameters and addresses become GPU display channel state and persist until reprogrammed.

## Dependencies And Integration Points
Consumed through push helpers for `GB202_DISP_WINDOW_CHANNEL_DMA` and display plane code. Uses the same DRF field notation as other generated NVHW class headers.

## Risks
Wrong address target, kind, enable bit, pitch, block height, format, or stereo mode can break scanout. The notifier surface must be valid if enabled or completion signalling can corrupt memory.

## Test Signals
Plane format tests, YUV scanout, stereo/present-control paths, notifier completion, GB202 display updates, and pushbuffer debug traces are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/clca7e.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/drf.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/drf.h

## Purpose
Provides generic NVIDIA DRF bitfield helpers for packing, extracting, testing, setting, and read-modify-writing register or method fields, including multi-word fields.

## Important APIs, Types, And Functions
Core helpers include `DRF_LO`, `DRF_HI`, `DRF_BITS`, `DRF_MASK`, `DRF_SMASK`, `NVVAL`, `NVDEF`, `NVVAL_GET`, `NVVAL_SET`, `NVDEF_SET`, `NVVAL_TEST`, `NVDEF_TEST`, multi-word `NVVAL_MW_GET/SET`, and object accessor families `DRF_RD`, `DRF_WR`, `DRF_MR`, `DRF_RV`, `DRF_WV`, `DRF_WD`, `DRF_MV`, `DRF_MD`, `DRF_TV`, and `DRF_TD`.

## Control Flow
All behavior is macro expansion. Selector macros choose indexed versus non-indexed fields and field-value versus named-definition variants. Read-modify helpers read an object through caller-supplied accessors, mask/merge values, write back, and return the previous field value.

## State And Persistence
The header stores no state. It mutates whichever register, mapped object, or in-memory descriptor the caller accessor targets.

## Dependencies And Integration Points
Used throughout NVIF/NVKM/NVHW code to manipulate generated bit ranges such as `31:16`. `nvif/object.h` and `nvkm/core/device.h` wrap it for MMIO/register access.

## Risks
The macros assume field definitions are valid C expressions using the `hi:lo` trick. Widths near 64 bits, signed shifts, multi-word fields, side-effecting arguments, and mismatched object element sizes are risk points.

## Test Signals
Compile failures catch malformed field names. Runtime validation comes from correct register programming, pushbuffer encoding, descriptor construction, and targeted unit-style checks for field pack/extract edge cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/drf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/ref/gb100/dev_hshub_base.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/ref/gb100/dev_hshub_base.h

## Purpose
Defines GB100 HSHUB register ranges and PCIe sysmem flush address registers for host system hub programming.

## Important APIs, Types, And Functions
Exports `NV_PFB_HSHUB0`, the generic `NV_PFB_HSHUB` range, and `NV_PFB_HSHUB_PCIE_FLUSH_SYSMEM_ADDR_{LO,HI}` plus `NV_PFB_HSHUB_EG_PCIE_FLUSH_SYSMEM_ADDR_{LO,HI}` address fields and masks.

## Control Flow
No executable flow exists. Driver code writes low/high address registers before using hardware flush paths.

## State And Persistence
No C state is stored. The target physical/sysmem flush address persists in HSHUB registers until reset or reprogramming.

## Dependencies And Integration Points
Integrated with framebuffer/host-memory coherency code and DRF helpers that pack the address fields.

## Risks
Address masks require 256-byte alignment and limit high address bits. Wrong programming can break PCIe flush completion or write to an unintended sysmem location.

## Test Signals
Host memory coherency tests, PCIe flush validation, suspend/resume register replay, and absence of timeout/error logs indicate correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/ref/gb100/dev_hshub_base.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/ref/gb10b/dev_fbhub.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/ref/gb10b/dev_fbhub.h

## Purpose
Defines GB10B FBHUB PCIe flush sysmem address registers.

## Important APIs, Types, And Functions
Exports `NV_PFB_FBHUB0_PCIE_FLUSH_SYSMEM_ADDR_LO` and `_HI` plus `ADR`, `ADR_INIT`, and `ADR_MASK` fields.

## Control Flow
No executable control flow. Consumers write the low/high halves of a flush target address.

## State And Persistence
The header has no software state. Register contents persist in hardware until changed or reset.

## Dependencies And Integration Points
Used by Nouveau memory/bar/fb coherency code on GB10B hardware with NVHW DRF accessors.

## Risks
High address width and low alignment masks must match the hardware. Incorrect masks can truncate or misalign the flush target.

## Test Signals
PCIe flush behavior, BAR/sysmem coherency checks, and hardware init logs are the relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/ref/gb10b/dev_fbhub.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/ref/gb202/dev_ce.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/ref/gb202/dev_ce.h

## Purpose
Defines the GB202 copy-engine GRCE mask register.

## Important APIs, Types, And Functions
Exports `NV_CE_GRCE_MASK`, `NV_CE_GRCE_MASK_VALUE`, and its init value.

## Control Flow
Declarative only. Driver code reads the mask to determine which copy-engine instances are graphics-copy-engine capable or reserved.

## State And Persistence
No C state. The register value is hardware-provided/configuration state.

## Dependencies And Integration Points
Integrated with CE discovery, runlist/engine selection, and scheduler setup for GB202.

## Risks
Treating the mask as writable or using stale assumptions about CE layout can schedule work on unsupported engines.

## Test Signals
CE enumeration, copy tests, GRCE exclusion behavior, and runlist engine masks validate usage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/ref/gb202/dev_ce.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/ref/gb202/dev_therm.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/ref/gb202/dev_therm.h

## Purpose
Defines the GB202 thermal I2CS scratch register used here as an FSP boot-complete status mailbox.

## Important APIs, Types, And Functions
Exports `NV_THERM_I2CS_SCRATCH`, its `DATA` field, and aliases for `NV_THERM_I2CS_SCRATCH_FSP_BOOT_COMPLETE_STATUS` with success `0xff` and failure `0x00`.

## Control Flow
Declarative only. Boot or firmware-management code polls/reads this register to decide whether FSP boot completed successfully.

## State And Persistence
The scratch value is firmware/hardware state and persists until firmware or the driver overwrites it or the GPU resets.

## Dependencies And Integration Points
Integrated with GSP/FSP initialization and thermal/PRI register access paths.

## Risks
Using the GH100 address on GB202 or vice versa would poll the wrong register. Treating any nonzero as success would differ from the explicit `0xff` definition.

## Test Signals
FSP boot logs, timeout paths, and register traces showing success/failure status are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/ref/gb202/dev_therm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/ref/gh100/dev_falcon_v4.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/ref/gh100/dev_falcon_v4.h

## Purpose
Defines GH100 Falcon v4 mailbox and hardware-configuration registers used by firmware-controller code.

## Important APIs, Types, And Functions
Exports `NV_PFALCON_FALCON_MAILBOX0/1` data fields and `NV_PFALCON_FALCON_HWCFG2_RISCV_BR_PRIV_LOCKDOWN` with lock/unlock values.

## Control Flow
No executable flow. Firmware code reads/writes mailboxes and inspects RISC-V branch privilege lockdown state.

## State And Persistence
Mailbox registers carry transient firmware/driver messages. `HWCFG2` is hardware configuration state.

## Dependencies And Integration Points
Integrated with Falcon/RISC-V firmware boot, status, and security bring-up paths.

## Risks
Mailbox interpretation is protocol-specific. Incorrect lockdown handling can misdiagnose firmware privilege state or violate security assumptions.

## Test Signals
Firmware boot logs, mailbox traces, and RISC-V privilege/lockdown status checks validate usage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/ref/gh100/dev_falcon_v4.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/ref/gh100/dev_fb.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/ref/gh100/dev_fb.h

## Purpose
Defines GH100 framebuffer hub sysmem flush-address registers and the NISO flush address shift.

## Important APIs, Types, And Functions
Exports `NV_PFB_NISO_FLUSH_SYSMEM_ADDR_SHIFT`, `NV_PFB_FBHUB_PCIE_FLUSH_SYSMEM_ADDR_LO`, `_HI`, and the high address mask.

## Control Flow
No control flow. Consumers program address halves before triggering or relying on FBHUB PCIe flush behavior.

## State And Persistence
No C state. Register state persists in the framebuffer hub while the GPU is initialized.

## Dependencies And Integration Points
Used by memory-management/coherency code and `nvkm_rd32/wr32` plus DRF helpers.

## Risks
Wrong address shifting or high mask truncation can invalidate host flush completion.

## Test Signals
FB coherency tests, BAR flushing behavior, and GH100 initialization/suspend-resume logs are the key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/ref/gh100/dev_fb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/ref/gh100/dev_fsp_pri.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/ref/gh100/dev_fsp_pri.h

## Purpose
Defines GH100 FSP PRI register range and queue/message-queue head/tail registers.

## Important APIs, Types, And Functions
Exports `NV_PFSP`, indexed `NV_PFSP_MSGQ_HEAD/TAIL(i)`, and `NV_PFSP_QUEUE_HEAD/TAIL(i)` with eight entries each and 32-bit value/address fields.

## Control Flow
Declarative only. FSP communication code advances or observes producer/consumer queue pointers through these registers.

## State And Persistence
Queue head/tail registers are live firmware communication state and persist until queue reset, firmware reset, or driver teardown.

## Dependencies And Integration Points
Integrated with GSP/FSP command queue transport and PRI register access paths.

## Risks
Head/tail races, wrong queue index, or stale pointer replay can desynchronize the driver and FSP firmware.

## Test Signals
FSP message exchange, boot completion, queue pointer traces, and timeout-free firmware RPCs validate usage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/ref/gh100/dev_fsp_pri.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/ref/gh100/dev_mmu.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/ref/gh100/dev_mmu.h

## Purpose
Defines GH100 MMU descriptor bitfields for PTEs, version-3 PDEs, dual PDEs, and version-3 PTEs.

## Important APIs, Types, And Functions
Key fields include PTE aperture, kind, valid, PCF, address, peer ID, and descriptor sizes. PDE fields encode valid/is-PTE, aperture, page-cache/ATS behavior, address, and separate big/small page fields for dual PDEs.

## Control Flow
No executable flow. VMM code uses these definitions to construct page-table entries and directory entries, then submits them to MMU memory.

## State And Persistence
No software state is stored in the header. Encoded descriptors persist in GPU page tables and control memory translation until unmapped or overwritten.

## Dependencies And Integration Points
Consumed by Nouveau VMM/MMU backends, `nvhw/drf.h` multi-word helpers, and memory-map code handling VRAM, peer, coherent, and non-coherent system memory.

## Risks
Descriptor bitfields are high-impact. Wrong aperture, valid bit, PCF, address shift, kind, or peer ID can cause GPU page faults, memory corruption, or cache-coherency bugs.

## Test Signals
VMM map/unmap tests, GPU page-fault logs, sparse mappings, ATS/coherency behavior, peer memory tests, and memory-kind validation are the important signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/ref/gh100/dev_mmu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/ref/gh100/dev_riscv_pri.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/ref/gh100/dev_riscv_pri.h

## Purpose
Defines the GH100 RISC-V CPU control halted status bit.

## Important APIs, Types, And Functions
Exports `NV_PRISCV_RISCV_CPUCTL`, `NV_PRISCV_RISCV_CPUCTL_HALTED`, and true/false/init values.

## Control Flow
No executable flow. Firmware boot code polls or reads the halted bit to determine processor state.

## State And Persistence
The halted bit is live hardware state and changes as firmware starts, stops, or resets the RISC-V core.

## Dependencies And Integration Points
Integrated with Falcon/RISC-V/FSP boot code and low-level PRI register access.

## Risks
Polling this bit without timeouts can hang boot. Misinterpreting polarity can proceed while firmware is stopped or wait while it is running.

## Test Signals
Firmware startup logs, timeout handling, and CPUCTL register traces validate usage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/ref/gh100/dev_riscv_pri.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/ref/gh100/dev_therm.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/ref/gh100/dev_therm.h

## Purpose
Defines the GH100 thermal I2CS scratch register and FSP boot-complete status aliases.

## Important APIs, Types, And Functions
Exports `NV_THERM_I2CS_SCRATCH`, data field definitions, and `FSP_BOOT_COMPLETE_STATUS` values for success `0xff` and failure `0x00`.

## Control Flow
Declarative only. Firmware code reads the scratch register as a boot-status mailbox.

## State And Persistence
Scratch data is hardware/firmware state that persists until changed or reset.

## Dependencies And Integration Points
Integrated with GH100 FSP/GSP initialization and thermal PRI register access.

## Risks
The GH100 address differs from GB202; classifying statuses too loosely can hide failed firmware boot.

## Test Signals
FSP boot-completion logs, timeout behavior, and scratch register dumps are useful validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/ref/gh100/dev_therm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/ref/gh100/dev_xtl_ep_pri.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/ref/gh100/dev_xtl_ep_pri.h

## Purpose
Defines the GH100 endpoint PCFGM PRI register aperture.

## Important APIs, Types, And Functions
Exports the `NV_EP_PCFGM` register range.

## Control Flow
No executable flow. Consumers use the range as an address boundary for endpoint configuration access.

## State And Persistence
The header stores no state; registers in the range are endpoint hardware configuration state.

## Dependencies And Integration Points
Integrated with PCIe/XTL endpoint code and BAR0/PRI access paths.

## Risks
Incorrect range constants can route endpoint configuration reads/writes to the wrong PRI block.

## Test Signals
PCIe endpoint initialization, BAR/window access tests, and register trace correctness validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/ref/gh100/dev_xtl_ep_pri.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/ref/gh100/pri_nv_xal_ep.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/ref/gh100/pri_nv_xal_ep.h

## Purpose
Defines GH100 XAL endpoint BAR0 window base field and register address.

## Important APIs, Types, And Functions
Exports `NV_XAL_EP_BAR0_WINDOW_BASE_SHIFT`, `NV_XAL_EP_BAR0_WINDOW_BASE`, and `NV_XAL_EP_BAR0_WINDOW`.

## Control Flow
No executable flow. BAR0 windowing code programs or decodes the window base field.

## State And Persistence
No C state. The BAR0 window register controls hardware address-window mapping until reprogrammed.

## Dependencies And Integration Points
Integrated with endpoint/BAR0 access paths and DRF helpers.

## Risks
Wrong shift or field width can expose the wrong BAR0 window, causing bogus MMIO accesses.

## Test Signals
BAR0 window read/write tests, endpoint register access, and fault-free GH100 initialization validate usage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/ref/gh100/pri_nv_xal_ep.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/chan.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/chan.h

## Purpose
Declares the NVIF channel helper object used to manage push buffers, GPFIFO entries, userd mappings, semaphores, and usermode doorbells.

## Important APIs, Types, And Functions
Defines `struct nvif_chan`, `struct nvif_chan_func`, DMA/GPFIFO wait and push helpers, 506F/906F/C36F constructors, GPFIFO post/kick helpers, semaphore release hooks, `doorbell_token`, and embedded `struct nvif_push`.

## Control Flow
Constructors bind class-specific function tables and memory mappings. Wait helpers check push/GPFIFO free space, push helpers write entries, post submits get/put pointers, and kick notifies hardware or usermode.

## State And Persistence
State includes mapped USERD, GPFIFO cursor/free counters, semaphore map/address, pushbuffer pointers, usermode object, and doorbell token. It persists for the lifetime of a GPU channel.

## Dependencies And Integration Points
Depends on `nvif/push.h`, channel class-specific push headers, NVIF memory/object mapping, and FIFO scheduling/runlists.

## Risks
Pointer/free accounting bugs can overwrite push buffers or GPFIFO rings. Wrong doorbell token, semaphore address, or class-specific post size can hang channel submission.

## Test Signals
GPU channel creation, pushbuffer submission, GPFIFO wrap tests, semaphore waits, doorbell kicks, and absence of FIFO faults validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/chan.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/cl0002.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/cl0002.h

## Purpose
Defines DMA object construction arguments for legacy and generation-specific DMA classes.

## Important APIs, Types, And Functions
Defines `nv_dma_v0`, `nv50_dma_v0`, `gf100_dma_v0`, and `gf119_dma_v0` with target, access, start/limit, privilege, partition, compression, kind, and page-size fields.

## Control Flow
No executable flow. These structures are passed through NVIF object construction to create DMA context objects.

## State And Persistence
The structures are transient ABI payloads; successful construction creates GPU DMA context state.

## Dependencies And Integration Points
Integrated with `NV_DMA_FROM_MEMORY`, `NV_DMA_TO_MEMORY`, `NV_DMA_IN_MEMORY`, and chipset-specific class selection in `nvif/class.h`.

## Risks
Incorrect access or target flags can grant wrong DMA access or fail object creation. Versioned struct size must match kernel/user expectations.

## Test Signals
DMA object creation, legacy channel setup, memory-to-memory copies, and NVIF ioctl validation errors are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/cl0002.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/cl0046.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/cl0046.h

## Purpose
Defines the NV04 display notification type for connector events.

## Important APIs, Types, And Functions
Exports `NV04_DISP_NTFY_CONN`.

## Control Flow
No executable flow. Event setup code uses the constant as a notification/event selector.

## State And Persistence
No state is stored. It identifies a hardware/software event source.

## Dependencies And Integration Points
Integrated with legacy `NV04_DISP` class handling and NVIF event construction.

## Risks
A wrong notification ID would wire connector hotplug events to the wrong source.

## Test Signals
Legacy display connector event delivery and hotplug tests validate usage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/cl0046.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/cl0080.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/cl0080.h

## Purpose
Defines NV_DEVICE methods and payloads for querying GPU identity, time, and host/runlist information.

## Important APIs, Types, And Functions
Exports `NV_DEVICE_V0_INFO`, `NV_DEVICE_V0_TIME`, `nv_device_info_v0`, `nv_device_info_v1`, `nv_device_time_v0`, `NV_DEVICE_INFO/HOST` query encoders, `NV_DEVICE_INFO_INVALID`, and host runlist/channel/engine query constants.

## Control Flow
No executable flow. `nvif_device_ctor()` and `nvif_device_time()` call methods with these payloads; variable query arrays request multiple data points and report unsupported queries with `INVALID`.

## State And Persistence
Payloads are transient; returned device info is cached in `struct nvif_device`. Host runlist data reflects current GPU capability.

## Dependencies And Integration Points
Used by `nvif/device.h`, FIFO runlist selection, family/platform discovery, and scheduler/channel setup.

## Risks
Family/platform enums must remain ABI-stable. Misreading runlist engine masks can schedule channels on unsupported engines.

## Test Signals
Device probe logs, family/chip/name reporting, PTIMER reads, runlist enumeration, and channel allocation tests validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/cl0080.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/cl9097.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/cl9097.h

## Purpose
Defines Fermi-class 3D ZBC color and depth method payloads.

## Important APIs, Types, And Functions
Exports `FERMI_A_ZBC_COLOR`, `FERMI_A_ZBC_DEPTH`, `fermi_a_zbc_color_v0`, and `fermi_a_zbc_depth_v0` with format, index, depth/stencil, and L2 color/depth values.

## Control Flow
No executable flow. GR/3D setup code sends these method payloads to program zero-bandwidth-clear table entries.

## State And Persistence
Payloads are transient; programmed ZBC entries persist in graphics engine state until reset or reprogrammed.

## Dependencies And Integration Points
Integrated with graphics engine class setup for Fermi through later classes listed in `nvif/class.h`.

## Risks
Wrong format/index/data pairing can cause incorrect fast-clear values or fallback paths.

## Test Signals
ZBC table programming logs, fast-clear rendering correctness, and GR method validation are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/cl9097.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/class.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/class.h

## Purpose
Centralizes NVIF internal class IDs and NVIDIA-assigned hardware/software class numbers used for object construction and class matching.

## Important APIs, Types, And Functions
Defines NVIF private classes for client/control/MMU/mem/VMM/event/display/channel objects, device/DMA/display/channel classes, 2D/M2MF/copy/video/compute/graphics classes, usermode classes, display core/window/cursor classes through GB202, and Blackwell additions.

## Control Flow
No executable flow. Class-selection helpers such as `nvif_mclass()` compare requested class IDs and versions against supported-class lists.

## State And Persistence
No state. Values become ABI object class identifiers in NVIF ioctls and hardware channel object bindings.

## Dependencies And Integration Points
Included by object constructors, channel/display/device setup, and class-specific push or method payload code.

## Risks
IDs are ABI-sensitive. A wrong class number can instantiate the wrong engine object or fail on supported hardware. Private negative IDs must not collide with hardware IDs.

## Test Signals
Successful object construction across GPU generations, supported-class matching, and feature probe logs validate correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/class.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/clb069.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/clb069.h

## Purpose
Defines NVIF ABI data for Maxwell/Volta fault-buffer classes.

## Important APIs, Types, And Functions
Defines `nvif_clb069_v0` with entry count, get pointer, and put pointer, plus an empty fault-buffer event argument union.

## Control Flow
No executable flow. Fault-buffer code constructs the object and uses get/put metadata to consume fault entries.

## State And Persistence
Payload state is transient; get/put pointers mirror hardware fault-buffer state.

## Dependencies And Integration Points
Integrated with fault-buffer class IDs `MAXWELL_FAULT_BUFFER_A` and `VOLTA_FAULT_BUFFER_A` in `class.h` and NVIF event handling.

## Risks
Incorrect entry count or pointer interpretation can lose GPU fault records or overrun the buffer.

## Test Signals
GPU page-fault injection, event delivery, and get/put wrap behavior are the key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/clb069.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/client.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/client.h

## Purpose
Declares the top-level NVIF client wrapper that binds a driver backend to an NVIF root object.

## Important APIs, Types, And Functions
Defines `struct nvif_client` with embedded `nvif_object` and `nvif_driver`, plus `nvif_client_ctor`, `nvif_client_dtor`, suspend, and resume functions.

## Control Flow
Construction initializes the backend driver and root object. Suspend/resume forward lifecycle transitions to the driver.

## State And Persistence
Client state holds the root object and backend pointer for the entire Nouveau device/client lifetime.

## Dependencies And Integration Points
Depends on `nvif/object.h` and `nvif/driver.h`; used by device, object, and logging layers.

## Risks
Client lifetime errors invalidate every child object. Suspend/resume ordering affects mapped objects and firmware state.

## Test Signals
Driver initialization, object creation under the client, suspend/resume tests, and clean teardown validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/client.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/conn.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/conn.h

## Purpose
Declares the NVIF display connector object and connector event constructor.

## Important APIs, Types, And Functions
Defines `struct nvif_conn` with object handle, DCB connector id, and connector type enum; exports `nvif_conn_ctor/dtor`, `nvif_conn_id`, and `nvif_conn_event_ctor`.

## Control Flow
Display enumeration constructs connector objects from display masks. Event construction attaches hotplug or connector notifications to an NVIF event.

## State And Persistence
Connector object state persists while the DRM connector is represented and stores immutable id/type information.

## Dependencies And Integration Points
Depends on `nvif/object.h`, `nvif/event.h`, and `struct nvif_disp`; integrates with DRM connector creation and hotplug handling.

## Risks
Wrong connector id/type mapping can create incorrect DRM connector types or miss HPD events.

## Test Signals
Connector enumeration, hotplug events, DVI/HDMI/DP/eDP classification, and teardown tests validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/conn.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/device.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/device.h

## Purpose
Declares the NVIF GPU device wrapper, including cached device information, runlist data, and usermode object.

## Important APIs, Types, And Functions
Defines `struct nvif_device`, `struct nvif_fifo_runlist`, and APIs `nvif_device_ctor`, `nvif_device_dtor`, `nvif_device_map`, and `nvif_device_time`.

## Control Flow
Construction queries device info and optional runlists. Map exposes device MMIO/object mapping. Time reads GPU timer data through the NV_DEVICE method interface.

## State And Persistence
State includes device object, `nv_device_info_v0`, runlist array/count, and embedded `nvif_user`. It persists for the lifetime of the Nouveau device wrapper.

## Dependencies And Integration Points
Depends on `nvif/object.h`, `nvif/cl0080.h`, and `nvif/user.h`; used by MMU, FIFO, timer, and display setup.

## Risks
Incorrect runlist cache or device info can break engine/channel selection. Mapping lifetime must match object lifetime.

## Test Signals
Probe logs, `nvif_device_time()` monotonicity, runlist discovery, usermode construction, and suspend/resume validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/device.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/disp.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/disp.h

## Purpose
Declares the NVIF display object and its connector/output/head masks.

## Important APIs, Types, And Functions
Defines `struct nvif_disp` with embedded object and bit masks, plus `nvif_disp_ctor` and `nvif_disp_dtor`.

## Control Flow
Construction instantiates a display class object and receives masks that drive later connector/output/head enumeration.

## State And Persistence
The masks persist in the display wrapper while the DRM device enumerates display resources.

## Dependencies And Integration Points
Depends on `nvif/object.h` and device display classes in `class.h`; connects NVKM display objects to DRM resource creation.

## Risks
Incorrect masks hide resources or cause attempts to construct nonexistent child objects.

## Test Signals
Display probe resource counts, connector/output/head creation, and modeset smoke tests validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/disp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/driver.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/driver.h

## Purpose
Defines the NVIF backend-driver abstraction used by client/object code to call into NVKM or another implementation.

## Important APIs, Types, And Functions
Defines `struct nvif_driver` callbacks for init, suspend, resume, ioctl, map, and unmap; exports `nvif_driver_init` and `nvif_driver_nvkm`.

## Control Flow
Client initialization selects a backend, then object operations dispatch through ioctl/map/unmap callbacks. Suspend/resume forward lifecycle changes.

## State And Persistence
Backend-private state is returned through `priv` during init and persists behind the client until teardown.

## Dependencies And Integration Points
Depends on `nvif/os.h`; bridges NVIF front-end code with the NVKM in-kernel server.

## Risks
Callback ABI mismatches can corrupt object construction or mappings. Map/unmap size mismatches can leak or invalidate MMIO mappings.

## Test Signals
NVKM backend initialization, object ioctl round trips, mapping/unmapping tests, and suspend/resume validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/driver.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/event.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/event.h

## Purpose
Declares NVIF event objects and callback plumbing for receiving asynchronous notifications.

## Important APIs, Types, And Functions
Defines `NVIF_EVENT_KEEP/DROP`, `nvif_event_func`, `struct nvif_event`, `nvif_event_constructed`, `nvif_event_ctor_`, wrapper `nvif_event_ctor`, destructor, allow, and block.

## Control Flow
Construction registers an event object with a callback and optional wait behavior. `allow` enables delivery and `block` disables it; callbacks return keep/drop.

## State And Persistence
Event state includes the embedded object and callback pointer and persists until destructor.

## Dependencies And Integration Points
Depends on `nvif/object.h` and `nvif/if000e.h`; used by connector, head/vblank, fault-buffer, and software event paths.

## Risks
Callbacks can run asynchronously relative to teardown. Blocking/allowing incorrectly can miss notifications or deliver after owner destruction.

## Test Signals
Hotplug, vblank, fault, and software event delivery plus teardown race tests validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/event.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/fifo.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/fifo.h

## Purpose
Declares FIFO runlist selection helpers.

## Important APIs, Types, And Functions
Exports `nvif_fifo_runlist()` and inline `nvif_fifo_runlist_ce()` which selects CE-capable runlists, excluding GRCE-only runlists when possible.

## Control Flow
`nvif_fifo_runlist_ce()` reads GR and CE runlist masks, removes GR overlap if independent CE runlists exist, and falls back to GR when only GRCE is available.

## State And Persistence
No state is stored; it queries cached device runlist information.

## Dependencies And Integration Points
Depends on `nvif/device.h` and `NV_DEVICE_HOST_RUNLIST_ENGINES_*` masks; integrated with channel/runlist selection for copy engines.

## Risks
Incorrect mask logic can route CE work to GR-only or unavailable runlists.

## Test Signals
Copy-engine channel allocation, multi-runlist hardware behavior, and runlist mask debug output validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/fifo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/head.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/head.h

## Purpose
Declares NVIF display head objects and vblank event construction.

## Important APIs, Types, And Functions
Defines `struct nvif_head`, `nvif_head_ctor/dtor`, `nvif_head_id`, and `nvif_head_vblank_event_ctor`.

## Control Flow
Display enumeration constructs head objects by id. Vblank event construction attaches event callbacks with optional wait behavior.

## State And Persistence
Head object state is the embedded NVIF object/handle and persists while the DRM CRTC/head exists.

## Dependencies And Integration Points
Depends on `nvif/object.h`, `nvif/event.h`, and `nvif_disp`; integrated with DRM CRTC and vblank handling.

## Risks
Incorrect head id mapping breaks CRTC-to-hardware routing or vblank delivery.

## Test Signals
CRTC enumeration, vblank IRQ delivery, modesets, and event teardown validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/head.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/if0000.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/if0000.h

## Purpose
Defines the client object construction payload.

## Important APIs, Types, And Functions
Defines `struct nvif_client_v0` with version and fixed 32-byte client name.

## Control Flow
No executable flow. The payload is passed to client construction.

## State And Persistence
The payload is transient; the server-side client stores the name in `nvkm_client`.

## Dependencies And Integration Points
Used by `nvif_client_ctor()` and `nvkm_client_new()`.

## Risks
Name truncation and version/size mismatch are the main ABI risks.

## Test Signals
Client creation and log prefixes containing the expected name validate usage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/if0000.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/if0001.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/if0001.h

## Purpose
Defines NVIF control object methods for querying and setting performance/power state policy.

## Important APIs, Types, And Functions
Exports `NVIF_CONTROL_PSTATE_INFO`, `_ATTR`, `_USER` and payloads `nvif_control_pstate_info_v0`, `nvif_control_pstate_attr_v0`, and `nvif_control_pstate_user_v0`.

## Control Flow
No executable flow. Callers query pstate count/current state/attributes and set user target state by power source.

## State And Persistence
Payloads are transient; user pstate policy persists in NVKM power-management state until changed.

## Dependencies And Integration Points
Integrated with control class construction and Nouveau power-management/sysfs/debugfs controls.

## Risks
Signed sentinel values for unknown/perfmon/disable must be preserved. Incorrect attribute iteration can skip states or overrun queries.

## Test Signals
Pstate listing, user pstate setting on AC/DC, and power-management logs validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/if0001.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/if0004.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/if0004.h

## Purpose
Defines NV04 software object event arguments and reference-query method payload.

## Important APIs, Types, And Functions
Exports `nv04_nvsw_event_args`, `NV04_NVSW_GET_REF`, and `nv04_nvsw_get_ref_v0`.

## Control Flow
No executable flow. Software-channel code queries a reference counter and receives empty event payloads.

## State And Persistence
Payloads are transient; referenced state lives in the software object/server implementation.

## Dependencies And Integration Points
Integrated with `NVIF_CLASS_SW_NV04` and event machinery.

## Risks
ABI version mismatch or ref-counter width assumptions can break legacy sync paths.

## Test Signals
Legacy software object creation, reference reads, and software event delivery validate usage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/if0004.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/if0005.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/if0005.h

## Purpose
Defines the NV10/NV50/GF100 software-object uevent notification selector.

## Important APIs, Types, And Functions
Exports `NV10_NVSW_NTFY_UEVENT`.

## Control Flow
No executable flow. Event code uses the constant to bind software-object notifications.

## State And Persistence
No state is stored in this header.

## Dependencies And Integration Points
Integrated with NVIF software classes and event delivery.

## Risks
Wrong notification selector would break user-event delivery for software sync objects.

## Test Signals
Software object event tests and sync notification delivery validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/if0005.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/if0008.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/if0008.h

## Purpose
Defines the generic NVIF MMU object ABI for discovering heaps, memory types, and memory kinds.

## Important APIs, Types, And Functions
Defines `nvif_mmu_v0`, method IDs `HEAP/TYPE/KIND`, and payloads `nvif_mmu_heap_v0`, `nvif_mmu_type_v0`, and `nvif_mmu_kind_v0`.

## Control Flow
No executable flow. MMU construction returns counts, then client code iterates heap/type/kind methods to populate `struct nvif_mmu`.

## State And Persistence
Payloads are transient; discovered heaps/types/kinds are cached in `nvif_mmu`.

## Dependencies And Integration Points
Used by `nvif/mmu.h`, memory allocation, VMM mapping, and display-compatible memory selection.

## Risks
Incorrect flags for vram/host/comp/disp/mappable/coherent/uncached can lead to invalid memory placement.

## Test Signals
Memory type enumeration, kind validity checks, allocation tests, and VMM map tests validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/if0008.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/if000a.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/if000a.h

## Purpose
Defines generic NVIF memory object construction payloads.

## Important APIs, Types, And Functions
Defines `nvif_mem_v0` with type, page, size, returned address, and trailing data; empty `nvif_mem_ram_vn`; and `nvif_mem_ram_v0` carrying DMA/scatterlist pointers for host RAM.

## Control Flow
No executable flow. Memory constructors pass these payloads to allocate VRAM or host-backed memory.

## State And Persistence
Payloads are transient; successful construction creates persistent `nvif_mem` object state until destroyed.

## Dependencies And Integration Points
Used by `nvif/mem.h`, MMU type selection, VMM mapping, pushbuffer allocation, and DMA mapping.

## Risks
Kernel pointer fields are in-kernel ABI and must not be exposed incorrectly. Page/type mismatch can allocate unmappable or unsuitable memory.

## Test Signals
VRAM/host allocation, DMA mapping, pushbuffer allocation, and map/unmap tests validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/if000a.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/if000b.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/if000b.h

## Purpose
Provides NV04 memory ABI placeholders that include the generic memory definitions.

## Important APIs, Types, And Functions
Defines empty `nv04_mem_vn` and `nv04_mem_map_vn` placeholders.

## Control Flow
No executable flow. The placeholders preserve versioned ABI extension points for NV04 memory/map payloads.

## State And Persistence
No state is stored. Actual memory state is managed by generic/NV04 memory implementations.

## Dependencies And Integration Points
Includes `if000a.h` and integrates with `NVIF_CLASS_MEM_NV04`.

## Risks
Adding fields must maintain ABI versioning and structure-size handling.

## Test Signals
NV04 memory object construction and map tests validate usage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/if000b.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/if000c.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/if000c.h

## Purpose
Defines the generic NVIF VMM ABI for virtual address spaces, page-size discovery, allocation, mapping, unmapping, PFN maps, and raw operations.

## Important APIs, Types, And Functions
Defines `nvif_vmm_v0`, method IDs `PAGE/GET/PUT/MAP/UNMAP/PFNMAP/PFNCLR/RAW`, payloads for each operation, raw op codes, PFN physical flags for address/aperture/atomic/write/valid, and trailing argument arrays.

## Control Flow
No executable flow. VMM code constructs an address space, queries page descriptors, allocates VA ranges with `GET`, frees them with `PUT`, maps memory with `MAP`/`PFNMAP`, unmaps with `UNMAP`/`PFNCLR`, or directly manipulates raw ranges.

## State And Persistence
Payloads are transient; VMM state persists in server-side VA managers and GPU page tables until unmapped or destroyed.

## Dependencies And Integration Points
Used by `nvif/vmm.h`, `nvif/mmu.h`, memory objects, raw BAR mappings, sparse mappings, and page-table descriptor code.

## Risks
Address/size/page alignment, sparse reference handling, trailing argument size, and PFN flag encoding are high risk because mistakes cause GPU faults or memory corruption.

## Test Signals
Managed/unmanaged/raw VMM tests, sparse maps, PFN maps, page-fault logs, and map/unmap stress validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/if000c.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/if000d.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/if000d.h

## Purpose
Provides NV04 VMM ABI placeholders layered on the generic VMM definitions.

## Important APIs, Types, And Functions
Defines empty `nv04_vmm_vn` and `nv04_vmm_map_vn` placeholders and includes `if000c.h`.

## Control Flow
No executable flow. It preserves generation-specific extension points for NV04 VMM construction and mapping.

## State And Persistence
No local state. Actual state is generic VMM/server-side state.

## Dependencies And Integration Points
Integrated with `NVIF_CLASS_VMM_NV04` and generic `nvif_vmm_*` helpers.

## Risks
Future extensions must preserve version/size compatibility with existing placeholder users.

## Test Signals
NV04 VMM construction and mapping tests validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/if000d.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/if000e.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/if000e.h

## Purpose
Defines the NVIF event object ABI and allow/block methods.

## Important APIs, Types, And Functions
Defines `nvif_event_args`, `nvif_event_v0` with wait flag and trailing data, method IDs `NVIF_EVENT_V0_ALLOW/BLOCK`, and empty allow/block payload unions.

## Control Flow
No executable flow. Event constructors pass the payload, then callers enable or disable notification delivery through allow/block methods.

## State And Persistence
Payloads are transient; event subscription state persists in NVKM event objects until destroyed or blocked.

## Dependencies And Integration Points
Used by `nvif/event.h`, connector/head/fault/software event wrappers, and NVKM uevent bridging.

## Risks
Incorrect wait flag or trailing data size can change event delivery semantics or reject construction.

## Test Signals
Event allow/block tests, hotplug/vblank/fault notifications, and teardown race checks validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/if000e.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/if0010.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/if0010.h

## Purpose
Defines the NVIF display object construction payload.

## Important APIs, Types, And Functions
Defines `nvif_disp_args` and `nvif_disp_v0` with connector, output, and head masks.

## Control Flow
No executable flow. Display construction returns masks that drive child-object enumeration.

## State And Persistence
Payloads are transient; masks are cached in `struct nvif_disp`.

## Dependencies And Integration Points
Used by `nvif/disp.h`, connector/output/head constructors, and DRM display probe.

## Risks
Mask width is 32 bits here; resource counts beyond that need ABI changes. Wrong masks hide or expose nonexistent resources.

## Test Signals
Display enumeration and modeset resource creation validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/if0010.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/if0011.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/if0011.h

## Purpose
Defines NVIF connector object ABI and connector event payloads.

## Important APIs, Types, And Functions
Defines `nvif_conn_args`/`nvif_conn_v0` with DCB connector id and connector type constants, plus event method/payload data for connector status notifications.

## Control Flow
No executable flow. Connector construction reports type metadata; event objects deliver status changes.

## State And Persistence
Construction payloads are transient; connector type/id are cached in `struct nvif_conn`, while event subscription persists until destroyed.

## Dependencies And Integration Points
Used by `nvif/conn.h`, DRM connector setup, and hotplug/event handling.

## Risks
Type enum mismatches can produce wrong DRM connector types. Event payload versioning must match server dispatch.

## Test Signals
Connector enumeration, hotplug delivery, and status-change event tests validate usage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/if0011.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/if0012.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/if0012.h

## Purpose
Defines the NVIF output object ABI for DAC/SOR/PIOR outputs, EDID/load detection, backlight, LVDS, HDMI, infoframes, HDA ELD, and DisplayPort AUX/training/MST programming.

## Important APIs, Types, And Functions
Defines `nvif_outp_args`, output type/protocol constants, method IDs from `DETECT` through `DP_MST_VCPI`, and payload unions for detect, EDID, acquire/inherit/release, backlight, LVDS, HDMI, infoframe, HDA ELD, DP AUX power/transfer, rates, training, drive, SST, MST ID, and VCPI.

## Control Flow
No executable C flow. Front-end display code calls output methods according to connector lifecycle: detect/read EDID, acquire OR, configure protocol-specific state, perform DP AUX/training, program MST allocation, and release output resources.

## State And Persistence
Payloads are transient. Acquired OR/link/head state, backlight level, HDMI/DP link state, and MST VCPI programming persist in NVKM/display hardware until released or reconfigured.

## Dependencies And Integration Points
Includes DRM DP receiver capability size and is consumed by `nvif/outp.h`, Nouveau DRM display, DP AUX helpers, HDMI audio/infoframe code, and MST topology management.

## Risks
Variable-length infoframe/ELD payloads, DP AUX transfer size limits, link-rate arrays, and acquire/release ordering are compatibility-sensitive. Wrong MST VCPI or training parameters can break displays.

## Test Signals
EDID reads, load detection, HDMI/DP modesets, DP AUX transactions, link training, MST stream allocation, backlight get/set, and hotplug logs validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/if0012.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/if0013.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/if0013.h

## Purpose
Defines the NVIF display head object ABI and vblank event selector/payload.

## Important APIs, Types, And Functions
Defines head construction args with head id, empty head event args, `NVIF_HEAD_V0_SCANOUTPOS`, and `nvif_head_scanoutpos_v0` carrying timestamp pair plus vertical/horizontal blank, total, and current line counters.

## Control Flow
No executable flow. Head objects are constructed by id, vblank events are registered for DRM vblank delivery, and scanout-position methods return timing snapshots used by modeset/vblank code.

## State And Persistence
Payloads are transient; event subscriptions persist in NVKM until destroyed. Scanout-position results are per-query timing samples.

## Dependencies And Integration Points
Used by `nvif/head.h`, DRM CRTC setup, and vblank handling.

## Risks
Incorrect head id, event selector, or scanout timing interpretation breaks vblank accounting, page-flip completion, or timestamping.

## Test Signals
Vblank interrupt/event tests, page flips, CRTC enumeration, and scanout-position timestamp checks validate usage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/if0013.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/if0014.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/if0014.h

## Purpose
Defines the NVIF display-channel construction ABI.

## Important APIs, Types, And Functions
Defines `nvif_disp_chan_args`/`nvif_disp_chan_v0` with version, display channel id, and pushbuffer object handle.

## Control Flow
No executable flow. Display code constructs cursor/base/core/window/overlay channels with an id and pushbuffer handle before issuing class-specific display methods.

## State And Persistence
Payloads are transient; successful construction creates persistent display channel objects and mappings.

## Dependencies And Integration Points
Integrated with display channel class IDs in `class.h`, `nvif/chan.h`, and class method headers.

## Risks
Wrong channel id/class pairing can route methods to the wrong display engine context.

## Test Signals
Display channel construction, pushbuffer submission, modeset/plane/cursor updates, and teardown validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/if0014.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/if0020.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/if0020.h

## Purpose
Defines NVIF channel object ABI for DMA/GPFIFO channel construction and event/engine bindings.

## Important APIs, Types, And Functions
Defines `nvif_chan_args`/`nvif_chan_v0` carrying variable name length, runlist, run queue, privilege flag, device mask, VMM handle, legacy ctxdma/offset/length, USERD handle/offset, doorbell token, returned channel id, instance-memory aperture, instance address, and trailing name. Also defines channel event args for non-stall interrupt and killed events.

## Control Flow
No executable flow. Channel constructors use these payloads to allocate server-side channel state, bind VMM/context/USERD/instance resources, return channel identity, and optionally register channel events.

## State And Persistence
Payloads are transient; returned token/channel id and created channel state persist in FIFO/NVKM until destroyed.

## Dependencies And Integration Points
Used by `nvif/chan.h`, channel class IDs, runlist selection, pushbuffer allocation, and usermode doorbell setup.

## Risks
Wrong runlist, run queue, VMM, ctxdma, USERD, instance aperture, or instance address can create unusable channels. Variable trailing names and ABI padding/versioning must be handled exactly.

## Test Signals
Channel creation, returned chid/token, GPFIFO submission, non-stall/killed events, engine scheduling, and FIFO fault absence validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/if0020.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/if0021.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/if0021.h

## Purpose
Defines NVIF channel-group ABI for grouped channel scheduling objects.

## Important APIs, Types, And Functions
Defines `nvif_cgrp_args`/`nvif_cgrp_v0` with variable name length, runlist id, returned channel-group id, VMM handle, and trailing name.

## Control Flow
No executable flow. FIFO code constructs a group object for a runlist/VMM and receives a channel-group id; channels can then be associated with the group.

## State And Persistence
Payloads are transient; group scheduling state persists in NVKM/FIFO until destroyed.

## Dependencies And Integration Points
Integrated with `NVIF_CLASS_CGRP`, `KEPLER_CHANNEL_GROUP_A`, and channel construction paths.

## Risks
Runlist/VMM/group mismatch can break grouped scheduling or channel admission. Trailing name length must match the payload size.

## Test Signals
Channel-group construction, multi-channel scheduling, and FIFO teardown tests validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/if0021.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/if500b.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/if500b.h

## Purpose
Defines NV50 memory object ABI extensions.

## Important APIs, Types, And Functions
Includes generic memory ABI and defines `nv50_mem_v0` with bankswizzle and contiguous-allocation flags, plus `nv50_mem_map_v0` with read-only, kind, and compression fields.

## Control Flow
No executable flow. Constructors use these payloads for NV50 memory objects and maps.

## State And Persistence
Payloads are transient; allocated memory object state persists until destroyed.

## Dependencies And Integration Points
Integrated with `NVIF_CLASS_MEM_NV50`, `nvif/mem.h`, and VMM mapping code.

## Risks
Generation-specific map arguments must align with NV50 MMU expectations. Bad kind/compression/read-only fields can cause faults or incorrect cache/compression behavior.

## Test Signals
NV50 memory allocation and mapping tests validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/if500b.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/if500d.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/if500d.h

## Purpose
Defines NV50 VMM ABI extensions.

## Important APIs, Types, And Functions
Includes generic VMM ABI and defines `nv50_vmm_map_v0` with read-only, privilege, kind, and compression fields.

## Control Flow
No executable flow. NV50 VMM constructors and map calls consume the payloads through NVIF.

## State And Persistence
Payloads are transient; VMM page-table state persists in NVKM until unmapped or destroyed.

## Dependencies And Integration Points
Integrated with `NVIF_CLASS_VMM_NV50`, `nvif/vmm.h`, and NV50 MMU backends.

## Risks
Mismatch between generic VMM fields and NV50-specific mapping data can cause page faults, privilege bugs, or compression/kind errors.

## Test Signals
NV50 VMM creation, map/unmap, and GPU fault logs validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/if500d.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/if900b.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/if900b.h

## Purpose
Defines GF100 memory object ABI extensions.

## Important APIs, Types, And Functions
Includes generic memory ABI and defines `gf100_mem_v0` with contiguous-allocation flag and `gf100_mem_map_v0` with read-only and kind fields.

## Control Flow
No executable flow. GF100 memory construction uses these ABI definitions.

## State And Persistence
Payloads are transient; memory object state persists in NVKM.

## Dependencies And Integration Points
Integrated with `NVIF_CLASS_MEM_GF100`, `nvif/mem.h`, and GF100+ memory management.

## Risks
Contiguity, kind, and read-only encoding must match GF100 MMU expectations.

## Test Signals
GF100+ memory allocation, mapping, and rendering/copy tests validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/if900b.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/if900d.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/if900d.h

## Purpose
Defines GF100 VMM ABI extensions.

## Important APIs, Types, And Functions
Includes generic VMM ABI and defines `gf100_vmm_map_v0` with volatile, read-only, privilege, and kind fields.

## Control Flow
No executable flow. VMM code passes these payloads to generation-specific map paths.

## State And Persistence
Payloads are transient; mappings persist in GPU page tables until unmapped.

## Dependencies And Integration Points
Integrated with `NVIF_CLASS_VMM_GF100`, `nvif/vmm.h`, and GF100 MMU/page-table code.

## Risks
Incorrect volatile/read-only/privilege/kind attributes can produce GPU faults, privilege mistakes, or cache-policy bugs.

## Test Signals
GF100 VMM map/unmap, sparse mapping, and GPU fault tests validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/if900d.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/ifb00d.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/ifb00d.h

## Purpose
Defines GM200 VMM ABI extensions.

## Important APIs, Types, And Functions
Includes generic VMM definitions, `gm200_vmm_v0` with big-page mode, and `gm200_vmm_map_v0` with volatile, read-only, privilege, and kind fields.

## Control Flow
No executable flow. GM200 VMM object construction and mapping use these payloads.

## State And Persistence
Payloads are transient; GPU virtual mappings persist until unmapped.

## Dependencies And Integration Points
Integrated with `NVIF_CLASS_VMM_GM200`, `nvif/vmm.h`, and GM200 MMU backends.

## Risks
Big-page selection and map attributes must match GM200 hardware descriptor expectations.

## Test Signals
GM200 map/unmap, page-fault logs, and memory-kind tests validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/ifb00d.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/ifc00d.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/ifc00d.h

## Purpose
Defines GP100 VMM ABI extensions, including newer mapping attributes used by Pascal/Volta-era page tables.

## Important APIs, Types, And Functions
Includes generic VMM definitions, `gp100_vmm_v0` with fault-replay capability flag, `gp100_vmm_map_v0` with volatile/read-only/privilege/kind fields, method IDs `GP100_VMM_VN_FAULT_REPLAY` and `GP100_VMM_VN_FAULT_CANCEL`, and `gp100_vmm_fault_cancel_v0` with hub/GPC/client/instance selector.

## Control Flow
No executable flow. Raw and normal VMM map paths pass these payloads into GP100 MMU backends. Fault-replay and fault-cancel methods control GPU fault handling for selected faulting instances/clients.

## State And Persistence
Payloads are transient; descriptor state persists in GPU page tables, while replay/cancel method effects apply to live fault handling state.

## Dependencies And Integration Points
Integrated with `NVIF_CLASS_VMM_GP100`, `nvif/vmm.h`, and GP100+ page descriptor construction.

## Risks
Descriptor attribute mismatch can cause faults, compression/kind issues, or coherency failures. Incorrect fault-cancel selectors can cancel the wrong fault context or fail to recover.

## Test Signals
GP100 VMM maps, sparse/raw maps, page faults, fault replay/cancel tests, and compression/kind tests validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/ifc00d.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/ioctl.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/ioctl.h

## Purpose
Defines the low-level NVIF ioctl command envelopes used for object construction, destruction, method calls, map/unmap, and supported-class queries.

## Important APIs, Types, And Functions
Defines `nvif_ioctl_v0` with grouped header fields version, type, owner, route, token, and target object; ioctl types for supported-class query, new, delete, method, map, and unmap; `nvif_ioctl_sclass_v0` with class/version ranges; `nvif_ioctl_new_v0` with route/token/object/handle/class and trailing class data; `nvif_ioctl_mthd_v0` with method id and trailing method data; and `nvif_ioctl_map_v0` with IO/VA map type, handle, length, and trailing map data.

## Control Flow
No executable flow. Front-end object helpers pack an envelope and backend `nvif_driver.ioctl` dispatches it to NVKM. Static assertions keep variable-data offsets equal to the tagged header sizes.

## State And Persistence
Ioctl payloads are transient; successful calls create/destroy/query persistent NVKM objects or mappings.

## Dependencies And Integration Points
Used by `nvif/object.h`, `nvif/driver.h`, and all NVIF object constructors/method calls.

## Risks
This is a central ABI boundary. Version, size, owner/route, token/object handles, class, method id, and embedded pointer/trailing-data handling must be exact to avoid object leaks or invalid dispatch.

## Test Signals
Object constructor/method/map tests, unsupported class queries, and ioctl trace logs validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/ioctl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/log.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/log.h

## Purpose
Declares NVIF logging-buffer tracking helpers, including global GSP log tracking.

## Important APIs, Types, And Functions
Defines `struct nvif_log`, `struct nvif_logs`, `NVIF_LOGS_DECLARE`, `nvif_log_shutdown()`, and external `gsp_logs`.

## Control Flow
`nvif_log_shutdown()` walks the list of logs and calls each entry's shutdown callback; callbacks are expected to remove their own list entries.

## State And Persistence
`nvif_logs` persists as a list root; each `nvif_log` tracks a backing logging resource until module exit or shutdown.

## Dependencies And Integration Points
Depends on kernel list APIs through NVIF OS headers and integrates with GSP logging allocation/cleanup.

## Risks
Shutdown callbacks must delete entries safely. Missing removal can loop or double-free; missing shutdown leaks log buffers.

## Test Signals
GSP log allocation, module unload cleanup, KASAN/list-debug checks, and repeated init/fini validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/log.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/mem.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/mem.h

## Purpose
Declares the NVIF memory object wrapper and constructors.

## Important APIs, Types, And Functions
Defines `struct nvif_mem` with object, type, page, address, and size; exports `nvif_mem_ctor_type`, `nvif_mem_ctor`, `nvif_mem_dtor`, and `nvif_mem_ctor_map`.

## Control Flow
Constructors allocate memory through an MMU object, optionally selecting a type from a mask. Destructor releases the object. `ctor_map` creates memory suitable for CPU mapping.

## State And Persistence
Memory object state persists until destructor and records GPU address/size/type/page metadata.

## Dependencies And Integration Points
Depends on `nvif/mmu.h`; used by push buffers, GPFIFO rings, semaphores, display surfaces, and VMM maps.

## Risks
Type/page selection errors produce unusable memory. Lifetime mismatches can leave mapped memory referenced by channels.

## Test Signals
Allocation/free, CPU map, VMM map, channel pushbuffer allocation, and leak checks validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/mem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/mmu.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/mmu.h

## Purpose
Declares the NVIF MMU wrapper and helpers for memory type/kind discovery.

## Important APIs, Types, And Functions
Defines `struct nvif_mmu`, memory type flags (`VRAM`, `HOST`, `COMP`, `DISP`, `KIND`, `MAPPABLE`, `COHERENT`, `UNCACHED`), constructor/destructor, `nvif_mmu_kind_valid()`, and `nvif_mmu_type()`.

## Control Flow
Construction queries heap/type/kind tables. `kind_valid` rejects invalid kind indices or sentinel kind values. `type` scans for a type containing all requested flags.

## State And Persistence
MMU state caches DMA bits, heaps, types, kind count, invalid kind marker, and kind table until destructor.

## Dependencies And Integration Points
Used by `nvif/mem.h`, `nvif/vmm.h`, memory allocation, display-compatible memory selection, and compression/kind validation.

## Risks
Cache population must match server counts. Invalid kind handling is easy to get wrong because kind zero is accepted specially.

## Test Signals
MMU enumeration, type lookup, kind validation, allocation placement, and compressed/display memory tests validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/mmu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/object.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/object.h

## Purpose
Declares the core NVIF object wrapper, object lifecycle/method/map APIs, class-selection helpers, and mapped-object MMIO access macros.

## Important APIs, Types, And Functions
Defines `nvif_sclass`, `nvif_object`, `nvif_map`, constructor/destructor/ioctl/method/map/sclass APIs, `nvif_mclass`, `nvif_sclass`, MMIO `nvif_rd/wr/mask`, and DRF wrappers `NVIF_RD32/RV32/TD32/WR32/WV32/WD32/MR32/MV32/MD32`.

## Control Flow
Object construction creates child objects under a parent. Method calls use ioctl dispatch. Class matching queries supported classes then selects the first compatible requested class. Map helpers expose BAR/object mappings for MMIO-style access.

## State And Persistence
Each object stores parent, client, name, handle, class, private pointer, and optional mapping pointer/size until destruction or unmap.

## Dependencies And Integration Points
Depends on `nvif/os.h` and `nvhw/drf.h`; all NVIF wrappers embed or operate on `nvif_object`.

## Risks
Handle collisions, stale mappings, unsupported class selection, and unchecked mapped access are central risks. `priv` is marked as a hack and should not become a broad contract.

## Test Signals
Object lifecycle tests, supported-class selection, map/unmap, MMIO access, and ioctl trace logs validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/object.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/os.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/os.h

## Purpose
Provides the kernel OS include surface and native-endian IO helper aliases used by NVIF code.

## Important APIs, Types, And Functions
Includes Linux kernel headers for types, devices, PCI/platform, firmware, I2C, delays, IO mapping, ACPI, PM, regulators, AGP, reset, IOMMU, OF, unaligned access, and Tegra SoC helpers. Defines endian-aware `ioread16/32_native`, `iowrite16/32_native`, and `iowrite64_native`.

## Control Flow
Only `iowrite64_native` has macro control flow: it writes low 32 bits then high 32 bits using native-endian 32-bit writes.

## State And Persistence
No state is stored. IO writes mutate hardware registers through caller-provided mapped addresses.

## Dependencies And Integration Points
Included by most NVIF headers and shared with object/device MMIO helpers.

## Risks
The 64-bit write order matters for hardware registers. Broad includes can hide missing direct dependencies or create build issues on non-Tegra configurations.

## Test Signals
Cross-endian build coverage, MMIO register access tests, and sparse/build warnings validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/os.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/outp.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/outp.h

## Purpose
Declares the NVIF output object wrapper and high-level output operations for display connectors.

## Important APIs, Types, And Functions
Defines `struct nvif_outp`, output type/protocol enums, DDC/connector info, OR acquisition state, detect enum, EDID/load/acquire/inherit/release APIs, backlight, LVDS, HDMI, infoframe, HDA ELD, DP AUX, rates, training, drive, SST, MST ID, and VCPI APIs.

## Control Flow
Callers construct outputs, detect sinks, get EDID, acquire an output resource, configure protocol-specific state, perform DP link training/AUX/MST, and release the resource when no longer used.

## State And Persistence
Output state stores id, hardware type/protocol, caps, DP link data, and acquired OR id/link until release or destruction.

## Dependencies And Integration Points
Depends on `nvif/object.h`, `nvif/if0012.h`, and DRM DP definitions; integrated with Nouveau DRM encoder/connector code.

## Risks
Acquire/release balance, protocol selection, DP training parameters, and MST allocation are high-risk display paths.

## Test Signals
Connector detection, EDID, HDMI/DP/eDP/LVDS modesets, backlight, AUX, MST, and hotplug tests validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/outp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/parent.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/parent.h

## Purpose
Defines the NVIF parent logging callback interface shared by child objects.

## Important APIs, Types, And Functions
Defines `struct nvif_parent`, `struct nvif_parent_func` with `debugf` and `errorf`, plus inline constructor/destructor.

## Control Flow
Construction stores the function table; destruction clears it. Logging macros later call through the parent function table.

## State And Persistence
The function-table pointer persists while the parent object is alive.

## Dependencies And Integration Points
Used by `nvif/printf.h` and embedded in parent-capable NVIF objects.

## Risks
Logging through a cleared or stale parent function pointer can crash. Teardown order must prevent child logging after parent destruction.

## Test Signals
Debug/error logging during object lifecycle and teardown race tests validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/parent.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/printf.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/printf.h

## Purpose
Defines NVIF object-scoped debug/error logging macros.

## Important APIs, Types, And Functions
Exports `NVIF_PRINT`, `NVIF_DEBUG`, `NVIF_ERROR`, and `NVIF_ERRON`. Messages include client name, object handle, and object name.

## Control Flow
Macros fetch the object's parent and call the selected logging callback. `NVIF_ERRON` logs error on nonzero condition or debug on success.

## State And Persistence
No state is stored; it reads object/client/parent state at logging time.

## Dependencies And Integration Points
Depends on `nvif/client.h` and `nvif/parent.h`; used by NVIF object, push, and driver code.

## Risks
Requires valid object, client, and parent pointers. Format strings must match arguments; debug can be compiled out through `NVIF_DEBUG_PRINT_DISABLE`.

## Test Signals
Expected log prefixes, error-path logs, and build format checking validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/printf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/push.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/push.h

## Purpose
Provides the generic NVIF pushbuffer writer abstraction and macro framework for emitting method/data packets safely.

## Important APIs, Types, And Functions
Defines `struct nvif_push`, `PUSH_WAIT`, `PUSH_KICK`, debug printing/assertion helpers, `PUSH_DATA`, reserved writes, bulk data writes, `PUSH()` generic arity dispatcher, and convenience forms `PUSH_IMMD`, `PUSH_MTHD`, `PUSH_1INC`, and `PUSH_NINC`.

## Control Flow
`PUSH_WAIT` ensures enough room, possibly calling the channel wait hook. Push macros emit a packet header then data words, checking segment and end bounds. `PUSH_KICK` submits accumulated words when `cur != bgn`.

## State And Persistence
`nvif_push` tracks memory object, GPU address, hardware get/max, and CPU pointers `bgn/cur/seg/end`. State persists for the channel/pushbuffer lifetime and changes on every emitted word or kick.

## Dependencies And Integration Points
Depends on `nvif/mem.h`, `nvif/printf.h`, `nvhw/drf.h`, and class-specific push headers that define packet encoders.

## Risks
Macro complexity and variadic dispatch make argument ordering critical. Segment/end bugs can corrupt pushbuffers; missing wait/kick can hang submissions.

## Test Signals
Debug push traces, overrun WARNs, channel submission tests, GPFIFO wrap tests, and GPU method-fault absence validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/push.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/push006c.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/push006c.h

## Purpose
Defines NV06C-style pushbuffer packet encoders for old DMA channels and subchannel assignments.

## Important APIs, Types, And Functions
Exports default `PUSH006C_SUBC_*` assignments, `PUSH_HDR`, method/non-incrementing headers, increment fields, and `PUSH_JUMP`.

## Control Flow
Macros validate subchannel, method address, count, or jump offset, then write an encoded packet word through `PUSH_DATA__`.

## State And Persistence
No separate state; macros advance the caller's `nvif_push` cursor and emit GPU-consumed commands.

## Dependencies And Integration Points
Depends on `nvif/push.h`, `nvhw/class/cl006c.h`, and DRF helpers. Used by old host/channel classes and 2D/M2MF/copy objects.

## Risks
Wrong subchannel assignment or method increment mode can send methods to the wrong object.

## Test Signals
Legacy channel push submission, debug push traces, and absence of NV06C method faults validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/push006c.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/push206e.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/push206e.h

## Purpose
Adds NV206E call-packet support on top of NV06C-style push helpers.

## Important APIs, Types, And Functions
Defines `PUSH_CALL`, validating and encoding a call offset using `NV206E_DMA_OPCODE2_CALL` and `NV206E_DMA_CALL_OFFSET`.

## Control Flow
The macro validates offset alignment/range and writes one call instruction into the pushbuffer.

## State And Persistence
No state; it advances the caller's push cursor and changes GPU control flow when consumed.

## Dependencies And Integration Points
Depends on `push006c.h`, `nvhw/class/cl206e.h`, and DRF helpers.

## Risks
Bad call target offsets can jump into invalid pushbuffer memory or create command loops.

## Test Signals
Pushbuffer call-chain tests, debug traces, and lack of DMA call faults validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/push206e.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/push507c.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/push507c.h

## Purpose
Defines NV507C display/base-channel pushbuffer packet encoders.

## Important APIs, Types, And Functions
Exports `PUSH_HDR`, `PUSH_MTHD_HDR`, `PUSH_MTHD_INC`, and `PUSH_JUMP` using `NV507C_DMA_*` fields.

## Control Flow
Macros validate method/count/jump fields and emit DMA method or jump packets.

## State And Persistence
No independent state; emitted words update the pushbuffer and hardware state when processed.

## Dependencies And Integration Points
Depends on `nvif/push.h`, `nvhw/class/cl507c.h`, and display channel code.

## Risks
Incorrect method count or offset validation can corrupt display push streams.

## Test Signals
NV50 display channel updates, modesets, debug traces, and no EVO DMA faults validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/push507c.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/push906f.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/push906f.h

## Purpose
Defines Fermi+ GPFIFO channel pushbuffer packet encoders with subchannel support.

## Important APIs, Types, And Functions
Exports default `PUSH906F_SUBC_*` assignments and encoders for incrementing, non-incrementing, immediate-data, and one-increment method packets.

## Control Flow
Macros validate subchannel, method address, count/immediate data, encode secondary op fields, and emit one packet word.

## State And Persistence
No independent state; macros advance `nvif_push` and hardware consumes the commands later.

## Dependencies And Integration Points
Depends on `nvif/push.h`, `nvhw/class/cl906f.h`, and Fermi/Kepler/Maxwell channel code.

## Risks
Immediate data shares the count field, so misuse can silently encode the wrong packet. Subchannel mapping must match bound objects.

## Test Signals
GPFIFO channel rendering/copy tests, immediate method use, debug push output, and FIFO method fault absence validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/push906f.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/pushc37b.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/pushc37b.h

## Purpose
Defines NVC37B display immediate/window-channel push method encoding.

## Important APIs, Types, And Functions
Exports `PUSH_HDR`, `PUSH_MTHD_HDR`, and `PUSH_MTHD_INC` using `NVC37B_DMA_*` fields.

## Control Flow
The macro validates method offset/count and emits a method packet word.

## State And Persistence
No state; it writes into the caller's pushbuffer.

## Dependencies And Integration Points
Depends on `nvif/push.h`, `nvhw/class/clc37b.h`, and Volta display channel code.

## Risks
Wrong class encoder on another display generation can emit incompatible packets.

## Test Signals
GV100 display channel submissions, modesets, and push traces validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/pushc37b.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/pushc97b.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/pushc97b.h

## Purpose
Defines NVC97B Blackwell display push method encoding.

## Important APIs, Types, And Functions
Exports `PUSH_HDR`, `PUSH_MTHD_HDR`, and `PUSH_MTHD_INC` using `NVC97B_DMA_METHOD_OFFSET`, `METHOD_COUNT`, and method opcode fields.

## Control Flow
The macro validates method offset/count and emits one encoded method packet word.

## State And Persistence
No local state; the caller's pushbuffer cursor advances.

## Dependencies And Integration Points
Depends on `nvif/push.h`, `nvhw/class/clc97b.h`, and GB202 display channel code.

## Risks
Incorrect field masks or using an older encoder for GB202 can fault display DMA processing.

## Test Signals
GB202 display modesets, debug push traces, and absence of display DMA faults validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/pushc97b.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/timer.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/timer.h

## Purpose
Declares GPU-timer-based wait helpers for polling hardware conditions using PTIMER time.

## Important APIs, Types, And Functions
Defines `struct nvif_timer_wait`, `nvif_timer_wait_init`, `nvif_timer_wait_test`, and macros `nvif_nsec`, `nvif_usec`, and `nvif_msec`.

## Control Flow
The wait macro initializes a deadline, executes caller-supplied polling code in a loop, and stops when `nvif_timer_wait_test()` reports timeout or the caller breaks.

## State And Persistence
Wait state stores device, limit, initial/current times, and read count for one polling operation.

## Dependencies And Integration Points
Depends on `nvif_device_time()` through the implementation and is used by hardware init, firmware boot, and register polling paths.

## Risks
Polling code must break on success. Timeout return semantics are unusual: timeout returns negative while break returns elapsed nanoseconds.

## Test Signals
Register polling success/timeout tests, firmware boot waits, and timer monotonicity validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/timer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/unpack.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/unpack.h

## Purpose
Provides macros for versioned NVIF payload unpacking.

## Important APIs, Types, And Functions
Defines `nvif_unvers` for empty-version handling and `nvif_unpack` for checking size/version range, advancing data pointers, shrinking remaining size, and enforcing trailing-data rules.

## Control Flow
Macros operate only when the current return code is `-ENOSYS`. On successful match they consume a structure and optionally reject unexpected trailing bytes.

## State And Persistence
No persistent state. They mutate local `void **data`, `u32 *size`, and return-code variables.

## Dependencies And Integration Points
Used by NVKM method/object handlers that decode versioned NVIF ABI payloads.

## Risks
Macro side effects and assignment inside conditionals require careful use. Wrong version bounds can accept incompatible payloads.

## Test Signals
ABI decode tests, invalid-size/version negative tests, and object method validation logs are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/unpack.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/user.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/user.h

## Purpose
Declares the NVIF usermode object wrapper for doorbell and time access.

## Important APIs, Types, And Functions
Defines `struct nvif_user`, `struct nvif_user_func` with `doorbell` and `time`, `nvif_user_ctor/dtor`, and external `nvif_userc361` function table.

## Control Flow
Construction creates a usermode object under the device. Function callbacks ring a doorbell or read GPU time.

## State And Persistence
User object state stores function table and embedded object while the device/usermode interface exists.

## Dependencies And Integration Points
Depends on `nvif/object.h`; used by `nvif_device`, channel doorbell submission, and timer paths.

## Risks
Doorbell token misuse can notify the wrong channel. Function table must match the usermode class generation.

## Test Signals
Usermode object creation, channel doorbell kicks, GPU time reads, and teardown validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/user.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/vmm.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/vmm.h

## Purpose
Declares the NVIF virtual memory manager wrapper and high-level VA allocation/map APIs.

## Important APIs, Types, And Functions
Defines VMM types `UNMANAGED/MANAGED/RAW`, get modes `ADDR/PTES/LAZY`, `nvif_vma`, `nvif_vmm`, page capability flags, constructor/destructor, `get/put/map/unmap`, and raw get/put/map/unmap/sparse helpers.

## Control Flow
Construction creates a VA space and discovers page capabilities. Clients allocate VA ranges, map memory objects, unmap, or use raw helpers for direct page-table operations.

## State And Persistence
VMM state stores address start/limit and page descriptors until destruction. VMA allocations and mappings persist until put/unmap.

## Dependencies And Integration Points
Depends on `nvif/object.h`, `nvif/mem.h`, and `nvif/mmu.h`; used by buffer-object mapping, sparse memory, and channel resources.

## Risks
Address/size/page alignment, sparse reference balancing, and raw operation misuse can cause page faults or leaks.

## Test Signals
VA allocation/free, map/unmap, raw/sparse tests, and GPU page-fault monitoring validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/vmm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/core/client.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/core/client.h

## Purpose
Declares the server-side NVKM client object backing NVIF clients and client-facing object logging.

## Important APIs, Types, And Functions
Defines `struct nvkm_client` with root object, name, device handle, debug level, RB-tree object registry, event callback, user memory list, locks, and `nvkm_client_new`. Logging macros include `nvif_fatal/error/debug/trace/info/ioctl`.

## Control Flow
Client creation initializes object tracking and event callback plumbing. Logging macros gate messages by `client->debug`.

## State And Persistence
Client state persists for the NVIF client lifetime and owns server-side object lookup and user-memory tracking.

## Dependencies And Integration Points
Depends on `core/object.h`; bridges NVIF ioctls into NVKM object management and logging.

## Risks
Object-tree locking, handle uniqueness, event callback lifetime, and user-memory cleanup are central risks.

## Test Signals
Client creation/destruction, object leak checks, debug-level filtering, and ioctl trace logs validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/core/client.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/core/debug.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/core/debug.h

## Purpose
Defines NVKM debug verbosity levels.

## Important APIs, Types, And Functions
Exports `NV_DBG_FATAL`, `ERROR`, `WARN`, `INFO`, `DEBUG`, `TRACE`, `PARANOIA`, and `SPAM`.

## Control Flow
No executable flow. Logging macros compare device/client debug levels against these constants.

## State And Persistence
No state is stored.

## Dependencies And Integration Points
Used by NVKM/NVIF logging macros throughout the driver.

## Risks
Changing numeric ordering changes filtering semantics globally.

## Test Signals
Debug option parsing and expected log filtering validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/core/debug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/core/device.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/core/device.h

## Purpose
Declares the core NVKM device object, chipset/family metadata, subdevice layout, interrupt state, privileged MMIO accessors, and device logging.

## Important APIs, Types, And Functions
Defines `enum nvkm_device_type`, `struct nvkm_device`, `nvkm_device_func`, `nvkm_device_quirk`, `nvkm_device_chip`, BAR IDs, resource callbacks, subdev/engine lookup, device find/delete, `nvkm_rd/wr/mask`, `NVKM_RD32`, device object class, and logging macros.

## Control Flow
Device functions implement preinit/init/fini/irq/resource flows. Subdevice and engine lookup traverse device layout. MMIO helpers read/write BAR0 PRI. Logging macros gate by device debug level.

## State And Persistence
Device state persists for the GPU lifetime: kernel device pointer, BAR0 PRI mapping, chip data, card type, chipset/revision, layout pointers, subdevice list, interrupt lists/locks, refcount, quirks, and debug config.

## Dependencies And Integration Points
Depends on core oclass/suspend/intr/layout definitions and underpins every NVKM subdevice, engine, interrupt, and NVIF device object.

## Risks
Device lifetime and refcount bugs affect all subdevices. Wrong card type/chip layout or BAR resource mapping can break initialization. MMIO accessors assume valid `pri`.

## Test Signals
GPU probe/remove, suspend/resume, IRQ delivery, subdevice init/fini ordering, BAR access, and debug logs validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/core/device.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/core/engine.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/core/engine.h

## Purpose
Declares the NVKM engine base class used by graphics, copy, video, display-related engines, and FIFO channel object class hooks.

## Important APIs, Types, And Functions
Defines `struct nvkm_engine`, `nvkm_engine_func`, constructors, ref/unref, reset, tile update, channel-switch-load query, base/fifo class hooks, and `sclass` arrays.

## Control Flow
Engine lifecycle calls dtor/preinit/oneinit/init/fini/reset/intr callbacks. FIFO hooks expose engine channel classes. Tile and chsw callbacks update memory tile state and channel-switch state.

## State And Persistence
Engine state includes function table, embedded subdevice, and lock. Subclass-specific state persists in containing engine implementations.

## Dependencies And Integration Points
Depends on `core/subdev.h`, `core/oclass.h`, channel and framebuffer tile types; used by engine implementations and FIFO object construction.

## Risks
Callback ordering and ref/unref correctness are critical. Missing nonstall/intr/reset hooks can leave engines wedged after faults.

## Test Signals
Engine init/fini/reset, interrupt handling, channel class creation, tile update tests, and suspend/resume validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/core/engine.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/core/enum.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/core/enum.h

## Purpose
Declares small utilities for mapping numeric values/bitfields to printable names.

## Important APIs, Types, And Functions
Defines `struct nvkm_enum`, `nvkm_enum_find`, `struct nvkm_bitfield`, and `nvkm_snprintbf`.

## Control Flow
`nvkm_enum_find` searches a sentinel-terminated enum table. `nvkm_snprintbf` formats names for set bits from a bitfield table.

## State And Persistence
No persistent state; table data is caller-owned static data.

## Dependencies And Integration Points
Depends on core OS helpers and is used in debug logging, register decoding, and status reporting.

## Risks
Tables must be correctly terminated and masks non-overlapping when expected. Buffer sizing matters for formatted bitfields.

## Test Signals
Register decode logs, enum lookup tests, and truncation-safe formatted output validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/core/enum.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/core/event.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/core/event.h

## Purpose
Declares NVKM server-side event and notification infrastructure, including user-event bridging to NVIF objects.

## Important APIs, Types, And Functions
Defines `struct nvkm_event`, `nvkm_event_func`, `nvkm_event_init/fini`, `NVKM_EVENT_KEEP/DROP`, `struct nvkm_event_ntfy`, notification add/delete/allow/block APIs, `nvkm_event_ntfy`, validation, `nvkm_uevent_func`, `nvkm_uevent_new`, and `nvkm_uevent_add`.

## Control Flow
Event initialization sets unique lock classes and reference tracking. Notifications are added to event lists, allowed/blocked atomically, dispatched by id/bits, and callbacks decide keep/drop. Uevents adapt NVKM notifications to NVIF client callbacks.

## State And Persistence
Event state stores function table, subdevice, type/index counts, reference counters, locks, and notification list. Each notification stores id, bits, wait flag, callback, allowed state, running flag, and list node.

## Dependencies And Integration Points
Depends on core OS locking/list primitives, NVKM objects/classes, subdevices, and NVIF event wrappers.

## Risks
Concurrency is the main risk: allow/block/delete versus dispatch, wait semantics, lock ordering, and callback lifetime must be correct to avoid missed events or use-after-free.

## Test Signals
Hotplug/vblank/fault/software event tests, concurrent teardown, lockdep, and event reference-count traces validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/core/event.h -->
