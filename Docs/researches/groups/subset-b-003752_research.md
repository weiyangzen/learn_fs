# subset-b-003752 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/sor.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/sor.c

## Purpose

`sor.c` implements the Tegra Serial Output Resource display encoder driver. It supports HDMI, DisplayPort, and eDP/LVDS-style panel paths across multiple Tegra SoC generations, programming SOR registers, clocks, reset/runtime PM, regulators, display-controller routing, DP AUX/link training, HDMI infoframes/SCDC, HDA audio handoff, debugfs register/CRC dumps, and host1x client registration.

## Important APIs, Types, and Functions

- `struct tegra_sor` is the main device state: host1x client, `tegra_output`, MMIO base, SoC data, clocks, reset, DP AUX/link, HDMI settings, regulators, delayed SCDC work, and HDA audio format.
- `struct tegra_sor_soc` and `struct tegra_sor_regs` describe per-SoC capabilities, register offsets, lane maps, link training tables, and HDMI production settings for Tegra124/132/210/186/194.
- `tegra_sor_readl()` and `tegra_sor_writel()` wrap MMIO and emit `trace_sor_*` tracepoints.
- `tegra_sor_dp_link_apply_training()` and `tegra_sor_dp_link_configure()` implement `drm_dp_link_ops` by programming training pattern, drive current, pre-emphasis, post-cursor, link speed, lane count, framing, and lane power sequencing.
- `tegra_sor_compute_config()` calculates DP transfer-unit parameters, watermarks, and blanking symbols from display mode, bpc, link rate, and lane count; `tegra_sor_apply_config()` writes those values.
- `tegra_sor_hdmi_enable()` / `tegra_sor_hdmi_disable()` and `tegra_sor_dp_enable()` / `tegra_sor_dp_disable()` are the DRM encoder helper enable/disable paths.
- `tegra_sor_connector_*()` implements connector state allocation/duplication, detection, mode probing, debugfs registration, and mode validation.
- `tegra_sor_init()` and `tegra_sor_exit()` integrate the SOR as a host1x client and create DRM connectors/encoders.
- `tegra_sor_probe()` and `tegra_sor_remove()` are platform-driver lifecycle hooks; `tegra_sor_suspend()`/`resume()` handle system sleep.
- `tegra_sor_irq()` handles HDA scratch interrupts and toggles HDMI audio programming through `sor->ops`.

## Control Flow

Probe allocates `struct tegra_sor`, selects SoC data from device tree, duplicates SoC HDMI settings, resolves an optional DPAUX phandle, chooses HDMI or DP operations, parses `nvidia,interface` and optional `nvidia,xbar-cfg`, probes the shared `tegra_output`, enables required regulators, maps MMIO, requests IRQ, resolves reset and clocks, switches the output clock to a safe parent, enables runtime PM, initializes the host1x client, optionally registers a local pad clock implementation for older SoCs, and registers the client.

Host1x initialization creates a DRM connector and simple encoder. HDMI without DPAUX uses HDMI-A/TMDS helpers; DPAUX with a panel becomes eDP; DPAUX without a panel becomes DisplayPort. The init path attaches DPAUX, performs a firmware-handover reset when available, enables module/safe/DP clocks, and leaves the device ready for atomic enable.

HDMI enable resumes the host1x client, selects a safe clock, powers the I/O pad, brings up the SOR PLL and lanes, programs link speed for HDMI 1.x versus HDMI 2.0 clocking, configures XBAR and clocks, sets output rate, writes HDMI control, AVI infoframes, production PLL/lane settings, DC color depth and routing, powers up and attaches SOR, enables DC-to-SOR output, starts HDMI SCDC scrambling for high-TMDS modes, and prepares HDA audio. Disable reverses audio/SCDC, detach, DC routing, SOR power, I/O pad, and host1x runtime state.

DP enable resumes the client, powers pads and DPAUX, probes and filters DP link rates, chooses a link, prepares an eDP panel if present, powers PLLs, configures DP clocking and XBAR, sets DP protocol and link control, calibrates termination, trains the link, powers the sink link, computes/applies TU configuration, programs mode timing, powers up/attaches SOR, enables DC routing, wakes the head, and enables the panel. DP disable powers down panel/link/aux and tears the hardware state down.

## State and Persistence Behavior

The persistent state is `struct tegra_sor`, held as platform driver data and embedded host1x/DRM output state. Runtime mutable state includes connector state (`struct tegra_sor_state` with link speed, pixel clock, bpc), DP link training state, HDMI production settings, SCDC delayed-work state, audio format derived from HDA scratch registers, and debugfs file allocations. Hardware state persists in SOR, DC, DPAUX, PLL, pad, regulator, and clock settings until disable/suspend/reset paths rewrite it.

PM state is split: host1x client runtime suspend/resume asserts/deasserts reset and gates `sor->clk`; DRM encoder enable/disable calls host1x resume/suspend around active output; system suspend disables HDMI supply after output suspend and re-enables it before output resume. The SCDC worker keeps rechecking sink scrambling every five seconds while `scdc_enabled` is true.

## Dependencies and Integration Points

This file depends on host1x client registration, Tegra display-controller helpers (`dc.h`), shared Tegra DRM output helpers, DPAUX/DP helpers, Tegra PMC I/O pad power APIs, reset/clock/regulator frameworks, DRM connector/encoder/atomic helpers, DRM DP/SCDC/EDID/ELD helpers, debugfs, and tracepoints from `trace.h`. Device-tree bindings provide compatible strings, `nvidia,dpaux`, `nvidia,panel`, `nvidia,interface`, clock names, reset, IRQ, MMIO resource, and regulator names.

It integrates with HDA audio through scratch interrupts and ELD buffer writes, with `tegra_hda_parse_format()`, and with display routing through `tegra_dc_*` register access and atomic clock setup.

## Risks and Edge Cases

