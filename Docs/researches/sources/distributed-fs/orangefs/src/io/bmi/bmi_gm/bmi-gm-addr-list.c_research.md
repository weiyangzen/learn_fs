<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi_gm/bmi-gm-addr-list.c -->
## sources/distributed-fs/orangefs/src/io/bmi/bmi_gm/bmi-gm-addr-list.c

Purpose: Implements GM method address list operations over OrangeFS quicklists.

Important APIs, types, and functions: `gm_addr_add()` inserts the `struct gm_addr` embedded list node into a provided list. `gm_addr_del()` removes it. `gm_addr_search()` scans a list for matching GM node id and port id and returns the enclosing `bmi_method_addr_p`.

Control flow and state: The list state is owned by the caller, primarily `gm_addr_list` in `bmi-gm.c`. `gm_addr_search()` linearly scans and compares `node_id` and `port_id`.

Dependencies and integration points: Depends on `bmi-gm-addressing.h`, `bmi-method-support.h`, `quicklist`, and GM headers. It assumes `struct bmi_method_addr` and `struct gm_addr` were allocated contiguously by `bmi_alloc_method_addr()`, then reconstructs the generic pointer by subtracting `sizeof(struct bmi_method_addr)` from the method-data pointer.

Risks and test signals: The reverse pointer arithmetic is fragile if allocation layout changes or alignment padding assumptions differ. There is no locking here; callers must hold the GM interface mutex. Tests should cover add/search/delete and duplicate node/port behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi_gm/bmi-gm-addr-list.c -->
