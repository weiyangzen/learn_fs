<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/filter_flags_encoder.c -->
# sources/compression/xz/src/liblzma/common/filter_flags_encoder.c

Purpose: Encodes and sizes the on-wire `.xz` Filter Flags field for a single filter.

Important APIs: `lzma_filter_flags_size()` computes encoded ID VLI size plus properties-size VLI plus properties bytes. `lzma_filter_flags_encode()` emits the same fields into caller-provided output.

Control flow: Both functions reject reserved Filter IDs as programming errors. Encoding writes Filter ID, obtains and writes properties size, verifies output capacity for fixed properties bytes, calls `lzma_properties_encode()`, and advances `*out_pos`.

State/dependencies: Stateless. Depends on encoder property table functions from `filter_encoder.c` and VLI encoding.

Risks/tests: Output capacity mismatch returns `LZMA_PROG_ERROR` because callers are expected to size the field first. Tests should cover reserved IDs, unsupported IDs in size calculation, zero-size properties, variable-size simple properties, and exact buffer boundaries.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/filter_flags_encoder.c -->
