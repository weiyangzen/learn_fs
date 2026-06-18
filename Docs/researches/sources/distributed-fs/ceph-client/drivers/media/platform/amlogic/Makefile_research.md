# sources/distributed-fs/ceph-client/drivers/media/platform/amlogic/Makefile

## Purpose

This Makefile descends into Amlogic media platform subdirectories.

## Important APIs, Types, And Symbols

- `obj-y += c3/` enters the Amlogic C3 media driver subtree.
- `obj-y += meson-ge2d/` enters the Meson GE2D subtree.

## Control Flow

Kbuild traverses both child directories when the Amlogic media platform directory is reached. The child Makefiles contain the actual Kconfig object gates.

## State And Persistence

There is no runtime state. Build artifacts are determined by child Makefiles and `.config`.

## Dependencies And Integration Points

The file pairs with `amlogic/Kconfig` and delegates C3 ISP, C3 MIPI, and GE2D build selection to child directories.

## Risks

A child Kconfig source without a matching `obj-y` traversal entry would make a visible config option fail to build its objects. Conversely, extra traversal is normally harmless but can expose stale Makefiles.

## Test Signals

Builds with `CONFIG_VIDEO_C3_ISP=m` should enter `amlogic/c3/isp/` and produce `c3-isp.o`.
