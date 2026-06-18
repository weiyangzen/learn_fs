
# sources/distributed-fs/ceph-client/drivers/media/pci/ttpci/budget.h

## Purpose
This header defines the shared object model and exported interface for SAA7146 budget DVB drivers. It gives board-specific modules a common `struct budget`, board type constants, debug macro, helper macro for PCI extension data, and prototypes for initialization, teardown, IRQ, video-port, and DEBI access.

## Important APIs, Types, And Functions
`struct budget_info` stores the human-readable board name and board type. `struct budget` aggregates DVB adapter/device/network/demux/dmxdev frontends, SAA7146 device pointer, I2C adapter, DMA buffer and page table, bottom-half work items, feed/capture state, locks, frontend hooks, and a `priv` pointer. `MAKE_BUDGET_INFO` constructs a `budget_info` plus `saa7146_pci_extension_data` linked to the external `budget_extension`. Public functions include `ttpci_budget_init`, `ttpci_budget_init_hooks`, `ttpci_budget_deinit`, `ttpci_budget_irq10_handler`, `ttpci_budget_set_video_port`, `ttpci_budget_debiread`, and `ttpci_budget_debiwrite`.

## Control Flow
The header itself has no runtime flow, but it defines the contract used by board modules: allocate/own `struct budget`, call the common init, attach a frontend, call hook initialization, then deinitialize through the common teardown. IRQ and DEBI helpers are called from SAA7146 extension callbacks and board-specific hardware helpers.

## State And Persistence
All fields are volatile driver state. Important state fields include `feeding`, `fe_synced`, `video_port`, buffer size/geometry, `ttbp`, warning counters, frontend pointer, original `read_fe_status`, and lock objects. No persistent data format is defined.

## Dependencies And Integration Points
The header includes Linux module/mutex/workqueue APIs, DVB core headers, and `media/drv-intf/saa7146.h`. It is included by common and board-specific budget sources and exports `budget_debug` for the `dprintk` macro.

## Risks
Because `struct budget` is shared across multiple modules, field layout and semantics are cross-file ABI within the kernel build. The macro assumes an in-scope `budget_extension` symbol, which is convenient but implicit. Feed and frontend state fields require callers to respect the locking discipline established in `budget-core.c`.

## Test Signals
Compile coverage is the primary signal for this header: all budget variants should build with the same struct and prototypes. Runtime signals include successful sharing of `dev->ext_priv`, frontend hook replacement through `dvb_adapter.priv`, and absence of lockdep issues around `feedlock`/`debilock`.
