# sources/distributed-fs/ceph-client/include/linux/devcoredump.h

Purpose: Declares the device coredump API that lets drivers expose crash dump data to userspace for a bounded time after device/firmware failures.

Important APIs, types, and functions: Defines `DEVCD_TIMEOUT`, `_devcd_free_sgtable()`, `dev_coredumpv()`, `dev_coredumpm_timeout()`, `dev_coredumpsg()`, `dev_coredump_put()`, and convenience `dev_coredumpm()`.

Control flow: Drivers submit dumps as vmalloc buffers, custom read/free callbacks, or scatterlists. The framework creates a device coredump object, exposes it for userspace reads, and frees data after read or timeout. If devcoredump support is disabled, stubs immediately free the provided buffer or scatterlist.

State and persistence: Coredump data is transient and normally expires after five minutes if unread. `_devcd_free_sgtable()` frees pages and chained scatterlist tables. The framework owns data lifetime after submission.

Dependencies and integration points: Depends on device core, modules for owner pinning, vmalloc/slab, scatterlists, pages, and sysfs/devcoredump framework implementation. Integrated by drivers that collect firmware/device crash state.

Risks and test signals: Risks include submitting data with the wrong allocator/free callback, leaking chained scatterlists, double-free on disabled configs, exposing sensitive crash memory, and replacing unread dumps. Test vmalloc/custom/sg dump paths, timeout cleanup, module unload while dump is open, disabled config stubs, chained scatterlist freeing, and userspace read truncation.
