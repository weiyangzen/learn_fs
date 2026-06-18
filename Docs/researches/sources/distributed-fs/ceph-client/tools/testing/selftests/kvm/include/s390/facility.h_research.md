# Research: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/s390/facility.h

# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/s390/facility.h

Purpose: s390 facility-list helper definitions. It lets selftests query and reason about architecture facilities exposed to the guest.

Important APIs/types/functions: includes facility bit constants, storage layout helpers, and functions/macros for testing whether a facility bit is present.

Control flow and state: guest or host code loads facility information, checks individual bits, and uses the result to skip or run feature-specific tests. The state is the facility bitmap reported by hardware/KVM.

Dependencies and integration: integrates with s390 processor helpers and tests for instruction/facility-specific behavior. It depends on s390 architectural definitions and KVM-exposed CPU model state.

Risks: facility numbering and bit ordering must be exact. Tests should avoid hard failing when optional facilities are absent and should clearly distinguish host absence from KVM bugs.

Test signals: s390 feature-gated tests validate that facility probing returns expected availability and skip decisions.
