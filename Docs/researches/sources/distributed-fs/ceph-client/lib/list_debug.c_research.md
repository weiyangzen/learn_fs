# sources/distributed-fs/ceph-client/lib/list_debug.c

Purpose: slow-path validation and corruption reporting for Linux doubly linked list operations under list hardening/debug configurations.

Important APIs/types/functions: `__list_add_valid_or_report()` and `__list_del_entry_valid_or_report()`.

Control flow: add validation checks null `prev`/`next`, reciprocal link consistency, and double-add of `new` against adjacent nodes. Delete validation checks null links, poison values, and reciprocal `prev->next`/`next->prev` consistency. Any corruption path reports through `CHECK_DATA_CORRUPTION()` and returns false.

State/persistence: does not mutate lists; only reads list pointers and emits diagnostics/warnings.

Dependencies/integration: called from list manipulation macros when hardening/debug slow paths are enabled. Depends on `linux/list.h`, `bug.h`, `kernel.h`, and exported symbols.

Risks: diagnostic reads may fault if corruption points to invalid memory outside safe hardening assumptions. Reporting includes pointer values and may be noisy under repeated corruption.

Test signals: no local tests here; kernel list debug/hardening tests and any corruption reports from list misuse serve as signals.
