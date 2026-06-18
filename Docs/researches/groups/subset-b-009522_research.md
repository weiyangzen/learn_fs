# Group Research: subset-b-009522

This grouped report covers the requested unionmount test scripts and xfstests-bld build/compatibility sources. Each file section is delimited for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/rename-mass-3.py -->
# sources/test-tools/unionmount-testsuite/tests/rename-mass-3.py

Purpose: exercises repeated circular renames of existing lower regular files and later removes the resulting names. It stresses overlay/union rename bookkeeping when one name in a fixed ring is intentionally absent.

Important APIs and functions: defines `ring_size`, `iter_count`, `subtest_1(ctx)`, and `subtest_2(ctx)`. It uses `ctx.reg_file()`, `ctx.rename()`, and `ctx.unlink()` with expected `ENOENT` from `errno`.

Control flow: `subtest_1` derives a base path from a regular-file fixture prefix, then repeatedly renames `next_gap` into `gap`. `subtest_2` recomputes the final missing slot and unlinks all names, expecting `ENOENT` only for the gap.

State and persistence: persistent filesystem state is the renamed dentry sequence. No module globals mutate during execution except loop-local `gap`; correctness depends on each rename moving exactly one file.

Dependencies and integration: run by the unionmount test harness, which supplies fixture numbering and validates expected errno behavior. The test integrates with overlayfs rename/copy-up behavior through `ctx.rename`.

Risks: off-by-one ring math can mask a missing entry or unlink the wrong path. The test assumes fixture files with matching numeric suffixes exist before it runs.

Test signals: success is the absence of unexpected rename/unlink errors and exactly one `ENOENT` at cleanup.
<!-- END_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/rename-mass-3.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/rename-mass-4.py -->
# sources/test-tools/unionmount-testsuite/tests/rename-mass-4.py

Purpose: verifies mass circular renames of newly created regular files. Unlike `rename-mass-3.py`, it creates the ring entries through the union mount before performing rename churn.

Important APIs and functions: exports `subtest_1(ctx)` and `subtest_2(ctx)`. It uses `ctx.no_file()`, `ctx.open_file(..., wo=1, crt=1, write=...)`, `ctx.rename()`, and `ctx.unlink()`.

Control flow: `subtest_1` creates all ring names with unique payloads, then rotates the gap backward through `iter_count`. `subtest_2` computes the missing slot after rotation and removes all surviving names.

State and persistence: created files live in the writable layer; after rotation their path identities change but data should remain bound to the moved inodes. Cleanup verifies dentry removal semantics.

Dependencies and integration: depends on harness path factories and open/rename wrappers. It targets union filesystem upper-layer rename behavior rather than lower copy-up behavior.

Risks: the test does not read file contents after the mass rename, so it catches namespace breakage and cleanup failures more directly than payload transposition.

Test signals: all creates and renames must succeed; cleanup must see one expected absent slot and no unexpected survivors.
<!-- END_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/rename-mass-4.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/rename-mass-5.py -->
# sources/test-tools/unionmount-testsuite/tests/rename-mass-5.py

Purpose: stresses circular renames across hardlinked file names, mixing a lower regular-file base and newly created hardlinks. It checks link-count/dentry consistency under repeated rename.

Important APIs and functions: defines `subtest_1(ctx)` to create hardlinks with `ctx.link()` and perform two rename cycles, and `subtest_2(ctx)` to unlink both hardlink and source namespaces.

Control flow: first it hardlinks `src_base + number` to `base + number`, then rotates the hardlink names backward. It then rotates source names forward. Cleanup calculates separate expected gaps for the two rings.

State and persistence: the relevant persistent state is shared inode identity across renamed hardlink names. The file keeps no local persistent state, so correctness is inferred from syscall outcomes.

Dependencies and integration: depends on preexisting regular fixtures, harness hardlink support, and overlayfs behavior for linked lower files and copied-up hardlinks.

Risks: cleanup loops use `ring_size + 1`, while rename loops rotate only modulo `ring_size`; this intentionally includes an extra linked name but makes gap math subtle.

Test signals: hardlink creation, both rename cycles, and unlink cleanup must match expected `ENOENT` only at computed gaps.
<!-- END_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/rename-mass-5.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/rename-mass-dir.py -->
# sources/test-tools/unionmount-testsuite/tests/rename-mass-dir.py

Purpose: validates mass circular renames of directories, first empty and then populated. It is aimed at overlay directory rename, whiteout/opaque handling, and child preservation.

Important APIs and functions: exports five `subtest_*` functions using `ctx.no_dir()`, `ctx.mkdir()`, `ctx.rename()`, `ctx.rmdir()`, `ctx.open_file()`, and `ctx.unlink()`.

Control flow: subtests 1 and 2 create empty directories, rotate one gap around a seven-name ring, and remove survivors. Subtests 3 to 5 repeat with a file `a` in each directory, compute final content order, read each payload, then unlink children and remove directories.

State and persistence: directory dentries and child files persist across multiple renames. The content check reconstructs expected order from `iter_count`, ring cycle length, and final gap.

Dependencies and integration: depends on harness directory factories and filesystem support for directory rename. It integrates with overlay lower/upper state through `ctx.rename` and `ctx.rmdir`.

Risks: the arithmetic for expected payload order is dense and can fail if `iter_count` or `ring_size` changes without updating reasoning. Directory renames across union layers are high-risk operations.

Test signals: successful renames, expected absent gap, preserved child file contents, and clean removal of every surviving directory.
<!-- END_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/rename-mass-dir.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/rename-mass-sym.py -->
# sources/test-tools/unionmount-testsuite/tests/rename-mass-sym.py

Purpose: stress-tests repeated circular renames of symlinks to files and symlinks to directories. It verifies both symlink object movement and target resolution after mass rename.

Important APIs and functions: six subtests use `ctx.direct_sym()`, `ctx.direct_dir_sym()`, `ctx.rename()`, `ctx.readlink()`, `ctx.open_file()`, `ctx.open_dir()`, `ctx.unlink()`, and `ctx.rmdir(..., err=ENOTDIR)`.

Control flow: subtests 1 to 3 rotate file symlinks, verify final link targets and readable file contents, then unlink them. Subtests 4 to 6 repeat for directory symlinks, verifying `readlink` target strings and openability as directories.

State and persistence: persistent state is the symlink inode/dentry mapping and link text. The test tracks only ring-position arithmetic locally.

Dependencies and integration: uses unionmount fixtures that provide numbered direct symlinks and directory symlinks. It exercises VFS symlink rename semantics through the overlay/union layer.

Risks: trailing slash mode changes behavior for operations through symlinks; the test explicitly checks directory symlink unlink by confirming `rmdir` returns `ENOTDIR`.

Test signals: expected link text, successful target opens, one missing gap, and no unexpected symlink leftovers after cleanup.
<!-- END_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/rename-mass-sym.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/rename-mass.py -->
# sources/test-tools/unionmount-testsuite/tests/rename-mass.py

Purpose: the simplest mass-rename file test, rotating an existing sequence of lower regular files through a fixed ring and then deleting the survivors.

Important APIs and functions: defines `subtest_1(ctx)` for circular `ctx.rename()` calls and `subtest_2(ctx)` for cleanup with `ctx.unlink()`. It imports `errno` for `ENOENT`.

Control flow: `subtest_1` starts with the gap at the last ring index and repeatedly moves the previous entry into the gap. `subtest_2` calculates the final gap and expects it to be absent.

State and persistence: the namespace state is the only persistent state. Data content is not read; the test is focused on dentry existence and rename success.

Dependencies and integration: depends on `ctx.reg_file()` generating a numeric base compatible with suffixes `100..106`. It is invoked by the harness as numbered subtests.

Risks: because no file content is checked, rename implementations that preserve existence but swap payloads incorrectly may escape this test.

Test signals: all rename calls succeed and exactly one `unlink` reports `ENOENT` during cleanup.
<!-- END_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/rename-mass.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/rename-move-dir.py -->
# sources/test-tools/unionmount-testsuite/tests/rename-move-dir.py

Purpose: covers moving directories between parent directories, including empty, populated, newly created, and nested directory cases. It targets overlay directory relocation correctness across lower and upper parents.

Important APIs and functions: twelve `subtest_*` functions use `ctx.empty_dir()`, `ctx.non_empty_dir()`, `ctx.no_dir()`, `ctx.mkdir()`, `ctx.rename()`, `ctx.open_dir()`, and `ctx.open_file()`.

