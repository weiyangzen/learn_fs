
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/nvram_64.c

Purpose: PPC64 NVRAM partition manager plus crash/error persistence backend for RTAS, oops/panic logs, pstore records, Open Firmware config, common, and skiboot partitions.

Important APIs/types/functions: `nvram_write_os_partition`; `nvram_read_partition`; `nvram_init_os_partition`; `nvram_init_oops_partition`; `oops_to_nvram`; `nvram_pstore_open/read/write`; `nvram_scan_partitions`; `nvram_create_partition`; `nvram_remove_partition`; `nvram_find_partition`; `nvram_get_partition_size`; `nvram_checksum`; global partition descriptors such as `rtas_log_partition`, `oops_log_partition`, `skiboot_partition`, `of_config_partition`, and `common_partition`.

Control flow: boot scans raw NVRAM headers into a linked list, validating checksums and lengths. OS partitions are found, resized, created from free space, or recovered by deleting obsolete OS partitions. Oops setup allocates buffers, tries to register pstore, and falls back to a kmsg dumper with zlib compression. On oops/panic/emergency dump, the dumper avoids clobbering unread RTAS events, try-locks, captures recent printk text, compresses when possible, builds an `oops_log_info` header, and writes the error header plus payload to the NVRAM partition. Pstore read iterates through configured partition types, reads OS or firmware partitions, decodes old/new oops headers, and returns records to pstore.

State and persistence: maintains an in-memory partition list and partition metadata, plus durable NVRAM contents containing headers, OS error-log metadata, sequence numbers, compressed or raw panic text, and platform firmware data. Partition creation/removal mutates NVRAM headers and merges free partitions.

Dependencies and integration: depends on `ppc_md.nvram_read/write/size`, RTAS/OPAL platform state, pstore, kmsg_dump, zlib, endian conversions, and PowerPC NVRAM signature conventions.

Risks: NVRAM is small and partition fragmentation can prevent allocation; checksum or zero-length corruption terminates scan; crash paths cannot allocate except preallocated buffers; compression failure falls back to shorter raw capture; pstore and kmsg_dump must avoid overwriting unread RTAS events; partition clearing loop bounds are delicate.

Test signals: scan real or emulated NVRAM partition tables, create/remove/merge partitions, trigger panic/oops pstore writes and reads across reboot, test compressed and uncompressed records, RTAS unread-event protection, and corrupted checksum handling.
