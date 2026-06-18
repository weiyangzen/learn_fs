# subset-b-003994 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/fsl_pamu.c -->
# sources/distributed-fs/ceph-client/drivers/iommu/fsl_pamu.c

## Purpose

`fsl_pamu.c` is the early platform driver for Freescale/NXP QorIQ PAMU hardware. It allocates and programs the shared primary PAACE table, secondary PAACE table, and operation mapping table, wires access-violation interrupts, disables PAMU bypass in GUTS registers, and enables LIODNs described by device tree so DMA clients can use PAMU identity/window translations.

## Important APIs, Types, and Functions

- `struct pamu_isr_data`: interrupt context with the mapped PAMU register base and PAMU count.
- Global table pointers `ppaact` and `spaact`: software-visible backing storage for hardware PAACE tables.
- `pamu_enable_liodn` / `pamu_disable_liodn`: exported LIODN validity toggles used by the domain layer.
- `pamu_config_ppaace`: programs one primary PAACE window, permissions, stash ID, address translation mode, and optional OMT index.
- `pamu_update_paace_stash`, `get_stash_id`, `get_ome_index`: stash and operation-mapping helpers used by `fsl_pamu_domain.c`.
- `setup_omt`, `setup_liodns`, `setup_one_pamu`: hardware table/register population.
- `pamu_av_isr`: logs access-violation registers, clears violation status, and may disable the offending LIODN.
- `create_csd`: erratum workaround that creates a coherence subdomain with LAW/CSDID programming on listed SoCs.
- `fsl_pamu_probe` and `fsl_pamu_init`: early manual platform-device registration and probe.

## Control Flow

`fsl_pamu_init` runs as an `arch_initcall`, finds the single `fsl,pamu` device-tree node, registers a synthetic platform driver/device, calls `pamu_domain_init`, and then adds the platform device so `fsl_pamu_probe` runs early enough for QMan/BMan users. Probe maps PAMU and GUTS registers, installs the access-violation IRQ, reads capability values, allocates a naturally aligned block for PAACT/SPAACT/OMT, optionally creates a CoreNet coherence subdomain for erratum A-004510, programs every PAMU instance with the table physical ranges, fills the OMT, disables bypass bits, then enables LIODNs from `fsl,liodn` properties.

LIODN setup initializes PAACE entries as primary, coherent, identity/no-translate windows with full permissions, with special QMan/BMan OMT and stash tweaks. Domain-level calls later disable a LIODN, reconfigure the PAACE with window translation and permissions, then re-enable it.

## State and Persistence Behavior

State is in kernel memory and MMIO registers only. `ppaact` persists for the platform lifetime and is shared between all PAMUs. `probed` prevents duplicate probe. PAACE stores are ordered with `mb()` so hardware sees completed descriptor updates before validity changes. There is no remove path; early platform initialization assumes PAMU remains active until reboot.

## Dependencies and Integration Points

The file depends on Open Firmware properties (`fsl,pamu`, `fsl,liodn`, cache nodes, GUTS, LAW, CoreNet CF), PowerPC/QorIQ SPR and CCSR definitions, big-endian MMIO accessors, and the domain APIs declared in `fsl_pamu.h`. It integrates directly with `fsl_pamu_domain.c`, QMan/BMan/CAAM-style LIODN users, and the Linux IRQ subsystem.

## Risks and Edge Cases

- `pamu_get_ppaace` checks `liodn >= PAACE_NUMBER_ENTRIES` but not negative LIODNs.
- Probe allocates one combined table block and has no driver remove path, so failures after table allocation depend on the error path and successful systems intentionally retain mappings.
- `get_stash_id` assumes several device-tree properties exist and traverses cache phandles; malformed CPU/cache nodes can return `~0`.
- `pamu_av_isr` uses `BUG_ON` for unexpected PAACE state or disable failure, turning hardware faults into kernel crashes.
- `setup_one_pamu` ignores its `pamu_reg_size` argument.
- `create_csd` manipulates undocumented CSDID offsets and searches LAW entries with strict assumptions about existing DDR LAW layout.

## Test Signals

Useful coverage includes boot on supported QorIQ device trees, validation of PAACT/SPAACT/OMT physical register programming, LIODN enable/disable and PAACE field checks, QMan/BMan special OMT/stash setup, malformed or missing `fsl,liodn` properties, access-violation IRQ injection, and erratum-path LAW/CSDID programming on matching SVRs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/fsl_pamu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/fsl_pamu.h -->
# sources/distributed-fs/ceph-client/drivers/iommu/fsl_pamu.h

## Purpose

`fsl_pamu.h` defines the Freescale PAMU hardware register map, PAACE/OME descriptor formats, field masks, operation encodings, table sizes, and cross-file APIs used by the PAMU platform and IOMMU-domain code.

## Important APIs, Types, and Functions

- `set_bf` / `get_bf`: mask-and-shift helpers for descriptor bitfields.
- Register offsets: PAMU table pointer registers, error/status registers, capability/control registers, and debug registers.
- `struct pamu_mmap_regs`: compact view of the PAMU table base/limit MMIO block.
- `struct paace`: primary/secondary PAACE descriptor, including window base, address fields, destination attributes, translation modes, translated base, secondary pointer, and operation encoding.
- `struct ome`: 128-byte operation mapping entry used by indexed operation translation.
- Constants such as `PAACE_NUMBER_ENTRIES`, `SPAACE_NUMBER_ENTRIES`, `OME_NUMBER_ENTRIES`, `PAACT_SIZE`, `SPAACT_SIZE`, and `OMT_SIZE`.
- Exported prototypes: `pamu_domain_init`, `pamu_enable_liodn`, `pamu_disable_liodn`, `pamu_config_ppaace`, `get_stash_id`, `get_ome_index`, and `pamu_update_paace_stash`.

## Control Flow

This header is passive, but it shapes the control flow of the implementation. `fsl_pamu.c` uses the register offsets to program hardware and the descriptor macros to construct PAACE/OME entries. `fsl_pamu_domain.c` calls the declared functions to change LIODN table entries when devices attach to or detach from IOMMU domains.

## State and Persistence Behavior

The data structures mirror hardware-visible memory. PAACE and OME contents persist in allocated RAM while PAMU is enabled and are consumed by hardware through programmed physical base/limit registers. The header encodes fixed table sizes rather than discovering all limits dynamically; comments indicate PAACE sizing is hard-coded to accommodate U-Boot LIODNs.

## Dependencies and Integration Points

It includes Linux IOMMU and PCI headers plus `<asm/fsl_pamu_stash.h>` for cache-stash attributes. Its ABI is private to the kernel tree but shared between PAMU hardware setup and PAMU domain integration.

## Risks and Edge Cases

- Bitfield macros evaluate the value argument in a write expression and assume matching `*_SHIFT` symbols.
- `struct paace` layout must remain exactly hardware-compatible; padding or endian mistakes would corrupt translations.
- Fixed table entry counts can reject valid future LIODNs unless updated.
- Register and descriptor constants are opaque hardware encodings, so accidental reuse across primary/secondary fields is hard to detect at compile time.

## Test Signals

Build-time coverage should catch structure and prototype drift. Runtime validation should dump PAACE/OME entries for known LIODNs and verify register writes match the QorIQ PAMU manual, including field encodings for validity, permissions, stash ID, window size, translation mode, and operation mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/fsl_pamu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/fsl_pamu_domain.c -->
# sources/distributed-fs/ceph-client/drivers/iommu/fsl_pamu_domain.c

## Purpose

`fsl_pamu_domain.c` connects PAMU LIODN programming to the Linux IOMMU API. It registers a PAMU `iommu_device`, creates unmanaged PAMU domains, attaches devices by programming their LIODNs, implements identity `iova_to_phys`, manages device/domain bookkeeping, and exposes the Freescale L1 stash configuration helper.

## Important APIs, Types, and Functions

- `struct fsl_dma_domain`: PAMU domain state with device list, stash ID, embedded `iommu_domain`, and lock.
- `struct device_domain_info`: per-device LIODN/domain link stored in `dev_iommu_priv`.
- `iommu_init_mempool`: allocates slab caches for domains and device links.
- `pamu_set_liodn`: disables, configures, and prepares a LIODN PAACE for a domain.
- `fsl_pamu_attach_device` and `fsl_pamu_platform_attach`: unmanaged attach and platform-domain detach behavior.
- `fsl_pamu_configure_l1_stash`: exported stash update path for existing domain LIODNs.
- `fsl_pamu_device_group`, `fsl_pamu_probe_device`: group and device admission callbacks.
- `fsl_pamu_ops`: Linux IOMMU ops registration.

## Control Flow

`pamu_domain_init` creates slab caches, adds `iommu0` sysfs state, and registers `fsl_pamu_ops`. Domain allocation only accepts `IOMMU_DOMAIN_UNMANAGED`, initializes an identity-like 64 GiB geometry, and defaults `stash_id` to `~0`. Device attach resolves PCI devices to their host controller parent, reads all `fsl,liodn` values, links each LIODN into the domain list, configures the PAACE under `iommu_lock`, then enables the LIODN. Platform-domain attach is used as a detach hook from unmanaged domains; it removes device references and disables LIODNs, but does not restore identity PAACE state.

## State and Persistence Behavior

Domain state persists in slab-allocated `fsl_dma_domain` objects. Attached device/LIODN links are kept on the domain list and, for the first LIODN, in `dev_iommu_priv`. `domain_lock` protects per-domain lists and stash updates, `device_domain_lock` protects `dev_iommu_priv`, and `iommu_lock` serializes hardware PAACE changes. PAACE state persists in PAMU tables owned by `fsl_pamu.c`.

