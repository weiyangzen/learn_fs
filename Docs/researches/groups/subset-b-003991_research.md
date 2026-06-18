# subset-b-003991 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/amd/iommu.c -->
# sources/distributed-fs/ceph-client/drivers/iommu/amd/iommu.c

Purpose: this is the main AMD-Vi IOMMU runtime driver. It registers `amd_iommu_ops`, manages device-table entries, AMD v1/v2 page-table domains, SVA/PASID GCR3 state, event/PPR/GA log interrupts, reserved regions, and x86 IRQ remapping support.

Important APIs, types, and functions: exported and cross-file entry points include `amd_iommu_ops`, `amd_iommu_update_dte()`, `amd_iommu_domain_flush_pages()`, `amd_iommu_dev_flush_pasid_pages()`, `amd_iommu_complete_ppr()`, `amd_iommu_pdom_id_*()`, `amd_iommu_set_gcr3()`, `amd_iommu_clear_gcr3()`, `amd_iommu_set_dte_v1()`, `protection_domain_alloc()`, `amd_iommu_domain_free()`, guest-IR exports `amd_iommu_update_ga()`, `amd_iommu_activate_guest_mode()`, and `amd_iommu_deactivate_guest_mode()`. Core state is carried by `struct amd_iommu`, `struct iommu_dev_data`, `struct protection_domain`, `struct gcr3_tbl_info`, `struct pdom_iommu_info`, and IRQ remapping tables.

Control flow: device probing validates PCI or ACPI-HID mappings, allocates or reuses `iommu_dev_data`, clones aliases, installs MSI domains when IRQ remapping is enabled, and records PASID/IRQ capacity. Attaching a domain first detaches any old domain, references the target IOMMU in the protection domain xarray, optionally allocates a GCR3 table, enables PCI ATS/PASID/PRI and IOPF, links the device to the domain list, and updates the DTE. Detach reverses this order: flush IOPF, disable PCI capabilities, clear the DTE, flush the domain, unlink state, destroy GCR3, and drop the IOMMU reference.

State and persistence: DTEs are hardware-persistent MMIO-visible tables protected by per-device `dte_lock`; command rings use `cmd_buf_tail`, `cmd_sem_val`, and completion-wait stores; domains keep `dev_list`, `iommu_array`, and `viommu_list`; PASID-capable devices have per-device GCR3 tables and per-device domain IDs. Domain IDs are allocated from global `pdom_ids`. Runtime state survives device release intentionally because unplug/replug races are avoided by retaining `dev_data`.

Dependencies and integration points: integrates with generic IOMMU domain ops, generic page-table library (`GENERIC_PT_IOMMU`), PCI ATS/PRI/PASID APIs, ACPI IVRS-derived maps, x86 IRQ domains/MSI parent support, IOPF/PPR code in `ppr.c`, SVA code in `pasid.c`, nested/iommufd hooks in `iommufd.c` and `nested.c`, SNP/RMP fault reporting, and architecture APIC/vector code.

Risks: DTE programming is order-sensitive because hardware reads 256-bit entries while the driver writes two 128-bit halves; wrong ordering can expose partially valid translations. Flush correctness spans IOMMU TLBs, device IOTLBs, DTE aliases, nested hDomIDs, and completion waits. SVA detach must not leave stale GCR3/PASID translations. IRQ remapping has separate 32-bit and 128-bit guest-IR formats, and affinity/vCPU updates intentionally avoid invalidations for fields the spec says are not cached.

Test signals: direct coverage is mostly integration and architecture boot testing. Strong signals include DMA API/IOMMU attach/detach stress, VFIO/iommufd domains with v1/v2 page tables, PASID/SVA with IOPF responses, SNP fault paths, kdump/preboot remap scenarios, PCI ATS/PRI toggling, and IRQ remapping with MSI/MSI-X, IOAPIC, HPET, and KVM posted-interrupt guest mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/amd/iommu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/amd/iommufd.c -->
# sources/distributed-fs/ceph-client/drivers/iommu/amd/iommufd.c

