# sources/distributed-fs/ceph-client/tools/testing/selftests/dmabuf-heaps/config

## Purpose

This config declares kernel support needed by the dma-buf heap selftest.

## Important APIs, Types, and Functions

It requests `CONFIG_DMABUF_HEAPS`, `CONFIG_DMABUF_HEAPS_SYSTEM`, and `CONFIG_DRM_VGEM`.

## Control Flow

There is no executable flow.

## State and Persistence Behavior

It persists feature requirements only.

## Dependencies and Integration Points

The C test needs `/dev/dma_heap/*` and optionally VGEM import via `/dev/dri/card*`.

## Risks and Edge Cases

VGEM absence causes import subtests to skip, while heap absence skips the whole test at runtime.

## Test Signals

Kernels with these symbols should expose at least the system heap and vgem importer for full coverage.
