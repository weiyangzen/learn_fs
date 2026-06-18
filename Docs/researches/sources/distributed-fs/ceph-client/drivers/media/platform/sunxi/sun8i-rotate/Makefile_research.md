# sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun8i-rotate/Makefile

Purpose: links the sun8i rotate driver from its core implementation and format table.

Important APIs and entries: `sun8i-rotate-y` includes `sun8i_rotate.o` and `sun8i_formats.o`; `obj-$(CONFIG_VIDEO_SUN8I_ROTATE)` builds `sun8i-rotate.o`.

Control flow: kbuild links both objects into one module or built-in object.

State and persistence: no runtime state.

Dependencies and integration points: matches the split between register/V4L2 logic and reusable format lookup/enumeration.

Risks: adding formats only in one file is safe, but splitting more helpers requires Makefile updates.

Test signals: targeted build with `CONFIG_VIDEO_SUN8I_ROTATE=m`.
