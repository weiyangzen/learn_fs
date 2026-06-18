# subset-b-003675 Research

Grouped research for nouveau NVKM device and display engine files. Each section is intentionally self-contained so it can be split into the requested `Docs/researches/<source_path>_research.md` output.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/device/pci.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/device/pci.c

Purpose: this file is the PCI-backed `nvkm_device` transport constructor for Nouveau. Most of the file is a static NVIDIA PCI ID database: top-level `nvkm_device_pci_10de[]` maps device IDs to marketing names and optional subsystem-specific override tables, while `nvkm_device_pci_vendor` entries can override the name and attach `struct nvkm_device_quirk` values such as TV GPIO or pin masks.

Important APIs and functions: `nvkm_device_pci_new()` is the exported constructor. It enables the `pci_dev`, matches vendor/device/subvendor/subdevice against the tables, allocates `struct nvkm_device_pci`, and calls `nvkm_device_ctor()` with the transport type (`NVKM_DEVICE_PCIE`, `NVKM_DEVICE_AGP`, or `NVKM_DEVICE_PCI`) and a stable BDF-derived handle. `nvkm_device_pci_func` supplies BAR address/size lookup, IRQ lookup, suspend/resume preinit/fini, destructor, and `cpu_coherent = !CONFIG_ARM`. BAR mapping is implemented through `nvkm_device_pci_resource_idx()`, which accounts for 64-bit BARs when translating Nouveau logical BARs (`PRI`, `FB`, `INST`) to PCI BAR indices.

Control flow: constructor enables PCI, resolves name/quirk, constructs the generic NVKM device, then sets a DMA mask based on `device.mmu->dma_bits` unless AGP forces 32-bit. If the high mask fails it falls back to 32-bit and updates `dma_bits`. Suspend `fini()` disables the PCI device except for poweroff and marks `pdev->suspend`; `preinit()` re-enables bus mastering on resume.

State and persistence: state is in the allocated `nvkm_device_pci`, especially `pdev`, `suspend`, and the embedded generic `device`. PCI enablement and DMA mask configuration affect kernel device state until teardown or suspend. The static PCI database has no runtime persistence.

Dependencies and integration points: depends on Linux PCI/resource/DMA APIs, `core/pci.h`, `priv.h`, and the generic device constructor. The rest of NVKM consumes the resulting `nvkm_device_func` to access BARs and IRQs without caring whether the backing transport is PCI.

Risks: the BAR index algorithm assumes Nouveau's logical BAR ordering matches probed PCI resources; new devices with unusual BAR layout need careful validation. Adding PCI IDs can change user-visible names or quirks, and wrong quirks may break legacy TV output. Constructor error paths after `nvkm_device_ctor()` do not explicitly disable the PCI device here, relying on higher-level cleanup expectations.

Test signals: probe a range of PCI, PCIe, and AGP NVIDIA devices and verify dmesg names, BAR sizes, IRQ, DMA mask width, suspend/resume, and fallback on systems limited to 32-bit DMA. PCI ID additions should be checked against `lspci -nn` subsystem IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/device/pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/device/priv.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/device/priv.h

Purpose: private device-engine header that gathers the subdevice and engine type declarations needed by the NVKM device constructor and lifecycle implementation. It is a dependency hub rather than a behavior implementation.

Important APIs and types: declares `nvkm_device_ctor()`, `nvkm_device_init()`, and `nvkm_device_fini()`. The constructor takes a transport-specific `nvkm_device_func`, optional quirk data, Linux `struct device`, `enum nvkm_device_type`, unique handle, name, configuration/debug strings, and the destination `struct nvkm_device`.

Control flow: files such as `pci.c`, `tegra.c`, and `user.c` include this header to call or expose device lifecycle functions. The many `#include <subdev/...>` and `#include <engine/...>` entries make the complete set of possible NVKM children visible to the device implementation.

State and persistence: none directly; it defines the private interface by which transport constructors populate persistent `struct nvkm_device` instances and by which user-facing objects refcount initialization.

Dependencies and integration points: tightly coupled to nearly every NVKM subdevice and engine family: ACR, BAR, BIOS, bus, clock, display, FIFO, graphics, MMU, PMU, GSP, thermal, video engines, and others. This header is an integration point between transport discovery and engine/subdevice instantiation.

Risks: because it is a broad private include hub, changes can trigger wide rebuilds and expose circular include problems. Prototype changes affect every transport constructor and the user object lifetime path.

Test signals: successful kernel build is the main signal. Runtime validation comes indirectly through PCI/Tegra device probe, user device open/close, and init/fini sequences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/device/priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/device/tegra.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/device/tegra.c

Purpose: implements the platform-device transport constructor for Tegra integrated NVIDIA GPUs when `CONFIG_NOUVEAU_PLATFORM_DRIVER` is enabled. It adapts clocks, resets, regulator power, platform resources, IRQs, and optional IOMMU state to the generic `nvkm_device` interface.

Important APIs and functions: `nvkm_device_tegra_new()` is exported and returns `-ENOSYS` when the platform driver is disabled. Runtime helpers include `nvkm_device_tegra_power_up()`, `nvkm_device_tegra_power_down()`, `nvkm_device_tegra_probe_iommu()`, `nvkm_device_tegra_remove_iommu()`, BAR resource callbacks, and IRQ lookup. `nvkm_device_tegra_func` provides `.tegra`, `.dtor`, `.irq`, `.resource_addr`, `.resource_size`, and marks the device non-coherent.

Control flow: constructor allocates `struct nvkm_device_tegra`, maps resource 0, optionally acquires `vdd`, obtains reset and GPU/ref/pwr clocks, initializes the GPU clock if its rate is zero, sets the DMA mask from `func->iommu_bit`, probes an IOMMU domain, powers the GPU, stores Tegra speedo values, and calls `nvkm_device_ctor()` as `NVKM_DEVICE_TEGRA`. Error paths unwind power and IOMMU before freeing.

State and persistence: persistent state includes regulator/clock/reset handles, MMIO mapping, platform device pointer, speedo values, and optional IOMMU domain/MM allocator. Power state is externally visible through clocks/regulator/reset and may survive until destructor.

