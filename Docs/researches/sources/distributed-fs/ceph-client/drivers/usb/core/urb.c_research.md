# sources/distributed-fs/ceph-client/drivers/usb/core/urb.c

## Purpose
Implements USB Request Block allocation, reference counting, anchoring, validation, submission, cancellation, poisoning, and wait helpers. It is the central policy layer between USB drivers and HCD transfer queues.

## Important APIs, Types, And Functions
URB lifetime APIs are `usb_init_urb()`, `usb_alloc_urb()`, `usb_free_urb()`, and `usb_get_urb()`. Anchor APIs include `usb_anchor_urb()`, `usb_unanchor_urb()`, `usb_kill_anchored_urbs()`, `usb_poison_anchored_urbs()`, `usb_unpoison_anchored_urbs()`, `usb_anchor_suspend_wakeups()`, `usb_anchor_resume_wakeups()`, `usb_wait_anchor_empty_timeout()`, `usb_get_from_anchor()`, `usb_scuttle_anchored_urbs()`, and `usb_anchor_empty()`. Transfer APIs include `usb_pipe_type_check()`, `usb_urb_ep_type_check()`, `usb_submit_urb()`, `usb_unlink_urb()`, `usb_kill_urb()`, `usb_poison_urb()`, `usb_unpoison_urb()`, and `usb_block_urb()`.

## Control Flow
Allocation creates flexible URBs with optional isochronous frame descriptors and initializes krefs/lists. Submission validates the URB, rejects active or disconnected devices, resolves the endpoint from the pipe, checks control setup direction/length, clears internal transfer flags, records direction, calls KMSAN handling, rejects non-control transfers before configuration, validates max packet and isochronous packet sizes including SuperSpeed/SuperSpeedPlus/eUSB2 rules, checks SG segment alignment, clamps/validates transfer length, warns about pipe type and illegal flags, normalizes periodic intervals, then delegates to `usb_hcd_submit_urb()`.

Unlinking delegates asynchronously to the HCD with `-ECONNRESET`. `usb_kill_urb()` and `usb_poison_urb()` increment `reject`, use memory barriers to block resubmission, unlink with `-ENOENT`, and wait for `use_count` to drop. Anchors hold references to grouped URBs; kill/poison helpers repeatedly take a reference to the newest anchored URB, kill or poison it outside the anchor lock, and loop until the list is empty and wakeups are no longer suspended.

## State And Persistence
All state is memory-only. URBs carry krefs, transfer buffers, endpoint pointers, status, actual length, flags, interval, reject count, use count, and anchor linkage. Anchors maintain a spinlocked list, poison state, wait queue, and suspended wakeup count. There is no persistent storage.

## Dependencies And Integration Points
Depends on HCD submit/unlink/giveback APIs, endpoint descriptors, USB pipe macros, scatterlist, KMSAN, wait queues, krefs, atomics, and memory barriers. It is used by virtually every USB class driver and by synchronous wrappers in `message.c`.

## Risks And Test Signals
High-risk areas include URB lifetime during completion, resubmission races with kill/poison, anchor wakeup suppression, illegal flag sanitization that warns but still masks, periodic interval normalization, isochronous packet size calculations, SG alignment constraints, and control setup/pipe direction mismatches. Test signals include invalid URB submissions, disconnect during active URBs, completion handlers that resubmit while kill/poison runs, anchor empty waits, isochronous boundary cases across speeds, SG bulk submissions, KMSAN/sanitizer runs, and HCD fault injection.
