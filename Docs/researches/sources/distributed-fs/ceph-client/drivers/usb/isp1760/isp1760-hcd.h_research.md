# sources/distributed-fs/ceph-client/drivers/usb/isp1760/isp1760-hcd.h

## Purpose
`isp1760-hcd.h` defines host-controller private state, memory-layout descriptors, slot tracking, queue categories, and HCD registration/cache APIs. It also provides no-op inline stubs when host role support is not compiled.

## Important APIs, Types, And Functions
`struct isp1760_slotinfo` binds a PTD slot to an active QH/QTD and timestamp. `struct isp1760_memory_layout` describes chip payload memory block counts, block sizes, slot count, payload block count, and payload area size. `struct isp1760_memory_chunk` tracks runtime allocation units. `enum isp1760_queue_head_types` separates control, bulk, and interrupt queues. `struct isp1760_hcd` stores USB HCD pointer, MMIO base, regmap/fields, variant flag, memory layout, spinlock, slot arrays, done maps, memory pool, QH lists, and root-hub scheduling/timing fields.

Public HCD functions are `isp1760_hcd_register()`, `isp1760_hcd_unregister()`, `isp1760_init_kmem_once()`, and `isp1760_deinit_kmem_cache()`, or stubs when disabled.

## Control Flow
The header has no standalone execution. Core registration fills regmaps and memory layout before calling `isp1760_hcd_register()`. The HCD implementation mutates the declared state under `lock` during enqueue, completion, dequeue, and hub control.

## State And Persistence
The structures define all host-side volatile state for a bound controller. PTD slot state and memory-pool state mirror hardware use and must be synchronized with skip/done maps and payload allocations.

## Dependencies And Integration Points
The header depends on spinlocks, regmap, local register enums, USB HCD declarations, and Kconfig. It is included by core so `struct isp1760_device` can embed HCD state.

## Risks
Constants `ISP176x_BLOCK_MAX` and `ISP176x_BLOCK_NUM` must match all memory layouts. If a new chip has more block classes or payload blocks, both array sizes and allocation loops need review. Inline stubs returning success mean core code can call HCD registration unconditionally in disabled builds, but a wrong Kconfig selection could hide missing host support until runtime.

## Test Signals
Build host-disabled and host-enabled configurations. Runtime host tests should monitor slot arrays and memory chunks for leaks after transfer enqueue/dequeue, endpoint disable, and controller unregister.
