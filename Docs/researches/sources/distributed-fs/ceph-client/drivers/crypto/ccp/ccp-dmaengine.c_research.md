# sources/distributed-fs/ceph-client/drivers/crypto/ccp/ccp-dmaengine.c

## Purpose

`ccp-dmaengine.c` exposes CCP passthrough operations as a DMAengine memcpy/interrupt provider. It creates one DMA channel per CCP command queue, converts DMA memcpy descriptors into one or more passthrough no-DMA-map CCP commands, manages DMAengine descriptor lifecycle/cookies/status, supports pause/resume/terminate, and registers/unregisters the DMA device.

## Important APIs, Types, And Functions

- Module parameters `dma_chan_attr` and `dmaengine` control channel visibility and whether DMAengine registration occurs.
- `ccp_get_dma_chan_attr()` resolves public/private channel flags from module parameter or vdata default.
- `ccp_free_cmd_resources()`, `ccp_free_desc_resources()`, and `ccp_free_chan_resources()` release command/descriptor lists.
- `ccp_cleanup_desc_resources()` and `ccp_do_cleanup()` free acknowledged completed descriptors from a tasklet.
- `ccp_issue_next_cmd()` submits the first pending CCP command for a DMA descriptor.
- `ccp_handle_active_desc()` advances command and descriptor completion, completes cookies, unmaps descriptors, invokes callbacks, and runs dependencies.
- `__ccp_pending_to_active()` moves submitted DMA descriptors into active state.
- `ccp_cmd_callback()` handles CCP command completion and issues the next command/descriptor.
- `ccp_tx_submit()`, `ccp_prep_dma_memcpy()`, `ccp_prep_dma_interrupt()`, `ccp_issue_pending()`, `ccp_tx_status()`, `ccp_pause()`, `ccp_resume()`, and `ccp_terminate_all()` implement DMAengine channel operations.
- `ccp_dmaengine_register()` allocates channels/caches, configures `struct dma_device`, and calls `dma_async_device_register()`.
- `ccp_dmaengine_unregister()` releases channels, unregisters the DMA device, and destroys caches.

## Control Flow

Registration exits early if `dmaengine=0`. Otherwise it allocates channel array, command and descriptor slab caches, configures source/destination address widths from the DMA mask, sets `DMA_MEMCPY` and `DMA_INTERRUPT`, optionally marks channels private, initializes one channel per CCP queue, and registers the DMA device.

`prep_dma_memcpy()` wraps source and destination DMA addresses in one-entry SGs and calls `ccp_create_desc()`. Descriptor creation walks source and destination SGs in lockstep, splitting at SG boundaries, and creates a passthrough command for every segment with `CCP_CMD_PASSTHRU_NO_DMA_MAP`, no bit modification or byte swap, source/destination DMA addresses, length, final flag, and callback. Submit moves the descriptor to channel pending. `issue_pending()` splices pending descriptors to active and triggers `ccp_cmd_callback(desc, 0)` to start processing.

Each lower CCP command completion frees the active command, either issues the next segment command or completes the DMA descriptor, then moves to the next active descriptor unless paused. Descriptor completion updates DMA cookie state, unmaps descriptor resources, invokes client callback, and runs dependencies.

## State And Persistence Behavior

Device state includes DMA device registration, per-queue DMA channels, slab caches, and channel lists (`created`, `pending`, `active`, `complete`) protected by spinlocks. Descriptor state stores DMAengine status, cookie, length, pending/active CCP commands, and callbacks. Completed descriptors remain on `complete` until acknowledged and cleaned by tasklet.

## Dependencies And Integration Points

This file depends on Linux DMAengine APIs, DMA mapping metadata, CCP command enqueue API, passthrough no-map command support in `linux/ccp.h`/operation layer, and queue count from `struct ccp_device`. It is called from v3/v5 device init/destroy.

## Risks And Edge Cases

- `GFP_NOWAIT` allocations in prep paths can fail under pressure, returning no descriptor.
- Pause and terminate contain TODOs about waiting for active DMA; active hardware commands may still complete after state changes.
- `ccp_prep_dma_interrupt()` creates a descriptor with no pending CCP commands; issue/completion behavior relies on the descriptor handling path accepting empty descriptors.
- Terminate frees active/pending/created descriptors but leaves complete descriptors unless acknowledged cleanup runs.
- Channel public/private visibility can be overridden globally, which may expose DMA channels not intended by platform vdata.

## Test Signals

Signals include DMAengine memcpy correctness for single and multi-SG transfers, cookie/status transitions, client callback invocation and dependency running, pause/resume behavior, terminate under active load, private/public channel attributes, `dmaengine=0` behavior, allocation failure handling, and module unload with clients attached.
