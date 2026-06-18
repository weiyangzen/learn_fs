# sources/distributed-fs/ceph-client/drivers/net/ipa/gsi_trans.h

Purpose: Declares the GSI transaction public interface and `struct gsi_trans`, the unit used by IPA endpoint and command code to describe transfers and immediate commands.

Important APIs/types: `IPA_COMMAND_TRANS_TRE_MAX` caps command transactions at 8 TREs. `struct gsi_trans` records GSI pointer, channel ID, cancellation state, reserved/used TRE counts, transfer length, caller data or command opcodes, scatterlist pointer, DMA direction, refcount, completion, and TX accounting snapshots. Public APIs cover pool init/alloc/free, DMA pool management, idle checks, transaction allocation/free, command/page/SKB add, commit/wait, and single-byte read helpers.

Control flow and integration: Callers allocate a transaction for a channel, add one or more operations, and commit it. Command code uses `gsi_trans_cmd_add()` and `gsi_trans_commit_wait()`; endpoint code uses page/SKB add and asynchronous commit. Completion is signaled through the embedded completion and IPA callbacks, while `gsi.c` consults transaction state during NAPI polling.

State and persistence: The header defines per-transaction mutable state but no global storage. Refcounting allows synchronous waiters and the polling path to coordinate destruction. `cancelled` carries reset/cancel state to IPA completion handlers.

Dependencies: Includes Linux completion, DMA direction, refcount, types, and `ipa_cmd.h` for command opcodes. Forward-declares device, page, scatterlist, SKB, GSI, and pools.

Risks: `used_count` can be less than `rsvd_count`, so users must not assume all reserved TREs are emitted. Command opcode storage is fixed to `IPA_COMMAND_TRANS_TRE_MAX`; command-channel TLV depth must be validated against that. Callers must free transactions after add failures.

Test signals: Compile integration with endpoint and command users, transaction wait completion, cancellation path behavior, and DMA map/unmap correctness for SKB/page transfers. Boundary tests should include max command TRE count and full-ring pressure.
