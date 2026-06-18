# sources/distributed-fs/ceph-client/drivers/hid/bpf/Makefile

## Purpose

This Makefile builds the kernel HID-BPF support object.

## Important APIs, Types, and Functions

`obj-$(CONFIG_HID_BPF) += hid_bpf.o` defines the composite target. `hid_bpf-objs += hid_bpf_dispatch.o hid_bpf_struct_ops.o` links the dispatch/kfunc and struct_ops registration halves. `CFLAGS_hid_bpf_dispatch.o` and `CFLAGS_hid_bpf_jmp_table.o` add `$(LIBBPF_INCLUDE)`.

## Control Flow

Kbuild compiles these objects when `CONFIG_HID_BPF` is enabled. Initialization happens through `late_initcall()` functions inside the C files.

## State and Persistence Behavior

No runtime state is stored here. The file determines that dispatcher and struct_ops code are always built together.

## Dependencies and Integration Points

It integrates with parent HID Kbuild and the kernel BPF/libbpf include setup. The `hid_bpf_jmp_table.o` flag appears to reference an object not in this composite target, so it may be leftover or for generated/optional code outside this snapshot.

## Risks and Test Signals

Risks include stale CFLAGS for missing objects and include path drift. Test signals are clean `CONFIG_HID_BPF=y` builds and BPF selftest compilation of HID programs.