Purpose: AMD-specific iommufd glue. It reports AMD hardware capability data to userspace and initializes per-vIOMMU state used by nested translation.

Important APIs, types, and functions: `amd_iommufd_hw_info()` allocates `struct iommu_hw_info_amd` and fills `efr`/`efr2`; `amd_iommufd_get_viommu_size()` returns the embedding size for `struct amd_iommu_viommu`; `amd_iommufd_viommu_init()` initializes the guest-domain xarray and links the vIOMMU to the parent `protection_domain`; `amd_iommufd_viommu_destroy()` removes that link and destroys the xarray. The local `amd_viommu_ops` currently only supplies `.destroy`.

Control flow: `amd_iommu_ops.hw_info`, `.get_viommu_size`, and `.viommu_init` call into this file. Init converts the parent `iommu_domain` to a `protection_domain`, stores it in the AMD vIOMMU wrapper, initializes `gdomid_array`, publishes ops, and adds the vIOMMU to the parent's `viommu_list` under the parent spinlock. Destroy performs the inverse.

State and persistence: the persistent runtime state is the `gdomid_array` that nested domains use to map guest domain IDs to host domain IDs, plus the list membership in the parent protection domain. The file does not store userspace data itself beyond these in-kernel objects.

Dependencies and integration points: depends on `iommufd_viommu`, UAPI `IOMMU_HW_INFO_TYPE_AMD`, AMD feature globals from init code, and nested allocation in `nested.c`, which relies on `viommu->ops.alloc_domain_nested` being provided elsewhere through AMD iommufd integration.

Risks: lifecycle ordering matters because nested domains may reference `gdomid_array`; destroying a vIOMMU while nested domains still exist would make those references invalid. Hardware-info reporting must stay ABI-compatible with UAPI sizes and feature-bit meanings.

Test signals: useful tests create/destroy AMD vIOMMUs through iommufd, read hardware info with default and AMD-specific types, reject unsupported types, and exercise nested domain allocation/free after vIOMMU init.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/amd/iommufd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/amd/iommufd.h -->
# sources/distributed-fs/ceph-client/drivers/iommu/amd/iommufd.h

Purpose: this header conditionally exposes AMD iommufd hooks to the main AMD IOMMU driver.

Important APIs, types, and functions: declares `amd_iommufd_hw_info()`, `amd_iommufd_get_viommu_size()`, and `amd_iommufd_viommu_init()` when `CONFIG_AMD_IOMMU_IOMMUFD` is enabled. When disabled, the same names are macros expanding to `NULL`, allowing `amd_iommu_ops` to be initialized without preprocessor branches.

Control flow: included by `amd/iommu.c` and `amd/iommufd.c`. The main ops table consumes these names directly; the IOMMU core sees absent callbacks as unsupported when the config is off.

State and persistence: no runtime state; it is purely a build-time interface boundary.

Dependencies and integration points: depends on the IOMMUFD config symbol and iommufd/IOMMU types visible through including translation units. It is the small compile-time bridge between generic AMD IOMMU support and optional iommufd nesting features.

Risks: the fallback macros must match callback pointer expectations exactly; changing callback signatures without this header would create either build failures or invalid ops-table initializers.

Test signals: build coverage with `CONFIG_AMD_IOMMU_IOMMUFD=y` and disabled is the key signal, plus runtime checking that iommufd callbacks are absent when disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/amd/iommufd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/amd/nested.c -->
# sources/distributed-fs/ceph-client/drivers/iommu/amd/nested.c

Purpose: implements AMD nested translation domains for iommufd/vIOMMU. It validates userspace-provided guest DTE data, allocates nested domains, maps guest domain IDs to host domain IDs, and programs physical DTEs combining host stage-2 and guest state.

