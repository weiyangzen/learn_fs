# sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_hv.h

## Purpose

`book3s_hv.h` is the private header for Book3S HV KVM C and assembly support. It defines host SPR save state for POWER9-style entry paths, declares guest-state load/store and PMU switching helpers, provides timing macros, and generates nestedv2-aware vCPU register accessors that keep local cached state synchronized with the guest-state-buffer dirty/reload mechanism.

## Important APIs, Types, And Functions

`struct p9_host_os_sprs` holds host privileged non-hypervisor SPRs that must be saved across guest entry: IAMR, AMR, PMCs, MMCRs, MMCRA, SIAR, SIERs, and SDAR. `nesting_enabled()` returns true only when the VM requested nested virtualization and is using radix MMU.

The header declares `load_vcpu_state()`, `store_vcpu_state()`, `save_p9_host_os_sprs()`, `restore_p9_host_os_sprs()`, `switch_pmu_to_guest()`, and `switch_pmu_to_host()`, which are implemented elsewhere and used by the POWER9/nested entry paths.

When `CONFIG_KVM_BOOK3S_HV_P9_TIMING` is enabled, `accumulate_time()`, `start_timing()`, and `end_timing()` update timebase accumulators. Otherwise the macros compile to no-ops.

`__kvmppc_set_msr_hv()` and `__kvmppc_get_msr_hv()` directly access the shadow MSR and integrate with nestedv2 dirty/reload tracking. The `KVMPPC_BOOK3S_HV_VCPU_ACCESSOR*` macros generate typed get/set helpers for scalar and array vCPU fields, including MMCRA, HFSCR, FSCR, DSCR, PURR, SPURR, AMR, UAMOR, SIAR, SDAR, IAMR, DAWR/DAWRX, DEXCR, hash key registers, CIABR, WORT, PPR, CTRL, MMCR arrays, SIER arrays, PMC arrays, and PSPB.

## Control Flow

Callers use the generated setters when guest state changes locally; each setter stores the new value and marks the corresponding nestedv2 guest-state ID dirty. Generated getters request a cached reload for the guest-state ID before returning the local field; several use `WARN_ON()` if reload fails. This creates a uniform path for normal HV state access and nestedv2 state synchronization.

## State And Persistence Behavior

The header does not define persistent storage. It defines access patterns for runtime vCPU architectural state and host SPR save areas. Its main state effect is ensuring that state modified in the in-kernel cache is marked dirty for nestedv2 and that reads reload from nestedv2 buffers when needed.

## Dependencies And Integration Points

The file depends on `asm/guest-state-buffer.h` for `KVMPPC_GSID_*` identifiers and nestedv2 dirty/reload helpers. It is included by `book3s_hv.c`, `book3s_hv_builtin.c`, and related HV support code that needs consistent access to guest SPRs and timing helpers.

## Risks

Accessor macro mistakes can silently desynchronize nestedv2 guest state. A wrong GSID mapping, missing dirty mark, or missing reload can make L0/L1 see stale or incorrect registers. The accessors are inline and widely used, so changes have a broad blast radius. Host SPR save structure layout must stay consistent with assembly/C save and restore routines.

## Test Signals

Signals include nestedv2 guests preserving MSR, LPCR, PMU, debug, and facility state across entries; one-reg get/set behavior matching guest execution; no `WARN_ON()` reload failures; PMU counters switching cleanly between host and guest; and timing debugfs output compiling both with and without P9 timing enabled.