## Dependencies and Integration Points

The file depends on Linux IOMMU core, OF LIODN properties, PowerPC PCI controller helpers, and the PAMU hardware functions from `fsl_pamu.c`. It integrates with platform devices, PCI host controllers, `iommu_group` assignment, and Freescale QMan portal code that calls the stash helper.

## Risks and Edge Cases

- The file contains explicit FIXME notes that PAMU does not fit the modern IOMMU API well: the unmanaged domain is not a true paging domain and detaching cannot restore identity mappings.
- `attach_device` does not check `kmem_cache_zalloc` failure before dereferencing `info`.
- LIODNs are read as big-endian device-tree cells but compared and passed as raw `liodn[i]` without `be32_to_cpup`, unlike `fsl_pamu.c`.
- `remove_device_ref` calls `list_del` while nested lock ordering crosses domain and device-domain locks.
- PCI grouping depends on controller version and initialization ordering between PAMU and FSL PCI.

## Test Signals

Test attach/detach of platform devices with one and multiple LIODNs, PCI devices behind partitionable and non-partitionable controllers, stash update after attach, missing/invalid `fsl,liodn`, domain free with attached devices, and IOMMU group reuse. Lockdep and fault-injection around slab allocation and PAACE programming would be especially valuable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/fsl_pamu_domain.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/fsl_pamu_domain.h -->
# sources/distributed-fs/ceph-client/drivers/iommu/fsl_pamu_domain.h

## Purpose

`fsl_pamu_domain.h` defines the PAMU domain-private state structures shared by the domain implementation and nearby PAMU code.

## Important APIs, Types, and Functions

- `struct fsl_dma_domain`: list of attached device LIODNs, current stash ID, embedded `struct iommu_domain`, and a per-domain spinlock.
- `struct device_domain_info`: list node, device pointer, LIODN, and owning domain pointer for one device/LIODN association.

## Control Flow

The header does not implement logic. `fsl_pamu_domain.c` allocates these structures from slab caches, stores `device_domain_info` in the domain list and `dev_iommu_priv`, and uses `fsl_dma_domain` as the container for Linux IOMMU domains.

## State and Persistence Behavior

The structures represent all mutable domain-level PAMU state outside the hardware PAACE tables. They persist for the lifetime of a domain or device attachment and are released on detach/domain free.

## Dependencies and Integration Points

It includes `fsl_pamu.h`, so users inherit PAMU constants and Linux IOMMU dependencies. The embedded `iommu_domain` makes container conversion possible for IOMMU callbacks.

## Risks and Edge Cases

The header exposes raw list and lock fields with no helper API, so correctness depends on `fsl_pamu_domain.c` lock ordering. `device_domain_info` has one `liodn` field per object; multi-LIODN devices require multiple instances and only the first is stored in `dev_iommu_priv`.

## Test Signals

Structural tests are indirect: attach/detach paths should verify list integrity, `dev_iommu_priv` cleanup, multi-LIODN handling, and domain-free cleanup under lockdep.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/fsl_pamu_domain.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/generic_pt/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/iommu/generic_pt/Kconfig

## Purpose

This Kconfig file defines the Generic Radix Page Table library and the IOMMU page-table formats that instantiate it for AMDv1, Intel VT-d second stage, RISC-V, and x86-64.

## Important APIs, Types, and Functions

- `GENERIC_PT`: top-level boolean library option, visible mainly for `COMPILE_TEST`.
- `DEBUG_GENERIC_PT`: enables extra runtime checks and full KUnit coverage behavior.
- `IOMMU_PT`: tristate generic IOMMU page-table implementation selecting `IOMMU_API`.
- `IOMMU_PT_AMDV1`, `IOMMU_PT_VTDSS`, `IOMMU_PT_RISCV64`, `IOMMU_PT_X86_64`: per-format modules.
- `IOMMU_PT_KUNIT_TEST`: KUnit test module covering enabled formats.

## Control Flow

The build graph is gated by `GENERIC_PT`, then `IOMMU_PT`, then format symbols. Format options are intended to be selected by real IOMMU drivers rather than manually chosen. The KUnit option uses dependency expressions that allow tests when each format is enabled or absent.

## State and Persistence Behavior

No runtime state is stored here. Configuration choices determine which format objects and tests are compiled and whether debug-only assertions/features are included.

## Dependencies and Integration Points

The options integrate with `drivers/iommu/generic_pt/fmt/Makefile`, generic IOMMU APIs, KUnit, and drivers such as Intel IOMMU that select `GENERIC_PT`, `IOMMU_PT`, `IOMMU_PT_X86_64`, and `IOMMU_PT_VTDSS`.

## Risks and Edge Cases

- Several formats depend on `!GENERIC_ATOMIC64` because they use 64-bit compare-exchange helpers.
- Enabling `DEBUG_GENERIC_PT` changes feature compilation for tests and may incur runtime cost.
- KUnit coverage depends on formats selected into the build; disabled formats are not tested.

## Test Signals

Build matrix coverage should include built-in and module `IOMMU_PT`, each format individually, all formats with `IOMMU_PT_KUNIT_TEST`, and debug vs non-debug builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/generic_pt/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/generic_pt/fmt/Makefile -->
# sources/distributed-fs/ceph-client/drivers/iommu/generic_pt/fmt/Makefile

## Purpose

The format Makefile instantiates the generic IOMMU page-table template for each enabled hardware format and builds matching KUnit objects by recompiling the same format source with `GENERIC_PT_KUNIT`.

## Important APIs, Types, and Functions

- `iommu_pt_fmt-*`: format list built from Kconfig symbols.
- `create_format`: make macro adding `iommu_<fmt>.o`, `kunit_iommu_<fmt>.o`, and test CFLAGS.
- Pattern rule for `kunit_iommu_%.o`: compiles `iommu_%.c` into a separate KUnit object.
- `IOMMU_PT_KUNIT_TEST`: aggregate test object name assigned when any format is processed.

## Control Flow

Enabled built-in and module formats are enumerated through `foreach` and passed to `create_format`. Normal objects compile the tiny `iommu_<fmt>.c` wrappers. KUnit objects reuse those same wrappers but add `-DGENERIC_PT_KUNIT=1`, causing format headers and `iommu_pt.h` to expose test suites.

## State and Persistence Behavior

No runtime state exists. The file controls object generation and ensures KUnit code is derived from the same format instantiations as production code.

## Dependencies and Integration Points

It depends on Kbuild variables from `generic_pt/Kconfig`, wrapper files such as `iommu_amdv1.c`, and template headers `iommu_pt.h`, `kunit_generic_pt.h`, and `kunit_iommu_pt.h`.

## Risks and Edge Cases

- If no format is enabled, `IOMMU_PT_KUNIT_TEST` remains empty and the KUnit target contributes no objects.
- The mock format is tied to `CONFIG_IOMMUFD_TEST`, not a public Generic PT format option.
- Recompiling the same source with different flags relies on dependency tracking through `if_changed_dep`.

## Test Signals

Validate `make M=drivers/iommu/generic_pt/fmt` with each format built in and as a module, and run KUnit with multiple enabled formats to confirm all `kunit_iommu_<fmt>.o` objects are generated.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/generic_pt/fmt/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/generic_pt/fmt/amdv1.h -->
# sources/distributed-fs/ceph-client/drivers/iommu/generic_pt/fmt/amdv1.h

## Purpose

`amdv1.h` defines the Generic PT format implementation for AMD IOMMU v1 host page tables. It supplies all format callbacks required by `pt_common.h` and `iommu_pt.h`: descriptor decode/encode, supported page sizes, table installation, protection conversion, dirty handling, and hardware-info extraction.

## Important APIs, Types, and Functions

- Format constants: 64-bit entries, 4 KiB table memory, max VA/OA sizes, top-level range, and top physical mask.
- Descriptor bits: present, dirty, next-level/page-size code, output address, force coherence, I/O read/write.
- `amdv1pt_table_pa`, `amdv1pt_entry_oa`, `amdv1pt_entry_num_contig_lg2`: address and contiguous-size decoding.
- `amdv1pt_possible_sizes`: exposes nearly all power-of-two page sizes while excluding 512 GiB due to a hardware bug.
- `amdv1pt_load_entry_raw`, `amdv1pt_install_leaf_entry`, `amdv1pt_install_table`, `amdv1pt_clear_entries`.
- Dirty helpers: `amdv1pt_entry_is_write_dirty`, `amdv1pt_entry_make_write_clean`, `amdv1pt_entry_make_write_dirty`.
- IOMMU callbacks: `amdv1pt_iommu_set_prot`, `amdv1pt_iommu_fmt_init`, `amdv1pt_iommu_fmt_hw_info`.

## Control Flow

The wrapper source defines `PT_FMT amdv1` and includes this header before `iommu_pt.h`. Generic mapping code calls the format callbacks to create AMDv1 PTEs. Leaf installation writes either one entry for base page size or a run of identical entries for contiguous mappings, using AMD's next-level size encoding. Table installation uses atomic `cmpxchg64` and sets IR/IW on intermediate entries so permissions are controlled by leaves.

## State and Persistence Behavior

The format stores all translation state in AMDv1 PTE words. Dirty state is hardware/software-visible through the `D` bit and may span a contiguous run. Optional SME encryption features set or clear memory-encryption bits in table and leaf addresses.

## Dependencies and Integration Points

