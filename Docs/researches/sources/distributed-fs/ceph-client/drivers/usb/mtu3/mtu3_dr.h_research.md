# sources/distributed-fs/ceph-client/drivers/usb/mtu3/mtu3_dr.h

## Purpose

`mtu3_dr.h` declares the role-dependent host, gadget, and dual-role interfaces used by MTU3 platform code, with inline no-op fallbacks when a role is not compiled.

## Important APIs, Types, and Functions

Host-side declarations include `ssusb_host_init()`, `ssusb_host_exit()`, `ssusb_wakeup_of_property_parse()`, `ssusb_host_resume()`, `ssusb_host_suspend()`, and `ssusb_wakeup_set()`. Gadget-side declarations include `ssusb_gadget_init()`, `ssusb_gadget_exit()`, `ssusb_gadget_suspend()`, `ssusb_gadget_resume()`, and `ssusb_gadget_ip_sleep_check()`. Dual-role declarations include `ssusb_otg_switch_init()`, `ssusb_otg_switch_exit()`, `ssusb_mode_switch()`, `ssusb_set_vbus()`, and `ssusb_set_force_mode()`.

## Control Flow

The header has no runtime control flow. Its `IS_ENABLED()` blocks select real prototypes or no-op inline functions, allowing `mtu3_plat.c` to call role helpers without local conditional compilation for every call site.

## State and Persistence Behavior

No state is stored in this header. The fallback functions return success or safe defaults, such as `ssusb_gadget_ip_sleep_check()` returning true when gadget support is absent.

## Dependencies and Integration Points

It depends on `struct ssusb_mtk`, `struct otg_switch_mtk`, `enum mtu3_dr_force_mode`, `struct device_node`, and `pm_message_t` definitions available through `mtu3.h` users. It connects platform lifecycle code to role-specific implementation files.

## Risks and Test Signals

Risks include no-op stubs hiding missing role behavior in unexpected configurations and mismatched `IS_ENABLED()` conditions relative to the Makefile. Test signals include compiling host-only, gadget-only, and dual-role modes and verifying platform probe calls resolve to the intended real or stub functions.
