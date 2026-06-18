# sources/distributed-fs/ceph-client/drivers/media/platform/amlogic/Kconfig

## Purpose

This Kconfig file is the Amlogic media platform submenu. It groups Amlogic-specific media drivers and sources the C3 and Meson GE2D child Kconfig files.

## Important APIs, Types, And Symbols

- The file emits a `comment "Amlogic media platform drivers"`.
- It sources `drivers/media/platform/amlogic/c3/Kconfig`.
- It sources `drivers/media/platform/amlogic/meson-ge2d/Kconfig`.

## Control Flow

There is no runtime flow. Kconfig includes this file from the top-level platform Kconfig and then recursively loads child driver configuration.

## State And Persistence

The file contributes to persistent kernel `.config` choices through its children. It owns no runtime state.

## Dependencies And Integration Points

It integrates the Amlogic subtree into the media platform menu and must remain paired with the sibling Makefile that descends into `c3/` and `meson-ge2d/`.

## Risks

Missing or incorrect `source` lines can hide entire Amlogic driver families. The comment does not gate anything, so each child must provide its own dependencies.

## Test Signals

Kconfig menu visibility checks and allmodconfig builds should show both C3 and Meson GE2D options under Amlogic media platform drivers.