Important APIs, types, and functions: `amd_iommu_alloc_domain_nested()` is the allocation callback for `iommufd_viommu_ops`; `validate_gdte_nested()` enforces legal guest DTE fields; `gdom_info_load_or_alloc_locked()` manages xarray entries; `set_dte_nested()` synthesizes the hardware DTE; `nested_attach_device()` installs it; `nested_domain_free()` decrements mapping refs and frees hDomIDs. Key state includes `struct nested_domain`, `struct amd_iommu_viommu`, and `struct guest_domain_mapping_info`.

Control flow: allocation copies `IOMMU_HWPT_DATA_AMD_GUEST` from userspace, validates mode/GCR3/GPT/GLX constraints, extracts guest DomID, and looks up or allocates a `guest_domain_mapping_info` under `gdomid_array`. Existing mappings increment a refcount; new mappings allocate an AMD protection-domain ID as hDomID. Attach rejects PASID-enabled devices, builds a nested DTE from the parent v1 page table plus guest GCR3/GPT fields, and calls `amd_iommu_update_dte()`.

State and persistence: the gDomID-to-hDomID map persists in the vIOMMU xarray and is refcounted across nested domains. hDomIDs are allocated from the same global IDA as protection domains. The nested domain stores the copied guest DTE, chosen gDomID, pointer to mapping info, and parent vIOMMU pointer.

Dependencies and integration points: depends on AMD DTE bit definitions, `pt_iommu_amdv1_hw_info()`, `amd_iommu_set_dte_v1()`, `amd_iommu_make_clear_dte()`, `amd_iommu_update_dte()`, iommufd UAPI copy helpers, and the parent-domain/vIOMMU state initialized in `iommufd.c`.

Risks: incorrect gDomID-to-hDomID reuse can cause TLB tag aliasing across nested devices. Validation must reject reserved DTE encodings and unsupported 5-level guest tables. Free paths must erase xarray entries only after the final reference and must always free the hDomID. Nested attach bypasses normal domain device-list ownership, so it relies on group locking and DTE update serialization.

Test signals: iommufd nested-domain allocation with duplicate and unique guest DomIDs, invalid DTE field fuzzing, 4-level versus 5-level capability checks, attach to devices with PASID disabled/enabled, and parent-domain flushes that must also invalidate every mapped hDomID.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/amd/nested.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/amd/pasid.c -->
# sources/distributed-fs/ceph-client/drivers/iommu/amd/pasid.c

Purpose: implements AMD SVA PASID binding. It binds process page tables into a device GCR3 table, handles mmu-notifier invalidations, and removes PASID mappings when the mm exits or the IOMMU core detaches a PASID.

Important APIs, types, and functions: `iommu_sva_set_dev_pasid()` is the domain op for binding a PASID; `amd_iommu_remove_dev_pasid()` clears a binding; `amd_iommu_domain_alloc_sva()` allocates SVA domains; `iommu_sva_domain_free()` unregisters the notifier; notifier callbacks are `sva_arch_invalidate_secondary_tlbs()` and `sva_mn_release()`. Binding records use `struct pdom_dev_data`.

Control flow: allocation creates a `protection_domain`, marks it SVA, installs `sva_mn`, and registers with the target `mm_struct`. Binding rejects replacement (`old`), PASID zero/out-of-range, and devices without enabled PASID/GCR3 state, then writes `domain->mm->pgd` into the device GCR3 table with `amd_iommu_set_gcr3()` and links a binding record. Invalidation iterates records and flushes each PASID range. mm release removes every binding and clears device GCR3 entries.

State and persistence: the SVA domain owns an mmu notifier and a `dev_data_list` of PASID/device bindings. Device GCR3 tables are persistent until explicit clear or mm release. `pasid_cnt` in `gcr3_info` tracks installed PASIDs.

Dependencies and integration points: depends on `amd_iommu_set_gcr3()`, `amd_iommu_clear_gcr3()`, `amd_iommu_dev_flush_pasid_pages()`, generic `IOMMU_DOMAIN_SVA` operations, mmu notifier infrastructure, and GCR3 allocation done during device attach in `iommu.c`.

