<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/phy/phy-mv-usb.h -->
# sources/distributed-fs/ceph-client/drivers/usb/phy/phy-mv-usb.h

## Purpose

`phy-mv-usb.h` is the private register and state header for Marvell/PXA-style OTG controller support. It defines command and OTGSC bits, OTG timing constants, software FSM state, MMIO register layout, and per-device runtime state.

## Important APIs, Types, and Functions

Important definitions include `USBCMD_RUN_STOP`, `USBCMD_CTRL_RESET`, `OTGSC_CTRL_*`, `OTGSC_STS_*`, `OTGSC_INTSTS_*`, `OTGSC_INTR_*`, timing constants `T_A_WAIT_*` and `T_B_*`, `enum otg_function`, `enum mv_otg_timer`, `struct mv_otg_ctrl`, `struct mv_otg_regs`, and `struct mv_otg`.

## Control Flow

The header has no execution path. Implementation code uses `struct mv_otg_regs` to access operational registers, `struct mv_otg_ctrl` to carry OTG FSM inputs and timeout flags, and `struct mv_otg` to coordinate PHY registration, IRQ handling, delayed work, workqueue, platform data, clocks, and active/clock-gating state.

## State and Persistence Behavior

`struct mv_otg_ctrl` is volatile FSM state. `struct mv_otg_regs` names hardware state for run/reset, port and OTG signaling, endpoint status, mux control, and interrupt bits. `struct mv_otg` persists for one probed controller instance.

## Dependencies and Integration Points

It depends on Linux types, timers, workqueues, clocks, platform data, and USB PHY definitions through includers. It is intended for Marvell OTG controller code sharing the ChipIdea/EHCI-style register layout.

## Risks and Test Signals

Risks are incorrect OTGSC write-one-to-clear behavior, timer-unit confusion, and mismatch between `VUSBHS_MAX_PORTS` layout and actual hardware. Tests should validate role switching, ID/VBUS interrupts, timer expiry, reset/run-stop programming, and register offsets against hardware documentation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/phy/phy-mv-usb.h -->