Dependencies and integration points: uses Linux platform, clk, reset, regulator, IOMMU, DMA mask, Tegra SKU/powergate APIs, and NVKM memory manager. It exposes only BAR0/PRI and BAR1/FB platform resources and the named `stall` IRQ.

Risks: power sequencing and reset/powergate ordering are timing-sensitive (`udelay` barriers). IOMMU setup depends on page-size compatibility and legacy ARM DMA-IOMMU detach behavior. Missing optional clocks/regulators or device-tree resource naming errors will fail probe.

Test signals: Tegra probe/remove, suspend/resume, IOMMU-enabled and disabled boot paths, DMA mapping above/below the configured bit width, and validation that BAR resources and `stall` IRQ match the device tree.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/device/tegra.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/device/user.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/device/user.c

Purpose: exposes the root user-visible NVIF `NV_DEVICE` object that clients use to query device information, map BAR0, get timer values, and enumerate child classes for engines/subdevices.

Important APIs and functions: `nvkm_udevice_sclass` registers the `NV_DEVICE` class. `nvkm_udevice_new()` allocates `struct nvkm_udevice` and binds it to `nvkm_device_find(client->device)`. `nvkm_udevice_info()` handles v0 legacy info and v1 batched `NV_DEVICE_INFO_*` requests. `nvkm_udevice_time()` returns `nvkm_timer_read()`. `nvkm_udevice_init()` and `nvkm_udevice_fini()` refcount calls to `nvkm_device_init()`/`nvkm_device_fini()`. `nvkm_udevice_child_get()` enumerates DMAOBJ, FIFO, DISP, control, MMU, fault, and VFN children.

Control flow: user methods are dispatched by `nvkm_udevice_mthd()`. Info v1 validates that the remaining payload equals `count * sizeof(data[0])` and translates supported unit queries to subdev info, currently only `NV_DEVICE_HOST(0)` to FIFO. Info v0 reports platform, family, chipset, revision, RAM size/user RAM, chip name, and device name.

State and persistence: persistent object state is just the `nvkm_object` and a device pointer. Device power/lifecycle state is managed through the shared `device->refcount` under `device->mutex`; failed init/fini paths restore the count.

Dependencies and integration points: depends on NVIF class headers, `nvif_unpack`, client lookup, timer, framebuffer/instmem RAM accounting, and engine class enumeration. It is the root bridge from DRM/user clients into NVKM engine objects.

Risks: ABI compatibility is critical because NVIF structs are user-visible. Family/platform mappings must stay aligned with new `card_type` values. Child enumeration order affects userspace class discovery. RAM accounting subtracts reserved instmem only when both FB RAM and instmem are present.

Test signals: create/destroy NVIF device objects, query both v0 and v1 info with valid and invalid payload sizes, map BAR0, read time, enumerate child classes, and exercise multiple simultaneous clients to verify refcounted init/fini.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/device/user.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/Kbuild -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/Kbuild

Purpose: Kbuild fragment listing the Nouveau NVKM display engine objects that are linked into `nvkm-y`.

Important entries: common display components include `base.o`, `chan.o`, `conn.o`, `dp.o`, `hdmi.o`, `head.o`, `ior.o`, `outp.o`, and `vga.o`. Generation implementations span `nv04.o`, `nv50.o`, `g84.o`, `g94.o`, `gt200.o`, `mcp77.o`, `gt215.o`, `mcp89.o`, `gf119.o`, `gk104.o`, `gk110.o`, `gm107.o`, `gm200.o`, `gp100.o`, `gp102.o`, `gv100.o`, `tu102.o`, and `ga102.o`. User-facing display object wrappers are `udisp.o`, `uconn.o`, `uoutp.o`, and `uhead.o`.

Control flow: no runtime control flow. Build order ensures shared display infrastructure and generation-specific callback providers are compiled into the module.

State and persistence: none directly; it determines which display implementations are available at runtime.

Dependencies and integration points: integrates with the parent Nouveau Kbuild by appending to `nvkm-y`. The list mirrors constructors referenced from chip/device tables elsewhere in NVKM.

Risks: omitting an object produces link failures or missing constructor symbols for a GPU generation. Adding a generation source without updating this file prevents it from being built. Removing common objects breaks many generations.

Test signals: kernel/module build, symbol resolution for all display constructors, and probe of GPUs from each listed family.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/base.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/base.c

Purpose: common display engine object implementation. It owns top-level display lifecycle, display object lists, vblank and user channel events, and registration of the root user display class.

Important APIs and functions: `nvkm_disp_new_()` allocates and initializes `struct nvkm_disp`, list heads, client lock, engine base, optional supervisor workqueue, and the user event object. `nvkm_disp_vblank()` emits per-head vblank events. The engine callbacks `nvkm_disp_oneinit()`, `nvkm_disp_init()`, `nvkm_disp_fini()`, `nvkm_disp_intr()`, and `nvkm_disp_dtor()` implement lifecycle. `nvkm_disp_class_get()` exposes the generation-specific display root class through `nvkm_udisp_new()`.

Control flow: oneinit calls generation `func->oneinit`, counts heads, and initializes vblank events. Init initializes outputs first, then generation display hardware, then powers all IORs into a fully enabled normal state. Fini calls generation fini and output fini callbacks. Destructor tears down RAMHT/GPU object, events, supervisor workqueue/mutex, then deletes connectors, outputs, IORs, and heads in list order.

State and persistence: persistent state is in `struct nvkm_disp`: object lists, `disp->chan[]`, client spinlock, RAMHT/GPU object pointers, vblank/uevent structures, and optional supervisor work item. Hardware state is delegated to generation callbacks and output/IOR callbacks.

Dependencies and integration points: depends on the NVKM engine framework, RAMHT/GPU object management, event subsystem, output/connector/head/IOR helpers, and user display class wrappers.

Risks: destructor ordering matters because outputs reference connectors/IORs and events may point at heads. Init ordering matters for output setup before display core programming. Event head count must reflect the maximum head ID plus one.

Test signals: display engine construction/destruction, hotplug/vblank event subscription, modeset init/fini, suspend/resume, and memory leak checks for list-owned objects and workqueues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/base.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/chan.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/chan.c

