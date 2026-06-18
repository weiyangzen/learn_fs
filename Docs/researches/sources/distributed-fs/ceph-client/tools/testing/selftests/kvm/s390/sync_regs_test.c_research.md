# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/s390/sync_regs_test.c

## Purpose
This s390x test validates `KVM_CAP_SYNC_REGS` behavior for synchronized GPR, ACR, CR, and DIAG318 fields through the `kvm_run` shared structure.

## Important APIs, Types, And Functions
It uses `kvm_valid_regs`, `kvm_dirty_regs`, `KVM_SYNC_GPRS`, `KVM_SYNC_ACRS`, `KVM_SYNC_CRS`, `KVM_SYNC_DIAG318`, `KVM_GET_REGS`, `KVM_GET_SREGS`, and helper `get_diag318_info()`. Guest code repeatedly exits with `diag 0,0,0x501` and increments r11.

## Control Flow
`main()` requires `KVM_CAP_SYNC_REGS`, creates one vCPU, and runs five test functions. Invalid read and dirty masks must make `_vcpu_run()` fail with `EINVAL`. Valid read masks populate sync regs and are compared with explicit get-reg ioctl results. Dirty GPR/ACR/DIAG318 values are injected before KVM_RUN and verified after guest execution. Clearing dirty bits confirms KVM overwrites stale userspace values with guest state.

## State, Dependencies, And Integration
All mutable state is in `struct kvm_run::s.regs`, traditional register getter structures, and the guest's r11 loop. The test depends on s390 sync-reg ABI and optional DIAG318 availability.

## Risks And Test Signals
Risks include accepting invalid mask bits, failing to synchronize one register class, or treating non-dirty userspace values as authoritative. Signals are exact `EINVAL` checks, SIEIC DIAG 0x501 intercept validation, compare helpers across every GPR/ACR/CR, and five kselftest pass lines.
