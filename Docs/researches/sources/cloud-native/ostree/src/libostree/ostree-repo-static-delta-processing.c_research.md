# sources/cloud-native/ostree/src/libostree/ostree-repo-static-delta-processing.c

## Purpose

This file executes a parsed static delta part. It interprets the compact operation stream emitted by the compiler, reconstructs metadata and file objects, writes them into the repository, supports rollsum-style copy from existing source objects, applies bsdiff patches, and exposes asynchronous execution wrappers.

## Important APIs, Types, and Functions

- `StaticDeltaExecutionState` holds interpreter state: object checksum array, op stream, mode/xattr dictionaries, payload bytes, current output object, bare-content writer, read-source fd, and stats/error flags.
- `_ostree_static_delta_part_execute()` is the synchronous interpreter.
- `_ostree_static_delta_part_execute_async()` and `_ostree_static_delta_part_execute_finish()` wrap execution in a `GTask`.
- `read_varuint64()`, `validate_ofs()`, `open_output_target()`, and `do_content_open_generic()` decode common operands and validate payload bounds.
- Dispatch functions implement each opcode: `dispatch_open_splice_and_close()`, `dispatch_open()`, `dispatch_write()`, `dispatch_set_read_source()`, `dispatch_unset_read_source()`, `dispatch_close()`, and `dispatch_bspatch()`.

## Control Flow

Execution parses the packed object list from the part header, extracts the mode dictionary, xattr dictionary, payload, and operation bytes from the part payload, then loops until the op stream is exhausted. Each opcode consumes varint operands from `state->opdata`. Unknown opcodes fail with an invalid-argument error. Optional stats count operations using the opcode-to-index mapping.

`OPEN_SPLICE_AND_CLOSE` is the one-shot path. For metadata objects it copies bytes from the payload into an aligned `GBytes`, parses the correct metadata variant type, and writes metadata. For content objects it reads mode/xattr offsets and content payload coordinates, then either uses a bare-repo fast path or constructs a raw file content stream for symlinks and non-bare modes before writing content. It always closes afterward.

`OPEN`, `WRITE`, `SET_READ_SOURCE`, `UNSET_READ_SOURCE`, `BSPATCH`, and `CLOSE` support optimized content reconstruction. `OPEN` starts a bare-content writer unless the object already exists. `WRITE` copies either from the part payload or from the current read-source fd. `SET_READ_SOURCE` reads a checksum from the payload and opens the corresponding bare file object. `BSPATCH` maps the source file, allocates a target buffer, reads patch bytes from payload through a bspatch stream, and writes the result. `CLOSE` commits the bare content and asserts the resulting checksum.

## State and Persistence Behavior

The interpreter writes metadata and content objects to the repository through `ostree_repo_write_metadata()`, `ostree_repo_write_content()`, and private bare-content helpers. It skips writes for objects already present. It opens source objects from the repository for copy/patch operations and closes the fd when the read source is unset or the object closes. Temporary state is cleaned through `_ostree_repo_bare_content_cleanup()`.

## Dependencies and Integration Points

This file depends on opcode and format definitions from the private header, varint utilities, bspatch, GLib/GIO streams, bare repo write internals, checksum conversion helpers, and raw file conversion helpers. It is invoked by offline execution and dump/stat paths in `ostree-repo-static-delta-core.c`.

## Risks and Edge Cases

Offset validation is critical because payload coordinates come from external delta data. The code checks overflow and payload bounds before payload reads, but read-source fd reads also need EOF handling, which `dispatch_write()` performs. `dispatch_open()` asserts bare-family repository modes for multi-op reconstruction, so archive mode relies on the one-shot path. `BSPATCH` allocates the full output size in memory. Stats-only mode must consume operands while avoiding writes and cleaning partial state.

## Test Signals

Tests should execute every opcode, include stats-only dumping, validate checksum mismatch on close, reject bad offsets and malformed varints, handle existing objects without rewriting, copy from read-source objects, apply bsdiff patches, reconstruct symlinks, run against bare and bare-user modes, exercise cancellation, and verify async finish propagates errors.