Purpose: generic user display channel object implementation for core, head/base/window, cursor, overlay, and immediate channels. It validates NVIF channel creation arguments, maps channel MMIO, handles channel init/fini/intr, and proxies child DMA objects through RAMHT binding.

Important APIs and functions: `nvkm_disp_core_new()`, `nvkm_disp_chan_new()`, and `nvkm_disp_wndw_new()` create channels with limits based on core count, head count, or window count. `nvkm_disp_chan_new_()` selects the generation `nvkm_disp_chan_user` by class, validates `nvif_disp_chan_args`, allocates `struct nvkm_disp_chan`, optionally binds push buffers, and reserves `disp->chan[user]` under `client.lock`. Channel object callbacks provide `.init`, `.fini`, `.ntfy`, `.map`, and `.sclass`.

Control flow: init enables interrupts then calls the generation channel init callback. Fini calls generation fini then disables interrupts. Child class creation uses DMAOBJ engine classes when the channel supports `bind`; the child is wrapped in `nvkm_oproxy` so the RAMHT hash is removed in the proxy destructor.

State and persistence: each channel tracks control/user channel IDs, head/window ID, memory/push buffer, suspend put pointer, and optional GSP RM object. `disp->chan[]` is the live lookup table used by interrupt/error paths.

Dependencies and integration points: depends on NVKM object/proxy classes, RAMHT, NVIF display channel ABI, DMAOBJ engine classes, and generation-specific channel function tables from files such as `gf119.c`, `gp102.c`, and `gv100.c`.

Risks: argument validation ties push-buffer presence to channel type; wrong `ctrl`/`user` offsets can corrupt another channel. The live slot is protected by a spinlock, but hardware callbacks must tolerate concurrent interrupts and teardown. RAMHT removal must pair exactly with successful binds.

Test signals: create duplicate channels and expect `-EBUSY`, pass malformed args and unsupported versions, map channel registers, create DMAOBJ children, and exercise init/fini with suspend resume and interrupt delivery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/chan.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/chan.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/chan.h

Purpose: private display channel header defining `struct nvkm_disp_chan`, channel function tables, user-channel descriptors, method-list metadata, and cross-generation exported channel helpers.

Important APIs and types: `struct nvkm_disp_chan` stores callback pointers, display pointer, control/user channel IDs, head ID, object base, memory/push state, saved suspend put pointer, and optional GSP object. `struct nvkm_disp_chan_func` defines push/init/fini/intr/user/bind callbacks. `struct nvkm_disp_chan_user` binds a public class to a channel function, control ID, user ID, and optional method map. `struct nvkm_disp_chan_mthd` and `nvkm_disp_mthd_list` describe method-to-register debug maps.

Control flow: constructors in `chan.c` consume these descriptors from generation `nvkm_disp_func.user[]` arrays. Debug/error paths use method maps through `nv50_disp_chan_mthd()`.

State and persistence: no runtime state itself, but it fixes the layout and saved state fields used across all display channel generations, including `suspend_put`.

Dependencies and integration points: depends on `core/object.h`, display private state, GSP object state, and numerous generation exports (`nv50`, `gf119`, `gp102`, `gv100` channel functions and method maps).

Risks: changing struct layout or callback contracts affects every generation file. Incorrect extern declarations can silently mismatch shared method maps or channel functions during refactors.

Test signals: build coverage across all display generations plus runtime channel creation and error decoding on NV50 through Ampere-class hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/chan.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/conn.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/conn.c

Purpose: creates and destroys display connector objects from VBIOS connector table entries and translates BIOS HPD bitmasks into GPIO line numbers.

Important APIs and functions: `nvkm_conn_new()` allocates and constructs a `struct nvkm_conn`; `nvkm_conn_del()` removes and frees it. `nvkm_conn_ctor()` copies `struct nvbios_connE`, initializes the HPD field to unused, logs connector metadata, maps BIOS HPD bit positions through a static `hpd[]` function table, and resolves the actual GPIO line with `nvkm_gpio_find()`.

Control flow: construction is linear. If the BIOS HPD mask is empty, the connector remains without HPD. If the bit index is out of the supported table or GPIO lookup fails, construction keeps the object but leaves `conn->info.hpd` unused and logs an error.

State and persistence: persistent connector state includes display pointer, connector index, copied BIOS connector info, list node, and object base. HPD line translation is stored in `conn->info.hpd`.

Dependencies and integration points: depends on BIOS connector parsing, GPIO subdevice lookup, display object lists, and output creation/HPD event paths that consume `conn->info`.

Risks: BIOS HPD bit encoding is hardware/firmware-specific; an unmapped index disables hotplug detection for that connector. Keeping construction successful after HPD errors is deliberate but can hide broken hotplug until runtime.

Test signals: parse connector tables on systems with internal panels, DP/HDMI, and no-HPD outputs; verify HPD GPIO line resolution and hotplug events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/conn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/conn.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/conn.h

Purpose: private connector header defining `struct nvkm_conn`, constructor/destructor prototypes, and connector-scoped logging macros.

Important APIs and types: `struct nvkm_conn` stores the owning display, connector index, VBIOS `nvbios_connE` data, list node, and embedded `nvkm_object`. `nvkm_conn_new()` and `nvkm_conn_del()` manage lifetime. `CONN_ERR`, `CONN_DBG`, and `CONN_TRACE` format messages with connector index/location/type.

Control flow: no runtime control flow; this header is consumed by connector construction, display teardown, output handling, and user connector wrappers.

State and persistence: defines the connector object state that is linked into `disp->conns` and referenced by outputs.

Dependencies and integration points: includes display private state, BIOS connector definitions, and NVKM logging macros through display subdev.

Risks: connector info is copied from BIOS and may be referenced by output code; layout changes must preserve users of `conn->info`. Logging macros assume `conn->disp` is valid.

Test signals: build and connector lifetime tests, especially teardown ordering with outputs still referencing connectors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/conn.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/dp.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/dp.c

Purpose: generic DisplayPort output implementation: AUX transfers, AUX/eDP power management, link training, LTTPR repeater handling, VBIOS script execution, MST ID helpers, and DP output construction.

