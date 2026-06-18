# sources/distributed-fs/ceph-client/tools/testing/selftests/liveupdate/Makefile

## Purpose

`liveupdate/Makefile` builds liveupdate selftest binaries and shared utility objects, registers the kexec helper script, and tracks generated dependency files.

## Important APIs, Types, and Functions

It sets `LIB_C += luo_test_utils.c`, `TEST_GEN_PROGS += liveupdate`, `TEST_GEN_PROGS_EXTENDED += luo_kexec_simple luo_multi_session`, `TEST_FILES += do_kexec.sh`, includes `../lib.mk`, adds kernel header includes and warning flags, builds `LIB_O`, `TEST_O`, and dependency `.d` files, and defines custom link rules.

## Control Flow and State

The Makefile compiles library objects into `OUTPUT`, compiles each test object, links test binaries with the shared utility object, includes generated dependency files, and extends `EXTRA_CLEAN` so object and dependency files are removed.

## Dependencies and Integration Points

It depends on `lib.mk`, kernel UAPI headers, liveupdate C sources outside this subset, and standard compiler dependency generation.

## Risks and Test Signals

Risks include stale `.d` files, missing shared object linkage, and divergence from common `lib.mk` pattern rules. Signals are successful builds of `liveupdate`, `luo_kexec_simple`, and `luo_multi_session`, plus clean removing generated objects/deps.
