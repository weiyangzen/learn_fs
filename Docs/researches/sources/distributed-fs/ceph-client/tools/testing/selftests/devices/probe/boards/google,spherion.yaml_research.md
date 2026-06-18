# sources/distributed-fs/ceph-client/tools/testing/selftests/devices/probe/boards/google,spherion.yaml

## Purpose

This YAML describes expected discoverable devices for the Google Spherion Chromebook and documents the board-file schema.

## Important APIs, Types, and Data Fields

It defines a USB2 controller identified by `dt-mmio: 11200000` with camera and bluetooth USB devices, and a PCI controller identified by `dt-mmio: 11230000` with a WiFi device. Comments document keys: `type`, `dt-mmio`, `of-fullname-regex`, `usb-version`, `acpi-uid`, `devices`, `path`, `name`, and USB `interfaces`.

## Control Flow

The file is loaded when `/proc/device-tree/compatible` contains `google,spherion`. The probe script resolves controller identifiers and nested USB/PCI paths.

## State and Persistence Behavior

It is static expected topology data.

## Dependencies and Integration Points

It depends on devicetree-compatible naming, OF_FULLNAME/uevent metadata, and sysfs USB/PCI topology matching the board.

## Risks and Edge Cases

Board variants or disabled devices can cause false failures. `dt-mmio` must be unique enough to identify controllers; comments describe using regex when it is not.

## Test Signals

For each leaf, the probe script checks sysfs device existence and driver binding for the named device/interfaces.