Risks: PASID zero is reserved for non-PASID traffic and must stay rejected. The code assumes binding removal runs under the protection-domain lock. `domain->mm` must be valid for the SVA domain; failures in notifier registration or GCR3 updates must not leave partial list entries.

Test signals: bind/unbind SVA PASIDs, invalid PASID rejection, mm exit while DMA may still be active, range invalidation propagation to all bound devices, and detach through the blocked-domain PASID path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/amd/pasid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/amd/ppr.c -->
# sources/distributed-fs/ceph-client/drivers/iommu/amd/ppr.c

Purpose: handles AMD Page Request (PPR) logs and generic I/O page fault integration. It allocates/enables the PPR ring, polls entries from interrupts, converts valid hardware page requests into `iopf_fault` events, and sends page responses back as COMPLETE_PPR commands.

Important APIs, types, and functions: `amd_iommu_alloc_ppr_log()`, `amd_iommu_enable_ppr_log()`, `amd_iommu_restart_ppr_log()`, `amd_iommu_poll_ppr_log()`, `amd_iommu_iopf_init()`, `amd_iommu_iopf_uninit()`, `amd_iommu_iopf_add_device()`, `amd_iommu_iopf_remove_device()`, and `amd_iommu_page_response()`. Helpers include `ppr_flag_to_fault_perm()`, `ppr_is_valid()`, and `iommu_call_iopf_notifier()`.

Control flow: init allocates the ring and queue; enable writes the physical ring base/length and turns on PPR interrupts/logging. The interrupt thread in `iommu.c` calls `amd_iommu_poll_ppr_log()`, which waits for entry materialization, optionally clears erratum-sensitive entries, advances the head pointer, validates request type/flags/PASID, reports device faults to generic IOMMU, or immediately completes failed requests. Page responses call back into `amd_iommu_complete_ppr()`.

State and persistence: per-IOMMU state includes `ppr_log`, MMIO head/tail, `iopf_queue`, and a queue name. Per-device `dev_data->ppr` records whether the device was added to the IOPF queue. PPR log memory is hardware-owned while enabled.

Dependencies and integration points: integrates with AMD command completion in `iommu.c`, PCI device lookup, generic `iommu_report_device_fault()`, IOPF queues, PRI enablement in attach, SNP erratum behavior, and hardware PPR field macros.

Risks: invalid or malicious PPR entries must be failed to prevent hanging devices. PASID bounds are checked against `dev_data->max_pasids`. Ring overflow restart is separate from normal polling. If PRI is enabled but IOPF queue add fails, attach disables PRI to avoid unhandled page requests.

Test signals: page request fault injection, invalid PASID/format/GN-bit cases, IOPF queue add/remove around attach/detach, response status propagation, PPR overflow restart, and SNP versus non-SNP entry clearing behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/amd/ppr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/amd/quirks.c -->
# sources/distributed-fs/ceph-client/drivers/iommu/amd/quirks.c

Purpose: applies DMI-based AMD IVRS quirks for systems whose firmware reports incorrect IOAPIC device IDs.

Important APIs, types, and functions: `struct ivrs_quirk_entry` stores IOAPIC ID to device ID pairs; `ivrs_ioapic_quirk_cb()` calls `add_special_device()` for each pair; `amd_iommu_apply_ivrs_quirks()` runs `dmi_check_system()`. The quirk table covers Dell Inspiron 7375, Dell Latitude 5495, Acer Aspire A315-41, and Lenovo ideapad 330S-15ARR.

Control flow: during AMD IOMMU init, `amd_iommu_apply_ivrs_quirks()` scans DMI matches. On match, the callback injects special IOAPIC mappings before normal IVRS-derived interrupt-remapping setup consumes them.

State and persistence: no runtime mutable state beyond the global special-device maps updated by `add_special_device()`. Tables are `__initconst`, and the public function is `__init`.

