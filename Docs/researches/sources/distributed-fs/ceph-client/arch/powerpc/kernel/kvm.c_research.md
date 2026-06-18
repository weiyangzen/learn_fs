
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/kvm.c

Purpose: boot-time KVM/ePAPR guest optimization for PowerPC kernels running under a paravirtualized host, replacing selected privileged SPR/MSR operations with faster magic-page memory accesses or nearby emulation trampolines.

Important APIs/types/functions: `kvm_guest_init`; `kvm_use_magic_page`; `kvm_map_magic_page`; `kvm_check_ins`; patch helpers `kvm_patch_ins_*`; trampoline builders for `mtmsrd`, `mtmsr`, BookE `wrtee/wrteei`, and Book3S 32-bit `mtsrin`; global `kvm_patching_worked`, `kvm_tmp`, and `kvm_tmp_index`.

Control flow: the postcore initcall exits unless KVM paravirt and ePAPR are enabled. If `KVM_FEATURE_MAGIC_PAGE` is present, every CPU asks the hypervisor to map the magic page at `-4096`, the kernel validates the mapping with `fault_in_readable`, disables local IRQs, scans `_stext` to `_etext`, skips the template range, and rewrites matching instructions. Simple reads/writes of MSR, SPRG, SRR, DAR/DEAR, DSISR, MAS, ESR, PIR, and segment-register state become loads/stores into `struct kvm_vcpu_arch_shared`. Instructions that need conditional interrupt semantics are replaced with branches into copied assembly templates stored in the 64 KiB `kvm_tmp` area.

State and persistence: changes are live kernel text patches and a fixed negative-address magic-page mapping supplied by the hypervisor. `kvm_tmp_index` consumes template space once during boot; `kvm_patching_worked` records failures for logging but does not roll back already-applied patches.

Dependencies and integration: depends on `kvm_para_available`, ePAPR hypercalls, `KVM_MAGIC_FEAT_*`, PowerPC opcode encodings, cache flushes after patching, and assembly labels exported by `kvm_emul.S`.

Risks: branch offsets are only checked against the positive maximum and depend on layout; relocatable Book3S interrupt handlers are intentionally skipped; partial success can leave mixed optimized/unoptimized text; IRQ disabling protects SPRG4-7 synchronization assumptions; scratch registers 30/31 require special magic-page save/restore handling.

Test signals: boot a PPC KVM guest with magic page enabled, check the "KVM: Live patching for a fast VM" log, verify no fault on `-4096`, compare instruction patch counts under BookE/Book3S configs, and run interrupt-heavy and TLB-heavy guest workloads.