Important APIs and functions: `nvkm_dp_new()` creates a DP `nvkm_outp`, resolves the AUX channel from the DCB entry, requires BIOS DP output data, and records whether MST is enabled in the DP table. `nvkm_dp_enable()` switches AUX monitoring and eDP panel power. `nvkm_dp_disable()` runs the DisableLT script. `nvkm_dp_train()` is the public train/retrain callback. Helpers `nvkm_dp_train_link()`, `nvkm_dp_train_cr()`, `nvkm_dp_train_eq()`, `nvkm_dp_train_drive()`, and `nvkm_dp_train_pattern()` implement sink/LTTPR training.

Control flow: training chooses the requested rate, locks `outp->dp.mutex`, populates `ior->dp` state, runs spread and before-training scripts, configures source links through `ior->func->dp->links()`, powers lanes, trains each LTTPR from farthest to sink using clock recovery then channel EQ, clears training pattern, runs after-training script, and unlocks. Retrain skips source reconfiguration and only repeats sink/repeater link training.

State and persistence: updates `outp->dp.enabled`, `aux_pwr`, `aux_pwr_pu`, cached DPCD, link-training target state, and `ior->dp` fields (`mst`, `ef`, `bw`, `nr`). eDP panel power GPIO may be toggled and later restored.

Dependencies and integration points: uses DRM DP register definitions, NVKM AUX/I2C, GPIO, BIOS DP output and init scripts, IOR DP callbacks for hardware-specific drive/pattern/power/link programming, and output acquire/release infrastructure.

Risks: link training is timing-sensitive and sink-dependent. The Ampere IED hack compensates for unchanged VBIOS table versions and must be preserved for newer boards. AUX power management affects laptop panels and can cause resume delays or external-output interference if GPIO restoration is wrong.

Test signals: DP and eDP hotplug, AUX reads/writes, link training at all advertised rates/lane counts, LTTPR repeater chains, MST enablement, suspend/resume, retraining without full modeset, and failure logging on bad sinks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/dp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/dp.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/dp.h

Purpose: DisplayPort private header exposing DP output constructors/control helpers and local DPCD address/bit definitions used by `dp.c` and output/IOR code.

Important APIs and definitions: declares `nvkm_dp_new()`, `nvkm_dp_disable()`, and `nvkm_dp_enable()`. Defines DPCD receiver capability offsets, link configuration fields, link/sink status bits, sink power control, and LTTPR addresses for training repeaters.

Control flow: no runtime control flow. The constants drive read/write decisions in link training and AUX power paths.

State and persistence: none directly; the constants describe sink-side state accessed over AUX.

Dependencies and integration points: includes `outp.h` and complements DRM DP definitions. Generation-specific IOR DP callbacks rely on the training code using these DPCD constants consistently.

Risks: wrong bit definitions can break link training in non-obvious ways. Some constants overlap with external DRM headers, so future cleanup must avoid conflicting semantics.

Test signals: successful DP link training, DPCD capability parsing, LTTPR support, and sink power transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/dp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/g84.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/g84.c

Purpose: G84/G82-era display implementation layered on NV50 display infrastructure. It adds HDMI programming for early SORs, defines G84 base/core/overlay method maps, and registers the generation display class.

Important APIs and functions: `g84_disp_new()` constructs display with `g84_disp`. `g84_sor_new()` creates SOR IORs using `g84_sor`. HDMI callbacks `g84_sor_hdmi_ctrl()`, `g84_sor_hdmi_infoframe_avi()`, and `g84_sor_hdmi_infoframe_vsi()` implement `g84_sor_hdmi`. Exports include `g84_disp_base`, `g84_disp_ovly`, `g84_disp_core`, and method maps used by later generations.

Control flow: HDMI enable writes audio infoframe registers, ACR/CTS controls, lookup reset bits, and `HDMI_CTRL`; disable clears HDMI and infoframe enable bits. Display construction delegates oneinit/init/fini/intr/supervisor/event handling to NV50 helpers, while user classes map cursor, overlay immediate, base DMA, core DMA, and overlay DMA channels.

State and persistence: hardware state is programmed in SOR/head registers and channel method maps. IOR objects persist in `disp->iors`; method maps are static debug/validation metadata.

Dependencies and integration points: uses NV50 head/DAC/SOR/PIOR helpers, `pack_hdmi_infoframe()`, NVIF G82 display classes, and shared method maps from `nv50`.

Risks: early HDMI register programming has unknown fields and incomplete VSI subpacket handling, as noted by comments. Method/register maps must match hardware class ABI or error diagnostics and channel programming become misleading.

Test signals: G84/G82 modeset, HDMI audio/infoframes, base/overlay/core channel creation, method error dump decoding, and vblank/hotplug behavior through NV50 shared code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/g84.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/g94.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/g94.c

Purpose: GT206/G94 display implementation extending NV50/G84 with DisplayPort SOR support, SOR state decoding, and a clock/power workaround path for TMDS SORs.

Important APIs and functions: `g94_disp_new()` constructs `g94_disp`; `g94_sor_cnt()` reads available SOR mask; `g94_sor_state()` decodes LVDS/TMDS/DP protocol and link from hardware; `g94_sor_dp` exposes DP `links`, `power`, `pattern`, `drive`, audio symbol, active symbol, and watermark callbacks. Workaround helpers are `g94_sor_war_needed()`, `_war_2()`, `_war_3()`, and `_war_update_sppll1()`.

Control flow: DP setup programs lane count, enhanced framing, link rate clock selection, lane power masks, training patterns, drive/pre-emphasis registers, and audio/active symbol registers. WAR paths detect certain TMDS clock configurations, manipulate SOR power sequencing and SPPLL1 state, and restore power if needed.

State and persistence: hardware SOR registers hold DP training parameters, TMDS state, workaround clock selections, and arm/asy decoded IOR state. Static core method maps extend G84 with four SOR entries.

Dependencies and integration points: reuses NV50 display lifecycle, G84 HDMI, G84 base channels, GT200 overlay, and NVIF GT206 classes. DP generic training in `dp.c` calls into `g94_sor_dp`.

