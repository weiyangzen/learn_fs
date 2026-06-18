# sources/distributed-fs/ceph-client/drivers/xen/privcmd.h

## Purpose
`privcmd.h` is the small local header shared by the Xen privcmd implementation and companion buffer device. It publishes file operations and the hypercall-buffer miscdevice for registration from the Xen driver code.

## Important APIs, types, and functions
It declares `xen_privcmd_fops`, `xen_privcmdbuf_fops`, and `xen_privcmdbuf_dev`. There are no local types or inline helpers.

## Control flow
The header has no runtime control flow. It allows `privcmd.c` to register both the privcmd and hypercall-buffer devices, while the buffer implementation supplies the second file-operations table and miscdevice object.

## State and persistence
No state is stored in the header. The declared objects refer to runtime file-operation tables and a miscdevice defined elsewhere.

## Dependencies and integration points
It includes `<linux/fs.h>` for `struct file_operations` and references `struct miscdevice`, relying on users including the normal miscdevice definitions where needed. It is a local integration point between `privcmd.c` and `privcmd-buf.c`.

## Risks and test signals
Risks are build-time only: declaration drift from the defining source files or missing includes in users. Test signals are Xen driver builds with `CONFIG_XEN_PRIVCMD` and symbol/export checks for both device registrations.