Dependencies and integration points: compiled only with `CONFIG_DMI`, depends on AMD IVRS parsing helpers from `amd_iommu.h`, and affects x86 interrupt remapping because IOAPIC source IDs must map to the right IOMMU device IDs.

Risks: overly broad DMI matches could change interrupt-remapping IDs on unrelated machines. Missing quirks leave affected systems with broken IOAPIC interrupt remapping. The callback treats zero as the sentinel, so quirk entries cannot use zero-valued id/devid pairs.

Test signals: boot logs on listed systems should show corrected IOAPIC mapping behavior; regression tests are mainly DMI match audits and interrupt-remapping smoke tests on affected hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/amd/quirks.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/apple-dart.c -->
# sources/distributed-fs/ceph-client/drivers/iommu/apple-dart.c

Purpose: Apple DART IOMMU driver for Apple Silicon SoCs. It probes DART MMIO blocks, maps device stream IDs from devicetree, creates IOMMU domains backed by `io-pgtable`, programs per-stream TCR/TTBR registers, handles faults, and supports suspend/resume.

Important APIs, types, and functions: the primary ops are `apple_dart_iommu_ops` and default domain ops for attach/map/unmap/TLB sync. Hardware description uses `struct apple_dart_hw`; device state uses `struct apple_dart`; domain state uses `struct apple_dart_domain`; device stream state uses `struct apple_dart_master_cfg` and stream maps. Key functions include `apple_dart_probe()`, `apple_dart_of_xlate()`, `apple_dart_finalize_domain()`, `apple_dart_attach_dev_paging()`, identity/blocked attach handlers, `apple_dart_domain_flush_tlb()`, and T8020/T8110 IRQ handlers.

Control flow: probe maps MMIO, enables clocks, reads parameters, validates stream count, resets hardware, registers IRQ and IOMMU device. `of_xlate` builds per-device stream maps and checks that all DARTs for a device share compatible page size/address size. Domain finalization allocates `io_pgtable_ops`, records aperture geometry, and snapshots stream maps. Paging attach adds streams atomically and writes TTBRs/TCRs; identity attach writes bypass TCRs; blocked attach disables DMA.

State and persistence: per-DART state includes MMIO base, clocks, stream count, capabilities, stream-to-group mapping, saved TCR/TTBR registers for PM, and an IOMMU core device. Domains retain atomic SID bitmaps because attach/detach can race. Hardware retains TCR/TTBR stream programming until reset, blocked attach, suspend/resume restore, or driver removal.

Dependencies and integration points: depends on devicetree IOMMU xlate, platform driver/probe, clocks, shared IRQs, `io-pgtable` formats `APPLE_DART`/`APPLE_DART2`, DMA-IOMMU reserved regions, PCI Apple MSI doorbell reserved region, and generic IOMMU grouping.

Risks: devices spanning multiple DARTs must have compatible geometry; `MAX_DARTS_PER_DEVICE` and static stream arrays encode platform assumptions. Flushes are whole-stream rather than fine-grained. Bypass may be unavailable or forced by page-size mismatch. Group merging for PCI assumes Apple PCIe devices from the same bus do not span multiple DARTs.

Test signals: devicetree xlate with one/multiple streams, map/unmap DMA through io-pgtable, identity/blocked domain switching, DART fault IRQ decoding, PM suspend/resume restoring TCR/TTBRs, PCI MSI doorbell reserved region, and probe/remove cleanup with clocks and shared IRQs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/apple-dart.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/arm/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/iommu/arm/Kconfig

Purpose: Kconfig menu for Arm-family IOMMU drivers, including Arm SMMU v1/v2, Arm SMMU v3, Qualcomm IOMMU, SVA, iommufd, KUnit tests, and Tegra241 CMDQ-V.

