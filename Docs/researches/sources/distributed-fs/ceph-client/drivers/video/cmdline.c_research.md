# sources/distributed-fs/ceph-client/drivers/video/cmdline.c

Purpose: common `video=` kernel command-line option storage and lookup for DRM/fbdev users. It preserves global and named video options parsed at boot.

Important APIs/types/functions: `video_options[FB_MAX]` stores named `video=name:options` strings; `video_option` stores a global unnamed option; `video_of_only` gates non-OF fb users. `__video_get_option_string()` performs lookup. Exported APIs are `video_get_options()` and, when fb core is enabled, `__video_get_options()`. `video_setup()` is registered with `__setup("video=", ...)`.

Control flow: boot parsing ignores empty options, recognizes `ofonly`, stores colon-containing options in the first free named slot, and stores non-colon options as the current global option. Lookup scans all named entries and returns the last matching name prefix followed by `:`, falling back to the global option when no named option matches.

State and persistence: parsed command-line pointers are retained in read-mostly static globals for the kernel lifetime. There is no dynamic allocation.

Dependencies and integration: fb constants for `FB_MAX`, init setup infrastructure, exported symbols for DRM/fbdev display drivers.

Risks: excess named options beyond `FB_MAX` are silently dropped. Multiple matching names return the last scanned match. The `ofonly` match uses a six-byte prefix and does not require exact string termination. Tests should cover named/global precedence, duplicate named options, NULL name lookup, capacity overflow, and fb-core `is_of` gating.
