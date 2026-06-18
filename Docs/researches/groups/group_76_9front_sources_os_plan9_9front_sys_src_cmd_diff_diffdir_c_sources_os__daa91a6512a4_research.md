# Group Research: group_76_9front_sources_os_plan9_9front_sys_src_cmd_diff_diffdir_c_sources_os__daa91a6512a4

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/plan9/9front`, which is included in subset A. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/diff/diffdir.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/diff/diffdir.c

Plan 9 `diff` directory dispatcher. It scans directories, sorts child names, reports entries present only on one side, and routes matching names into recursive directory comparison or regular file comparison.

Key behavior:
- `scandir` opens a directory, reads all `Dir` entries with `dirreadall`, copies names into a null-terminated `char **`, and sorts with `qsort`.
- `diffdir` walks the two sorted name lists, skips `.` and `..`, emits `Only in ...` lines for unmatched entries in normal and `-n` modes, and calls `diff` for common names.
- `diff` stats both inputs through `statfile`, handles stdin/special-file temporary conversion indirectly, compares directories recursively only when `rflag` or top-level, compares regular files with `diffreg`, and handles file-vs-directory by comparing the regular file to a same-basename child path under the directory.

Notable dependencies:
- Shared globals and helpers from `diff.h`/`util.c`: `mode`, `rflag`, `mflag`, `mkpathname`, `statfile`, `emalloc`, `erealloc`.
- Plan 9 `Dir` metadata and `QTDIR`/type checks.

Research notes:
- `scandir` treats an unopenable directory as empty after printing an error, allowing comparison to continue.
- Path building is bounded by `MAXPATHLEN`, with too-long paths fataling in `mkpathname`.
- Directory entries are freed after traversal; `statfile` results are also freed before return.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/diff/diffdir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/diff/diffio.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/diff/diffio.c

Input, verification, and output formatting support for the local `diff` implementation.

Key behavior:
- `readline` reads one bounded logical line from a `Biobuf`, truncating overly long physical lines after `MAXLINELEN-1` bytes and discarding the remainder.
- `readhash` hashes lines for the LCS engine, with `bflag` modes for exact text, coalesced whitespace, or all-whitespace stripping.
- `prepare` opens a file, detects likely binary input by scanning up to 1024 bytes as UTF, then builds the per-line hash array for text files.
- `check` rereads both files to build byte-offset arrays and validates hash-derived matches against actual text, clearing false matches.
- `fetch` prints ranges with prefixes and emits the standard “No newline at end of file” diagnostic when needed.
- `change` emits normal, ed, reverse-ed, and `-n` style hunks immediately, while context/unified/all-context modes accumulate `Change` records.
- `flushchanges` groups nearby accumulated changes and prints context, all-context, or unified diff hunks.

Notable dependencies:
- Plan 9 `Biobuf` I/O.
- Shared `Diff`, `Change`, and global mode flags from `diff.h`.

Research notes:
- The binary heuristic rejects NUL and C1/control-like Unicode range `0x80..0xa0`, then lets `diffreg.c` perform byte comparison.
- `ixold`/`ixnew` offsets are central to both hunk printing and `merge3`.
- The whitespace handling in hashing is intentionally rechecked with squished full lines to avoid hash-only matches.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/diff/diffio.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/diff/diffreg.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/diff/diffreg.c

Regular-file diff engine using the classic Harold Stone longest common subsequence approach over hashed lines.

Key behavior:
- `prune` removes common prefix/suffix ranges from the expensive comparison window.
- `sort`, `equiv`, and `unsort` organize equal line hashes into equivalence classes.
- `stone` builds candidate chains for the longest common subsequence; `unravel` converts the selected chain into match vector `J`.
- `cmp` byte-compares binary files after `prepare` marks input as binary.
- `calcdiff` orchestrates input preparation, pruning, sorting, equivalence construction, LCS computation, match verification, and offset table creation.
- `output` converts `J` gaps into `change` calls, using reverse order for ed-script mode.
- `diffreg` owns a temporary `Diff` instance and `freediff` releases open buffers and generated arrays.

Notable dependencies:
- `prepare`, `check`, `change`, and `flushchanges` from `diffio.c`.
- Memory helpers from `util.c`.

Research notes:
- The implementation overlays storage aggressively, matching the long file comment’s goal of minimizing memory.
- `unsort` uses plain `malloc` without an allocation check, unlike most code in this command.
- Binary differences print `binary files <file1> <file2> differ` and skip text hunk output.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/diff/diffreg.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/diff/merge3.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/diff/merge3.c

Standalone three-way merge command built on the same `Diff` machinery as `diff`.

Key behavior:
- Usage is `merge3 theirs base ours`.
- It computes `base -> theirs` and `base -> ours` diffs with `calcdiff`.
- `collect` converts each diff’s match vector into sorted change ranges.
- `merge` walks both change streams, emits unchanged base ranges, applies non-overlapping changes, and handles overlapping edits.
- Overlapping edits are expanded to aligned old-file ranges, then `same` compares replacement text. Identical replacements are accepted once; differing replacements produce conflict markers.
- Conflict output uses `<<<<<<<<<<`, `========== original`, `========== <ours>`, and `>>>>>>>>>>`.
- Exits with status `"conflict"` on conflicts and rejects binary merges.

Notable dependencies:
- `calcdiff`, `fetch`, `readline`, and `freediff` from the diff implementation.

Research notes:
- The code mutates `Change` ranges while aligning overlaps, so collected changes are not immutable.
- `ln` tracks the next base line to emit; range printing uses existing `fetch` offset arrays.
- The file contains a Unicode identifier `δ`, unusual in otherwise old Plan 9 C style.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/diff/merge3.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/diff/test/diff-t1.l -->
# File Research: sources/os/plan9/9front/sys/src/cmd/diff/test/diff-t1.l

Empty diff regression fixture.

Key behavior:
- Contains no bytes and no lines.
- Useful as one side of tests for empty-file comparisons, additions, deletions, or no-op empty comparisons.

Research notes:
- SHA1 is the empty-file digest `da39a3ee5e6b4b0d3255bfef95601890afd80709`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/diff/test/diff-t1.l -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/diff/test/diff-t10.l -->
# File Research: sources/os/plan9/9front/sys/src/cmd/diff/test/diff-t10.l

Single-line diff regression fixture.

Key behavior:
- Contains the text `a line of text`.
- The stored file is 14 bytes and has no terminating newline, making it useful for testing final-line newline diagnostics.

Research notes:
- This fixture exercises `fetch` behavior for “No newline at end of file”.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/diff/test/diff-t10.l -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/diff/test/diff-t11.l -->
# File Research: sources/os/plan9/9front/sys/src/cmd/diff/test/diff-t11.l

Large text diff fixture containing a Unix manual page for `ed`.

Key behavior:
- Begins with OpenBSD/NetBSD roff comments and `.TH ED 1 "21 May 1993"`.
- Covers `ed` synopsis, description, addressing, regular expressions, commands, diagnostics, and related manual sections.
- Ends with “but any changes to the buffer are lost.”

Research notes:
- The file is 1003 text lines with many roff macros and blank lines.
- It is a realistic long-form prose/manual input for testing large text diffs, context hunks, and line matching.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/diff/test/diff-t11.l -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/diff/test/diff-t12.l -->
# File Research: sources/os/plan9/9front/sys/src/cmd/diff/test/diff-t12.l

Small Makefile-style diff fixture.

Key behavior:
- Starts with `# Test HMAC:`.
- Defines `PROG=	hmactest`, `NOMAN=	yes`, `DPADD`, `LDADD`, `CFLAGS`, and `SRCS`.
- Ends with `.include <bsd.prog.mk>`.

