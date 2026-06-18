# sources/distributed-fs/ceph-client/include/linux/remoteproc/st_slim_rproc.h

Purpose: this header describes STMicroelectronics SLIM remote processor allocation support and its memory/register layout.

Important APIs/types/functions: constants `ST_SLIM_MEM_MAX` and `ST_SLIM_MAX_CLK` bound memory and clock arrays. Anonymous enum values identify `ST_SLIM_DMEM` and `ST_SLIM_IMEM`. `struct st_slim_mem` stores CPU virtual I/O address, bus address, and size. `struct st_slim_rproc` stores the `rproc` handle, DMEM/IMEM descriptors, `slimcore` and `peri` register mappings, and private clock pointers. APIs are `st_slim_rproc_alloc()` and `st_slim_rproc_put()`.

Control flow: platform code calls `st_slim_rproc_alloc()` with a device and firmware name, receiving a populated wrapper around remoteproc plus mapped memory/register resources and clocks. It later releases the object with `st_slim_rproc_put()`.

State and persistence: the wrapper persists remoteproc pointer, memory mappings, register bases, and clock handles for the SLIM device lifetime. Firmware and hardware memory contents are external state.

Dependencies and integration points: integrates with remoteproc core, platform devices, clock framework, MMIO mapping, and ST SLIM firmware loading.

Risks: array bounds are fixed at two memories and four clocks; new hardware with more resources would need header changes. Incorrect bus/CPU address pairing can corrupt firmware load or data access. Test signals include allocation failure unwinding, firmware load to IMEM/DMEM, clock enable/disable sequencing, and remoteproc boot/stop on ST platforms.
