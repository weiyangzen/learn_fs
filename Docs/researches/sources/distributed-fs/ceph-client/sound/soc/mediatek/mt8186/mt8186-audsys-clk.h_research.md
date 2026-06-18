# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8186/mt8186-audsys-clk.h

## Purpose

This header declares the MT8186 audsys gate-clock registration entry point.

## Important APIs, Types, and Data

It exposes `int mt8186_audsys_clk_register(struct mtk_base_afe *afe);`. The implementation registers local gate clocks and clkdev lookups for AFE-internal audio gates.

## Control Flow and State

The header owns no state. The function is called during AFE clock initialization before consumer clock lookup.

## Dependencies and Integration Points

Consumers must have `struct mtk_base_afe` visible or forward-declared by included headers. `mt8186-afe-clk.c` includes this header and treats registration as part of probe setup.

## Risks

The header does not forward-declare `struct mtk_base_afe` itself, so include ordering matters. Any signature change must be synchronized with the implementation and the AFE clock init path.

## Test Signals

Build coverage catches declaration mismatch. Runtime clock acquisition in `mt8186_init_clock()` confirms registration did its job.
