# Group Research: group_28_9front_sources_os_plan9_9front_sys_src_9_xen_xen_public_arch_x86_xen__58c6e0939bb7

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/arch-x86/xen-x86_64.h -->
# File Research: sources/os/plan9/9front/sys/src/9/xen/xen-public/arch-x86/xen-x86_64.h

Imported Xen public 64-bit x86 guest ABI header.

Purpose:
- Defines the 64-bit x86 Xen guest ABI: hypercall calling convention, segment selectors, hypervisor virtual windows, trap-return context, saved CPU registers, CR3/PFN helpers, VCPU arch info, and callback address type.

Key content:
- Documents x86-64 hypercall arguments in `%rdi`, `%rsi`, `%rdx`, `%r10`, `%r8`, `%r9`, return in `%rax`, via a hypercall page.
- Defines flat ring-3 selectors and aliases them for kernel/user selector constants.
- Defines hypervisor and machine-to-physical virtual address windows plus `machine_to_phys_mapping`.
- Defines `SEGBASE_*` constants for `HYPERVISOR_set_segment_base`.
- Defines `VGCF_in_syscall`, `struct iret_context`, and `struct cpu_user_regs` with 64-bit register layout and segment fields.
- Defines `xen_pfn_to_cr3`, `xen_cr3_to_pfn`, `struct arch_vcpu_info`, and `typedef unsigned long xen_callback_t`.

Integration:
- Included through `arch-x86/xen.h` when compiling for `__x86_64__`.
- Provides the ABI types used by callback, vCPU context, trap, and low-level hypercall code if this 9front Xen tree is built for 64-bit.

Risks/notes:
- Pure ABI surface; field layout, selector constants, and virtual address windows are not locally owned.
- Any divergence from Xen’s expected saved-register or callback type layout would break trap return, event delivery, and context setup.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/arch-x86/xen-x86_64.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/arch-x86/xen.h -->
# File Research: sources/os/plan9/9front/sys/src/9/xen/xen-public/arch-x86/xen.h

Imported Xen public common x86 guest ABI header.

Purpose:
- Provides x86-wide guest handle definitions, includes the correct 32/64-bit x86 ABI header, and defines shared x86 trap/vCPU/shared-info structures and constants.

Key content:
- Defines structural `XEN_GUEST_HANDLE` forms based on `__XEN_INTERFACE_VERSION__`.
- Selects `xen-x86_32.h` or `xen-x86_64.h` based on target architecture.
- Defines `xen_pfn_t`, `xen_ulong_t`, GDT reserved region constants, and `XEN_LEGACY_MAX_VCPUS`.
- Defines `struct trap_info` and helper macros for trap privilege and interrupt flags.
- Defines `struct vcpu_guest_context`, including FPU state, `VGCF_*` flags, CPU user registers, trap table, LDT/GDT, kernel stack, control/debug registers, callbacks, VM assist flags, and x86-64 segment bases.
- Defines `struct arch_shared_info` with max PFN, p2m list root, NMI reason, and padding.
- Defines `XEN_EMULATE_PREFIX` and `XEN_CPUID`.

Integration:
- Pulled in by compatibility wrappers `arch-x86_32.h` and `arch-x86_64.h`.
- The 9front Xen build’s `mkfile` includes x86 public headers when generating local Xen data/header material.
- Provides `vcpu_guest_context_t` and guest handles consumed by other public interfaces such as `domctl.h`.

Risks/notes:
- ABI-sensitive mixed 32/64 layout.
- Guest handle representation changes with interface version; generated headers and users must agree on `__XEN_INTERFACE_VERSION__`.
- Trap and vCPU context structures must match Xen exactly.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/arch-x86/xen.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/arch-x86_32.h -->
# File Research: sources/os/plan9/9front/sys/src/9/xen/xen-public/arch-x86_32.h

Imported Xen public 32-bit x86 compatibility include.

Purpose:
- Provides the legacy top-level 32-bit x86 public header path by including `arch-x86/xen.h`.

Key content:
- Contains license/comment header only, followed by `#include "arch-x86/xen.h"`.

Integration:
- The 9front Xen `mkfile` can choose this wrapper for older public-header layouts.
- The actual ABI definitions come from `arch-x86/xen.h` and its selected `xen-x86_32.h`.

Risks/notes:
- Small forwarding header, but include-path compatibility matters for generated Xen headers and source expecting the older public layout.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/arch-x86_32.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/arch-x86_64.h -->
# File Research: sources/os/plan9/9front/sys/src/9/xen/xen-public/arch-x86_64.h

Imported Xen public 64-bit x86 compatibility include plus legacy callback note.

Purpose:
- Provides the legacy top-level 64-bit x86 public header path by including `arch-x86/xen.h`.
- Documents the older `HYPERVISOR_set_callbacks` 64-bit behavior.

Key content:
- Includes `arch-x86/xen.h`.
- Documents event and failsafe callback registration arguments and notes that selectors are ignored on x86-64.

Integration:
- Used for source compatibility with older Xen public header paths.
- The real x86-64 ABI definitions come through `arch-x86/xen.h` and `arch-x86/xen-x86_64.h`.

