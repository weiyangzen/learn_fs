# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/dma-buf/config

## Purpose

This config declares the kernel feature needed by the drivers/dma-buf udmabuf selftest.

## Important APIs, Types, and Functions

It requests `CONFIG_UDMABUF=y`.

## Control Flow

There is no executable flow.

## State and Persistence Behavior

It persists only the kernel configuration requirement.

## Dependencies and Integration Points

The generated `udmabuf` test expects `/dev/udmabuf` and UDMABUF ioctl support.

## Risks and Edge Cases

If UDMABUF is modular or absent despite the config expectation, the runtime test may skip or fail opening the device.

## Test Signals

With the symbol enabled, the udmabuf selftest can exercise create and create-list ioctls.