It depends on `defs_amdv1.h` for per-table structs, `pt_defs.h`, Linux bitfield helpers, SME memory encryption helpers, and Generic PT's `struct pt_iommu` ABI. It integrates with IOMMUFD dirty tracking and KUnit format configuration.

## Risks and Edge Cases

- Contiguous size encoding is nontrivial and relies on low OA bits; wrong alignment would corrupt the decoded page size.
- 512 GiB pages are deliberately excluded for a hardware bug.
- SME encryption is inferred from table encryption features and `IOMMU_MMIO`, not an explicit higher-level encrypted mapping flag.
- Dirty cleaning clears all entries in a contiguous run and relies on later TLB synchronization.

## Test Signals

KUnit should cover all AMDv1 page sizes except the excluded 512 GiB case, contiguous entry encode/decode, dirty read/clear/set, SME table/leaf encoding, force-coherence bit generation, top mode export, and failure for invalid `starting_level`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/generic_pt/fmt/amdv1.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/generic_pt/fmt/defs_amdv1.h -->
# sources/distributed-fs/ceph-client/drivers/iommu/generic_pt/fmt/defs_amdv1.h

## Purpose

`defs_amdv1.h` declares the AMDv1-specific Generic PT table containers, configuration, write attributes, and hardware-info structures consumed by `amdv1.h` and external drivers.

## Important APIs, Types, and Functions

- `typedef u64 pt_vaddr_t`, `typedef u64 pt_oaddr_t`: AMDv1 uses 64-bit virtual and output addresses.
- `struct amdv1pt_write_attrs`: descriptor bits passed from protection conversion to PTE installation.
- `struct pt_amdv1`: embeds `struct pt_common`.
- `struct pt_iommu_amdv1`: embeds `struct pt_iommu` plus AMDv1 common state.
- `struct pt_iommu_amdv1_cfg`: common hardware limits and `starting_level`.
- `struct pt_iommu_amdv1_hw_info`: root physical pointer and AMD mode.

## Control Flow

The header supplies type names that `amdv1.h` binds through `#define pt_write_attrs`, `pt_iommu_table`, and container helpers. Drivers pass `pt_iommu_amdv1_cfg` to the generated `pt_iommu_amdv1_init` and receive root/mode information via generated hardware-info APIs.

## State and Persistence Behavior

Runtime state is the embedded `pt_common` and `pt_iommu` inside caller-owned table storage. The configuration is input-only; hardware-info is output-only.

## Dependencies and Integration Points

It integrates with `linux/generic_pt/common.h` and the generated symbols exported from `iommu_amdv1.c`.

## Risks and Edge Cases

The header is small but ABI-sensitive inside the kernel: container layout must match `amdv1.h`, and `starting_level` must agree with the hardware DTE mode expected by callers.

## Test Signals

Compile coverage should validate external users can include the header and call generated init/hw-info functions. KUnit indirectly validates `starting_level` configurations and the root/mode export structure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/generic_pt/fmt/defs_amdv1.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/generic_pt/fmt/defs_riscv.h -->
# sources/distributed-fs/ceph-client/drivers/iommu/generic_pt/fmt/defs_riscv.h

## Purpose

`defs_riscv.h` declares the RISC-V Generic PT format types for 32-bit and 64-bit variants, including entry width, address types, write attributes, table containers, configuration, and hardware-info output.

## Important APIs, Types, and Functions

- `pt_riscv_entry_t`: `u32` under `PT_RISCV_32BIT`, otherwise `u64`.
- `pt_vaddr_t` and `pt_oaddr_t`: RISC-V virtual and output address types.
- `struct riscvpt_write_attrs`: descriptor bits for PTE installation.
- `struct pt_riscv`: common format state.
- `struct pt_iommu_riscv_64`, `pt_iommu_riscv_64_cfg`, `pt_iommu_riscv_64_hw_info`: generated 64-bit IOMMU table ABI.

## Control Flow

`riscv.h` consumes these definitions to select PPN masks and container names, then `iommu_pt.h` generates the exported RISC-V IOMMU operations.

## State and Persistence Behavior

The structures hold in-memory page-table state and generated hardware control values such as root PPN and `iosatp` mode. Configuration fields are consumed during initialization and not persisted separately.

## Dependencies and Integration Points

It integrates with the generic page-table common ABI and RISC-V IOMMU drivers that need Sv39/Sv48/Sv57-compatible root information.

## Risks and Edge Cases

The conditional 32-bit type branch is present even though the listed wrapper instantiates RISC-V 64. Layout and symbol names must remain aligned with `riscv.h` macros.

## Test Signals

Build RISC-V 64 format and KUnit configurations for Sv39, Sv48, and Sv57, including Svnapot-enabled cases, to verify these definitions support generated APIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/generic_pt/fmt/defs_riscv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/generic_pt/fmt/defs_vtdss.h -->
# sources/distributed-fs/ceph-client/drivers/iommu/generic_pt/fmt/defs_vtdss.h

## Purpose

`defs_vtdss.h` declares the Intel VT-d second-stage Generic PT type wrappers used by `vtdss.h` and generated IOMMU page-table code.

## Important APIs, Types, and Functions

- `typedef u64 pt_vaddr_t`, `typedef u64 pt_oaddr_t`: 64-bit IOVA/output address types.
- `struct vtdss_pt_write_attrs`: descriptor bits for second-stage entries.
- `struct pt_vtdss`: common second-stage page-table state.
- `struct pt_iommu_vtdss`: generated IOMMU table container.
- `struct pt_iommu_vtdss_cfg`: common hardware limits and `top_level`.
- `struct pt_iommu_vtdss_hw_info`: exported second-stage root pointer and address-width encoding.

## Control Flow

The file provides compile-time names and layouts. `vtdss.h` binds them to Generic PT callback names and `iommu_vtdss.c` exports generated functions.

## State and Persistence Behavior

State lives in the embedded `pt_common` and `pt_iommu` in caller-provided storage. Hardware-info output reflects the current top table pointer and top-level encoding.

## Dependencies and Integration Points

It is part of the internal Generic PT ABI used by Intel IOMMU nested/second-stage support.

## Risks and Edge Cases

The `top_level` setting must match hardware address-width encoding. Mismatched layout between this header and `vtdss.h` would break container conversions.

## Test Signals

KUnit configurations for 3-, 4-, and 5-level second-stage tables validate this header's configuration and hardware-info path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/generic_pt/fmt/defs_vtdss.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/generic_pt/fmt/defs_x86_64.h -->
# sources/distributed-fs/ceph-client/drivers/iommu/generic_pt/fmt/defs_x86_64.h

## Purpose

`defs_x86_64.h` declares x86-64 Generic PT wrappers for first-stage/x86-style page tables, including address types, write attributes, table containers, configuration, and hardware-info output.

## Important APIs, Types, and Functions

- `pt_vaddr_t` and `pt_oaddr_t`: both 64-bit.
- `struct x86_64_pt_write_attrs`: descriptor bits used during entry installation.
- `struct pt_x86_64`: embeds `pt_common`.
- `struct pt_iommu_x86_64`: generated IOMMU table container.
- `struct pt_iommu_x86_64_cfg`: common hardware limits and `top_level`.
- `struct pt_iommu_x86_64_hw_info`: GCR3/root pointer and number of levels.

## Control Flow

`x86_64.h` uses these definitions to generate format callbacks, while wrapper sources expose `pt_iommu_x86_64_init` and hardware-info helpers.

## State and Persistence Behavior

The generated table object persists in caller-owned memory. `top_level` controls the initial root depth and hardware-info output.

## Dependencies and Integration Points

It integrates with Intel/AMD IOMMU code needing x86-compatible page tables and the Generic PT common ABI.

## Risks and Edge Cases

The same format is used for multiple hardware contexts with different sign-extension and encryption semantics, so callers must set feature flags and top levels correctly.

## Test Signals

KUnit should cover 4- and 5-level sign-extended x86, plus non-sign-extended AMD-style configurations, validating layout and hardware-info fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/generic_pt/fmt/defs_x86_64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/generic_pt/fmt/iommu_amdv1.c -->
# sources/distributed-fs/ceph-client/drivers/iommu/generic_pt/fmt/iommu_amdv1.c

## Purpose

`iommu_amdv1.c` is the AMDv1 wrapper that instantiates the shared `iommu_pt.h` template with AMDv1 format definitions.

## Important APIs, Types, and Functions

- `#define PT_FMT amdv1`: selects `fmt/amdv1.h`.
- `PT_SUPPORTED_FEATURES`: enables AMDv1 force-coherence, AMDv1 encrypted tables, dynamic top growth, and DMA-incoherent page-table handling.
- Inclusion of `iommu_template.h`: expands the format-specific Generic PT IOMMU implementation.

## Control Flow

The wrapper contains no runtime control flow of its own. Compilation sets preprocessor knobs and then includes the template, generating AMDv1-namespaced init, map, unmap, dirty, info, deinit, and hardware-info symbols.

## State and Persistence Behavior

State is whatever the template and `amdv1.h` generate in `struct pt_iommu_amdv1`. The wrapper only controls feature availability at compile time.

## Dependencies and Integration Points

It depends on `amdv1.h`, `iommu_template.h`, Kbuild format selection, and consumers that link to the exported `GENERIC_PT_IOMMU` namespace symbols.

## Risks and Edge Cases

Incorrect `PT_SUPPORTED_FEATURES` would silently remove support expected by AMD users. Dynamic top requires driver callbacks at runtime; DMA-incoherent requires an IOMMU device for cache maintenance.

## Test Signals

