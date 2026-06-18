# sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/kvm-build.sh

Purpose: builds a kernel suitable for rcutorture qemu execution from a config template.

Important APIs and functions: checks `TORTURE_STOPFILE`, appends initrd and virtio config options, calls `configinit.sh`, then runs `make -j(2*ncpus)` with `$TORTURE_KMAKE_ARG`. It scans build output for errors and warnings.

Control flow: validate config template, stage config, initialize `.config`, exit on config-init hard failure, build kernel, and reject nonzero make or suspicious output.

State and persistence: modifies/builds the kernel tree and writes `Make.out` plus configinit logs in result dir.

Dependencies and integration: called by `kvm-test-1-run.sh`; depends on generated `TORTURE_INITRD`.

Risks and test signals: treats many warnings in RCU paths as build errors. It can be expensive and mutates build artifacts in the working tree.
