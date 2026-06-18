<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/uv_mmtimer.c -->
# sources/distributed-fs/ceph-client/drivers/char/uv_mmtimer.c

Purpose: SGI UV platform misc character device exposing the UV real-time clock as `/dev/mmtimer`. It provides ioctls for resolution, frequency, counter width/current value, and supports read-only mmap of the hardware RTC page.

Important APIs/types/functions: `uv_mmtimer_ioctl()` handles `MMTIMER_GETOFFSET`, `MMTIMER_GETRES`, `MMTIMER_GETFREQ`, `MMTIMER_GETBITS`, `MMTIMER_MMAPAVAIL`, and `MMTIMER_GETCOUNTER`. `uv_mmtimer_mmap()` maps the UV local MMR RTC page with noncached page protection. `uv_mmtimer_init()` validates UV hardware and clock frequency, computes femtosecond period, and registers a `miscdevice`.

Control flow: module init rejects non-UV systems and invalid `sn_rtc_cycles_per_second`, computes `(1e15 + freq/2) / freq`, registers the misc device, and logs version/frequency. Ioctl requests either return scalar values directly or copy frequency/resolution/counter values to userspace. `MMTIMER_GETOFFSET` returns zero for hub rev 1 or a cacheline-based per-processor offset for replicated RTC pages. mmap accepts exactly one read-only page, forces noncached mapping, aligns `UV_LOCAL_MMR_BASE | UVH_RTC`, and calls `remap_pfn_range()`.

State and persistence: only `uv_mmtimer_femtoperiod` and the misc registration are stored by the driver. The actual counter and frequency live in UV platform firmware/MMR state and are not persisted by this module.

Dependencies and integration: depends on x86 SGI UV platform headers, `is_uv_system()`, `uv_local_mmr_address()`, `uv_get_min_hub_revision_id()`, `uv_blade_processor_id()`, `sn_rtc_cycles_per_second`, miscdevice, mmap, and mmtimer ioctl ABI.

Risks: this is hardware-specific and returns generic `-1` rather than specific errno from init failures. mmap assumes the UV RTC physical mapping and rejects large pages over 64 KiB. Userspace sees raw hardware timing state, so counter width/frequency correctness depends on firmware values. Writeable mappings must remain rejected.

Test signals: boot on UV hardware, verify `/dev/mmtimer`, ioctl frequency/resolution/bit count/counter values, offset behavior across hub revisions and CPUs, read-only mmap success for one page, mmap rejection for wrong length/write flags, and failure on non-UV systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/uv_mmtimer.c -->
