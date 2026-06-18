# sources/distributed-fs/ceph-client/include/linux/kvm_types.h

Purpose: centralizes KVM scalar address types, forward declarations, export macros, generic stats structs, and small cache structures shared before `kvm_host.h` can be included.

Important APIs and types: address typedefs define `gva_t`, `gpa_t`, `gfn_t`, `hva_t`, `hpa_t`, `hfn_t`, and `kvm_pfn_t`; `INVALID_GPA` is the invalid sentinel. `struct gfn_to_hva_cache` caches guest-to-userspace translations by generation. `struct gfn_to_pfn_cache` caches GPA/HVA-to-PFN mappings with a list node, rwlock, refresh mutex, kernel mapping, active/valid flags, and owning VM. Optional `struct kvm_mmu_memory_cache` preallocates MMU objects. `KVM_STATS_NAME_SIZE`, `struct kvm_vm_stat_generic`, and `struct kvm_vcpu_stat_generic` define generic stats.

Control flow: low-level KVM and arch headers include this file to share type names without pulling the full host interface. Export macros conditionally expose symbols to `kvm` and configured submodules.

State and persistence: the declared cache structs hold in-memory acceleration state only; validity depends on memslot generations and MMU notifier invalidation. Stats are in-memory counters exposed through KVM stats infrastructure.

Dependencies and integration points: depends on arch `asm/kvm_types.h`, lock types, export machinery, and optional `KVM_ARCH_NR_OBJS_PER_MEMORY_CACHE`. It is included by KVM generic and arch code.

Risks and test signals: risks include width mismatch for guest physical types, stale cache validity rules, export visibility regressions when KVM is modular, and stats layout ABI drift. Test compile on multiple architectures, KVM module/submodule builds, gfn cache invalidation paths, and stats consumers.
