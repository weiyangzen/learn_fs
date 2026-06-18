# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/efx_common.h

Purpose: Declares shared lifecycle, IO, reset, MAC, netdev, feature, stats, PCI error, and representor helper APIs for the SFC driver.

Important APIs and definitions: Defines queue-size constants `EFX_MAX_DMAQ_SIZE`, `EFX_DEFAULT_DMAQ_SIZE`, `EFX_MIN_DMAQ_SIZE`, `EFX_MAX_EVQ_SIZE`, and `EFX_MIN_EVQ_SIZE`; declares IO/struct init/fini, start/stop, reset workqueue, monitor, reset down/up/schedule, MAC and feature handlers, MTU/XDP max, PCI error handlers, features check, physical port helpers, and representor attach/detach. Inline helpers include `EFX_ASSERT_RESET_SERIALISED()`, `efx_check_disabled()`, `efx_schedule_channel()`, and `efx_schedule_channel_irq()`.

Control flow and integration: Used by core PCI/netdev code, channel code, ethtool, SR-IOV, and NIC-specific modules to share reset/start/stop and netdev operations. The channel scheduling helpers bridge interrupt handlers to NAPI.

State and persistence: Header owns no state. Constants determine default queue allocations and ring bounds. Inline helpers inspect or mutate NAPI scheduling and disabled/recovering device state.

Dependencies: Relies on shared driver types and Linux netdev/NAPI/PCI types. Optional MCDI logging declarations depend on `CONFIG_SFC_MCDI_LOGGING`.

Risks: Reset serialization macro assumes RTNL for active states; callers outside expected contexts can race resets. Queue constants must remain compatible with hardware descriptor limits. Disabled-state checks prevent operations after serious errors but can expose user-visible `-EIO`.

Test signals: Compile all users, reset paths under RTNL, interrupt scheduling from IRQ context, queue-size ethtool operations, MCDI logging builds enabled/disabled, and operations on disabled or recovering devices.
