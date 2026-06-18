# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/cadence/cdns-mhdp8546-core.h

# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/cadence/cdns-mhdp8546-core.h

## Purpose

This header defines MHDP8546 register offsets, firmware mailbox opcodes, DP link capability structures, platform hooks, bridge state, HDCP state, and the main device object shared by the core, HDCP, and J721E wrapper files.

## Important APIs, Types, And Functions

Key structures are `cdns_mhdp_link`, `cdns_mhdp_host`, `cdns_mhdp_sink`, `cdns_mhdp_display_fmt`, `mhdp_platform_ops`, `cdns_mhdp_bridge_state`, `cdns_mhdp_platform_info`, `cdns_mhdp_hdcp`, and `cdns_mhdp_device`. It declares `cdns_mhdp_wait_for_sw_event()`. Constants cover APB/mailbox registers, DP framer registers, mailbox modules, firmware name, HPD events, lane mapping, link training, and HDCP SW events.

## Control Flow

The header has no executable flow, but it encodes the control contract: core mailbox commands use module/opcode constants, video setup uses framer register macros, wrappers provide `init/exit/enable/disable`, and HDCP waits for SW events produced by the core IRQ handler.

## State And Persistence Behavior

`struct cdns_mhdp_device` centralizes all mutable runtime state: MMIO bases, clocks/PHY, AUX, bridge, link caps, DP sink/source caps, display format, HPD/link flags, locks, wait queues, work structs, firmware state, and HDCP fields. State is volatile and reconstructed on probe/firmware load/modeset.

## Dependencies And Integration Points

It depends on DRM DP helper, DRM bridge/connector, mutex/spinlock APIs, and forward declarations for clock/device/PHY. The HDCP and J721E files include it to access device state and shared constants.

## Risks And Test Signals

Register macro mistakes can silently misprogram hardware. Locking comments document important concurrency contracts; violations can race firmware callback, bridge detach, IRQ masking, or link training. Build coverage across core, HDCP, and J721E configs validates type visibility and optional integrations.
