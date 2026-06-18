# sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/Makefile

Purpose: minimal makefile entry point to run a short rcutorture KVM test from the kernel top-level tree.

Important APIs and functions: `all` changes four directories up and invokes `tools/testing/selftests/rcutorture/bin/kvm.sh --duration 10 --configs TREE01`.

Control flow: single default target delegates everything to `kvm.sh`.

State and persistence: creates normal rcutorture result directories through the delegated script.

Dependencies and integration: assumes qemu/KVM tooling and rcutorture scripts are usable from the top-level Linux tree.

Risks and test signals: running `make` here can build kernels and launch qemu. Failures are surfaced by `kvm.sh` and its recheck scripts.
