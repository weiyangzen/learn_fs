# sources/distributed-fs/ceph-client/arch/x86/kvm/debugfs.c

## Purpose

`debugfs.c` creates x86-specific KVM debugfs files for per-vCPU timing state and VM-level MMU reverse-map statistics. It is diagnostic-only and does not modify guest or host virtualization state.

## Important APIs, Types, And Functions

- `kvm_arch_create_vcpu_debugfs()`: creates `guest_mode`, `tsc-offset`, optional LAPIC timer advance, and optional TSC scaling files.
- `kvm_arch_create_vm_debugfs()`: creates `mmu_rmaps_stat`.
- Simple-attribute getters for timer advance, guest mode, TSC offset, TSC scaling ratio, and TSC scaling fractional bits.
- `kvm_mmu_rmaps_stat_show()`: seqfile histogram of rmap counts by page size.
- `kvm_mmu_rmaps_stat_open()` and `kvm_mmu_rmaps_stat_release()`: safe VM pin/release around seqfile lifetime.
- `mmu_rmaps_stat_fops`: VM debugfs file operations.

## Control Flow

Per-vCPU setup always creates `guest_mode` and `tsc-offset`, conditionally creates `lapic_timer_advance_ns` when the in-kernel LAPIC exists, and conditionally creates TSC scaling files when `kvm_caps.has_tsc_control` is true.

The rmap seqfile pins the VM, allocates one histogram per page size, locks `slots_lock` and `mmu_lock`, walks every address-space id and memslot, counts `pte_list_count()` for each rmap head, buckets counts logarithmically, prints a tabular report, frees temporary arrays, and drops the VM reference on release.

## State And Persistence

The file reads live fields from `struct kvm_vcpu`, `kvm_caps`, memslots, and MMU rmaps. It temporarily allocates histogram arrays per read and pins the VM only for the debugfs open lifetime. No persistent state is changed.

## Dependencies And Integration Points

It depends on Linux debugfs/seqfile infrastructure, KVM host data, LAPIC helpers, MMU internals, memslot iteration, and rmap helpers. The exported hook names are called by generic KVM debugfs setup.

## Risks And Maintenance Notes

- LAPIC timer state is read only when `lapic_in_kernel(vcpu)` caused the file to exist.
- `mmu_rmaps_stat` can be expensive on large VMs because it scans all rmap heads under MMU locking.
- Histogram overflow saturates into the last bucket with `WARN_ON_ONCE()`.
- Lock ordering must stay consistent with KVM MMU rules: slots lock before MMU lock here.

## Test Signals

Verify debugfs file presence under different LAPIC/TSC-scaling capabilities, read files while vCPUs run, read `mmu_rmaps_stat` with and without rmaps and large pages, and use lockdep/fault injection for concurrent teardown and allocation failures.
