# sources/distributed-fs/ceph-client/drivers/usb/usbip/usbip_common.h

## Purpose

`usbip_common.h` defines the shared USB/IP protocol structures, debug flags, event bits, common device state, exported helper prototypes, and small inline helpers used by all USB/IP kernel modules.

## Important APIs, Types, and Functions

It declares wire PDUs: `usbip_header_basic`, `usbip_header_cmd_submit`, `usbip_header_ret_submit`, `usbip_header_cmd_unlink`, `usbip_header_ret_unlink`, and `usbip_header`. It defines `usbip_iso_packet_descriptor`, side enum values for VHCI/STUB/VUDC, event masks, side-specific event combinations, and `struct usbip_device` with status, locks, sysfs mutex, socket, RX/TX tasks, event bits, event ops, and optional KCOV handle. It also provides debug macros and prototypes for common receive/pack/event helpers.

## Control Flow

The header has no standalone runtime flow, but it establishes the state machine used by all modules: connection state lives in `usbip_device`, transport threads observe `event`, and event operations perform shutdown/reset/unusable handling.

## State and Persistence Behavior

`struct usbip_device` is per exported/virtual device and runtime-only. Kconfig-dependent KCOV handle state permits remote coverage attribution during socket-driven processing.

## Dependencies and Integration Points

It integrates Linux USB, networking, device, waitqueue, task, spinlock, KCOV, and UAPI USB/IP definitions. It is the central internal ABI between core, host stub, VHCI, and VUDC.

## Risks and Test Signals

Risks include changing packed wire structs, event-mask semantics, status lock rules, debug flag bit overlap, and task/socket lifetime contracts. Test signals are cross-module compile coverage, UAPI compatibility tests, attach/detach event behavior across all sides, and KCOV-enabled/disabled builds.
