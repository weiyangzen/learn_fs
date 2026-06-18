<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc2/core_intr.c -->
# sources/distributed-fs/ceph-client/drivers/usb/dwc2/core_intr.c

## Purpose
`core_intr.c` implements common DWC2 interrupt handling shared by host and device modes. It handles OTG events, connector ID changes, session requests, wakeup/resume, USB suspend, LPM L1 transitions, disconnects, port interrupts observed in device mode, and GPWRDN hibernation wake events.

## Important APIs, types, and functions
The exported entry point is `dwc2_handle_common_intr`. Important helpers include `dwc2_op_state_str`, `dwc2_handle_usb_port_intr`, `dwc2_handle_mode_mismatch_intr`, `dwc2_handle_otg_intr`, `dwc2_handle_conn_id_status_change_intr`, `dwc2_handle_session_req_intr`, `dwc2_wakeup_from_lpm_l1`, `dwc2_handle_wakeup_detected_intr`, `dwc2_handle_disconnect_intr`, `dwc2_handle_usb_suspend_intr`, `dwc2_handle_lpm_intr`, `dwc2_read_common_intr`, `dwc_handle_gpwrdn_disc_det`, and `dwc2_handle_gpwrdn_intr`.

## Control flow
The IRQ entry takes `hsotg->lock`, verifies the controller is alive, snapshots the current frame number from `DSTS` or `HFNUM`, masks common interrupts through `GINTSTS`, `GINTMSK`, and global interrupt enable, and dispatches handlers. Hibernated controllers bypass normal `GINTSTS` handling and use `GPWRDN` bits. OTG interrupts update `op_state`, clear HNP/SRP status, and may start or disconnect the host controller while temporarily dropping the spinlock. Connector ID changes clear and mask SOF, then queue OTG work. Session request wakes device low-power state or powers host port and connects HCD. Suspend paths choose partial power down, hibernation, or clock gating. LPM transitions place the gadget in L1 and call suspend callbacks; wake exits L1/L2 and calls resume as appropriate.

## State and persistence behavior
The file mutates `op_state`, `lx_state`, `frame_number`, `srp_success`, `hibernated`, `bus_suspended`, and power-down/clock-gating state. It writes many clear-on-write interrupt registers (`GINTSTS`, `GOTGINT`, `GPWRDN`) and relies on hardware interrupt masks. State is volatile in memory and hardware registers, with no disk persistence.

## Dependencies and integration points
It depends on `core.h`, `hcd.h`, host start/connect/disconnect helpers, gadget connect/disconnect/suspend/resume helpers, power management routines in `core.c`, USB PHY suspend handling, timers/workqueues, and low-level register definitions. It is the bridge from the platform IRQ registration to host and gadget mode-specific interrupt handlers.

## Risks
Interrupt handlers mix hardware register clears, state transitions, callbacks, timers, and lock dropping, so races are the main risk. Incorrect clearing can lose interrupts or cause storms, especially restore-done and GPWRDN wake cases. LPM L1 wake has timeout paths that reinitialize LPM but do not report a hard failure to the IRQ caller. HNP/mode transitions depend on revision-specific delays and can fail on marginal hardware. Calling host/gadget callbacks with state changes in progress requires strong lockdep and stress coverage.

## Test signals
Exercise cable attach/detach, ID pin changes, B-device SRP, HNP transitions, host and gadget suspend/resume, L1 LPM entry/exit with remote wakeup, partial power down, hibernation wake by disconnect/line-state/reset/status-change, dead-controller IRQ handling, and port enable-change in device mode. Logs for `Mode Mismatch`, timeout warnings, restore-done, GPWRDN reasons, and lockdep reports are key diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc2/core_intr.c -->
