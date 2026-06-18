# File Research: sources/block-storage/kvdo/vdo/io-submitter.h

Header for VDO I/O submission helpers.

Key responsibilities:
- Declares I/O submitter lifecycle: `vdo_make_io_submitter()`, `vdo_cleanup_io_submitter()`, and `vdo_free_io_submitter()`.
- Declares direct VIO processing, data VIO submission, and metadata VIO submission.
- Provides inline helpers `submit_metadata_vio()` and `submit_flush_vio()`.

Dependencies:
- Includes Linux bio, completion, kernel types, and VIO definitions.

Notable risks:
- `submit_flush_vio()` contains a FIXME asking whether pure `REQ_OP_FLUSH` can be used.
- Opaque `struct io_submitter` is forward-declared in `kernel-types.h`, not here.