Build the AMDv1 module and run the AMDv1 KUnit suite under normal and debug configurations, including dynamic-top and DMA-incoherent feature toggles where supported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/generic_pt/fmt/iommu_amdv1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/generic_pt/fmt/iommu_mock.c -->
# sources/distributed-fs/ceph-client/drivers/iommu/generic_pt/fmt/iommu_mock.c

## Purpose

`iommu_mock.c` instantiates the Generic PT IOMMU template using the AMDv1 format in an IOMMUFD self-test variant.

## Important APIs, Types, and Functions

- `#define PT_FMT amdv1`, `#define PT_FMT_VARIANT mock`, and `#define AMDV1_IOMMUFD_SELFTEST`: select AMDv1 with altered test constants.
- `PT_SUPPORTED_FEATURES`: enables dynamic top, DMA-incoherent handling, and AMDv1 force coherence.
- Inclusion of `iommu_template.h`: generates mock-namespaced test symbols.

## Control Flow

There is no direct runtime logic. The file exists so IOMMUFD tests can exercise the generic template with nonstandard AMDv1 parameters, including a 2 KiB granule path defined in `amdv1.h`.

## State and Persistence Behavior

Generated state follows the AMDv1 template but is intended for tests, not hardware use.

## Dependencies and Integration Points

It is built when `CONFIG_IOMMUFD_TEST` is enabled and integrates with Generic PT and IOMMUFD test infrastructure.

## Risks and Edge Cases

Because this is a variant build, symbol naming and feature differences must remain isolated from real AMDv1. It intentionally stresses cases where CPU page size and IOMMU granule differ.

## Test Signals

IOMMUFD selftests and Generic PT KUnit should verify mock initialization, mapping/unmapping, dirty behavior where compiled, and no symbol collision with real AMDv1.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/generic_pt/fmt/iommu_mock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/generic_pt/fmt/iommu_riscv64.c -->
# sources/distributed-fs/ceph-client/drivers/iommu/generic_pt/fmt/iommu_riscv64.c

## Purpose

`iommu_riscv64.c` instantiates the Generic PT IOMMU template for RISC-V 64-bit Sv39/Sv48/Sv57 page tables.

## Important APIs, Types, and Functions

- `#define PT_FMT riscv` and `#define PT_FMT_VARIANT 64`: select the RISC-V 64 format.
- `PT_SUPPORTED_FEATURES`: enables sign extension, RISC-V Svnapot 64 KiB contiguous mappings, and DMA-incoherent handling.
- Inclusion of `iommu_template.h`: generates RISC-V namespaced IOMMU page-table functions.

## Control Flow

Compilation expands template code with RISC-V format callbacks. Runtime control flow is in generated map/unmap/init paths from `iommu_pt.h` and descriptor logic from `riscv.h`.

## State and Persistence Behavior

State lives in generated `pt_iommu_riscv_64` objects and RISC-V PTE memory, with optional sign-extended address ranges and Svnapot contiguous entries.

## Dependencies and Integration Points

It integrates with RISC-V IOMMU drivers that need Generic PT roots and with KUnit format configurations for Sv39/Sv48/Sv57.

## Risks and Edge Cases

Svnapot contiguous entries are only valid at level 0 and require feature gating. DMA-incoherent feature use requires cache-maintenance support through the generic template.

## Test Signals

Run RISC-V Generic PT KUnit for Sv39, Sv48, Sv57, with and without Svnapot, including sign-extension upper-range mapping tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/generic_pt/fmt/iommu_riscv64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/generic_pt/fmt/iommu_template.h -->
# sources/distributed-fs/ceph-client/drivers/iommu/generic_pt/fmt/iommu_template.h

## Purpose

`iommu_template.h` is the thin preprocessor dispatcher that includes the selected format header, the shared IOMMU page-table implementation, and optional KUnit suites for one format instantiation.

## Important APIs, Types, and Functions

- `PTPFX_RAW` and `PTPFX`: generated prefix names based on `PT_FMT` and optional `PT_FMT_VARIANT`.
- Includes `PTFVMOD(PT_FMT, h)`: the selected format header.
- Includes `../iommu_pt.h`: shared map/unmap/init/deinit implementation.
- Under `GENERIC_PT_KUNIT`, includes `../kunit_generic_pt.h` and `../kunit_iommu_pt.h`.

## Control Flow

Wrapper `.c` files define `PT_FMT`, optional variants, and supported features, then include this file. The preprocessor constructs unique symbol prefixes and expands the same shared implementation for each format.

## State and Persistence Behavior

The file has no state but determines symbol names and which code is compiled into each object.

## Dependencies and Integration Points

It depends on the macro utilities in `linux/generic_pt/common.h`, format headers under `fmt/`, and KUnit headers when building test objects.

## Risks and Edge Cases

Preprocessor naming must avoid collisions between base formats and variants. Any wrapper missing `PT_FMT` or defining an inconsistent variant will fail or generate wrong symbol names.

## Test Signals

Build all wrappers together, including `iommu_mock.c`, and verify distinct exported symbols and distinct KUnit suite names for each instantiation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/generic_pt/fmt/iommu_template.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/generic_pt/fmt/iommu_vtdss.c -->
# sources/distributed-fs/ceph-client/drivers/iommu/generic_pt/fmt/iommu_vtdss.c

## Purpose

`iommu_vtdss.c` instantiates the Generic PT IOMMU template for Intel VT-d second-stage page tables.

## Important APIs, Types, and Functions

- `#define PT_FMT vtdss`: selects `fmt/vtdss.h`.
- `PT_SUPPORTED_FEATURES`: enables VT-d second-stage force-coherence, force-writeable erratum handling, and DMA-incoherent handling.
- Inclusion of `iommu_template.h`: generates VT-d second-stage operations.

## Control Flow

The wrapper delegates all runtime behavior to generated template code. The selected features affect protection conversion and cache-maintenance behavior during mapping.

## State and Persistence Behavior

State is in generated `pt_iommu_vtdss` objects and VT-d second-stage PTE tables. Force-writeable and force-coherence features alter descriptor bits, not separate state.

## Dependencies and Integration Points

It is selected by Intel IOMMU support and used for nested/second-stage translation roots.

## Risks and Edge Cases

The force-writeable feature rejects read-only mappings for erratum-sensitive parent domains. DMA-incoherent support requires a valid IOMMU device in the generated table.

## Test Signals

KUnit should cover 3-, 4-, and 5-level tables, read-only rejection when force-writeable is active, dirty tracking, and hardware-info `ssptptr/aw` output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/generic_pt/fmt/iommu_vtdss.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/generic_pt/fmt/iommu_x86_64.c -->
# sources/distributed-fs/ceph-client/drivers/iommu/generic_pt/fmt/iommu_x86_64.c

## Purpose

`iommu_x86_64.c` instantiates the Generic PT IOMMU template for x86-64 style 4- and 5-level page tables.

## Important APIs, Types, and Functions

- `#define PT_FMT x86_64`: selects the x86-64 format header.
- `PT_SUPPORTED_FEATURES`: enables sign-extension, AMD table encryption, dynamic top growth, and DMA-incoherent handling.
- Inclusion of `iommu_template.h`: generates x86-64 namespaced operations.

## Control Flow

Runtime behavior is generated by `iommu_pt.h` and `x86_64.h`. The feature set controls whether top levels can grow dynamically, whether upper/lower sign-extended ranges are accepted, and whether SME bits are applied.

## State and Persistence Behavior

State is held in generated `pt_iommu_x86_64` containers and x86 PTE memory. Dynamic top changes can update the root table pointer through driver callbacks.

## Dependencies and Integration Points

It is selected by Intel IOMMU Kconfig and can support AMD/VT-d first-stage style page-table users.

## Risks and Edge Cases

Sign-extension cannot coexist with dynamic top or full-VA mode. AMD encryption behavior is feature-driven and must align with hardware context.

## Test Signals

KUnit should cover 4-level and 5-level sign-extended configurations, non-sign-extended AMD PASID-0 configurations, dynamic-top growth, and encrypted table/leaf encoding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/generic_pt/fmt/iommu_x86_64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/generic_pt/fmt/riscv.h -->
# sources/distributed-fs/ceph-client/drivers/iommu/generic_pt/fmt/riscv.h

## Purpose

`riscv.h` implements the Generic PT format callbacks for RISC-V page tables, including Sv39/Sv48/Sv57 64-bit roots and optional Svnapot 64 KiB contiguous mappings.

## Important APIs, Types, and Functions

- Format constants for entry size, max VA/OA, granule, table size, top physical mask, and max top level.
- RISC-V PTE bits: V/R/W/X/U/G/A/D/RSW, PPN fields, PBMT, and NAPOT bit.
- `riscvpt_table_pa`, `riscvpt_entry_oa`, `riscvpt_entry_num_contig_lg2`, `riscvpt_contig_count_lg2`.
- `riscvpt_load_entry_raw`: classifies invalid, table, and leaf entries.
- `riscvpt_install_leaf_entry` and `riscvpt_install_table`: write PTEs and table pointers.
- `riscvpt_iommu_set_prot`: converts IOMMU protection flags to RISC-V R/W/X/A/D/U bits.
- `riscvpt_iommu_fmt_init` and `riscvpt_iommu_fmt_hw_info`: choose Sv mode and export root PPN/mode.

## Control Flow

The generated Generic PT mapper calls RISC-V callbacks for descriptor operations. Leaves are valid if any R/W/X bit is set or at level 0. Non-leaf tables are valid entries without R/W/X. Svnapot 64 KiB mappings write a run of level-0 entries with the N bit and 64 KiB PPN encoding.

