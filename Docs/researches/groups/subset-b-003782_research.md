# subset-b-003782 Research

Grouped research for Intel Xe DRM driver files under `sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/`. Each section preserves the source path in its title and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pat.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pat.c

## Purpose

`xe_pat.c` owns the Xe driver's page attribute table programming. It defines the platform-specific PAT register encodings for Xe_LP, Xe_HP/G, Xe_HPC, Xe_LPG, Xe2, Xe3, and Xe3p variants, maps driver cache levels to PAT indices, programs graphics and media GT PAT registers, and exposes debug dump helpers for hardware and software PAT state.

## Important APIs, Types, and Functions

The core private type is `struct xe_pat_ops`, which selects graphics/media programming functions, hardware dump behavior, and the modern entry formatter. `xe_pat_init_early()` selects the PAT table, ATS/PTA special entries, entry count, and `xe->pat.idx[]` cache-level map from platform/IP version. `xe_pat_init()` writes the table to a GT unless running as an SR-IOV VF. `xe_pat_dump()` reads hardware registers with forcewake, while `xe_pat_dump_sw_config()` prints the software-selected table. Query helpers `xe_pat_index_get_coh_mode()`, `xe_pat_index_get_comp_en()`, and `xe_pat_index_get_l3_policy()` expose PAT metadata used by page-table and BO code.

## Control Flow and State

Initialization starts before GT bring-up with platform dispatch in `xe_pat_init_early()`. Older platforms use compact four/eight-entry tables and direct or MCR programming paths. Xe2 and newer use 32-entry tables with no-promote, compression, L3 class, L3/L4 policy, and coherency fields; some entries are intentionally reserved and marked invalid. Later `xe_pat_init()` chooses media or graphics programming based on GT type and writes `_PAT_INDEX()`, optional `_PAT_ATS`, and optional `_PAT_PTA` registers. Persistent state lives in `xe->pat`: selected table pointer, operation table, entry count, cache index map, and special ATS/PTA entries.

## Dependencies and Integration Points

This file depends on register definitions, MCR multicast access, forcewake, platform macros, workarounds, SR-IOV mode checks, and the UAPI cache-level concepts in `xe_drm.h`. Page-table encoding relies on the cache-to-PAT index map and query helpers. Debugfs and diagnostics call the dump paths through `drm_printer`.

## Risks and Test Signals

The highest risk is platform table drift: wrong PAT encodings cause subtle coherency, compression, or cacheability bugs. The query helpers only warn on out-of-range indices and still dereference the table. Xe2+ compression combined with coherency is explicitly constrained by CCS clearing behavior. Tests should verify platform selection, entry counts, reserved entry formatting, cache-level index map, SR-IOV VF no-op programming, MCR versus non-MCR media/graphics access, and debug dump behavior when forcewake cannot be acquired.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pat.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pat.h

## Purpose

`xe_pat.h` is the public interface for Xe PAT setup and introspection. It defines the PAT table entry metadata shared with the rest of the driver, cache/coherency constants, and the functions used during early device setup, GT hardware programming, page-table encoding, and diagnostics.

## Important APIs and Types

`struct xe_pat_table_entry` contains a platform-specific register `value`, a normalized `coh_mode`, and a `valid` bit for reserved entries. `XE_COH_NONE`, `XE_COH_1WAY`, and `XE_COH_2WAY` are the normalized coherency modes. `XE_PAT_INVALID_IDX` marks absent cache-level mappings. Exported functions are `xe_pat_init_early()`, `xe_pat_init()`, `xe_pat_dump()`, `xe_pat_dump_sw_config()`, `xe_pat_index_get_coh_mode()`, `xe_pat_index_get_comp_en()`, and `xe_pat_index_get_l3_policy()`. The header also publishes the L3 policy constants `XE_L3_POLICY_WB`, `XE_L3_POLICY_XD`, and `XE_L3_POLICY_UC`.

## Control Flow and State

Callers initialize software PAT selection once per device with `xe_pat_init_early()`, program each GT with `xe_pat_init()`, and later query table metadata by PAT index. The header itself stores no state; it exposes access to `xe_device` state filled by `xe_pat.c`.

## Dependencies and Integration Points

The interface is consumed by device probe, GT initialization, debug printers, BO/page-table encoding, and any logic that needs to inspect cacheability, coherency, compression, or L3 policy from a selected PAT index.

## Risks and Test Signals

Because this header is a cross-module contract, enum-like constants and function semantics must stay synchronized with `xe_pat.c` and `xe_pt_types.h`. Test signals include successful compile coverage across PAT users, valid behavior for invalid cache mappings, and platform tests that verify compression and coherency metadata match the programmed table.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pci.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pci.c

## Purpose

`xe_pci.c` is the PCI driver front door for Xe. It binds Intel PCI IDs to static device descriptors, enforces force-probe policy, initializes early device/platform/IP information, allocates tiles and GTs, wires the DRM device into PCI probe/remove/shutdown, and provides system/runtime PM callbacks for PCI D-states.

## Important APIs, Types, and Functions

The file defines static `xe_graphics_desc`, `xe_media_desc`, `xe_ip`, and `xe_device_desc` tables for platforms from Tigerlake through Novalake/Crescent Island. `pciidlist[]` maps PCI IDs to descriptors and registers with `MODULE_DEVICE_TABLE`. Helper functions include `device_id_in_list()`, `id_forced()`, `id_blocked()`, `find_subplatform()`, `read_gmdid()`, `find_graphics_ip()`, `find_media_ip()`, `handle_gmdid()`, `xe_info_init_early()`, `xe_info_probe_tile_count()`, `alloc_primary_gt()`, `alloc_media_gt()`, and `xe_info_init()`. Driver entry points are `xe_pci_probe()`, `xe_pci_remove()`, `xe_pci_shutdown()`, PM callbacks, `xe_pci_to_pf_device()`, `xe_register_pci_driver()`, and `xe_unregister_pci_driver()`.

## Control Flow and State