Risks: clock workaround sequencing is delicate and waits on hardware state with timeouts. Lane mapping `{2,1,0,3}` must match board routing. Unsupported training pattern inputs WARN and return without programming.

Test signals: DP link training on G94/GT206, TMDS modesets through SOR WAR transitions, HDMI inherited behavior, SOR count detection, and method-error dumps for core channels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/g94.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/ga102.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/ga102.c

Purpose: Ampere GA102 display implementation, extending GV100/TU102-style display with GA102 SOR DP link programming and GSP-RM delegation support.

Important APIs and functions: `ga102_disp_new()` chooses `r535_disp_new()` when `nvkm_gsp_rm(device->gsp)` is active, otherwise constructs `ga102_disp` with `nvkm_disp_new_()`. `ga102_sor_new()` creates SORs with HDA capability bits from `0x08a15c`. `ga102_sor_dp_links()` maps DP bandwidth codes to SOR clock settings, including UHBR-like values, and programs MST/enhanced-frame/link lane controls. `ga102_sor_clock()` handles TMDS high-speed clock divide.

Control flow: display lifecycle uses `tu102_disp_init`, `gv100_disp_fini`, `gv100_disp_intr`, and `gv100_disp_super`. User classes expose caps, cursor, window immediate, core, and window DMA channels. DP link setup programs clock select, waits briefly, toggles link control bits, then writes final DP control.

State and persistence: SOR route, state, clock, HDA, DP, HDMI, and backlight state is stored in IOR hardware registers. The display object uses a larger `ramht_size = 0x2000` and GV100 window/head/SOR object models.

Dependencies and integration points: depends on GSP subdev, R535 RM display path, GV100/TU102 helpers, GM200 SOR routing, GV100 HDMI/HDA/audio/watermark, TU102 VCPI, and NVIF GA102 display classes.

Risks: two construction paths (native NVKM and GSP RM) must expose compatible behavior. DP bandwidth mapping returns `-EINVAL` on unknown codes, so new rates require explicit support. The fixed 40 ms delay is a hardware workaround and should not be removed casually.

Test signals: GA102 modeset under both native and GSP-RM modes, DP rates/lane counts including high-rate codes, HDMI high-speed TMDS, HDA presence, window channel creation, and interrupt handling through GV100 paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/ga102.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/gf119.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/gf119.c

Purpose: GF119/GF110 display implementation and a major shared base for Fermi/Kepler/Maxwell/Pascal display generations. It implements SOR/DAC/head callbacks, HDMI/DP/HDA support, channel init/fini/bind, event handling, supervisor work, interrupt handling, and generation method maps.

Important APIs and functions: exported callbacks include `gf119_sor_hda`, `gf119_sor_dp`, `gf119_sor_clock()`, `gf119_sor_state()`, `gf119_sor_cnt()`, `gf119_dac_new()/cnt()`, `gf119_head_new()/cnt()`, `gf119_disp_chan_uevent`, `gf119_disp_chan_intr()`, `gf119_disp_dmac_func`, `gf119_disp_pioc_func`, `gf119_disp_core_func`, `gf119_disp_base`, `gf119_disp_curs`, `gf119_disp_oimm`, `gf119_disp_core_fini()`, `gf119_disp_super()`, `gf119_disp_intr_error()`, `gf119_disp_intr()`, `gf119_disp_init()`, and `gf119_disp_fini()`. `gf119_disp_new()` registers the GF110 display class set.

Control flow: init copies CRTC/DAC/SOR capabilities into EVO-visible registers, steals display from VBIOS if needed, points display to `disp->inst`, enables interrupts, and disables underflow reporting. Interrupt handling dispatches user events, channel errors, supervisor work, and per-head vblank notifications. Supervisor work runs phased NV50 supervisor helpers based on pending bits. Channel init programs push buffer, control registers, saved put pointers, and waits for inactive state.

State and persistence: state spans SOR/DAC/head hardware registers, HDA ELD/HPD state, DP MST/VCPI/audio/watermark registers, channel `suspend_put`, `disp->super.pending`, RAMHT bindings, and static method maps for base/core/overlay channels.

Dependencies and integration points: reuses NV50 supervisor helpers and method dumps, GT215 backlight, G94 DP power, HDMI infoframe packing, RAMHT, timer delays, NVIF classes, and display event framework. Later generations reuse most of its functions.

Risks: this file is broad and highly hardware-sensitive. Interrupt acknowledgement order, channel timeout waits, VBIOS takeover, and underflow masking can affect stability. Method maps and channel IDs must match each generation's class tables.

Test signals: GF119 display probe, modeset, HDMI/DP/HDA audio, MST VCPI, vblank events, channel creation/fini with suspend resume, injected method errors, and downstream generations that reuse these callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/gf119.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/gk104.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/gk104.c

Purpose: GK104 display generation definition. It reuses GF119 lifecycle and channel mechanics, adds GK104 HDMI register programming, SOR construction, overlay/core method maps, and class registration.

Important APIs and functions: `gk104_disp_new()` constructs `gk104_disp`; `gk104_sor_new()` creates HDA-capable SORs with `gk104_sor`; exported HDMI callbacks are `gk104_sor_hdmi_ctrl()`, `_infoframe_avi()`, and `_infoframe_vsi()`. Exports `gk104_disp_ovly`, `gk104_disp_core`, and their method maps for later generations.

Control flow: HDMI enable writes generic/AVI infoframe registers in the `0x690xxx` range, programs an unknown infoframe/control register, and updates `0x616798` HDMI control. Display lifecycle delegates to `gf119_disp_init/fini/intr/super` with `nv50_disp_oneinit`.

State and persistence: SOR clock/state/backlight/DP/HDA come from `gf119`/`gt215`; HDMI state is in GK104-specific registers. Core channel method maps expand head register coverage and use negative `prev` offsets for method dump traversal.

Dependencies and integration points: uses GF119 head/DAC/SOR count and channel functions, GT215 backlight, GF119 DP/HDA, NVIF GK104 classes, and HDMI packing helper.

Risks: HDMI VSI handling still lacks extra subpacket writes. Reused GF119 DP lane mapping and SOR state must match GK104 hardware. Method maps are large static ABI descriptions and easy to regress during register-map edits.