- HDMI and DP enable paths often log errors and continue rather than unwinding immediately, so partial hardware programming can persist after failures.
- Several register sequences are annotated as not in the TRM or TODO, including timing programming and XBAR/preamble details; regressions may be hardware-specific and hard to cover without boards.
- `tegra_sor_probe()` calls `devm_kmemdup()` even when `soc->num_settings` is zero; the surrounding code assumes this succeeds, so SoCs without HDMI settings should be reviewed for zero-size allocation semantics.
- Busy polling and `while (true)` loops around lane sequence state rely on hardware eventually clearing bits; some paths have no explicit timeout.
- DP TU/watermark math is sensitive to zero/overflow and lane-rate combinations; it clamps high watermarks but malformed modes or link data can still produce invalid programming.
- The HDA IRQ path dereferences `sor->ops->audio_enable`/disable only after checking the function pointers, but audio scratch interrupts on non-audio ops still depend on interrupt mask setup.
- Connector mode validation returns `MODE_OK` unconditionally; bad modes are mostly filtered by link selection/clock setup later.

## Test Signals

Useful tests include device-tree probe permutations for HDMI, DP, eDP, and missing clocks/regulators; KUnit-style tests around `tegra_sor_compute_config()` and connector state duplication; tracepoint inspection for expected register access; DP link training on RBR/HBR/HBR2 sinks; HDMI 2.0 SCDC scrambling persistence; suspend/resume and runtime PM lockdep checks; debugfs `crc`/`regs` active/inactive behavior; and board tests across Tegra124/210/186/194 lane maps and clock providers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/sor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/sor.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/sor.h

## Purpose

`sor.h` is the register and bitfield map for the Tegra SOR hardware block. It defines offsets and masks used by `sor.c` to program super-state, power sequencing, PLLs, DP link and lane controls, HDMI infoframes, HDMI 2.0 scrambling, audio/HDA handoff, interrupts, timing, CRC, and XBAR routing.

## Important APIs, Types, and Definitions

- State/control registers: `SOR_SUPER_STATE*`, `SOR_STATE*`, `SOR_HEAD_STATE*`, `SOR_PWR`, `SOR_TEST`, `SOR_TRIG`, and CRC registers.
- PLL/pad macros: `SOR_PLL0/1/2/3`, `SOR_DP_PADCTL0/2`, powerdown, calibration, TX pull-up, spare PLL, and TMDS termination fields.
- DP registers: `SOR_DP_LINKCTL0/1`, `SOR_DP_CONFIG0/1`, `SOR_DP_TPG`, DP audio blanking symbols, generic infoframe registers, link-quality custom registers, and spare-panel bits.
- Lane programming: drive current, pre-emphasis, post-cursor, lane sequencer, XBAR select/polarity, lane powerdown and common-mode bits.
- HDMI registers: AVI/audio/vendor infoframe controls, ACR registers, HDMI control, HDMI spare, HDMI 2.0 control, reference clock, and input-control bits.
- Audio/HDA registers: audio control/source selection, N/CTS values, ELD buffer write, presence, codec scratch, and interrupt status/mask/enable bits.

## Control Flow

The header has no executable control flow. Its definitions are consumed by `sor.c` in ordered hardware programming flows: reset/power sequencing, DP link configuration/training, HDMI infoframe/audio setup, DC routing, SCDC toggling, debugfs dumps, and IRQ handling.

## State and Persistence Behavior

All symbols describe hardware state persisted in SOR registers. Writes through `tegra_sor_writel()` change device state until overwritten, reset, runtime suspend, or power loss. The header itself owns no memory or mutable C state.

## Dependencies and Integration Points

It is included by `sor.c` and tightly coupled to Tegra SOR register layouts. The debugfs register table in `sor.c` uses many offsets directly. Any change here must be checked against SoC-specific offset remapping in `struct tegra_sor_regs`.

## Risks and Edge Cases

- Incorrect masks or shifts can silently corrupt hardware programming and are difficult to catch without hardware.
- Some fields are marked with uncertainty in the implementation, so definitions may encode undocumented behavior.
- Register offsets differ on newer SoCs; callers must use SoC-specific `struct tegra_sor_regs` where provided rather than fixed offsets for remapped blocks.

## Test Signals

Compile coverage catches macro syntax. Stronger signals come from register trace comparison against known-good enable sequences, hardware bring-up across SoC generations, debugfs dump sanity, HDMI audio/infoframe validation, and DP link training stability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/sor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/submit.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/submit.c

## Purpose

`submit.c` implements the new Tegra DRM channel submission ioctl. It copies userspace gather command streams into DMA memory, resolves mapped GEM buffers, applies relocations, validates gathers through the engine firewall, builds host1x jobs with waits and syncpoint increments, handles syncobj fences, binds optional memory contexts or stream IDs, powers the target engine, submits to host1x, and releases job resources through host1x reference counting.

## Important APIs, Types, and Functions

- `struct gather_bo` is a small host1x BO wrapper for copied gather data. It owns coherent DMA memory, a kref, and `host1x_bo_ops` for get/put/pin/unpin/mmap.
- `alloc_copy_user_array()` safely copies bounded userspace arrays with overflow detection and a 16 KiB maximum.
- `submit_copy_gather_data()` validates `gather_data_words`, allocates DMA memory, and copies the gather words from userspace.
- `submit_process_bufs()` copies `drm_tegra_submit_buf` entries, validates flags, looks up context mappings, writes relocations into gather data, and records referenced mappings in `tegra_drm_submit_data`.
- `submit_job_add_gather()` validates gather commands, enforces max per-gather words, validates command data with `tegra_drm_fw_validate()`, and appends host1x gather entries.
- `submit_create_job()` copies submit commands, allocates `host1x_job`, attaches syncpoint state, adds gathers and waits, enforces at least one gather, and returns a job ready for pinning.
- `release_job()` is installed as the host1x job release callback. It drops memory-context and mapping refs, frees job data, and drops runtime PM autosuspend.
- `tegra_drm_ioctl_channel_submit()` is the ioctl entry point.

## Control Flow

The ioctl locks `tegra_drm_file.lock`, loads the channel context from `fpriv->contexts`, optionally waits up to 10 seconds on an input syncobj, resolves an output syncobj, copies gather data, allocates per-job tracking data, processes buffer relocations, builds a host1x job from command descriptors, pins the job for the engine device, fills stream-ID or memory-context fields, powers the engine with runtime PM, installs `job->user_data`, `job->release`, and `job->timeout`, submits through `host1x_job_submit()`, returns the syncpoint end value, and optionally replaces the output syncobj fence.