## State and Persistence Behavior

Translation state is stored in RISC-V PTEs. The format does not implement dirty helper callbacks for Generic PT dirty tracking even though it sets A/D bits for mappings; dirty behavior is descriptor-level, not exported through `read_and_clear_dirty`.

## Dependencies and Integration Points

It depends on `defs_riscv.h`, Generic PT helpers, Linux bitfield/log2 APIs, and RISC-V IOMMU hardware consumers that need `iosatp`-style root fields.

## Risks and Edge Cases

- `riscvpt_install_leaf_entry` has a FIXME asking whether a RISC-V leaf write needs `cmpxchg`.
- Svnapot support is only valid for 64-bit level-0 entries and must be feature-gated.
- Protection conversion rejects mappings with no R/W/X permission; callers must request a supported combination.
- `riscvpt_num_items_lg2` uses `sizeof(u64)` even though the header has a 32-bit conditional type branch.

## Test Signals

Run KUnit across Sv39/Sv48/Sv57, upper sign-extended ranges, Svnapot 64 KiB entries, permission combinations including `IOMMU_NOEXEC`, table-pointer encode/decode, and hardware-info mode values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/generic_pt/fmt/riscv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/generic_pt/fmt/vtdss.h -->
# sources/distributed-fs/ceph-client/drivers/iommu/generic_pt/fmt/vtdss.h

## Purpose

`vtdss.h` implements Generic PT callbacks for Intel VT-d second-stage 3-, 4-, and 5-level page tables.

## Important APIs, Types, and Functions

- Format constants: 52-bit output, 57-bit VA, 4 KiB granule/table memory, 64-bit entries, top level up to 4.
- Descriptor bits: R/W, A/D, SNP, output address, and page-size `PS`.
- `vtdss_pt_table_pa`, `vtdss_pt_entry_oa`, `vtdss_pt_can_have_leaf`, `vtdss_pt_load_entry_raw`.
- `vtdss_pt_install_leaf_entry`, `vtdss_pt_install_table`, `vtdss_pt_attr_from_entry`.
- Dirty helpers and software-bit helpers for ignored descriptor bits.
- `vtdss_pt_iommu_set_prot`, `vtdss_pt_iommu_fmt_init`, `vtdss_pt_iommu_fmt_hw_info`.

## Control Flow

Entries with neither R nor W are empty. Level 0 entries are leaves; levels 1 and 2 can be leaves when `PS` is set; higher levels are table-only. Mapping protection sets R/W and optionally SNP for forced coherence. The force-writeable feature rejects read-only mappings for nested-parent domains affected by an erratum.

## State and Persistence Behavior

Translations are stored in second-stage PTEs. Dirty state uses the VT-d D bit and Generic PT can clear or set it atomically. Software bits are stored in ignored descriptor positions for DMA-incoherent table-flush markers.

## Dependencies and Integration Points

The format is consumed by Intel IOMMU nested translation code through generated `pt_iommu_vtdss_*` APIs. It depends on Generic PT common/template headers and Linux bitfield helpers.

## Risks and Edge Cases

- VT-d second-stage has no independent present bit, so descriptor classification depends on R/W bits.
- Force-writeable domains intentionally reject read-only mappings and log a rate-limited erratum message.
- Software-bit allocation must avoid bits with architectural meaning across all entry levels.
- Dirty clearing requires a following IOTLB flush to synchronize hardware writes.

## Test Signals

KUnit should verify 3/4/5-level roots, 4 KiB/2 MiB/1 GiB mappings, dirty read/clear, force-coherence SNP bit, force-writeable rejection, software-bit operations, and hardware-info address-width encoding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/generic_pt/fmt/vtdss.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/generic_pt/fmt/x86_64.h -->
# sources/distributed-fs/ceph-client/drivers/iommu/generic_pt/fmt/x86_64.h

## Purpose

`x86_64.h` implements Generic PT callbacks for x86-compatible 4- and 5-level page tables used by CPUs and IOMMU first-stage contexts.

## Important APIs, Types, and Functions

- Format constants: 52-bit output, 57-bit VA, 4 KiB granule/table memory, 64-bit entries.
- Descriptor bits: present, RW, user, accessed, dirty, output address, execute-disable, and page-size.
- `x86_64_pt_table_pa`, `x86_64_pt_entry_oa`, `x86_64_pt_can_have_leaf`, `x86_64_pt_load_entry_raw`.
- `x86_64_pt_install_leaf_entry`, `x86_64_pt_install_table`, `x86_64_pt_attr_from_entry`.
- `x86_64_pt_sw_bit`: maps Generic PT software bits to ignored/available PTE bits.
- `x86_64_pt_iommu_set_prot`, `x86_64_pt_iommu_fmt_init`, `x86_64_pt_iommu_fmt_hw_info`.

## Control Flow

PTEs are empty if not present. Level 0 is always a leaf; levels 1 and 2 can be large leaves when `PS` is set; upper levels are tables. Table entries are installed atomically with present/RW/user/accessed bits. Leaf protection sets user/accessed, sets RW/dirty for writable mappings, and optionally applies SME encryption bits.

## State and Persistence Behavior

Page-table state persists in x86 PTE memory. This format does not implement Generic PT dirty callbacks despite encoding the D bit on writable mappings. Software bits support Generic PT internal synchronization markers.

## Dependencies and Integration Points

It depends on `defs_x86_64.h`, Generic PT helpers, Linux bitfield/log2 helpers, and SME encryption helpers. It integrates with Intel and AMD IOMMU first-stage or guest-translation users.

## Risks and Edge Cases

- `IOMMU_READ` is not explicitly encoded; present plus format semantics imply readability, while write controls RW/D.
- SME encryption is feature-driven and skipped for `IOMMU_MMIO`.
- Sign-extension and dynamic-top feature combinations must be validated by shared init code.
- Software-bit placement must remain safe across CPU and IOMMU interpretations.

## Test Signals

KUnit should cover 4- and 5-level tables, sign-extended upper/lower ranges, large pages, AMD non-sign-extended configurations, encrypted tables/leaves, software-bit operations, and hardware-info root/level fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/generic_pt/fmt/x86_64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/generic_pt/iommu_pt.h -->
# sources/distributed-fs/ceph-client/drivers/iommu/generic_pt/iommu_pt.h

## Purpose

`iommu_pt.h` is the shared template implementation that turns a Generic PT format into Linux `iommu_domain` page-table operations. It implements IOVA-to-physical lookup, mapping, unmapping, dirty tracking, table allocation/freeing, dynamic top growth, DMA-incoherent table cache maintenance, and initialization/deinitialization.

## Important APIs, Types, and Functions

- Generated namespace macros such as `DOMAIN_NS` and `NS`.
- Range validation helpers `make_range_ul`, `make_range_u64`, and `make_range`.
- Lookup walker `__iova_to_phys` and exported `DOMAIN_NS(iova_to_phys)`.
- Dirty walker `DOMAIN_NS(read_and_clear_dirty)` and test-only `set_dirty`.
- Table lifecycle helpers `_table_alloc`, `table_alloc_top`, `pt_iommu_new_table`, `__collect_tables`, and `NS(deinit)`.
- Mapping path: `compute_best_pgsize`, `clear_contig`, `__map_range_leaf`, `__map_range`, `__map_single_page`, `increase_top`, `check_map_range`, `NS(map_range)`.
- Unmapping path: `__unmap_range`, `NS(unmap_range)`, and `gather_range_pages`.
- Initialization: `pt_init_common`, `pt_iommu_init_domain`, `pt_iommu_zero`, generated `pt_iommu_init`, and optional hardware-info export.

## Control Flow

Generated `map_range` validates permissions, output-address limits, and IOVA ranges, computes the best page size, grows the root if `PT_FEAT_DYNAMIC_TOP` requires it, then either uses a single-page fast path or recursive mapping walkers. Mapping allocates lower tables atomically and can replace empty table subtrees with larger leaves only after ensuring no existing mappings are present. Unmap recursively clears leaves, frees fully covered lower tables, records the unmapped byte count, and moves freed tables to the IOTLB gather list. Dirty read walks mapped leaves, records dirty IOVAs, optionally clears dirty bits, and schedules IOTLB ranges.

## State and Persistence Behavior

Persistent state is in `struct pt_iommu`, format-specific `pt_common`, the root pointer encoded in `top_of_table`, and allocated page-table pages. Dynamic top updates use driver-provided locking and `change_top` callbacks. Freed page-table pages are delayed through `iommu_iotlb_gather`. DMA-incoherent formats use page-list start/stop and targeted flushes; a software bit marks table pointers whose cache flush has completed.

## Dependencies and Integration Points

This template depends on `pt_iter.h`, format callbacks from `pt_common.h`, Linux IOMMU APIs, `iommu-pages.h`, dirty bitmap APIs, and driver callbacks for dynamic top. Wrapper files compile it once per format and export symbols in `GENERIC_PT_IOMMU`.

## Risks and Edge Cases

- Correctness depends on format callbacks obeying atomic table-install, alignment, and descriptor-classification contracts.
- Partial unmap of a large leaf unmaps the whole leaf and returns that size, matching current IOMMU API expectations but surprising for older split-map assumptions.
- Dynamic top readers are lockless, so `top_of_table` pointer/level packing and hardware `change_top` ordering are critical.
- DMA-incoherent table updates rely on software-bit acquire/release and cache flush ordering.
- `DOMAIN_NS(iova_to_phys)` returns negative range errors cast as `phys_addr_t` for invalid range before later returning 0 on walk miss.

