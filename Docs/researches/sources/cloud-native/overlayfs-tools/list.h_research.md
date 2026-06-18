# sources/cloud-native/overlayfs-tools/list.h

Purpose: provides a small Linux-kernel-style intrusive doubly linked list implementation for overlayfs-tools.

Important APIs/types/functions: `struct list_head`, `LIST_HEAD_INIT`, `LIST_HEAD`, `INIT_LIST_HEAD`, `list_add`, `list_add_tail`, `list_del`, `list_del_init`, `list_empty`, `list_entry`, `list_for_each`, and `list_for_each_safe`.

Control flow: macros and static inline helpers manipulate embedded list nodes. `check.c` uses this for the redirect-origin tracking list.

State and persistence: state is embedded in caller-owned structs; no allocation or persistence.

Dependencies/integration: adapted from Linux kernel list API for C userspace.

Risks: no type safety beyond macro conventions. Deleting uninitialized or double-deleted entries corrupts memory. Requires including `<stdbool.h>` before use because `list_empty` returns `bool`.

Test signals: redirect duplicate tests exercise list add/find/delete/free flows.