Risks/notes:
- Mostly forwarding/documentation, but callback semantics are relevant to low-level trap setup.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/arch-x86_64.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/callback.h -->
# File Research: sources/os/plan9/9front/sys/src/9/xen/xen-public/callback.h

Imported Xen public callback registration ABI.

Purpose:
- Defines `callback_op` command IDs, callback types, flags, and register/unregister structures.

Key content:
- Defines callback types for event, failsafe, syscall, deprecated sysenter, NMI, sysenter, and syscall32.
- Defines `CALLBACKF_mask_events`.
- Defines `CALLBACKOP_register` with `struct callback_register { type, flags, xen_callback_t address }`.
- Defines `CALLBACKOP_unregister` with `struct callback_unregister`.
- Keeps older interface-version compatibility for `CALLBACKTYPE_sysenter`.

Integration:
- 9front currently uses the older `HYPERVISOR_set_callbacks` path in `trap.c` and low-level callback assembly, but this header supplies the newer public callback-op ABI.
- Depends on architecture-defined `xen_callback_t`.

Risks/notes:
- Callback address type is architecture-specific.
- Event masking semantics differ for event/NMI callbacks versus other callback types.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/callback.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/dom0_ops.h -->
# File Research: sources/os/plan9/9front/sys/src/9/xen/xen-public/dom0_ops.h

Imported Xen legacy dom0 compatibility ABI.

Purpose:
- Provides pre-`0x00030204` compatibility aliases from legacy `dom0_op` names to platform-operation names.

Key content:
- Errors out for newer interface versions because it is compatibility-only.
- Maps `DOM0_SETTIME`, memtype operations, microcode update, and platform quirks to `XENPF_*` equivalents.
- Defines legacy unsupported `DOM0_MSR` and `DOM0_PHYSICAL_MEMORY_MAP` structures for API compatibility.
- Defines `struct dom0_op` with command, interface version, and a 128-byte union payload.

Integration:
- Not part of the 9front guest’s runtime fast path.
- Vendored for Xen public header completeness and older control-stack compatibility.

Risks/notes:
- Deliberately version-gated legacy interface.
- Should not be used in new guest code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/dom0_ops.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/domctl.h -->
# File Research: sources/os/plan9/9front/sys/src/9/xen/xen-public/domctl.h

Imported Xen public domain-control ABI for node control tools.

Purpose:
- Defines the `domctl` hypercall command payloads used by Xen tools/control stacks for domain lifecycle, memory, vCPU, scheduler, device assignment, HVM state, memory events, sharing, debugging, and affinity.

Key content:
- Tools-only guard: errors unless compiling Xen or Xen tools.
- Defines `XEN_DOMCTL_INTERFACE_VERSION`.
- Provides domain creation and information structures, including HVM/HAP/S3/OOS flags and domain state flags.
- Defines memory list/page-frame info operations and page type/status constants.
- Defines shadow paging operations, dirty bitmap handling, and shadow memory allocation controls.
- Defines vCPU context/info, CPU/node affinity, scheduler parameters, domain handle/debugging, IRQ/I/O memory/I/O port permissions.
- Defines HVM context get/set/partial, address-size, real-mode area, triggers, PCI/device assignment, pass-through IRQs, memory and I/O port mappings.
- Defines CPUID, extended vCPU context/state, TSC info, mem-event, mem-sharing, audit, broken-page, and gdbsx debug structures.
- Ends with the main `struct xen_domctl` command union and command-number table.

Integration:
- Not compiled into normal 9front guest code because it is a control-tool interface.
- Other vendored Xen public headers, such as `sysctl.h`, depend on its types.
- Useful context for understanding the complete Xen ABI snapshot bundled under `xen-public`.

Risks/notes:
- Large, packed public control ABI with many version-sensitive fields.
- Includes HVM save-state and grant-table types; changes can ripple through tool builds.
- Not a filesystem/block path directly, except through domain/device/memory control semantics.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/domctl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/elfnote.h -->
# File Research: sources/os/plan9/9front/sys/src/9/xen/xen-public/elfnote.h

Imported Xen public ELF note definitions.

Purpose:
- Defines Xen-specific ELF note IDs used by Xen loaders, kernels, crash dumps, and dump-core tooling.

Key content:
- Documents PT_NOTE entries named `Xen`.
- Defines boot/kernel notes: info, entry, hypercall page, virtual base, physical-address offset, Xen version, guest OS/version, loader, PAE mode, feature strings, BSD symbol table, hypervisor start low, L1 MFN valid mask, suspend cancel, initial P2M location, module start PFN, supported feature bitmap.
- Defines `XEN_ELFNOTE_MAX`.
- Defines crash notes `XEN_ELFNOTE_CRASH_INFO` and `XEN_ELFNOTE_CRASH_REGS`.
- Defines dump-core notes for none/header/Xen version/format version.

Integration:
- Relevant to Xen boot image metadata rather than runtime I/O.
- Pairs with `features.h` for `XEN_ELFNOTE_FEATURES` and `XEN_ELFNOTE_SUPPORTED_FEATURES`.

