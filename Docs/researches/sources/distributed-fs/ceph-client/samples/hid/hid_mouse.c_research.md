# sources/distributed-fs/ceph-client/samples/hid/hid_mouse.c

Purpose: user-space libbpf loader for the HID mouse BPF sample.

Important APIs/functions: generated `hid_mouse.skel.h`, `hid_mouse__open`, `hid_mouse__load`, `bpf_map__attach_struct_ops`, `hid_mouse__destroy`, `get_hid_id`, signal handlers, and sysfs `uevent` probing.

Control flow: validates a HID sysfs path, extracts the HID numeric ID from the device directory name, sets `skel->struct_ops.mouse_invert->hid_id`, loads the BPF object, attaches struct ops, then sleeps until signal.

State and persistence: process holds the BPF link while running; no persistent files.

Dependencies and integration: requires libbpf, generated skeleton, and a HID device path such as `/sys/bus/hid/devices/...`.

Risks: `basename((char *)path)` mutates/uses argv storage and assumes a fixed HID name length. The program exits from signal handler without explicit link cleanup beyond process teardown.

Test signals: run with a target HID path, confirm load/attach succeeds, move the device, then Ctrl-C and confirm behavior returns to normal.
