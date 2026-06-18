# sources/distributed-fs/ceph-client/kernel/time/namespace_vdso.c

Purpose: supports time namespace VDSO data by allocating a per-namespace VVAR page, freezing namespace offsets into VDSO clock data, and zapping VVAR mappings when a task joins a namespace.

Important APIs and flow: `timens_setup_vdso_clock_data()` writes `VDSO_CLOCKMODE_TIMENS` and namespace offsets for monotonic, raw/coarse monotonic, boottime, and boottime alarm clocks. `find_timens_vvar_page()` returns the current task namespace page and warns on remote VVAR access. `timens_set_vvar_page()` freezes offsets once per non-init namespace under `timens_offset_lock`, including auxiliary clock data when configured. `timens_commit()` sets the page then calls `vdso_join_timens()`, which scans VMAs and zaps the VVAR special mapping so faults rebuild with the namespace-specific layout.

State and persistence: `ns->vvar_page` is allocated zeroed at clone time and freed at namespace teardown. `ns->frozen_offsets` permanently prevents later proc offset writes once a task enters the namespace and VDSO data is materialized.

Dependencies and integration: VDSO datastore/page layout, special VVAR mapping, mm VMA iteration, mmap read lock, time namespace offsets, and optional POSIX auxiliary clock data.

Risks and test signals: risks include stale VVAR mappings after setns/fork, remote access warnings, offset freeze races, and missing auxiliary clock offsets. Test namespace entry after offset writes, rejected writes after first task commit, VDSO clock_gettime results versus syscall paths, and VMA zapping across processes.
