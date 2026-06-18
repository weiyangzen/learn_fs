# sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_hv_nestedv2.c

## Purpose

`book3s_hv_nestedv2.c` implements the Book3S HV nested v2 guest-state-buffer interface used when this KVM instance itself runs as a nested guest under a parent hypervisor that supports `H_GUEST_*` hcalls. Instead of directly running L2 through the local real-mode path, it serializes selected vcpu and vcore state into guest state buffers, sends modified guest-wide state to L0, receives lazy state back from L0, and parses `H_GUEST_RUN_VCPU` output.

## Important APIs, Types, And Functions

The file exports the static key `__kvmhv_is_nestedv2`, plus `__kvmhv_nestedv2_mark_dirty()`, `__kvmhv_nestedv2_cached_reload()`, `kvmhv_nestedv2_flush_vcpu()`, `kvmhv_nestedv2_set_ptbl_entry()`, `kvmhv_nestedv2_set_vpa()`, `kvmhv_nestedv2_parse_output()`, `__kvmhv_nestedv2_reload_ptregs()`, `__kvmhv_nestedv2_mark_dirty_ptregs()`, `kvmhv_nestedv2_vcpu_create()`, and `kvmhv_nestedv2_vcpu_free()`.

Important local abstractions are `struct kvmppc_gs_msg_ops`, `struct kvmppc_gs_msg`, `struct kvmppc_gs_buff`, `struct kvmppc_gs_bitmap`, and `struct kvmhv_nestedv2_io`. `config_msg_ops` handles run input/output buffer configuration. `vcpu_message_ops` maps many `KVMPPC_GSID_*` identifiers to and from fields in `struct kvm_vcpu`, `struct pt_regs`, `vcpu->arch.shregs`, vector/floating state, performance counters, and `vcpu->arch.vcore`.

## Control Flow

`kvmhv_nestedv2_vcpu_create()` calls `plpar_guest_create_vcpu()` for the parent hypervisor and then `kvmhv_nestedv2_host_create()` to allocate and register nested v2 buffers. Host creation first queries `KVMPPC_GSID_RUN_OUTPUT_MIN_SIZE`, allocates an output buffer, sends its physical address and size to L0, builds a thread-wide `vcpu_message`, allocates a run input buffer sized from the serialized message, sends that input buffer to L0, then builds a guest-wide `vcore_message`. On success it fills `io->valids`, treating all state as initially cached locally.

Dirty and reload control is bitmap driven. `__kvmhv_nestedv2_mark_dirty()` includes a GSID in both vcpu and vcore messages and marks it valid locally. `__kvmhv_nestedv2_cached_reload()` only issues a receive hcall when the GSID is not valid in `io->valids`, using flags from `kvmppc_gsid_flags()` to request the correct scope. `kvmhv_nestedv2_flush_vcpu()` sends guest-wide dirty elements first, resets and fills the run input buffer with thread-wide dirty state, and always appends `KVMPPC_GSID_HDEC_EXPIRY_TB` for the requested run time limit.

`gs_msg_ops_vcpu_fill_info()` is the outbound serializer. It iterates requested GSIDs, skips entries whose requested wide/non-wide flag does not match the element scope, and writes scalar, GPR, SPR, vector, PMU, DEC expiry, TB offset, LPCR, VTB, DPDES, and logical PVR values. `gs_msg_ops_vcpu_refresh_info()` is the inbound parser. It parses a GSB into elements, writes recognized values into vcpu/vcore fields, and sets validity bits for each refreshed GSID. `kvmhv_nestedv2_parse_output()` clears fault/emulation defaults before parsing the output buffer so absent output fields do not preserve stale fault state.

Partition table updates use `kvmhv_nestedv2_set_ptbl_entry()`, which converts raw PATE doublewords into `kvmppc_gs_part_table` and `kvmppc_gs_proc_table` records and sends them wide to L0. VPA registration uses `kvmhv_nestedv2_set_vpa()` to send a `KVMPPC_GSID_VPA` datum through the run input buffer.

## State And Persistence Behavior

Persistent per-vcpu state lives in `vcpu->arch.nestedv2_io`: configuration records, input and output guest-state buffers, vcpu and vcore messages, and validity bits. The validity bitmap is a local cache contract: a set bit means local `vcpu->arch` has the current value; a clear bit lets accessors lazily fetch from L0. Dirty messages persist across changes until flushed. Buffer physical addresses and sizes are registered with L0 and must remain valid until `kvmhv_nestedv2_vcpu_free()`.

## Dependencies And Integration Points

This file is enabled by `kvmhv_nested_init()` after successful pseries capability negotiation. It integrates with inline accessors in `book3s_hv.h`, the nested vcpu run path in `book3s_hv.c`, VPA registration in the Book3S HV core, and partition-table updates from `book3s_hv_nested.c`. It depends heavily on `asm/guest-state-buffer.h` helpers for sizing, parsing, and sending GSB data, and on pseries `plpar_guest_create_vcpu()` and related GSB hcalls.

## Risks

The main risks are GSID coverage gaps, scope mismatches between thread-wide and guest-wide state, stale validity bits, and buffer lifetime errors. Missing a GSID in fill or refresh can produce state loss only under nested v2, which is hard to detect on bare metal. `gs_msg_ops_vcpu_get_size()` excludes host-wide and configuration elements; mistakes there can under-size buffers. Logical PVR defaults are synthesized from CPU features when `arch_compat` is zero, so compatibility tests should cover POWER9, POWER10, and POWER11 feature combinations. Error paths in host creation must free partially allocated messages and buffers without leaving L0 configured with freed addresses.

## Test Signals

Useful tests include nested v2 boot on pseries, vcpu create/free failure injection, dirty/reload accessors for GPRs, MSR, LPCR, PMU, vector, and DEC expiry GSIDs, VPA register/unregister, L2 exits that return HDAR/HDSISR/ASDR/HEIR, logical PVR propagation, partition/process table changes, and repeated vcpu run loops that verify no stale fault fields survive an output buffer that omits them.