Control flow: early subtests move existing empty/populated directories into another directory and verify old names vanish. Middle cases rename a directory or child before moving it, then verify child locations. Later cases create new directories under lower ancestors and move leaves or branches into lower-name targets.

State and persistence: directory tree topology is the key state. Child files `a` and nested `pop/b` are used as durable signals that descendants moved with their parent and that removed source paths stay hidden.

Dependencies and integration: relies on harness fixtures for empty and non-empty directories and on overlayfs support for redirect/rename of directories. It integrates with tests for whiteouts and copy-up through expected `ENOENT`.

Risks: uses trailing slashes on many paths, so path normalization differences can influence errno. Cross-directory rename of populated directories is one of the more sensitive overlay operations.

Test signals: old source names must fail with `ENOENT`, destination dirs must open, and expected child files must be found in exactly the new locations.
<!-- END_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/rename-move-dir.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/rename-new-dir.py -->
# sources/test-tools/unionmount-testsuite/tests/rename-new-dir.py

Purpose: tests rename behavior for empty directories created during the test. It covers round trips, deletion interactions, self-renames, replacements, and renaming over removed lower directories.

Important APIs and functions: contains fourteen `subtest_*` definitions, though the final four reuse names `subtest_11` and `subtest_12`; in normal Python import the later definitions shadow the earlier same-named functions. Uses `ctx.mkdir()`, `ctx.rename()`, `ctx.rmdir()`, `ctx.unlink()`, `ctx.open_dir()`, and `ctx.open_file()`.

Control flow: the active definitions include initial rename-back and remove/unlink checks, double rename, invalid replacement over populated dirs/files/parent, and cases where a new empty dir replaces an emptied or recursively removed lower dir.

State and persistence: the test creates upper-layer directories and validates that deleted lower names stay hidden or can be replaced. No file data is persisted except checks for absent lower children after replacement.

Dependencies and integration: depends on the harness collecting subtests by function name after module import. Duplicate function names are an integration risk because earlier cases can be silently lost.

Risks: duplicate `subtest_11` and `subtest_12` definitions likely reduce coverage. Replacement over lower directories is sensitive to opaque directory and whiteout semantics.

Test signals: expected `ENOENT`, `EISDIR`, `ENOTDIR`, or `ENOTEMPTY` results plus successful opens of final directory names.
<!-- END_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/rename-new-dir.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/rename-new-pop-dir.py -->
# sources/test-tools/unionmount-testsuite/tests/rename-new-pop-dir.py

Purpose: exhaustively tests renaming newly created populated directories. It validates child preservation, replacement semantics, and behavior when lower directories have been removed, emptied, or left populated.

Important APIs and functions: nineteen `subtest_*` functions use `ctx.mkdir()`, `ctx.open_file()`, `ctx.rename()`, `ctx.rmdir()`, `ctx.unlink()`, `ctx.rmtree()`, `ctx.open_dir()`, and errno expectations including `ENOENT`, `EISDIR`, `EINVAL`, `ENOTDIR`, and `ENOTEMPTY`.

Control flow: initial cases create a new directory containing `a`, rename it back and forth, attempt invalid unlinks/removes, and verify content. Later cases rename over empty dirs, removed lower dirs, removed populated lower dirs, same-name/different-name child layouts, and an emptied lower directory.

State and persistence: state includes upper-created directory trees and lower directory deletion markers. Child files such as `a`, `b`, and `pop/x` verify which tree survived after replacement.

Dependencies and integration: integrates with overlay whiteout/opaque handling and recursive removal via harness helpers. It assumes lower fixtures have a known `pop` subtree.

Risks: high coverage but high setup sensitivity; a fixture layout change can invalidate many hardcoded child checks. Rename-over-removed-lower cases are subtle across overlay modes.

Test signals: final directories must open at the target, source names must disappear where expected, and child contents or absences must match each scenario.
<!-- END_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/rename-new-pop-dir.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/rename-pop-dir.py -->
# sources/test-tools/unionmount-testsuite/tests/rename-pop-dir.py

Purpose: tests rename behavior for existing populated lower directories. It validates preserving descendants, invalid replacements, and replacement over empty directories.

Important APIs and functions: eleven `subtest_*` functions use `ctx.non_empty_dir()`, `ctx.empty_dir()`, `ctx.no_dir()`, `ctx.rename()`, `ctx.rmdir()`, `ctx.unlink()`, `ctx.open_dir()`, and `ctx.open_file()`.

Control flow: cases rename a populated dir away and back, remove/unlink old names, try removing non-empty directories, perform double rename, replace an empty directory, self-rename, and reject replacement over files, child files, and parent directory.

State and persistence: persistent state is a lower directory with child `a` and sometimes nested `pop/b`. The test expects child files to remain attached after legal renames and old paths to be hidden.

Dependencies and integration: depends on overlay copy-up or redirect semantics for lower populated directories. Harness errno checking distinguishes `ENOTEMPTY`, `EISDIR`, `ENOTDIR`, and `EINVAL`.

Risks: different filesystems can disagree on exact errno for invalid directory-over-file cases; the test encodes Linux overlay expectations.

Test signals: child `a` remains readable after valid renames; invalid operations leave source trees intact; removed source paths report `ENOENT`.
<!-- END_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/rename-pop-dir.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/rmdir.py -->
# sources/test-tools/unionmount-testsuite/tests/rmdir.py

Purpose: validates `rmdir` behavior over nonexistent paths, files, empty lower dirs, populated dirs, copied-up contents, symlinks, dangling symlinks, and opaque recreated dirs.

Important APIs and functions: sixteen `subtest_*` functions call `ctx.rmdir()`, `ctx.rmtree()`, `ctx.unlink()`, `ctx.mkdir()`, `ctx.open_file()`, and fixture providers for files, dirs, direct/indirect symlinks, and broken symlinks.

Control flow: the test starts with negative nonexistent/file cases, proceeds through empty and populated directory removal sequences, mutates lower-populated dirs by unlinking/copying-up/recreating children, then checks directory symlink behavior and opaque directory recreation.

State and persistence: it creates and removes upper entries, whiteouts lower names, and verifies child file visibility after directory tree removal. Recreated directories test opacity after a lower directory was removed.

Dependencies and integration: relies on harness recursive removal and trailing slash behavior. It exercises overlayfs whiteout, opaque directory, and symlink traversal rules.

Risks: exact errno values for symlink plus trailing slash paths can be filesystem-specific. Recursive cleanup must be reliable or later assertions may see stale children.

Test signals: expected errno values, successful removal after children are deleted, and absent child files after `rmtree`.
<!-- END_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/rmdir.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/rmtree-new.py -->
# sources/test-tools/unionmount-testsuite/tests/rmtree-new.py

Purpose: tests recursive removal of a lower populated directory after adding a new upper subdirectory inside it.

Important APIs and functions: one `subtest_1(ctx)` uses `ctx.non_empty_dir()`, `ctx.mkdir()`, and `ctx.rmtree()`.

Control flow: it selects a populated directory, creates a new child `b`, then recursively removes the parent directory.

State and persistence: state spans merged lower contents and newly created upper contents. The important behavior is that recursive removal handles both layers as one merged tree.

Dependencies and integration: depends on the harness `rmtree` helper to issue the correct unlink/rmdir sequence through the union mount.

Risks: minimal assertions after removal mean this primarily detects syscall failure, not every possible leftover hidden entry.

Test signals: the recursive remove operation completes without unexpected errors.
<!-- END_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/rmtree-new.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/rmtree.py -->
# sources/test-tools/unionmount-testsuite/tests/rmtree.py

Purpose: verifies recursive removal of a populated lower directory containing lower files.

Important APIs and functions: single `subtest_1(ctx)` uses `ctx.non_empty_dir()` and `ctx.rmtree()`.

Control flow: resolves a populated directory path, appends the harness trailing slash convention, and asks the context to recursively delete it.

State and persistence: removes a merged lower directory tree through the union mount, causing whiteouts or opaque state depending on implementation.

Dependencies and integration: depends entirely on the test harness `rmtree` helper for traversal and operation ordering.

Risks: no explicit post-removal opens are performed here, so failures are detected by exceptions from `rmtree` rather than later visibility checks.

Test signals: success is completion of recursive removal without unexpected errno.
<!-- END_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/rmtree.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/sym1-creat-excl.py -->
# sources/test-tools/unionmount-testsuite/tests/sym1-creat-excl.py

Purpose: verifies that opening a direct symlink to an existing file with `O_CREAT|O_EXCL` fails with `EEXIST` and leaves the target unchanged.

Important APIs and functions: five subtests cover read-only, write-only, append write-only, read/write, and append read/write combinations through `ctx.open_file()`.

