# sources/distributed-fs/ceph-client/drivers/usb/mtu3/mtu3_dr.c

## Purpose

`mtu3_dr.c` implements MTU3 dual-role switching. It changes port0 between host and device ownership, controls VBUS, handles extcon or USB role-switch requests, supports manual debugfs switching, and programs forced IDDIG mode.

## Important APIs, Types, and Functions

Key public functions are `ssusb_otg_switch_init()`, `ssusb_otg_switch_exit()`, `ssusb_mode_switch()`, `ssusb_set_vbus()`, and `ssusb_set_force_mode()`. Internal helpers include `ssusb_port0_switch()`, `switch_port_to_host()`, `switch_port_to_device()`, `ssusb_mode_sw_work()`, extcon notifier `ssusb_id_notifier()`, and role-switch callbacks `ssusb_role_sw_set()` and `ssusb_role_sw_get()`.

## Control Flow

Initialization creates a work item and selects manual debugfs, USB role switch, or extcon notifier mode. Role changes store `desired_role` and queue `ssusb_mode_sw_work()` on the freezable workqueue. The work function normalizes `USB_ROLE_NONE` to the default role, skips no-op transitions, runtime-resumes the device, then for host mode forces host, stops gadget, switches U2/U3 port0 to host, enables VBUS, and marks `is_host`. For device mode it forces device, disables VBUS, switches port0 to device, starts gadget, and marks non-host.

## State and Persistence Behavior

Role state lives in `otg_switch_mtk` and `ssusb_mtk`: desired/default role, whether role switch or manual DRD is used, whether U3 port0 supports DRD, VBUS regulator handle, and `ssusb->is_host`. Hardware state is held in IPPC U2/U3 port mode bits and force-IDDIG bits. No state persists across remove.

## Dependencies and Integration Points

The file depends on regulators, extcon, USB role-switch framework, system workqueues, runtime PM, debugfs helper hooks, and host/gadget core functions from `mtu3_dr.h`. It is used only in dual-role builds.

## Risks and Test Signals

Risks include role-switch races with suspend/remove, ignoring `ssusb_check_clocks()` return values in port switch helpers, VBUS regulator failures leaving partially switched roles, and policy differences between extcon and role-switch defaults. Test signals include extcon host cable insertion/removal, userspace role-switch writes, manual debugfs mode writes, VBUS regulator on/off behavior, U3 DRD and U2-only DRD variants, and remove canceling pending work before unregistering role switch.