## Test Signals

KUnit should exercise map/unmap across all page sizes, table-to-leaf replacement, dynamic top growth, disjoint gather behavior, DMA-incoherent cache flushes, dirty read/clear, failed overmaps, malformed ranges, deinit leak checks, and 32-bit host truncation paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/generic_pt/iommu_pt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/generic_pt/kunit_generic_pt.h -->
# sources/distributed-fs/ceph-client/drivers/iommu/generic_pt/kunit_generic_pt.h

## Purpose

`kunit_generic_pt.h` defines format-level KUnit tests for Generic PT primitives, independent of higher-level IOMMU map/unmap behavior.

## Important APIs, Types, and Functions

- `do_map`, `KUNIT_ASSERT_PT_LOAD`, `check_all_levels`: shared test helpers.
- Bit/log tests: `test_bitops`, `test_best_pgsize`, `test_pgsz_count`.
- Format primitive tests: `test_table_ptr`, `test_table_radix`, `test_entry_possible_sizes`, `test_entry_oa`, `test_attr_from_entry`, and dirty tests.
- Uses generated format callbacks such as `pt_install_table`, `pt_table_pa`, `pt_possible_sizes`, `pt_install_leaf_entry`, `pt_attr_from_entry`, and dirty helpers.

## Control Flow

The header is included by `iommu_template.h` only for `GENERIC_PT_KUNIT` builds. Tests initialize a format-specific IOMMU table, map enough pages to populate levels, then use recursive Generic PT walkers to visit representative entries at each level and verify callback contracts.

## State and Persistence Behavior

State is per-KUnit fixture (`kunit_iommu_priv`) and temporary page-table mappings. Tests deliberately mutate entries, clear them, and rely on fixture teardown to deinitialize the generated table.

## Dependencies and Integration Points

It depends on `kunit_iommu.h`, `pt_iter.h`, generated format callbacks, Linux KUnit, and randomization helpers. It is compiled once per enabled format through the format Makefile.

## Risks and Edge Cases

- Tests are header-based template code, so failures can be format-specific and symbol-heavy.
- Some checks skip or adjust behavior on 32-bit hosts.
- The tests assume isolated KUnit execution for page-table leak accounting in the paired IOMMU test fixture.

## Test Signals

Passing suites indicate correct bit helpers, page-size selection, radix coverage, table pointer encode/decode, leaf OA encode/decode, attribute round-trip, dirty helper behavior, and format-supported page-size reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/generic_pt/kunit_generic_pt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/generic_pt/kunit_iommu.h -->
# sources/distributed-fs/ceph-client/drivers/iommu/generic_pt/kunit_iommu.h

## Purpose

`kunit_iommu.h` provides the shared KUnit fixture, generated-symbol declarations, domain ops, driver callbacks, assertions, and configuration setup used by Generic PT format and IOMMU tests.

## Important APIs, Types, and Functions

- Generated declarations for `pt_iommu_init` and `pt_iommu_table_cfg`.
- `kunit_pt_gen_params_cfg` and `KUNIT_CASE_FMT`: per-format parameterization.
- `struct kunit_iommu_priv`: union of `iommu_domain` and generated format table, dummy device, locks, config, info, page-size data, and leak baseline.
- `pt_kunit_iotlb_sync`: frees gather pages during tests.
- `kunit_pt_ops`: generated domain ops plus test sync callback.
- `pt_kunit_driver_ops`: no-op `change_top` and top-lock callback for dynamic top tests.
- `pt_kunit_priv_init`: builds a dummy device, initializes generated page table, and derives test limits.

## Control Flow

KUnit suites allocate `kunit_iommu_priv`, register a dummy device, set feature defaults or parameterized format config, initialize the generated page-table object, and then run tests through normal `iommu_map`, `iommu_unmap`, and callback APIs.

## State and Persistence Behavior

Fixture state persists for a test case and is cleaned by suite exit. `top_lock` serializes dynamic top updates. `orig_nr_secondary_pagetable` is used by `kunit_iommu_pt.h` teardown to detect page-table leaks.

## Dependencies and Integration Points

It depends on KUnit, `iommu-pages.h`, Generic PT headers, and generated format symbols. It provides a fake driver integration surface for `iommu_pt.h`.

## Risks and Edge Cases

- The no-op `change_top` is sufficient for software tests but does not model hardware root-update failures.
- 32-bit hosts require skipped or narrowed coverage because IOMMU APIs use `unsigned long`/`dma_addr_t` differently.
- Feature defaults are expanded under debug builds and may exercise combinations production wrappers do not request.

## Test Signals

Successful fixture initialization across all format parameter sets is the main signal. Failures often indicate invalid feature combinations, unsupported hardware limits, dummy-device allocation issues, or generated API signature drift.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/generic_pt/kunit_iommu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/generic_pt/kunit_iommu_pt.h -->
# sources/distributed-fs/ceph-client/drivers/iommu/generic_pt/kunit_iommu_pt.h

## Purpose

`kunit_iommu_pt.h` defines end-to-end KUnit tests for the generated Generic PT `iommu_domain` operations, focusing on map, unmap, lookup, dynamic top growth, large-page behavior, random overlap handling, and leak detection.

## Important APIs, Types, and Functions

- Counting helpers: `count_valids`, `count_valids_single`, and recursive `__count_valids`.
- Mapping helpers: `do_map`, `do_unmap`, `check_iova`.
- Tests: `test_increase_level`, `test_map_simple`, `test_map_table_to_oa`, `test_unmap_split`, `test_random_map`, `test_pgsize_boundary`, and `test_mixed`.
- Suite lifecycle: `pt_kunit_iommu_init`, `pt_kunit_iommu_exit`, and generated suite `NS(iommu_suite)`.

## Control Flow

The suite initializes a generated IOMMU table via `kunit_iommu.h`. Tests map every reported page size, verify IOVA-to-phys translations, unmap and check empty trees, convert populated lower tables into larger leaves, ensure partial unmap of a large page returns the large size, and perform randomized map/unmap with a maple tree tracking current mappings.

## State and Persistence Behavior

Each test mutates an in-memory page-table tree and cleans it before teardown. Teardown calls `pt_iommu_deinit` and compares `NR_SECONDARY_PAGETABLE` against the baseline to catch leaks.

## Dependencies and Integration Points

It uses Linux IOMMU API entry points, Generic PT walkers, KUnit, maple tree helpers, random helpers, and global VM page-state counters.

## Risks and Edge Cases

- Random tests are probabilistic and may miss rare ordering bugs without repeated runs.
- Some cases skip on 32-bit hosts or formats with insufficient page-size/range support.
- Leak checks assume isolated execution and stable `NR_SECONDARY_PAGETABLE` accounting.

## Test Signals

Passing tests validate generated domain ops for all enabled formats, including large-page selection, overmap rejection, table cleanup, top-level growth, translation correctness, and known regression cases referenced by `test_pgsize_boundary` and `test_mixed`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/generic_pt/kunit_iommu_pt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/generic_pt/pt_common.h -->
# sources/distributed-fs/ceph-client/drivers/iommu/generic_pt/pt_common.h

## Purpose

`pt_common.h` documents and declares the Generic PT format callback API, then layers common inline helpers on top of format-specific implementations and defaults.

## Important APIs, Types, and Functions

- Format callback contracts: `pt_attr_from_entry`, `pt_can_have_leaf`, `pt_clear_entries`, dirty helpers, `pt_entry_oa`, `pt_install_leaf_entry`, `pt_install_table`, `pt_load_entry_raw`, `pt_num_items_lg2`, `pt_possible_sizes`, `pt_table_pa`, and more.
- Derived helpers: `pt_entry_oa_lg2sz`, `pt_entry_oa_exact`, `pt_item_oa`, `pt_load_entry`, `pt_table_item_lg2sz`, `pt_table_oa_lg2sz`, `pt_table_ptr`, `pt_max_sw_bit`.
- Includes `pt_fmt_defaults.h` to supply missing optional callbacks.

## Control Flow

Format headers are included before this file and define macros mapping generic names to format-specific functions. `pt_common.h` then exposes a uniform API to walkers and IOMMU template code. `pt_load_entry` wraps raw entry loading and populates derived table pointers for table entries.

## State and Persistence Behavior

The helpers operate on `struct pt_common`, `struct pt_range`, and `struct pt_state` but do not own memory. They interpret current entry state and compute derived addresses, sizes, and capabilities.

## Dependencies and Integration Points

It depends on `pt_defs.h`, selected format headers, and `pt_fmt_defaults.h`. It is consumed by `pt_iter.h`, `iommu_pt.h`, and KUnit template headers.

## Risks and Edge Cases

- The callback API is macro-based; missing or incorrectly named format functions may silently fall back to defaults where that is not intended.
- Derived address helpers depend on correct contiguous-entry behavior from formats.
- Dirty and software-bit helpers may be absent depending on format support, changing generated IOMMU capabilities.

## Test Signals

`kunit_generic_pt.h` is the primary validation surface for callback contracts, including attribute round-trip, OA decode, page-size reporting, table pointer encode/decode, dirty helpers, and fallback defaults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/generic_pt/pt_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/generic_pt/pt_defs.h -->
# sources/distributed-fs/ceph-client/drivers/iommu/generic_pt/pt_defs.h

## Purpose

`pt_defs.h` provides the foundational Generic PT language, core types, feature gating, address arithmetic wrappers, atomic table-install helpers, top-table encoding, and debug assertion behavior.

