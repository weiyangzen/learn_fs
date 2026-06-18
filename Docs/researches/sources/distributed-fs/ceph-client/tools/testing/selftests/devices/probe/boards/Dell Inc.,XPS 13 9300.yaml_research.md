# sources/distributed-fs/ceph-client/tools/testing/selftests/devices/probe/boards/Dell Inc.,XPS 13 9300.yaml

## Purpose

This board YAML describes expected discoverable PCI and USB devices for a Dell XPS 13 9300 system.

## Important APIs, Types, and Data Fields

It contains one top-level `pci-controller` with child PCI paths for USB controller, GPU, thermal, sensors, WiFi, SSD, SD card reader, and audio. The USB controller at `14.0` has `usb-version: 2` and child USB paths for camera and bluetooth with expected interface lists.

## Control Flow

The file is declarative. `test_discoverable_devices.py` selects it from DMI `sys_vendor,product_name`, recursively resolves paths in sysfs, and checks device and driver presence.

## State and Persistence Behavior

It persists expected hardware topology and has no runtime state.

## Dependencies and Integration Points

It depends on stable sysfs path topology for the Dell model and the board-file vocabulary implemented by the probe script.

## Risks and Edge Cases

Hardware revisions, firmware differences, disabled devices, or alternate USB routing can make expected paths absent. The top-level controller has no unique key, which is valid only because the machine is expected to have one PCI host controller.

## Test Signals

The probe script emits device existence and driver-binding test results for each leaf and USB interface named here.
