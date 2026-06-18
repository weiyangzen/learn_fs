# sources/distributed-fs/ceph-client/drivers/gpu/drm/tidss/tidss_irq.h

## Purpose

`tidss_irq.h` defines the packed software IRQ status layout used by TIDSS. It maps device, writeback, video-port, and plane interrupt bits into a single `dispc_irq_t` value and declares the IRQ-management functions implemented by `tidss_irq.c`.

## Important APIs, Types, and Definitions

- Device/writeback masks include `DSS_IRQ_DEVICE_FRAMEDONEWB`, `DSS_IRQ_DEVICE_WBBUFFEROVERFLOW`, `DSS_IRQ_DEVICE_WBUNCOMPLETEERROR`, and `DSS_IRQ_DEVICE_WB_MASK`.
- Bit-position helpers `DSS_IRQ_VP_BIT_N()` and `DSS_IRQ_PLANE_BIT_N()` allocate four bits per VP and one bit per plane.
- Mask helpers `DSS_IRQ_VP_MASK()` and `DSS_IRQ_PLANE_MASK()` select all bits for a VP or plane.
- VP event macros cover frame-done, even/odd VSYNC, and sync-lost.
- Plane event macro covers FIFO underflow.
- Public functions declare vblank enable/disable, IRQ install/uninstall, and resume-mask restore.

## Control Flow

`tidss_dispc.c` translates raw hardware bits to these packed macros. `tidss_irq.c` stores and updates masks in this representation and dispatches callbacks based on it. CRTC vblank code calls the enable/disable functions declared here.

## State and Persistence Behavior

The header has no state; the packed values are stored in `tidss->irq_mask` and transient handler status variables. The layout assumes the configured `TIDSS_MAX_PORTS` and `TIDSS_MAX_PLANES` fit inside `u32`.

## Dependencies and Integration Points

It includes Linux types and `tidss_drv.h` for `dispc_irq_t` and max resource counts. It is the common dependency between the DISPC hardware translator and high-level IRQ handler.

## Risks and Edge Cases

- The comment describes a fixed bit layout; increasing resource limits can overflow or collide bits.
- `DSS_IRQ_PLANE_MASK()` currently returns a single-bit `GENMASK` and is equivalent to the underflow bit; future multi-bit plane events would require adjustment.
- Device/writeback bits are defined but not handled in the reviewed TIDSS IRQ dispatcher.

## Test Signals

Unit-style checks can validate bit positions and masks for all max VPs/planes. Integration tests should confirm that DISPC K2G and K3 translations produce the same packed bits for equivalent events and that vblank toggles affect only VSYNC bits.