Failure paths release resources in reverse order: unpin jobs, put jobs, drop memory-context refs, put mapping refs, free job data, put gather BOs, put syncobjs, and unlock the file. Once `job_data` is attached to `job->user_data`, release ownership moves to `release_job()`.

## State and Persistence Behavior

Persistent per-file/context state lives in `uapi.c` xarrays and is only referenced here. Submission creates transient gather BOs and job data. Mapping references are incremented before relocation and held until job release so submitted jobs cannot outlive the mappings. Runtime PM is acquired before submit and released in `release_job()` via autosuspend. `args->syncpt.value` is written back with the job's end threshold, and `syncobj_out` is replaced with a host1x fence when requested.

The gather BO implements host1x BO pin/unpin around copied DMA memory, so host1x pinning can map the command buffer to the engine. Relocations mutate the private copied gather buffer, not userspace memory.

## Dependencies and Integration Points

This file depends on DRM syncobj/fence APIs, dma-mapping/scatterlist helpers, host1x job/channel/syncpoint APIs, Tegra GEM lookup and BO conversion, IOMMU stream-ID helpers, runtime PM, xarray mapping state from `uapi.c`, and firewall validation from `tegra_drm_fw_validate()`. Engine clients supply `get_streamid_offset` and `can_use_memory_ctx` callbacks.

## Risks and Edge Cases

- `submit_write_reloc()` has an explicit TODO to check `target_offset` bounds against the mapped buffer; currently it can compute an IOVA beyond `mapping->iova_end`.
- The ioctl holds the per-file mutex while copying userspace memory, waiting on syncobj input, pinning jobs, powering hardware, and submitting. That simplifies lifetime but can serialize or block unrelated channel operations for long periods.
- `dma_fence_wait_timeout()` returns zero on timeout and negative on error; this code treats any nonzero as an error, so a positive success return incorrectly enters the timeout/error path. This deserves review against kernel API semantics.
- If `host1x_fence_create()` fails for `syncobj_out`, the code still calls `drm_syncobj_replace_fence(syncobj, fence)` with an error pointer unless the helper tolerates it; this looks risky.
- User array copies are capped at 16 KiB each; large valid workloads may fail with `-E2BIG`.
- Relative waits must target the job syncpoint, but absolute waits accept any ID without checking allocation in this file.
- Error unwinding after runtime PM acquisition depends on whether `job->release` was installed; `put_memory_context` handles pre-submit setup, while `release_job()` handles post-install ownership.

## Test Signals

Tests should cover invalid context IDs, zero/overflow gather sizes, oversized user arrays, bad buffer flags, invalid mapping IDs, relocation gather offset bounds, missing syncpoint allocation, invalid command flags/types, gather overflow, firewall rejection, no-gather jobs, syncobj in/out failures, memory context support and fallback stream IDs, job pin/submit failure unwinds, and reference release after asynchronous job completion. Runtime tests should watch PM get/put balance and mapping kref balance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/submit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/submit.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/submit.h

## Purpose

`submit.h` declares shared data structures for Tegra DRM job submission and the firmware firewall validator used by `submit.c` and engine-specific validation code.

## Important APIs, Types, and Functions

- `struct tegra_drm_used_mapping` records a `tegra_drm_mapping` reference plus submit buffer flags for each mapping used by a job.
- `struct tegra_drm_submit_data` stores the dynamically allocated array of used mappings and its count; it is attached to `host1x_job.user_data`.
- `tegra_drm_fw_validate()` validates gather words for a given client, updates current job class, and receives relocation/mapping metadata.

## Control Flow

The header itself has no control flow. `submit.c` fills `tegra_drm_submit_data` after copying user buffer descriptors, passes it into `tegra_drm_fw_validate()` per gather command, then releases all contained mappings from the host1x job release callback.

## State and Persistence Behavior

The structures are per-submit transient state. Their mapping references persist until the host1x job is released, preventing buffers from being unmapped while hardware can still access them.

## Dependencies and Integration Points

It depends on definitions of `struct tegra_drm_mapping`, `struct tegra_drm_client`, and fixed-width `u32` from surrounding Tegra DRM headers. It is included by `submit.c` and by firewall validation implementations.

## Risks and Edge Cases

Because ownership is by convention, callers must ensure every mapping stored in `used_mappings` has an active ref and that cleanup runs exactly once. The validator contract is not documented here beyond its signature, so class mutation and mapping flag semantics must be inferred from implementations.

## Test Signals

Compile coverage verifies structure visibility. Runtime submission tests should assert mapping refs remain held while jobs are live and are dropped on every success and failure path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/submit.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/trace.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/trace.c

## Purpose

`trace.c` instantiates the Tegra DRM tracepoints declared in `trace.h` by defining `CREATE_TRACE_POINTS` and including the trace header.

## Important APIs, Types, and Functions

There are no functions. The important symbol is `CREATE_TRACE_POINTS`, which causes `trace/define_trace.h` included by `trace.h` to emit the tracepoint definitions for register access events.

## Control Flow

No runtime control flow exists in this file. It participates at build/link time to ensure one translation unit owns the tracepoint storage.

## State and Persistence Behavior

The generated tracepoint descriptors are static kernel tracing state. Event payloads are produced by call sites such as `trace_sor_readl()` and `trace_sor_writel()`.

## Dependencies and Integration Points

It depends entirely on `trace.h` and Linux tracepoint infrastructure. Tegra DRM register access wrappers in display, HDMI, DSI, DPAUX, and SOR code call the generated tracepoint functions.

## Risks and Edge Cases

The file must remain the single tracepoint-definition translation unit for this trace system. Duplicating `CREATE_TRACE_POINTS` elsewhere would cause duplicate definitions; removing this file would leave unresolved tracepoint references.

## Test Signals

Build/link success is the primary signal. Runtime signal is the presence of Tegra DRM register events under ftrace/perf tracepoint listings when tracing is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/trace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/trace.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/trace.h

## Purpose

`trace.h` declares a Tegra DRM trace system for MMIO register reads and writes. It defines one event class carrying device, register offset, and value, then derives per-block events for display controller, HDMI, DSI, DPAUX, and SOR access.

