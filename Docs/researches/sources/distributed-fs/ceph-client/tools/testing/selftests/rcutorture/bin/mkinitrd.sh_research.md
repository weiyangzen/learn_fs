# sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/mkinitrd.sh

Purpose: creates the small initrd used by rcutorture qemu runs if it does not already exist.

Important APIs and functions: validates `tools/testing/selftests/rcutorture`, checks existing `initrd/init`, writes a temporary `init.c`, detects nolibc-supported architectures with the preprocessor, compiles static `init`, and removes source.

Control flow: if init exists, exit success. Otherwise create initrd directory, generate a simple infinite-loop init program that prints command line, sleeps, and burns small userspace time, compile with nolibc when supported or static glibc otherwise, and report success/failure.

State and persistence: writes `tools/testing/selftests/rcutorture/initrd/init` and temporarily `init.c`.

Dependencies and integration: called by `kvm.sh` unless `--no-initrd`; depends on compiler and optional `CROSS_COMPILE`.

Risks and test signals: uses shell redirection to create C source and can fail if static linking is unavailable. The generated init loops forever by design for qemu guest boot.
