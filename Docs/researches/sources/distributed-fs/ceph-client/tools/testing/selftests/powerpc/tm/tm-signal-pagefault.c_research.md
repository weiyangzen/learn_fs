# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/tm/tm-signal-pagefault.c

Purpose: stresses kernel TM signal handling when signal-stack and signal-frame memory faults are serviced by userfaultfd.

Important APIs/types/functions: `get_uf_mem()`, `fault_handler_thread()`, `setup_uf_mem()`, `signal_handler()`, `have_userfaultfd()`, and `tm_signal_pagefault()` coordinate userfaultfd-backed memory and TM traps.

Control flow: the test sets up a userfaultfd-managed region and a fault-handler thread that copies backing data into faulting pages. It installs an alt stack from that region, handles SIGTRAP by redirecting `v_regs`, TM `v_regs`, and `uc_link` into userfaultfd memory, then triggers SIGTRAP once in active TM and once in suspended TM.

State and persistence behavior: `uf_mem`, `backing_mem`, offsets, and handler thread are process-global. Faulting pages are populated lazily with saved backing data.

Dependencies and integration points: requires HTM, non-synthetic TM, `userfaultfd`, pthreads, signal alt stack, and powerpc signal frame layout.

Risks and test signals: timeout is only 2 seconds because bugs may hang the kernel path. Failure appears as setup errors, timeout, or process crash.
