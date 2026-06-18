# sources/distributed-fs/coda/coda-src/venus/local_repair.cc

Purpose: implements user-facing local mutation repair commands over a volume's `ClientModifyLog`: check the head mutation, discard it, preserve/reintegrate one mutation, preserve all possible mutations, and list CML entries.

Important APIs and flow: `ClientModifyLog::CheckCMLHead` formats the head CML entry and its `CheckRepair` diagnostic. `DiscardLocalMutation` validates that the head exists and is marked for repair, cancels freezes, calls `m->cancel()` in a recovery transaction, and reports success/failure. `reintvol::DiscardAllLocalMutation` is intentionally disabled in favor of `purgeml`. `PreserveLocalMutation` checks repair feasibility, calls `DoRepair`, and cancels the local CML entry after successful reintegration. `PreserveAllLocalMutation` iterates commit order until it hits an IOT transaction entry or an unrecoverable conflict, preserving entries that repair cleanly or have non-fatal check codes. `ListCML` writes all CML entries.

State and persistence: CML cancellation and freeze toggling are recoverable. User-visible messages are transient but depend on persistent CML opcodes, flags, and tids.

Dependencies and integration: depends on `cmlent::CheckRepair`, `DoRepair`, `GetLocalOpMsg`, `cancelFreezes`, `cml_iterator`, `vproc` repair context, and `reintvol` command dispatch.

Risks and test signals: risks include TODO dependency checks before discard, preserving entries with non-zero mutation codes, interaction with transaction-grouped CML entries, message buffer sizing, and proper freeze cancellation around `cancel`. Tests should cover empty logs, non-conflicting head discard rejection, discard success, preserve success/failure per opcode, preserve-all stopping at tids, and list output order.