Research notes:
- Includes tabs and make syntax, useful for whitespace-sensitive diff tests.
- Stored bytes indicate a trailing-line/newline edge case relative to visible lines.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/diff/test/diff-t12.l -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/diff/test/diff-t13.l -->
# File Research: sources/os/plan9/9front/sys/src/cmd/diff/test/diff-t13.l

Short sentence fixture for simple line edits.

Key behavior:
- Contains lines such as `A line of text`, `Another line of text`, and `A new line of text`.
- Ends with a single `.` line.
- Repeats similar sentence structure to exercise nearby insert/delete/change detection.

Research notes:
- Useful for small, human-readable hunk output tests.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/diff/test/diff-t13.l -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/diff/test/diff-t14.l -->
# File Research: sources/os/plan9/9front/sys/src/cmd/diff/test/diff-t14.l

Tiny numeric fixture.

Key behavior:
- Contains visible lines `1` and `2`.
- The file is 3 bytes, so the final line has no trailing newline.

Research notes:
- Pairs naturally with `diff-t15.l` for one-line addition/change tests.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/diff/test/diff-t14.l -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/diff/test/diff-t15.l -->
# File Research: sources/os/plan9/9front/sys/src/cmd/diff/test/diff-t15.l

Tiny numeric fixture.

Key behavior:
- Contains visible lines `1`, `2`, and `3`.
- The file is 5 bytes, with the final line lacking a trailing newline.

Research notes:
- Likely paired with `diff-t14.l` to test final-line insertion and no-newline reporting.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/diff/test/diff-t15.l -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/diff/test/diff-t2.l -->
# File Research: sources/os/plan9/9front/sys/src/cmd/diff/test/diff-t2.l

OpenBSD license-text diff fixture.

Key behavior:
- Begins “Below is an example license to be used for new code in OpenBSD,”.
- Contains the standard ISC-style permission and warranty disclaimer block.
- Ends with ` */`.

Research notes:
- `diff-t2.l` and `diff-t4.l` are byte-identical, forming a known-equal pair.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/diff/test/diff-t2.l -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/diff/test/diff-t3.l -->
# File Research: sources/os/plan9/9front/sys/src/cmd/diff/test/diff-t3.l

Empty diff regression fixture.

Key behavior:
- Contains no bytes and no lines.
- Byte-identical to `diff-t1.l`.

Research notes:
- Useful for empty-vs-empty and empty-vs-nonempty regression cases.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/diff/test/diff-t3.l -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/diff/test/diff-t4.l -->
# File Research: sources/os/plan9/9front/sys/src/cmd/diff/test/diff-t4.l

OpenBSD license-text diff fixture.

Key behavior:
- Same 25-line license example content as `diff-t2.l`.
- Contains blank lines plus a C comment license block.

Research notes:
- Byte-identical to `diff-t2.l`, giving the test set a known unchanged text pair.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/diff/test/diff-t4.l -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/diff/test/diff-t5.l -->
# File Research: sources/os/plan9/9front/sys/src/cmd/diff/test/diff-t5.l

Short OpenBSD login/banner-style text fixture.

Key behavior:
- Begins `OpenBSD 3.3-current (GENERIC) #47: Mon Jun 30 11:19:56 CEST 2003`.
- Includes “Welcome to OpenBSD: The proactively secure Unix-like operating system.”
- Contains bug-reporting prose and blank lines.

Research notes:
- Related to `diff-t6.l` and `diff-t7.l`, which contain similar but shorter banner/reporting text.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/diff/test/diff-t5.l -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/diff/test/diff-t6.l -->
# File Research: sources/os/plan9/9front/sys/src/cmd/diff/test/diff-t6.l

Short OpenBSD banner/reporting text fixture.

Key behavior:
- Shares the same opening OpenBSD version line and welcome line as `diff-t5.l`.
- Ends with `known fix for it exists, include that as well.`

