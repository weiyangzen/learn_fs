<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/csiostor/csio_defs.h -->
## sources/distributed-fs/ceph-client/drivers/scsi/csiostor/csio_defs.h

Purpose: this header provides common Chelsio FCoE definitions, generic state-machine helpers, list helpers, stats macros, WWN validation, 64-bit MMIO fallbacks, and assertion macros used across csiostor.

Important APIs, types, and functions: macros include `CSIO_INVALID_IDX`, `CSIO_INC_STATS`, `CSIO_DEC_STATS`, `CSIO_VALID_WWN`, `CSIO_DID_MASK`, `CSIO_WORD_TO_BYTE`, `csio_list_next`, `csio_list_prev`, `CSIO_ASSERT`, and `CSIO_DB_ASSERT`. Fallback inline `readq()` and `writeq()` are defined when absent. State-machine definitions include `enum csio_ln_ev`, `csio_sm_state_t`, `struct csio_sm`, and helpers `csio_set_state()`, `csio_init_state()`, `csio_post_event()`, `csio_get_state()`, and `csio_match_state()`.

Control flow: `csio_post_event()` invokes the current state function directly, making these state machines synchronous unless callers arrange deferred context elsewhere. `csio_set_state()` and `csio_init_state()` update the function pointer in `struct csio_sm`. `csio_match_state()` compares the current function pointer to a known state implementation. `csio_list_deleted()` checks whether a list head points to itself in both directions.

State and persistence behavior: this header does not own storage. It defines how other objects store state as function pointers in `struct csio_sm` and how stats fields are incremented/decremented. There is no persistence beyond the in-memory driver objects using these helpers.

Dependencies and integration points: it depends on Linux kernel, list, timer, PCI, jiffies, and bug headers. It is foundational for csiostor lnode and hardware state machines and for shared stats accounting.

Risks: function-pointer state machines are compact but provide little type safety; the helpers accept `void *`, so misuse can compile and fail at runtime. `CSIO_VALID_WWN()` only checks the high nibble of the first byte, which is a narrow validation. `CSIO_ASSERT()` maps to `BUG_ON()`, making assertion failures fatal.

Test signals: compile coverage across architectures with and without native `readq/writeq`, state-machine transition tests for expected function-pointer matches, debug builds with `__CSIO_DEBUG__`, and static analysis for `void *` helper misuse.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/csiostor/csio_defs.h -->