Important symbols: `ARM_SMMU`, `ARM_SMMU_LEGACY_DT_BINDINGS`, `ARM_SMMU_DISABLE_BYPASS_BY_DEFAULT`, `ARM_SMMU_MMU_500_CPRE_ERRATA`, `ARM_SMMU_QCOM`, `ARM_SMMU_QCOM_DEBUG`, `ARM_SMMU_V3`, `ARM_SMMU_V3_SVA`, `ARM_SMMU_V3_IOMMUFD`, `ARM_SMMU_V3_KUNIT_TEST`, `TEGRA241_CMDQV`, and `QCOM_IOMMU`.

Control flow: build configuration selects the generic IOMMU API and io-pgtable backends, exposes optional subfeatures only under their parent driver, and gates SVA/iommufd/test source inclusion through the Makefiles. `ARM_SMMU_V3` selects `IOMMUFD_DRIVER` when IOMMUFD is enabled.

State and persistence: no runtime state; this file determines which code is compiled and which runtime capabilities can exist.

Dependencies and integration points: ties Arm drivers to `ARM64`, `ARM`, `COMPILE_TEST`, `IOMMU_API`, `IOMMU_IO_PGTABLE_LPAE`, `IOMMU_SVA`, `IOMMU_IOPF`, `MMU_NOTIFIER`, `KUNIT`, and Qualcomm SCM/ARM DMA helper selections.

Risks: incorrect dependency/select relationships can build unsupported feature combinations, especially SVA without notifier/IOPF support or KUnit without SVA symbols. Defaults like disabling unmatched bypass affect platform security posture.

Test signals: `allyesconfig`, `allmodconfig`, ARM64 defconfig, SVA/iommufd-enabled builds, and KUnit config builds should all resolve symbols consistently.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/arm/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/arm/Makefile -->
# sources/distributed-fs/ceph-client/drivers/iommu/arm/Makefile

Purpose: delegates Arm IOMMU builds to the `arm-smmu/` and `arm-smmu-v3/` subdirectories.

Important build entries: `obj-y += arm-smmu/ arm-smmu-v3/` ensures both subdirectory Makefiles are visited regardless of whether their contained objects are selected.

Control flow: Kbuild descends into both folders, where config-dependent object variables decide actual compilation.

State and persistence: no runtime state.

Dependencies and integration points: integrates this directory into the parent `drivers/iommu` build and relies on subdirectory Makefiles to honor Kconfig symbols.

Risks: removing a subdirectory here would silently omit its driver even if Kconfig enables it. Adding config gating here could diverge from subdirectory selection.

Test signals: Kbuild traversal under configs with only SMMU v1/v2, only SMMU v3, or neither should remain clean.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/arm/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/arm/arm-smmu-v3/Makefile -->
# sources/distributed-fs/ceph-client/drivers/iommu/arm/arm-smmu-v3/Makefile

Purpose: Kbuild rules for the Arm SMMU v3 driver and optional companion objects.

Important build entries: `obj-$(CONFIG_ARM_SMMU_V3) += arm_smmu_v3.o`; base object list `arm_smmu_v3-y := arm-smmu-v3.o`; optional additions for `CONFIG_ARM_SMMU_V3_IOMMUFD`, `CONFIG_ARM_SMMU_V3_SVA`, and `CONFIG_TEGRA241_CMDQV`; separate KUnit module/object `obj-$(CONFIG_ARM_SMMU_V3_KUNIT_TEST) += arm-smmu-v3-test.o`.

Control flow: Kbuild links optional iommufd/SVA/CMDQ-V code into the main SMMU v3 object when enabled, while tests are built independently under the KUnit config.

State and persistence: no runtime state.

Dependencies and integration points: mirrors `arm/Kconfig` feature symbols and determines whether functions such as SVA domain allocation or iommufd vSMMU hooks are present in the driver binary.

Risks: missing an optional object here produces unresolved callbacks or disabled features despite Kconfig enabling them. Test object dependencies must match exported-for-KUnit symbols from the core driver.

