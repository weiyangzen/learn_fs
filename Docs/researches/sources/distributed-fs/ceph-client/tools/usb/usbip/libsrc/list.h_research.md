# sources/distributed-fs/ceph-client/tools/usb/usbip/libsrc/list.h

Purpose: `list.h` provides a small userspace copy of Linux kernel-style intrusive doubly linked lists for usbip internals.

Important APIs: `struct list_head` stores `next` and `prev`. `LIST_HEAD_INIT`, `LIST_HEAD`, and `INIT_LIST_HEAD()` initialize lists. `list_add()` inserts after a head, `list_del()` removes and poisons pointers, `list_entry()` maps a node pointer back to its containing struct, and `list_for_each()`/`list_for_each_safe()` iterate. Local `offsetof` and `container_of` macros support embedding.

Control flow and state: the list primitives mutate only embedded pointers inside caller-owned objects. usbip uses them for exported-device lists in the host and device driver backends.

Dependencies, risks, and tests: it depends on GNU C `typeof` in `container_of`, so strict non-GNU compilers are not supported. It lacks many kernel-list helpers and no runtime validation is performed; misuse can corrupt process memory. `LIST_POISON*` helps expose use-after-delete under debugging. Test signals are successful enumeration/destruction of exported device lists, especially safe deletion through `list_for_each_safe()`.