## Important APIs, Types, and Functions

- Core types: `enum pt_entry_type`, `struct pt_range`, `struct pt_state`, and forward `struct pt_table_p`.
- Feature gates: `PT_SUPPORTED_FEATURES`, `PT_FORCE_ENABLED_FEATURES`, `pt_feature`, and `pts_feature`.
- Atomic install helpers: `pt_table_install64` and `pt_table_install32`.
- `PT_WARN_ON`: debug-only invariant reporting.
- VA/OA log2 arithmetic aliases and full-VA variants.
- Top pointer helpers: `_pt_top_set`, `pt_top_set`, `pt_top_set_level`, `pt_top_get_level`.

## Control Flow

Every format instantiation includes this before its format header and before `pt_common.h`. It normalizes feature availability, expands debug-mode feature matrices, and provides low-level helpers used by descriptor callbacks and walkers.

## State and Persistence Behavior

`struct pt_range` captures a snapshot of the root table pointer, top level, current VA interval, and maximum VA width. `struct pt_state` captures a walker position and loaded entry. `top_of_table` stores a pointer with low bits reserved for top-level encoding.

## Dependencies and Integration Points

It depends on `linux/generic_pt/common.h`, atomics, bit helpers, Kconfig, and `pt_log2.h`. It is the base include for all Generic PT implementation files.

## Risks and Edge Cases

- Pointer/level packing assumes table alignment leaves enough low bits for `PT_TOP_LEVEL_BITS`.
- Debug mode rewrites supported feature masks, so production and debug behavior can differ intentionally.
- `pt_table_install64` is unavailable under `CONFIG_GENERIC_ATOMIC64`, matching Kconfig restrictions.
- Full-VA helper variants are needed because shifting by the type width would be undefined.

## Test Signals

Build all formats in debug and non-debug modes. KUnit bitops and top-range tests validate arithmetic, feature handling, range construction, and atomic install assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/generic_pt/pt_defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/generic_pt/pt_fmt_defaults.h -->
# sources/distributed-fs/ceph-client/drivers/iommu/generic_pt/pt_fmt_defaults.h

## Purpose

`pt_fmt_defaults.h` supplies default Generic PT format callbacks for common radix geometry, no-contiguous mappings, no dirty tracking, OA/item conversion, max output address, system page-size support, entry clearing, software-bit helpers, and leaf argument validation.

## Important APIs, Types, and Functions

- Defaults for `pt_table_item_lg2sz`, `pt_pgsz_lg2_to_level`, `pt_entry_num_contig_lg2`, `pt_contig_count_lg2`, `pt_dirty_supported`, `pt_entry_make_write_dirty`, `pt_possible_sizes`, and `pt_full_va_prefix`.
- OA conversion helpers that derive `pt_item_oa` from `pt_entry_oa` or vice versa.
- `pt_clear_entries32`, `pt_clear_entries64`, and generic `pt_clear_entries`.
- Software-bit helpers `pt_test_sw_bit_acquire` and `pt_set_sw_bit_release` when a format defines `pt_sw_bit`; otherwise trap-like stubs call `__pt_no_sw_bit`.
- `pt_check_install_leaf_args`: shared validation for leaf alignment, size, and index alignment.

## Control Flow

After a format header defines its specialized callbacks, `pt_common.h` includes this file to fill gaps. Generic template code then calls the uniform callback names without caring whether the implementation is format-specific or default.

## State and Persistence Behavior

Defaults operate on current page-table memory through `pt_state`. Software-bit helpers update entries atomically and use acquire/release barriers for DMA-incoherent synchronization markers.

## Dependencies and Integration Points

It depends on `pt_defs.h`, Linux log2 helpers, and optional format-provided macros. All Generic PT formats transitively use at least some defaults.

## Risks and Edge Cases

- Fallbacks can hide a missing format implementation; tests must ensure defaults are intended.
- Software-bit stubs deliberately reference `__pt_no_sw_bit` so accidental use without format support fails at link/runtime.
- `pt_check_install_leaf_args` uses Generic PT invariants and cannot validate hardware-specific reserved-bit constraints.

## Test Signals

KUnit should cover formats relying on defaults and formats overriding them, especially page-size computation, entry clearing, software-bit synchronization, and invalid leaf-install arguments under debug checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/generic_pt/pt_fmt_defaults.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/generic_pt/pt_iter.h -->
# sources/distributed-fs/ceph-client/drivers/iommu/generic_pt/pt_iter.h

## Purpose

`pt_iter.h` implements Generic PT range construction, range validation, table index math, entry iteration, recursive walking, top/upper/all range helpers, page-size selection, and macro-generated inlined level walkers.

## Important APIs, Types, and Functions

- Range validation and conversion: `pt_check_range`, `pt_index_to_va`, `pt_range_to_index`, `pt_range_to_end_index`.
- Iteration primitives: `_pt_iter_first`, `_pt_iter_load`, `pt_next_entry`, `for_each_pt_level_entry`, `pt_load_single_entry`.
- Range constructors: `pt_top_range`, `pt_all_range`, `pt_upper_range`, `pt_make_range`, `pt_make_child_range`, `pt_range_slice`.
- Walker helpers: `pt_init`, `pt_init_top`, `pt_descend`, `pt_walk_range`, `pt_walk_descend`, `pt_walk_descend_all`.
- Geometry helpers: `pt_top_memsize_lg2`, `pt_compute_best_pgsize`, `pt_pgsz_count`.
- `PT_MAKE_LEVELS`: generates unrolled per-level walkers for performance.

## Control Flow

Callers build a `pt_range`, validate it, initialize a `pt_state`, then iterate entries in the current table level. Walkers recurse through `pt_descend` or `pt_walk_descend` and use `PT_MAKE_LEVELS` to let the compiler specialize each level as a constant. The map path uses page-size helpers to choose the largest valid leaf size constrained by VA/OA alignment, range length, and format page-size bitmap.

## State and Persistence Behavior

The file does not allocate or persist state. It mutates stack `pt_range` and `pt_state` objects during traversal, including lazily updating `range->va` to reflect current indexes.

## Dependencies and Integration Points

It depends on `pt_common.h` callback APIs and is used by `iommu_pt.h` and both KUnit headers. It is central to every generated format instance.

## Risks and Edge Cases

- Sign-extended formats require special lower/upper range handling; using `range->va` from `pt_all_range` during iteration is explicitly unsafe.
- Full-VA cases need `fvalog2_*` helpers to avoid undefined shifts.
- `pt_next_entry` must skip all items in contiguous leaves or walkers can double-count/clear entries.
- Generated level walkers produce larger code and require `PT_MAX_TOP_LEVEL <= 5`.

## Test Signals

KUnit validates range indexes, radix coverage, upper/lower sign-extended ranges, best page-size selection, page-size counts, contiguous iteration, and all generated walker levels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/generic_pt/pt_iter.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/generic_pt/pt_log2.h -->
# sources/distributed-fs/ceph-client/drivers/iommu/generic_pt/pt_log2.h

## Purpose

`pt_log2.h` provides type-generic helpers for power-of-two arithmetic used throughout Generic PT to avoid expensive or undefined divide/mod operations on large address types.

## Important APIs, Types, and Functions

- `log2_to_int_t`, `log2_to_max_int_t`, `log2_div_t`, `log2_div_eq_t`, `log2_mod_t`, `log2_mod_eq_max_t`, `log2_set_mod_t`, `log2_set_mod_max_t`, and `log2_mul_t`.
- Dispatch macro `_dispatch_sz` for 32-bit vs 64-bit bit operations.
- `fls_t`, `ffs_t`, and `ffz_t` wrappers with 32-bit and 64-bit implementations.
- Compile-time `static_assert` checks for basic arithmetic identities.

## Control Flow

The helpers are inline macros/functions used by range math, page-size selection, descriptor encoding, and tests. They operate on log2-encoded sizes rather than byte counts.

## State and Persistence Behavior

No state is stored. All operations are pure arithmetic.

## Dependencies and Integration Points

It depends on Linux bitops and limits headers and is included by `pt_defs.h`.

## Risks and Edge Cases

- Several helpers are undefined for zero inputs or shifts equal to the type width; higher-level full-VA wrappers handle those cases where needed.
- Macro arguments may be evaluated in expression contexts, so callers should avoid side-effect-heavy arguments.
- Correct type selection matters for 32-bit hosts and 64-bit address formats.

## Test Signals

`test_bitops` and page-size KUnit tests validate the helpers across 32-bit and 64-bit values, random low-bit patterns, and high page-size ranges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/generic_pt/pt_log2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/hyperv-iommu.c -->
# sources/distributed-fs/ceph-client/drivers/iommu/hyperv-iommu.c

## Purpose

`hyperv-iommu.c` is a stub IRQ-remapping driver for Hyper-V x86 systems. It creates an IRQ-remapping domain for the Hyper-V-emulated IO-APIC, constrains guest IO-APIC interrupt affinity when real remapping is unavailable, and provides a root-partition path that maps/unmaps IO-APIC interrupts through Hyper-V hypercalls.

## Important APIs, Types, and Functions

- `IOAPIC_REMAPPING_ENTRY`: 24 entries for the single exposed IO-APIC.
- Guest path: `hyperv_ir_set_affinity`, `hyperv_irq_remapping_alloc/free/select`, `hyperv_ir_domain_ops`.
- `hyperv_prepare_irq_remapping` and `hyperv_enable_irq_remapping`: exported via `hyperv_irq_remap_ops`.
- Root path: `struct hyperv_root_ir_data`, `hyperv_root_ir_compose_msi_msg`, `hyperv_root_ir_set_affinity`, `hyperv_root_irq_remapping_alloc/free`, `hyperv_root_ir_domain_ops`.

