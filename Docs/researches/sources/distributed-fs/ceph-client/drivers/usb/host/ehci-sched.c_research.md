# sources/distributed-fs/ceph-client/drivers/usb/host/ehci-sched.c

## Purpose
EHCI periodic scheduler for interrupt and isochronous transfers. It manages the periodic frame list and shadow list, allocates high-speed iTD and full/low-speed split siTD descriptors, reserves high-speed and TT bandwidth, schedules URBs into microframes, scans completions, and coordinates delayed unlink/free operations.

## Important APIs, types, and functions
Periodic list helpers are `periodic_next_shadow()`, `shadow_next_periodic()`, and `periodic_unlink()`. TT and bandwidth helpers include `find_tt()`, `drop_tt()`, `compute_tt_budget()`, `reserve_release_intr_bandwidth()`, `reserve_release_iso_bandwidth()`, `check_period()`, `check_intr_schedule()`, and `qh_schedule()`. Interrupt paths use `intr_submit()`, `scan_intr()`, `qh_link_periodic()`, `start_unlink_intr_wait()`, and `end_unlink_intr()`. Iso paths use `iso_stream_find()`, `iso_stream_schedule()`, `itd_submit()`, `sitd_submit()`, `itd_link_urb()`, `sitd_link_urb()`, `itd_complete()`, `sitd_complete()`, and `scan_isoc()`.

## Control flow
Interrupt URBs share QH/qTD construction with `ehci-q.c` but run through periodic placement. The scheduler finds or reuses a phase, checks per-microframe bandwidth and TT collision/budget constraints, writes S-mask/C-mask bits, reserves bandwidth, and links the QH into all required frame-list slots sorted after iso entries. Empty interrupt QHs are unlinked after a delay so common one-URB interrupt endpoints can be reused cheaply. Iso submission builds an endpoint `ehci_iso_stream`, precomputes packet descriptors, allocates iTDs or siTDs, schedules start time with underrun and `URB_ISO_ASAP` handling, links descriptors into periodic frames, and enables the periodic schedule. Completion scanning walks from `last_iso_frame` to current frame, leaves active descriptors in current frames, removes completed descriptors, updates packet status/length/error counts, gives back URBs, and caches descriptors for delayed safe freeing.

## State and persistence behavior
State includes periodic hardware frame list, `pshadow`, interrupt QH list, iso stream lists/free lists, TT objects stored in `usb_tt->hcpriv`, global `bandwidth[]`, per-TT bandwidth, computed `tt_budget[]`, `last_iso_frame`, `now_frame`, and USB core bandwidth counters. The hardware consumes periodic descriptors asynchronously, so descriptors are cached before pool-free to avoid immediate reuse hazards.

## Dependencies and integration points
Depends on `ehci.h` QH/iTD/siTD/FSTN structures, queue helpers from `ehci-q.c`, hrtimer events from `ehci-timer.c`, USB bandwidth calculation helpers, TT topology from usbcore, and AMD PLL quirk helpers for active isochronous traffic.

## Risks and edge cases
Periodic scheduling is sensitive to off-by-one frame/microframe math, wraparound, TT carryover, and bandwidth release symmetry. Full-speed split IN scheduling avoids late uframes and does not implement all FSTN possibilities. Reusing descriptors too soon can trigger silicon corruption. URBs too far in the future return `-EFBIG`; URBs entirely in the past may complete immediately with errors counted.

## Test signals
High-speed interrupt and high-bandwidth interrupt endpoints, FS/LS interrupt behind single-TT and multi-TT hubs, bandwidth exhaustion, sysfs `uframe_periodic_max` changes, high-speed iso IN/OUT, split iso IN/OUT, `URB_ISO_ASAP`, underrun/overflow paths, queue teardown while active, descriptor free delay, and AMD PLL transitions are important tests.