Research notes:
- Very close to `diff-t7.l` by visible structure, but has a distinct checksum.
- Useful for testing small edits in similar prose.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/diff/test/diff-t6.l -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/diff/test/diff-t7.l -->
# File Research: sources/os/plan9/9front/sys/src/cmd/diff/test/diff-t7.l

Short OpenBSD banner/reporting text fixture.

Key behavior:
- Shares the same first and last visible lines as `diff-t6.l`.
- Differs by content/spacing enough to have a distinct checksum and byte count.

Research notes:
- Useful as a near-match fixture for whitespace or small textual edits.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/diff/test/diff-t7.l -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/diff/test/diff-t8.l -->
# File Research: sources/os/plan9/9front/sys/src/cmd/diff/test/diff-t8.l

Large C-source diff fixture based on NetBSD `kern_malloc.c`.

Key behavior:
- Begins with `/*	$NetBSD: kern_malloc.c...`.
- Contains kernel memory allocator code, comments, copyright text, and C function bodies.
- Ends with a closing brace.

Research notes:
- 392-line realistic C source fixture for testing code diffs, repeated braces, comments, and long common subsequences.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/diff/test/diff-t8.l -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/diff/test/diff-t9.l -->
# File Research: sources/os/plan9/9front/sys/src/cmd/diff/test/diff-t9.l

Very large C-source diff fixture based on NetBSD `vfs_syscalls.c`.

Key behavior:
- Begins with `/*	$NetBSD: vfs_syscalls.c...`.
- Contains VFS syscall implementations and helper routines, including open/close/read/write/lseek/access/stat/readlink/chmod/chown/rename/mkdir/rmdir/getdirentries/umask/revoke and vnode/file-descriptor handling.
- Ends with a closing brace.

Research notes:
- 2045-line realistic filesystem-heavy C fixture, directly relevant to broad filesystem research even though it lives under diff tests.
- Exercises diff behavior on long source files with many repeated syscall patterns and comments.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/diff/test/diff-t9.l -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/diff/test/merge-t1.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/diff/test/merge-t1.c

Merge regression base/side fixture.

Key behavior:
- Contains numeric lines `1` through `10`.
- Byte-identical to several other baseline merge `.c` fixtures and to `merge-t1.l`.

Research notes:
- Serves as a simple unchanged sequence for three-way merge tests.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/diff/test/merge-t1.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/diff/test/merge-t1.l -->
# File Research: sources/os/plan9/9front/sys/src/cmd/diff/test/merge-t1.l

Merge regression expected/output fixture.

Key behavior:
- Contains numeric lines `1` through `10`.
- Byte-identical to `merge-t1.c`.

Research notes:
- Represents an unchanged merge result for the simplest case.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/diff/test/merge-t1.l -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/diff/test/merge-t10.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/diff/test/merge-t10.c

Merge regression fixture.

Key behavior:
- Contains numeric lines `1` through `10`.
- Same baseline content as `merge-t1.c`.

Research notes:
- Paired with a `.l` side/result fixture that changes line `5` to `y`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/diff/test/merge-t10.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/diff/test/merge-t10.l -->
# File Research: sources/os/plan9/9front/sys/src/cmd/diff/test/merge-t10.l

Merge regression fixture with one replacement.

Key behavior:
- Contains numeric sequence `1` through `10` except line `5` is `y`.
- Tests a simple non-overlapping or single-side line replacement.

Research notes:
- Related to `merge-t3.l`, which has identical content.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/diff/test/merge-t10.l -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/diff/test/merge-t11.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/diff/test/merge-t11.c

Merge regression baseline fixture.

Key behavior:
- Contains numeric lines `1` through `10`.
- Same baseline content as `merge-t1.c`.

Research notes:
- Paired with `merge-t11.l`, which adds boundary lines and changes the middle.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/diff/test/merge-t11.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/diff/test/merge-t11.l -->
# File Research: sources/os/plan9/9front/sys/src/cmd/diff/test/merge-t11.l

Merge regression fixture with boundary insertions and middle replacement.

Key behavior:
- Adds `A` before `1` and `Z` after `10`.
- Replaces line `5` with `y`.

Research notes:
- Exercises merge handling at file start, file end, and an interior change in one fixture.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/diff/test/merge-t11.l -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/diff/test/merge-t12.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/diff/test/merge-t12.c

Merge regression baseline fixture.

Key behavior:
- Contains numeric lines `1` through `10`.
- Same baseline content as `merge-t1.c`.

Research notes:
- Paired with `merge-t12.l`, which deletes line `9`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/diff/test/merge-t12.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/diff/test/merge-t12.l -->
# File Research: sources/os/plan9/9front/sys/src/cmd/diff/test/merge-t12.l

Merge regression fixture with a deletion.

Key behavior:
- Contains `1` through `8`, then `10`.
- Omits line `9`.

Research notes:
- Tests simple deletion propagation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/diff/test/merge-t12.l -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/diff/test/merge-t13.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/diff/test/merge-t13.c

Merge regression fixture with sparse/marker content.

Key behavior:
- Starts with `1`, then several blank lines, then `10`.
- Includes marker-like lines `###1` and `###0`.
- Contains a second block with `1`, `2`, `3`, `4`, `y`, `6`, `9`, `ZZZZZZZZ`, blank line, `9`, `B`.

Research notes:
- Designed to stress merge chunk alignment, blank-line handling, and marker-like data that must not be confused with conflict markers.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/diff/test/merge-t13.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/diff/test/merge-t13.l -->
# File Research: sources/os/plan9/9front/sys/src/cmd/diff/test/merge-t13.l

Merge regression fixture with blank ranges and marker-like lines.

Key behavior:
- Starts with `1` through `4`, then `x6`, `7`, `8`, `9`.
- Contains a long run of blank lines.
- Includes `##3`, then `4` through `10`.

Research notes:
- Complements `merge-t13.c` for complex overlap/alignment tests.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/diff/test/merge-t13.l -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/diff/test/merge-t2.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/diff/test/merge-t2.c

