# sources/distributed-fs/ceph-client/samples/seccomp/Makefile

## Purpose

This Makefile builds the seccomp user-space sample programs as kernel-tree user programs.

## Important APIs, Types, and Functions

It sets `userprogs-always-y += bpf-fancy dropper bpf-direct user-trap`, defines the composite `bpf-fancy-objs := bpf-fancy.o bpf-helper.o`, and adds `userccflags += -I usr/include`.

## Control Flow

Kbuild compiles all listed user programs unconditionally when this samples directory is built. `bpf-fancy` links with the helper object.

## State and Persistence Behavior

No runtime state is created by the Makefile; it affects build outputs only.

## Dependencies and Integration Points

It integrates with Kbuild user program rules and UAPI headers under `usr/include`.

## Risks and Edge Cases

The samples are architecture- and kernel-feature-sensitive. Missing UAPI seccomp headers or unsupported host architectures can limit build/runtime behavior.

## Test Signals

Build `samples/seccomp/` and verify the four user binaries are emitted.