Test signals: compile matrix for base SMMU v3, SVA, iommufd, Tegra CMDQ-V, and KUnit combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/arm/arm-smmu-v3/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/arm/arm-smmu-v3/arm-smmu-v3-iommufd.c -->
# sources/distributed-fs/ceph-client/drivers/iommu/arm/arm-smmu-v3/arm-smmu-v3-iommufd.c

Purpose: Arm SMMU v3 iommufd support for hardware info, vSMMU creation, nested domains, virtual invalidation forwarding, and virtual event reporting.

Important APIs, types, and functions: `arm_smmu_hw_info()` reports IDR/IIDR/AIDR data; `arm_vsmmu_alloc_domain_nested()` creates `IOMMU_DOMAIN_NESTED`; `arm_smmu_attach_dev_nested()` installs nested STEs; `arm_vsmmu_cache_invalidate()` copies and converts userspace invalidation commands; `arm_smmu_get_viommu_size()` gates vIOMMU support; `arm_vsmmu_init()` initializes vSMMU state; `arm_vmaster_report_event()` rewrites event SID to vSID. Local helpers validate vSTEs and convert vSID to host SID.

Control flow: nested allocation copies `IOMMU_HWPT_DATA_ARM_SMMUV3`, validates allowed STE bits/configs, extracts ATS intent, and stores sanitized STE words. Nested attach ensures same SMMU, no active SSIDs, prepares attach state under the ASID lock, derives ATS disable policy from virtual EATS, builds a physical STE that combines S2 parent and virtual S1/CD-table/bypass/abort state, installs it, and commits attach state. Invalidation copies an array from userspace, converts each command to CPU-endian internal format, overwrites VMID/SID with host values, batches into the command queue, and reports progress by shrinking `entry_num`.

State and persistence: `struct arm_vsmmu` stores the host SMMU, S2 parent, and VMID. `struct arm_smmu_nested_domain` stores sanitized virtual STE data, ATS enable flag, and vSMMU pointer. `struct arm_smmu_vmaster` stores per-attached-device vSID state for invalidations and event reporting.

Dependencies and integration points: depends on core SMMU v3 stream-table/CD/cmdq helpers, iommufd vIOMMU/vDEVICE APIs, UAPI structures for Arm SMMUv3, S2 parent domains, implementation-specific hooks, and event queue reporting. Imports the `IOMMUFD` namespace.

Risks: command conversion must not trust userspace VMID/SID fields; failures return `-EIO` for invalid virtual commands. ATS coherency depends on the VM generating ATC invalidations when EATS says ATS is enabled. vIOMMU support is withheld unless hardware has nesting, no forced sync defect, and either full writeback snoop or S2FWB.

Test signals: iommufd create vSMMU, nested attach with abort/bypass/S1 translate STEs, invalid vSTE bit fuzzing, vDEVICE mapping for invalidation/event paths, TLBI/ATC/CFGI command conversion, command queue batching, and event SID rewriting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/arm/arm-smmu-v3/arm-smmu-v3-iommufd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/arm/arm-smmu-v3/arm-smmu-v3-sva.c -->
# sources/distributed-fs/ceph-client/drivers/iommu/arm/arm-smmu-v3/arm-smmu-v3-sva.c

Purpose: implements SVA domains for Arm SMMU v3. It builds context descriptors for process page tables, registers mmu notifiers, invalidates SMMU TLBs on CPU page-table changes, binds PASIDs, and cleans up ASIDs safely.

Important APIs, types, and functions: `arm_smmu_make_sva_cd()` creates SVA context descriptors and is exported for KUnit; `arm_smmu_sva_supported()` gates feature support; `arm_smmu_sva_domain_alloc()` allocates an SVA domain and ASID; `arm_smmu_sva_set_dev_pasid()` binds a PASID; `arm_smmu_sva_domain_free()` frees through mmu-notifier SRCU; notifier callbacks are `arm_smmu_mm_arch_invalidate_secondary_tlbs()`, `arm_smmu_mm_release()`, and `arm_smmu_mmu_notifier_free()`.

