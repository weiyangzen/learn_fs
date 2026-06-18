# File Research: sources/block-storage/kvdo/vdo/recovery-utils.h

Read completely: 90 lines.

This header declares recovery utility helpers and provides inline accessors/validators for loaded journal data. `vdo_get_recovery_journal_block_header()` maps a sequence number to the corresponding block offset in a loaded journal buffer. `vdo_is_valid_recovery_journal_block()` validates metadata type, nonce, and recovery count. `vdo_is_exact_recovery_journal_block()` additionally requires an exact sequence number match.

Public declarations cover asynchronous journal loading, head/tail discovery, and recovery journal entry validation.

Dependencies: constants, packed recovery journal block headers, recovery journal entries, recovery journal state, and VDO types.

Security/reliability notes: buffer indexing uses the journal's circular block-number helper, so callers must pass a buffer sized for the full journal and a journal with valid power-of-two sizing.
