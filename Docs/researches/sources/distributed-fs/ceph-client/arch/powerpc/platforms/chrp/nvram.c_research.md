# sources/distributed-fs/ceph-client/arch/powerpc/platforms/chrp/nvram.c

Purpose: provides CHRP `/dev/nvram` backend hooks through RTAS NVRAM fetch/store calls.

Important functions: `chrp_nvram_read_val`, `chrp_nvram_write_val`, `chrp_nvram_size`, and exported initializer `chrp_nvram_init`. Static state includes `nvram_size`, a four-byte RTAS transfer buffer, and `nvram_lock`.

Control flow: initialization finds the Open Firmware node of type `nvram`, reads its `#bytes` property, stores the size, logs it, and installs `ppc_md.nvram_read_val`, `ppc_md.nvram_write_val`, and `ppc_md.nvram_size`. Reads and writes range-check the byte address, serialize through `nvram_lock`, call RTAS `NVRAM_FETCH` or `NVRAM_STORE` with the physical address of `nvram_buf`, and return `0xff` or log on RTAS failure.

State and dependencies: depends on device tree, RTAS function tokens, `ppc_md` machdep hooks, and a global one-byte transfer buffer protected by a spinlock. Risks include RTAS calls under IRQ-disabled spinlock latency, physical address validity of a static buffer, silent write failures, and returning `0xff` for both real data and error. Test signals are NVRAM size detection, byte read/write round trips, out-of-range logging, and RTAS error handling.