Probe checks configfs, force-probe allow/deny lists, display deferral, enables the PCI device, creates `xe_device`, stores DRM drvdata, disables PM for unbound bridges, initializes descriptor-only info and the root tile, optionally resizes ReBAR, performs early device probe, handles boot survivability, reads GMD_ID or pre-GMD descriptors, allocates remote tiles/VRAM/GTs, probes display, initializes PM, probes the full device, then enables runtime PM. Remove disables SR-IOV VFs for PFs, skips normal teardown in survivability mode, then removes device state and PM. System sleep calls `xe_pm_suspend()`/`xe_pm_resume()` around PCI state save/restore and D3cold transitions. Runtime suspend/resume toggles D3cold based on `xe->d3cold.allowed`.

## Dependencies and Integration Points

This file integrates Linux PCI/PM/runtime-PM, DRM driver registration, Intel PCI ID macros, configfs feature gating, SR-IOV VF/PF helpers, GMD_ID MMIO, GuC VF bootstrap for GMD_ID reads, display probe, tile/GT allocation, ReBAR, pcode, PM, and survivability mode. KUnit static stubs are present for selected discovery helpers.

## Risks and Test Signals

Descriptor table correctness drives almost every downstream feature bit; wrong fields can mis-size VA, DMA masks, GT counts, engine masks, SR-IOV support, display, flat CCS, PXP, or PM behavior. GMD_ID reads for VFs allocate a temporary GT and can fail early. Force-probe parsing accepts wildcards and negative lists, so module parameter tests are important. Runtime PM asserts no VF lifetime during PF runtime suspend. Test signals include PCI ID matching, force-probe allow/block behavior, descriptor feature snapshots, GMD_ID unknown version rejection, media-fused-off handling, configfs GT gating, tile count reduction from MTCFG, probe error injection cleanup, SR-IOV PF lookup from VF, and D3hot/D3cold suspend/resume paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pci.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pci.h

## Purpose

`xe_pci.h` declares the minimal PCI-driver interface exported outside `xe_pci.c`. It lets module init/exit register or unregister the Xe PCI driver and lets VF-side code resolve the parent PF Xe device.

## Important APIs

`xe_register_pci_driver()` wraps `pci_register_driver()` for the static Xe PCI driver. `xe_unregister_pci_driver()` unregisters it. `xe_pci_to_pf_device(struct pci_dev *pdev)` uses PCI IOV PF drvdata lookup to return the PF `struct xe_device` associated with a VF `pci_dev`, or `NULL` if no matching PF driver data is available.

## Control Flow and State

The header stores no state. The registration functions affect global PCI-driver state in the kernel. PF lookup depends on the PF probe path having stored DRM drvdata on the PCI device and on the PCI core's SR-IOV relationship tracking.

## Dependencies and Integration Points

It forward-declares `struct pci_dev` and `struct xe_device` for use by module setup, SR-IOV, and any helper code that needs to cross from a VF PCI device to the PF driver instance.

## Risks and Test Signals

The API is intentionally tiny, so the main risks are lifecycle misuse and stale PF references. Test signals include module load/unload registering exactly once, VF lookup returning `NULL` when PF driver data is absent or wrong, and correct PF resolution after VFs are enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pci_rebar.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pci_rebar.c

## Purpose

`xe_pci_rebar.c` handles optional Resizable BAR setup for the local-memory BAR. It either forces the VRAM BAR to a module-parameter size or grows it to the largest supported size before the main device probe starts using local memory.

## Important APIs and Functions

The exported function is `xe_pci_rebar_resize(struct xe_device *xe)`. Private `resize_bar()` converts a byte size to PCI ReBAR encoding, calls `pci_resize_resource()`, and logs success or BIOS/platform guidance on failure. `xe_pci_rebar_resize()` reads `xe_modparam.force_vram_bar_size`, inspects `LMEM_BAR`, validates supported sizes with PCI ReBAR helpers, verifies a root bus memory resource above 4 GiB, disables PCI memory decoding, resizes, reassigns unassigned bus resources, and restores the PCI command register.

## Control Flow and State

The function is called during PCI probe after early device info exists and before full device probing. Negative `force_vram_bar_size` disables resizing. Zero means "grow to maximum if larger than current." A positive value requests a specific MiB size. Persistent state is PCI resource sizing and assigned bus resources; the Xe object only provides logging, module parameters, and PCI device access.

## Dependencies and Integration Points

It depends on Linux PCI ReBAR APIs, BAR constants from `xe_bars.h`, module parameters, and Xe logging helpers. It is integrated directly into `xe_pci_probe()`.

## Risks and Test Signals

Resizing PCI resources is platform-sensitive. Failure paths are non-fatal, so later VRAM behavior depends on the existing BAR aperture. The root-resource scan only accepts memory resources above 4 GiB, matching large BAR requirements. Tests should cover disabled, forced-supported, forced-unsupported, grow-to-max, already-large-enough, missing-root-resource, resize failure, and command register restoration after resize attempts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pci_rebar.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pci_rebar.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pci_rebar.h

## Purpose

`xe_pci_rebar.h` exposes the single ReBAR resize hook used by PCI probe.

## Important APIs

`xe_pci_rebar_resize(struct xe_device *xe)` attempts to resize the local-memory BAR based on the `force_vram_bar_size` module parameter or the maximum supported ReBAR size. The header forward-declares `struct xe_device` and has no inline behavior.

## Control Flow and State

The header itself is stateless. Calling the function can change PCI BAR resource sizing and bus resource assignment.

## Dependencies and Integration Points

The only consumer in this subset is `xe_pci.c`, which calls it during probe after early descriptor setup.

## Risks and Test Signals

The contract is intentionally best-effort and non-fatal. Compile-time tests should ensure only PCI-facing code includes it, while runtime tests should verify that unsupported platforms continue probing with the original BAR size.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pci_rebar.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pci_sriov.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pci_sriov.c

## Purpose

`xe_pci_sriov.c` implements the Xe PCI SR-IOV configure callback for PF devices. It provisions or unprovisions virtual functions, keeps the PF awake while VFs exist, sizes VF local-memory BARs, links PF/VF devices for resume ordering, and toggles GuC engine-activity accounting for PF/VF functions.

## Important APIs and Functions

