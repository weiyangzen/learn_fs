# sources/distributed-fs/ceph-client/drivers/hid/bpf/hid_bpf_struct_ops.c

## Purpose

`hid_bpf_struct_ops.c` registers the `hid_bpf_ops` BPF struct_ops type and manages attachment, detachment, verifier write permissions, and device cleanup for HID-BPF programs.

## Important APIs, Types, and Functions

Verifier hooks include `hid_bpf_ops_is_valid_access()`, `hid_bpf_ops_check_member()`, and `hid_bpf_ops_btf_struct_access()`. Initialization and member-copy hooks are `hid_bpf_ops_init()` and `hid_bpf_ops_init_member()`. Runtime attach/detach handlers are `hid_bpf_reg()` and `hid_bpf_unreg()`. `__hid_bpf_ops_destroy_device()` nulls attached ops during HID device destruction. `hid_bpf_struct_ops_init()` registers the struct_ops type at late init.

## Control Flow

When userspace links a `hid_bpf_ops` map, `hid_bpf_reg()` resolves `hid_id` to a device, locks the device BPF list, enforces `HID_BPF_MAX_PROGS_PER_DEV`, installs a single descriptor-fixup op if requested, allocates event data when needed, inserts the ops before or after existing programs based on `BPF_F_BEFORE`, and triggers reprobe for descriptor fixups. Detach removes the list node, clears descriptor fixup if owned, optionally reprobes, and drops the device reference.

## State and Persistence Behavior

State persists in `hdev->bpf.prog_list`, `hdev->bpf.rdesc_ops`, and each `struct hid_bpf_ops` instance's `hdev` and list node. The file stores a BTF pointer in `hid_bpf_ops_btf`. Destroy-device cleanup clears `e->hdev` so later unregister avoids using a destroyed device.

## Dependencies and Integration Points

It depends on BPF verifier APIs, BTF, HID core, workqueue headers, and the dispatcher helpers. It integrates with BPF syscall loading of struct_ops maps and HID device lifecycle hooks.

## Risks and Test Signals

Risks include write-permission gaps in verifier rules, descriptor fixup exclusivity, list ordering with `BPF_F_BEFORE`, reference drops during destroy, and sleepable-program restrictions for event callbacks. Test signals include verifier tests for writable fields, attach limit tests, rdesc-fixup attach/detach reprobe, concurrent device removal, and ordering tests with multiple programs.
