# sources/distributed-fs/ceph-client/include/linux/fbcon.h

## Purpose

`sources/distributed-fs/ceph-client/include/linux/fbcon.h` declares the framebuffer console integration hooks used by fbdev registration, mode changes, blanking, suspend/resume, and console-to-fb mappings. The source was read as a complete 55-line file for this report.

## Important APIs, Types, and Functions

Key functions are `fb_console_init`, `fb_console_exit`, `fbcon_fb_registered`, `fbcon_fb_unregistered`, `fbcon_fb_unbind`, `fbcon_suspended`, `fbcon_resumed`, `fbcon_mode_deleted`, `fbcon_delete_modelist`, `fbcon_new_modelist`, `fbcon_get_requirement`, `fbcon_fb_blanked`, `fbcon_modechange_possible`, `fbcon_update_vcs`, `fbcon_remap_all`, and console mapping ioctls. Disabled `CONFIG_FRAMEBUFFER_CONSOLE` builds provide no-op or zero-return inline stubs.

## Control Flow

fbdev core calls these hooks as framebuffers appear, disappear, change modes, blank, or suspend. fbcon then updates virtual consoles, font/blit requirements, and console mappings.

## State and Persistence Behavior

The header owns no state. fbcon state lives in console, vc, and framebuffer console internals.

## Dependencies and Integration Points

It forward-declares fb structures and depends on compiler attributes. It integrates the fbdev core with the virtual terminal console layer.

## Risks and Edge Cases

Disabled stubs make framebuffer devices usable without console support but can hide fbcon-specific regressions. Mode deletion and remapping must avoid stale modelist or console mappings.

## Test Signals

Builds with and without `CONFIG_FRAMEBUFFER_CONSOLE`, framebuffer registration tests, VT switch/remap ioctl tests, suspend/resume and blanking tests, and mode deletion tests.
