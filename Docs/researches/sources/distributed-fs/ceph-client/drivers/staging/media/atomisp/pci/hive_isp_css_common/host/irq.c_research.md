# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/irq.c

## Purpose

`irq.c` programs IRQ controller masks, enables, edge/pulse behavior, clears, software IRQ raising, nested virtual IRQ mapping, and IRQ status collection..

## Important APIs, Types, And Data

Key includes: `assert_support.h`, `irq.h`, `gp_device.h`, `irq_private.h`. Important macros/constants include `__INLINE_GP_DEVICE__`. Important types include `return`. Important functions include `irq_wait_for_write_complete()`, `any_irq_channel_enabled()`, `irq_clear_all()`, `irq_enable_channel()`, `irq_enable_pulse()`, `irq_disable_channel()`, `irq_get_channel_id()`, `irq_raise()`, `any_virq_signal()`, `cnd_virq_enable_channel()`, `virq_clear_all()`, `virq_get_channel_signals()`.

## Control Flow

`irq_enable_channel()` reads mask/enable/edge registers, masks the target bit, programs rising-edge input behavior, enables output, clears stale status, unmasks the bit, and forces completion with a readback. `irq_disable_channel()` clears enable/mask bits and clears status. Virtual IRQ helpers map the flat `enum virq_id` space into nested IRQ controllers, enable or disable parent IRQ0 routes when nested controllers become active or empty, and collect or clear status from all enabled controllers.

## State And Persistence Behavior

Software state is limited to static mapping tables for channel counts, ID offsets, and nesting routes. Persistent state is held in IRQ controller mask, enable, edge, edge-not-pulse, clear/status registers and in GP-device software IRQ request registers.

## Dependencies And Integration Points

Dependencies are local to the AtomISP CSS host stack: `type_support.h` scalar types, `system_global.h`/`system_local.h` base addresses and IDs, block-specific public/private headers, `assert_support.h`, `device_access.h` or `ia_css_device_access.h`, and low-level HRT register/memory operations. Integration points are the higher-level CSS pipeline code that configures sensors, DMA, GDC, input formatting, IRQ delivery, SP/ISP execution, and diagnostics through these wrappers.

## Risks And Edge Cases

- Most validation relies on `assert()`/`OP___assert()`, so production builds with assertions disabled may convert bad IDs, sizes, or enum values into invalid hardware accesses.
- The code is tightly coupled to RTL register indexes, bit positions, and shared firmware layouts; a one-bit drift can silently program the wrong CSS block.
- Many helpers are thin wrappers around MMIO or firmware memory and do not serialize concurrent callers, so sequencing must be enforced by the higher-level CSS pipeline.

## Test Signals

- Build AtomISP with the relevant CSS blocks enabled and with both inline and out-of-line helper configurations where supported.
- Run static checks that compare register indexes, bit widths, enum ranges, and shared struct sizes against the generated hardware definitions.
- Exercise representative sensor/input-system startup, DMA transfers, GDC LUT programming, IRQ delivery/clear, FIFO monitor snapshots, SP/ISP start/idle, and debug-buffer reads on hardware or the HSS/simulation model.
