# sources/distributed-fs/ceph-client/arch/x86/include/asm/mshyperv.h

## Purpose
Declares x86 Microsoft Hyper-V integration: hypercall ABI helpers, isolation-type detection, VP assist pages, TLB flush hypercalls, APIC/MSI mapping, confidential VM hooks, VTL mode support, and synthetic MSR helpers.

## Important APIs, Types, And Functions
Important definitions include `HV_IOAPIC_BASE_ADDRESS`, VTL constants, `hyperv_fill_flush_list_func`, `hv_do_hypercall()`, `hv_do_fast_hypercall8()`, `hv_do_fast_hypercall16()`, `hv_get_vp_assist_page()`, `hyperv_init()`, `hyperv_setup_mmu_ops()`, TSC change callbacks, `hyperv_flush_guest_mapping*()`, `hv_create_pci_msi_domain()`, `hv_map_msi_interrupt()`, `hv_map_ioapic_interrupt()`, `hv_ghcb_*()`, `hv_vtom_init()`, `hv_ivm_msr_read/write()`, `hv_is_synic_msr()`, `hv_is_sint_msr()`, `hv_get_msr()`, `hv_set_msr()`, `hv_apicid_to_vp_index()`, `struct mshv_vtl_cpu_context`, and VTL return-call hooks.

## Control Flow
On 64-bit Hyper-V builds, hypercalls dispatch through a static call that selects standard, SNP, or TDX hypercall implementations. On 32-bit, inline assembly calls the hypercall page through `CALL_NOSPEC`. Fast hypercalls pass register operands without parameter pages. Disabled configs compile most operations to stubs returning failure or zero.

## State And Persistence
State includes hypercall page pointers, per-CPU GHCB pages, VP assist pages, isolation static keys, TSC callbacks, and VTL CPU context saved across secure returns. It persists for the running guest or root partition session only.

## Dependencies And Integration Points
Depends on Hyper-V HVDK ABI, x86 MSR and nospec helpers, MSI/IRQ domains, io access, FPU state, SEV-SNP, TDX, and generic Hyper-V code. It integrates with clock/TLB management, APIC, PCI MSI, crash dump, confidential VM boot, and VTL mode transitions.

## Risks And Edge Cases
Hypercall register ABI and physical address translation are critical. Isolation type must select the correct hypercall path. Disabled stubs must match callers' error expectations. VTL context layout must match assembly save/restore.

## Test Signals
Hyper-V guest boot, enlightened TLB flush tests, synthetic interrupt/MSI tests, SNP/TDX confidential guest boot, VTL mode tests, crash dump coverage, and non-Hyper-V build coverage are useful.