Control flow: support detection checks SMMU coherency/VAX/BBML/page-size/output-address/ASID requirements against sanitized CPU features. Allocation creates a domain, assigns stage SVA, allocates an ASID in `arm_smmu_asid_xa`, registers the notifier, and returns the domain. Binding takes a temporary mm ref, builds a CD pointing at `mm->pgd`, and calls `arm_smmu_set_pasid()`. mm release rewrites bound CDs into valid faulting descriptors with translation disabled, then invalidates the domain.

State and persistence: SVA domains retain ASID, mmu notifier, SMMU pointer, device list, and per-CD descriptor state. ASID xarray membership persists until domain free erases it; actual memory free is deferred through `mmu_notifier_put()` and the notifier free callback.

Dependencies and integration points: uses Arm64 CPU feature registers, `vabits_actual`, MAIR, mmu notifier infrastructure, core SMMU CD write and invalidation helpers, PASID installation, and io-pgtable Arm definitions for TCR encodings.

Risks: SVA ignores CPU permission overlays/GCS and emits a warning. mm release must keep CDs valid to avoid C_BAD_CD event storms while DMA may continue. ASID reuse is allowed after domain invalidation even if notifier invalidations race, relying on harmless extra invalidations.

Test signals: KUnit covers `arm_smmu_make_sva_cd()` transitions. Runtime signals include SVA feature gating on varied page sizes/ASID widths, PASID bind/unbind, mm exit during DMA, secondary TLB invalidation ranges, and ASID reuse stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/arm/arm-smmu-v3/arm-smmu-v3-sva.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/arm/arm-smmu-v3/arm-smmu-v3-test.c -->
# sources/distributed-fs/ceph-client/drivers/iommu/arm/arm-smmu-v3/arm-smmu-v3-test.c

Purpose: KUnit tests for Arm SMMU v3 entry-writing and invalidation-set helpers. It verifies that STE/CD transitions use the expected number of sync points and remain hitless where required.

Important APIs, types, and functions: `struct arm_smmu_test_writer` wraps `arm_smmu_entry_writer`; `arm_smmu_v3_test_ste_expect_transition()` and `arm_smmu_v3_test_cd_expect_transition()` are the core assertions; helper constructors build bypass, abort, CD-table, S2, S1, SVA, release, and nested STE/CD shapes. `arm_smmu_v3_invs_test()` covers `arm_smmu_invs_alloc/merge/unref/purge`.

Control flow: each test builds an initial and target entry, runs `arm_smmu_write_entry()` through a fake writer, records every sync, checks that intermediate entries are equivalent to either old or new state for used bits during hitless transitions, checks whether an invalid entry was written, and verifies final memory equality. The suite initializes global bypass/abort STEs in `suite_init`.

State and persistence: all state is test-local except static fixtures (`bypass_ste`, `abort_ste`, fake `smmu`, fake `sva_mm`) and static invalidation examples. There is no hardware access; fake structures provide enough data for entry constructors.

Dependencies and integration points: depends on KUnit, `EXPORTED_FOR_KUNIT_TESTING` symbols from the SMMU v3 driver and SVA file, io-pgtable config structs, and SMMU entry helper APIs. Built only with `CONFIG_ARM_SMMU_V3_KUNIT_TEST`.

Risks: tests encode expected sync counts, so legitimate algorithm changes require deliberate test updates. Fake hardware data may not cover every implementation-specific bit. The invalidation tests are algorithmic and do not verify command queue hardware side effects.

Test signals: the suite itself is the primary signal: bypass/abort/CD-table/S2/S1/SVA/nested transitions, hitless versus non-hitless paths, stall and ATS variants, SVA release CD behavior, and invalidation merge/refcount/trash purge semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/arm/arm-smmu-v3/arm-smmu-v3-test.c -->
