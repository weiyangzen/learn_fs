# sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/fuse/Makefile

## Purpose

This Makefile builds the FUSE control selftest and its helper FUSE daemon.

## Important APIs, Types, and Functions

It builds `fusectl_test` as `TEST_GEN_PROGS` and `fuse_mnt` as `TEST_GEN_FILES`. It discovers FUSE CFLAGS and LDLIBS through `pkg-config fuse`, falling back to `-D_FILE_OFFSET_BITS=64 -I/usr/include/fuse` and `-lfuse -pthread`.

## Control Flow, State, and Persistence

Build flow is conditional on pkg-config output. The output-specific rules add the discovered FUSE flags only to `fuse_mnt`; `fusectl_test` uses the base flags.

## Dependencies, Integration Points, Risks, and Test Signals

It depends on libfuse development headers/libraries, kselftest `lib.mk`, and kernel headers. It integrates `fuse_mnt` as a local daemon executed by `fusectl_test`. Risks are distribution-specific FUSE package names and fallback include paths being wrong. Passing signals are successful build of both files and link of `fuse_mnt` against libfuse.
