# sources/distributed-fs/ceph-client/include/video/pmagb-b-fb.h

## Purpose
`pmagb-b-fb.h` defines resource offsets and video timing field encodings for the TURBOchannel PMAGB-B Smart Frame Buffer card.

## Important APIs, Types, and Functions
Resource offsets cover option ROM, SFB ASIC, general-purpose outputs, Bt459 RAMDAC, framebuffer memory, and total size. SFB register offsets include horizontal/vertical video setup, video base address, and TURBOchannel/video clock counters. Field macros define back-porch, sync, front-porch, active-pixel/scan-line shifts and masks, base-row mask, and Bt459 byte-wide address/data/cmap offsets.

## Control Flow
The driver maps the card aperture, programs SFB timing registers by packing porch/sync/active fields, sets video base row, optionally reads clock counters, and configures the Bt459 palette through its byte-wide window.

## State and Persistence Behavior
Framebuffer memory, timing registers, GP outputs, and RAMDAC state are hardware state. No software state is defined in this header.

## Dependencies and Integration Points
It integrates TURBOchannel SFB hardware with DEC framebuffer drivers, mode timing setup, palette programming, and framebuffer memory mapping.

## Risks and Test Signals
Risks include incorrect shift/mask packing for timing fields, active pixel/line limits, video base row alignment, byte-wide Bt459 access mistakes, and confusion with PMAG-BA offsets. Test signals include known-resolution mode programming, palette update, framebuffer base panning if supported, clock-counter reads, and console display on PMAGB-B hardware.
