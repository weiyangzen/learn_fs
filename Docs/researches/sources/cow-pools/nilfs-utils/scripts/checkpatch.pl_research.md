# File Research: sources/cow-pools/nilfs-utils/scripts/checkpatch.pl

## Purpose
`checkpatch.pl` is a NILFS-utils-adapted copy of Linux kernel `checkpatch.pl`, version `0.32`, used to check patch or source-file style. It reports typed errors, warnings, and optional strict checks, with experimental auto-fix support.

## Command-Line Interface
Important options:
- `--patch` / default: treat inputs as unified diffs.
- `-f` / `--file`: treat inputs as regular source files by running `diff -u /dev/null <file>`.
- `--tree`, `--root`: enable kernel-tree-aware checks.
- `--no-signoff`: skip Signed-off-by requirement.
- `--subjective` / `--strict`: enable extra `CHECK` diagnostics.
- `--types`, `--ignore`, `--show-types`: filter or label report types.
- `--max-line-length`
- `--min-conf-desc-length`
- `--fix`, `--fix-inplace`: experimental rewriting.
- `--ignore-perl-version`
- `--debug`
- `--test-only`
- `--quiet`, `--terse`, `--emacs`, `--summary`, `--mailback`.

## Configuration and Inputs
- Reads `.checkpatch.conf` from current directory, `$HOME`, or `.scripts`.
- Loads spelling corrections from `scripts/spelling.txt` relative to the script path when present.
- Requires Perl `5.10.0` for full regex-based checks, unless overridden.
- In file mode, opens a pipe to `diff -u /dev/null $filename`.
- In patch mode, reads each file or stdin into `@rawlines`, then processes each input independently.

## Main Processing Phases
1. Build large regex grammars for identifiers, types, attributes, constants, operators, declarations, and kernel annotations.
2. Optionally seed CamelCase exceptions from kernel include files.
3. Pre-scan input lines:
   - Track hunk line numbers.
   - Sanitize strings and comments into placeholders.
   - Preserve raw lines for exact output and fixes.
4. Process hunk and commit-log lines:
   - Maintain real file and real line state.
   - Track commit message versus patch body.
   - Annotate expression/operator context.
   - Emit typed reports.
5. Print report summary.
6. Optionally write experimental fixed output.

## Reporting Model
- `ERROR(type, msg)`: increments error count and marks input unclean.
- `WARN(type, msg)`: increments warning count and marks input unclean.
- `CHK(type, msg)`: emitted only in strict/check mode.
- Reports are filtered by `--types`, `--ignore`, and `--test-only`.
- `--emacs` changes prefixes to file/line style.

## Fix Mode
When `--fix` or `--fix-inplace` is enabled:
- The script tracks line replacements, insertions, and deletions.
- It can fix selected whitespace, brace, pointer, comment, spelling, macro, and API style issues.
- Non-inplace mode writes `<input>.EXPERIMENTAL-checkpatch-fixes`.
- The script explicitly warns not to trust generated fixes without inspection.

## Major Check Categories
Patch metadata:
- Missing or malformed Signed-off-by lines.
- Duplicate signatures.
- Non-standard signature tags.
- Commit ID formatting.
- Old stable address.
- Gerrit Change-Id.
- MAINTAINERS updates for added/moved/deleted files.
- UTF-8 and charset issues.
- Spelling mistakes.
- FSF mailing address boilerplate.

File and build metadata:
- Executable permissions on non-script source files.
- Kconfig help length and deprecated `EXPERIMENTAL`/`boolean`.
- Deprecated Makefile variables such as `EXTRA_CFLAGS`.
- Device tree compatible string documentation when tree context is available.
- Patch corruption/wrapping.

C and source style:
- Long lines.
- Missing EOF newline.
- Tabs, indentation, leading spaces, spaces before tabs.
- Parenthesis alignment and conditional indentation.
- Missing blank lines after declarations.
- Multiple blank lines.
- Switch/case indentation.
- Brace placement for functions, structs, unions, enums, `if`, `else`, `while`, and macros.
- C99 `//` comments.
- Spacing around operators, commas, semicolons, parentheses, brackets, and braces.
- Function pointer declaration spacing.
- Pointer `*` placement.
- Misordered C type specifiers.
- New typedefs.
- Function declarations without `void`.
- Multiple assignments.
- Assignment in conditionals.
- Trailing statements after conditionals/cases.
- Unnecessary parentheses.
- Return parentheses and void returns.
- Labels indentation.

Kernel/API-oriented checks:
- `printk` level usage and preference for `pr_*`/`dev_*`.
- Deprecated `DEFINE_PCI_DEVICE_TABLE`.
- `LINUX_VERSION_CODE`.
- `volatile`.
- `sizeof` misuse.
- `memset` suspicious arguments.
- Allocation patterns such as `kmalloc_array`, `kcalloc`, `krealloc` arg reuse.
- `sscanf` return checking and `kstrto*` preference.
- `jiffies` comparison helpers.
- Memory barriers and locks without comments.
- `__init` attribute placement.
- `__FUNCTION__`, `__DATE__`, `__TIME__`, `__TIMESTAMP__`.
- `yield`, `in_atomic`, lockdep misuse.
- World-writable debugfs/device attributes.
- Non-octal permission constants.

Macro checks:
- Multi-statement macros should use `do { } while (0)`.
- Complex macro values should be parenthesized.
- Single-statement `do while` macros are discouraged.
- Macro trailing semicolons.
- Flow control in macros.
- Unnecessary line continuations.
- `BIT()` macro preference for `1 << n`.

## NILFS-Utils Context
Although distributed with NILFS-utils, the script remains heavily kernel-oriented. Many checks reference kernel paths, APIs, docs, and conventions. In this repository it functions as a maintainer style gate for C patches, not as runtime NILFS functionality.

## Notable Risks and Edge Cases
- File mode invokes `diff` through a string pipe using the filename, so untrusted filenames could be problematic.
- Debug option handling uses `eval` on debug keys.
- Some tree-aware checks shell out to `git`, `find`, and `grep`.
- The grammar is regex-based and can produce false positives or miss complex C constructs.
- Advanced matching depends on Perl version.
- Experimental fixes can rewrite code incorrectly by design; the script warns about this.
