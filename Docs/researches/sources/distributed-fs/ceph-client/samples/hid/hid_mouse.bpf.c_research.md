# sources/distributed-fs/ceph-client/samples/hid/hid_mouse.bpf.c

Purpose: HID-BPF struct-ops program that swaps and inverts mouse X/Y behavior and patches the report descriptor.

Important APIs/functions: `hid_bpf_get_data`, `BPF_PROG(hid_event)`, helper functions `hid_y_event` and `hid_x_event`, `BPF_PROG(hid_rdesc_fixup)`, and `struct hid_bpf_ops mouse_invert` in `.struct_ops.link`.

Control flow: device events fetch nine report bytes, negate Y and X 16-bit values, and write them back. Descriptor fixup fetches descriptor bytes and swaps usage bytes at fixed offsets for X and Y.

State and persistence: no maps or durable state; mutations affect in-flight reports and the attached HID device while the struct-ops link is active.

Dependencies and integration: loaded by `hid_mouse.c` skeleton and attached to a specific HID device ID.

Risks: assumes a particular report format and descriptor offsets; on other devices it can corrupt input interpretation. Fixed-size data access must pass verifier bounds checks.

Test signals: attach to the intended Etekcity mouse, inspect `bpf_printk` output, and confirm axes are swapped/inverted; detach by stopping loader.
