# sources/distributed-fs/ceph-client/drivers/gpu/ipu-v3/ipu-pre.c

## Purpose
Implements the i.MX6QP IPU Prefetch Resolve Engine support used by DRM/display paths for tiled framebuffer prefetch and resolve into an intermediate IRAM buffer.

## Important APIs, Types, and Functions
`struct ipu_pre` stores list membership, device, IPU pointer, MMIO base, AXI clock, IRAM pool, allocated buffer virtual/physical addresses, and current shadow register state. Public functions include `ipu_pre_get_available_count()`, `ipu_pre_lookup_by_phandle()`, `ipu_pre_get()/put()`, `ipu_pre_configure()`, `ipu_pre_update()`, `ipu_pre_update_pending()`, `ipu_pre_get_baddr()`, and platform probe/remove. Helpers issue software reset and configure TPR tile format.

## Control Flow
Probe maps registers, gets the AXI clock, obtains the `fsl,iram` gen_pool, allocates a fixed intermediate buffer sized for `IPU_PRE_MAX_WIDTH * IPU_PRE_NUM_SCANLINES * 4`, enables the clock, and adds the instance to a global list. Users look up/get a PRE, configure dimensions, strides, modifier/tile settings, current/next buffer addresses, prefetch and store engines, then update the next buffer during scanout with `ipu_pre_update()`. Remove deletes from the list, disables the clock, and frees IRAM.

## State and Persistence
Global state is `ipu_pre_list` plus `available_pres` protected by `ipu_pre_list_mutex`. Per-engine state includes the allocated IRAM buffer, current control shadow (`pre->cur.ctrl`), and hardware registers. No disk persistence exists; IRAM allocation persists for device lifetime.

## Dependencies and Integration Points
Built only with DRM. Depends on DRM fourcc modifiers, genalloc IRAM pools, platform/OF, clk, and IPU private APIs. It integrates with `ipu-prg.c`, which obtains PRE instances for PRG channels, and with display scanout code that needs resolved/tiled buffer handling.

## Risks
IRAM availability is mandatory; probe fails if the pool or allocation is missing. Width is capped at 2048 and buffer sizing assumes four bytes per pixel over eight scanlines. Update waits/polls store-engine status and can be sensitive to scanout timing. Global list lookup by phandle must match IPU/PRG device tree relationships.

## Test Signals
Probe/remove with and without IRAM, PRE allocation exhaustion, tiled modifiers, buffer address updates during active scanout, update-pending polling, and suspend-like reconfiguration should be exercised. Display CRCs and underflow counters reveal resolve/prefetch errors.