Merge regression fixture with deletions.

Key behavior:
- Contains `1`, `2`, `4`, `5`, `6`, `8`, `9`, `10`.
- Omits `3` and `7` relative to the 1-10 baseline.

Research notes:
- Paired with `merge-t2.l`, which restores/includes `3` but still omits `7`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/diff/test/merge-t2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/diff/test/merge-t2.l -->
# File Research: sources/os/plan9/9front/sys/src/cmd/diff/test/merge-t2.l

Merge regression fixture with one deletion.

Key behavior:
- Contains `1` through `6`, then `8`, `9`, `10`.
- Omits line `7`.

Research notes:
- Useful for deletion-vs-deletion or deletion-vs-context merge cases.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/diff/test/merge-t2.l -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/diff/test/merge-t3.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/diff/test/merge-t3.c

Merge regression baseline fixture.

Key behavior:
- Contains numeric lines `1` through `10`.

Research notes:
- Paired with `merge-t3.l`, which changes line `5` to `y`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/diff/test/merge-t3.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/diff/test/merge-t3.l -->
# File Research: sources/os/plan9/9front/sys/src/cmd/diff/test/merge-t3.l

Merge regression fixture with one middle replacement.

Key behavior:
- Contains `1`, `2`, `3`, `4`, `y`, `6`, `7`, `8`, `9`, `10`.

Research notes:
- Byte-identical to `merge-t10.l`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/diff/test/merge-t3.l -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/diff/test/merge-t4.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/diff/test/merge-t4.c

Merge regression baseline fixture.

Key behavior:
- Contains numeric lines `1` through `10`.

Research notes:
- Paired with `merge-t4.l`, which changes line `5` to `x`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/diff/test/merge-t4.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/diff/test/merge-t4.l -->
# File Research: sources/os/plan9/9front/sys/src/cmd/diff/test/merge-t4.l

Merge regression fixture with one middle replacement.

Key behavior:
- Contains `1`, `2`, `3`, `4`, `x`, `6`, `7`, `8`, `9`, `10`.

Research notes:
- Contrasts with the `y` replacement fixtures to test conflicting edits to the same line.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/diff/test/merge-t4.l -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/diff/test/merge-t5.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/diff/test/merge-t5.c

Merge regression baseline fixture.

Key behavior:
- Contains numeric lines `1` through `10`.

Research notes:
- Paired with `merge-t5.l`, which inserts multiple lines and changes line `5`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/diff/test/merge-t5.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/diff/test/merge-t5.l -->
# File Research: sources/os/plan9/9front/sys/src/cmd/diff/test/merge-t5.l

Merge regression fixture with insertion plus replacement.

Key behavior:
- Inserts `a`, `b`, `c` after `1`.
- Replaces baseline line `5` with `x`.
- Keeps remaining numeric context through `10`.

Research notes:
- Tests multi-line insertion close to a later replacement.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/diff/test/merge-t5.l -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/diff/test/merge-t6.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/diff/test/merge-t6.c

Merge regression baseline fixture.

Key behavior:
- Contains numeric lines `1` through `10`.

Research notes:
- Paired with `merge-t6.l`, which appends `11`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/diff/test/merge-t6.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/diff/test/merge-t6.l -->
# File Research: sources/os/plan9/9front/sys/src/cmd/diff/test/merge-t6.l

Merge regression fixture with tail insertion.

Key behavior:
- Contains `1` through `10`, followed by `11`.

Research notes:
- Tests append-at-EOF merge behavior.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/diff/test/merge-t6.l -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/diff/test/merge-t7.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/diff/test/merge-t7.c

Merge regression baseline fixture.

Key behavior:
- Contains numeric lines `1` through `10`.

Research notes:
- Paired with `merge-t7.l`, which adds both head and tail lines.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/diff/test/merge-t7.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/diff/test/merge-t7.l -->
# File Research: sources/os/plan9/9front/sys/src/cmd/diff/test/merge-t7.l

Merge regression fixture with boundary insertions.

Key behavior:
- Adds `0` before `1`.
- Contains `1` through `10`.
- Adds `11` after `10`.

Research notes:
- Tests simultaneous start/end insertions.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/diff/test/merge-t7.l -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/diff/test/merge-t8.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/diff/test/merge-t8.c

Tiny merge fixture.

Key behavior:
- Contains one line: `foo`.

Research notes:
- Paired with an empty `.l` fixture to test full deletion or empty-side merge behavior.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/diff/test/merge-t8.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/diff/test/merge-t8.l -->
# File Research: sources/os/plan9/9front/sys/src/cmd/diff/test/merge-t8.l

Empty merge fixture.

Key behavior:
- Contains no bytes and no lines.

Research notes:
- Complements `merge-t8.c` for empty-vs-nonempty merge cases.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/diff/test/merge-t8.l -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/diff/test/merge-t9.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/diff/test/merge-t9.c

Tiny merge fixture.

Key behavior:
- Contains lines `1` and `2`.

Research notes:
- Paired with `merge-t9.l`, which changes the first line to `a`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/diff/test/merge-t9.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/diff/test/merge-t9.l -->
# File Research: sources/os/plan9/9front/sys/src/cmd/diff/test/merge-t9.l

Tiny merge fixture with one replacement.

Key behavior:
- Contains lines `a` and `2`.

Research notes:
- Tests a one-line replacement at file start.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/diff/test/merge-t9.l -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/diff/util.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/diff/util.c

Shared utility and global-state file for the Plan 9 `diff` command.

Key behavior:
- Defines global `stdout`, mode flags, recursion/multiple-file flags, and `anychange`.
- Provides fatal allocation wrappers `emalloc` and `erealloc`.
- `mkpathname` joins directory and child names with length enforcement.
- `mktmpfile` copies stdin or special-file contents to an ORCLOSE temporary file for stable diffing.
- `statfile` returns regular files/directories directly, maps `-` to stdin temp storage, and copies non-regular/non-directory readable files to a temp file.