The public entry point is `xe_pci_sriov_configure(struct pci_dev *pdev, int num_vfs)`, installed in `struct pci_driver.sriov_configure`. `xe_pci_sriov_get_vf_pdev()` resolves a 1-based VF ID to a referenced VF `pci_dev`. Private helpers reset VFs, create device links, enable engine activity function stats, choose VF LMEM BAR size, arm/disarm the PF guard, and perform `pf_enable_vfs()`/`pf_disable_vfs()`.

## Control Flow and State

`xe_pci_sriov_configure()` validates PF mode, bounds, and existing VFs, then takes a scoped runtime PM reference. Enabling waits for PF readiness, arms a guard against conflicting VF enabling, takes a noresume PM reference that persists for the VF lifetime, provisions VFs, optionally sizes VF LMEM BAR for dGFX, calls `pci_enable_sriov()`, links devices for resume order, creates sysfs links, and enables per-function engine activity stats. Failure unprovisions and drops the PM reference. Disabling reverses stats, sysfs links, PCI SR-IOV, VF reset, provisioning, PM reference, and guard.

## Dependencies and Integration Points

It depends on Linux PCI IOV APIs, Xe SR-IOV PF provisioning/control/sysfs helpers, GuC engine activity, runtime PM guards, BAR constants, and Xe SR-IOV logging/assertion helpers. PCI probe/remove calls this path indirectly through the PCI driver and explicitly disables VFs during PF remove.

## Risks and Test Signals

The persistent runtime PM reference is critical: missing a put on disable or failure leaks a wakeref; missing a get lets the PF enter D3 while VFs exist. Device-link creation is best-effort, so resume-order bugs may appear only on systems with both PF and VF drivers bound. Tests should cover invalid VF counts, non-PF rejection, enabling while VFs already exist, provisioning failure unwinds, LMEM BAR sizing failure non-fatal logging, sysfs link creation/removal, engine stats toggling, PF remove disabling VFs, and `pci_dev_put()` ownership for VF lookups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pci_sriov.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pci_sriov.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pci_sriov.h

## Purpose

`xe_pci_sriov.h` declares the PCI SR-IOV integration hooks used by the Xe PCI driver and PF/VF helper code.

## Important APIs

When `CONFIG_PCI_IOV` is enabled, `xe_pci_sriov_configure()` enables or disables VFs for a PF and `xe_pci_sriov_get_vf_pdev()` returns a referenced VF `pci_dev` for a 1-based VF ID. Without PCI IOV, `xe_pci_sriov_configure()` is an inline no-op returning 0.

## Control Flow and State

The header is stateless, but the enabled implementation changes PCI SR-IOV state, PF provisioning state, runtime PM references, and PF/VF sysfs/device-link relationships.

## Dependencies and Integration Points

It forward-declares `struct pci_dev` and is consumed by `xe_pci.c` and SR-IOV PF logic.

## Risks and Test Signals

The `CONFIG_PCI_IOV` fallback means callers must tolerate no-op configuration on kernels without IOV support. Compile coverage should include both enabled and disabled builds. Runtime tests should validate VF pdev reference ownership and correct error propagation from `sriov_configure`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pci_sriov.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pci_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pci_types.h

## Purpose

`xe_pci_types.h` defines the descriptor structures that translate PCI IDs and graphics/media IP versions into Xe runtime capability flags.

## Important APIs and Types

`struct xe_subplatform_desc` maps subplatform enum values to names and PCI ID lists. `struct xe_device_desc` is the platform-level descriptor used from the PCI ID table: it contains pre-GMD graphics/media IP pointers, platform/subplatform names, DMA/VA/VM sizing, tile/GT limits, VRAM flags, force-probe and dGFX flags, and feature bits such as display, SR-IOV, flat CCS, PXP, GSC, HECI, I2C, pcode/mtcfg skips, page reclaim assist, and shared VF workqueue needs. `struct xe_graphics_desc`, `struct xe_media_desc`, and `struct xe_ip` describe IP-version-specific engines and features.

## Control Flow and State

The structures are immutable descriptor inputs to PCI probe. `xe_pci.c` copies selected fields into `xe->info`, uses subplatform lists to refine platform identity, and uses IP descriptors to allocate GTs and set engine masks.

## Dependencies and Integration Points

It includes `xe_platform_types.h` for platform enums and Linux types. The definitions are central to PCI probing, GT allocation, display gating, VM/page-table sizing, SR-IOV feature exposure, PM policy, and workarounds.

## Risks and Test Signals

Bitfield packing keeps descriptors compact but makes initialization omissions easy. Feature bits must reflect hardware and firmware expectations exactly. Test signals include descriptor snapshot tests, KUnit coverage for IP lookup, compile checks when adding new feature bits, and boot probes on each platform family validating `xe->info` fields and engine masks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pci_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pcode.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pcode.c

## Purpose

`xe_pcode.c` centralizes communication with PCODE firmware through MMIO mailbox registers. It provides serialized read/write/request helpers, PCODE readiness polling for dGFX, and initialization of the minimum GT frequency QOS table.

## Important APIs and Functions

The public API includes `xe_pcode_init()`, `xe_pcode_probe_early()`, `xe_pcode_ready()`, `xe_pcode_read()`, `xe_pcode_write_timeout()`, `xe_pcode_write64_timeout()`, `xe_pcode_write()`, `xe_pcode_request()`, and `xe_pcode_init_min_freq_table()`. `pcode_mailbox_status()` translates PCODE error codes into Linux errno values. `__pcode_mailbox_rw()` performs the raw mailbox transaction, while `pcode_mailbox_rw()` asserts `tile->pcode.lock`. `pcode_try_request()` repeatedly sends a request and checks masked replies.

## Control Flow and State

Each mailbox transaction checks `skip_pcode`, verifies the mailbox is not already ready/busy, writes DATA0/DATA1, writes `PCODE_READY | mbox`, waits for the ready bit to clear, optionally reads reply data, then decodes status. Public read/write APIs take `tile->pcode.lock`. `xe_pcode_request()` starts with sleepable retry, then logs and retries for 50 ms with preemption disabled if the short timeout path did not acknowledge. `xe_pcode_ready()` polls root tile PCODE init status for up to three minutes on dGFX. Persistent state is the per-tile mutex and PCODE firmware/hardware state behind the mailbox.

