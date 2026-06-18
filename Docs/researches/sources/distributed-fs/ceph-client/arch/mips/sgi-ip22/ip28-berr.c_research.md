# sources/distributed-fs/ceph-client/arch/mips/sgi-ip22/ip28-berr.c

Purpose: enhanced IP28 bus-error handler. It captures MC/HPC/DMA/cache-tag state, distinguishes fatal errors from discardable speculative bus errors, and exposes counters for diagnostics.

Important APIs and control flow: `save_and_clear_buserr()` snapshots CPU/GIO/error registers, HPC3 DMA descriptors, Ethernet/SCSI/PBDMA state, and cache tags around the error address. `print_buserr()` decodes hardware status and cache tags. `check_microtlb()`, `check_vdma_memaddr()`, and `check_vdma_gioaddr()` correlate errors with virtual DMA translation. `ip28_be_interrupt()` rejects fatal causes, HPC/EISA errors, non-address memory errors, and DMA descriptor hits, otherwise discards likely speculative errors. `ip22_be_init()` installs `ip28_be_handler()`, and `ip28_debug_be` enables verbose discard logging.

State, persistence, and integration: state includes diagnostic counters, last hardware snapshots, and optional debug flag. Dependencies include R4k cache tag operations, MC/HPC/IOC globals, and MIPS bus-error semantics. Risks include complex hardware heuristics, infinite fatal behavior through `die_if_kernel()`/SIGBUS paths, and disabled locking around diagnostics. Test signals are counters from `ip28_show_be_info()`, successful exception-table fixups, and safe discard of known speculative bus errors.