Test signals: GK104 HDMI infoframes/audio, DP modesets, base/core/overlay channel creation, method error decoding, and suspend/resume inherited from GF119.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/gk104.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/gk110.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/gk110.c

Purpose: compact GK110 display generation registration. It reuses GK104/GF119 behavior with GK110-specific root, base, and core channel classes.

Important APIs and functions: `gk110_disp_new()` constructs `gk110_disp`. The `gk110_disp` table uses `nv50_disp_oneinit`, `gf119_disp_init/fini/intr/intr_error/super`, GF119 event handling, GF119 head/DAC counts, `gk104_sor_new`, and GK104/GF119 channel descriptors.

Control flow: no unique hardware routines. Construction routes through `nvkm_disp_new_()`, and runtime behavior follows inherited callbacks.

State and persistence: same display state as GF119/GK104. Class table differences select `GK110_DISP_BASE_CHANNEL_DMA` and `GK110_DISP_CORE_CHANNEL_DMA`.

Dependencies and integration points: depends on `gk104.c` exported SOR/core/overlay method maps and `gf119.c` display engine callbacks.

Risks: because behavior is inherited, the main risk is class-ID mismatch. If GK110 differs in a register detail not represented here, reused callbacks can produce subtle modeset failures.

Test signals: GK110 probe, class enumeration, base/core/cursor/overlay channel creation, DP/HDMI modeset, vblank, and method error reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/gk110.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/gm107.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/gm107.c

Purpose: GM107/Maxwell display generation registration with a Maxwell-specific SOR DP training-pattern callback and otherwise GF119/GK104-derived behavior.

Important APIs and functions: `gm107_disp_new()` constructs `gm107_disp`; `gm107_sor_new()` creates HDA-capable SORs; `gm107_sor_dp_pattern()` supports DP training patterns 0 through 4 and programs link-specific pattern registers. `gm107_sor_dp` uses GF119 links/drive/audio/VCPI/watermark plus G94 lane power.

Control flow: the DP pattern callback selects register `0x61c110` or `0x61c12c` based on active link and writes repeated pattern codes. Display runtime delegates to GF119 init/fini/intr/super and GK104 method maps.

State and persistence: DP pattern state is in SOR link registers; SOR, head, DAC, channel, and supervisor state follow GF119. User classes use GM107 core class with GK110 base and GK104 overlay/control classes.

Dependencies and integration points: uses GF119 SOR state/clock/HDA, GK104 HDMI, GT215 backlight, GF119 channel helpers, and NVIF GM107 classes.

Risks: pattern 4 support is required by newer DP sinks; writing the wrong link register can break dual-link setups. Reused channel IDs must match GM107 hardware.

Test signals: GM107 DP link training with TPS4-capable sinks, HDMI modesets, channel class creation, suspend/resume, and inherited GF119 interrupt behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/gm107.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/gm200.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/gm200.c

Purpose: GM200/Maxwell display generation support, adding post-cursor DP drive programming, HDMI 2.0 SCDC/scrambling control, SOR route get/set, and HDA capability detection.

Important APIs and functions: `gm200_disp_new()` constructs `gm200_disp`; `gm200_sor_new()` creates SORs with HDA bits from fuse/cap registers; `gm200_sor_dp_drive()` writes drive, pre-emphasis, power-up, and post-cursor registers; `gm200_sor_hdmi_scdc()` controls scrambling/high-speed TMDS; route helpers `gm200_sor_route_set()` and `gm200_sor_route_get()` map DCB output sublinks to SOR/link selections. Exports `gm200_sor_dp` and `gm200_sor_hdmi`.

Control flow: route set writes per-sublink mux registers based on output `sorconf.link` and current IOR link. Route get reads both sublinks, validates dual-link consistency, and returns the SOR ID. Display lifecycle uses GF119 callbacks and GK104 method maps with a GM200 core class.

State and persistence: persistent hardware state includes SOR mux routing, TMDS high-speed flag, SCDC scrambling bits, DP drive/post-cursor registers, HDA capability, and inherited channel/head state.

Dependencies and integration points: depends on GF119 display core, GM107 DP pattern, GK104 HDMI base behavior, GT215 backlight, and output DCB routing metadata from `outp`.

Risks: route validation returns `-1` for missing or inconsistent SORs; incorrect muxing can disconnect outputs. SCDC control must align with sink HDMI 2.0 support and pixel clock. HDA bit source differs depending on a capability flag.

Test signals: GM200 HDMI 2.0 high-clock modes with scrambling, DP training with post-cursor adjustment, dual-link route detection, audio/HDA, and channel class creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/gm200.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/gp100.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/gp100.c

Purpose: GP100/Pascal display generation registration, primarily reusing GM200 SOR routing/DP/HDMI behavior with GP100-specific HDA capability probing and class IDs.

Important APIs and functions: `gp100_disp_new()` constructs `gp100_disp`; `gp100_sor_new()` creates SORs using `gp100_sor`. The `gp100_sor` function table reuses GM200 route get/set, GF119 SOR state/clock/HDA, GT215 backlight, GM200 HDMI and DP callbacks.

Control flow: SOR construction checks `0x08a15c`; if the high flag is not set, it reads HDA capability from `0x10ebb0 >> 8`. Display lifecycle delegates to GF119 init/fini/intr/super and class table exposes GP100 core DMA class with GK110 base and GK104 overlay classes.

State and persistence: no unique runtime state beyond HDA capability source and Pascal class selection. Inherited SOR routing, DP, HDMI, channel, and head state apply.

Dependencies and integration points: depends on GM200 SOR routing/DP/HDMI, GF119 display infrastructure, GK104 method maps, and NVIF GP100 class IDs.

Risks: HDA capability register interpretation differs from GM200; wrong bit shifting affects audio exposure. Lack of DAC entry reflects display hardware assumptions and should be validated against supported boards.

Test signals: GP100 probe, SOR/HDA detection, DP/HDMI modesets, class enumeration, and inherited channel/interrupt behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/gp100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/gp102.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/gp102.c

Purpose: GP102/Pascal display support that adjusts DMA channel register layout and error reporting while reusing GP100/GM200 SOR behavior.