## Dependencies and Integration Points

It depends on `xe_mmio_wait32()`, PCODE register definitions, device/platform flags, DRM managed mutex init, delay primitives, and error injection. PCI early probe and PM resume call readiness checks; GT frequency management and power/thermal features consume mailbox helpers and constants.

## Risks and Test Signals

Timeouts and firmware status mapping are failure-critical. `xe_pcode_request()` returns `status ? status : ret`, where `status` is an errno-like value filled by mailbox attempts, so callers must handle PCODE-specific negative errors. Atomic retry disables preemption and must remain bounded. Tests should cover busy mailbox `-EAGAIN`, skip-pcode no-op behavior, all decoded PCODE error codes, read/write64 data ordering, request timeout fallback, max/min frequency table bounds, three-minute readiness timeout, and error injection during PCI probe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pcode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pcode.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pcode.h

## Purpose

`xe_pcode.h` is the public PCODE firmware mailbox interface for Xe components.

## Important APIs

The header declares initialization and readiness functions, synchronous mailbox read/write helpers, 64-bit write support, a retrying request helper, and `xe_pcode_init_min_freq_table()`. The `xe_pcode_write()` macro is a one millisecond timeout wrapper. `PCODE_MBOX(mbcmd, param1, param2)` builds mailbox command words using `PCODE_MB_COMMAND`, `PCODE_MB_PARAM1`, and `PCODE_MB_PARAM2` fields from `xe_pcode_api.h`.

## Control Flow and State

Callers initialize the per-tile PCODE mutex with `xe_pcode_init()`, wait for firmware readiness during early probe or resume, then issue serialized mailbox commands through the helpers. State resides in hardware PCODE registers and the per-tile lock.

## Dependencies and Integration Points

It relies on PCODE bit definitions from `xe_pcode_api.h` being visible to macro users and is consumed by PM, GT frequency/power, thermal, fan, and late-binding firmware code.

## Risks and Test Signals

Mailbox helper timeouts are caller-selected, so users must choose realistic values. Compile tests should verify macro field definitions are available. Integration tests should verify callers hold no conflicting locks that can deadlock while waiting for PCODE.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pcode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pcode_api.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pcode_api.h

## Purpose

`xe_pcode_api.h` is the internal register and command definition map for PCODE firmware mailboxes, power setup, thermal info, late binding, frequency config, fan control, scratch breadcrumbs, and PCIe capability reporting.

## Important Definitions

The header defines `PCODE_MAILBOX`, `PCODE_DATA0`, `PCODE_DATA1`, mailbox ready and field masks, status/error codes, min-frequency table commands, dGFX init status commands, power-limit commands and fixed-point fields, thermal info subcommands, late-binding capability/version fields, frequency config command/subdomain fields, fan count read command, scratch register layout, boot failure states, auxiliary info fields, and `BMG_PCIE_CAP` link downgrade bits.

## Control Flow and State

This header has no executable control flow. It encodes the ABI used by `xe_pcode.c` and higher-level feature modules to construct PCODE mailbox commands and decode replies. The persistent state represented by these constants is in PCODE firmware and MMIO registers.

## Dependencies and Integration Points

It includes `regs/xe_reg_defs.h` for `XE_REG`, `REG_BIT`, and field-mask helpers. It is marked internal to `xe_pcode` but is included by the public header for the `PCODE_MBOX()` macro and by feature code that needs command constants.

## Risks and Test Signals

Incorrect bitfields directly corrupt firmware commands or reply decoding. Test signals include mailbox command construction tests, power/thermal/frequency feature validation against known firmware replies, and compile-time checks when new PCODE commands are added.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pcode_api.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_platform_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_platform_types.h

## Purpose

`xe_platform_types.h` defines the canonical Xe platform and subplatform enums used throughout the driver.

## Important APIs and Types

`enum xe_platform` names platform families in graphics-version and chronological order, starting at `XE_PLATFORM_UNINITIALIZED` and covering Tigerlake, Rocketlake, Alder/Raptor Lake variants, DG1/DG2/PVC, Meteor/Lunar/Battlemage/Pantherlake, Novalake, Crescent Island, and Novalake-P. `enum xe_subplatform` identifies finer PCI-ID-derived variants such as RPLU, RPLS, DG2 G10/G11/G12, and BMG G21.

## Control Flow and State

The header has no runtime logic. PCI probe fills `xe->info.platform` and `xe->info.subplatform`; later code uses those enum values for workarounds, PAT tables, PM policy, display behavior, and feature gating.

## Dependencies and Integration Points

It is included by PCI descriptor types and many platform-checking helpers. The enum order is documented as intentional and should be maintained for readability and stable platform classification.

## Risks and Test Signals

Adding or reordering platforms can break switch statements, platform macros, descriptor tables, and tests that assume chronological order. Test signals include build coverage for exhaustive platform switches, PCI descriptor mapping for each enum, and feature/workaround selection for new platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_platform_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pm.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pm.c

## Purpose

`xe_pm.c` implements Xe system suspend/resume, runtime suspend/resume, D3cold policy, PM notifiers, runtime PM reference helpers, and lockdep annotations that keep GPU memory management, display, GT, PXP, IRQ, I2C, and firmware flows ordered around power transitions.

## Important APIs and Functions

Public functions include `xe_pm_suspend()`, `xe_pm_resume()`, `xe_pm_init_early()`, `xe_pm_init()`, `xe_pm_fini()`, `xe_pm_runtime_suspend()`, `xe_pm_runtime_resume()`, runtime PM get/put variants, `xe_pm_set_vram_threshold()`, `xe_pm_d3cold_allowed_toggle()`, `xe_pm_block_on_suspend()`, `xe_pm_might_block_on_suspend()`, `xe_rpm_reclaim_safe()`, `xe_pm_assert_unbounded_bridge()`, and `xe_pm_module_init()`. Private helpers handle D3cold capability, runtime PM init/fini, notifier eviction, rebind worker wakeup, callback-task tracking, and lockdep map priming.

## Control Flow and State

