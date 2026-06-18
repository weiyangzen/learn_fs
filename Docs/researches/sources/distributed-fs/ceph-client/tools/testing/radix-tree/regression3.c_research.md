# sources/distributed-fs/ceph-client/tools/testing/radix-tree/regression3.c

Purpose: checks iterator retry and resume helpers after concurrent-like insertion during radix-tree slot and tagged iteration.

Important APIs/types/functions: `regression3_test()` uses `RADIX_TREE`, `radix_tree_for_each_tagged()`, `radix_tree_for_each_slot()`, `radix_tree_iter_retry()`, `radix_tree_iter_resume()`, and `radix_tree_deref_retry()`.

Control flow: starts with one tagged entry, inserts a second entry during tagged iteration, exercises retry handling, deletes/reinserts during untagged iteration, then forces `radix_tree_iter_resume()` from index 0 for both untagged and tagged iteration. It deletes both entries at the end.

State and persistence: only stack-local tree and constant pointer values are used. No heap allocation and no persistence.

Dependencies/integration: declared by `regression.h`; uses kernel radix-tree iterator macros and `printv()`.

Risks and test signals: the historical failure was NULL dereference or stale cached tag state after resume. Completion with "passed" is the signal; assertions are implicit through crash avoidance and iterator behavior.
