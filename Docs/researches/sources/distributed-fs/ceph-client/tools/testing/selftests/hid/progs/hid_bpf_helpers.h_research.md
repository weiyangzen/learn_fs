# sources/distributed-fs/ceph-client/tools/testing/selftests/hid/progs/hid_bpf_helpers.h

## Purpose
`hid_bpf_helpers.h` is the local compatibility header that lets the HID-BPF test programs compile against BPF CO-RE while overriding selected `vmlinux.h` HID types with stable test-local definitions.

## Important APIs, types, and functions
The header temporarily renames `vmlinux.h` symbols, defines `BPF_NO_KFUNC_PROTOTYPES`, includes `vmlinux.h`, then restores the names and declares local `enum hid_report_type`, `struct hid_device`, `struct bpf_wq`, `struct hid_bpf_ctx`, `enum hid_class_request`, and `struct hid_bpf_ops`. It declares weak kfunc symbols for HID data access, context allocation/release, hw request/output/input report helpers, try-input helper, and BPF workqueue helpers.

## Control flow
There is no runtime control flow. Its compile-time control flow is macro based: hide vmlinux definitions, include BTF-derived declarations, undefine the aliases, then provide the exact structs and prototypes needed by `progs/hid.c`.

## State and persistence
The header itself has no state. It defines struct layouts that determine what BPF programs can read and write through CO-RE and through struct_ops maps.

## Dependencies and integration points
It integrates with libbpf helper headers, BPF tracing macros, `linux/const.h`, kernel BTF, and the HID-BPF kernel ABI. The struct_ops layout must match enough of the kernel contract for map initial values and callback slots to work.

## Risks and test signals
The main risk is layout or prototype drift from the kernel. Because these declarations shadow `vmlinux.h`, mismatches may produce verifier failures, wrong field access, or silent bad tests. Successful loading of `progs/hid.c`, correct `hid_id` injection, and passing kfunc behavior are the practical validation signals.