Notable dependencies:
- Plan 9 temp naming via `mktemp`.
- Plan 9 `Dir` metadata and `ORCLOSE`.

Research notes:
- `mktmpfile` intentionally leaks the created fd so the temporary remains for the program’s lifetime and is removed at exit.
- Only two temp paths are statically defined, matching the two-input model.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/diff/util.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/disk/9660/boot.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/disk/9660/boot.c

El Torito boot support for the ISO 9660 image writer.

Key behavior:
- `Cputbootvol` writes the boot volume descriptor with `EL TORITO SPECIFICATION` and records where the boot catalog block pointer must later be patched.
- `Cupdatebootvol` patches the boot catalog block number into the boot volume descriptor.
- `Cputbootcat` writes the validation entry and records where boot image entries will be patched.
- `Caddbootentry` writes a bootable catalog entry, selecting 1.44MB, 2.88MB, or no-emulation mode and setting load-sector count.
- `Cupdatebootcat` finds BIOS and optional EFI boot image directory entries, writes catalog entries, and emits an EFI section header when both BIOS and EFI images are present.

Notable dependencies:
- Directory lookup via `walkdirec`.
- ISO byte emitters from `cdrdwr.c`.

Research notes:
- Warns when boot images are not encountered or when no-emulation BIOS images exceed the 2KB initial load count.
- Supports both traditional floppy-emulation and no-emulation boot images.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/disk/9660/boot.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/disk/9660/cdrdwr.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/disk/9660/cdrdwr.c

Core ISO image open/create, descriptor parsing, endian conversion, and buffered read/write primitives.

Key behavior:
- `createcd` creates a new image, writes initial empty sectors, primary descriptor, optional boot/Joliet/dump structures, descriptor terminator, and initializes `nextblock`.
- `opencd` opens an existing block-aligned image, parses descriptors, detects Plan 9/Rock Ridge/conform/boot/Joliet/dump features, and validates the system identifier.
- `big` and `little` decode multi-byte integers.
- `Creadblock` performs block-addressed reads after flushing pending writes.
- `parsedir` converts on-disc directory records into `Direc`, including Plan 9 system-use fields when applicable.
- `setroot`, `setvolsize`, and `setpathtable` patch descriptor fields after layout is known.
- `Cput*`, `Cread`, `Cwseek`, `Crseek`, and related helpers abstract byte, endian, string, UTF-16-ish rune, block-padding, and date emission.

Notable dependencies:
- `Cputisopvd`, `Cputjolietsvd`, `Cputendvd`, dump and boot helpers.
- Plan 9 `Biobuf` for separate read/write streams on the same image.

Research notes:
- The implementation maintains separate read and write buffers and carefully flushes the opposite side when switching directions.
- `parsedir` has a comment noting Rock Ridge parsing is not implemented.
- `Cputc` contains a suspicious leftover debug conditional around offset `0x9962` and `abort()` for byte values >=256.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/disk/9660/cdrdwr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/disk/9660/conform.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/disk/9660/conform.c

Name-conformance map support for ISO 9660-safe filenames.

Key behavior:
- Maintains a sorted `Conform` map of bad original names to generated conforming names.
- `conform` interns the source name, reuses any existing translation, or assigns `Dnnnnnn`/`Fnnnnnn` depending on directory/file status.
- `addtx` inserts translations by atom pointer order and warns on duplicates.
- `wrconform` writes new `_conform.map` entries sorted by generated name, then restores map ordering by original atom.

Notable dependencies:
- Global `map` from `dump9660.c`.
- `atom`, `emalloc`, `erealloc`, `Cwrite`, and `Cpadblock`.

Research notes:
- Pointer ordering is safe only because names are atomized and retained for process lifetime.
- The older `_conform.map` mechanism is still used for dump/update compatibility even though Joliet covers many long-name cases.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/disk/9660/conform.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/disk/9660/direc.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/disk/9660/direc.c

In-memory ISO directory tree construction and manipulation.

Key behavior:
- `mkdirec` converts an `XDir` into a `Direc`.
- `walkdirec` follows slash-separated paths through sorted child arrays.
- `adddirec` inserts a file or directory into a sorted child list, requiring intermediate directories to already exist.
- `copydirec` deep-copies directory subtrees.
- `checknames` marks non-conforming names and `_conform.map`.
- `convertnames` assigns each entry’s `confname`, using generated conform names for `Dbadname` entries.
- `dsort` recursively sorts the tree by ISO or Joliet comparison function.

Notable dependencies:
- Name validation/comparison from `ichar.c` and `jchar.c`.
- Conformance map from `conform.c`.

Research notes:
- `adddirec` mutates the path string temporarily when splitting parent path from basename.
- After `dsort`, callers must not use `adddirec` on that tree because the sort order may no longer match UTF-name insertion order.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/disk/9660/direc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/disk/9660/dump.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/disk/9660/dump.c

Incremental dump-CD metadata and content-deduplication support.

Key behavior:
- Computes MD5 digests of existing CD file extents and indexes them by both digest and block number.
- `dumpcd` walks existing dump day directories and records file content for deduplication.
- `lookupmd5` and `insertmd5` support reusing existing extents when new input content matches old content.
- `readkids` parses directory blocks into child `Direc` arrays.
- `adddumpdir` creates year/day dump directory names based on local time, adding numeric suffixes for duplicates.
- `Cputdumpblock` writes a special `plan 9 dump cd` marker block.
- `hasdump`, `readdumpdirs`, and `readdumpconform` walk the linked dump-block chain and reconstruct dump roots plus conform-name mappings.

Notable dependencies:
- MD5 from `libsec`.
- Directory parsing and block I/O from `cdrdwr.c`.

