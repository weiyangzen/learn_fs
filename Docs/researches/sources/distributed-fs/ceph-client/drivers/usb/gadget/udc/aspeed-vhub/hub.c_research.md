# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/aspeed-vhub/hub.c

## Purpose
Emulates the upstream-facing USB 2.0 hub for the Aspeed vHub controller. It supplies the root hub descriptors and string descriptors, handles standard and hub-class control requests on the vHub EP0, maintains per-port status/change bits, drives the hardware status-change interrupt endpoint, and propagates hub reset/suspend/resume/wakeup events to the virtual downstream gadget devices.

## Important APIs, Types, And Functions
The public functions are `ast_vhub_init_hub`, `ast_vhub_std_hub_request`, `ast_vhub_class_hub_request`, `ast_vhub_device_connect`, `ast_vhub_hub_suspend`, `ast_vhub_hub_resume`, `ast_vhub_hub_reset`, and `ast_vhub_hub_wake_all`. Descriptor constants include `ast_vhub_dev_desc`, `ast_vhub_qual_desc`, `ast_vhub_conf_desc`, `ast_vhub_hub_desc`, and default English strings. Hub request helpers include descriptor/string responders, `ast_vhub_hub_dev_status`, `ast_vhub_hub_ep_status`, feature handlers, and port status handlers.

Port state lives in `struct ast_vhub_port` inside `struct ast_vhub`: `status`, `change`, and the attached `struct ast_vhub_dev`. vHub-wide state includes current upstream speed, suspend flag, remote wakeup enable, EP1 stall state, descriptor copies, and the list of language-specific string containers.

## Control Flow
`ast_vhub_init_hub` initializes speed to unknown, initializes wake work, and calls `ast_vhub_init_desc`. Descriptor initialization copies defaults, applies device-tree overrides for vendor/product/revision, optionally forces USB 1.1 descriptor values, sets hub port count, and loads either default strings or `vhub-strings` children with validated USB language IDs.

During early control traffic, `ast_vhub_std_hub_request` lazily samples `AST_VHUB_USBSTS` to determine full/high speed, then handles SET_ADDRESS, GET_STATUS, device/interface/endpoint features, configuration, descriptors, and interface requests. Descriptor responses are copied to the EP0 buffer before sending, allowing in-place type patching for other-speed configuration. `ast_vhub_class_hub_request` handles hub-class status/descriptor requests, port feature set/clear, and TT no-op requests. `ast_vhub_change_port_stat` updates USB port status, derives USB change bits from selected status transitions, suppresses enable-change on enable as required by host behavior, and mirrors changes into `AST_VHUB_EP1_STS_CHG`.

Device connect/disconnect changes CONNECTION and ENABLE state and can issue host remote wake. Port reset disables/suspends the port, calls `ast_vhub_dev_reset`, selects a speed compatible with the vHub upstream speed and gadget driver max speed, then sets ENABLE plus speed status. Suspend and resume forward bus state to every port that is not explicitly port-suspended. `ast_vhub_hub_wake_all` schedules `wake_work` so a downstream device wakeup can clear suspended port bits and signal remote wake without recursive call chains.

## State And Persistence Behavior
There is no disk persistence. Runtime state is the emulated USB hub state: descriptor copies, string container list allocated with devm memory, per-port status/change bits, remote wakeup enable, EP1 stall flag, upstream speed, and bus suspend flag. Port changes persist until the host clears the corresponding C_* feature. Bus reset clears wakeup enable, speed, non-connection port state, EP1 status-change hardware, and vHub address/config registers.

## Dependencies And Integration Points
Depends on USB descriptor and hub class definitions, device tree property parsing, `usb_gadget_get_string`, `usb_validate_langid`, `usb/ch11.h` hub feature constants, and shared vHub endpoint helpers from `ep0.c`. It integrates with `dev.c` through `ast_vhub_dev_suspend`, `ast_vhub_dev_resume`, and `ast_vhub_dev_reset`; with hardware through `AST_VHUB_CONF`, `AST_VHUB_EP1_CTRL`, `AST_VHUB_EP1_STS_CHG`, and `AST_VHUB_CTRL`; and with host enumeration through the hub interrupt endpoint.

## Risks
Hub behavior is host-sensitive. Incorrect change-bit semantics can break enumeration or upset OS-specific hub drivers; the file already contains a MacOS-oriented suppression of enable-change on enable. Port reset is effectively immediate rather than delayed, which may hide timing issues. Device-tree string parsing relies on a small fixed string ID set and EP0 buffer-size limits. Remote wake state is split between hub feature state and hardware wake signaling, so wake tests must cover both host-enabled and host-disabled cases. USB 1.1 forced mode modifies descriptors but shares much of the same control path as USB 2.0 mode.

## Test Signals
Important signals are host enumeration of the vHub itself, descriptor reads in full-speed and high-speed modes, custom device-tree VID/PID/revision/string descriptors, language descriptor reads, port connection-change and reset flows for each virtual port, suspend/resume propagation to downstream gadgets, remote wake from a suspended port, EP1 halt clear/set behavior, and repeated bus resets. `lsusb -v`, hub class request traces, dmesg debug logs, and gadget driver suspend/resume/reset callbacks provide practical validation.
