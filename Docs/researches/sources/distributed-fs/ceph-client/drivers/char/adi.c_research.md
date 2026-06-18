# sources/distributed-fs/ceph-client/drivers/char/adi.c

## Purpose
This file implements a privileged SPARC64 miscdevice exposing ADI/MCD memory version tags to user space. It is intended for crash dump and diagnostic tools that need to read or restore Application Data Integrity metadata.

## Important APIs, Types, and Functions
Core helpers are `read_mcd_tag()` and `set_mcd_tag()`, which use SPARC `ldxa`/`stxa` with `ASI_MCD_REAL` and exception-table fixups. File operations are `adi_read()`, `adi_write()`, and `adi_llseek()`, registered through `adi_miscdev`.

## Control Flow
Module init checks `adi_capable()` and registers a dynamic-minor miscdevice named after `KBUILD_MODNAME`. Reads allocate a temporary buffer up to one page, convert file offset units into real addresses by multiplying by `adi_blksize()`, read one tag per ADI block, batch-copy to user space, and advance `f_pos` by tags read. Writes copy user tag bytes in page-sized batches, set one tag per ADI block, advance the offset, and execute a final sync memory barrier.

## State and Persistence Behavior
The driver stores no per-open state. The persistent effect is modification of hardware-maintained ADI version tags for physical memory. File position is interpreted in tag units rather than bytes of physical memory. Failed reads/writes stop at the first hardware fault.

## Dependencies and Integration Points
It depends on SPARC64 ADI architecture helpers, ASI access, exception tables, miscdevice infrastructure, and user-copy helpers. Consumers are privileged user-space tools.

## Risks
This is a powerful low-level interface: writes can alter memory protection tags and affect corruption detection. `adi_read()` advances `*offp` by bytes/tags read, while address calculation multiplies by `adi_blksize()`, so API users must understand the unit. Partial progress before a fault is not returned if the code jumps to error, which may obscure how much work completed. The device relies on external permissions for privilege enforcement after registration.

## Test Signals
On ADI-capable SPARC64, verify miscdevice creation, reads/writes over valid and invalid physical ranges, offset seeking, zero-length write rejection, fault fixup returning `-EFAULT`, final memory barrier behavior, and access permissions for non-privileged users.
