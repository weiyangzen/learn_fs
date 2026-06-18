# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/hvcserver.c

Purpose: Provides architecture-specific API helpers for IBM hypervisor virtual console server adapters, including partner discovery and connection registration/freeing.

Important APIs/types/functions: Defines `hvcs_convert()`, exported `hvcs_free_partner_info()`, helper `hvcs_next_partner()`, exported `hvcs_get_partner_info()`, `hvcs_register_connection()`, and `hvcs_free_connection()`.

Control flow: Partner discovery initializes the caller-supplied page buffer, iteratively calls `H_VTERM_PARTNER_INFO` using the previous partner id/address as cursor, stops on all-ones terminator, allocates `struct hvcs_partner_info` entries with `GFP_ATOMIC`, copies location code text, and appends to the caller list. Connection helpers issue `H_REGISTER_VTERM` and `H_FREE_VTERM`, mapping hypervisor return codes to Linux errnos.

State and persistence: The file owns no global mutable state. Persistent effects are caller-owned partner info lists and hypervisor vterm connection state. Allocated list entries must be freed through `hvcs_free_partner_info()`.

Dependencies and integration points: Depends on PowerVM hcalls, `struct hvcs_partner_info`, hvcs driver code, page-sized firmware work buffer supplied by caller, and list management.

Risks: Partner discovery may be called under spinlock, so allocations use `GFP_ATOMIC` and can fail. If firmware returns an error after some partners, the function treats partial lists as success. Connection `-EINVAL` has ambiguous firmware meaning and may require caller refresh/retry. `more` is constant but loop exits through terminator or error.

Test signals: HVCS partner enumeration, connection open/close, busy retry on free, partial partner-list behavior, allocation failure cleanup, and module user stress under concurrent console changes are useful.

Source read size: 239 lines, 7296 bytes.
