# sources/distributed-fs/ceph-client/drivers/net/phy/mscc/mscc_fc_buffer.h

## Purpose
Defines register offsets and bitfield helpers for the MSCC flow-control buffer block used by VSC85xx datapath configuration.

## Important APIs, Types, And Constants
Constants cover enable, mode, PPM rate adaptation thresholds, TX control/data queues, RX data queue, XON/XOFF thresholds, flow-control read thresholds, and frame-gap compensation. Bit helpers pack 32-bit queue start/end and threshold fields.

## Control Flow
No executable control flow. Consumers write offsets and packed values through MSCC CSR/register access helpers.

## State And Persistence
No software state. Hardware state controls TX/RX buffer enablement, pause reaction/generation, rate adaptation, queue partitioning, and thresholds.

## Dependencies And Integration Points
Requires Linux bit helpers through consumers. Expected users are MSCC MACsec/PTP/datapath code around the line MAC.

## Risks
Macros do not validate arguments; callers must avoid overflow and overlapping queue regions. Bad threshold values can cause drops, stalls, or pause storms.

## Test Signals
Compile consumers, validate generated writes against datasheet layouts, and run pause-frame/rate-adaptation traffic tests.
