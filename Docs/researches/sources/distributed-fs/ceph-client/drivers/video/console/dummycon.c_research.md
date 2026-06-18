# sources/distributed-fs/ceph-client/drivers/video/console/dummycon.c

Purpose: minimal console switch used when no real text console is available or before framebuffer console takeover. With deferred fbcon takeover, it also notifies fbcon when visible text output first occurs.

Important APIs/types/functions: exports `const struct consw dummy_con`. Under `CONFIG_FRAMEBUFFER_CONSOLE_DEFERRED_TAKEOVER`, it defines a raw notifier chain, `dummycon_register_output_notifier()`, `dummycon_unregister_output_notifier()`, and output-detection logic in `dummycon_putc()`/`dummycon_putcs()`.

Control flow: startup returns a dummy display string. Init sets color support and console dimensions from Kconfig or Footbridge VGA screen info. Most drawing operations are no-ops. In deferred mode, non-erase output marks `dummycon_putc_called` and calls the notifier chain; blank and switch return true to request redraw, causing deferred consoles to see output after blank/switch.

State and persistence: static notifier chain and output-seen flag are protected by console lock. Console dimensions live in `vc_data`.

Dependencies and integration: VT console core, optional fbcon deferred takeover, screen_info on Footbridge, exported `dummy_con` for fallback from vgacon.

Risks: notifier registration requires console lock and warns otherwise. Deferred takeover intentionally ignores erase-only writes, so tests must distinguish real output from clears. Test signals include init dimensions, no-op scroll behavior, deferred notifier immediate callback after first output, and fallback from invalid VGA startup.