## Important APIs, Types, and Definitions

- `TRACE_SYSTEM tegra` names the trace namespace.
- `DECLARE_EVENT_CLASS(register_access, ...)` defines the common payload and print format.
- `DEFINE_EVENT(register_access, dc_writel/readl, ...)`, `hdmi_*`, `dsi_*`, `dpaux_*`, and `sor_*` create block-specific tracepoints.
- `TRACE_INCLUDE_PATH` and `TRACE_INCLUDE_FILE` point trace generation back to the driver-local header.

## Control Flow

The header is included by normal code for tracepoint declarations and by `trace.c` for definitions. At runtime, register wrappers call generated `trace_*` functions; the tracepoint fast path records events only when enabled by tracing infrastructure.

## State and Persistence Behavior

Tracepoint enablement and recorded events are managed by kernel tracing. This header owns no driver state. It exposes device pointers in event payloads and prints `dev_name()`, offset, and value.

## Dependencies and Integration Points

It includes `<linux/device.h>` and `<linux/tracepoint.h>` and ends with `<trace/define_trace.h>` outside the include guard as required by kernel tracepoint conventions. It integrates with MMIO wrappers throughout the Tegra DRM driver, especially `sor.c`.

## Risks and Edge Cases

Trace include paths are fragile because they are relative to kernel trace generation. Event payloads store a raw `struct device *`; trace consumers should not assume more lifetime than the trace framework supports. Adding a new block requires both a `DEFINE_EVENT` here and call-site wrappers.

## Test Signals

Build tests catch trace-generation failures. Runtime tracing should show events with device names, four-digit register offsets, and eight-digit values when tracepoints are enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/uapi.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/uapi.c

## Purpose

`uapi.c` implements Tegra DRM per-file UAPI resource management for the newer channel API: opening/closing engine channels, mapping/unmapping GEM BOs into engine or memory-context address spaces, allocating/freeing/waiting on host1x syncpoints, and closing all resources on file teardown.

## Important APIs, Types, and Functions

- `tegra_drm_mapping_release()` and `tegra_drm_mapping_put()` release pinned host1x BO mappings and GEM BO references through krefs.
- `tegra_drm_channel_context_close()` drops a context's memory context, all mappings, xarray storage, host1x channel, and the context allocation.
- `tegra_drm_uapi_close_file()` closes every context and syncpoint in `struct tegra_drm_file`.
- `tegra_drm_find_client()` searches registered Tegra DRM clients by host1x class.
- `tegra_drm_ioctl_channel_open()` allocates a context, finds an engine client, requests or references a host1x channel, optionally allocates a host1x memory context, inserts the context into `fpriv->contexts`, and returns version/capability data.
- `tegra_drm_ioctl_channel_map()` looks up a context and GEM handle, pins the BO for read/write direction, records IOVA range, and inserts a mapping ID.
- `tegra_drm_ioctl_channel_unmap()` erases a mapping and drops its ref.
- `tegra_drm_ioctl_syncpoint_allocate/free/wait()` expose client-managed host1x syncpoint allocation and waiting.

## Control Flow

Channel open validates flags, allocates context state, finds a client matching `host1x_class`, obtains a shared or new channel, optionally allocates an isolated memory context when the engine and IOMMU support it, inserts the context into the file xarray with IDs starting at 1, initializes the mapping xarray, and returns client version and cache-coherency capability. Close erases the context under the file lock, then performs potentially blocking teardown outside the lock.

Mapping validates flags, locks file state, loads the context, allocates mapping state, chooses the mapping device as either the memory-context device or engine device, looks up the GEM BO, converts requested READ/WRITE flags into DMA direction, pins via `host1x_bo_pin()`, stores IOVA and IOVA end, allocates an ID in the context mapping xarray, and returns it. Unmap erases the mapping under the lock and then releases it.

Syncpoint allocate requests a host1x client-managed syncpoint, uses its host1x ID as the userspace handle, and inserts it into the per-file xarray. Free erases and puts it. Wait validates padding, resolves a syncpoint by global host1x ID without taking a ref, converts absolute timeout to jiffies, and waits until threshold or timeout.

## State and Persistence Behavior

`struct tegra_drm_file` persists for a DRM file and contains an IDR for legacy contexts, a mutex, and xarrays for new channel contexts and syncpoints. Each `tegra_drm_context` owns a host1x channel, optional memory context, client pointer, and mapping xarray. Each mapping owns a kref, host1x BO ref, host1x pin mapping, and IOVA range. File close tears down contexts before syncpoints; job submission can hold mapping refs after userspace unmaps them.

Memory contexts are tied to the current TGID at channel open. Syncpoint IDs are host1x-global IDs but lifetime is tracked per file through `fpriv->syncpoints`.

## Dependencies and Integration Points

The file depends on DRM file/ioctl plumbing, Tegra DRM client registration, host1x channels/syncpoints/memory contexts, Tegra GEM lookup, dma/IOMMU state, xarray, kref, and `drm_timeout_abs_to_jiffies()`. It provides state consumed by `submit.c`.

## Risks and Edge Cases

- `tegra_drm_uapi_close_file()` iterates xarrays and releases entries but does not erase before `xa_destroy()`; this is acceptable only if no concurrent lookup can occur during file teardown.
- Syncpoint wait uses `host1x_syncpt_get_by_id_noref()` by global ID rather than checking `fpriv->syncpoints`, so a file may wait on a syncpoint it did not allocate if it knows the ID.
- Mapping `iova_end` is computed but not used by `submit.c` relocation bounds, leaving range checking incomplete.
- Channel open does not call an engine `open_channel` callback visible in some clients; it directly uses `shared_channel` or `host1x_channel_request()`, so client-specific open hooks must be wired elsewhere or are bypassed for this UAPI version.
- File mutex is not used consistently around syncpoint allocate insertion, while free takes it; xarray concurrency expectations should be verified.
- DMA direction mapping is easy to misread: userspace READ maps to `DMA_TO_DEVICE`, WRITE maps to `DMA_FROM_DEVICE`, and READ_WRITE maps bidirectional.

## Test Signals

