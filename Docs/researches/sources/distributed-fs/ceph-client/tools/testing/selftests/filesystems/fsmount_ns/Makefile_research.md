# sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/fsmount_ns/Makefile

## Purpose

This Makefile builds the `fsmount_ns_test` kselftest for the `FSMOUNT_NAMESPACE` mount API flag.

## Important APIs, Types, and Functions

It sets `CFLAGS += -Wall -O2 -g $(KHDR_INCLUDES)`, declares `TEST_GEN_PROGS := fsmount_ns_test`, adds `LOCAL_HDRS += ../wrappers.h ../statmount/statmount.h ../utils.h`, and links `fsmount_ns_test` with `../utils.c`.

## Control Flow, State, and Persistence

There is no runtime flow. The common kselftest makefile compiles the test with local wrapper and utility dependencies.

## Dependencies, Integration Points, Risks, and Test Signals

It depends on kernel headers, kselftest `lib.mk`, and utility source availability. Integration points are the new mount API wrappers and statmount helper. Risks are header/API drift around newly added flags. Passing signals are successful compile and the generated `fsmount_ns_test` binary.
