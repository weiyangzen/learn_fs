# `sources/distributed-fs/ceph-client/include/linux/usb/otg-fsm.h`

## Purpose

`otg-fsm.h` defines the USB OTG finite state machine state container, timer identifiers, operation callbacks, inline operation wrappers, protocol constants, and the `otg_statemachine()` entry point.

## Important APIs, Types, and Constants

- Protocol constants identify undefined, host, and gadget modes.
- OTG status selector, host request flag, and HNP polling interval constants support OTG/EH flows.
- `enum otg_fsm_timer` enumerates standard and auxiliary timers such as A_WAIT_VRISE, A_WAIT_BCON, B_SE0_SRP, and A_WAIT_ENUM.
- `struct otg_fsm` stores hardware inputs, application inputs, auxiliary inputs, outputs, internal variables, timeout flags, ops, `usb_otg` pointer, current protocol, mutex, host request flag, HNP delayed work, and state-change flag.
- `struct otg_fsm_ops` supplies VBUS, local connect/SOF, SRP/ADP, timer, host, and gadget control callbacks.
- Inline wrappers validate optional callbacks, update output state where appropriate, and return `-EOPNOTSUPP` when unsupported.

## Control Flow and Lifetimes

An OTG controller owns `struct otg_fsm`, updates input bits from hardware/application events, schedules or cancels timers through callbacks, and calls `otg_statemachine()` under the FSM lock. The FSM toggles outputs through wrappers, starts/stops host or gadget roles, and uses delayed HNP polling when initialized.

## State and Persistence Behavior

The FSM object is persistent runtime state for the OTG controller. Inputs mirror hardware and policy state; outputs cache last-applied hardware actions to avoid redundant callbacks; timer timeout fields drive transitions. No disk persistence exists.

## Dependencies and Integration Points

It depends on mutex, errno, delayed work through including context, and `struct usb_otg`. It integrates OTG transceiver/controller drivers with host and gadget controller start/stop paths.

## Risks and Edge Cases

Missing callbacks produce `-EOPNOTSUPP` and can block required state transitions. Input bits must be updated atomically with FSM execution. Timer callbacks must match OTG timing requirements. HNP polling work must be canceled during teardown. Cached output fields must not diverge from actual hardware state after reset.

## Test Signals

Exercise A-device and B-device state transitions, SRP, HNP, ADP probing/sensing, timer expiration paths, host/gadget start failures, ID/VBUS changes, teardown with delayed work pending, and lockdep around the FSM mutex.
