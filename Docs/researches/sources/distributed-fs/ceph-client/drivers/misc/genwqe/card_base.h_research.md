# sources/distributed-fs/ceph-client/drivers/misc/genwqe/card_base.h

## Purpose
Private GenWQE module header defining shared constants, core state structures, request/mapping types, and cross-file function prototypes used by the GenWQE driver implementation.

## Important APIs, Types, And Functions
Important definitions include PCI IDs, card limits, DDCB timeout defaults, debug unit IDs, FFDC structures, error-injection flags, `struct dma_mapping`, `struct ddcb_queue`, `struct genwqe_dev`, `struct genwqe_sgl`, `struct ddcb_requ`, and `struct genwqe_file`. Inline helpers include `genwqe_mapping_init()`, `genwqe_get_slu_id()`, `dma_mapping_used()`, and `genwqe_is_privileged()`. Prototypes cover service-layer setup, DDCB execution, char-device creation, debugfs, FFDC reads, register access, DMA allocation, SGL setup, CRC, app ID, and trap control.

## Control Flow
This file does not execute control flow directly, but it defines the lifecycle contracts used by `card_base.c` and sibling files. A `genwqe_dev` is allocated at PCI probe, populated by PCI setup, used by service-layer and char-device code, monitored by the health thread, and freed at remove. `ddcb_requ` and `ddcb_queue` model request submission, queue slots, wait queues, and completion state for DDCB execution. `genwqe_file` tracks per-open mappings and async notification.

## State, Persistence, And Dependencies
The header describes all major volatile GenWQE state: MMIO, FFDC buffers, DDCB queue, health/card threads, cdev/class/debugfs handles, VF settings, cached register values, open files, and DMA mappings. Persistent state is hardware-owned and accessed through the declared register and DDCB helpers. Dependencies include PCI, cdev, semaphores, uaccess, I/O accessors, debugfs, Linux GenWQE UAPI, and local `genwqe_driver.h`.

## Integration Points
Every GenWQE object file depends on this header for shared structure layout. It bridges kernel-private implementation with public `include/linux/genwqe/genwqe_card.h` UAPI structures. Function prototypes make `card_base.c` the lifecycle owner while delegating DDCB, device, sysfs/debugfs, utilities, and memory mapping.

## Risks
Because this is a private shared header, structure layout changes can silently break assumptions across GenWQE source files. DMA mapping state must be kept consistent across map, pin, execute, and cleanup paths. Comments describe fragile recovery behavior when user file descriptors survive device teardown. Error-injection flags are useful for tests but dangerous if exposed without proper privilege checks.

## Test Signals
Compile coverage is the main signal: all GenWQE objects should build after structure/prototype changes. Runtime tests should cover DDCB request state transitions, DMA mapping lifecycle, open-file cleanup, FFDC buffer sizing, privilege detection, and all callers of declared register accessors.
