# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_jeq_infer_not_null.c

## Purpose

`verifier_jeq_infer_not_null.c` tests branch inference that converts nullable pointer types to non-null pointer types after equality or inequality comparisons. It covers socket pointers returned in cgroup/skb programs and map-value pointers in XDP programs.

## Important APIs, Types, and Functions

The file defines an XSKMAP named `map_xskmap` and seven programs. Four cgroup/skb programs check `PTR_TO_SOCKET_OR_NULL` behavior after `JNE` and `JEQ` branches. Three XDP programs check `PTR_TO_MAP_VALUE_OR_NULL` and register-register null comparisons. Expected unprivileged failures mention pointer comparison; expected privileged failures mention invalid access to `sock_or_null`.

## Control Flow

Socket tests obtain a nullable socket pointer, compare it against zero or another register, and then dereference either the branch where non-null can be inferred or the branch where null remains possible. Map-value tests perform lookup-like operations, compare result registers to null, and dereference only after the verifier should have refined the type.

## State and Persistence Behavior

Persistent state is the XSKMAP. Verifier state tracks nullable pointer ids, branch predicates, equality between registers, and type refinement from `*_OR_NULL` to concrete pointer types.

## Dependencies and Integration Points

The file integrates with cgroup socket helpers/context, XDP map-value lookup semantics, and verifier branch-state splitting. It is also tied to unprivileged restrictions on pointer comparisons.

## Risks and Test Signals

Risks are failing to refine non-null pointers on the correct branch, refining the wrong branch, or allowing unprivileged pointer comparisons. Test signals are success for true non-null branches, failure for unchanged nullable dereference, and verifier log messages showing dereference after null-check branches.
