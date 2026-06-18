# sources/distributed-fs/openafs/src/WINNT/aklog/linked_list.c

Purpose: implements a minimal doubly linked list used by `aklog` for cell/path queues and duplicate string suppression.

Important APIs and control flow: `ll_init` initializes an empty list and aborts on NULL. `ll_add_node` allocates a node and inserts at head or tail. `ll_delete_node` scans for a node, relinks neighbors, frees the node, and decrements count. `ll_string_check` scans string data using `strcmp`. `ll_add_string` adds a `strdup` copy only if absent.

State and dependencies: list state is caller-owned in `linked_list`; node allocation uses C runtime `malloc/free`, and string data allocated by `ll_add_string` remains caller-owned for cleanup. Dependencies are only stdio/stdlib/string and the local header.

Risks and test signals: no list-level cleanup function exists, and node deletion does not free `data`; callers can leak strings. `ll_string_check` assumes every data pointer is a valid string. Tests should cover empty lists, head/tail insertion, delete first/last/missing node, duplicate string suppression, and allocation failure paths.
