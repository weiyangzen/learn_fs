# sources/distributed-fs/ceph-client/tools/testing/selftests/hid/progs/hid.c

## Purpose
`progs/hid.c` contains the BPF programs exercised by `hid_bpf.c`. It defines HID `struct_ops` callbacks, syscall-test programs, fentry tracing, and a BPF workqueue path to validate the HID-BPF kernel kfunc surface.

## Important APIs, types, and functions
The file uses `SEC("?struct_ops/...")` programs for `hid_device_event`, `hid_rdesc_fixup`, `hid_hw_request`, and `hid_hw_output_report`, with matching `SEC(".struct_ops.link") struct hid_bpf_ops` maps. It uses `hid_bpf_get_data()`, `hid_bpf_allocate_context()`, `hid_bpf_release_context()`, `hid_bpf_hw_request()`, `hid_bpf_hw_output_report()`, `hid_bpf_input_report()`, and `hid_bpf_try_input_report()`. Syscall programs share `struct hid_hw_request_syscall_args` with userspace tests.

## Control flow
Simple event callbacks mutate report bytes and return either the original or changed size. Insert-order programs verify `BPF_F_BEFORE` and normal insertion ordering. `hid_rdesc_fixup` copies an added descriptor fragment at offset 73 and changes a usage byte. Raw/output request hooks either return negative filter errors, forward requests to the device, rewrite data, or validate recursion prevention. `hidraw_open` captures the current hidraw `struct file *` so hooks can distinguish hidraw-originated requests. The workqueue path stores a `bpf_wq` in a hash map, starts a sleepable callback, allocates a HID context, and injects an additional input report.

## State and persistence
BPF global variables `callback_check`, `callback2_check`, and `current_file` persist for the lifetime of the loaded object. The `hmap` BPF hash map persists workqueue state while attached. All state is destroyed when userspace detaches and destroys the skeleton.

## Dependencies and integration points
It depends on custom HID helper declarations in `hid_bpf_helpers.h`, vmlinux CO-RE types, libbpf section conventions, and kernel HID-BPF kfunc exports. It is tightly coupled to program/map names expected by `hid_bpf.c`.

## Risks and test signals
Risks include ABI drift in `struct hid_bpf_ctx` or kfunc prototypes, verifier constraints around sleepable callbacks and workqueues, and brittle struct_ops naming conventions. Test signals include exact report byte rewrites, return sizes, errno propagation, recursion guard behavior, and descriptor fixup visibility through hidraw.
