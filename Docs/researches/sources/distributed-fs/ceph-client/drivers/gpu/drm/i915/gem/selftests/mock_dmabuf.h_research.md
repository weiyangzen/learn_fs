# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/selftests/mock_dmabuf.h

## Purpose
Defines the mock dma-buf private container and conversion helper.

## APIs And Control Flow
Defines `struct mock_dmabuf` with `npages` and a flexible page array, plus inline `to_mock()` returning `buf->priv`. There is no other runtime flow.

## State, Dependencies, Integration, Risks, And Tests
The header stores no state; the described state is owned by `mock_dmabuf.c`. It depends on `<linux/dma-buf.h>` and is used by mock dma-buf ops and dma-buf selftests. Risk is calling `to_mock()` on a non-mock dma-buf. Build and PRIME mock tests validate it.
