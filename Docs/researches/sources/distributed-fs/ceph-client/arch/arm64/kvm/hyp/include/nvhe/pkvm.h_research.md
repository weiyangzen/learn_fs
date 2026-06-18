# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/include/nvhe/pkvm.h

## Purpose

This header defines protected KVM hyp-side VM/vCPU containers and declares pKVM VM lifecycle and protected guest trap interfaces.

## Important APIs, Types, And Functions

`struct pkvm_hyp_vcpu` embeds a trusted hyp `struct kvm_vcpu`, an untrusted host-vCPU backpointer, and loaded-vCPU tracking. `struct pkvm_hyp_vm` embeds a trusted `struct kvm`, host backpointer, guest stage-2 page table, pool, lock, and flexible vCPU array. APIs include VM table init/reserve/unreserve/init, vCPU init/load/put, VM lookup/refcount helpers, teardown/reclaim functions, and protected trap handlers.

## Control Flow

Host hypcalls reserve a VM handle, initialize hyp VM/vCPU copies, load a hyp vCPU for execution, then put it back. Teardown transitions through start/finalize phases and can reclaim dying guest pages.

## State And Persistence Behavior

Persistent trusted state is maintained entirely at hyp for protected VMs and vCPUs, with backpointers to untrusted host objects. The VM table is protected by `vm_table_lock`.

## Dependencies And Integration Points

It integrates with pKVM memory protection, hyp allocator, host hypcall dispatch, protected sysreg/HVC handling, and KVM protected VM feature checks.

## Risks And Test Signals

Risks are stale host backpointers, handle lifetime bugs, loaded-vCPU pointer leaks, guest page reclaim races, and untrusted host state confusion. Test signals are protected VM creation/destruction, vCPU load/put nesting, invalid handle rejection, and protected HVC/sysreg trap behavior.
