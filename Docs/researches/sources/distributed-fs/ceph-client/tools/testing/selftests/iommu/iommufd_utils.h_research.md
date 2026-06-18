# sources/distributed-fs/ceph-client/tools/testing/selftests/iommu/iommufd_utils.h

`iommufd_utils.h` is the shared helper layer for IOMMUFD selftests. It converts raw IOMMUFD and in-kernel selftest ioctls into concise assertion macros and owns common page-size and buffer globals used by both functional and fail-nth tests.

The header imports `kselftest_harness.h` and `drivers/iommu/iommufd/iommufd_test.h`. It defines bit helpers, IOPT accounting constants, `DIV_ROUND_UP`, `buffer`, `BUFFER_SIZE`, `mfd_buffer`, `mfd`, `PAGE_SIZE`, `offsetofend()`, `EXPECT_ERRNO()`, and a large set of wrappers for mock-domain creation/replacement, HWPT allocation/invalidation, vIOMMU invalidation, access objects, dirty tracking, dmabufs, IOAS alloc/map/unmap/map-file, temporary memory limits, hardware info, fault queues, IOPF triggering, vIOMMU/vdevice/hardware-queue/event-queue allocation, event reads, and PASID operations.

Most helpers build a UAPI or `iommu_test_cmd` struct, issue `ioctl()`, and copy returned ids or counts back to callers. Mapping helpers preserve automatic or fixed IOVA results. Invalidation wrappers expose kernel-updated `entry_num` for partial-progress tests. Dirty-bitmap helpers synthesize dirty bits, retrieve them with clear or no-clear flags, and verify bit-level coalescing. Event helpers poll/read event fds and detect lost events or sequence gaps. `teardown_iommufd()` closes the current fd, reopens `/dev/iommu`, and validates page references returned to baseline.

The header is tightly coupled to IOMMUFD UAPI and selftest-only kernel ABI constants such as mock aperture, mock page size, IOTLB count, and cache count. It depends on memfd, mmap, poll, fcntl, ioctl, Linux integer types, and kselftest assertions.

Risks include macro coupling to fixture fields such as `self->fd`, hidden assertion semantics, wrong errno polarity in helper selection, and unusual include-guard placement: helper definitions after the `#endif` are not protected from duplicate inclusion. Test signals are clean compilation, expected ids and errno values, updated invalidation counts, correct dirty/event behavior, and successful teardown reference checks.