Control flow: each subtest builds a direct symlink path from `ctx.direct_sym()`, attempts an exclusive create expecting `EEXIST`, then reopens the symlink read-only and expects original content `:xxx:yyy:zzz`.

State and persistence: the test should not change file data. Persistence signal is that the lower target remains readable and unchanged after failed opens.

Dependencies and integration: depends on harness mapping flag booleans `ro`, `wo`, `rw`, `app`, `crt`, and `ex` into open flags.

Risks: one case passes `ro=1, app=1` for an append read/write label, mirroring surrounding tests but relying on harness interpretation.

Test signals: `EEXIST` on each exclusive create and unchanged file contents after each failure.
<!-- END_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/sym1-creat-excl.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/sym1-creat.py -->
# sources/test-tools/unionmount-testsuite/tests/sym1-creat.py

Purpose: checks ordinary `O_CREAT` opens through a direct symlink to an existing file, including overwrites and appends.

Important APIs and functions: five subtests use `ctx.direct_sym()`, `ctx.reg_file()`, and `ctx.open_file()` with read-only, write-only, append, and read/write modes.

Control flow: read-only opens confirm existing content. Write and read/write cases write `q` then `p` at offset zero or append them, with follow-up reads proving expected content transitions.

State and persistence: the target file content changes through the symlink. Overwrite cases modify the first byte; append cases extend the file.

Dependencies and integration: depends on symlink following during open and harness content checking. It interacts with overlay copy-up if the lower target is modified.

Risks: tests assume write offset starts at zero for non-append opens and that `O_CREAT` does not replace the symlink itself.

Test signals: final content strings `pxxx:yyy:zzz` or `:xxx:yyy:zzzqp` prove writes reached the target through the symlink.
<!-- END_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/sym1-creat.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/sym1-plain.py -->
# sources/test-tools/unionmount-testsuite/tests/sym1-plain.py

Purpose: validates plain opens through a direct symlink to an existing file without create or truncate flags.

Important APIs and functions: five subtests call `ctx.open_file()` on `ctx.direct_sym()` with read-only, write-only, append write-only, read/write, and append read/write modes.

Control flow: read-only subtests verify baseline content. Write modes overwrite first bytes, while append modes append `q` then `p`, and each mutation is followed by a read check.

State and persistence: target file data persists across operations within each subtest. The symlink object should remain a symlink; only the target content changes.

Dependencies and integration: depends on harness fixtures and open flag conversion. It exercises symlink resolution through the union filesystem.

Risks: shared fixture reuse across subtests could be problematic if the harness does not reset state; these tests assume isolated subtest setup.

Test signals: expected content after overwrite or append, with no unexpected creation or symlink replacement.
<!-- END_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/sym1-plain.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/sym1-trunc.py -->
# sources/test-tools/unionmount-testsuite/tests/sym1-trunc.py

Purpose: verifies `O_TRUNC` opens through a direct symlink to an existing file.

Important APIs and functions: five subtests combine `tr=1` with read-only, write-only, append write-only, read/write, and append read/write calls to `ctx.open_file()`.

Control flow: read-only truncate empties the target and reads empty content. Write and read/write cases truncate first, then write `q` or `p`; append with truncate also yields only the newly written byte.

State and persistence: target content is deliberately destroyed through the symlink. Follow-up reads prove truncation applied to the target file, not to the symlink object.

Dependencies and integration: relies on Linux open semantics and harness flag mapping for `O_TRUNC`. Exercises copy-up of truncated lower file data under overlay.

Risks: `O_TRUNC|O_RDONLY` behavior can be platform-sensitive; this suite encodes the expected Linux behavior used by the harness.

Test signals: empty reads after read-only truncation and single-byte contents after truncating writes.
<!-- END_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/sym1-trunc.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/sym2-creat-excl.py -->
# sources/test-tools/unionmount-testsuite/tests/sym2-creat-excl.py

Purpose: checks `O_CREAT|O_EXCL` through an indirect symlink chain pointing to an existing file. It should fail without modifying either link or target.

Important APIs and functions: five subtests use `ctx.indirect_sym()`, `ctx.direct_sym()`, `ctx.reg_file()`, and `ctx.open_file()` with exclusive create flag combinations.

Control flow: each case attempts to open the indirect symlink with `crt=1, ex=1`, expects `EEXIST`, then reads through the indirect link to confirm original content.

State and persistence: both the direct symlink, indirect symlink, and target file remain unchanged. No writes should be committed after the failed exclusive create.

Dependencies and integration: depends on the harness constructing an indirect symlink chain and on VFS semantics for exclusive create through symlinks.

Risks: symlink chains plus exclusive create are sensitive to whether the final target exists; broken fixture setup would change expected errno.

Test signals: `EEXIST` on every exclusive open and stable target content `:xxx:yyy:zzz`.
<!-- END_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/sym2-creat-excl.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/sym2-creat.py -->
# sources/test-tools/unionmount-testsuite/tests/sym2-creat.py

Purpose: validates `O_CREAT` opens through an indirect symlink chain to an existing file.

Important APIs and functions: five subtests use `ctx.indirect_sym()` and `ctx.open_file()` in read-only, write-only, append, and read/write forms.

Control flow: read-only creates are no-ops over an existing target. Other cases write `q` and then `p`, either overwriting the first byte or appending at end, then verify content.

State and persistence: target content changes through a two-hop symlink path; the symlink chain should remain intact.

Dependencies and integration: depends on correct resolution of indirect symlink fixtures and copy-up behavior for lower targets modified through links.

Risks: because `direct` and `f` variables are assigned but unused, the test relies entirely on fixture names being created by context helpers rather than local checks.

Test signals: readbacks through the indirect symlink show exact overwrite or append content.
<!-- END_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/sym2-creat.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/sym2-plain.py -->
# sources/test-tools/unionmount-testsuite/tests/sym2-plain.py

Purpose: tests ordinary open/read/write/append behavior through an indirect symlink chain.

Important APIs and functions: five `subtest_*` functions use `ctx.indirect_sym()` and `ctx.open_file()` with `ro`, `wo`, `rw`, and `app` flag combinations.

Control flow: the file is read through the chain, then overwritten or appended twice depending on subtest. Each mutation is verified by a read through the same indirect path.

State and persistence: persistent data changes only at the ultimate target; symlink dentries should remain unchanged.

Dependencies and integration: relies on unionmount context fixture isolation and Linux symlink-following semantics through overlay layers.

Risks: multi-hop symlink resolution can expose path normalization or copy-up bugs that direct-symlink tests do not catch.

Test signals: expected contents after each operation and no unexpected open failures.
<!-- END_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/sym2-plain.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/sym2-trunc.py -->
# sources/test-tools/unionmount-testsuite/tests/sym2-trunc.py

Purpose: verifies truncating opens through an indirect symlink chain to an existing file.

Important APIs and functions: five subtests combine `ctx.indirect_sym()` with `ctx.open_file(..., tr=1)` and mode flags.

Control flow: each case opens through the indirect symlink with truncation. Read-only checks an empty target; write modes write one byte after truncation and verify the target contains only that byte.

State and persistence: target data is truncated through a two-hop link path. The symlink objects should not be replaced or truncated.

Dependencies and integration: depends on the context's indirect symlink fixtures and open flag mapping. Exercises overlay copy-up and truncation of lower target data.

Risks: platform behavior for `O_TRUNC|O_RDONLY` can differ outside the intended Linux environment.

Test signals: empty or single-byte target reads after truncating opens.
<!-- END_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/sym2-trunc.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/symx-creat-excl.py -->
# sources/test-tools/unionmount-testsuite/tests/symx-creat-excl.py

Purpose: checks exclusive create through a dangling symlink. Because the symlink's target is absent, `O_CREAT|O_EXCL` should fail with `EEXIST` for the symlink itself.

Important APIs and functions: five subtests use `ctx.pointless()` for a broken symlink, `ctx.no_file()` for the absent target, and `ctx.open_file()` with `crt=1, ex=1`.

Control flow: each subtest attempts an exclusive create through the dangling symlink under different access modes and expects `EEXIST`.

State and persistence: no new target file should be created and the dangling symlink should remain in place.

Dependencies and integration: relies on Linux `O_EXCL` symlink behavior and harness errno checking.

Risks: filesystems or wrappers that follow dangling symlinks before applying exclusive-create rules could report different errno or create the target.

Test signals: every open returns `EEXIST`; no follow-up reads are needed because the operation must not create data.
<!-- END_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/symx-creat-excl.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/symx-creat-trunc.py -->
# sources/test-tools/unionmount-testsuite/tests/symx-creat-trunc.py