Research notes:
- The dump block chain is the commit log for append/update operations; the old null header is rewritten last to commit changes.
- Duplicate content on CD is warned about but can be used for extent reuse.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/disk/9660/dump.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/disk/9660/dump9660.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/disk/9660/dump9660.c

Main program for `disk/dump9660` and `disk/mk9660`, building or updating ISO 9660 dump images from proto files.

Key behavior:
- Parses options for dump vs mk9660 mode, Plan 9/Rock Ridge/Joliet/conform flags, boot images, source/proto roots, max size, offset alignment, timestamps, and verbosity.
- Creates or opens a `Cdimg`, builds the new ISO tree from a proto file via `rdproto`, and converts host `Dir` to `XDir`.
- For dump mode, reconstructs existing dump trees and `_conform.map`, creates a new dated dump directory, and builds a dedup index.
- Writes file data first so directory entries get final blocks/lengths.
- Builds ISO and optional Joliet trees, validates/converts names, sorts them, writes directories, writes conform maps, patches roots/volume sizes, writes path tables, and commits dump blocks.
- Handles max-size abort by restoring the old dump tree and exiting non-zero.
- `addprotofile` inserts proto-enumerated files, with optional colon-to-space name conversion.

Notable dependencies:
- Almost every 9660 module: tree, write, dump, conform, boot, path table, char conversion, and host adapters.

Research notes:
- This is the top-level orchestrator for both fresh images and incremental dump CDs.
- The commit protocol intentionally leaves a reconstructable null dump block at the end for the next append.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/disk/9660/dump9660.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/disk/9660/ichar.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/disk/9660/ichar.c

ISO 9660 character conversion, validation, sorting, and primary volume descriptor writing.

Key behavior:
- `isostring` converts fixed-width ISO strings to lowercase atomized Plan 9 strings, trimming trailing spaces.
- `isisofrog` and `isbadiso9660` enforce lowercase/digit/underscore plus 8.3-style basename/extension constraints in the in-memory naming model.
- `isocmp` implements ISO-style name sorting by basename then extension.
- `mkisostring` uppercases in-memory names and pads fixed descriptor fields.
- `Cputisopvd` writes the primary volume descriptor with system id, volume id, root directory placeholder, volume metadata, dates, and block padding.

Notable dependencies:
- Directory entry writer `Cputisodir`.
- Global `now`.

Research notes:
- The code stores ISO names lowercase internally and uppercases when writing.
- Names matching generated conform patterns like `Ddddddd`/`Fdddddd` are treated as bad to avoid collisions.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/disk/9660/ichar.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/disk/9660/iso9660.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/disk/9660/iso9660.h

Shared data model and prototypes for the ISO 9660 reader/writer tools.

Key contents:
- Defines host-neutral `XDir`, in-memory `Direc`, volume descriptor `Voldesc`, image state `Cdimg`, command-line `Cdinfo`, conformance maps, dump indexes, dump roots, and on-disc `Cvoldesc`, `Cdir`, and `Cpath`.
- Defines feature flags: Joliet, Plan 9, conform names, Rock Ridge, new image, dump CD, bootable, and no-emulation boot.
- Defines Rock Ridge/SUSP constants and directory-entry dot/root selector constants.
- Declares all cross-module functions for boot, I/O, conform maps, directories, dump support, ISO/Joliet char handling, path tables, utilities, host adapters, rune helpers, system-use records, and image writing.

Research notes:
- This header is the architectural center of the `disk/9660` subsystem.
- `Cdimg` stores both physical layout state (`nextblock`, descriptor blocks, boot/dump pointers) and parsed logical volume trees.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/disk/9660/iso9660.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/disk/9660/jchar.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/disk/9660/jchar.c

Joliet string conversion, validation, sorting, and secondary volume descriptor writing.

Key behavior:
- `jolietstring` converts big-endian two-byte UCS-style names into UTF strings and interns them.
- `isbadjoliet` rejects names longer than 64 runes and characters forbidden by Joliet.
- `jolietcmp` compares basename and extension as rune sequences.
- `Cputjolietsvd` writes the Joliet secondary descriptor, including UCS-2 Level 2 escape sequence `%/C`, metadata strings, root placeholder, and dates.

Notable dependencies:
- Rune helpers from `rune.c`.
- Directory entry writer `Cputjolietdir`.

Research notes:
- The comparison mirrors ISO sorting but on encoded runes.
- Fixed-size local rune arrays are marked with a `/*BUG*/` comment for long names.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/disk/9660/jchar.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/disk/9660/path.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/disk/9660/path.c

ISO 9660 path table generation and descriptor patching.

Key behavior:
- Writes little-endian and big-endian path tables at the end of the image after directories are finalized.
- Uses the just-written path table as a breadth-first queue while reading directory records from the image.
- Tracks directory lengths separately because path table records do not store them.
- `writepathtablepair` writes both endian variants and patches descriptor path size and locations.
- `writepathtables` applies this to the primary descriptor and optional Joliet descriptor.

Notable dependencies:
- `Creadblock`, `Crdpath`, `writepath`, `setpathtable`, and directory record structures.

Research notes:
- The file includes a warning not to pad path table entries across block boundaries, based on observed Windows behavior.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/disk/9660/path.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/disk/9660/plan9.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/disk/9660/plan9.c

Plan 9 host adapter for ISO image building.

Key behavior:
- `dirtoxdir` converts Plan 9 `Dir` metadata to `XDir`, atomizing name/uid/gid, copying mode, atime, mtime, length, and using numeric uid/gid zero.
- `fdtruncate` is a no-op stub on Plan 9.

Research notes:
- Contrasts with `unix.c`, which uses POSIX `ftruncate` and passwd/group lookups.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/disk/9660/plan9.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/disk/9660/rune.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/disk/9660/rune.c

Small rune-string helper library for Joliet support.

