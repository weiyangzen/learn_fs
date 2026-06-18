# sources/distributed-fs/ceph-client/arch/parisc/kernel/pdt.c

Purpose: reads and monitors the PA-RISC firmware Page Deallocation Table, which records physical pages with correctable or uncorrectable memory errors, and prevents or reacts to use of those pages.

Important state includes `pdt_type`, `pdt_poll_interval`, `pdt_status`, and page-aligned `pdt_entry`. Important functions are `arch_report_meminfo`, `get_info_pat_new`, `get_info_pat_cell`, `report_mem_err`, `pdc_pdt_init`, `pdt_mainloop`, and `pdt_initcall`. Access modes cover no support, legacy PDC, newer PAT all-cell reporting, and older PAT cell-local reporting.

Control flow during early init probes PAT-new, PAT-cell, then legacy PDC interfaces. On success it logs table metadata, reads existing entries, reports DIMM location when available, warns if bad memory intersects the kernel image or initrd, reserves each bad page through `memblock_reserve`, and increments poisoned-page accounting. A late initcall starts `kpdtd`, which sleeps for five minutes normally or one minute after errors, polls firmware for new entries, reads only the required entries where possible, reports them, and invokes `memory_failure` for permanent or multi-bit errors or `soft_offline_page` for transient single-bit errors when memory-failure support is built.

State persists in firmware PDT contents, kernel status mirrors, memblock reservations, poisoned-page counters, and the kthread. Dependencies include PDC/PAT memory calls, `parisc_cell_num`, `memblock`, initrd bounds, memory-failure APIs, procfs `/proc/meminfo` reporting, and PA-RISC physical-address encoding.

Risks include PDT entry format differences between PAT and non-PAT systems, truncating to one page of entries, bad memory inside kernel/initrd areas where mitigation is limited, kthread failure on unexpected firmware errors, and ignored runtime errors without `CONFIG_MEMORY_FAILURE`. Test signals include boot logs with PDT type and entries, `/proc/meminfo` PDT counters, reserved bad pages in early memory maps, runtime memory-offline events, and firmware error injection or hardware logs matching kernel reports.
