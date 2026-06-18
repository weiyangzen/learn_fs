# sources/distributed-fs/ceph-client/drivers/video/fbdev/wmt_ge_rops.h

Purpose: configuration wrapper for WonderMedia GE ROP helpers. It lets fbdev drivers call `wmt_ge_*` functions unconditionally while providing system-memory fallbacks when GE acceleration is not built.

Important APIs, types, and functions: declares or inlines `wmt_ge_fillrect`, `wmt_ge_copyarea`, and `wmt_ge_sync`. With `CONFIG_FB_WMT_GE_ROPS`, these are externs from `wmt_ge_rops.c`; otherwise `wmt_ge_fillrect` maps to `sys_fillrect`, `wmt_ge_copyarea` maps to `sys_copyarea`, and sync returns success.

Control flow: compile-time only through preprocessor conditionals.

State and persistence: no state; fallback behavior is stateless aside from normal fbdev memory writes.

Dependencies and integration points: included by `wm8505fb.c`; depends on fbdev declarations being visible to callers.

Risks: software fallback uses `sys_*` helpers while the accelerated path uses I/O request programming. That can hide acceleration-specific bugs unless both configurations are tested. The header itself does not include fb headers, so include ordering matters.

Test signals: compile both enabled and disabled configurations; verify `wm8505fb_ops` resolves symbols and that software fallback draws correctly without the GE platform device.
