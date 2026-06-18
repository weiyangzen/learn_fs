# sources/distributed-fs/ceph-client/drivers/media/platform/allegro-dvt/Makefile

## Purpose

This Makefile builds the Allegro DVT encoder module from the core driver, mailbox protocol helpers, and H.264/HEVC RBSP/NAL helper files.

## Important APIs, Types, And Symbols

- `allegro-objs := allegro-core.o allegro-mail.o` defines the main module object list.
- Additional objects are `nal-rbsp.o`, `nal-h264.o`, and `nal-hevc.o`.
- `obj-$(CONFIG_VIDEO_ALLEGRO_DVT) += allegro.o` ties the aggregate object to the Kconfig symbol.

## Control Flow

Kbuild aggregates all listed objects into one `allegro` module or built-in object when `VIDEO_ALLEGRO_DVT` is enabled. There is no runtime logic in the Makefile.

## State And Persistence

Build artifacts are the only state. Runtime state lives in the compiled C files.

## Dependencies And Integration Points

The object list mirrors internal dependencies: `allegro-core.c` calls `allegro-mail.c` for firmware message serialization and uses `nal-rbsp.c`, `nal-h264.c`, and `nal-hevc.c` to synthesize codec parameter-set NAL units.

## Risks

If an object is omitted, link failures or missing exported helper symbols will occur. Because helper APIs are local to the module but some functions are exported, changes should keep symbol visibility and module composition consistent.

## Test Signals

Build `CONFIG_VIDEO_ALLEGRO_DVT=m` and inspect that `allegro.ko` includes all helper objects. Linker errors around `nal_*` or `allegro_*mail*` symbols point directly to this Makefile.
