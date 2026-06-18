# sources/distributed-fs/ceph-client/arch/sh/kernel/crash_dump.c

Purpose: provides SH old-memory copying for crash dump readers.

Important APIs and control flow: `copy_oldmem_page()` maps a crash-dump PFN with `ioremap()`, copies `csize` bytes from `offset` into the supplied `iov_iter` with `copy_to_iter()`, unmaps, and returns the bytes copied. A zero-size request returns immediately.

State, dependencies, and risks: it has no persistent state and depends on generic crash dump code, `ioremap()`, `iov_iter`, and old-memory reservation from kexec/crashkernel setup. It does not explicitly validate that `offset + csize` is within a page, so callers must honor the page-sized contract. Test signals are kdump capture reads, `/proc/vmcore` extraction, zero-length reads, and partial iterator-copy behavior.
