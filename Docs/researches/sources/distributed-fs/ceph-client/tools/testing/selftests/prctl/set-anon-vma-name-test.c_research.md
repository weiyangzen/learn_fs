# sources/distributed-fs/ceph-client/tools/testing/selftests/prctl/set-anon-vma-name-test.c

Purpose: tests `PR_SET_VMA` / `PR_SET_VMA_ANON_NAME` for naming anonymous VMAs.

Important APIs/types/functions: `rename_vma()` wraps prctl and returns negative errno; `was_renaming_successful()` parses `/proc/self/maps`; fixture `vma` owns anonymous and non-anonymous mappings.

Control flow: setup maps one anonymous private area and one non-anonymous private area. The test successfully names the anonymous VMA and confirms `[anon:goodname]` appears at the mapping start, then expects `-EINVAL` for a non-printable name and for a non-anonymous VMA.

State and persistence behavior: modifies only current process VMA metadata and reads `/proc/self/maps`. Teardown unmaps both regions.

Dependencies and integration points: uses `kselftest_harness.h`, `CONFIG_ANON_VMA_NAME`, and prctl VMA naming support.

Risks and test signals: `mmap(... MAP_PRIVATE, fd=0, offset=0)` for the non-anonymous mapping depends on fd 0 being mappable; in unusual test environments setup may fail before intended assertions.
