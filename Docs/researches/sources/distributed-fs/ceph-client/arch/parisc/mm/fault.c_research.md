# sources/distributed-fs/ceph-client/arch/parisc/mm/fault.c

Purpose: handles PA-RISC page faults, access-type decoding, exception-table fixups, trap descriptions, user signal delivery, and non-access DTLB faults.

Important APIs and functions: `parisc_acctyp()` decodes faulting instructions into `VM_READ`, `VM_WRITE`, or `VM_EXEC`; `fixup_exception()` applies exception-table fixups for kernel user-access helpers; `trap_name()` names trap codes; `do_page_fault()` is the main MM fault handler; `handle_nadtlb_fault()` handles cache/probe/LPA non-access DTLB cases.

Control flow: `do_page_fault()` rejects no-MM contexts, derives access flags from the instruction, finds or expands the VMA, validates permissions, calls `handle_mm_fault()`, handles retry/completed/error cases, and maps failures to kernel fixups, user `SIGSEGV`/`SIGBUS`, memory-failure signals, or `parisc_terminate()`. `handle_nadtlb_fault()` nullifies selected cache flush/purge instructions, evaluates PROBE without faulting pages in, and returns zero for unhandled cases.

State and persistence: updates register state during fixups and non-access handlers, including IAOQ, PSW bits, base modification, target registers, and error registers. It logs fatal user faults subject to `show_unhandled_signals` and rate limits.

Dependencies and integration: called from `arch/parisc/kernel/traps.c`. Relies on Linux MM, exception tables, perf fault events, hugetlb memory failure helpers, and PA-RISC instruction/register definitions.

Risks: instruction access decoding must be accurate or permissions and signal codes will be wrong. Kernel fixups must avoid taking branch delay slots. PROBE handling intentionally does not fault pages in, so it can differ from a subsequent real access.

Test signals: user read/write/execute faults, stack growth, invalid permissions, unmapped addresses, OOM, hwpoison, kernel `get_user`/`put_user` fixups, unaligned traps, cache flush nullification, PROBE results, and LPA target zeroing.
