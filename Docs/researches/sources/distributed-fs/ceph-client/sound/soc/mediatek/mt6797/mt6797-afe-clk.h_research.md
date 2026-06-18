# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt6797/mt6797-afe-clk.h

## Purpose

This header declares the MT6797 AFE clock-control interface.

## Important APIs, Types, and Functions

It forward-declares `struct mtk_base_afe` and exports `mt6797_init_clock()`, `mt6797_afe_enable_clock()`, and `mt6797_afe_disable_clock()`.

## Control Flow

No executable flow. The declarations support platform probe and runtime PM hooks.

## State and Persistence Behavior

No state is stored here; state resides in the platform-private clock array and CCF.

## Dependencies and Integration Points

Included by `mt6797-afe-pcm.c`, implemented by `mt6797-afe-clk.c`, and linked via the MT6797 composite object.

## Risks and Edge Cases

The API is minimal and cannot express partial clock state or validate runtime PM ordering; callers must handle return values carefully.

## Test Signals

Compile coverage and runtime PM clock traces validate the interface.
