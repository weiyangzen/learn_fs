# sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/hid_bpf.h

Purpose: This small public header defines the section names, struct-op declaration helper, simple device-name helper, and probe argument structure shared by HID-BPF programs in this directory.

Important APIs/types/functions: `HID_BPF_DEVICE_EVENT` expands to `struct_ops/hid_device_event`, and `HID_BPF_RDESC_FIXUP` expands to `struct_ops/hid_rdesc_fixup`; programs use these names in `SEC()` annotations. `HID_BPF_OPS(name)` declares a linked `.struct_ops.link` `struct hid_bpf_ops` object. `hid_set_name(_hdev, _name)` copies a compile-time string into `hdev->name`. `struct hid_bpf_probe_args` carries the HID identifier, report descriptor size, up to 4096 descriptor bytes, and a `retval` field set by syscall-style probe programs.

Control flow: The header has no runtime flow itself. It shapes how BPF object files expose callbacks. A typical program defines descriptor and/or event functions in the section names, creates a `HID_BPF_OPS()` object assigning those callbacks, and defines `probe()` in the `syscall` section to accept or reject a device.

State and persistence: The header stores no state. `hid_bpf_probe_args` is transient per probe invocation. `HID_BPF_OPS()` creates static BPF object metadata that persists as part of the loaded BPF program.

Dependencies and integration points: It depends on `struct hid_bpf_ops` and HID objects from `vmlinux.h` included by users. It is the local ABI glue between BPF C source files, libbpf section loading, and kernel HID-BPF struct-ops registration.

Risks: Section-name strings are contract-sensitive; changing them would break loader/kernel attachment. `hid_set_name()` copies `sizeof(_name)` bytes, so it is intended for fixed arrays or string literals and can be wrong for pointers. The probe descriptor buffer is fixed at 4096 bytes, matching `HID_MAX_DESCRIPTOR_SIZE` in helpers, and code should not assume larger descriptors are available.

Test signals: Build HID-BPF programs using the macros, inspect BTF/ELF sections for `.struct_ops.link` and expected callback sections, validate probe programs can read `rdesc_size` and set `retval`, and confirm no duplicate or mismatched struct-op symbols are emitted.
