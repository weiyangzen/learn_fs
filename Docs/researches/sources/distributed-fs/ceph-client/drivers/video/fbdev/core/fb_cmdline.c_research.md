# sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fb_cmdline.c

## Purpose

This file preserves fbdev boot-command-line option compatibility through `fb_get_options()`. It bridges legacy `video=<fbname>:<options>` parsing to the common video command-line parser. The complete 61-line source was read.

## Important APIs, Types, and Functions

The exported API is `fb_get_options(const char *name, char **option)`. It calls `__video_get_options()` from `<video/cmdline.h>` and may duplicate the returned option string with `kstrdup()`.

## Control Flow

The function treats names beginning with `offb` as Open Firmware style, asks the common parser whether the framebuffer is enabled and what option string applies, treats an option beginning with `off` as disabled, optionally returns a newly allocated option string, and returns `0` when enabled or `1` otherwise.

## State and Persistence Behavior

There is no persistent state. The caller owns any allocated option string. Boot command-line data is read through the common parser.

## Dependencies and Integration Points

It integrates fbdev drivers with the generic `video=` command-line parser. Many legacy drivers call it during probe or init to honor disable and mode options.

## Risks and Edge Cases

The return convention is historical: `0` means enabled/success and `1` means disabled, not a negative errno. The `"off"` match uses a three-character prefix, so option strings beginning with those characters disable the driver. Callers must free `*option` when non-NULL according to the comment.

## Test Signals

Test absent options, `video=name:off`, `video=name:<mode>`, `offb` names, NULL `option` storage, allocation failure behavior, and callers that expect the legacy 0/1 convention.