System suspend blocks new suspend-sensitive work, suspends PXP, waits late binding, prepares GTs, suspends display, evicts BOs, suspends GTs, IRQ, display late, and I2C. Resume disables GT C6, applies tile workarounds, waits PCODE, restores display early and pinned BOs, resumes I2C/IRQ/GT/display, restores late BOs, resumes PXP, re-registers VF CCS, and reloads late-bind firmware. Runtime suspend marks the callback task, applies lockdep annotations, suspends PXP/display, releases VRAM userfault mmap offsets, evicts BOs only if D3cold is allowed, suspends GTs or runtime-suspends GTs, and suspends IRQ/display-late/I2C. Runtime resume mirrors that path and conditionally restores BOs/firmware only for D3cold. D3cold allowed is recomputed from VRAM usage versus a threshold under `xe->d3cold.lock`.

## Dependencies and Integration Points

This file coordinates PCI PM callbacks, TTM BO eviction/restoration, display PM, GT idle/suspend, IRQ, I2C, PCODE, PXP, late binding firmware, SR-IOV VF CCS, workarounds, runtime PM, Linux suspend notifiers, DMI quirks, and lockdep/reclaim annotations.

## Risks and Test Signals

Ordering bugs can leave hardware inaccessible, display blank, BOs lost, or runtime PM deadlocked. D3cold depends on root-port PME/_PR3, platform quirks, VRAM thresholds, and runtime idle timing. The PM notifier intentionally holds a runtime PM reference across suspend preparation and completion. Tests should cover system suspend/resume success and failure unwinds, D3hot versus D3cold runtime paths, VRAM threshold validation, BMG NUC13RNG threshold quirk, notifier eviction and rebind wakeup, callback-task recursion avoidance, missing outer runtime PM warning, lockdep prime paths, VF RPM disabled behavior, and PM teardown after partial init.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pm.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pm.h

## Purpose

`xe_pm.h` declares the Xe power-management interface and scope-guard helpers used by callers that need device wake references.

## Important APIs

The header exports system PM, runtime PM, initialization/finalization, D3cold threshold/toggle, reclaim-safety, callback-task, suspend-blocking, and module-init functions. `DEFAULT_VRAM_THRESHOLD` is 300 MiB. Scope helpers are defined with `DEFINE_GUARD`: `xe_pm_runtime`, `xe_pm_runtime_noresume`, conditional `xe_pm_runtime_ioctl`, and `xe_pm_runtime_release_only`.

## Control Flow and State

The declarations represent functions implemented in `xe_pm.c`. The guard macros automatically pair get/put calls across C scopes and are used by IOCTLs, sysfs/debugfs paths, SR-IOV code, and other outer-level call sites.

## Dependencies and Integration Points

It includes Linux cleanup and runtime PM headers. It is a broad driver contract for safe register and memory access while runtime PM can suspend the device.

## Risks and Test Signals

Incorrect use of noresume or release-only guards can leak or drop wakerefs incorrectly. Test signals include sparse/compile coverage for guard use, runtime PM balance checks, and lockdep coverage for callers that might resume under memory-management locks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pmu.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pmu.c

## Purpose

`xe_pmu.c` registers a perf PMU for Xe devices and exposes GT residency/frequency plus engine activity counters through sysfs and perf events.

## Important APIs and Functions

The public API is `xe_pmu_register(struct xe_pmu *pmu)`, with cleanup through a devm action. Event config fields encode GT, SR-IOV function, engine class, engine instance, and event ID. Event IDs cover GT C6 residency, engine active ticks, engine total ticks, GT actual frequency, and GT requested frequency. The perf callbacks are `xe_pmu_event_init()`, add/del/start/stop/read helpers, and `xe_pmu_event_destroy()`. Helpers validate params, resolve GTs and hardware engines, acquire/release forcewake where needed, and read GuC PC or GuC engine-activity counters.

## Control Flow and State

Registration skips SR-IOV VFs, creates a PMU name from the DRM device name, installs format/events attribute groups, computes supported event bits, registers with perf, and marks `pmu->registered`. Event init rejects unsupported sampling/modes, invalid CPUs, unknown event IDs, bad GT/engine/function parameters, branch stacks, or unsupported events. Parentless events hold a DRM device reference, a runtime PM reference, and sometimes a forcewake reference stored in `event->pmu_private`. Reads update `hw.prev_count` and `event->count`; frequency events add instantaneous values rather than deltas.

## Dependencies and Integration Points

It integrates Linux perf PMU APIs, sysfs attributes, DRM device lifetime, runtime PM, forcewake, GT idle residency, GuC PC frequency, GuC engine activity, hardware engine lookup, and SR-IOV PF total-VF accounting.

## Risks and Test Signals

Forcewake allocation and release must balance across event lifetime. Frequency events are not monotonic counters and intentionally use different accumulation semantics. Event visibility currently checks support against GT 0, so multi-GT support must stay consistent. Tests should cover sysfs format/event files, invalid config rejection, reserved engine rejection, SR-IOV PF function bounds, VF no-registration path, runtime PM/DRM refs on event init/destroy, forcewake failure cleanup, event stop with update, unregister while events exist, and perf stat readings for all supported counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pmu.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pmu.h

## Purpose

`xe_pmu.h` declares the Xe perf PMU registration interface.

## Important APIs

When `CONFIG_PERF_EVENTS` is enabled, `xe_pmu_register(struct xe_pmu *pmu)` registers the device PMU. Otherwise an inline stub returns 0, allowing the rest of the driver to compile without perf support.

## Control Flow and State

The header has no runtime state. The implementation fills `struct xe_pmu` and registers/unregisters with perf core.

## Dependencies and Integration Points

It includes `xe_pmu_types.h` and is consumed by device initialization.

## Risks and Test Signals

The stub means feature code must not assume PMU sysfs exists when perf is disabled. Build tests should cover both perf-enabled and perf-disabled configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pmu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pmu_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pmu_types.h

## Purpose

`xe_pmu_types.h` defines the per-device state used by Xe's perf PMU integration.

## Important APIs and Types