Risks/notes:
- Loader-facing constants are ABI-stable; wrong note values can prevent boot or feature negotiation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/elfnote.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/event_channel.h -->
# File Research: sources/os/plan9/9front/sys/src/9/xen/xen-public/event_channel.h

Imported Xen public event-channel ABI.

Purpose:
- Defines Xen event-channel operations, port type, operation payloads, status values, and legacy compat wrapper.

Key content:
- Documents event channels as Xen’s notification/interrupt primitive with pending and mask bits in shared info/VCPU info.
- Defines `EVTCHNOP_*` commands: bind interdomain, bind virq, bind pirq, close, send, status, alloc unbound, bind ipi, bind vcpu, unmask, reset.
- Defines `evtchn_port_t`.
- Defines payload structures for allocation, interdomain binding, VIRQ/PIRQ/IPI binding, close, send, status, vCPU binding, unmask, and reset.
- Defines status constants for closed, unbound, interdomain, PIRQ, VIRQ, and IPI.
- Defines legacy `struct evtchn_op` for the older compat hypercall.

Integration:
- Directly used by 9front Xen event-channel allocation/notification paths in `xensystem.c`.
- Underpins xenstore, console, virtual block, and virtual network notification paths.
- `sdxen.c` and `etherxen.c` use event channels alongside rings and grant references.

Risks/notes:
- Event masking and pending-bit handling is interrupt-critical.
- Incorrect port binding or unmask behavior can cause lost device completions or stuck startup.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/event_channel.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/features.h -->
# File Research: sources/os/plan9/9front/sys/src/9/xen/xen-public/features.h

Imported Xen public feature flag definitions.

Purpose:
- Defines feature bits reported by `XENVER_get_features` and referenced by Xen ELF feature notes.

Key content:
- Defines feature names for writable page tables, writable descriptor tables, auto-translated physmap, supervisor-mode kernel, PAE page directories above 4GB, MMU update preserve A/D, highmem assist, grant-table map available bits, HVM callback vector, HVM safe pvclock, HVM PIRQs, and dom0 support.
- Defines `XENFEAT_NR_SUBMAPS`.

Integration:
- Included by `version.h` in this Xen public tree.
- Feature names are also referenced by `elfnote.h`.
- Relevant for guest boot/feature negotiation, though the visible 9front Xen guest code mostly uses fixed PV paths.

Risks/notes:
- Feature-bit interpretation is negotiated with Xen; assuming a feature without checking can break on older hosts.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/features.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/gcov.h -->
# File Research: sources/os/plan9/9front/sys/src/9/xen/xen-public/gcov.h

Imported Xen public coverage-data ABI.

Purpose:
- Defines Xen’s exported coverage blob tags and structures, distinct from GCC’s native gcov layout.

Key content:
- Defines coverage tag base, file/function/counter/end tags, counter count, and helper macros for counter tag recognition.
- Documents blob grammar: file records, counter records, function records, and terminator.
- Defines variable-length `xencov_file`, `xencov_counter`, `xencov_function`, `xencov_functions`, and `xencov_end`.

Integration:
- Not used by the 9front guest runtime.
- Vendored for Xen tooling/control completeness.

Risks/notes:
- Variable-length structure parsing requires respecting 8-byte alignment and tag ordering.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/gcov.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/grant_table.h -->
# File Research: sources/os/plan9/9front/sys/src/9/xen/xen-public/grant_table.h

Imported Xen public grant-table ABI.

Purpose:
- Defines Xen’s capability mechanism for sharing pages between domains and transferring page ownership, including grant table entries, operations, flags, handles, and status codes.

Key content:
- Documents grant tables as the memory-sharing foundation for split block and network drivers.
- Defines `grant_ref_t`, grant entry v1, reserved console/xenstore entries, grant types, permit-access flags, transfer flags, and v2 grant entries/status for newer interface versions.
- Defines grant-table hypercall operations: map, unmap, setup, dump, transfer, copy, query size, unmap-and-replace, set/get version, status frames, swap refs.
- Defines map/unmap/setup/transfer/copy/query/version/status structures and guest handles.
- Defines `GNTMAP_*` flags and grant status codes/messages.
- Documents concurrency rules for publishing, invalidating, and modifying grant entries.

Integration:
- Directly used by 9front’s `xengrant.c` to set up one grant-table frame and allocate/release grant references.
- Used by `sdxen.c` for block I/O buffers and by `etherxen.c` for network buffers through `blkif.h`/`netif.h`.
- Included by many I/O protocol headers.

Risks/notes:
- High-risk ABI area: incorrect memory barriers, stale grants, or releasing in-use grants can corrupt cross-domain I/O.
- 9front’s implementation currently maps one grant table frame; expansion requires matching mapping changes.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/grant_table.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/hvm/e820.h -->
# File Research: sources/os/plan9/9front/sys/src/9/xen/xen-public/hvm/e820.h

Imported Xen public HVM E820 layout constants.

Purpose:
- Defines fixed HVM guest physical locations for the E820 memory map and below-4GB RAM/MMIO split.

Key content:
- Defines `HVM_E820_PAGE`, E820 count offset, and E820 table offset.
- Defines `HVM_BELOW_4G_RAM_END`, `HVM_BELOW_4G_MMIO_START`, and MMIO length.

