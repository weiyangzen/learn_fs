# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/common/command_buffer.c

Purpose: implements HabanaLabs command-buffer allocation, mapping, mmap exposure, ioctl handling, kernel CB pools, and per-context command-buffer VA pools.

Important APIs/functions: `hl_cb_create()` validates device/reset state and size, then allocates an `hl_mmap_mem_buf` using `cb_behavior`. Allocation may reuse a kernel CB pool entry, allocate internal pool memory, or allocate coherent DMA memory. Optional `cb_map_mem()` reserves device VA from `ctx->cb_va_pool`, maps the CB into the device MMU, and invalidates MMU cache. `hl_cb_destroy()` atomically marks a handle destroyed and drops the handle reference. `hl_cb_info()` reports usage count or mapped device VA. `hl_cb_ioctl()` dispatches create/destroy/info UAPI operations. Kernel helpers create/get/destroy CBs, initialize/finalize the kernel CB pool, and initialize/finalize per-context CB VA pools.

Control flow: user ioctl creates CB handles in a file memory manager; command submission gets CB refs and increments usage elsewhere; mmap uses ASIC-specific mmap callback; release unmaps, removes debugfs, drops context ref, and either returns CB to pool or frees it.

State and persistence: CBs store kernel address, bus address, size, mapped VA, context/device refs, pool/internal flags, handle-destroyed atomic, and mmap buffer linkage. VA pools reserve a 4 GiB host VA range per context when supported.

Dependencies: HabanaLabs memory manager, MMU, ASIC DMA/mmap callbacks, gen_pool, debugfs, UAPI, reset/device status, and context refs.

Risks: GFP_ATOMIC allocation path is latency-sensitive. Mapping is unsupported for kernel context. Destroy can occur while CB is in use, leaving release to final ref. MMU map/unmap/cache invalidation must stay under `mmu_lock`.

Test signals: create/destroy/info ioctl, max-size rejection, disabled/reset device rejection, pool reuse, internal CB allocation, mapped CB VA reporting, mmap, destroy while in use, VA pool init/fini, and MMU failure unwinds.
