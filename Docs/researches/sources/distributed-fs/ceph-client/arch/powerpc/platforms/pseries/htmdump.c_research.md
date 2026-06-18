# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/htmdump.c

Purpose: Implements a debugfs interface for PowerVM Hardware Trace Macro data and control through the `H_HTM` hcall.

Important APIs/types/functions: Maintains global buffers and selectors `nodeindex`, `nodalchipindex`, `coreindexonchip`, `htmtype`, `htmconfigure`, `htmstart`, `htmsetup`, and `htmflags`. Key functions include `htm_return_check()`, read handlers for trace/status/info/caps/system memory, setters/getters for configure/start/setup/flags, `htmdump_init_debugfs()`, module init, and module exit.

Control flow: Module init refuses to run inside KVM guests, allocates page buffers, and creates `arch_debugfs_dir/htmdump` controls. Reads issue `H_HTM` dump/status/capability/config hcalls using current selector globals and copy returned buffer data to userspace. Write controls configure/deconfigure, start/stop, set up buffer size, and choose wrap mode, updating local state only on successful hcall completion.

State and persistence: Persistent state consists of debugfs files, allocated page buffers, selector/control globals, and HTM hypervisor state changed by configure/start/setup hcalls. No locking protects concurrent debugfs readers/writers.

Dependencies and integration points: Depends on debugfs, PowerVM `htm_hcall_wrapper()`, hcall return codes, `arch_debugfs_dir`, physical-address access to kmalloc buffers, and KVM guest detection.

Risks: Global buffers and controls are shared across all users without serialization. Error unwinding in `htmdump_init_debugfs()` can leak earlier buffers if a later allocation fails before module exit. Several readers trust output-buffer header fields for copy sizes. `htmdump_read()` updates `*ppos` but passes a local offset to `simple_read_from_buffer()`, making repeated-read semantics worth testing.

Test signals: Debugfs file creation, capability/status/info reads on HTM-capable PowerVM, configure/start/stop/setup/flags writes, hcall error-code mapping, concurrent debugfs access, module unload leak checks, and KVM guest refusal are useful.

Source read size: 589 lines, 15960 bytes.