Tests should cover invalid flags, unknown host1x class, channel exhaustion, memory-context allocation errors and `-EOPNOTSUPP` fallback, cache-coherent capability reporting, map/unmap invalid context/handle/flags, DMA direction selection, mapping ID uniqueness, close-file cleanup with live mappings, syncpoint allocation with nonzero ID rejected, duplicate syncpoint insertion, free invalid ID, wait invalid padding/ID/timeouts, and interaction with live submitted jobs holding mapping refs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/uapi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/uapi.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/uapi.h

## Purpose

`uapi.h` declares the Tegra DRM private per-file state, BO mapping state, new channel/syncpoint ioctl entry points, and mapping close helpers shared by `drm.c`, `uapi.c`, and `submit.c`.

## Important APIs, Types, and Functions

- `struct tegra_drm_file` stores legacy context IDR state plus new UAPI xarrays for channel contexts and syncpoints, protected by `lock` for many operations.
- `struct tegra_drm_mapping` owns a kref, host1x BO mapping, host1x BO ref, and IOVA start/end.
- Ioctl declarations cover channel open/close/map/unmap/submit and syncpoint allocate/free/wait.
- `tegra_drm_uapi_close_file()` tears down per-file UAPI resources.
- `tegra_drm_mapping_put()` drops a mapping reference.

## Control Flow

The header has no runtime control flow. It defines the contracts used by the DRM file open/close and ioctl dispatch paths.

## State and Persistence Behavior

The declared structures are long-lived per DRM file or per mapped BO. Context and syncpoint xarrays persist until explicit close/free or file teardown. Mapping krefs allow submitted jobs to outlive userspace unmap calls safely.

## Dependencies and Integration Points

It includes DMA mapping, IDR, kref, xarray, and DRM declarations. It depends on host1x BO types defined through surrounding Tegra DRM includes. `submit.c` uses mapping refs and ioctl declaration; `uapi.c` owns implementation.

## Risks and Edge Cases

The locking contract is implicit. Callers must know which xarray operations require `tegra_drm_file.lock` and which are safe through xarray locking or teardown context. Exposed `iova_end` suggests range validation, but correctness depends on submit/firewall users checking it.

## Test Signals

Build coverage verifies ioctl declarations match dispatch tables. Runtime tests should assert file close destroys every context/syncpoint and that mapping refs are balanced with job submission.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/uapi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/vic.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/vic.c

## Purpose

`vic.c` implements the Tegra Video Image Compositor host1x client and platform driver. It initializes the VIC Falcon firmware engine, registers VIC as a Tegra DRM render client, manages channel/syncpoint/IOMMU/runtime PM state, loads SoC-specific firmware, boots the Falcon, configures stream IDs and clock gating, and exposes submit/memory-context capability callbacks to the Tegra DRM UAPI.

## Important APIs, Types, and Functions

- `struct vic_config` describes firmware filename, client version, and stream-ID support per SoC.
- `struct vic` embeds `struct falcon`, Tegra DRM client state, host1x channel, clock/reset/MMIO resources, firmware capability state, and SoC config.
- `vic_boot()` programs stream IDs and clock gating, boots Falcon firmware, handles old firmware FCE microcode setup, and waits for idle.
- `vic_init()` attaches IOMMU, requests channel and syncpoint, registers the Tegra DRM client, and inherits DMA parameters from host1x.
- `vic_exit()` unregisters the client, forces runtime suspend, releases syncpoint/channel/IOMMU, and frees firmware memory according to whether a shared IOMMU group was used.
- `vic_load_firmware()` reads, allocates, maps, loads, and classifies firmware; it also decides whether memory-context isolation is usable.
- `vic_runtime_resume()` and `vic_runtime_suspend()` gate clock/reset and boot/stop the engine.
- `vic_open_channel()`, `vic_close_channel()`, and `vic_can_use_memory_ctx()` are client operation helpers.
- `vic_probe()` and `vic_remove()` are platform-driver hooks.

## Control Flow

Probe coerces the DMA mask from the host1x parent, allocates `struct vic`, obtains SoC config, allocates syncpoint storage, maps MMIO, gets and maxes the clock, obtains reset when no PM domain owns it, initializes Falcon state, fills host1x and Tegra DRM client descriptors, registers the host1x client, and enables autosuspended runtime PM.

When the host1x client initializes, VIC attaches to the IOMMU, requests a host1x channel and syncpoint, registers with Tegra DRM so userspace can open channels by class, and borrows DMA parameters from host1x. Runtime resume enables the clock, deasserts reset, loads firmware if not already loaded, and boots the Falcon. Runtime suspend stops the channel, asserts reset, delays, and disables the clock.

Firmware loading is serialized by a static mutex. It reads the SoC firmware blob, allocates firmware memory either with DMA coherent memory or Tegra DRM shared-domain allocation, loads firmware into the Falcon image, maps shared-domain memory for cache maintenance if needed, then inspects the FCE data offset to disable memory contexts for old firmware that accesses FCE through data buffer stream IDs. Booting later writes stream IDs when supported, enables clock gating, boots Falcon, optionally sends FCE method setup for old firmware, and waits idle.

## State and Persistence Behavior

VIC platform state persists in `struct vic`. Firmware memory is allocated once and reused across runtime resumes. `vic->can_use_context` persists after firmware inspection and informs UAPI channel-open/submission behavior. The host1x channel and syncpoint are owned for the registered client lifetime. Runtime PM autosuspend releases engine power after job release through submission code.

Firmware allocation/free differs by IOMMU grouping: non-group clients use `dma_alloc_coherent()`/`dma_free_coherent()`, while grouped clients use `tegra_drm_alloc()`/`tegra_drm_free()` plus `dma_map_single()`/`dma_unmap_single()` for physical cache maintenance.

## Dependencies and Integration Points

This file depends on platform resources, clock/reset/runtime PM, host1x client/channel/syncpoint/IOMMU APIs, Tegra DRM client registration/allocation helpers, Falcon firmware helpers, Tegra stream-ID helpers, device-tree compatible matching, and firmware files under `nvidia/tegra*/`. It exposes `tegra_drm_submit`, stream-ID offset, and memory-context capability through `tegra_drm_client_ops`.

## Risks and Edge Cases

