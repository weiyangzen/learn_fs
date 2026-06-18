# File Research: sources/cow-pools/bcachefs-tools/include/linux/posix_acl.h

This header defines POSIX ACL constants and in-memory ACL structures. It includes ACL type constants, tag constants, permission bits, `struct posix_acl_entry`, and `struct posix_acl`.

`struct posix_acl` stores an RCU head, reference count, and zero-length entry array. It is a structural compatibility definition; ACL manipulation functions are not declared here.