Purpose: verifies that `O_CREAT|O_TRUNC` through a dangling symlink creates the missing target file and writes or reads through it.

Important APIs and functions: five subtests use `ctx.pointless()`, `ctx.no_file()`, and `ctx.open_file()` with `crt=1, tr=1` plus access mode variants.

Control flow: read-only create/truncate yields an empty newly created target. Write and append variants create/truncate then write `q`, and read the previously absent target path to confirm contents.

State and persistence: the dangling symlink remains, while its target path becomes a new upper-layer file. The target content is empty or `q` depending on mode.

Dependencies and integration: depends on harness fixture alignment where `ctx.pointless()` resolves to `ctx.no_file()`. Exercises symlink-following creation in overlay.

Risks: `O_CREAT|O_TRUNC|O_RDONLY` through dangling symlink is subtle and Linux-specific. The local variable `f` is only used for validation, not for setup.

Test signals: successful open through the symlink and target file content visible at `ctx.no_file()`.
<!-- END_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/symx-creat-trunc.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/symx-creat.py -->
# sources/test-tools/unionmount-testsuite/tests/symx-creat.py

Purpose: tests `O_CREAT` through a dangling symlink without truncation. It should create the missing target and allow normal reads/writes through the link.

Important APIs and functions: five subtests use `ctx.pointless()`, `ctx.no_file()`, and `ctx.open_file()` with create and access mode flags.

Control flow: read-only create checks an empty created file. Write and read/write cases create then write `q`; append cases also create and append `q`, resulting in the same one-byte content for a new file.

State and persistence: the target file is newly created in the upper layer while the symlink object remains intact.

Dependencies and integration: depends on the context's broken symlink target matching `ctx.no_file()`.

Risks: if trailing slash mode is active, a dangling symlink path may produce directory-related errors in some operations; the test expects harness-normalized Linux behavior.

Test signals: target file becomes readable with empty or `q` content after open through the dangling symlink.
<!-- END_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/symx-creat.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/symx-plain.py -->
# sources/test-tools/unionmount-testsuite/tests/symx-plain.py

Purpose: verifies plain opens through a dangling symlink without create fail with `ENOENT`.

Important APIs and functions: five subtests call `ctx.open_file()` on `ctx.pointless()` with read-only, write-only, append, read/write, and append read/write modes.

Control flow: each subtest constructs the broken symlink and absent target, then expects `ENOENT` for the open.

State and persistence: no file is created and no target data is modified because all operations fail.

Dependencies and integration: depends on harness broken-symlink fixtures and errno validation.

Risks: no postcondition checks are performed beyond open failure; if a buggy filesystem creates a target and still reports failure, this test alone would not detect the leftover.

Test signals: consistent `ENOENT` for every non-create open mode through the dangling symlink.
<!-- END_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/symx-plain.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/symx-trunc.py -->
# sources/test-tools/unionmount-testsuite/tests/symx-trunc.py

Purpose: verifies truncating opens through a dangling symlink without `O_CREAT` fail because the target does not exist.

Important APIs and functions: five subtests use `ctx.pointless()` and `ctx.open_file(..., tr=1)` with mode variants, expecting `ENOENT`.

Control flow: each subtest attempts `O_TRUNC` through the dangling symlink and asserts the absent-target error.

State and persistence: no target file should be created or truncated. The dangling symlink should remain.

Dependencies and integration: relies on Linux open semantics and harness mapping of `tr=1` to `O_TRUNC`.

Risks: exact behavior for `O_TRUNC|O_RDONLY` can be implementation-specific, but the intended Linux result here is `ENOENT` for the unresolved target.

Test signals: every truncating open without create returns `ENOENT`.
<!-- END_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/symx-trunc.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/truncate.py -->
# sources/test-tools/unionmount-testsuite/tests/truncate.py

Purpose: tests explicit truncate sizes on existing regular files and validates resulting file size and content prefixes.

Important APIs and functions: one `subtest_1(ctx)` uses `ctx.reg_file()`, `ctx.get_file_size()`, `ctx.truncate()`, `ctx.open_file()`, `ctx.incr_filenr()`, and `TestError`.

Control flow: builds a 29-byte expected key by padding `:xxx:yyy:zzz` with NULs, then loops sizes 0..28. For non-trailing-slash mode it validates initial size, truncates, checks post size, and reads the expected prefix. In trailing-slash mode it expects `ENOTDIR`.

State and persistence: each loop uses a fixture file and advances the file number to avoid repeated truncation of one path. Truncation changes file length and content visibility.

Dependencies and integration: depends on context size and truncate helpers, and on `TestError` being available from harness imports.

Risks: binary NUL content in expected reads requires the harness to compare exact strings. Initial file size is assumed to be 12.

Test signals: exact post-truncate size and prefix data for every tested length, or expected `ENOTDIR` in trailing slash mode.
<!-- END_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/truncate.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/unlink.py -->
# sources/test-tools/unionmount-testsuite/tests/unlink.py

Purpose: validates unlink behavior for files, direct and indirect symlinks, directories, directory symlinks, absent files, and broken symlinks.

Important APIs and functions: ten `subtest_*` functions use `ctx.unlink()`, `ctx.open_file()`, `ctx.open_dir()`, and fixture helpers for regular files, symlinks, directory symlinks, and broken symlinks.

Control flow: file and symlink cases unlink an object, verify it disappears, and verify targets remain where relevant. Directory cases expect `EISDIR`. Directory symlink cases account for trailing-slash mode, where path resolution may still open the target after unlink. Absent and broken symlink cases assert `ENOENT` on repeat unlink.

State and persistence: unlink creates whiteouts for lower names or removes upper symlinks. Target files/directories should persist when only symlink dentries are removed.

Dependencies and integration: depends on context trailing slash behavior and fixture isolation.

Risks: subtests 8 and 9 are effectively identical dangling-symlink unlink checks. Trailing slash semantics around symlinks are a known portability hazard.

Test signals: expected `EISDIR` or `ENOENT`, target preservation after symlink unlink, and removed path invisibility.
<!-- END_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/unlink.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tool_box.py -->
# sources/test-tools/unionmount-testsuite/tool_box.py

Purpose: shared utility module for unionmount tests. It provides lightweight exceptions, file I/O helpers, shell command execution, kernel taint checking, and overlay option discovery helpers.

Important APIs and functions: defines `ArgumentError`, `TestError`, `exit_error()`, `system()`, `read_file()`, `write_file()`, `write_kmsg()`, `check_not_tainted()`, `check_bool_modparam()`, and `check_bool_mntopt()`.

Control flow: `system` wraps `os.system` and raises on nonzero exit. `current_taint` is captured at import time, and `check_not_tainted` compares later `/proc/sys/kernel/tainted` reads against it. Mount/module option helpers parse sysfs module params and mount option strings.

State and persistence: module global `current_taint` is persistent baseline state. File helpers read/write real system paths such as `/dev/kmsg` and `/sys/module/overlay/parameters`.

Dependencies and integration: imported by setup/unmount/test harness code. Depends on Linux procfs/sysfs, `modprobe`, and Python `os`/`sys`.

Risks: `os.system` uses shell parsing and returns encoded wait status; any nonzero raises a generic `RuntimeError`. `check_not_tainted` constructs a `RuntimeError` with multiple arguments by mistake in the taint mismatch path.

Test signals: helper failures propagate as exceptions, making harness runs fail when shell commands fail or kernel taint changes.
<!-- END_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tool_box.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/unmount_union.py -->
# sources/test-tools/unionmount-testsuite/unmount_union.py

Purpose: central teardown helper for unmounting unionmount/overlay test filesystems and checking kernel taint after each unmount stage.

Important APIs and functions: exports `unmount_union(ctx)`. It imports `system` and `check_not_tainted` from `tool_box`.

Control flow: obtains `cfg = ctx.config()`, unmounts the union mount, optionally unmounts lower, overlay upper submounts, base, or upper mounts based on config predicates. Overlay upper child unmounts are attempted with a wildcard and ignored if they fail.

State and persistence: tears down real mounted filesystems. It does not persist local state, but it changes global mount namespace state and checks kernel taint after operations.

Dependencies and integration: depends on configuration methods such as `union_mntroot()`, `should_mount_lower()`, `testing_overlayfs()`, `maxfs()`, `is_nested()`, `upper_mntroot()`, `should_mount_base()`, and `should_mount_upper()`.

Risks: wildcard unmount command is shell-expanded and may behave unexpectedly if paths contain spaces. Ignoring upper child unmount failures may hide partial teardown problems until later stages.