Integration:
- HVM-loader/device-model ABI context; not directly used by the visible 9front PV guest path.

Risks/notes:
- Constants are firmware/HVM memory-map ABI and must match Xen toolstack expectations.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/hvm/e820.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/hvm/hvm_info_table.h -->
# File Research: sources/os/plan9/9front/sys/src/9/xen/xen-public/hvm/hvm_info_table.h

Imported Xen public HVM information-table ABI.

Purpose:
- Defines the HVM info table placed in guest memory by the HVM domain builder.

Key content:
- Defines `HVM_INFO_PFN`, `HVM_INFO_OFFSET`, `HVM_INFO_PADDR`, and `HVM_MAX_VCPUS`.
- Defines `struct hvm_info_table` with signature, length, checksum, APIC mode, VCPU count, low/reserved/high memory boundaries, and boot-online VCPU bitmap.

Integration:
- HVM domain-builder/firmware ABI; not part of the current 9front PV block/net driver path.

Risks/notes:
- Structure layout and checksum semantics are boot ABI.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/hvm/hvm_info_table.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/hvm/hvm_op.h -->
# File Research: sources/os/plan9/9front/sys/src/9/xen/xen-public/hvm/hvm_op.h

Imported Xen public HVM operation ABI.

Purpose:
- Defines `hvm_op` command IDs and argument structures for HVM parameter access, interrupt routing, memory typing/access, time, tracing, trap injection, and MSI injection.

Key content:
- Defines `HVMOP_set_param`/`get_param` with `struct xen_hvm_param`.
- Defines PCI INTx, ISA IRQ, and PCI link route updates.
- Defines `HVMOP_flush_tlbs`.
- Defines HVM memory types `HVMMEM_ram_rw`, `HVMMEM_ram_ro`, and `HVMMEM_mmio_dm`.
- Under Xen/tools guards, defines dirty VRAM tracking, modified-memory notification, and memory type setting.
- Defines `HVMOP_pagetable_dying`, `HVMOP_get_time`, and `HVMOP_xentrace`.
- Under Xen/tools guards, defines memory access modes, get/set access operations, trap injection, and MSI injection.
- Defines `HVMOP_get_mem_type`.

Integration:
- HVM/device-model ABI context; not used by the visible 9front PV guest runtime.
- Included by `hvm/params.h`.

Risks/notes:
- Several interfaces are explicitly tools-only and may change.
- Memory access and trap injection semantics are security-sensitive in control stacks.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/hvm/hvm_op.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/hvm/hvm_xs_strings.h -->
# File Research: sources/os/plan9/9front/sys/src/9/xen/xen-public/hvm/hvm_xs_strings.h

Imported Xen public HVM xenstore key definitions.

Purpose:
- Defines xenstore string paths consumed by `hvmloader` for BIOS, ACPI, SMBIOS, generation ID, and related HVM firmware configuration.

Key content:
- Defines `hvmloader` root keys for BIOS choice, generation-id address, and memory relocation.
- Defines ACPI passthrough address/length keys.
- Defines SMBIOS passthrough address/length and default battery key.
- Defines BIOS/system/enclosure/battery string override keys and OEM string format.

Integration:
- HVM firmware/toolstack ABI only; not used by 9front’s PV xenstore client except as part of the vendored public header set.

Risks/notes:
- Xenstore key spelling is ABI; mismatches silently break firmware customization.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/hvm/hvm_xs_strings.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/hvm/ioreq.h -->
# File Research: sources/os/plan9/9front/sys/src/9/xen/xen-public/hvm/ioreq.h

Imported Xen public HVM I/O request ABI.

Purpose:
- Defines shared I/O request pages used between HVM guests, Xen, and device models.

Key content:
- Defines read/write directions, I/O request states, and I/O request types for PIO, MMIO copy, time offset, and invalidate.
- Defines `struct ioreq` with address, data, count, size, event-channel port, state, pointer/data direction flags, and type.
- Defines `struct shared_iopage` and buffered I/O request structures/ring.
- Defines legacy and modern ACPI PM/GPE I/O port locations and compatibility aliases.

Integration:
- HVM device-model ABI; not used by visible 9front PV block/net code.
- `hvm/params.h` references these ACPI location definitions.

Risks/notes:
- Bitfield layout and one-page buffered I/O structure size are ABI constraints.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/hvm/ioreq.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/hvm/params.h -->
# File Research: sources/os/plan9/9front/sys/src/9/xen/xen-public/hvm/params.h

Imported Xen public HVM parameter index definitions.

Purpose:
- Defines the HVM parameter namespace for `HVMOP_set_param` and `HVMOP_get_param`.

Key content:
- Defines callback IRQ delivery parameter and encoding.
- Defines xenstore PFN/event-channel convenience params, PAE, ioreq PFNs, buffered ioreq PFN/event channel, Viridian, timer mode, HPET, identity page table, device-model domain, ACPI S state, VM86 TSS, VPT alignment, console PFN/event channel, ACPI I/O port location, memory event params, nested HVM, mem-event ring PFNs, triple-fault reason, and `HVM_NR_PARAMS`.
- Defines virtual timer mode constants and memory-event mode flags.