Key behavior:
- `strtorune` converts UTF-8 `char *` to a null-terminated `Rune *`.
- `runechr` finds a rune in a rune string.
- `runecmp` lexicographically compares rune strings.

Research notes:
- Callers provide output buffers; there is no bounds checking in this helper.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/disk/9660/rune.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/disk/9660/sysuse.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/disk/9660/sysuse.c

Rock Ridge/SUSP system-use record writer for ISO directory entries.

Key behavior:
- Computes and writes SUSP/RRIP records including `SP`, `ER`, `RR`, `PX`, `NM`, `SL`, `TF`, and continuation `CE`.
- `Cputsysuse` first sizes and then writes records, managing inline directory-entry space and continuation blocklets.
- Long names and symlink components are split across NM/SL records as needed.
- Continuation areas are block-aligned and linked with CE records whose length fields are patched after writing.
- POSIX mode, nlink, uid/gid, and timestamps are derived from `Direc`.

Notable dependencies:
- `Cputn`, `Cputdate`, `Cwoffset`, `Cwseek`, `chat`.
- Plan 9 mode bits and optional `CHLINK` symlink flag.

Research notes:
- The implementation explicitly calls the format awkward and is full of defensive asserts around continuation sizing.
- `mode` asserts only directory or regular-file support despite defining symlink constants, which may conflict with `CHLINK` symlink handling.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/disk/9660/sysuse.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/disk/9660/uid.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/disk/9660/uid.c

Incomplete/sketch file for detecting user database format.

Key behavior:
- Contains comments describing `/adm/users` and `/etc/{passwd,group}` field formats.
- Defines `isnumber`.
- Contains a non-C pseudocode-like `sniff(Biobuf *b)` body with placeholders such as “read first line of file into p;” and references to `_plan9`/`_unix`.

Research notes:
- This file does not appear to be production-compilable as written.
- It may be a dormant design note or unfinished utility for uid/gid mapping.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/disk/9660/uid.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/disk/9660/unix.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/disk/9660/unix.c

Unix host adapter for ISO image building.

Key behavior:
- `dirtoxdir` converts `Dir` to `XDir`, resolves numeric uid/gid via `getpwnam`/`getgrnam`, and preserves symlink targets when `CHLINK` is set.
- `fdtruncate` calls POSIX `ftruncate`.
- `numericuid` and `numericgid` warn once if user/group lookup fails and return zero.

Notable dependencies:
- `<pwd.h>`, `<grp.h>`, and Plan 9 compatibility headers.

Research notes:
- Provides host-specific behavior needed when building the tools outside native Plan 9.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/disk/9660/unix.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/disk/9660/util.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/disk/9660/util.c

Utility support for the ISO 9660 tools.

Key behavior:
- Implements an atom table for interned strings using 1024 hash buckets.
- Provides zeroing `emalloc`, fatal `erealloc`, uppercase-copy helper `struprcpy`, and conditional diagnostic printer `chat`.

Research notes:
- Atomized strings enable pointer comparisons in conform-map code.
- `erealloc` loses the old pointer in the error message expression after `realloc` assignment, but fatal exit makes recovery irrelevant.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/disk/9660/util.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/disk/9660/write.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/disk/9660/write.c

File data, directory records, dump directories, and descriptor terminator writer for ISO images.

Key behavior:
- `writefiles` recursively writes non-directory file contents, computes MD5 while copying, and reuses existing extents when `lookupmd5` finds duplicate content.
- `writedirs` writes directory trees from leaves upward, first sizing entries then writing, padding blocks, and patching `.`/`..` records.
- `writedumpdirs` writes the special dump hierarchy while preserving already-written day roots.
- `Cputplan9` emits Plan 9 system-use fields for bad original name, uid, gid, and mode.
- `genputdir` writes ISO/Joliet directory entries, including file flags, extent, length, date, identifier, and optional Plan 9 or Rock Ridge system-use data.
- `Cputisodir` and `Cputjolietdir` specialize `genputdir`.
- `Cputendvd` writes the volume descriptor set terminator.

Notable dependencies:
- MD5 from `libsec`.
- `Cputsysuse`, `Cputrscvt`, block I/O helpers, and dump dedup structures.

Research notes:
- Zero-length files get block 0; non-empty regular files assert block >= 18 when directory records are written.
- File copy updates length if the source changes during read and warns about it.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/disk/9660/write.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/disk/cryptsetup.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/disk/cryptsetup.c

Small encrypted-disk setup/open helper for Plan 9’s `fs` crypt device.

Key behavior:
- `setupkey` derives an AES key from a password and salt using PBKDF2-HMAC-SHA1 with 9999 iterations, then initializes AES-CBC.
- `cformat` prompts for password confirmation, generates random master/slot data, encrypts the master key into slot 0, writes a 64KB randomized header, and stores a validation pad encrypted under the master key.
- `copen` reads the header, prompts/retries password, decrypts slot 0, validates the pad, and prints or installs a `/dev/fs/ctl` `crypt` command with the decrypted master key.
- Modes are `-f` format, `-o` print open command, and `-i` install/open through `/dev/fs/ctl`.

Notable dependencies:
- `libsec` AES/PBKDF2/HMAC/SHA1 and Plan 9 `readcons`.
- `/dev/fs/ctl` control protocol.

Research notes:
- Password buffers are wiped before free.
- Only slot 0 is actually used despite storage for 8 slots.
- This is a low-level destructive formatter when run with `-f`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/disk/cryptsetup.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/disk/exsort.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/disk/exsort.c

Utility for sorting and reporting block-number cache files.

Key behavior:
- Reads a file of `ulong` values, defaulting to `/adm/cache`.
- Counts low/high marker bits to infer endianness; if high bits dominate, byte-swaps values.
- Sorts block numbers and reports counts per `Wormsize` disk-sized range for 100 ranges.
- With `-w`, writes the sorted data back, swapping back if needed.

