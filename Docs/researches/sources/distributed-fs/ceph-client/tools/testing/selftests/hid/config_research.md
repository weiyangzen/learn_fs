<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/hid/config -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/hid/config

## Purpose
This file lists kernel options needed for HID, HID-BPF, hidraw, UHID, USB HID, and device-specific HID selftests.

## Important APIs, Types, And Functions
It includes BPF core options (`CONFIG_BPF`, `CONFIG_BPF_SYSCALL`, JIT, BTF, LSM, cgroup), tracing helpers, `CONFIG_HIDRAW`, `CONFIG_HID`, `CONFIG_HID_BPF`, `CONFIG_INPUT_EVDEV`, `CONFIG_UHID`, USB HID, and vendor drivers such as Apple, ITE, Multitouch, PlayStation/Sony, and Wacom.

## Control Flow
The config is prerequisite metadata for kselftest; wrappers and hid-tools still perform runtime device/test availability checks.

## State And Persistence
No runtime state is mutated.

## Dependencies And Integration Points
It aligns with the HID Makefile's BPF build needs and the Python hid-tools target coverage.

## Risks
The list is broad; a missing vendor driver may only affect that vendor wrapper, but config reporting may present it as a suite prerequisite.

## Test Signals
A kernel matching these options should support building HID-BPF tests and running UHID/hidraw/hid-tools scenarios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/hid/config -->