Test signals: any unmount command failure outside the ignored wildcard path or any kernel taint change fails teardown.
<!-- END_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/unmount_union.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/.checkpatch.conf -->
# sources/test-tools/xfstests-bld/.checkpatch.conf

Purpose: configures Linux `checkpatch.pl` expectations for the xfstests-bld tree.

Important APIs and functions: no functions; it contains command-line style options for checkpatch.

Control flow: checkpatch consumes the file as configuration and ignores `EXECUTE_PERMISSIONS`, `FILE_PATH_CHANGES`, and `SPDX_LICENSE_TAG` warnings.

State and persistence: no runtime state. It persists repository lint policy.

Dependencies and integration: integrates with Linux checkpatch tooling, likely invoked by developer CI or review scripts.

Risks: ignoring SPDX and permission warnings can hide issues that matter for packaging or licensing review, but it may be intentional for imported/generated build assets.

Test signals: checkpatch output should be quieter for known non-actionable warnings in this tree.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/.checkpatch.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/.travis.yml -->
# sources/test-tools/xfstests-bld/.travis.yml

Purpose: legacy Travis CI configuration for building xfstests-bld and producing a tarball on Linux with GCC.

Important APIs and functions: YAML keys include `language: c`, `os`, `compiler`, `script`, `env.global`, and `before_install`.

Control flow: before install updates apt metadata and installs build dependencies including autoconf, debootstrap, fakechroot, qemu-utils, rsync, lib dependencies, and Go 1.8. The build script runs `make clean && make && make tarball`.

State and persistence: CI installs packages into the Travis VM and produces build artifacts in the workspace. No persistent service state is configured.

Dependencies and integration: integrates with Travis CI's Linux environment and the top-level Makefile targets.

Risks: Travis environment and package names are stale; `autoconf2.64` and `golang-1.8-go` may not exist in modern distributions. CI coverage may not reflect Dockerfile's current Debian trixie build.

Test signals: a successful CI run proves clean build, default `make`, and tarball generation work with the declared dependencies.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/.travis.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/Dockerfile -->
# sources/test-tools/xfstests-bld/Dockerfile

Purpose: builds a Debian-based Docker image containing the xfstests-bld build environment and an installed xfstests test appliance layout.

Important APIs and functions: Docker directives `FROM debian:trixie`, package-installing `RUN`, `LABEL`, `COPY`, build/install `RUN`, `ENTRYPOINT`, and `CMD`.

Control flow: installs build dependencies, copies the repository to `/devel/xfstests-bld`, builds `fstests-bld` with `config.docker`, makes a tarball, extracts it under `/root`, installs test-appliance files, creates `fsgqa`, removes source tree, creates `/results`, and purges some build packages.

State and persistence: final image persists built xfstests files, appliance files, `/entrypoint`, `/root` contents, user `fsgqa`, and `/results`. Apt caches and documentation are removed to reduce size.

Dependencies and integration: integrates top-level repository, `fstests-bld`, and `test-appliance/docker-entrypoint`. Depends on Debian package availability and Docker build context.

Risks: package names and Debian trixie behavior can change. Purging build dependencies may remove tools needed for debugging inside the image. `COPY .` makes image builds sensitive to local untracked files unless `.dockerignore` exists.

Test signals: successful Docker build and default command `-g quick` via `/entrypoint` indicate the packaged appliance can run quick tests.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/Makefile -->
# sources/test-tools/xfstests-bld/Makefile

Purpose: top-level makefile that materializes user-facing helper scripts from templates and installs them with bash completion links.

Important APIs and functions: variables `SCRIPTS`, `KBUILD_SCRIPTS`, `bindir`, and `completiondir`; targets `all`, `clean`, `install`, pattern rules for run-fstests and kernel-build templates.

Control flow: `all` builds wrapper scripts. Pattern rules substitute `@DIR@` with the current repository path and mark outputs executable. `install` copies scripts to `$(HOME)/bin` by default and creates completion symlinks.

State and persistence: creates generated executable scripts in the source tree and installs copies/symlinks under `DESTDIR` plus user-oriented directories.

Dependencies and integration: integrates with `run-fstests/*.sh.in`, `kernel-build/*.sh.in`, and bash-completion layout.

Risks: generated scripts bake in the current absolute path, so moving the repository requires regeneration. Default install paths target the invoking user's home.

Test signals: `make`, `make clean`, and `make install DESTDIR=...` should produce/remove/copy the expected wrapper scripts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/build-appliance -->
# sources/test-tools/xfstests-bld/build-appliance

Purpose: orchestrates building or updating an xfstests test appliance image/tarball, optionally including a GCE image.

Important APIs and functions: shell script with `usage()`, option parsing via `getopt`, config loading from `config.custom` or `config`, architecture helpers from `run-fstests/util/arch-funcs`, and calls to `fstests-bld`, `run-fstests`, and `test-appliance` tools.

Control flow: parses flags such as `--add-package`, `--chroot`, `--out-tar`, `--out-both`, `--update`, `--gce`, and `--datecode`; sets architecture; runs `update-all` or clean build; generates tarball; optionally starts GCE image creation; runs `test-appliance/gen-image`; then streams and waits for GCE output.

State and persistence: produces `root_fs.img` and/or `root_fs.tar.gz`, may update repository build outputs, may create cloud image artifacts, and writes a temporary `/tmp/gce-xfstests-create.$$` log.

Dependencies and integration: depends on config variables, schroot/sudo, git timestamps, `fstests-bld/build-all`, `gen-tarball`, `gce-xfstests`, and `gen-image`.

Risks: uses `set -e -u`, so unset config variables can abort. Background job control with `wait %./gce-xfstests` is fragile outside interactive-style shells. Package list concatenation converts only the first space to a comma.

Test signals: successful appliance build, generated tarball/image, and optional GCE image creation without unexpected shell exits.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/build-appliance -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/config -->
# sources/test-tools/xfstests-bld/config

Purpose: default configuration for root filesystem image builds.

Important APIs and functions: shell variable assignments for `BUILD_ENV`, `SUDO_ENV`, optional `OUT_TAR`, and `gen_image_args`.

Control flow: sourced by `build-appliance`; it does not execute complex logic. Commented examples show schroot-based build environments and tarball output selection.

State and persistence: persists default build policy in the repo. Runtime scripts import these variables into their shell state.

Dependencies and integration: integrates directly with `build-appliance` and `test-appliance/gen-image` argument construction.

Risks: because it is sourced shell, local modifications in `config.custom` or this file can execute arbitrary shell code. Default `SUDO_ENV=sudo` requires passwordless or interactive sudo for image creation.

Test signals: build scripts should pick up networking-enabled `gen_image_args` and default direct build environment when no `config.custom` exists.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/config -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/Makefile -->
# sources/test-tools/xfstests-bld/fstests-bld/Makefile

Purpose: makefile for fetching, building, cleaning, and packaging the component repositories used in an xfstests appliance.

Important APIs and functions: variables `REPOS`, `SUBDIRS`, `SCRIPTS`; targets `all`, `all-clean-first`, `clean`, `realclean`, `tarball`, and `run-fstests/util/zerofree`.

Control flow: `all` runs `./get-all` then `./build-all`. `all-clean-first` removes build products and invokes `build-all --clean-first`. `clean` delegates clean to subdirectories, handles xfsprogs realclean, and removes generated build output. `realclean` additionally removes fetched repositories.

State and persistence: creates fetched repository directories, `bld`, generated scripts, version files, `xfstests`, and optional static `zerofree`.

Dependencies and integration: integrates with `get-all`, `build-all`, `gen-tarball`, component subprojects, and system `cc`.

Risks: `realclean` is destructive to fetched repos. The clean loop ignores subdirectories without Makefiles, which is useful but can leave non-Makefile build products.

Test signals: `make all`, `make all-clean-first`, and `make tarball` are the primary build validation paths.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/android-compat/Makefile.in -->
# sources/test-tools/xfstests-bld/fstests-bld/android-compat/Makefile.in

Purpose: Autoconf template for building Android compatibility static/shared libraries and headers needed when cross-compiling xfstests components for bionic.

Important APIs and functions: variables for tool substitutions, `OBJS_RT`, `OBJS_COMPAT`, `LIBS`, `INCLUDES`, `SYS_INCLUDES`; targets `all`, `librt.a`, `libandroid_compat.a`, `libpthread.a`, `aio.h`, `install`, `clean`, and regenerated `Makefile`.

