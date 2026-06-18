## `sources/distributed-fs/ceph-client/arch/x86/hyperv/ivm.c`

Purpose: Hyper-V isolated VM support for AMD SEV-SNP, Intel TDX, paravisor-mediated MSR/hypercalls, AP startup, and vTOM shared/private memory visibility.

Important APIs and functions: SNP/paravisor functions include `hv_ghcb_hypercall()`, `hv_ghcb_negotiate_protocol()`, `hv_ghcb_terminate()`, GHCB MSR read/write helpers, `hv_snp_boot_ap()`, and `hv_snp_hypercall()`. TDX functions include `hv_tdx_msr_read/write()` and `hv_tdx_hypercall()`. Shared wrappers are `hv_ivm_msr_read/write()`, `hv_vtom_init()`, `hv_get_isolation_type()`, `hv_is_isolation_supported()`, `hv_isolation_type_snp()`, and `hv_isolation_type_tdx()`.

Control flow: SNP paravisor paths use a per-CPU GHCB page, fill Hyper-V-specific hypercall fields, and execute `VMGEXIT`. Fully enlightened SNP AP boot constructs a VMSA, marks it as VMSA with `RMPADJUST`, and starts the VP. TDX paths use GHCI hypercalls for MSR and Hyper-V calls. vTOM initialization sets confidential-computing masks, adjusts physical address mask, installs encryption-status-change hooks, and forces WB MTRR state.

State and persistence: tracks GHCB protocol version, per-CPU VMSA pages, a global list of PFN regions made host-visible, static keys for isolation type, and platform encryption hooks. Hypervisor host-visibility state persists until reversed, especially around kexec/kdump.

Dependencies and integration points: AMD SEV/SNP GHCB, RMPADJUST, Intel TDX module calls, Hyper-V isolation fields, memory encryption APIs, x86 platform guest hooks, VMBus shared pages, IOAPIC/vTPM private MMIO, and kexec conversion stop hooks.

Risks: host visibility accounting must stay consistent on hypercall failures. Clearing PTE present bits avoids paravisor #VC/#VE issues during transitions but must always restore them. AP VMSA allocation has a potential leak path if VP index lookup fails after allocation. NMI use of GHCB hypercalls is warned against.

Test signals: SNP and TDX Hyper-V isolated boots, paravisor/no-paravisor hypercalls, AP startup, memory share/unshare with VMBus, kexec/kdump clearing host visibility, and static-key detection of isolation type.
