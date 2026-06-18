<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/ss/constraint.h -->
# sources/distributed-fs/ceph-client/security/selinux/ss/constraint.h

## Purpose
Defines SELinux constraint expression structures used to impose restrictions beyond type enforcement and role transitions. Constraints can compare users, roles, types, and MLS levels/categories across source, target, and validatetrans contexts.

## Important APIs, Types, and Functions
Key types are `struct constraint_expr` and `struct constraint_node`. Expression kinds include logical NOT/AND/OR, attribute comparisons, and name-set comparisons. Attribute flags select user/role/type, source versus target, validatetrans extra target, and MLS low/high level pairings. Operators include equality, inequality, dominance, dominated-by, and incomparability. `CEXPR_MAXDEPTH` caps evaluation stack depth.

## Control Flow
This header does not implement evaluation; policydb/services code builds linked lists of `constraint_expr` under `constraint_node`, then decision code evaluates them when permissions are constrained. The linked-list layout supports serialized policy expressions and sequential evaluation.

## State and Persistence
Constraint state is policy-owned and persistent for the life of a loaded policy. Each expression may own an `ebitmap names` set and a `type_set *type_names`, with the next pointer forming the expression stream.

## Dependencies and Integration Points
Depends on `ebitmap` and policydb type-set definitions from including translation units. Integrated with access-decision checks and transition validation in the SELinux security server.

## Risks
Constraint expressions are security-critical because they can deny permissions otherwise allowed by TE/RBAC. MLS attribute flags are numerous and easy to misinterpret. Memory ownership for `names` and `type_names` must be paired with policydb destruction paths.

## Test Signals
Load policies with user/role/type constraints, MLS dominance constraints, validatetrans constraints using extra target context, malformed expression depth/operator cases, and permissions allowed by TE but denied by constraints.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/ss/constraint.h -->
