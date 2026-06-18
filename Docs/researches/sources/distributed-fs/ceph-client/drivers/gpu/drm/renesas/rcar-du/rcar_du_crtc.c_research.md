# sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rcar-du/rcar_du_crtc.c

## Purpose

`rcar_du_crtc.c` implements R-Car DU CRTC objects and runtime display-channel control. It programs display timings and clocks, handles start/stop, page flips, vblank IRQs, CMM setup, VSP clock/source integration, CRC source control, and CRTC creation for Gen2/Gen3/Gen4 hardware variants.

## Important APIs, Types, and Functions

- Register access helpers offset CRTC registers by `rcrtc->mmio_offset`; `rcar_du_crtc_dsysr_clr_set()` updates cached `dsysr` and writes DSYSR.
- Clock/timing helpers include `rcar_du_dpll_divider()`, `rcar_du_escr_divider()`, and `rcar_du_crtc_set_display_timing()`.
- Plane composition is updated by `rcar_du_crtc_update_planes()`, which sorts visible planes by zpos, writes DS1PR/DS2PR, updates DPTSR association, and restarts groups when required.
- Page flip helpers are `rcar_du_crtc_finish_page_flip()`, `rcar_du_crtc_page_flip_pending()`, and `rcar_du_crtc_wait_page_flip()`.
- CMM helpers `rcar_du_cmm_check()` and `rcar_du_cmm_setup()` validate and apply gamma LUTs.
- Lifecycle helpers are `rcar_du_crtc_get()`, `rcar_du_crtc_put()`, `rcar_du_crtc_start()`, `rcar_du_crtc_disable_planes()`, and `rcar_du_crtc_stop()`.
- Atomic hooks implement check, begin, flush, enable, disable, and mode validation.
- CRC helpers build source names, parse/verify/set CRC source through atomic commits, and expose Gen3 CRC callbacks.
- `rcar_du_crtc_irq()` handles vblank status, acknowledges interrupts, wakes waiters, and completes page flips on Gen2.
- `rcar_du_crtc_create()` creates DRM CRTCs, selects primary plane, wires CMM/color management, requests IRQs, and initializes CRC sources.

## Control Flow

CRTC creation resolves functional and optional external clocks, initializes wait queues/locks/state, selects the primary plane from VSP or DU planes, initializes the DRM CRTC, links CMM and gamma properties if available, registers helper callbacks, requests the correct IRQ, and prepares CRC sources for Gen3+.

Atomic enable powers CMM, gets/enables clocks and group resources, programs display timings and routing, optionally enables LVDS/DSI pixel clocks early, starts the DU group, and applies CMM LUT setup. Atomic begin ensures the CRTC is initialized before plane programming and applies color-management-only updates. Atomic flush updates plane assignment/registers, captures page-flip events under event lock, and flushes VSP if used. Atomic disable stops the CRTC, releases resources, disables companion pixel clocks, and completes any pending event.

Stop sequencing disables planes and waits for vblank so stale framebuffers are not scanned after restart, waits for page flips, turns vblank off, disables VSP and CMM, switches sync mode if supported, and stops the group.

## State and Persistence Behavior

Driver state in `struct rcar_du_crtc` includes cached DSYSR, initialized flag, vblank enabled flag, pending flip event, wait queues, vblank countdown, group/CMM/VSP links, CRC source strings, and writeback connector. Hardware state includes clocks, DPLL/ESCR, timing registers, DSMR polarity, DSYSR start/reset/sync bits, DS1PR/DS2PR plane priorities, DPTSR associations, interrupt enable/status, CMM routing, and bridge-provided pixel clocks.

## Dependencies and Integration Points

- Depends on DRM atomic helpers, vblank, bridge, CRTC state, writeback, GEM DMA scanout, and event locking.
- Integrates with R-Car group, plane, KMS, CMM, VSP, LVDS, MIPI DSI, and register headers.
- Uses media `vsp1_du_crc_config` for CRC source state.

## Risks and Edge Cases

- DPTSR and source changes require group restarts, producing visible flicker by design.
- CMM adds a 25-pixel timing offset and stricter mode-valid constraints; routing CMM when no color management is used is a TODO.
- Page flip timeout forcibly completes the event after 50 ms, which preserves userspace progress but can hide lost interrupts or hardware stalls.
- `drm_crtc_vblank_get()` warning in atomic flush assumes vblank can always be acquired when events are queued.
- DPLL calculations are optimized for 64-bit arithmetic and only used on 64-bit-capable paths; future 32-bit usage could overflow.
- Early LVDS/DSI pixel clock enable/disable must match bridge behavior and output bitmasks exactly.

## Test Signals

- Mode tests should cover interlaced rejection, minimum porch constraints, CMM and non-CMM timing offsets, DPLL channels, external dot clocks, LVDS/DSI clock routing, and Gen2 versus Gen3 limits.
- Atomic tests should validate enable/begin/flush/disable ordering, pending event completion, group restart conditions, and plane priority/zpos ordering.
- IRQ tests should verify vblank ack, vblank wait countdown, page flip completion, and shared IRQ behavior on older hardware.
- CRC tests should list `auto` and `plane<ID>` sources, reject invalid names, and apply source changes through atomic commits.
