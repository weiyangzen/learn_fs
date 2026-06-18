# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/amx_test.c

## Purpose
This x86_64 KVM selftest validates AMX tile state virtualization, including XFD-triggered `#NM`, XTILEDATA save/restore, `KVM_GET_XSAVE`/`KVM_SET_XSAVE`, and full VM state recreation.

## Important APIs, Types, And Functions
It requires XSAVE, OSXSAVE, XFD, AMX_TILE, XTILECFG, XTILEDATA, and XTILEDATA_XFD. It uses `vm_xsave_require_permission()`, CPUID property helpers, `wrmsr()`/`rdmsr()` for `MSR_IA32_XFD` and `MSR_IA32_XFD_ERR`, AMX instruction encodings for `ldtilecfg`, `tileloadd`, `tilerelease`, `xsavec`, `vcpu_save_state()`, `vcpu_xsave_set()`, `vcpu_load_state()`, and VM recreation helpers. Guest data structures model tile config, tile data, and XSAVE state.

## Control Flow
The host enables AMX permissions, creates a VM, allocates guest tile config/data/XSAVE buffers, and loops over guest ucalls. The guest checks tile CPUID properties, enables AMX by clearing XFD, loads tile config/data, syncs for host save/compare, disables tiledata via XFD, lets host attempt restore, tests XSAVEC compacted tile metadata, triggers a safe `tileloadd` expecting `NM_VECTOR`, checks XFD_ERR, clears XFD, reloads tile data, and exits. Host sync handling saves tile state, compares TMM0 bytes with guest data, restores saved XSAVE state, and repeatedly saves/recreates the VM to validate full state persistence.

## State, Dependencies, And Integration
State includes allocated guest AMX buffers, `tile_state` saved by KVM, full `kvm_x86_state` snapshots, and AMX-related MSRs. The test depends on host kernel AMX permission support and correct CPUID property enumeration. No persistent files are used.

## Risks And Test Signals
Risks include XSAVE compacted offset assumptions, permission/setup ordering, XFD state restore mistakes, and incorrect tile-data handling across VM recreation. Signals are guest assertions for CPUID properties and MSRs, exact `#NM` vector detection, TMM0 `memcmp()`, register equality after restore, and UCALL_DONE completion.
