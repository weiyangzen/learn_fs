# sources/distributed-fs/ceph-client/include/linux/libfdt_env.h

Purpose: supplies Linux kernel environment definitions required by the shared libfdt code.

Important APIs and types: maps `INT32_MAX`/`UINT32_MAX` to kernel limits, defines `fdt16_t`, `fdt32_t`, and `fdt64_t` as big-endian integer types, and maps `fdt32_to_cpu()`, `cpu_to_fdt32()`, `fdt64_to_cpu()`, and `cpu_to_fdt64()` to Linux byte-order helpers.

Control flow: libfdt uses these macros while reading and writing big-endian FDT fields from caller-provided blobs.

State and persistence: no state is stored. Correctness affects persistent FDT blob interpretation.

Dependencies and integration points: depends on Linux limits/string headers and architecture byte-order definitions; consumed by `linux/libfdt.h`.

Risks and test signals: risks include endian conversion mistakes and type-width drift. Test FDT parsing on big- and little-endian builds, property length/address decoding, and overlay application.
