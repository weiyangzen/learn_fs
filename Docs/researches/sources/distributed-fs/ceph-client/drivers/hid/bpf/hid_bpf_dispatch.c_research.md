# sources/distributed-fs/ceph-client/drivers/hid/bpf/hid_bpf_dispatch.c

## Purpose

`hid_bpf_dispatch.c` provides the runtime dispatch layer and BPF kfuncs for HID-BPF. It lets attached BPF struct_ops programs modify device events, intercept raw requests/output reports, fix report descriptors, allocate contexts, access report buffers, send hardware requests, and inject input reports.

## Important APIs, Types, and Functions

Exported dispatch APIs include `dispatch_hid_bpf_device_event()`, `dispatch_hid_bpf_raw_requests()`, `dispatch_hid_bpf_output_report()`, and `call_hid_bpf_rdesc_fixup()`. Device lifecycle APIs include `hid_bpf_connect_device()`, `hid_bpf_disconnect_device()`, `hid_bpf_destroy_device()`, and `hid_bpf_device_init()`. BPF kfuncs include `hid_bpf_get_data()`, `hid_bpf_allocate_context()`, `hid_bpf_release_context()`, `hid_bpf_hw_request()`, `hid_bpf_hw_output_report()`, `hid_bpf_try_input_report()`, and `hid_bpf_input_report()`. `hid_ops` is an exported bridge to HID core operations.

## Control Flow

HID core calls dispatchers at event, raw-request, output-report, and descriptor-fixup points. The dispatchers build `hid_bpf_ctx_kern`, copy or reference report data, iterate attached ops under RCU/SRCU, and propagate return sizes/errors. Kfuncs validate report types and report IDs through `hid_ops`, prevent recursive hardware calls when `from_bpf` is set, copy DMA buffers for hardware requests, and inject reports through HID core locks.

## State and Persistence Behavior

Per-device BPF state lives in `hdev->bpf`: attached program list, SRCU, mutex, descriptor-fixup op, allocated event buffer, allocation size, and destroyed flag. Context allocations hold a device reference until released. `hid_bpf_init()` registers kfunc sets at late init and logs but does not fail HID if registration fails.

## Dependencies and Integration Points

The file depends on HID core internals, BTF kfunc registration, BPF program types, SRCU/RCU, kfifo/minmax helpers, and exported `__hid_bpf_ops_destroy_device()` from the struct_ops file.

## Risks and Test Signals

Risks include recursion/deadlock if `from_bpf` checks are bypassed, event buffer sizing based on parsed reports, descriptor fixup allocation fallback silently ignoring BPF, and device destruction races. Test signals include HID-BPF selftests for event rewriting, descriptor reprobe, kfunc verifier access, concurrent detach/destroy, and hardware request recursion rejection.