## Control Flow

Preparation only proceeds on Microsoft Hyper-V when extended destination IDs are unavailable. It creates a named IRQ-domain hierarchy under the architecture IRQ parent. Guests build an `ioapic_max_cpumask` of CPUs whose physical APIC IDs fit in 8 bits and enforce that mask on IO-APIC IRQ affinity. Root partitions use a different irq chip; composing an MSI message unmaps any previous Hyper-V IO-APIC interrupt, maps the new CPU/vector through `hv_map_ioapic_interrupt`, stores the returned entry, and translates its RTE into MSI message fields.

## State and Persistence Behavior

Guest state is the global `ioapic_max_cpumask` and `ioapic_ir_domain`. Root-partition state is per-IRQ `hyperv_root_ir_data`, including IO-APIC ID, trigger type, and last mapped Hyper-V interrupt entry. Freeing root IRQs unmaps any live Hyper-V mapping and releases the per-IRQ state.

## Dependencies and Integration Points

The file is compiled under `CONFIG_IRQ_REMAP` and integrates with x86 APIC/IO-APIC IRQ domains, Hyper-V detection and hypercalls, MSI message composition, vector cleanup, and the common `irq_remapping.h` operations table.

## Risks and Edge Cases

- Guest affinity is limited to CPUs with APIC IDs below 256; systems with sparse/high APIC IDs may reject requested masks.
- `hyperv_root_ir_compose_msi_msg` silently returns if `hv_map_ioapic_interrupt` fails, leaving the MSI message zeroed.
- Root compose chooses the first online CPU in the effective affinity mask; empty masks would be problematic.
- Domain creation assumes one Hyper-V IO-APIC with 24 entries.

## Test Signals

Boot Hyper-V guest and root-partition configurations with IRQ remapping enabled, exercise IO-APIC IRQ allocation/free, affinity changes across APIC-ID boundaries, xAPIC/x2APIC enable return modes, root hypercall map/unmap paths, and CPU hotplug or affinity updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/hyperv-iommu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/intel/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/iommu/intel/Kconfig

## Purpose

`intel/Kconfig` defines Intel VT-d/DMAR IOMMU support options, including base DMA remapping, debugfs, SVM, default enablement, scalable mode defaults, floppy workaround, and performance events.

## Important APIs, Types, and Functions

- `DMAR_TABLE`, `DMAR_PERF`, `DMAR_DEBUG`: internal feature symbols.
- `INTEL_IOMMU`: main Intel DMA-remapping option selecting IOMMU APIs, Generic PT, x86-64 and VT-d second-stage formats, IOVA, IOPF, PCI ATS/PRI/PASID, SWIOTLB, and related state.
- `INTEL_IOMMU_DEBUGFS`: exposes internals and selects debug/perf support.
- `INTEL_IOMMU_SVM`: Shared Virtual Memory support selecting MMU notifier and IOMMU SVA.
- `INTEL_IOMMU_DEFAULT_ON`, `INTEL_IOMMU_FLOPPY_WA`, `INTEL_IOMMU_SCALABLE_MODE_DEFAULT_ON`, `INTEL_IOMMU_PERF_EVENTS`.

## Control Flow

These symbols drive which Intel IOMMU source files and features are compiled. Enabling `INTEL_IOMMU` pulls in the Generic PT stack and PCI capabilities needed for modern VT-d operation. Nested/scalable features are controlled by additional booleans and runtime hardware detection.

## State and Persistence Behavior

No runtime state is stored here. Configuration choices affect boot defaults, feature availability, and built object files.

## Dependencies and Integration Points

The main option depends on `PCI_MSI`, `ACPI`, and `X86`, and integrates with the Generic PT Kconfig in this work item. The Makefile uses these symbols to include Intel IOMMU modules.

## Risks and Edge Cases

- Debugfs option warns it is not for production.
- Default-on and scalable-mode default-on alter boot behavior unless overridden by kernel command-line options.
- The floppy workaround creates identity mapping for legacy ISA DMA behavior.

## Test Signals

Build and boot matrices should include Intel IOMMU on/off/default-on, scalable mode on/off, SVM, debugfs, perf events, and Generic PT format selection. Runtime signals include DMAR ACPI parsing, device DMA translation, ATS/PRI/PASID setup, and perf/debugfs availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/intel/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/intel/Makefile -->
# sources/distributed-fs/ceph-client/drivers/iommu/intel/Makefile

## Purpose

The Intel IOMMU Makefile lists object files built for VT-d support and gates optional files by Kconfig symbols.

## Important APIs, Types, and Functions

- Core `obj-y`: `iommu.o`, `pasid.o`, `nested.o`, `cache.o`, and `prq.o`.
- `CONFIG_DMAR_TABLE`: adds `dmar.o` and `trace.o`.
- `CONFIG_DMAR_PERF`: adds `perf.o`.
- `CONFIG_INTEL_IOMMU_DEBUGFS`: adds `debugfs.o`.
- `CONFIG_INTEL_IOMMU_SVM`: adds `svm.o`.
- `CONFIG_IRQ_REMAP`: adds `irq_remapping.o`.
- `CONFIG_INTEL_IOMMU_PERF_EVENTS`: adds `perfmon.o`.

## Control Flow

Kbuild includes core Intel IOMMU code whenever the directory is selected, then adds optional features based on symbols from `intel/Kconfig` and common IRQ-remap config.

## State and Persistence Behavior

No runtime state exists. Build composition controls which runtime subsystems are present.

## Dependencies and Integration Points

It ties Intel IOMMU Kconfig symbols to source objects and ensures `cache.o`, the cache-tag implementation in this work item, is always part of the core Intel IOMMU build.

## Risks and Edge Cases

Object ordering can matter for initcall/link dependencies in built-in code. Optional trace/perf/debug files must only reference symbols available under their Kconfig gates.

## Test Signals

Run compile tests for minimal Intel IOMMU, with DMAR table parsing, debugfs, SVM, IRQ remapping, and perf events toggled individually and together.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/intel/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/intel/cache.c -->
# sources/distributed-fs/ceph-client/drivers/iommu/intel/cache.c

## Purpose

`intel/cache.c` manages Intel VT-d cache invalidation targets for domains. It tracks per-domain cache tags for IOTLB, device TLB, nested IOTLB, and nested device TLB associations, batches queued-invalidation descriptors by IOMMU unit, and provides range/full/non-present flush helpers for mapping changes.

## Important APIs, Types, and Functions

- `cache_tag_assign` / `cache_tag_unassign`: reference-counted cache-tag list management.
- `cache_tag_assign_domain` / `cache_tag_unassign_domain`: attach/detach cache tags for a domain, device, PASID, and nested parent domain.
- `domain_qi_batch_alloc`: lazy allocation of per-domain invalidation batch storage.
- `domain_get_id_for_dev`: resolves DID, with SVA using `FLPT_DEFAULT_DID`.
- `calculate_psi_aligned_address`: computes page-selective invalidation address/mask covering a range.
- Batch helpers: `qi_batch_flush_descs`, `qi_batch_add_iotlb`, `qi_batch_add_dev_iotlb`, `qi_batch_add_piotlb*`, `qi_batch_add_pasid_dev_iotlb`.
- Flush APIs: `cache_tag_flush_range`, `cache_tag_flush_all`, and `cache_tag_flush_range_np`.

## Control Flow

Assigning a domain lazily allocates `domain->qi_batch`, adds an IOTLB tag, and adds a device-TLB tag when ATS is enabled. Nested domains also assign cache tags to the stage-2 parent. Flush range computes a PSI-aligned address/mask, walks cache tags grouped by IOMMU, flushes queued descriptors when switching IOMMU units, emits IOTLB or device-TLB invalidations by tag type, and flushes the final batch. Non-present flushes either flush write buffers or IOTLBs depending on caching-mode and first-stage paging rules.

## State and Persistence Behavior

Each `dmar_domain` owns a `cache_tags` list protected by `cache_lock` and a reusable `qi_batch`. Tags are reference-counted with `users` so duplicate associations share invalidation targets. Tags persist until unassigned on detach. Batches are transient and reset after submission.

## Dependencies and Integration Points

The file depends on Intel IOMMU internals (`struct dmar_domain`, `struct intel_iommu`, `device_domain_info`), PASID helpers, queued invalidation descriptor builders, ATS metadata, tracepoints, and generic IOMMU dirty/map/unmap paths that call flush helpers.

## Risks and Edge Cases

- `cache_tage_match` appears misspelled but consistently used.
- Device-TLB invalidations are skipped when translation is disabled, per VT-d recommendation.
- Nested device-TLB flushes widen to full-device invalidation because affected nested translations cannot be precisely identified.
- `calculate_psi_aligned_address` must cover unaligned ranges without under-flushing; mask math is subtle.
- `cache_tag_assign` insertion groups tags by IOMMU for batching; list ordering bugs could reduce batching or mix descriptors.

## Test Signals

Test tag reference counting, ATS vs non-ATS devices, nested domain parent assignment rollback, SVA DID selection, PSI alignment for unaligned and full ranges, batching across multiple IOMMUs, queued-invalidation fallback paths, translation-disabled device-TLB skips, `dtlb_extra_inval`, and non-present flush behavior under caching mode and first-stage paging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/intel/cache.c -->
