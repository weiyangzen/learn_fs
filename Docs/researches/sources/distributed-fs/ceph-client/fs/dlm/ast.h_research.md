<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/dlm/ast.h -->
# sources/distributed-fs/ceph-client/fs/dlm/ast.h

Purpose: declares the DLM callback management interface implemented by `ast.c`.

Important APIs/types/functions: prototypes for `dlm_may_skip_callback`, `dlm_get_cb`, `dlm_add_cb`, `dlm_callback_start`, `dlm_callback_stop`, `dlm_callback_suspend`, and `dlm_callback_resume`.

Control flow: lock management code includes this header to decide whether callbacks can be skipped, allocate callback records, enqueue AST/BAST notifications, and manage callback execution around lockspace lifecycle and recovery.

State and persistence: no state in the header; it exposes operations over `struct dlm_lkb`, `struct dlm_callback`, and `struct dlm_ls` state owned elsewhere.

Dependencies and integration: depends on DLM internal type declarations provided before inclusion, especially lock blocks, callback records, and lockspaces. It links `lock.c`, `recoverd`, userspace paths, and lockspace lifecycle to `ast.c`.

Risks: signature changes must stay synchronized with callers and with userspace/user-lock routing semantics. `copy_lvb` is optional and must be handled by callers that care about lock value block propagation.

Test signals: compile coverage across DLM objects and runtime callback delivery tests validate this contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/dlm/ast.h -->
