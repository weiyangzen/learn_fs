# sources/distributed-fs/ceph-client/arch/powerpc/mm/nohash/kaslr_booke.c

Purpose: implements early physical kernel randomization for BookE/e500 relocatable kernels.

Important APIs and control flow: `kaslr_choose_location()` reads the boot command line, honors `nokaslr`, combines build/FDT/timebase entropy and an optional FDT `kaslr-seed` that is wiped after reading, computes CAM-mappable lowmem, records DTB/initrd/crash/reserved-memory regions, chooses a 64 MiB bucket and 16 KiB-aligned offset, and searches for a non-overlapping placement. `kaslr_early_init()` updates kernel start globals, creates a temporary TLB entry if needed, copies the kernel, flushes I-cache, and branches to relocated code. `kaslr_late_init()` zeros the original image.

State and dependencies: state includes global `regions`, boot command line, `kernstart_addr`, `kernstart_virt_addr`, and `is_second_reloc`. Dependencies include libfdt, memblock/CAM dry-run sizing, crashkernel parsing, cache flushing, and relocation assembly hooks. Risks are weak entropy without `kaslr-seed`, overlap calculation truncation to 32-bit ranges, incorrect reserved-memory cell parsing, and failure to clear the original kernel. Test signals include randomized and `nokaslr` boots, initrd/crashkernel/reserved-memory overlap cases, seed wiping, and relocation above 64 MiB.