- `vic_load_firmware()` uses one static mutex for all VIC instances, which is simple but serializes firmware loading globally.
- The cleanup path after `dma_map_single()` failure in grouped mode calls `tegra_drm_free()` but does not undo a successful `dma_map_single()` before later failures unless `vic_exit()` runs; the immediate failure path should be reviewed for map/unmap balance.
- Old firmware disables context isolation, reducing process isolation; the warning is once-only and depends on firmware header magic values.
- `vic_exit()` returns early if unregistering the client fails, leaving resources allocated.
- Runtime resume failure unwinds reset/clock but keeps loaded firmware memory for reuse.
- Reset handling differs when a PM domain exists; assumptions about reset ownership must match device-tree and genpd behavior.

## Test Signals

Tests and validation should cover probe failures at each resource, IOMMU attach absence versus error, channel/syncpoint allocation failures, firmware missing/corrupt cases, old versus new FCE firmware offsets, stream-ID programming on SID-capable SoCs, runtime PM resume/suspend cycles, autosuspend after submitted jobs, memory-context capability reporting, and unload/reload memory cleanup for grouped and non-grouped IOMMU cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/vic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/vic.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/vic.h

## Purpose

`vic.h` defines VIC method IDs, register offsets, stream-ID transaction configuration fields, clock-gating fields, and firmware header offsets used by `vic.c`.

## Important APIs, Types, and Definitions

- Methods: `VIC_SET_FCE_UCODE_SIZE` and `VIC_SET_FCE_UCODE_OFFSET` are Falcon method IDs for old firmware FCE setup.
- Registers: `VIC_THI_STREAMID0/1`, `NV_PVIC_MISC_PRI_VIC_CG`, and `VIC_TFBIF_TRANSCFG`.
- Bitfield helpers: `CG_IDLE_CG_DLY_CNT`, `CG_IDLE_CG_EN`, `CG_WAKEUP_DLY_CNT`, and `TRANSCFG_ATT`.
- Stream-ID attributes: `TRANSCFG_SID_HW`, `TRANSCFG_SID_PHY`, and `TRANSCFG_SID_FALCON`.
- Firmware offsets: `VIC_UCODE_FCE_HEADER_OFFSET`, `VIC_UCODE_FCE_DATA_OFFSET`, and `FCE_UCODE_SIZE_OFFSET`.

## Control Flow

The header has no runtime control flow. `vic.c` uses these constants during firmware boot and stream-ID/clock-gating setup.

## State and Persistence Behavior

The constants refer to hardware registers and firmware binary layout. Writes to the registers persist until reset or power loss; firmware offsets are read-only interpretation of loaded firmware data.

## Dependencies and Integration Points

It is consumed by `vic.c` and must match VIC hardware and firmware ABI expectations across Tegra generations.

## Risks and Edge Cases

Incorrect offsets can break firmware boot or memory isolation. Firmware-layout constants are especially sensitive because old/new firmware behavior is inferred from magic offset values in `vic.c`.

## Test Signals

Build coverage plus runtime VIC firmware boot, stream-ID isolation tests, and old firmware FCE setup traces validate these definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/vic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tests/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tests/Makefile

## Purpose

This Makefile lists DRM KUnit test objects built when DRM KUnit configuration options are enabled. It wires helper tests and a broad set of DRM core/helper unit tests into the kernel build.

## Important APIs, Types, and Functions

- `obj-$(CONFIG_DRM_KUNIT_TEST_HELPERS)` builds `drm_kunit_helpers.o`.
- `obj-$(CONFIG_DRM_KUNIT_TEST)` builds atomic, bridge, connector, damage, DP MST, exec, format, framebuffer, GEM shmem, HDMI state, managed, MM, modes, plane/probe helper, rect, sysfb, and fixed-point tests.
- `CFLAGS_drm_mm_test.o := $(DISABLE_STRUCTLEAK_PLUGIN)` disables structleak plugin for the DRM MM test object.

## Control Flow

There is no runtime control flow. Kbuild evaluates the configuration symbols and compiles the listed objects into the relevant test module/built-in target.

## State and Persistence Behavior

No persistent runtime state is owned here. The file controls build inclusion of test objects.

## Dependencies and Integration Points

It integrates with Linux Kbuild, DRM KUnit configuration options, and source files in the same tests directory. The test source files in this work item are included through the `CONFIG_DRM_KUNIT_TEST` object list.

## Risks and Edge Cases

Adding a test source without listing it here leaves it unbuilt. Removing or renaming an object breaks configured builds. Per-object CFLAGS should stay narrowly scoped because they alter compiler hardening behavior.

## Test Signals

`make`/KUnit builds with `CONFIG_DRM_KUNIT_TEST=y/m` and `CONFIG_DRM_KUNIT_TEST_HELPERS=y/m` should include all listed test suites. Build logs should show `drm_mm_test.o` compiled with structleak disabled only for that object.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tests/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tests/drm_atomic_state_test.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tests/drm_atomic_state_test.c

## Purpose

`drm_atomic_state_test.c` provides KUnit tests for DRM atomic helper modeset and clone-mode behavior. It verifies that connector changes trigger encoder modeset callbacks and that clone-mode helper checks accept only valid encoder clone combinations.

## Important APIs, Types, and Functions

- `struct drm_atomic_test_priv` embeds a test DRM device, primary plane, CRTC, three encoders, and two connectors.
- `drm_atomic_test_init_drm_components()` creates a minimal atomic modeset device with configurable connectors, encoder clone masks, helper callbacks, and mode-config reset.
- `set_up_atomic_state()` allocates an atomic state, optionally attaches a connector to the CRTC, sets a fixed 1024x768 mode, enables/activates the CRTC, and commits or seeds a connector mask.
- `drm_test_check_connector_changed_modeset()` asserts that moving an active CRTC from one connector to another increments `modeset_counter`.
- `drm_test_check_in_clone_mode()` tests `drm_crtc_in_clone_mode()` against one-encoder and two-encoder masks.
- `drm_test_check_valid_clones()` tests `drm_atomic_helper_check_modeset()` with valid and invalid `possible_clones` combinations.

## Control Flow

