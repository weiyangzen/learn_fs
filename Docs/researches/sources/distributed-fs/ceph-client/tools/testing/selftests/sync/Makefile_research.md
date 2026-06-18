# sources/distributed-fs/ceph-client/tools/testing/selftests/sync/Makefile

## Purpose
Builds the sw_sync selftest executable from a custom object set.

## Important APIs, types, and functions
Sets pthread-capable CFLAGS/LDFLAGS, includes `../lib.mk`, defines `TEST_CUSTOM_PROGS := $(OUTPUT)/sync_test`, core objects `sync_test.o sync.o`, and test objects for allocation, fence, merge, wait, and stress scenarios.

## Control flow
`all` builds `sync_test`; object pattern rules compile core sources with full `CFLAGS` and test objects with default compile flags; final link combines all objects with pthread flags. `EXTRA_CLEAN` removes binary and objects.

## State and persistence
Only build outputs under `$(OUTPUT)`.

## Dependencies and integration points
Depends on other sync selftest C files not in this work item, kernel headers via `$(KHDR_INCLUDES)`, pthreads, and staging sw_sync config.

## Risks
The test object compile rule omits explicit `$(CFLAGS)`, unlike core object rule, so include/warning options may differ for test modules.

## Test signals
Successful build emits `sync_test`, which lib.mk runs/installs as a custom test.