Integration:
- HVM guest/device-model ABI; not on the visible 9front PV runtime path.
- Depends on `hvm_op.h` and references `features.h`/`ioreq.h` semantics.

Risks/notes:
- Parameter numbers are stable ABI; wrong indices affect guest boot, event delivery, xenstore, or device-model communication.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/hvm/params.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/hvm/pvdrivers.h -->
# File Research: sources/os/plan9/9front/sys/src/9/xen/xen-public/hvm/pvdrivers.h

Imported Xen public PV driver product registry.

Purpose:
- Defines a macro list of product IDs for HVM paravirtual driver packages.

Key content:
- Provides `PVDRIVERS_PRODUCT_LIST(EACH)` entries for xensource-windows, gplpv-windows, linux, and experimental.

Integration:
- HVM/PV-driver identification ABI; not directly used by 9front’s PV guest drivers.

Risks/notes:
- Registry values should not be invented locally; comments note product IDs should be allocated through Xen development process.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/hvm/pvdrivers.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/hvm/save.h -->
# File Research: sources/os/plan9/9front/sys/src/9/xen/xen-public/hvm/save.h

Imported Xen public HVM save/restore record framework.

Purpose:
- Defines generic HVM migration/save-state record descriptors and type macros, then includes architecture-specific HVM save records.

Key content:
- Documents strict 32/64-bit layout requirements: explicit sizes, natural alignment, and multiples of 8 bytes.
- Requires GNU anonymous structs/unions.
- Defines `struct hvm_save_descriptor` with typecode, instance, and payload length.
- Defines `DECLARE_HVM_SAVE_TYPE*` machinery and `HVM_SAVE_TYPE`, `HVM_SAVE_LENGTH`, `HVM_SAVE_CODE`.
- Defines terminator record `hvm_save_end`.
- Includes x86 or ARM architecture-specific HVM save header based on target architecture.

Integration:
- Used by `domctl.h` HVM context operations.
- Not used by the visible 9front PV guest runtime.

Risks/notes:
- Save/restore ABI is highly layout-sensitive.
- Requires architecture-specific companion headers to be present and compatible.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/hvm/save.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/io/blkif.h -->
# File Research: sources/os/plan9/9front/sys/src/9/xen/xen-public/io/blkif.h

Imported Xen public block frontend/backend protocol ABI.

Purpose:
- Defines the Xen split block-device protocol, including xenstore negotiation keys, state-machine documentation, request/response opcodes, scatter/gather segment layout, and ring type generation.

Key content:
- Documents notification hold-off using generic ring `req_event`/`rsp_event`.
- Defines `blkif_vdev_t` and `blkif_sector_t`.
- Thoroughly documents backend and frontend xenstore nodes: mode, params, type, barrier/flush/discard/persistent features, ring sizes, sector sizes, sectors, ring refs, protocol, and virtual device properties.
- Documents startup XenBus state transitions.
- Defines request opcodes for read, write, write barrier, flush disk cache, reserved command, and discard/secure discard.
- Defines `BLKIF_MAX_SEGMENTS_PER_REQUEST` as 11.
- Defines `struct blkif_request_segment`, `struct blkif_request`, `struct blkif_request_discard`, and `struct blkif_response`.
- Defines response statuses and `DEFINE_RING_TYPES(blkif, ...)`.
- Defines virtual disk flags for CD-ROM, removable, and readonly.

Integration:
- Directly used by 9front’s Xen block driver `sdxen.c`.
- Combines with `ring.h`, `grant_table.h`, xenstore keys, and event channels for virtual disk I/O.
- This is one of the most relevant files in the group for filesystem/block-storage research.

Risks/notes:
- Sector fields are in 512-byte units even when physical sector size differs.
- Grant references and ring producer/consumer ordering must be managed correctly.
- Feature negotiation is xenstore-string based; missing or stale keys can reduce functionality or break attach.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/io/blkif.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/io/console.h -->
# File Research: sources/os/plan9/9front/sys/src/9/xen/xen-public/io/console.h

Imported Xen public console ring ABI.

Purpose:
- Defines the shared-memory console interface used by Xen guest consoles.

Key content:
- Defines `XENCONS_RING_IDX`.
- Defines `MASK_XENCONS_IDX`.
- Defines `struct xencons_interface` with 1024-byte input ring, 2048-byte output ring, and consumer/producer indexes.

Integration:
- Directly used by 9front’s `uartxen.c` Xen console driver.
- Console ring is mapped from Xen start info and signalled via an event channel.

Risks/notes:
- Ring index masking assumes power-of-two ring array sizes.
- Producer/consumer ordering is essential to avoid lost console bytes.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/io/console.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/io/fbif.h -->
# File Research: sources/os/plan9/9front/sys/src/9/xen/xen-public/io/fbif.h

Imported Xen public virtual framebuffer protocol ABI.

Purpose:
- Defines the Xen virtual framebuffer shared page and in/out event formats.

