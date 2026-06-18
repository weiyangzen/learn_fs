# sources/distributed-fs/ceph-client/tools/testing/selftests/dmabuf-heaps/Makefile

## Purpose

This Makefile builds the dma-buf heaps selftest binary.

## Important APIs, Types, and Functions

It sets static optimized CFLAGS with exported kernel headers, declares `TEST_GEN_PROGS = dmabuf-heap`, and includes `../lib.mk`.

## Control Flow

Kselftest builds and runs the C program.

## State and Persistence Behavior

The Makefile has no runtime state.

## Dependencies and Integration Points

It integrates with dma-buf heaps and DRM/VGEM testing through the generated binary.

## Risks and Edge Cases

Static linking and `-O3` can expose toolchain/library availability issues on minimal systems.

## Test Signals

Build success creates the `dmabuf-heap` executable.
