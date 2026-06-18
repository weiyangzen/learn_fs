
# sources/distributed-fs/ceph-client/tools/perf/util/mmap.h

Purpose: declares perf's higher-level mmap wrapper around libperf ring buffers, including optional AIO, auxtrace, compression, and affinity metadata.

Important APIs/types/functions: `struct mmap_cpu_mask` stores a bitmap and bit count. `MMAP_CPU_MASK_BYTES` computes its byte size. `struct mmap` embeds `struct perf_mmap core`, `struct auxtrace_mmap`, optional AIO control/data arrays, affinity mask, compression buffer pointer, perf data file pointer, and zstd state. `struct mmap_params` wraps libperf params plus AIO count, affinity mode, flush mode, compression level, and auxtrace mmap params. Public functions are `mmap__mmap`, `mmap__munmap`, `perf_mmap__read_forward` declaration, `perf_mmap__push`, `mmap__mmap_len`, and `mmap_cpu_mask__scnprintf`.

Control flow: no local execution; callers allocate/initialize `struct mmap`, pass params into `mmap__mmap`, read/push data, then call `mmap__munmap`.

State and persistence: describes live process memory mappings and buffers tied to active perf events. The caller owns the struct storage; helpers own the dynamic subfields after successful setup.

Dependencies: includes internal libperf mmap, Linux bitops/types, perf cpumap, optional `<aio.h>`, auxtrace, and compression helpers.

Integration points: included by evlist/recording code and data writers that coordinate mmap buffers. It is also the stable boundary for auxtrace and compression support.

Risks: ABI is internal but broad; changing field layout affects many perf utility users. Callers must respect ownership and zero/cleanup expectations. Test signals are build coverage across AIO/non-AIO and auxtrace/non-auxtrace configurations plus record-mode runtime tests.
