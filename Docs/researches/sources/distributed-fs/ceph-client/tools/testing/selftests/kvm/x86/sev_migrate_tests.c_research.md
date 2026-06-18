<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/sev_migrate_tests.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/sev_migrate_tests.c

## Purpose
This test exercises KVM SEV encrypted-context move and copy capabilities. It verifies migration chains, dead-source behavior, mirror VM creation, parameter validation, concurrent migration locking, and mirror/migration interactions for SEV and SEV-ES where available.

## Important APIs, Types, and Functions
Key helpers are `sev_vm_create()`, `aux_vm_create()`, `__sev_migrate_from()`, `test_sev_migrate_from()`, `test_sev_migrate_locking()`, `test_sev_migrate_parameters()`, `__sev_mirror_create()`, `verify_mirror_allowed_cmds()`, `test_sev_mirror()`, `test_sev_mirror_parameters()`, and `test_sev_move_copy()`. It uses `KVM_CAP_VM_MOVE_ENC_CONTEXT_FROM`, `KVM_CAP_VM_COPY_ENC_CONTEXT_FROM`, SEV launch helpers from `sev.h`, and `KVM_SEV_*` commands.

## Control Flow, State, and Persistence
`main()` requires SEV and relevant capabilities. Migration tests create launched SEV/SEV-ES VMs with four vCPUs, move encrypted context through a chain of destination VMs, and verify moving back from a dead source fails. Locking tests repeatedly call migration from several threads to stress internal serialization. Parameter tests reject non-SEV sources, already encrypted destinations, vCPU count mismatches, and missing SEV-ES VMSA updates. Mirror tests copy encrypted context into vCPU-less VMs, add vCPUs later, verify allowed/disallowed SEV commands, and combine move/copy chains. State is encrypted VM context, launch state, vCPU count, and mirror ownership; it is destroyed with each VM.

## Dependencies and Integration Points
The file integrates with SEV firmware ioctls, KVM encrypted-context ownership, vCPU creation rules, SEV-ES VMSA update requirements, pthread concurrency, and selftests SEV helpers.

## Risks and Test Signals
Risks include context ownership leaks, allowing migration to/from invalid VM states, races in encrypted-context locks, and mirror command over-permissiveness. Signals are expected success through valid chains, `EINVAL` or `EIO` for invalid moves, no crashes under concurrent migration attempts, and successful `KVM_SEV_GUEST_STATUS` on mirrors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/sev_migrate_tests.c -->
