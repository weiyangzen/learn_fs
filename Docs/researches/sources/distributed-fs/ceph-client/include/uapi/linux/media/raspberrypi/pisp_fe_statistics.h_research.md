# sources/distributed-fs/ceph-client/include/uapi/linux/media/raspberrypi/pisp_fe_statistics.h

## Purpose
Defines the packed statistics buffer ABI emitted by the Raspberry Pi PiSP front end for AWB, AGC, and CDAF algorithms.

## Important APIs, Types, And Functions
Exports zone-count constants and packed structs: `pisp_agc_statistics_zone`, `pisp_agc_statistics`, `pisp_awb_statistics_zone`, `pisp_awb_statistics`, `pisp_cdaf_statistics`, and aggregate `pisp_statistics`. Constants define 4 floating zones, 1024 AGC bins, 16x16 AGC zones, 512 row sums, 32x32 AWB zones, and 8x8 CDAF figures of merit.

## Control Flow
The front-end hardware writes a single `pisp_statistics` buffer according to enabled stats blocks and configured windows. Userspace reads fixed arrays and floating regions to update exposure, white balance, and focus algorithms.

## State, Persistence, And Dependencies
No owned state exists in the header. Persistence is the DMA statistics buffer supplied through FE configuration. It depends only on `linux/types.h` and packed fixed-width integer layouts.

## Integration Points
Consumed by camera middleware that also writes `pisp_fe_config` stats windows. The struct layout must match the FE driver’s stats buffer size and the hardware’s row/histogram/zone ordering.

## Risks
Large fixed arrays make buffer size assumptions important. Counter width can still saturate for extreme frame/window configurations, and packed 64-bit fields may be misread by userspace that assumes natural alignment.

## Test Signals
Check aggregate `sizeof(struct pisp_statistics)`, zone counts, DMA buffer length, histogram bin count, floating-zone ordering, and sane nonzero counted fields under known test patterns.