Key content:
- Defines frontend-to-backend update and resize events.
- Defines backend-to-frontend refresh-period advice event.
- Defines fixed event sizes and shared-page ring offsets/macros.
- Defines `struct xenfb_page` with ring indexes, framebuffer dimensions, line length, memory length, depth, and framebuffer page directory.
- Defines default framebuffer dimensions under `__KERNEL__`.

Integration:
- Not used by the visible 9front Xen kernel drivers in the scan.
- Vendored for Xen public I/O protocol completeness.

Risks/notes:
- Shared-page layout and event sizes are fixed ABI.
- Uses `unsigned long` page directory entries, so ABI protocol selection matters across 32/64-bit peers.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/io/fbif.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/io/fsif.h -->
# File Research: sources/os/plan9/9front/sys/src/9/xen/xen-public/io/fsif.h

Imported Xen public filesystem split-driver protocol ABI.

Purpose:
- Defines an older Xen filesystem-level split device protocol over grant-backed rings.

Key content:
- Defines request types for open, close, read, write, stat, truncate, remove, rename, create, directory list, chmod, filesystem space, and sync.
- Defines per-operation request structures, many carrying grant references for paths or data buffers.
- Defines stat response layout and directory-list result bit masks.
- Defines `struct fsif_request`, `struct fsif_response`, fixed ring entry size, derived grant counts for read/write, and `DEFINE_RING_TYPES(fsif, ...)`.
- Defines string states `init`, `ready`, `closing`, and `closed`.

Integration:
- Not used by visible 9front Xen runtime code.
- Relevant to filesystem research as a vendored Xen FS protocol, but 9front’s active virtual storage path here is `blkif.h` via `sdxen.c`.

Risks/notes:
- Variable-length grant arrays are constrained by the fixed 64-byte ring entry size.
- Protocol is less central than blkif in this tree and may be legacy/unused.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/io/fsif.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/io/kbdif.h -->
# File Research: sources/os/plan9/9front/sys/src/9/xen/xen-public/io/kbdif.h

Imported Xen public virtual keyboard/mouse protocol ABI.

Purpose:
- Defines shared-page event formats for Xen virtual keyboard and pointer input.

Key content:
- Defines backend-to-frontend event types for motion, key, and absolute position.
- Defines `xenkbd_motion`, `xenkbd_key`, and `xenkbd_position`.
- Defines fixed in/out event sizes, ring sizes, offsets, and ring access macros.
- Defines `struct xenkbd_page` with in/out consumer/producer indexes.

Integration:
- Not used by visible 9front Xen kernel drivers in this subset.
- Vendored for Xen public I/O protocol completeness.

Risks/notes:
- Keycodes reference Linux input key definitions, which may not map directly to Plan 9 without translation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/io/kbdif.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/io/libxenvchan.h -->
# File Research: sources/os/plan9/9front/sys/src/9/xen/xen-public/io/libxenvchan.h

Imported Xen/Qubes-origin vchan shared-interface header.

Purpose:
- Defines the shared data structure for libxenvchan inter-domain communication over grant pages and event channels.

Key content:
- Uses LGPL license text, unlike many MIT-style Xen public headers.
- Explains that vchan uses a symmetric datagram-style ring interface with runtime-sized rings rather than `ring.h`’s fixed asymmetric macros.
- Defines `struct ring_shared` with consumer/producer indexes.
- Defines notify flags `VCHAN_NOTIFY_WRITE` and `VCHAN_NOTIFY_READ`.
- Defines `struct vchan_interface` with left/right rings, ring orders, client/server liveness, notify bits, and a flexible grant list.

Integration:
- Not used by visible 9front Xen runtime code.
- Vendored as part of the Xen public I/O ABI set.

Risks/notes:
- License differs from surrounding headers and should be tracked when redistributing.
- Runtime ring sizing and flexible grant list require careful bounds checks in implementations.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/io/libxenvchan.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/io/netif.h -->
# File Research: sources/os/plan9/9front/sys/src/9/xen/xen-public/io/netif.h

Imported Xen public network frontend/backend protocol ABI.

Purpose:
- Defines Xen split network-device rings, packet descriptors, checksum/offload flags, multicast/GSO extra info, and response codes.

Key content:
- Defines minimum slot support `XEN_NETIF_NR_SLOTS_MIN`.
- Documents notification behavior and split event-channel feature.
- Documents TX wire format for chained request descriptors and optional extra descriptors.
- Defines TX flags for checksum blank, data validated, more data, and extra info.
- Defines `struct netif_tx_request`, `struct netif_extra_info`, `struct netif_tx_response`, `struct netif_rx_request`, and `struct netif_rx_response`.
- Defines RX flags, GSO/multicast extra-info types, and response codes.
- Generates TX and RX ring types with `DEFINE_RING_TYPES`.

Integration:
- Directly used by 9front’s `etherxen.c` Xen network driver.
- Uses grant references for packet buffers and event channels for notifications.
- Shares `ring.h` ordering and notification rules with the block driver.

Risks/notes:
- Multi-slot packet and extra-info chains require careful validation to avoid malformed frontend/backend traffic.
- Offload flags must match packet contents; incorrect checksum flags can corrupt networking.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/io/netif.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/io/pciif.h -->
# File Research: sources/os/plan9/9front/sys/src/9/xen/xen-public/io/pciif.h