`XE_PMU_MAX_GT` is fixed at 2 and checked against `XE_MAX_GT_PER_TILE` in the implementation. `struct xe_pmu` embeds `struct pmu base`, a `registered` flag, registered PMU `name`, and a `supported_events` bitmap indexed by event ID.

## Control Flow and State

The structure is stored in `struct xe_device`. `registered` gates event init/read behavior and avoids double unregister. `supported_events` controls sysfs visibility and event validation.

## Dependencies and Integration Points

It includes Linux perf and spinlock type headers. It is used by `xe_pmu.c` and device lifetime code.

## Risks and Test Signals

The GT maximum must match driver topology assumptions. Tests should verify event bit population on devices with and without GuC PC or engine activity support and confirm unregister clears `registered` before perf teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pmu_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_preempt_fence.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_preempt_fence.c

## Purpose

`xe_preempt_fence.c` implements a Xe-specific `dma_fence` used to preempt or suspend an execution queue and signal once the queue is quiesced enough for VM rebinding.

## Important APIs and Functions

Public helpers are `xe_preempt_fence_alloc()`, `xe_preempt_fence_free()`, `xe_preempt_fence_arm()`, `xe_preempt_fence_create()`, and `xe_fence_is_xe_preempt()`. The fence ops provide driver/timeline names and `preempt_fence_enable_signaling()`. `preempt_fence_work_func()` performs asynchronous completion on the driver's ordered preempt fence workqueue.

## Control Flow and State

Allocation initializes the list link and work item. Unarmed fences can live on lists using the embedded link and must be freed with `xe_preempt_fence_free()`. Arming removes the link, stores a referenced exec queue, initializes the fence lock and `dma_fence`, and returns the embedded fence. Enabling signaling calls `q->ops->suspend(q)`, stores any immediate error, and queues work. The worker either sets the stored error, waits for suspend completion, retries on `-EAGAIN`, marks reset queues as `-ENOENT`, signals the fence, queues VM rebind work, and drops the exec queue reference.

## Dependencies and Integration Points

It depends on `dma_fence`, workqueues, exec queue operations, GuC exec queue IDs for debugging, GT logging, and VM rebind scheduling. It is part of the VM preempt-fence mode and rebind worker pipeline.

## Risks and Test Signals

The ordered global workqueue means blocking work in the callback can block all preempt fences; the code uses `dma_fence_begin_signalling()` to make lockdep catch unsafe locks. Retry loops rely on `suspend_wait()` eventually stopping returning `-EAGAIN`. Tests should cover allocation failure, unarmed free, arm lifetime, suspend success, immediate suspend error, reset-status error, retry behavior, queue reference release, VM rebind enqueue, and `xe_fence_is_xe_preempt()` distinguishing fence ops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_preempt_fence.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_preempt_fence.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_preempt_fence.h

## Purpose

`xe_preempt_fence.h` declares the preempt-fence lifecycle and list-link helpers used by VM and exec queue code.

## Important APIs

`xe_preempt_fence_create()` allocates and arms a fence in one step. `xe_preempt_fence_alloc()` creates an unarmed fence, `xe_preempt_fence_free()` frees an unarmed fence, and `xe_preempt_fence_arm()` binds it to an exec queue, context, and seqno. Inline helpers convert between `dma_fence`, `xe_preempt_fence`, and the embedded list link. `xe_fence_is_xe_preempt()` identifies this fence class.

## Control Flow and State

The header defines the intended split between unarmed fences stored on lists and armed fences owned through `dma_fence_put()`. It does not own runtime state beyond accessors to `struct xe_preempt_fence`.

## Dependencies and Integration Points

It includes `xe_preempt_fence_types.h` and is used by scheduler/VM code that tracks pending preemptions before arming.

## Risks and Test Signals

Misusing free paths can double-free or leak fences. Tests should cover link conversion, unarmed list handling, and transition to armed DMA fence ownership.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_preempt_fence.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_preempt_fence_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_preempt_fence_types.h

## Purpose

`xe_preempt_fence_types.h` defines the concrete preempt-fence object.

## Important Types

`struct xe_preempt_fence` embeds `struct dma_fence base`, a list `link` for unarmed tracking, a referenced `struct xe_exec_queue *q`, the `preempt_work` item that performs suspend/wait/signaling, a spinlock used by `dma_fence_init()`, and an `error` field set by suspend paths.

## Control Flow and State

Before arming, only the link and work item are initialized. After arming, the object participates in DMA fence signaling and owns an exec queue reference until the worker signals and puts it. The `error` field is persisted between enable-signaling and work execution.

## Dependencies and Integration Points

It includes Linux DMA fence and workqueue headers and forward-declares `struct xe_exec_queue`.

## Risks and Test Signals

Because the type embeds both list and fence lifetime state, callers must not treat an armed fence as an ordinary list node. Test signals include lockdep validation of fence signaling and object lifetime checks under retry/error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_preempt_fence_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_printk.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_printk.h

## Purpose

`xe_printk.h` wraps DRM logging and warning helpers for Xe device-scoped messages and provides `drm_printer` constructors that route printer output to Xe logging levels.

## Important APIs and Macros

Macros include `xe_printk()`, `xe_err()`, `xe_err_once()`, `xe_err_ratelimited()`, `xe_warn()`, `xe_notice()`, `xe_info()`, `xe_dbg()`, `xe_WARN()`, `xe_WARN_ONCE()`, `xe_WARN_ON()`, and `xe_WARN_ON_ONCE()`. Inline printer callbacks implement `xe_err_printer()`, `xe_info_printer()`, and `xe_dbg_printer()`. The debug printer redirects through `drm_dbg_printer()` with preserved origin to improve debug callsite annotation.

## Control Flow and State

The macros pass through to DRM logging using `xe->drm`. The printer helpers create stack-returned `struct drm_printer` values with `arg = xe`; no persistent state is allocated.

## Dependencies and Integration Points

It depends on DRM print helpers and `xe_device_types.h`. It is used broadly by PCI, ReBAR, SR-IOV, debug dump, and diagnostics code.

## Risks and Test Signals

