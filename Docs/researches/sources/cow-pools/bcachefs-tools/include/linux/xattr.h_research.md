# File Research: sources/cow-pools/bcachefs-tools/include/linux/xattr.h

Declares extended attribute handler structures and VFS/generic xattr operations. It includes UAPI names/flags, defines `xattr_handler_can_list()`, `xattr_prefix()`, and xattr value container structure.

Actual filesystem handlers are expected elsewhere; this header supplies kernel VFS-compatible types and prototypes.