Important APIs and functions: `gp102_disp_new()` constructs `gp102_disp`. `gp102_disp_dmac_init()` and `gp102_disp_core_init()` program channel push/control registers at `0x61149x` instead of GF119's `0x61049x`. `gp102_disp_dmac_func` and `gp102_disp_core_func` reuse GF119 fini/intr/user/bind logic. `gp102_disp_intr_error()` reads error state from `0x6111f0` registers.

Control flow: channel init writes push address, control fields, saved `suspend_put`, activates the channel, then waits for the inactive bit to clear/settle. Error handling logs method/data/unknown fields, dumps method maps for method `0x0080`, acknowledges the channel bit, and resets the error register.

State and persistence: channel state includes saved put pointers and live register programming in the Pascal channel register block. Display state otherwise follows GF119/GP100. User channel descriptors shift cursor and immediate user IDs to 17 and 13.

Dependencies and integration points: uses GP100 SOR creation, GF119 display init/fini/intr/super/event helpers, GF119/GK104 method maps, and NVIF GP102 classes.

Risks: register-base differences are the key hazard; using GF119 init on GP102 channels would program the wrong block. Error decoding differs and must acknowledge the right registers to avoid interrupt storms.

Test signals: GP102 channel creation/init/fini for core/base/overlay/cursor/oimm, method error injection, suspend/resume preserving `suspend_put`, DP/HDMI modesets, and interrupt ack behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/gp102.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/gt200.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/gt200.c

Purpose: GT200 display generation registration and overlay method map extension on top of G84/NV50 display behavior.

Important APIs and functions: `gt200_disp_new()` constructs `gt200_disp`. `gt200_disp_ovly` defines the GT200 overlay DMA channel using `nv50_disp_dmac_func`, control/user channel 3, and a GT200-specific method map with additional color/key/scaler-style registers.

Control flow: no unique runtime callbacks beyond constructor. Display lifecycle uses `nv50_disp_oneinit/init/fini/intr/super`, NV50 event handling, NV50 head/DAC/SOR/PIOR counts, G84 SOR creation, G84 base/core channels, and GT200 overlay channel.

State and persistence: static overlay method metadata and inherited NV50 display state. User-visible root class is `GT200_DISP`.

Dependencies and integration points: depends on G84 exported base/core/SOR helpers, NV50 display infrastructure, and NVIF GT200 classes.

Risks: overlay method map differences are the main generation-specific risk. Wrong root or class IDs would prevent userspace from creating expected channels.

Test signals: GT200 probe, overlay DMA channel creation, overlay method error decode, inherited HDMI/DP/modeset behavior where hardware supports it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/gt200.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/gt215.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/gt215.c

Purpose: GT215/GT214 display generation support adding HDA audio, DP audio control, GT215 HDMI register layout, SOR backlight control, and display class registration.

Important APIs and functions: `gt215_disp_new()` constructs `gt215_disp`; `gt215_sor_new()` creates HDA-capable SORs. Exports `gt215_sor_hda`, `gt215_sor_dp_audio()`, `gt215_sor_hdmi`, and `gt215_sor_bl`. Backlight helpers read/write PWM divisor/value registers. HDMI infoframe/control callbacks mirror G84 behavior at SOR-relative addresses.

Control flow: HDA ELD writes up to `0x60` bytes and marks ELD valid; HPD toggles presence bits. DP audio sets an enable bit and waits for hardware ack. HDMI enable writes audio/AVI/VSI infoframes, ACR/CTS, lookup reset, and HDMI control; disable clears all infoframe/control enables. Display lifecycle otherwise uses NV50/G94 helpers.

State and persistence: HDA ELD/HPD state, DP audio enable, HDMI infoframes, backlight PWM value, and inherited display channels/heads/IORs. The SOR function table uses G94 state, NV50 power/clock, G94 DP, and GT215 HDA/HDMI/backlight.

Dependencies and integration points: depends on G94 DP helpers and SOR count, G84 base/overlay/core maps, NV50 lifecycle, HDMI packing, timer waits, and NVIF GT214 classes.

Risks: HDMI register comments include unknown fields and partial VSI subpacket handling. Backlight math assumes divisor/value relationship and returns 100 on invalid reads. HDA ELD sizing must not exceed hardware expectations.

Test signals: GT215 HDMI audio/infoframes, DP audio, HDA ELD/HPD, eDP backlight get/set, and GT214 channel class creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/gt215.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/gv100.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/gv100.c

Purpose: GV100/Volta display implementation, introducing the modern window/channel model, caps object, GV100 SOR/head callbacks, interrupt decode, supervisor flow, and display classes reused by later generations.

Important APIs and functions: `gv100_disp_new()` constructs `gv100_disp`. Exports include `gv100_sor_hda`, `gv100_sor_dp` helpers, `gv100_sor_hdmi`, `gv100_sor_new()/cnt()`, `gv100_head_new()/cnt()`, `gv100_disp_chan_user()`, `gv100_disp_dmac_init/fini/bind()`, window immediate/window/cursor/core channel descriptors, `gv100_disp_wndw_cnt()`, `gv100_disp_caps_new()`, `gv100_disp_super()`, `gv100_disp_intr()`, `gv100_disp_fini()`, and `gv100_disp_init()`.

Control flow: display classes expose a caps object plus cursor, window-immediate, core, and window DMA channels. Channel user mapping uses `0x690000 + user * 0x1000`; core uses a distinct user mapping. Init copies capability registers, sets display instance memory, initializes interrupt masks, and prepares GV100-specific window/head/SOR resources. Interrupt handling dispatches head timing/vblank, window exceptions, immediate window exceptions, other exceptions, and control-display events.

State and persistence: persistent state includes GV100 SOR/head/window hardware, channel put pointers, caps object MMIO mapping (`0x640000` range), supervisor pending state, and per-window/head method maps.

Dependencies and integration points: uses NV50 oneinit and supervisor pieces where still applicable, GM200 SOR routing for later variants, HDMI packing, RAMHT, event framework, and NVIF GV100 classes. GA102 and TU102 build on these exports.

