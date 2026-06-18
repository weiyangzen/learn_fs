# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/s390/ucontrol_test.c

## Purpose
This s390x harness test exercises privileged user-controlled KVM VMs created with `KVM_VM_S390_UCONTROL`. It validates direct SIE block access, ucontrol memory mapping, storage-key interception, unsupported features, FLIC device attributes, and GSI routing rejection.

## Important APIs, Types, And Functions
It checks `CAP_SYS_ADMIN` and `KVM_CAP_S390_UCONTROL`, creates VMs with `KVM_CREATE_VM(KVM_VM_S390_UCONTROL)`, maps `kvm_run` and the SIE block at `KVM_S390_SIE_PAGE_OFFSET`, and uses `KVM_S390_UCAS_MAP`, `KVM_S390_UCAS_UNMAP`, `KVM_S390_VCPU_FAULT`, `KVM_SET_USER_MEMORY_REGION{,2}`, `KVM_CAP_S390_HPAGE_1M`, FLIC device attributes, and `KVM_SET_GSI_ROUTING`. The fixture owns raw VM/vCPU fds and aligned UCAS memory.

## Control Flow
Fixture setup creates the ucontrol VM, maps initial memory, faults in the first page, and un-stops the SIE block. Tests assert SIE bits, memory-limit attributes, dirty-log rejection, huge-page rejection, user-region rejection, UCAS map/unmap behavior on segment-translation exits, GPR synchronization from raw code, storage-key handling with intercepted ISKE/SSKE/RRBE, FLIC attribute errno policy, and invalid adapter routing. `uc_handle_exit()` dispatches `KVM_EXIT_S390_UCONTROL` page faults and `KVM_EXIT_S390_SIEIC` instruction/KSS/operation intercepts.

## State, Dependencies, And Integration
State is low-level and fixture-local: fds, mapped run/SIE pages, base/code GPA/HVA translation, guest code copied into UCAS memory, and mutable SIE controls. The test depends on admin privileges, s390 ucontrol support, instruction length decoding, and direct SIE ABI layout.

## Risks And Test Signals
Risks include privilege-dependent skips, fragile raw SIE-field assumptions, segment-alignment validation, and storage-key interception fallback paths. Signals are kselftest harness assertions, exact exit reason/program-code checks, expected errno values, GPR/skey value checks, and FLIC attr get/set result matrices.