Each test constructs DRM objects with KUnit helpers, initializes mode config, and uses `drm_modeset_acquire_ctx` retry loops for `-EDEADLK`. The connector-change test performs an initial commit to enable one connector, creates a second atomic state, detaches the old connector, attaches a new one, commits, and checks that `atomic_mode_set` ran once more. Clone tests parameterize encoder masks and either call the helper directly or force a modeset check on a dummy CRTC state.

## State and Persistence Behavior

All DRM objects are KUnit-managed and test-local. `modeset_counter` is file-static and incremented by `drm_test_encoder_mode_set()`, so tests depending on its delta record the initial count. Atomic state objects are managed by KUnit helper cleanup and DRM managed resources.

## Dependencies and Integration Points

The tests depend on DRM atomic, atomic helper, atomic UAPI, probe helper, and DRM KUnit helper APIs. They target behavior in `drm_atomic_helper_check_modeset()`, `drm_crtc_in_clone_mode()`, connector/encoder atomic commit handling, and possible-clone validation.

## Risks and Edge Cases

- The global `modeset_counter` is not reset per test, so tests must continue using deltas if more cases are added.
- Clone validation is synthetic: it manipulates `encoder_mask` directly and does not cover full connector/encoder routing.
- The no-connector setup seeds `connector_mask` manually, which is enough for helper testing but not a full userspace-equivalent atomic state.

## Test Signals

KUnit suites `drm_validate_modeset` and `drm_validate_clone_mode` should pass. Signals include mode-set count increasing on connector replacement, `drm_crtc_in_clone_mode()` returning true only for multi-encoder masks, and invalid clone masks returning `-EINVAL` from modeset check.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tests/drm_atomic_state_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tests/drm_atomic_test.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tests/drm_atomic_test.c

## Purpose

`drm_atomic_test.c` provides a focused KUnit test for `drm_atomic_get_connector_for_encoder()`, verifying that an enabled encoder can be resolved back to its currently attached connector through atomic state and modeset locking.

## Important APIs, Types, and Functions

- `struct drm_atomic_test_priv` embeds a test DRM device, primary plane, CRTC, encoder, and connector.
- `create_device()` creates the minimal DRIVER_MODESET/DRIVER_ATOMIC test device, plane, CRTC, encoder, connector, helper hooks, attachment, and mode-config reset.
- `drm_test_drm_atomic_get_connector_for_encoder()` enables the CRTC/connector on a CEA VIC 16 mode and then calls `drm_atomic_get_connector_for_encoder()`.

## Control Flow

The test allocates a KUnit DRM device, obtains a 1080p CEA mode, initializes a modeset acquire context, enables the CRTC/connector with retry on `-EDEADLK`, drops/finalizes locks, creates a fresh acquire context, calls `drm_atomic_get_connector_for_encoder()` with retry on `-EDEADLK`, and expects the returned connector pointer to equal the test connector.

## State and Persistence Behavior

All state is KUnit-scoped. DRM managed objects are reset through `drm_mode_config_reset()`. The enabled connector/encoder state persists only for the lifetime of the test case.

## Dependencies and Integration Points

It depends on DRM atomic, atomic state helpers, atomic UAPI, encoder, KUnit helpers, and modeset helper vtables. It tests the DRM core atomic helper's ability to inspect current committed state under proper locking.

## Risks and Edge Cases

The test covers one encoder and one connector only. It does not test disconnected connectors, multiple connectors, disabled encoders, clone mode, or error cases beyond deadlock retry. Future changes to helper locking need to preserve the acquire-context retry pattern.

## Test Signals

The `drm_test_atomic_get_connector_for_encoder` KUnit suite should pass and return the exact connector pointer after an enabled atomic commit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tests/drm_atomic_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tests/drm_bridge_test.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tests/drm_bridge_test.c

## Purpose

`drm_bridge_test.c` provides KUnit coverage for DRM bridge helpers: retrieving current atomic bridge state, resetting an attached CRTC through a bridge for atomic and legacy bridges, and managed bridge allocation lifetime/reference behavior.

## Important APIs, Types, and Functions

- `struct drm_bridge_priv` embeds a bridge at a nonzero offset and tracks enable/disable counts plus private data.
- `struct drm_bridge_init_priv` holds the test DRM device, device-only allocation state, plane, CRTC, encoder, bridge, connector, and destroyed flag.
- `drm_test_bridge_init()` creates a minimal DRM atomic device, allocates a managed bridge, attaches it to an encoder, creates a bridge connector, attaches the connector, and resets mode config.
- `drm_test_drm_bridge_get_current_state_atomic()` commits an atomic bridge state and expects `drm_bridge_get_current_state()` to return it while locked.
- `drm_test_drm_bridge_get_current_state_legacy()` expects NULL for a non-atomic bridge.
- `drm_test_drm_bridge_helper_reset_crtc_*()` verifies reset CRTC power-cycles enabled bridges and fails cleanly for disabled atomic bridges.
- `drm_test_drm_bridge_alloc_basic()` and `_get_put()` verify `devm_drm_bridge_alloc()` destruction and bridge refcounting.

## Control Flow

Common setup allocates a KUnit device/DRM device, creates a plane/CRTC/encoder, allocates a bridge with either legacy or atomic funcs, adds/removes the bridge through KUnit cleanup actions, attaches it, creates a bridge connector, and resets mode config. State tests use atomic state allocation and commit with `-EDEADLK` retry. Reset tests enable a CRTC/connector using a CEA mode, call `drm_bridge_helper_reset_crtc()`, and assert callback counts. Allocation tests use a KUnit device directly and unregister it before or after holding an extra bridge reference.

## State and Persistence Behavior

Enable/disable counters and `destroyed` flag are test-local state. Managed bridge memory persists until the owning KUnit device unregisters and bridge references are dropped. Atomic bridge current state persists after commit until replaced, protected by `bridge->base.lock`.

## Dependencies and Integration Points

The tests depend on DRM bridge, bridge connector, bridge helper, atomic state helper, KUnit device helpers, and DRM KUnit helpers. They validate behavior of `drm_bridge_add/remove`, `drm_bridge_attach`, `drm_bridge_connector_init`, `drm_bridge_get_current_state`, `drm_bridge_helper_reset_crtc`, `devm_drm_bridge_alloc`, and bridge get/put.

## Risks and Edge Cases

