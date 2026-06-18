<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/linux/kernel.h -->
# sources/distributed-fs/ceph-client/tools/virtio/linux/kernel.h

## Purpose

`kernel.h` is a header for the local userspace/kernel-test compatibility layer or exported build shim. It provides includes (stdbool.h, stdlib.h, stddef.h, stdio.h, string.h, assert.h, stdarg.h, linux/compiler.h, ../../../include/linux/container_of.h, linux/log2.h, linux/types.h, linux/overflow.h, plus 7 more), macros (KERNEL_H, CONFIG_SMP, PAGE_SIZE, PAGE_MASK, PAGE_ALIGN, READ, WRITE, virt_to_phys, phys_to_virt, page_to_phys, virt_to_page, offset_in_page, plus 13 more), and declarations needed by nearby C sources without pulling in full kernel internals.

## Important APIs, Types, and Functions

Source size: 160 lines, 3601 bytes. Functions/classes: kfree, free_pages_exact, __get_free_page, free_page, is_vmalloc_addr, synchronize_rcu. Includes: stdbool.h, stdlib.h, stddef.h, stdio.h, string.h, assert.h, stdarg.h, linux/compiler.h, ../../../include/linux/container_of.h, linux/log2.h, linux/types.h, linux/overflow.h, linux/limits.h, linux/list.h, linux/printk.h, linux/bug.h, errno.h, unistd.h, plus 1 more. Macros/defines: KERNEL_H, CONFIG_SMP, PAGE_SIZE, PAGE_MASK, PAGE_ALIGN, READ, WRITE, virt_to_phys, phys_to_virt, page_to_phys, virt_to_page, offset_in_page, __printf, ARRAY_SIZE, likely, unlikely, pr_err, pr_debug, plus 7 more.

## Control Flow and Data Flow

There is no standalone control flow. Included macros and inline helpers are expanded into userspace tests or kernel build units at compile time.

## State and Persistence Behavior

State is either absent or stored in caller-owned structs and globals. Header-defined wrappers often model kernel primitives over libc, pthreads, eventfd-safe memory, or direct include forwarding.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/tools/virtio/linux`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

Stub semantics may diverge from in-kernel behavior. Macro-only APIs can hide type/ordering bugs, and include-forwarding paths can break when the kernel tree layout changes.

## Test Signals

Compile all dependent virtio, ringtest, vhost, and initramfs header-test targets with warnings enabled; run the corresponding runtime tests where the header models synchronization or memory access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/linux/kernel.h -->
