# sources/distributed-fs/ceph-client/samples/acrn/Makefile

Purpose: builds the ACRN hypervisor sample userspace VM launcher and its tiny guest payload.

Important APIs/types/functions: declares phony `vm-sample`, links `vm-sample.o` and `payload.o`, builds `payload.o` with `$(LD) -T payload.ld` from `guest16.o`, and provides a simple `clean`.

Control flow: make compiles normal objects through implicit rules, links the executable with `$(CC)`, and links the payload with a custom linker script.

State and persistence: creates `vm-sample`, object files, and `payload.o`.

Dependencies and integration: depends on `guest16.o`, `payload.ld`, `vm-sample.c`, kernel UAPI headers for ACRN, and an environment with `CC`/`LD`.

Risks: clean uses `rm *.o vm-sample` without `-f`, so it errors if files are absent. The standalone Makefile assumes all payload inputs exist and may not inherit all kbuild hardening flags.

Test signals: standalone `make` in `samples/acrn`, successful link of `payload.o`, and running `vm-sample` only on an ACRN Service VM with `/dev/acrn_hsm`.
