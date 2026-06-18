# sources/distributed-fs/ceph-client/drivers/nvmem/rmem.c

Purpose: NVMEM provider backed by reserved memory, with optional Mobileye EyeQ5 bootloader-config checksum validation.

Important APIs/types/functions: `struct rmem` stores device, NVMEM, and `struct reserved_mem`. `rmem_read()` maps the reserved region with `memremap()`, copies the requested bytes, and unmaps immediately. `rmem_eyeq5_checksum()` validates magic, size, and CRC32 over the reserved-memory payload before registration.

Control flow: probe looks up reserved memory by the device node, fills NVMEM config with size and read callback, optionally runs compatible-specific checksum, then registers. Reads bounds-check against reserved memory size and map only during the read.

State/persistence: the backing region is reserved RAM populated by firmware/bootloader; it persists across kernel runtime but not necessarily across power cycles. Driver has no write path and no cache.

Dependencies/integration: compatibles `nvmem-rmem` and `mobileye,eyeq5-bootloader-config`; depends on reserved-memory OF binding, memremap, CRC32, and NVMEM provider.

Risks: repeated reads remap the entire reserved region, which is simple but inefficient for large/frequent reads. Checksum validation allocates `header.size`; size is bounded by reserved memory before allocation. The memory is not made read-only, so other kernel code could still corrupt it if mapped elsewhere.

Test signals: missing reserved memory, read bounds failure, EyeQ5 bad magic/size/CRC, successful checksum, and NVMEM reads after registration.
