# sources/distributed-fs/ceph-client/drivers/media/platform/Makefile

## Purpose

This Makefile descends into platform media driver subdirectories and builds two ancillary platform driver objects. It mirrors the Kconfig vendor list so that each child directory can decide its own object inclusion from Kconfig symbols.

## Important APIs, Types, And Symbols

- `obj-y += allegro-dvt/`, `obj-y += amlogic/`, and similar lines always visit child directories during media platform builds.
- `obj-$(CONFIG_VIDEO_MEM2MEM_DEINTERLACE) += m2m-deinterlace.o` builds the generic deinterlace driver when selected.
- `obj-$(CONFIG_VIDEO_MUX) += video-mux.o` builds the ancillary video multiplexer when selected.

## Control Flow

Kbuild evaluates this Makefile when the media platform subtree is entered. Directory traversal happens unconditionally through `obj-y` entries; the child Makefiles contain the final `CONFIG_*` gates for their driver objects.

## State And Persistence

There is no runtime state. Build output state is the set of compiled objects and modules produced from the current `.config`.

## Dependencies And Integration Points

This file is coupled to `drivers/media/platform/Kconfig` by directory naming and ordering. It also integrates with Kbuild's recursive object traversal rules and with child directories such as `allegro-dvt/` and `amlogic/`.

## Risks

Adding a Kconfig source without a matching Makefile directory entry, or the reverse, can create confusing config/build mismatches. Alphabetic ordering comments are maintenance constraints but not enforced by Kbuild.

## Test Signals

Run `make drivers/media/platform/` or allmodconfig builds after directory changes. Confirm that selected child modules, for example `allegro.o` and `c3-isp.o`, are reached by the traversal.
