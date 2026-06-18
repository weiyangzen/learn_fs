# Research: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/s390/processor.h

# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/s390/processor.h

Purpose: s390 processor support header for KVM selftests. It defines CPU/register helper declarations and architecture constants needed by s390 guest and host test code.

Important APIs/types/functions: includes s390 processor state helpers, guest entry/setup declarations, interrupt/exception-related types, and low-level instruction helper prototypes used by s390 tests.

Control flow and state: s390 tests use these declarations to initialize vCPU state, execute guest instructions, and inspect architecture-specific CPU state. Persistent state lives in KVM vCPU registers and s390-specific control blocks.

Dependencies and integration: integrates with `kvm_util.h`, `s390/sie.h`, facility helpers, debug printing, and ucall support.

Risks: s390 CPU model and facility exposure are highly architecture-specific. Register layout mismatches or missing facility gates can make tests fail on otherwise valid hosts.

Test signals: s390 KVM selftests that create vCPUs, run guest code, inspect registers, or handle exceptions validate this header.
