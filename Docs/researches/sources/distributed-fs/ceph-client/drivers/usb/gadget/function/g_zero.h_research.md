# sources/distributed-fs/ceph-client/drivers/usb/gadget/function/g_zero.h

## Purpose
This header defines shared constants, option structures, and utility declarations for Gadget Zero function drivers. Gadget Zero is a USB gadget test/demo composition, and this header centralizes its source/sink and loopback configuration knobs.

## Important APIs, types, and functions
Constants define default buffer lengths, queue lengths, isochronous interval, packet sizes, and SuperSpeed queue defaults. `struct usb_zero_options` is a plain aggregate of module/config options. `struct f_ss_opts` stores source/sink function-instance state, including pattern, isochronous parameters, bulk parameters, a configfs mutex, and a refcount. `struct f_lb_opts` stores loopback function-instance state. The declared functions are `lb_modinit()`, `lb_modexit()`, and `disable_endpoints()`.

## Control flow
The header itself has no executable flow. Source/sink and loopback implementation files include it to interpret configfs or module options, guard option changes while a function is linked, and call `disable_endpoints()` during teardown or reset paths.

## State and persistence
The option structures hold in-memory configfs state for Gadget Zero function instances. The mutex comments document the intended concurrency model: configfs handles attribute read/write entry points, while the local lock protects against simultaneous attribute access and symlink create/remove operations. Refcounts indicate active users.

## Dependencies and integration points
The declarations integrate with the USB composite framework through `struct usb_function_instance`, `struct usb_composite_dev`, and endpoint pointers. The header is consumed by Gadget Zero-specific function drivers rather than exporting a standalone module API.

## Risks and edge cases
The option structures expose raw unsigned fields with validation expected in users. Incorrect validation can request unsupported endpoint intervals, packet sizes, bursts, or queue depths. The shared `disable_endpoints()` declaration implies callers must pass valid endpoint pointers and tolerate NULL or disabled endpoints according to the implementation contract.

## Test signals
Compile both source/sink and loopback functions, exercise configfs attributes for each option, link/unlink functions while reading and writing options, and verify endpoint disable behavior during disconnect and configuration changes.