Control flow: compiles each C source into normal and `elfshared` PIC objects. Builds a stub `librt`, empty `libpthread`, and `libandroid_compat`; installs libraries and headers into configured prefix paths.

State and persistence: produces `.o`, `.a`, `.so.1.0`, `aio.h`, and `elfshared` artifacts; install persists libraries and headers into `libdir` and `includedir`.

Dependencies and integration: configured by `configure`; invoked by `build-all` in Android cross builds. Consumed by xfsprogs/xfstests builds via `-landroid_compat`.

Risks: `libandroid_compat.so.1.0` links `$(OBJS_RT)` instead of `$(OBJS_COMPAT)`, which appears suspicious. The empty `libpthread.a` may satisfy linkers but not functionality.

Test signals: successful `./configure && make && make install` under Android cross toolchain.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/android-compat/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/android-compat/android_compat.h -->
# sources/test-tools/xfstests-bld/fstests-bld/android-compat/android_compat.h

Purpose: compatibility header that declares or defines libc features missing from Android bionic for xfstests and related tools.

Important APIs and functions: defines `DEV_BSIZE`, `ino64_t`, permission aliases, and prototypes for `basename`, `hasmntopt`, `seekdir`, `telldir`, `sighold`, `sigrelse`, `getsubopt`, `valloc`, SysV shared memory functions, and `sync_file_range`.

Control flow: purely preprocessor declarations, guarded to avoid x86/x86_64 and repeated inclusion. It is meant to be force-included for target builds, not build-host tools.

State and persistence: no runtime state. It shapes compile-time ABI assumptions.

Dependencies and integration: used by `build-all` via `-include android_compat.h` for Android builds and installed by the android-compat Makefile.

Risks: declaring libc/kernel interfaces manually can drift from bionic or kernel headers. The architecture guard excludes x86/x86_64 Android builds.

Test signals: component builds compile without missing symbol/prototype errors when this header is included.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/android-compat/android_compat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/android-compat/configure -->
# sources/test-tools/xfstests-bld/fstests-bld/android-compat/configure

Purpose: generated GNU Autoconf 2.69 script that configures the android-compat subpackage and emits `Makefile` from `Makefile.in`.

Important APIs and functions: generated shell helpers for portable echo, path lookup, option parsing, temp directory creation, compile tests, `config.status` generation, and substitutions for `CC`, `CFLAGS`, `RANLIB`, build/host triplets, and installation directories.

Control flow: initializes portable shell environment, parses standard configure options and precious variables, finds `install-sh`/`config.guess`/`config.sub` in `../e2fsprogs-libs/config`, canonicalizes build and host, discovers a C compiler and `ranlib`, checks compiler behavior, registers `Makefile` in `CONFIG_FILES`, writes `config.status`, and runs it unless `--no-create` was given.

State and persistence: writes `config.log`, `config.status`, cache data if requested, and the configured `Makefile`. Temporary `conftest*` and `conf*` files are cleaned on normal exit.

Dependencies and integration: generated from `configure.ac`; invoked by `build-all` before building the Android compatibility library.

Risks: generated script is large and sensitive to missing e2fsprogs config helpers. Environment changes across cached runs cause explicit failure. It should usually be regenerated from `configure.ac` rather than manually edited.

Test signals: successful completion with a valid `Makefile` and compiler/ranlib substitutions.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/android-compat/configure -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/android-compat/configure.ac -->
# sources/test-tools/xfstests-bld/fstests-bld/android-compat/configure.ac

Purpose: concise Autoconf source for the android-compat build system.

Important APIs and functions: uses `AC_PREREQ(2.59)`, `AC_INIT(lio_listio.c)`, `AC_CONFIG_AUX_DIR(../e2fsprogs-libs/config)`, `AC_CANONICAL_BUILD`, `AC_CANONICAL_HOST`, `AC_PROG_CC`, `AC_PROG_RANLIB`, and `AC_OUTPUT(Makefile)`.

Control flow: Autoconf expands this into `configure`, which validates source identity, canonicalizes build/host, locates compiler and ranlib, and substitutes `Makefile.in`.

State and persistence: source-level build metadata only; generated outputs are `configure` and, at configure time, `Makefile`.

Dependencies and integration: depends on Autoconf and e2fsprogs config auxiliary scripts. It feeds `autoconf` when regenerating the script.

Risks: minimal checks mean missing headers/functions are not detected here; the compatibility library assumes its source code is suitable for the target.

Test signals: `autoconf` can regenerate `configure`, and `./configure` can create `Makefile`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/android-compat/configure.ac -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/android-compat/getgrent.c -->
# sources/test-tools/xfstests-bld/fstests-bld/android-compat/getgrent.c

Purpose: provides simple group database iteration for Android builds that lack full `getgrent`, `setgrent`, and `endgrent` behavior.

Important APIs and functions: static `entries[]` contains `root` gid 0 and `fsgqa` gid 31415; exports `getgrent()`, `setgrent()`, and `endgrent()`. Debug-only helpers implement lookup tests.

Control flow: `getgrent` initializes `current_grp` to the first entry, returns entries until a null sentinel, then returns `NULL`. Reset functions clear `current_grp`.

State and persistence: static pointer `current_grp` is process-global iteration state. No external files such as `/etc/group` are read.

Dependencies and integration: compiled into `libandroid_compat` and used by tools expecting POSIX group iteration in the appliance environment.

Risks: not thread-safe, not reentrant, and only models two groups. `gr_mem` is `NULL`, which may surprise callers expecting a null-terminated member list pointer.

Test signals: debug-only main can check `root`, `fsgqa`, and missing lookups when compiled with `DEBUG`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/android-compat/getgrent.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/android-compat/getpwent.c -->
# sources/test-tools/xfstests-bld/fstests-bld/android-compat/getpwent.c

Purpose: simulates passwd database iteration for Android builds, exposing `root` and `fsgqa` users required by filesystem tests.

Important APIs and functions: static `entries[]`, `current_pw`, exported `getpwent()` and `setpwent()`, disabled `endpwent()`, and debug-only `getpwnam`, `getpwuid`, `print_passwd`, and `main`.

Control flow: `getpwent` lazily starts at the first entry and advances until a null sentinel. `setpwent` resets iteration.

State and persistence: static iteration pointer is process-global. It does not consult `/etc/passwd`.

Dependencies and integration: compiled into Android compatibility library for xfstests tools that enumerate users.

Risks: `setpwent` is declared `int` but does not return a value, which can produce warnings or undefined return values. The implementation is not thread-safe and covers only two users.

Test signals: debug main validates lookup behavior for root, fsgqa, and absent entries.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/android-compat/getpwent.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/android-compat/getsubopt.c -->
# sources/test-tools/xfstests-bld/fstests-bld/android-compat/getsubopt.c

Purpose: supplies a BSD-derived implementation of `getsubopt` for Android/bionic environments.

Important APIs and functions: global `char *suboptarg` and exported `getsubopt(char **optionp, char * const *tokens, char **valuep)`.

Control flow: skips leading delimiters, isolates the next token and optional `=value`, updates `*optionp` to the remaining string, compares the token against `tokens`, and returns the matched index or `-1`.

State and persistence: mutates the input option string in place by writing NUL terminators; stores unmatched token start in global `suboptarg`.

Dependencies and integration: used by tools that parse comma-separated mount or command suboptions and expect glibc-like `getsubopt`.

Risks: destructive parsing requires writable input. The global `suboptarg` is not thread-safe. Behavior with quoted delimiters is not supported.

Test signals: callers should observe correct token indexes, `valuep` values, and progressive advancement of `optionp`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/android-compat/getsubopt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/android-compat/hasmntopt.c -->
# sources/test-tools/xfstests-bld/fstests-bld/android-compat/hasmntopt.c

Purpose: implements `hasmntopt` for Android, allowing callers to query comma-separated mount option strings in `struct mntent`.

Important APIs and functions: exported `hasmntopt(const struct mntent *mnt, const char *opt)` and debug-only test table/main.

Control flow: scans `mnt->mnt_opts` with `strstr`, checks option boundaries at start/comma and end/comma/equal, and returns a pointer to the match or `0`.

State and persistence: no mutable persistent state; reads the caller-provided mount option string.

Dependencies and integration: declared in `android_compat.h` and compiled into `libandroid_compat`.

Risks: uses substring search and advances by `len + 1`, so unusual overlapping option names may need careful review. Returns a mutable `char *` into the original option string.

Test signals: debug main checks positive matches for `foo`, `bar`, `baz` and negatives for absent names.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/android-compat/hasmntopt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/android-compat/lio_listio.c -->
# sources/test-tools/xfstests-bld/fstests-bld/android-compat/lio_listio.c

