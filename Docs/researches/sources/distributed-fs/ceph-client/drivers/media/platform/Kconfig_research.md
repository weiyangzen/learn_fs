# sources/distributed-fs/ceph-client/drivers/media/platform/Kconfig

## Purpose

This top-level media platform Kconfig file gates the whole `drivers/media/platform` subtree. It defines broad user-visible switches for platform media drivers, V4L platform devices, SDR platform devices, DVB platform devices, and V4L2 memory-to-memory drivers, then sources per-vendor platform Kconfig files in alphabetic order.

## Important APIs, Types, And Symbols

- `MEDIA_PLATFORM_DRIVERS` is a `menuconfig` defaulting to `y`; every later symbol in this file is guarded by `if MEDIA_PLATFORM_DRIVERS`.
- `V4L_PLATFORM_DRIVERS`, `SDR_PLATFORM_DRIVERS`, `DVB_PLATFORM_DRIVERS`, and `V4L_MEM2MEM_DRIVERS` are umbrella booleans used by child drivers.
- `VIDEO_MEM2MEM_DEINTERLACE` and `VIDEO_MUX` are ancillary non-SoC-specific platform drivers selected directly from this file.
- `source "drivers/media/platform/<vendor>/Kconfig"` lines integrate Allegro DVT, Amlogic, and many other SoC/vendor subtrees.

## Control Flow

Kconfig evaluation enters the menu when `MEDIA_PLATFORM_DRIVERS` is enabled. Users or defconfigs can enable the category booleans, and later sourced child files use those category symbols as dependencies. The file has no runtime control flow; it controls compile-time visibility and dependency resolution.

## State And Persistence

The persistent state is the kernel configuration generated from these symbols. Choices are stored in `.config` and affect which objects are built. There is no runtime state.

## Dependencies And Integration Points

This file integrates with the broader media subsystem through symbols such as `VIDEO_DEV`, `MEDIA_SDR_SUPPORT`, and `MEDIA_DIGITAL_TV_SUPPORT`. It integrates vendor subtrees by sourcing child Kconfig files, including the Allegro DVT encoder and Amlogic C3 ISP tree researched in this item.

## Risks

Dependency mistakes here can hide large classes of drivers or expose drivers without required core media support. Ordering is intentionally alphabetic; merge conflicts or misplaced source lines can make maintenance harder. Broad defaults such as `MEDIA_PLATFORM_DRIVERS=y` affect build coverage across architectures.

## Test Signals

Useful validation includes `make menuconfig` visibility checks, `make olddefconfig` on representative configs, allmodconfig build coverage, and verifying that enabling `VIDEO_ALLEGRO_DVT` or `VIDEO_C3_ISP` is only possible when their dependencies are satisfied.
