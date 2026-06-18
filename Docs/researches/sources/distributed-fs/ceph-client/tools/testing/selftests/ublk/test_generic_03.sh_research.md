# sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_generic_03.sh

## Purpose
This test verifies sysfs queue limits reported by a zero-copy null ublk device.

## Important APIs, Types, and Functions
It uses `_add_ublk_dev -t null -z` and reads `/sys/block/ublkbN/queue/dma_alignment`, `max_segments`, and `max_segment_size`.

## Control Flow
The script creates a zero-copy null device and expects DMA alignment `4095`, `max_segments` `32`, and `max_segment_size` `32768`. Any mismatch sets failure before cleanup.

## State and Persistence
It creates a temporary null ublk device and removes it after checking sysfs.

## Dependencies and Integration Points
It depends on null target params and kernel block queue sysfs reporting.

## Risks
Kernel queue-limit representation changes can break exact string checks. Zero-copy feature absence may cause device creation skip through common helpers.

## Test Signals
Pass means the null target's DMA and segment parameters are reflected in sysfs.