Imported Xen public PCI frontend/backend shared structure ABI.

Purpose:
- Defines shared structures and command codes for Xen PCI configuration, MSI/MSI-X, and PCIe AER frontend/backend operations.

Key content:
- Defines `XEN_PCI_MAGIC`.
- Defines shared-info flags for active frontend/backend and AER handler.
- Defines PCI operation codes for config read/write, MSI/MSI-X enable/disable, and AER actions.
- Defines PCI error codes.
- Defines `struct xen_msix_entry`, `struct xen_pci_op`, `struct xen_pcie_aer_op`, and `struct xen_pci_sharedinfo`.

Integration:
- Not used by visible 9front Xen runtime code.
- Vendored control/device protocol context for PCI passthrough.

Risks/notes:
- Large MSI-X entry array must fit expected shared page constraints.
- PCI passthrough operations are privilege/security sensitive.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/io/pciif.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/io/protocols.h -->
# File Research: sources/os/plan9/9front/sys/src/9/xen/xen-public/io/protocols.h

Imported Xen public I/O protocol ABI string definitions.

Purpose:
- Defines the xenstore protocol ABI strings used by split-device frontends/backends to agree on ring structure layout.

Key content:
- Defines ABI strings for x86_32, x86_64, and ARM.
- Defines `XEN_IO_PROTO_ABI_NATIVE` based on compile-time architecture.
- Emits a compile error for unsupported architectures.

Integration:
- Referenced by `blkif.h` xenstore protocol documentation.
- Important when front/back ends run with different machine ABIs.

Risks/notes:
- Protocol string mismatch causes peers to interpret ring structures incorrectly.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/io/protocols.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/io/ring.h -->
# File Research: sources/os/plan9/9front/sys/src/9/xen/xen-public/io/ring.h

Imported Xen public shared-ring macro framework.

Purpose:
- Defines generic producer/consumer ring types and manipulation macros used by Xen split device protocols.

Key content:
- Defines `RING_IDX` and helpers to round ring capacity down to a power of two.
- Defines `DEFINE_RING_TYPES` to generate shared ring, frontend ring, and backend ring structs.
- Defines shared/front/back initialization macros.
- Defines ring size/free/full/unconsumed checks and direct request/response element access.
- Defines overflow checks for request indexes.
- Defines push macros with memory barriers.
- Defines notification hold-off macros using `req_event` and `rsp_event`, including final checks before sleeping.

Integration:
- Directly used by `blkif.h`, `netif.h`, `fsif.h`, `usbif.h`, `vscsiif.h`, and `mem_event.h`.
- 9front’s `sdxen.c` and `etherxen.c` depend on these generated ring types and macros for block and network I/O.

Risks/notes:
- Explicitly provides no interlocks or flow control beyond the ring accounting; caller must enforce outstanding-request limits.
- Memory barriers are essential for cross-domain visibility.
- Ring sizes are power-of-two masked; corrupt producer indexes can cause overflow bugs if not checked.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/io/ring.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/io/tpmif.h -->
# File Research: sources/os/plan9/9front/sys/src/9/xen/xen-public/io/tpmif.h

Imported Xen public TPM/vTPM protocol ABI.

Purpose:
- Defines Xen TPM frontend/backend request structures, including older single-request ring and v2 shared-page state machine.

Key content:
- Defines `struct tpmif_tx_request`, one-entry TPM ring, and `tpmif_tx_interface`.
- Documents v2 passive TPM request/response behavior with submit/finish/cancel/idle state changes.
- Defines `enum tpmif_state`.
- Defines `struct tpmif_shared_page` with length, state, locality, extra page count, and flexible grant list.

Integration:
- Not used by visible 9front Xen runtime code.
- Vendored for Xen public device protocol completeness.

Risks/notes:
- Long TPM packets use extra grants that must be mapped contiguously by the backend.
- State transitions are asymmetric by design: frontend submits/cancels, backend idles/finishes.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/io/tpmif.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/io/usbif.h -->
# File Research: sources/os/plan9/9front/sys/src/9/xen/xen-public/io/usbif.h

Imported Xen public USB frontend/backend protocol ABI.

Purpose:
- Defines Xen USB request/response rings for URB submission/unlink and connection notifications.

Key content:
- Defines USB spec version enum.
- Documents USB pipe bit layout for port number, unlink/submit flag, direction, device address, endpoint, and pipe type.
- Defines helpers for pipe port/unlink bits.
- Defines `USBIF_MAX_SEGMENTS_PER_REQUEST`.
- Defines `usbif_request_segment`, `usbif_urb_request`, `usbif_urb_response`, and URB ring type.
- Defines connection request/response structures and connection ring type.
- Defines ring-size constants using `__CONST_RING_SIZE`.

Integration:
- Not used by visible 9front Xen runtime code.
- Depends on `ring.h` and grant references.

Risks/notes:
- Requires `PAGE_SIZE` to be defined by the including environment for ring-size constants.
- Complex URB/ISO fields need host USB semantics to implement correctly.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/io/usbif.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/io/vscsiif.h -->
# File Research: sources/os/plan9/9front/sys/src/9/xen/xen-public/io/vscsiif.h

