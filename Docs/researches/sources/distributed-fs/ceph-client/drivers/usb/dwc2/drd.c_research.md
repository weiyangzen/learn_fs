<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc2/drd.c -->
# sources/distributed-fs/ceph-client/drivers/usb/dwc2/drd.c

## Purpose
`drd.c` implements DWC2 dual-role integration with the Linux USB role-switch framework. It translates role-switch requests into GOTGCTL session-valid overrides and controller mode forcing, and preserves role behavior across suspend/resume.

## Important APIs, types, and functions
The public functions are `dwc2_drd_init`, `dwc2_drd_suspend`, `dwc2_drd_resume`, and `dwc2_drd_exit`. Internal helpers are `dwc2_ovr_init`, `dwc2_ovr_avalid`, `dwc2_ovr_bvalid`, and `dwc2_drd_role_sw_set`. The key macro `dwc2_ovr_gotgctl` enables B/A/VBUS valid overrides and bypasses the debounce filter.

## Control flow
`dwc2_drd_init` only acts when firmware has `usb-role-switch`; it reads the default mode, registers a userspace-controllable role switch, stores it on `hsotg`, then initializes override bits. Role changes reject requests incompatible with fixed `dr_mode`, reject dropping to none while gadget test mode is active, temporarily enable the clock if low-level hardware is off, take the spinlock, map `USB_ROLE_NONE` to a configured default if any, exit gadget clock gating if needed, set A-session or B-session validity, connect/disconnect gadget soft state when appropriate, release the lock, force host/device mode for OTG if the session actually changed, and disable the temporary clock. Suspend masks connector-ID changes for role-switch-managed controllers; resume restores the last role/default, forces mode, and unmasks connector-ID changes. Exit unregisters the role switch.

## State and persistence behavior
Runtime state lives in `hsotg->role_sw`, `role_sw_default_mode`, `dr_mode`, `ll_hw_enabled`, `test_mode`, `lx_state`, `bus_suspended`, and GOTGCTL/GUSBCFG hardware bits. The last role is retrieved from the role-switch framework during resume; no disk persistence exists.

## Dependencies and integration points
It integrates DWC2 with firmware properties, fwnode/device property APIs, USB role-switch, platform clock control, the common DWC2 lock and MMIO helpers, gadget connect/disconnect helpers, clock-gating exit helpers, and `dwc2_force_mode`. It is always compiled into the core DWC2 object, but most useful behavior depends on role-switch firmware data and dual-role-capable configuration.

## Risks
Role switching touches clocks, spinlocks, register overrides, gadget connection state, and forced mode, so ordering is sensitive. Returning success for `-EALREADY` session states is intentional but can hide no-op changes. Temporary clock enable must be balanced on all paths. Forcing mode after releasing the lock can race with cable/interrupt changes. Test mode blocks role-none only in gadget-capable builds.

## Test signals
Test firmware with and without `usb-role-switch`, default host/peripheral/none modes, userspace role changes among host/device/none, fixed host/peripheral `dr_mode` rejection, boot with cable already plugged while clocks are off, suspend/resume preserving role, connector-ID interrupt masking/unmasking, gadget test mode blocking role-none, and repeated role toggling under lockdep and clock framework debug.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc2/drd.c -->
