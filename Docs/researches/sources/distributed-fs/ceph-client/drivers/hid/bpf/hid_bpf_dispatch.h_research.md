# sources/distributed-fs/ceph-client/drivers/hid/bpf/hid_bpf_dispatch.h

## Purpose

`hid_bpf_dispatch.h` is the private header shared between HID-BPF dispatcher and struct_ops implementation.

## Important APIs, Types, and Functions

`struct hid_bpf_ctx_kern` embeds public `struct hid_bpf_ctx`, a kernel data pointer, and a `from_bpf` recursion flag. Prototypes cover device lookup/reference helpers, event data allocation, device-destroy cleanup, and HID reprobe.

## Control Flow

Struct_ops registration uses `hid_get_device()`, `hid_put_device()`, `hid_bpf_allocate_event_data()`, and `hid_bpf_reconnect()` while dispatch code provides the implementations.

## State and Persistence Behavior

The header defines transient context wrapper state. Device references acquired by `hid_get_device()` must be released by `hid_put_device()`.

## Dependencies and Integration Points

It includes `<linux/hid.h>` and is private to `drivers/hid/bpf`. It forms the internal ABI between the two HID-BPF C files.

## Risks and Test Signals

Risks are ownership mismatches for HID device references and accidental exposure of private context fields. Test signals include attach/detach reference-count tests, device removal under active BPF programs, and compile checks when `struct hid_bpf_ctx` changes.
