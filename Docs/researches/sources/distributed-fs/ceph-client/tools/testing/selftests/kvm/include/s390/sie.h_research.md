# Research: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/s390/sie.h

# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/s390/sie.h

Purpose: s390 SIE (Start Interpretive Execution) control-block definitions for nested/low-level KVM selftests. It models the packed architecture data structures and intercept fields used by s390 virtualization.

Important APIs/types/functions: defines SIE control-block structs, prefix/state/intercept fields, bit constants, and layout helpers for interpreting or constructing SIE state.

Control flow and state: tests allocate or inspect SIE-related structures, set control bits, run guest/nested guest code, and examine intercept/exit fields after execution. Persistent state is the SIE control block and virtual CPU architecture state.

Dependencies and integration: integrates with s390 processor helpers, KVM vCPU state ioctls, and nested virtualization tests. Layout must match s390 architecture and kernel ABI expectations.

Risks: packed-structure layout is the main risk. Padding, alignment, or field-width mistakes can corrupt nested execution state or misinterpret intercept causes. Architecture updates may add fields or redefine bits.

Test signals: s390 nested/SIE selftests validate layout by successfully entering/exiting interpretive execution and matching expected intercept codes.
