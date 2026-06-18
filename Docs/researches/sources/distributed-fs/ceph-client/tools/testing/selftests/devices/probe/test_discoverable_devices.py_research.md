# sources/distributed-fs/ceph-client/tools/testing/selftests/devices/probe/test_discoverable_devices.py

## Purpose

`test_discoverable_devices.py` validates that expected board-specific PCI/USB devices exist in sysfs and are bound to drivers.

## Important APIs, Types, and Functions

It uses PyYAML, glob, os.walk, regexes, sysfs roots `/sys/devices` and `/sys/bus/usb/devices`, and `ksft`. Important functions include `find_pci_controller_dirs()`, `find_usb_controller_dirs()`, `get_dt_mmio()`, `get_of_fullname()`, `get_acpi_uid()`, `get_usb_version()`, `get_usb_busnum()`, `find_controller_in_sysfs()`, `path_to_dir()`, `find_in_sysfs()`, `check_driver_presence()`, `fill_meta_keys()`, `parse_device_tree_node()`, `count_tests()`, and `get_board_filenames()`.

## Control Flow

The script scans all PCI and USB controller directories, prints a KTAP header, selects a board YAML by devicetree compatible strings or DMI vendor/product, loads device trees, sets a plan based on leaf devices and USB interfaces, recursively resolves each controller/device path, and emits existence and driver-binding results.

## State and Persistence Behavior

It reads sysfs, DMI, and devicetree state without mutation. It builds in-memory controller lists and metadata pathnames for test names.

## Dependencies and Integration Points

It depends on board YAML files, PyYAML, kselftest `ksft`, sysfs PCI/USB topology, `uevent` metadata, DMI or devicetree identifiers, and driver symlinks.

## Risks and Edge Cases

Controller matching can return zero or multiple entries, both fail. `get_dt_mmio()` and `get_of_fullname()` walk parents until a match and may loop toward root if metadata is absent. USB interface globbing expects one interface directory. Board files can become stale as firmware or hardware variants change.

## Test Signals

Failures are named as missing sysfs entries, multiple matches, absent device paths, or missing driver symlinks. Success means every board-described leaf exists and is driver-bound.
