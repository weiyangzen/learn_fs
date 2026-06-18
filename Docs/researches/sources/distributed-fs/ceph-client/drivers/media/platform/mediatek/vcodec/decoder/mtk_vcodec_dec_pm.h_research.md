# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/decoder/mtk_vcodec_dec_pm.h

## Purpose
This header exposes decoder power-management helpers for clock initialization and per-hardware enable/disable.

## Important APIs, Types, And Functions
`mtk_vcodec_init_dec_clk()` initializes a `struct mtk_vcodec_pm` from a platform device. `mtk_vcodec_dec_enable_hardware()` and `mtk_vcodec_dec_disable_hardware()` wrap locking, runtime PM, clocks, IRQs, and racing-state handling for a decoder context and hardware index.

## Control Flow
No direct execution. Probe calls clock init; codec workers call enable before accessing hardware and disable afterward.

## State, Persistence, And Dependencies
The helpers operate on runtime PM and clock state stored in decoder device/subdevice structures. The header depends on decoder driver state.

## Integration Points
Included by parent probe, subdevice probe, shared decoder operations, stateful/stateless workers through codec interfaces, and hardware driver code.

## Risks
Callers must pair enable/disable for the same hardware index or deadlock/leak PM references. The API does not expose failure from enable.

## Test Signals
Pairing tests, lockdep around hardware mutexes, runtime PM traces, and clock prepare/unprepare balancing.
