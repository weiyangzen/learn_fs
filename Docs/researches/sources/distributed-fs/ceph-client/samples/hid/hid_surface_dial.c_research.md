# sources/distributed-fs/ceph-client/samples/hid/hid_surface_dial.c

Purpose: user-space libbpf loader and controller for the Surface Dial HID-BPF sample.

Important APIs/functions: generated `hid_surface_dial.skel.h`, `hid_surface_dial__open/load/destroy`, `bpf_map__attach_struct_ops`, `bpf_prog_test_run_opts`, and data variable assignment for `resolution` and `physical`.

Control flow: parses optional `-r`, extracts HID ID from sysfs path, sets struct-ops HID ID, loads BPF, writes BPF globals, attaches struct ops, calls `set_haptic`, and waits until signal.

State and persistence: active BPF link and configured BPF globals while the process is alive.

Dependencies and integration: requires libbpf, generated skeleton, HID-BPF kernel support, and Surface Dial-style report layout.

Risks: `physical = resolution / 72` can be zero for low values. `set_haptic` errors are printed but main continues into wait loop. Fixed path parsing assumes the HID directory naming scheme.

Test signals: run with Surface Dial sysfs path and `-r 72` or `-r 3600`, confirm attach and haptic setting, then interrupt and verify detachment.
