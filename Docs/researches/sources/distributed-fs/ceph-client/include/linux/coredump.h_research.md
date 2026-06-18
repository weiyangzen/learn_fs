## sources/distributed-fs/ceph-client/include/linux/coredump.h

Purpose: This header declares coredump parameters and helper functions used to emit process core files safely and consistently.

Important APIs, types, and functions: Under `CONFIG_COREDUMP`, `struct core_vma_metadata` stores VMA start/end, flags, dump size, page offset, and backing file. `struct coredump_params` tracks signal info, output file, limit, mm flags, CPU, written byte count, file position, deferred skip amount, VMA count/data size, VMA metadata array, and pid. Helpers include `dump_skip_to`, `dump_skip`, `dump_emit`, `dump_align`, `dump_user_range`, and `vfs_coredump`. `core_file_note_size_limit` bounds note size. Logging macros `coredump_report` and `coredump_report_failure` add TGID and comm to ratelimited printk output. `validate_coredump_safety()` exists when sysctl support is present.

Control flow: Signal/exit code invokes `vfs_coredump()`, which fills `coredump_params` and format-specific dumpers use only the dump helpers to advance, align, skip, and emit file data. Logging macros report policy or write failures. Disabled builds stub out coredump behavior.

State and persistence: Coredump state persists during dump generation in `coredump_params` and output file contents. It serializes memory and VMA metadata to storage subject to resource limits.

Dependencies and integration points: It depends on mm, fs, signal info, current task identity, printk, sysctl, ELF/binfmt coredump implementations, and filesystem write paths.

Risks and test signals: Risks include exceeding dump limits, leaking sensitive mappings, incorrect skip/position accounting, partial writes, and unsafe coredump sysctl combinations. Test signals include coredump generation for sparse VMAs, file-backed mappings, RLIMIT_CORE, huge processes, failing filesystems, disabled config, and sysctl safety validation.
