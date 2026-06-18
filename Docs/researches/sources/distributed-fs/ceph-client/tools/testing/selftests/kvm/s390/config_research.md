# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/s390/config

## Purpose
This kselftest configuration fragment declares kernel configuration prerequisites for s390 KVM selftests.

## Important APIs, Types, And Functions
There is no C API or control flow. The file contains two Kconfig requirements: `CONFIG_KVM=y` and `CONFIG_KVM_S390_UCONTROL=y`.

## Control Flow
Build/test harness tooling consumes this file as declarative metadata. It does not execute directly.

## State, Dependencies, And Integration
The file integrates with kselftest configuration checking so s390 KVM tests are only expected to run on kernels with base KVM and s390 user-control VM support. It has no runtime state and no persistence beyond its tracked text.

## Risks And Test Signals
The main risk is under-declaring dependencies as new s390 tests require additional kernel features. Current signals are binary config checks: missing `CONFIG_KVM` invalidates all KVM tests, while missing `CONFIG_KVM_S390_UCONTROL` invalidates tests using the privileged s390 ucontrol interface.