Purpose: provides a stub `lio_listio` symbol for builds that require librt linkage on Android.

Important APIs and functions: exports `int lio_listio(int mode, void *aiocb_list[], int nitems, void *sevp)`.

Control flow: prints a diagnostic to stderr and calls `abort()` unconditionally.

State and persistence: no persistent state; process terminates if the function is called.

Dependencies and integration: built into `librt.a`/shared librt by the android-compat Makefile to satisfy link-time references.

Risks: this is not a functional implementation. Any runtime path that calls `lio_listio` will abort the program, so consumers must not exercise async list I/O on Android.

Test signals: link success is the main signal; runtime use should be considered a failure unless a test deliberately expects abort.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/android-compat/lio_listio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/android-compat/quota.h -->
# sources/test-tools/xfstests-bld/fstests-bld/android-compat/quota.h

Purpose: minimal quota API header for Android builds lacking Linux quota definitions.

Important APIs and functions: defines quota type constants, `QCMD`, quota command constants, `QIF_*` and `IIF_*` masks, `struct dqblk`, shorthand field macros, `dqoff`, `struct dqinfo`, and `quotactl` prototype.

Control flow: preprocessor definitions and type declarations only.

State and persistence: no runtime state. Defines ABI layout expectations for quota tools.

Dependencies and integration: included by `quotactl.c` and installed as `sys/quota.h` by the android-compat Makefile.

Risks: structure layouts and command values must match kernel expectations. The header is intentionally minimal and may omit fields or commands needed by newer quota utilities.

Test signals: quota tools compile and link; runtime quota syscalls receive correctly shaped data structures.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/android-compat/quota.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/android-compat/quotactl.c -->
# sources/test-tools/xfstests-bld/fstests-bld/android-compat/quotactl.c

Purpose: implements `quotactl` on Android by forwarding directly to the kernel syscall.

Important APIs and functions: exports `int quotactl(int cmd, const char *special, int id, caddr_t addr)` and defines `__NR_quotactl` for aarch64 if missing.

Control flow: includes syscall headers and returns `syscall(SYS_quotactl, cmd, special, id, addr)`.

State and persistence: no local state; modifies/query quota state through the kernel.

Dependencies and integration: depends on syscall numbers and `quota.h`; compiled into the Android compatibility library for quota-tools and xfstests.

Risks: uses `SYS_quotactl` while conditionally defining `__NR_quotactl`; portability depends on headers mapping the macro. Non-aarch64 targets without a definition hit a preprocessor error.

Test signals: quota tools link, and runtime quota operations return kernel syscall results.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/android-compat/quotactl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/android-compat/shmget.c -->
# sources/test-tools/xfstests-bld/fstests-bld/android-compat/shmget.c

Purpose: supplies System V shared memory wrappers for Android/bionic builds.

Important APIs and functions: exports `shmctl`, `shmat`, `shmdt`, and `shmget`, each forwarding to the matching `SYS_*` syscall.

Control flow: each wrapper calls `syscall` with the provided arguments. `shmat` currently calls `syscall(SYS_shmat, ...)` but does not return the result.

State and persistence: operations create, attach, detach, or control kernel shared memory segments. The file maintains no local state.

Dependencies and integration: depends on `sys/glibc-syscalls.h`, syscall numbers, and `android_compat.h`; used by programs requiring SysV IPC.

Risks: missing return in `shmat` is a correctness bug and can corrupt callers' attached address handling. SysV IPC availability varies on Android kernels.

Test signals: compile/link success plus runtime shared-memory tests; `shmat` should be specifically validated.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/android-compat/shmget.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/android-compat/sighold.c -->
# sources/test-tools/xfstests-bld/fstests-bld/android-compat/sighold.c

Purpose: implements legacy `sighold` and `sigrelse` APIs using POSIX signal masks for Android builds.

Important APIs and functions: static helper `set_to_int(sigset_t *set, int sig)`, exported `sighold(int sig)`, and `sigrelse(int sig)`.

Control flow: helper initializes a signal set with one signal. `sighold` blocks it via `sigprocmask(SIG_BLOCK)`, and `sigrelse` unblocks it with `SIG_UNBLOCK`.

State and persistence: changes the calling thread/process signal mask according to `sigprocmask` semantics.

Dependencies and integration: declared by `android_compat.h` and linked into compatibility library.

Risks: `sigprocmask` behavior in multithreaded programs can be subtle; callers expecting System V signal semantics should be reviewed.

Test signals: callers can verify the target signal is blocked/unblocked and return codes propagate from `sigprocmask`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/android-compat/sighold.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/android-compat/sync_file_range.c -->
# sources/test-tools/xfstests-bld/fstests-bld/android-compat/sync_file_range.c

Purpose: exposes `sync_file_range` on Android by forwarding to the kernel syscall.

Important APIs and functions: exports `int sync_file_range(int fd, off64_t offset, off64_t nbytes, unsigned int flags)`.

Control flow: returns `syscall(SYS_sync_file_range, fd, offset, nbytes, flags)`.

State and persistence: requests writeback/synchronization of file ranges through the kernel; no local state.

Dependencies and integration: depends on syscall headers and `android_compat.h`; used by filesystem tools that call `sync_file_range`.

Risks: syscall availability and argument ABI can vary by architecture/kernel. Errors are returned directly through syscall conventions.

Test signals: compile/link success and runtime calls returning expected kernel success or errno.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/android-compat/sync_file_range.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/android-compat/telldir.c -->
# sources/test-tools/xfstests-bld/fstests-bld/android-compat/telldir.c

Purpose: implements `telldir` and `seekdir` for Android by relying on bionic's internal `DIR` layout.

Important APIs and functions: local redefinition `struct DIR { int fd_; }`, exported `long telldir(struct DIR *dirp)`, and `void seekdir(DIR *dirp, long loc)`.

Control flow: `telldir` returns `lseek(dirp->fd_, 0, SEEK_CUR)`. `seekdir` calls `lseek(dirp->fd_, loc, SEEK_SET)` and ignores the return.

State and persistence: manipulates directory stream kernel file offset. No local persistent state.

Dependencies and integration: depends on the first field of bionic `DIR` being the file descriptor, as documented in the source comment. Declared in `android_compat.h`.

Risks: intentionally relies on private libc layout, so it can break if bionic changes `DIR`. Error returns from `seekdir` are discarded.

Test signals: directory iteration code using `telldir`/`seekdir` works on the Android target without crashes or incorrect offsets.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/android-compat/telldir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/android-compat/ustat.c -->
# sources/test-tools/xfstests-bld/fstests-bld/android-compat/ustat.c

Purpose: provides an Android wrapper for the legacy `ustat` syscall.

Important APIs and functions: exports `int ustat(dev_t dev, struct ustat *ubuf)`.

Control flow: returns `syscall(SYS_ustat, dev, ubuf)`.

State and persistence: queries kernel filesystem statistics for a device; no local state.

Dependencies and integration: includes `ustat.h` and syscall headers; installed with android-compat for tools still referencing `ustat`.

Risks: `ustat` is obsolete and may be unavailable on some architectures/kernels. Callers should handle `ENOSYS`.

Test signals: link success and runtime syscall return matching target kernel support.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/android-compat/ustat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/android-compat/ustat.h -->
# sources/test-tools/xfstests-bld/fstests-bld/android-compat/ustat.h

Purpose: declares the legacy `ustat` interface and structure for Android builds.

Important APIs and functions: guarded header defining `struct ustat` with `f_tfree`, `f_tinode`, `f_fname`, and `f_fpack`, plus `ustat(dev_t, struct ustat *)` prototype.

Control flow: no runtime flow; preprocessor declarations only.

State and persistence: no state. Defines ABI shape for callers and `ustat.c`.

Dependencies and integration: installed as `sys/ustat.h` by the android-compat Makefile.

Risks: structure definition must match users' expectations; the legacy API is not suitable for new code and may not be implemented by target kernels.

Test signals: source files including `<sys/ustat.h>` compile under Android cross builds.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/android-compat/ustat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/android-compat/valloc.c -->
# sources/test-tools/xfstests-bld/fstests-bld/android-compat/valloc.c

Purpose: implements `valloc` for Android using `memalign`.

Important APIs and functions: exports `void *valloc(size_t size)`.

Control flow: calls `memalign(getpagesize(), size)` and returns the allocation.

State and persistence: returns heap memory owned by the caller and freed with normal allocator-compatible free if supported by the platform allocator.

Dependencies and integration: includes `<malloc.h>` and `<unistd.h>`; declared in `android_compat.h`.