Risks: interrupt/error decode is more complex than GF119 and must acknowledge multiple status domains. Window channel count comes from hardware masks. Caps object mapping exposes display capability MMIO to userspace-facing NVIF paths and must stay read-only/controlled by object semantics.

Test signals: GV100 window/core/cursor channel creation, caps object map/read, DP/HDMI modeset, HDA, vblank, window exception logging, suspend/resume, and downstream GA/TU generation reuse.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/gv100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/hdmi.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/hdmi.c

Purpose: utility for packing raw HDMI infoframe bytes into the register layout used by Nouveau SOR HDMI callbacks.

Important APIs and functions: `pack_hdmi_infoframe()` fills `struct packed_hdmi_infoframe` fields: `header`, `subpack0_low`, `subpack0_high`, `subpack1_low`, and `subpack1_high`. It accepts a raw byte buffer and a length.

Control flow: a fallthrough switch copies bytes 0 through up to 16 into little-endian-style 32-bit register words. Inputs longer than 17 bytes are intentionally truncated to 17 bytes; length 0 leaves all packed fields zero. The fallthrough implementation lets one switch handle every short length without loops.

State and persistence: no persistent state. The packed result is consumed immediately by generation HDMI callbacks in G84, GT215, GF119, GK104, GV100, and descendants.

Dependencies and integration points: includes `hdmi.h`; callers write packed fields to hardware infoframe registers and handle enable/disable bits.

Risks: assumes no valid frame needed by these hardware paths exceeds 17 octets including header. The function does not validate `raw_frame` for nonzero length; callers must pass a valid buffer. Byte ordering must match hardware register expectations.

Test signals: compare packed output for known AVI/VSI infoframes, check len 0 through 17, check truncation for longer frames, and verify HDMI infoframes on a sink analyzer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/hdmi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/hdmi.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/hdmi.h

Purpose: header for the HDMI infoframe packing helper and packed register-word structure.

Important APIs and types: `struct packed_hdmi_infoframe` stores one `header` word and four subpacket words. `pack_hdmi_infoframe()` converts raw bytes into this structure. Including `ior.h` ties the helper to display output-resource code.

Control flow: none in the header; generation HDMI callbacks call the declared helper before writing registers.

State and persistence: none directly; instances are stack-local in callers.

Dependencies and integration points: included by generation SOR HDMI implementations. The struct field order mirrors common hardware write order in those files.

Risks: changing field names/order requires updates to all generation HDMI callbacks. The helper contract permits truncation and does not include validation metadata.

Test signals: build all HDMI callback users and validate packed values through `hdmi.c` tests or sink-visible infoframes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/hdmi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/head.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/head.c

Purpose: common display head object lifetime and lookup helpers. Heads represent scanout/timing engines in the NVKM display model.

Important APIs and functions: `nvkm_head_find()` searches `disp->heads` by ID. `nvkm_head_new_()` allocates, initializes function pointer/display/id, links the head into `disp->heads`, and logs construction. `nvkm_head_del()` logs destruction, removes from the list, frees memory, and nulls the caller pointer.

Control flow: simple list allocation/lookup/free. Generation files provide the `nvkm_head_func` callback table for state, raster position/clock, and vblank enablement.

State and persistence: persistent per-head state is defined in `head.h`; this file owns list membership and lifecycle. Deletion mutates the display's head list.

Dependencies and integration points: used by display generation oneinit paths and vblank event code in `base.c`. User head wrappers and supervisor/modeset code look up or iterate these objects.

Risks: deleting heads while events or outputs still reference them would break vblank and state queries; display destructor ordering currently finalizes events before deleting heads.

Test signals: head count creation on probe, `nvkm_head_find()` for valid/invalid IDs, vblank event init/fini, and teardown leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/head.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/head.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/head.h

Purpose: private display head header defining head state, callback contracts, constructors, and generation-specific head exports.

Important APIs and types: `struct nvkm_head` stores callback table, display pointer, ID, list node, arm/asy `nvkm_head_state`, and embedded object. `nvkm_head_state` stores horizontal/vertical totals, sync and blanking edges, refresh rate, and pre-GF119 output depth. `struct nvkm_head_func` supplies state readout, raster position, raster clock divisor, and vblank get/put callbacks.

Control flow: no direct flow; generation files instantiate heads with `nvkm_head_new_()` and implement callbacks such as `nv50_head_new`, `gf119_head_new`, and `gv100_head_new`.

State and persistence: defines the cached arm/asy state fields used by modeset/supervisor code. Vblank callback state is hardware-owned and controlled through function pointers.

Dependencies and integration points: includes NVIF object definitions and display private state. `base.c` uses `vblank_get/put` through this contract; generation files use count/new exports.

Risks: field width choices (`u16` timings, `u32 hz`) must match hardware register decoding. Adding state fields requires updating generation state readers.

Test signals: head state reads across generations, vblank subscription/unsubscription, raster position queries, and modeset state comparison.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/head.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/ior.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/ior.c

Purpose: common output-resource object lifecycle and lookup helpers. IORs represent DAC, SOR, and PIOR hardware resources used to drive connectors.

Important APIs and functions: `nvkm_ior_find()` searches `disp->iors` for a matching type and optional ID. `nvkm_ior_new_()` allocates an IOR, initializes callbacks, display pointer, type, ID, HDA flag, human-readable name (`DAC-0`, `SOR-1`, etc.), links it into `disp->iors`, and logs construction. `nvkm_ior_del()` removes and frees an IOR.

Control flow: simple list management. Generation files provide `nvkm_ior_func` tables for state, power, clock, HDMI, DP, HDA, backlight, route, and sense behavior.

State and persistence: persistent state is held in `struct nvkm_ior` as defined in `ior.h`, including function table, type/id, HDA capability, name, and arm/asy protocol state. This file owns allocation and list membership.

Dependencies and integration points: used by display oneinit/generation constructors, output acquire/release paths, DP/HDMI programming, and base display init which powers all IORs through their callbacks.

Risks: ID/type matching must reflect hardware masks; wrong HDA flag changes audio exposure. Teardown ordering must ensure outputs release IORs before IOR deletion.

Test signals: IOR count/mask creation on each generation, output acquire/release, HDMI/DP/DAC modesets, audio capability detection, and display teardown leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/ior.c -->