Logging macros assume a valid `struct xe_device *` and initialized DRM device. Format handling goes through variadic macros, so compile-time format checking is important. Test signals include builds with warnings enabled, debug printer output preserving origin, and warning macros producing expected DRM_WARN behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_printk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_psmi.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_psmi.c

## Purpose

`xe_psmi.c` provides debugfs support for PSMI capture buffers. It allocates physically contiguous pinned VRAM GEM objects for selected memory regions and exposes their physical addresses and size to a userspace PSMI tool, while leaving register programming to userspace.

## Important APIs and Functions

Public functions are `xe_psmi_init()` and `xe_psmi_debugfs_register()`. Private helpers check configfs enablement, allocate/free pinned BOs, clean up all selected capture objects, resize allocation based on debugfs writes, show capture addresses, get/set capture size, and get/set capture region mask. Debugfs files are `psmi_capture_addr`, `psmi_capture_region_mask`, and `psmi_capture_size`.

## Control Flow and State

PSMI is disabled unless configfs enables it. Init registers a devm cleanup action. Debugfs registration creates files under the primary DRM minor. Users first set `psmi_capture_region_mask` to non-system memory regions, then write `psmi_capture_size`, which frees existing buffers, allocates one pinned VRAM BO per selected region, and stores it in `xe->psmi.capture_obj[id]`. Address reads print `region: physical_address` using `__xe_bo_addr()`. Region mask changes are rejected once buffers exist. Size zero frees all current buffers.

## Dependencies and Integration Points

The file depends on debugfs, Xe BO creation/pinning/unpinning, configfs, DRM minor debugfs roots, device-managed cleanup, memory region masks, and dGFX VRAM placement flags.

## Risks and Test Signals

Debugfs setters do not take a dedicated PSMI mutex in this file, so concurrent writes need external serialization guarantees from debugfs usage or additional locking if expanded. Size is documented as power-of-two but not validated here. System memory is explicitly unsupported. Tests should cover disabled mode, debugfs file creation, invalid region masks, SMEM rejection, busy region-mask change, size zero cleanup, allocation failure rollback, multi-tile address reporting, and devm cleanup unpinning all BOs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_psmi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_psmi.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_psmi.h

## Purpose

`xe_psmi.h` declares the PSMI capture-buffer initialization and debugfs registration hooks.

## Important APIs

`xe_psmi_init(struct xe_device *xe)` registers cleanup when PSMI is enabled. `xe_psmi_debugfs_register(struct xe_device *xe)` creates the debugfs files used by the PSMI userspace tool.

## Control Flow and State

The header has no state. The implementation uses `xe->psmi` fields to store selected memory regions and capture BOs.

## Dependencies and Integration Points

It forward-declares `struct xe_device` and is used by device init/debugfs setup.

## Risks and Test Signals

Call ordering matters: debugfs registration should happen after the DRM minor debugfs root exists and init should register cleanup before buffers can be allocated. Tests should cover disabled configfs behavior and cleanup after debugfs-driven allocations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_psmi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pt.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pt.c

## Purpose

`xe_pt.c` implements Xe GPU page-table allocation, population, bind/unbind staging, CPU-side commit/abort, GPU migration updates, TLB invalidation scheduling, SVM/userptr validation, page reclaim list generation, and PTE zapping for eviction and invalidation.

## Important APIs, Types, and Functions

Public APIs are `xe_pt_create()`, `xe_pt_populate_empty()`, `xe_pt_shift()`, `xe_pt_destroy()`, `xe_pt_clear()`, `xe_pt_zap_ptes()`, `xe_pt_zap_ptes_range()`, `xe_pt_update_ops_prepare()`, `xe_pt_update_ops_run()`, `xe_pt_update_ops_fini()`, and `xe_pt_update_ops_abort()`. Internal structures include `struct xe_pt_dir` for directory page tables with child/staging arrays, `struct xe_pt_stage_bind_walk`, `struct xe_pt_stage_unbind_walk`, and `struct xe_pt_update`. Major helper groups cover shared-update staging, huge/64K/compact PTE selection, atomic-access PTE flags, SVM range DMA cursors, nonshared offset detection, PRL generation, dependency gathering, commit preparation, and operation-level bind/unbind/remap/prefetch handling.

## Control Flow and State

Page-table creation allocates metadata plus a pinned mapped 4 KiB page-table BO. Empty population writes scratch PDE/PTEs when the VM has scratch support or zeros otherwise. Bind preparation walks the target range, allocates disconnected subtrees when needed, writes private subtree entries immediately, and records shared page-table updates in `xe_vm_pgtable_update` arrays. It handles null/purged BOs, userptr DMA arrays, VRAM/stolen/SG resources, compact 64K L0 tables, PS64 hints, huge PTEs, device atomic flags, and scratch invalidation needs. Unbind preparation walks only shared tables, computes entries to clear, may kill private subtrees, updates `num_live`, and optionally builds page reclaim entries. Run creates migration/TLB jobs, inserts dependencies/range fences, performs GPU or CPU page-table updates, commits CPU child/staging state at the point of no return, adds fences to VM/BO reservations, updates VMA or SVM tile-present state, and returns the migration fence. Abort unwinds staged CPU state for operations not committed; fini frees staging arrays and deferred BO puts.

## Dependencies and Integration Points

This file integrates BO/TTM resource cursors, DRM GPUVA operations, VM locks/reservations, exec queues, migrate engine, TLB invalidation jobs, GuC page reclaim hardware assist, SVM notifier locks, userptr invalidation, scheduler jobs, range fence trees, GT stats, PAT indices, scratch page tables, trace/debug helpers, and memory placement flags.

## Risks and Test Signals

This is a high-risk state machine. Locking contracts differ for BO-backed VMAs, userptr, SVM ranges, and CPU address mirrors. The point-of-no-return in `xe_pt_update_ops_run()` kills the VM on some late failures for non-root tiles. `num_live`, child/staging pointers, range fences, and tile_present/tile_invalidated bits must remain consistent across prepare/run/fini/abort. Huge/64K/compact decisions depend on VA and DMA alignment; VRAM with `XE_VM_FLAG_64K` fails if 64K hints cannot be formed. Tests should cover bind/unbind/remap/prefetch for BO, userptr, null, purged, scratch and non-scratch VMs; SVM range retry paths; compact and normal 64K PTEs; huge PTE alignment; PRL overflow/abort; TLB invalidation creation for primary/media GT; dependency failures for CPU updates; injected prepare/run errors; and abort/fini leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pt.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pt.h

