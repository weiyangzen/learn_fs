<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/ss/conditional.c -->
# sources/distributed-fs/ceph-client/security/selinux/ss/conditional.c

## Purpose
Implements SELinux conditional policy support: boolean symbol loading/indexing, reverse-polish conditional expression evaluation, conditional AV rule loading/writing, enabled-state updates, conditional decision contribution, and duplication of conditional state during policy operations.

## Important APIs, Types, and Functions
Public APIs include `cond_policydb_init()`, `cond_policydb_destroy()`, `cond_init_bool_indexes()`, `cond_destroy_bool()`, `cond_index_bool()`, `cond_read_bool()`, `cond_read_list()`, `cond_write_bool()`, `cond_write_list()`, `evaluate_cond_nodes()`, `cond_compute_av()`, `cond_compute_xperms()`, `cond_policydb_dup()`, and `cond_policydb_destroy_dup()`. Core internals are `cond_evaluate_expr()`, `evaluate_cond_node()`, `cond_insertf()`, `cond_read_av_list()`, and duplication helpers.

## Control Flow
Boolean records are read into the boolean symbol table and indexed by value. Conditional nodes read a current state, an RPN expression, and true/false AV lists. Each AV rule is inserted into `te_cond_avtab`; type rules are checked against unconditional and conditional conflicts. Evaluation recomputes each expression and toggles `AVTAB_ENABLED` on true/false list nodes. Decision computation searches matching conditional nodes and merges only enabled rules into `av_decision` or xperm decisions.

## State and Persistence
Policydb owns `bool_val_to_struct`, `cond_list`, `cond_list_len`, and `te_cond_avtab`. Conditional rule enabled state is stored in each AV node's key. Binary policy persistence writes boolean records and writes each conditional's AV rules directly, rebuilding the conditional AV table on load.

## Dependencies and Integration Points
Depends on `avtab`, `hashtab`, `symtab`, `policydb`, and services helpers for merging xperm data. It integrates with boolean writes from selinuxfs and security-server decision computation.

## Risks
Expression evaluation has fixed stack depth `COND_EXPR_MAXDEPTH`; malformed expressions become undefined and disable all rules for that node. Conflict checks for conditional type rules are subtle because one matching rule may be shared across true/false branches but additional conflicts are invalid. Duplication must preserve node pointer relationships into the duplicated conditional AV table.

## Test Signals
Load policies with simple and nested booleans, true/false branch rules, conditional xperms, conflicting type rules, invalid operators/boolean indexes, stack-depth overflow, boolean toggles through selinuxfs, policy write/read round trips, and policy duplication failure injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/ss/conditional.c -->
