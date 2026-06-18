# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt2701/mt2701-afe-clock-ctrl.h

## Purpose

This header declares the MT2701 clock-control API exported from `mt2701-afe-clock-ctrl.c` to the AFE PCM/platform driver.

## Important APIs, Types, and Functions

It forward-declares `struct mtk_base_afe` and `struct mt2701_i2s_path`, then declares initialization, global enable/disable, per-I2S path clock enable/disable, MCLK enable/disable, BT merge clock control, and MCLK parent/divider configuration helpers.

## Control Flow

The header has no flow. Its declarations support the PCM probe/runtime path (`init`, runtime resume/suspend) and DAI path (`startup`, `prepare`, `shutdown`, BT merge startup/shutdown).

## State and Persistence Behavior

No state is stored here. Callers mutate `mt2701_afe_private`, `mt2701_i2s_path`, CCF clock state, and AFE registers through the declared helpers.

## Dependencies and Integration Points

It is included by `mt2701-afe-pcm.c` and implemented by `mt2701-afe-clock-ctrl.c`. The forward declarations keep include coupling low, but callers still need the common MT2701 structures from `mt2701-afe-common.h`.

## Risks and Edge Cases

The API does not encode valid I2S IDs or clock state, so callers must pass IDs validated against the SoC variant. Calling disable helpers without matching successful enables relies on CCF tolerance.

## Test Signals

Build coverage catches signature drift. Runtime I2S and BT paths validate the declared helpers are called in the right lifecycle order.
