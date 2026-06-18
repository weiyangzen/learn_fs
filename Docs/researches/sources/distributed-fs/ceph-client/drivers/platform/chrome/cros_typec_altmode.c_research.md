<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_typec_altmode.c -->
# sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_typec_altmode.c

## Purpose

This file implements Chrome EC-backed USB Type-C alternate-mode operations for DisplayPort and Thunderbolt. It registers Type-C altmodes, translates Type-C altmode enter/exit/VDM callbacks into Chrome EC Type-C control commands, and asynchronously feeds ACK VDMs back to the Type-C altmode framework.

## Important APIs, Types, And Functions

`struct cros_typec_altmode_data` stores the Type-C altmode, owning port, SVID/mode, AP-driven mode-entry capability, VDM header/data, mutex, and work item. `struct cros_typec_dp_data` extends it with DisplayPort status/configuration state. `cros_typec_altmode_enter()` and `_exit()` issue `EC_CMD_TYPEC_CONTROL` requests. `cros_typec_displayport_vdm()` and `cros_typec_thunderbolt_vdm()` handle incoming structured VDMs. `cros_typec_displayport_status_update()` sends pending DP status ACKs after mux updates. Registration functions create Type-C altmodes and attach `cros_typec_altmode_ops`.

## Control Flow

Altmode VDM callbacks run under a mutex and stage response header/data into private state, then schedule `cros_typec_altmode_work()`. The work item calls `typec_altmode_vdm()` outside the immediate callback flow, then clears the staged packet. Enter/exit first ask the EC to enter or exit the physical mode, then synthesize an ACK VDM toward the altmode framework. DisplayPort status update is delayed until an external DP status path reports the actual mux/configuration state.

## State And Persistence

State is per-altmode and volatile: pending VDM header/data, DP configuration, `configured`, and `pending_status_update`. There is no persistence beyond EC/partner Type-C state. The mutex serializes staged VDM state with work execution.

## Dependencies And Integration Points

The file depends on `cros_ec_typec.h`, Chrome EC `EC_CMD_TYPEC_CONTROL`, the USB Type-C altmode core, DisplayPort altmode support, Thunderbolt altmode support, and USB PD VDO helpers. Build-time stubs in the header preserve basic registration when DP/TBT altmode support is disabled.

## Risks

The work item stores raw pointers to VDO data; for DP status it points into `dp_data`, but future changes must avoid stack-backed VDO pointers. Staging has only one slot, so multiple VDMs before work executes can overwrite pending data. AP-driven mode entry must be correctly advertised, or callbacks return `-EOPNOTSUPP`. Thunderbolt enter-mode handling intentionally does not ACK in this layer.

## Test Signals

Validate DP and TBT altmode registration, EC enter/exit commands, SVDM version downgrades, DP configure and status-update sequencing, mux-driven DP status ACK, concurrent VDM callback behavior, and disabled `CONFIG_TYPEC_DP_ALTMODE` or `CONFIG_TYPEC_TBT_ALTMODE` builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_typec_altmode.c -->
