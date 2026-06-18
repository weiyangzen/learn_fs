# sources/distributed-fs/ceph-client/tools/mm/page-types.c

Purpose: Inspects kernel page flags from `/proc/kpageflags`, optionally through process pagemap or file page-cache walks, and can mark pages idle or inject/forget hwpoison.

Important APIs and types: Global option state drives the tool. Key routines include `do_u64_read`, `pagemap_read`, `kpageflags_read`, `expand_overloaded_flags`, `well_known_flags`, `bit_mask_ok`, `add_page`, `walk_pfn`, `walk_vma`, `walk_task`, `walk_page_cache`, `parse_bits_mask`, and `show_summary`. Page flag names come from `kernel-page-flags.h` plus tool-local overloaded/raw bits.

Control flow: `main` parses options for raw mode, pid/file/address/cgroup filters, list modes, idle marking, hwpoison, and alternate kpageflags file. It opens required proc/sys/debugfs files, walks either PFN ranges or file cache/process mappings, accumulates page counts in a hash table keyed by normalized flags, optionally lists ranges or individual pages, then prints a summary.

State and persistence behavior: Most state is in global counters and hash tables. It can persist side effects by writing page-idle bitmap or debugfs hwpoison controls. File-cache walking mmaps files and touches cached pages to populate PTEs.

Dependencies and integration points: Uses Linux procfs, sysfs page-idle bitmap, debugfs hwpoison, cgroup inode IDs, `api/fs/fs.h` debugfs helpers, and UAPI page flag definitions.

Risks: Requires privileges for many files. Kernel ABI bit meanings and overloaded flags are version-sensitive. Fixed limits (`MAX_VMAS`, filter counts, hash size) can be exceeded. The file walker intentionally handles SIGBUS but still touches live files.

Test signals: Validate `--describe`, synthetic alternate `--kpageflags`, address-range filters, pid walks, file-cache walks, cgroup filtering, list/mapcount output, and privileged idle/hwpoison paths on controlled systems.