Risks: `memalign` portability and free compatibility depend on bionic allocator behavior. No overflow or zero-size special handling is added.

Test signals: callers needing page-aligned memory receive non-null aligned allocations or allocator failures consistent with `memalign`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/android-compat/valloc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/build-all -->
# sources/test-tools/xfstests-bld/fstests-bld/build-all

Purpose: main build orchestrator for all component packages needed in the xfstests-bld appliance.

Important APIs and functions: shell functions `build_start()` and `set_skip_all()`, many `SKIP_*` flags, config loading, Android/cross-compile setup, reproducibility exports, and per-component build subshells.

Control flow: detects distro, sources config, sets Go/toolchain paths, handles cross/Android/static options, parses skip/only/clean/debug flags, sets `DESTDIR=bld`, builds Android compatibility if needed, then conditionally builds e2fslibs, popt, libaio, keyutils, fsverity, ima-evm-utils, util-linux, stress-ng, dbench, xfsprogs, fio, xfstests, quota, syzkaller, blktests, LTP, nvme-cli, and misc utilities.

State and persistence: creates `bld`, version `.ver` files, configured component trees, installed binaries/libraries/headers, and build-distro metadata. It mutates fetched repositories during configure/build.

Dependencies and integration: depends on `config`, fetched component repos, autoconf/automake/make, optional Go, cross toolchains, and component-specific build systems.

Risks: large script with many environment-sensitive branches. Static/cross/Android flags can interact subtly. Some paths patch upstream files with `ed` or remove generated files, so repeated builds must be tested.

Test signals: successful component builds, populated `bld`, generated version files, and no skipped required component unless explicitly configured.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/build-all -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/config -->
# sources/test-tools/xfstests-bld/fstests-bld/config

Purpose: default source repository and version configuration for building xfstests-bld components.

Important APIs and functions: shell variables for upstream git URLs, optional repository URLs, pinned commits/tags for fio, libaio, quota, and xfsprogs, optional toolchain variables, and linker flags.

Control flow: sourced by `get-all`/`build-all`; it contains no complex logic.

State and persistence: defines the reproducible source inputs and default build flags. Local `config.custom` can override it.

Dependencies and integration: integrated by build scripts that fetch repos, check out commits, and configure cross compilation.

Risks: pinned versions can become stale against newer kernels/tests. Optional repos are commented out, so related components are skipped unless configured and present.

Test signals: `get-all` fetches expected repositories and `build-all` uses the pinned commits and linker settings.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/config -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/dbench/Makefile.in -->
# sources/test-tools/xfstests-bld/fstests-bld/dbench/Makefile.in

Purpose: Autoconf Makefile template for building and installing dbench, tbench, and tbench server.

Important APIs and functions: variables `VERSION`, `CC`, `CFLAGS`, `LIBS`, object lists `DB_OBJS`, `TB_OBJS`, `SRV_OBJS`; targets `all`, `dbench`, `tbench`, `tbench_srv`, `install`, `clean`, and `proto`.

Control flow: links three executables from shared benchmark/control objects and either file I/O or socket I/O implementations. `install` copies binaries, workload data, man page, and manpage symlinks.

State and persistence: creates object files and executables in the build tree; install persists binaries and `client.txt` under configured prefix paths.

Dependencies and integration: generated by dbench `configure`; uses libpopt and generated `config.h`.

Risks: object list assumes companion files exist in the dbench source directory. Install path `mandir` receives a single `dbench.1` with symlinks for tbench tools.

Test signals: `make`, `make install DESTDIR=...`, and optional `make proto` succeed.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/dbench/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/dbench/autogen.sh -->
# sources/test-tools/xfstests-bld/fstests-bld/dbench/autogen.sh

Purpose: regenerates dbench Autoconf files.

Important APIs and functions: shell script invoking `autoheader` then `autoconf`, exiting on the first failure.

Control flow: runs `autoheader || exit 1`, then `autoconf || exit 1`, then exits 0.

State and persistence: regenerates `config.h.in` and `configure` in the dbench directory.

Dependencies and integration: used by developers or build scripts when Autoconf inputs change. `build-all` runs `autoheader; autoconf` directly instead of this wrapper.

Risks: depends on local Autoconf version; generated output can churn across versions.

Test signals: both Autoconf commands complete and generated files are refreshed.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/dbench/autogen.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/dbench/child.c -->
# sources/test-tools/xfstests-bld/fstests-bld/dbench/child.c

Purpose: implements dbench/tbench child workload execution, parsing NetBench-style load files and dispatching operations to backend `nb_*` functions.

Important APIs and functions: static timing helpers `nb_target_rate`, `nb_time_reset`, `nb_time_delay`, `finish_op`, dispatch helper `child_op`, and exported `child_run(struct child_struct *child0, const char *loadfile)`.

Control flow: initializes client names, allocates token buffers, opens the load file, loops over workload lines forever until `child->done`, normalizes paths, tokenizes fields, validates status tokens, maps `client1` to per-client names, rate-limits or time-aligns operations, and dispatches commands such as `NTCreateX`, `Rename`, `Unlink`, `Deltree`, `Mkdir`, `ReadX`, `WriteX`, and `Flush`.

State and persistence: mutates shared `child_struct` fields including line count, bytes, timing, latency stats, cleanup flags, and per-operation counters. Backend operations mutate filesystem or socket state.

Dependencies and integration: included in both dbench and tbench builds with backend implementations from `fileio.c` or `sockio.c`. Uses global `options`.

Risks: fixed token buffer sizes and line length can truncate malformed workloads. Uses `goto again` for infinite replay and `goto done` for termination. Allocated token buffers are not freed before process exit.

Test signals: children execute workload lines, update operation latency counters, respect target rate/timestamps, and perform cleanup when stopped.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/dbench/child.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/dbench/configure.in -->
# sources/test-tools/xfstests-bld/fstests-bld/dbench/configure.in

Purpose: Autoconf input for configuring dbench portability features and Makefile generation.

Important APIs and functions: uses compiler/install/header checks, `_GNU_SOURCE` definition, library searches for `getxattr`, `socket`, and `gethostbyname`, extensive xattr/EA function checks, snprintf/asprintf checks, and `va_copy`/`__va_copy` probes.

Control flow: configures compiler flags, detects headers and functions, defines `HAVE_EA_SUPPORT` if any file-descriptor xattr API exists, defines `HAVE_VA_COPY` or `HAVE___VA_COPY`, then outputs `Makefile`.

State and persistence: generated artifacts include `configure`, `config.h`, and substituted `Makefile`.

Dependencies and integration: consumed by `autoconf`/`autoheader` and invoked by `build-all` before compiling dbench.

Risks: uses older Autoconf macros such as `AC_TRY_LINK`; modern Autoconf may warn. EA detection is broad and may enable code paths with partial platform support.

Test signals: configure completes, `config.h` reflects detected APIs, and dbench builds against the selected libraries.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/dbench/configure.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/dbench/dbench.c -->
# sources/test-tools/xfstests-bld/fstests-bld/dbench/dbench.c

Purpose: main process for dbench/tbench benchmark execution. It parses options, starts child worker processes, synchronizes launch, reports throughput and latency, and prints final results.

Important APIs and functions: global `struct options options`, static `open_loadfile`, `sem_cleanup`, `sig_alarm`, `show_one_latency`, `report_latencies`, `create_procs`, `show_usage`, `process_opts`, and `main`.

Control flow: `main` parses popt options, sets warmup, and calls `create_procs`. `create_procs` opens the load file, allocates shared memory for child structures, initializes a System V semaphore barrier, forks worker processes, waits until all are ready, releases the barrier, schedules periodic `SIGALRM` reports, waits for children, and prints latency summaries. `sig_alarm` handles warmup cutoff, timelimit stop, cleanup progress, throughput, and latency sampling.

State and persistence: uses shared memory for child metrics, a System V semaphore for launch synchronization, global timing values, and global `throughput`. Child workers mutate filesystem/socket state via `child_run`.

Dependencies and integration: depends on libpopt, dbench utility functions, `shm_setup`, backend `nb_*` operations, and `child.c`. Build-time macros provide `VERSION`, `DATADIR`, EA support, and TCP defaults.

Risks: signal handler performs substantial non-async-signal-safe work including `printf`. Semaphore creation test treats ID 0 as failure. Exit handling assumes `WEXITSTATUS` is meaningful without first checking normal exit.

Test signals: periodic output reports active clients and MB/sec, final throughput line includes client/process counts and max latency, and nonzero child exits fail the run.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/dbench/dbench.c -->