## Purpose

`xe_pt.h` declares the public page-table management API used by VM, migration, eviction, and SVM code.

## Important APIs

`MAX_HUGEPTE_LEVEL` currently allows huge PTEs up to level 2, or 1 GiB. `xe_pt_write()` writes a 64-bit page-table entry through `xe_map_wr()`. Creation/destruction helpers manage page-table metadata and BOs. Update operation functions prepare, run, finish, or abort staged VMA operations. `xe_pt_zap_ptes()` and `xe_pt_zap_ptes_range()` zero GPU mappings for VMA or SVM invalidation.

## Control Flow and State

The declared API follows a prepare/run/fini or prepare/abort pattern. Prepare mutates CPU-side staging state, run submits/commits GPU updates, fini releases temporary resources and deferred BO puts, and abort unwinds staged state after failures.

## Dependencies and Integration Points

The header includes `xe_pt_types.h` and forward-declares DMA fence, DRM exec, BO, device, exec queue, SVM range, sync entry, tile, VM, VMA, and VMA ops types. It is central to VM bind paths.

## Risks and Test Signals

Callers must hold the locks required by the implementation and must pair prepare with run/fini or abort. Test signals include lockdep coverage, fence lifetime checks, and no leaks after error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pt_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pt_types.h

## Purpose

`xe_pt_types.h` defines page-table-related cache levels, page-table metadata, encoding operations, and staged update data structures shared between VM and page-table implementation code.

## Important APIs and Types

`enum xe_cache_level` names cache choices including uncached, write-through, write-back, and compression variants. `XE_VM_MAX_LEVEL` is 4. `struct xe_pt` embeds generic walker state, the backing BO, level, live-entry count, rebind and compact flags, and optional debug VA. `struct xe_pt_ops` abstracts PTE/PDE encoding for BOs, VMAs, raw addresses, and page-table BOs. `struct xe_vm_pgtable_update` describes one page-table BO update. `struct xe_vm_pgtable_update_op` groups updates for one VMA operation. `struct xe_vm_pgtable_update_ops` tracks a batch across operations, deferred destruction, update queue, page reclaim list, affected range, current op, and dependency/invalidation flags.

## Control Flow and State

These structures carry the persistent VM page-table tree and the temporary staging state used during bind/unbind. `children` represents committed CPU tree state, while `staging` represents prepared but not fully committed changes.

## Dependencies and Integration Points

It includes page reclaim and page-table walker definitions and is consumed by `xe_pt.c`, VM code, migration, and architecture-specific PTE encoding.

## Risks and Test Signals

The update arrays are sized around `XE_VM_MAX_LEVEL * 2 + 1`; changes to VM levels require auditing staging limits. Tests should verify cache-level-to-PAT mappings, compact flag behavior, deferred destruction, and batch state reset between operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pt_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pt_walk.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pt_walk.c

## Purpose

`xe_pt_walk.c` provides a generic GPU page-table tree walker similar to Linux CPU pagewalk helpers, but parameterized by numeric page-table levels and driver-supplied shift arrays.

## Important APIs and Functions

The public functions are `xe_pt_walk_range()` and `xe_pt_walk_shared()`. Private helpers are `xe_pt_addr_end()`, which computes the next boundary for a level, and `xe_pt_next()`, which advances offsets and optionally skips private regions during shared walks. Walk behavior is controlled by `struct xe_pt_walk_ops` callbacks from `xe_pt_walk.h`.

## Control Flow and State

`xe_pt_walk_range()` computes the starting offset, selects committed or staging entries, then iterates entries from `addr` to `end`. For each entry it calls `pt_entry`, honors `ACTION_AGAIN`, `ACTION_CONTINUE`, and `ACTION_SUBTREE`, recursively descends to children, and calls `pt_post_descend` after returning. `xe_pt_walk_shared()` enables `shared_pt_mode`, first calls the callback for the root as a synthetic shared entry, then walks the range while skipping private page tables fully covered by the range.

## Dependencies and Integration Points

It depends on the generic walker types and inline helpers in `xe_pt_walk.h`. `xe_pt.c` uses it for bind staging, unbind staging, and PTE zapping.

## Risks and Test Signals

The walker trusts callback mutation of child pointers and action values. Shared mode skipping must match unbind/zap assumptions or entries can be missed. Tests should cover full and partial range walks, root callback behavior in shared mode, staging versus committed arrays, post-descend callbacks, ACTION_AGAIN retry, and shift-array changes during compact page-table decisions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pt_walk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pt_walk.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pt_walk.h

## Purpose

`xe_pt_walk.h` defines the generic page-table walker interface used by Xe GPU page-table code.

## Important APIs and Types

`struct xe_ptw` is the embeddable base for page-table nodes with optional `children` and `staging` arrays. `struct xe_pt_walk` stores callback ops, level shift array, max level, shared-walk mode, and whether to walk staging state. `xe_pt_entry_fn` is the callback signature, receiving parent, offset, level, address range, child pointer, action, and walk state. `struct xe_pt_walk_ops` provides `pt_entry` and optional `pt_post_descend`. Inline helpers `xe_pt_covers()`, `xe_pt_num_entries()`, and `xe_pt_offset()` compute coverage, entry counts, and offsets.

## Control Flow and State

The header has inline math only. Runtime traversal is implemented in `xe_pt_walk.c`. The `shifts` pointer may be changed during a walk, which lets bind code switch between normal 4K and compact 64K leaf layouts.

## Dependencies and Integration Points

It includes Linux `pagewalk.h` for `enum page_walk_action` and is used by `xe_pt_types.h` and `xe_pt.c`.

## Risks and Test Signals

Shift arrays, alignment math, and max-level selection define the walk shape. Off-by-one errors here affect all bind/unbind/zap paths. Tests should validate offset/count calculations at every level, partial edges, max-level masking, and compact shift changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pt_walk.h -->
