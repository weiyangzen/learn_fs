<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kvm/vmid.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kvm/vmid.c

## Purpose
`vmid.c` allocates and rolls RISC-V G-stage VMIDs for KVM guests so guest TLB entries can be tagged and invalidated safely.

## Important APIs, Types, And Functions
`kvm_riscv_gstage_vmid_detect()` probes hardware VMID width. `kvm_riscv_gstage_vmid_init()` initializes per-VM ids. `kvm_riscv_gstage_vmid_ver_changed()` checks version staleness. `kvm_riscv_gstage_vmid_update()` allocates or refreshes VMIDs and requests HGATP updates.

## Control Flow
Boot-time detection writes a max VMID into HGATP, reads back implemented bits, clears HGATP, and flushes guest TLBs. Update returns if VMID version is current; otherwise under `vmid_lock` it rechecks, rolls global version and flushes all CPUs when ids wrap, assigns the next VMID, stores the global version, and requests `KVM_REQ_UPDATE_HGATP` on all vCPUs.

## State And Persistence
Global state is `vmid_version`, `vmid_next`, `vmid_bits`, and `vmid_lock`. Per-VM state is `kvm->arch.vmid`. State is runtime only and recomputed across host boot.

## Dependencies And Integration Points
It depends on HGATP CSR access, G-stage mode selection, local hfence helpers, CPU masks, and KVM request delivery to vCPUs.

## Risks
VMID wrap requires global guest TLB flush and vCPU HGATP updates. Insufficient VMID bits disables tagging. Bit arithmetic around `(1 << vmid_bits)` must match supported widths.

## Test Signals
Stress many VMs/vCPUs to force VMID rollover, verify remote TLB flushes, and run guest memory isolation tests across VMID reuse.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kvm/vmid.c -->
