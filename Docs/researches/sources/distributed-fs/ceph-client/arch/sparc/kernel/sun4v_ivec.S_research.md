# sources/distributed-fs/ceph-client/arch/sparc/kernel/sun4v_ivec.S

Purpose: handles sun4v hypervisor interrupt queues for CPU mondos, device mondos, resumable errors, and non-resumable errors at trap level.

Important APIs/symbols: defines `sun4v_cpu_mondo`, `sun4v_dev_mondo`, `sun4v_res_mondo`, and `sun4v_nonres_mondo`. It uses ASI queue head/tail registers, `trap_block` queue physical addresses/masks, `cpu_mondo_counter`, `ivector_table_pa`, IRQ work storage, and C callbacks `sun4v_resum_error()`, `sun4v_resum_overflow()`, `sun4v_nonresum_error()`, and `sun4v_nonresum_overflow()`.

Control flow: each handler compares queue head/tail and retries if empty. CPU mondos derive the current CPU from the trap block, increment the mondo counter, load the three-word xcall payload, advance the queue head, and jump to the handler PC encoded in the first word. Device mondos fetch IVEC or VIRQ cookie, link the bucket into IRQ work, and set the device softint. Error mondos copy a 64-byte queue entry into a kernel buffer if free, advance head, enter an IRQ trap frame, and call C; if the kernel buffer slot is full, they collapse head to tail and report overflow.

State and persistence: mutates hypervisor queue heads, CPU mondo counters, IRQ work queues, and per-CPU error buffers; no persistent storage.

Dependencies and integration points: depends on sun4v queue layout, trap-block offsets, CPU xcall ABI from `smp_64.c`, device IRQ softint processing, and error-reporting C code.

Risks: head/tail updates and kernel-buffer overflow handling are critical to avoid repeated traps or lost errors. CPU mondo handler trusts the payload PC. Queue entries are physical loads using ASI_PHYS_USE_EC.

Test signals: CPU xcall delivery, device IVEC/VIRQ interrupts, MSI-like device mondos, resumable/non-resumable error logging, queue-empty retry, and forced overflow handling.
