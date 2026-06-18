<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-mock-gio.c -->
# sources/cloud-native/ostree/tests/test-mock-gio.c

## Purpose
`test-mock-gio.c` implements mock GIO volume-monitor objects used by tests that need controlled removable drive, volume, and mount topology.

## Important APIs, Types, And Functions
It defines `OstreeMockVolumeMonitor`, `OstreeMockVolume`, `OstreeMockDrive`, and `OstreeMockMount` with GObject/GIO interface boilerplate. Constructors include `ostree_mock_volume_monitor_new`, `ostree_mock_volume_new`, `ostree_mock_drive_new`, and `ostree_mock_mount_new`. Interface methods include monitor `get_mounts`/`get_volumes`, volume `get_name`/`get_drive`/`get_mount`, drive `is_removable`, and mount `get_name`/`get_root`.

## Control Flow
Class init functions install dispose handlers and interface vfuncs. Constructors allocate objects and ref/copy supplied mount, volume, drive, and root references. Dispose methods release owned lists and objects. Getter vfuncs return copied or referenced state to emulate GIO behavior.

## State And Persistence
State is in-memory GObject fields: monitor lists, volume name/drive/mount, drive removable flag, and mount name/root file. There is no persistence.

## Dependencies And Integration Points
The file integrates with GLib object type registration, GIO `GVolumeMonitor`, `GVolume`, `GDrive`, and `GMount` interfaces, and OSTree tests that need deterministic removable-media discovery.

## Risks And Test Signals
The main risk is incorrect reference ownership, which would cause leaks or dangling objects in tests. The signal is successful compilation and use by higher-level tests without GObject criticals, plus correct mock topology returned through standard GIO interfaces.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-mock-gio.c -->
