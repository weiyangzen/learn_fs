# File Research: sources/block-storage/bcache-tools/list.h

This is a userspace copy/adaptation of Linux kernel-style intrusive list and hlist macros. It defines `container_of`, `struct list_head`, add/delete/move/splice helpers, forward/reverse/safe iteration macros, and hlist equivalents.

The bcache CLI uses the `list_head` portion to collect discovered devices from `/sys/block`. Some hlist macros still reference `prefetch`, but the code paths in this toolset appear to use only the basic list macros.