Research notes:
- Appears tailored for historical WORM/cache administration.
- Reads the full file into memory.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/disk/exsort.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/disk/format.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/disk/format.c

Disk/floppy/file FAT formatter and boot-sector writer.

Key behavior:
- Supports floppy geometries, hard disks, and file-backed images.
- Can write a Plan 9 boot sector/program, initialize FAT12/FAT16/FAT32 structures, and add root-directory files.
- Parses options for boot block, cluster size, label, reserved sectors, disk type, file creation, DOS/FAT mode, verbosity, and safety override.
- `sanitycheck` guards against formatting whole disks or clobbering Plan 9 partition tables without explicit override.
- `dosfs` computes FAT size, root directory size, cluster count, FAT type, BIOS parameter block fields, FAT info sector, FAT tables, root directory, and file data.
- Long filenames are emitted through VFAT long-name slots with generated 8.3 aliases.
- `clustalloc` writes FAT12/16/32 chains.

Notable dependencies:
- Plan 9 `disk.h` and `opendisk`.
- Embedded x86 boot stub that prints a not-bootable message.

Research notes:
- Performs a dry run before commit to catch errors.
- The code has duplicated `fatsecs` global declaration in the file.
- Adds files only to the root directory; it is not a general recursive FAT builder.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/disk/format.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/disk/mbr.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/disk/mbr.c

PC master boot record installer.

Key behavior:
- Reads the existing first sector, replaces boot code from either an embedded default MBR or `-m mbrfile`, preserves the partition table unless `-9` is requested, and writes the MBR signature.
- `-9` clears the partition table and creates one active Plan 9 partition of type `0x39` starting after the first track.
- Handles CHS encoding with saturation at cylinder 1023 and writes little-endian LBA/size fields.
- Refuses to install on floppy disks.

Notable dependencies:
- Plan 9 `disk.h`/`opendisk`.

Research notes:
- For non-512-byte media, it still operates on 512-byte MBR content and relies on the device layer for safe sector handling.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/disk/mbr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/disk/mkext.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/disk/mkext.c

Extractor/listing tool for `mkfs -a` archive streams.

Key behavior:
- Reads archive headers from stdin: quoted name, mode, uid, gid, mtime, byte count.
- Stops on `end of archive`.
- Can extract files/directories, list headers with `-h`, preserve uid/gid with `-u`, preserve mtime with `-T`, set a destination prefix with `-d`, and filter selected paths.
- Creates needed parent directories for selected extraction.
- Verifies uid/gid/time preservation after writing when requested.

Notable dependencies:
- Plan 9 quoted string parsing and `Biobuf`.

Research notes:
- Archive file data follows each header immediately; skipped entries are consumed with `seekpast`.
- `error` exits with status `0`, matching some old Plan 9 tool conventions but surprising for fatal errors.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/disk/mkext.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/disk/mkfs.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/disk/mkfs.c

Proto-file driven filesystem/archive population tool.

Key behavior:
- Reads one or more proto files through `rdproto`.
- In filesystem mode, copies files from a source root to a destination root, creates directories, updates modes/times/groups, and optionally uid/gid.
- In archive mode (`-a`), emits `mkext`-compatible headers plus file contents to stdout.
- Supports ream/force behavior, mode-only updates, verbose logging, source/destination prefixes, listing modes `-x`/`-o`, and configurable copy buffer.
- File copying uses a temp sibling `__mkfstmp`, sparse zero skipping, and final `dirfwstat` rename semantics.

Notable dependencies:
- `libproto` via `rdproto`, Plan 9 `Dir` metadata, `Biobuf`.

Research notes:
- `uptodate` skips copying existing destination files whose mtime is newer unless reaming/archive mode.
- Archive mode and `mkext.c` are paired formats.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/disk/mkfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/disk/partfs.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/disk/partfs.c

9P file server that exposes byte ranges of an underlying disk image/file as devsd-style partitions.

Key behavior:
- Serves a root containing an sd-like directory, `ctl`, and partition files.
- Initializes a default `data` partition over the entire underlying file.
- `ctl` reports inquiry, geometry, and partitions; writes support `part`, `delpart`, `inquiry`, and `geometry`, passing unknown commands through to an underlying ctl file when serving a device directory.
- Partition reads/writes translate request offsets through partition sector offsets and clamp to partition length.
- Qid versions invalidate stale fids after partition recreation.
- Supports read-only open of the underlying image with `-r`, custom sd name, mountpoint, and service name.

Notable dependencies:
- Plan 9 thread/9p libraries.
- Underlying file or `<dir>/data` plus optional `<dir>/ctl`.

Research notes:
- No explicit locking protects global partition state; typical 9P service serialization may be relied on.
- `evommem` is a wrapper around `memmove` with reversed argument naming and is unused in the read file.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/disk/partfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/disk/prep/calc.y -->
# File Research: sources/os/plan9/9front/sys/src/cmd/disk/prep/calc.y

Yacc grammar and evaluator for partition-size expressions in `disk/prep`.

Key behavior:
- Parses numbers, `.`, `$`, parentheses, addition, subtraction, multiplication, division, unary minus, and postfix `%`.
- Numeric suffixes `k`, `m`, `g`, `t` scale byte quantities and convert them to sectors using `unit`.
- `.` evaluates to current position, `$` to end, and `%` evaluates a percentage of total size.
- `parseexpr` sets parser context, runs `yyparse`, evaluates the expression tree, and returns an error string or nil.

Notable dependencies:
- `disk.h`, `edit.h`, and `emalloc` from the surrounding prep program.

Research notes:
- Uses `setjmp`/`longjmp` for parse/evaluation errors such as division by zero.
- The `#ifdef TEST` main appears stale: its call to `parseexpr` does not match the current parameter list.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/disk/prep/calc.y -->