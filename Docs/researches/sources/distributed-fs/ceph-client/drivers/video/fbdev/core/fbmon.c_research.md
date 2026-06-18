<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fbmon.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fbmon.c

## Purpose

`fbmon.c` parses monitor EDID data, builds fbdev mode databases from EDID descriptors, computes VESA Generalized Timing Formula modes, converts generic `videomode` objects to fbdev modes, validates modes against monitor specs, and exposes firmware EDID for primary adapters. The file was read as a complete 1525-line source.

## Important APIs, Types, and Functions

Exported APIs are `fb_parse_edid`, `fb_edid_to_monspecs`, `fb_get_mode`, `fb_validate_mode`, `fb_destroy_modedb`, `fb_firmware_edid`, and optionally `fb_videomode_from_videomode` and `of_get_fb_videomode`. Internal helpers classify EDID descriptor blocks, repair known-bad EDIDs via `brokendb`, check header/checksum, parse vendor/display/chroma/DPMS data, derive established/standard/detailed timings, create a `struct fb_videomode` array, estimate monitor limits, and compute GTF timings using `struct __fb_timings`.

## Control Flow

EDID paths apply known fixups and validate checksum/header. `fb_parse_edid()` returns the first detailed timing in `fb_var_screeninfo`. `fb_edid_to_monspecs()` fills `struct fb_monspecs`, parses vendor strings and descriptors, derives limits, populates capabilities, creates `specs->modedb`, and clears the preferred-detailed flag if needed. `fb_create_modedb()` collects detailed, established, standard, and descriptor standard timings into a compact allocated array. `fb_get_mode()` calculates GTF timings from requested vertical refresh, horizontal frequency, pixel clock, or maximum monitor limits.

## State and Persistence Behavior

The file owns static EDID fixup tables. Mode databases are dynamically allocated and owned by callers until `fb_destroy_modedb()`. `fb_edid_to_monspecs()` stores parsed fields and allocated mode database in caller-provided `struct fb_monspecs`.

## Dependencies and Integration Points

It integrates with `modedb.c` tables, fbdev monitor structures, firmware/sysfb EDID, PCI ROM resource flags, devicetree videomode helpers, and display timing flags. Fbdev drivers typically consume it during probe and mode validation.

## Risks and Edge Cases

EDID parsing is byte-offset heavy and depends on descriptor macros. Malformed EDID can produce no modes or require fixups. GTF integer math can reject modes outside monitor limits and uses safe 640x480 defaults when specs are invalid. Firmware EDID is returned only for shadow-ROM primary devices.

## Test Signals

Use valid EDIDs, all-null/bad-checksum headers, known broken DEC/ViewSonic/Sharp entries, EDIDs with no detailed timings, high pixel-clock modes, standard timing descriptors, devicetree display timings, GTF generation under each flag, and validation against hfreq/vfreq/dclk bounds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fbmon.c -->
