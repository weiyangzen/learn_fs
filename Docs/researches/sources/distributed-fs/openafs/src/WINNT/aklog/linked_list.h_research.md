# sources/distributed-fs/openafs/src/WINNT/aklog/linked_list.h

Purpose: declares the simple linked-list abstraction used by `aklog`.

Important APIs/types: defines `ll_node`, `linked_list`, `ll_end`, status constants, the `ll_add_data` macro, and functions for initialization, node add/delete, duplicate string checks, and unique string add.

State and dependencies: the header is standalone C and exposes struct layouts directly, so callers iterate nodes and manage stored data themselves.

Risks and test signals: direct struct access makes invariant enforcement caller-dependent. Tests should verify `nelements`, `first`, and `last` remain coherent after mixed head/tail operations and deletions.
