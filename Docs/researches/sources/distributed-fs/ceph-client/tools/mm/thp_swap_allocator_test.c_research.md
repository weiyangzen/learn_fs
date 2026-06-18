# sources/distributed-fs/ceph-client/tools/mm/thp_swap_allocator_test.c

Purpose: Stress test for multi-size THP swap-out allocation, checking that 64KB transparent huge pages obtain whole swap slots instead of falling back to split swap-out.

Important APIs and functions: `aligned_alloc_mem` wraps `posix_memalign`; `random_madvise_dontneed` randomly discards aligned regions then refaults them; `random_swapin` randomly touches regions; `read_stat` reads THP `swpout` and `swpout_fallback` sysfs counters. `main` implements `-s` for a small-folio comparison area and `-a` for aligned swap-in.

Control flow: The program allocates 60MB 64KB-aligned mTHP memory, marks it `MADV_HUGEPAGE`, optionally allocates a 4MB `MADV_NOHUGEPAGE` region, warms and pages out memory, then performs 100 iterations of reading counters, random swap-in/refault, optional small-folio activity, `MADV_PAGEOUT`, final counter read, and fallback-percentage print.

State and persistence behavior: Process memory and kernel swap/THP counters are the live state. The program does not write files, but it relies on externally configured zram/swap and THP sysfs state.

Dependencies and integration points: Uses Linux `madvise` flags and `/sys/kernel/mm/transparent_hugepage/hugepages-64kB/stats/*`. Intended for MM regression testing.

Risks: `read_stat` returns 0 on errors, which can hide missing sysfs counters. Fallback percentage divides by zero if no swpout counters change. Randomness is not seeded. Test assumptions depend on 64KB mTHP support and swap setup.

Test signals: Run with documented zram/THP setup, both with and without `-s` and `-a`; verify fallback remains near 0 percent and counter deltas are nonzero.
