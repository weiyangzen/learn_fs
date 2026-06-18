<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/mod/sumversion.c -->
# sources/distributed-fs/ceph-client/scripts/mod/sumversion.c

## Purpose

`sumversion.c` computes module source-version hashes for `MODULE_INFO(srcversion, ...)`. It hashes relevant source files and dependency lists using an in-file MD4 implementation.

## Important APIs, Types, and Functions

The public function is `get_src_version()`. Internal MD4 helpers include `md4_init()`, `md4_update()`, `md4_transform()`, and `md4_final_ascii()`. Source parsing helpers include `parse_file()`, `parse_source_files()`, `parse_string()`, `parse_comment()`, and `is_static_library()`.

## Control Flow

Given a module name, the code reads the module's `.mod` file to find object/source inputs, skips static libraries as needed, parses source file content while normalizing comments and strings, updates the MD4 context, and writes an ASCII digest into the provided buffer.

## State and Persistence Behavior

State is local to the MD4 context and temporary file buffers. The result persists only when `modpost` emits it into generated `.mod.c`.

## Dependencies and Integration Points

It depends on `modpost.h`, `read_text_file()`, `get_line()`, Kbuild `.mod` files, and source file availability. It integrates with `CONFIG_MODULE_SRCVERSION_ALL` and module `version` metadata behavior in `modpost.c`.

## Risks and Edge Cases

The hash is build metadata, not cryptographic integrity. Missing `.mod` or source files, generated sources, static libraries, and parser approximations for C syntax can affect reproducibility. MD4 implementation and endian conversion must remain stable for existing version semantics.

## Test Signals

Compare srcversion output before and after source edits, comments, string changes, generated file changes, missing files, and static library references. Verify deterministic results across host endianness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/mod/sumversion.c -->
