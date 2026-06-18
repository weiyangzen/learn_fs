# sources/distributed-fs/glusterfs/xlators/features/metadisp/src/gen-fops.py

## Purpose

`gen-fops.py` generates metadisp default fop implementations from libglusterfs fop metadata, routing each operation to either metadata child, data child, or a GFID-rewritten data loc.

## Important APIs, Types, and Functions

The script imports `fop_subs` and `generate` from `generator.py`. Template strings are `FN_METADATA_CHILD_GENERIC`, `FN_GENERIC_TEMPLATE`, `FN_DATAFD_TEMPLATE`, `FN_DATALOC_TEMPLATE`, and `FOPS_LINE_TEMPLATE`. The main function `gen_fops()` emits generated C and the `fops` table. The `skipped` list reserves special fops implemented manually: readdir, readdirp, lookup, fsync, stat, open, create, unlink, setattr, and inodelk as a TODO.

## Control Flow

For each input template line, the script detects `#pragma generate`. At that point it prints a generated-code comment, calls `gen_fops`, and prints an end comment; all other template lines are copied through. Within `gen_fops`, fd-based data operations such as writev/readv/ftruncate/zerofill/discard/seek/fstat are emitted to `DATA_CHILD`, truncate is emitted through `build_backend_loc`, and dentry/metadata/xattr operations such as mkdir/link/rename/opendir/readlink/access and xattr fops are emitted to `METADATA_CHILD`.

## State and Persistence Behavior

The script has no persisted state except stdout, which the makefile redirects to `fops.c`. The `done` list controls which generated table entries appear and must include both skipped manual fops and generated fops.

## Dependencies and Integration Points

It relies on Python execution in the build environment and libglusterfs generator metadata for fop argument substitutions. The generated C depends on metadisp child macros, default callbacks, and `build_backend_loc`.

## Risks and Edge Cases

The script uses Python 2 style shebang but Python 3 compatible print calls are not used; it currently uses `print(...)`, but compatibility still depends on the configured interpreter and `generator.py`. The dataloc template's unwind path hard-codes `STACK_UNWIND_STRICT(lookup, ...)`, which is suspicious for generated non-lookup fops and could report the wrong fop signature if build generation enabled more dataloc operations. The `done = skipped` alias mutates the global skipped list if reused in-process.

## Test Signals

Regenerate `fops.c`, inspect routing for each fop class, compile with all generated prototypes, and exercise generated fd, metadata, and dataloc fops. A regression test should verify truncate error unwinds use the correct fop signature if the generator is repaired.