- The legacy current-state test intentionally skips locking because non-atomic bridges do not initialize `bridge->base`; that assumption should remain documented if helper behavior changes.
- Reset tests cover one bridge in a simple pipeline, not bridge chains with mixed atomic/legacy behavior.
- Managed allocation tests rely on destroy callbacks firing exactly once when device and refs are released.

## Test Signals

KUnit suites `drm_test_bridge_get_current_state`, `drm_test_bridge_helper_reset_crtc`, and `drm_bridge_alloc` should pass. Signals include state pointer equality for atomic bridges, NULL for legacy current state, enable/disable counts changing from 1/0 to 2/1 on reset, disabled reset returning an error without callbacks, and destruction delayed by an extra bridge ref.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tests/drm_bridge_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tests/drm_client_modeset_test.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tests/drm_client_modeset_test.c

## Purpose

`drm_client_modeset_test.c` provides KUnit tests for command-line mode selection in DRM client modeset helpers. It verifies that parsed command-line modes pick the expected probed display mode for explicit resolution/refresh and for named analog TV modes.

## Important APIs, Types, and Functions

- `struct drm_client_modeset_test_priv` stores a test DRM device, backing device, and connector.
- `drm_client_modeset_connector_get_modes()` supplies probed modes: no-EDID modes up to 1920x1200 plus analog NTSC 480i and PAL 576i modes.
- `drm_client_modeset_test_init()` allocates the test DRM device and connector, installs helper funcs, and allows interlace/doublescan.
- `drm_test_pick_cmdline_res_1920_1080_60()` parses `1920x1080@60`, probes modes, and expects DMT 1920x1080@60.
- `drm_test_pick_cmdline_named()` is parameterized for `NTSC`, `NTSC-J`, `PAL`, and `PAL-M`.

## Control Flow

Each test parses a command-line mode into `connector->cmdline_mode`, locks the mode-config mutex, probes connector modes with `drm_helper_probe_single_connector_modes()`, unlocks, calls `drm_connector_pick_cmdline_mode()`, and compares the selected mode with an expected DRM mode. The named-mode tests generate expected modes through analog mode helpers.

## State and Persistence Behavior

The test connector stores parsed cmdline mode state and probed modes for the duration of each test. KUnit cleanup handles allocated modes through `drm_kunit_add_mode_destroy_action()` and test device cleanup.

## Dependencies and Integration Points

The file depends on KUnit, DRM connector, EDID/mode helpers, DRM driver allocation helpers, modeset helper vtables, and probe helpers. It is included directly by `drm_client_modeset.c`, so it deliberately avoids `MODULE_*` macros.

## Risks and Edge Cases

- It is built by inclusion rather than as a normal standalone test module source, so include ordering and symbol visibility depend on `drm_client_modeset.c`.
- Coverage is limited to successful mode picking; malformed command lines are covered in the separate parser tests.
- The connector type is unknown, but analog named modes are supplied by the helper get-modes function.

## Test Signals

The `drm_test_pick_cmdline` KUnit suite should pass, selecting DMT 1920x1080@60 for the explicit command line and matching NTSC/PAL helper modes for named command lines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tests/drm_client_modeset_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tests/drm_cmdline_parser_test.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tests/drm_cmdline_parser_test.c

## Purpose

`drm_cmdline_parser_test.c` provides broad KUnit coverage for `drm_mode_parse_command_line_for_connector()`. It verifies parsing of force-only commands, resolutions, bpp, refresh, CVT/reduced-blanking flags, interlace, margins, connector-type-sensitive digital forcing, named modes, rotation/reflection, TV margins, panel orientation, TV mode options, freestanding options, and invalid strings.

## Important APIs, Types, and Functions

- Static connector fixtures include `no_connector`, HDMI-B, and DVI-I connectors to test connector-type-dependent `D` force behavior.
- Individual tests named `drm_test_cmdline_*` parse a command line into `struct drm_cmdline_mode` and assert fields such as `specified`, `xres`, `yres`, `refresh`, `bpp`, `rb`, `cvt`, `interlace`, `margins`, `force`, `rotation_reflection`, `tv_margins`, `panel_orientation`, and `tv_mode`.
- `struct drm_cmdline_invalid_test` and `drm_cmdline_invalid_tests[]` define parameterized invalid syntax cases.
- `struct drm_cmdline_tv_option_test` and `drm_cmdline_tv_option_tests[]` define parameterized TV mode option cases with expected analog modes.
- `drm_cmdline_parser_tests[]` registers all direct and parameterized cases in the `drm_cmdline_parser` suite.

## Control Flow

Every positive test initializes a zeroed `drm_cmdline_mode`, calls `drm_mode_parse_command_line_for_connector()`, asserts success, and checks exact field values. Invalid parameterized tests assert parsing failure for malformed resolution/name/options and conflicting force strings. TV option tests allocate an expected analog mode, register KUnit cleanup for it, parse a command line with `tv_mode=...`, and compare expected resolution/interlace plus enum value.

## State and Persistence Behavior

All parser output is stack-local per test. Static connector fixtures are read-only. KUnit cleanup owns temporary expected analog modes in TV tests. There is no persistent driver state.

## Dependencies and Integration Points

The tests depend on KUnit, DRM connector definitions, DRM KUnit mode cleanup helpers, and DRM mode helpers. They target the DRM cmdline parser used by connector setup, fbdev/client modeset, and kernel command-line display configuration.

## Risks and Edge Cases

- The suite encodes exact grammar expectations; parser changes for new options must update both positive and invalid lists.
- Force `D` behavior depends on connector type, so new digital connector classifications may require additional fixtures.
- Invalid tests catch many but not all malformed comma-option combinations; parser fuzzing could complement them.
- The tests verify parsed state, not later mode selection or connector probing.

## Test Signals

The `drm_cmdline_parser` KUnit suite should pass. Strong signals include correct force mapping (`e`, `d`, `D`), exact numeric parsing for resolution/bpp/refresh/margins, correct rotation/reflection bitmasks, freestanding option handling without `specified`, panel orientation enum mapping, rejection of malformed strings, and TV mode enum/resolution matching for NTSC/PAL/SECAM/Mono variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tests/drm_cmdline_parser_test.c -->