Imported Xen public virtual SCSI frontend/backend protocol ABI.

Purpose:
- Defines Xen virtual SCSI request/response ring structures and scatter/gather segment layout.

Key content:
- Defines commands for SCSI CDB, abort, reset, and SG preset.
- Defines scatter/gather table size, max CDB size, and sense buffer size.
- Defines `vscsiif_segment_t`, `struct vscsiif_request`, `struct vscsiif_sg_list`, and `struct vscsiif_response`.
- Generates `vscsiif` ring types.

Integration:
- Not used by visible 9front Xen runtime code.
- Storage-related vendored protocol, but 9front’s active virtual storage code uses block `blkif`.

Risks/notes:
- Response includes large fixed reserved space and sense buffer; ABI size assumptions matter for ring layout.
- SG preset requires first fields to match main request layout.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/io/vscsiif.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/io/xenbus.h -->
# File Research: sources/os/plan9/9front/sys/src/9/xen/xen-public/io/xenbus.h

Imported Xen public XenBus state definitions.

Purpose:
- Defines the XenBus frontend/backend state machine enumeration.

Key content:
- Defines `enum xenbus_state`: unknown, initialising, init-wait, initialised, connected, closing, closed, reconfiguring, and reconfigured.
- Typedefs `XenbusState`.

Integration:
- Directly used by 9front’s xenstore/xenbus and virtual device setup paths.
- `sdxen.c` writes and waits on XenBus states while attaching virtual block devices.
- `blkif.h` documents the detailed block-device startup transitions using these states.

Risks/notes:
- State transition tolerance matters because peers may skip optional negotiation states.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/io/xenbus.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/io/xs_wire.h -->
# File Research: sources/os/plan9/9front/sys/src/9/xen/xen-public/io/xs_wire.h

Imported Xen public XenStore wire protocol ABI.

Purpose:
- Defines the socket/shared-ring protocol between XenStore daemon and client libraries or guest kernels.

Key content:
- Defines `enum xsd_sockmsg_type` for debug, directory, read/write, perms, watch/unwatch, transactions, introduce/release, domain path, mkdir/rm, watch event, error, resume, set target, restrict, and reset watches.
- Defines write mode strings.
- Optionally defines errno-to-string mapping table when errno constants are available.
- Defines `struct xsd_sockmsg` header with type, request ID, transaction ID, and payload length.
- Defines watch tuple type enum.
- Defines `XENSTORE_RING_SIZE`, ring index type/mask, and `struct xenstore_domain_interface` with request/response rings and producer/consumer indexes.
- Defines payload and path maximums.

Integration:
- Directly used by 9front’s `devxenstore.c` XenStore device/client implementation.
- XenStore is used by xenbus setup for block/network devices and shutdown watches.
- Mapped from Xen start info at the fixed `XENBUS` virtual address in this port.

Risks/notes:
- The comment warns that violating `XENSTORE_PAYLOAD_MAX` is severe.
- Concurrent request/response matching depends on request IDs and ring ordering.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/io/xs_wire.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/kexec.h -->
# File Research: sources/os/plan9/9front/sys/src/9/xen/xen-public/kexec.h

Imported Xen public kexec/kdump hypercall ABI.

Purpose:
- Defines Xen’s public kexec operation interface for dom0 reboot/crash-kernel loading and crash range discovery.

Key content:
- Documents three operation groups: range information, load/unload images, and executing a loaded image.
- Defines `KEXEC_XEN_NO_PAGES` for x86.
- Defines kexec types default and crash.
- Defines `xen_kexec_image_t` with page list, indirection page, and start address.
- Defines command IDs and structures for execute, load/unload, and get-range.
- Defines range IDs for crash area, Xen, CPU notes, xenheap, obsolete ia64 boot param, EFI memory map, and vmcoreinfo.

Integration:
- Dom0/control-plane ABI; not used by 9front’s guest block/network runtime.

Risks/notes:
- Machine-address ranges and crash-kernel paths are host/control-stack sensitive.
- x86 page-list count is fixed by ABI.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/kexec.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/mem_event.h -->
# File Research: sources/os/plan9/9front/sys/src/9/xen/xen-public/mem_event.h

Imported Xen public memory-event ring ABI.

Purpose:
- Defines common request/response structures for Xen memory event mechanisms such as paging, access violations, sharing, and introspection.

Key content:
- Includes `xen.h` and generic `io/ring.h`.
- Defines memory event flags for VCPU paused, drop page, eviction failure, foreign, and dummy.
- Defines memory event reasons for unknown, access violation, CR0, CR3, CR4, INT3, single-step, and MSR.
- Defines `mem_event_request_t`/`mem_event_response_t` with flags, VCPU ID, GFN, offset, guest linear address, p2m type, access bits, GLA validity, and reason.
- Generates `mem_event` ring types.

Integration:
- Used by `domctl.h` memory-event setup/control structures.
- Not used by visible 9front guest runtime.

Risks/notes:
- Blocking memory-event users can pause VCPUs pending response; incorrect handlers can deadlock guests.
- Bitfields and ring layout must match Xen/tool expectations.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/mem_event.h -->