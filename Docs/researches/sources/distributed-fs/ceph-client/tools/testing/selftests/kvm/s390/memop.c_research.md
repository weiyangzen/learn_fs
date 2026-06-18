# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/s390/memop.c

## Purpose
This large s390x selftest validates `KVM_S390_MEM_OP` across logical, absolute, SIDA, and absolute compare-exchange modes. It covers copy correctness, storage-key protection, access-register mode, protection overrides, exception injection, cmpxchg atomicity, and invalid argument handling.

## Important APIs, Types, And Functions
The core wrapper is `ksmo_from_desc()` and the `MOP`/`ERR_MOP` macro family that builds `struct kvm_s390_mem_op` and calls either VM or vCPU `KVM_S390_MEM_OP`. Test state is described by `struct mop_desc`, `struct test_info`, and `struct test_default`. Guest helpers set storage keys with `sske`, copy memory, perform concurrent `cs/csg/cdsg` cmpxchg loops, and synchronize with `GUEST_SYNC`. Capabilities include `KVM_CAP_S390_MEM_OP` and `KVM_CAP_S390_MEM_OP_EXTENSION`.

## Control Flow
`main()` requires base MEM_OP and computes extension bits, then runs or skips a table of copy, key, cmpxchg, override, termination, and error tests. Copy tests write guest memory via MEM_OP, let the guest copy, read back, and compare. Key tests create protected pages and exercise matching, mismatching, fetch-protected, and override cases. Cmpxchg tests cover sizes 1/2/4/8/16 where valid, alignment errors, and a concurrent host/guest loop that checks bit-count preservation. Error tests validate bad sizes, flags, addresses, keys, access registers, SIDA rejection, and TEID termination data after injected exceptions.

## State, Dependencies, And Integration
Static page-aligned buffers `mem1` and `mem2` are shared guest/host data. `kvm_run` sync registers are manipulated for CR0 protection override bits and AR mode. There is no persistence. The test integrates deeply with s390 guest memory translation, storage keys, selftest ucalls, and KVM's MEM_OP extension-capability bitmask.

## Risks And Test Signals
Risks include subtle differences between VM absolute and vCPU logical paths, off-by-one in fetch-protection override ranges, incorrect exception injection, non-atomic cmpxchg, and key handling around page boundaries. Signals are exhaustive per-test kselftest pass/skip output, exact errno checks, positive program-exception return codes, memory equality assertions, and TEID bit validation.
