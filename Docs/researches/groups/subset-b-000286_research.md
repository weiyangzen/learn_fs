# Group Research: subset-b-000286

This grouped report covers the exact source files assigned to work item `subset-b-000286`. Each section is delimited for deterministic reconciliation into one source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/tests/test-lz4-abi.py -->
# sources/compression/lz4/tests/test-lz4-abi.py

## Purpose
This Python harness verifies dynamic-library ABI compatibility between the current LZ4 tree and historical tagged `liblz4` releases from v1.7.5 onward. It builds libraries for `-m64` and `-m32`, then exercises mismatched compile-time and run-time library combinations with `tests/abiTest`.

## Important APIs and Control Flow
The helper functions `proc()`, `make()`, `git()`, `get_git_tags()`, and `sha1_of_file()` wrap subprocess execution, build invocation, tag discovery, and file hashing. Main flow clones the upstream repository into `tests/abiTests/lz4`, checks out release tags into per-tag directories, builds `liblz4`, builds the current `abiTest`, and runs it under `LD_LIBRARY_PATH` pointing at each tested library. It then rebuilds `abiTest` against older headers/libs and runs against the current shared library.

## State, Dependencies, and Integration
Persistent state lives under `tests/abiTests`, including cloned source and built libraries. The script depends on `git`, `make`, C compiler multilib support, `check_liblz4_version.sh`, and `abiTest`. It mutates cwd heavily and exits on first subprocess failure.

## Risks and Test Signals
The test is Linux-oriented because it assumes shared-library naming, `LD_LIBRARY_PATH`, and `-m32`/`-m64`; macOS is only warned about. It gives strong ABI regression signals for old/current interop and ASan-enabled out-of-bounds checks, but is slow, network-dependent on first clone, and brittle when tags or toolchains are unavailable.
<!-- END_FILE_RESEARCH: sources/compression/lz4/tests/test-lz4-abi.py -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/tests/test-lz4-basic.sh -->
# sources/compression/lz4/tests/test-lz4-basic.sh

## Purpose
This shell test is broad CLI smoke coverage for `lz4`, `lz4cat`, and `unlz4`. It validates core compression/decompression, frame options, pass-through behavior, `--rm`, filename edge cases, multi-threading options, directory rejection, block checksum handling, and fast-compression parser edge cases.

## Important Control Flow
The script uses `set -e`, `set -x`, a `tmp-tlb` prefix, and an EXIT trap that removes temporary files. It streams `datagen` output through different `lz4` options, uses `diff`/`grep`/`test` for assertions, and intentionally expects some commands to fail with `&& exit 1`.

## State, Dependencies, and Integration
It relies on test binaries in PATH (`datagen`, `lz4`, `lz4cat`, `unlz4`) and a POSIX-like shell environment. Runtime state is entirely temporary files prefixed with `tmp-tlb`, including files whose names begin with `-` to exercise `--` option termination. It integrates with the LZ4 CLI regression suite rather than library APIs.

## Risks and Test Signals
The script catches high-value command-line regressions such as deleting inputs only when intended, refusing directories, rejecting invalid trailing data, preserving pass-through mode, and avoiding an out-of-bounds issue for very high `--fast` values. It is not isolated from PATH issues and contains a case-sensitive reference to `$FPREFIX-dg20K` while the generated file is `dg20k`, so behavior may depend on the intended failure path.
<!-- END_FILE_RESEARCH: sources/compression/lz4/tests/test-lz4-basic.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/tests/test-lz4-contentSize.sh -->
# sources/compression/lz4/tests/test-lz4-contentSize.sh

## Purpose
This shell test verifies when LZ4 frame content-size metadata is emitted and preserved. It distinguishes regular file input, redirection from a seekable file, and piped stdin where the size cannot be known.

## Important Control Flow
The script creates a 15 MiB deterministic file, compresses it with and without `--content-size`, decompresses to prove round-trip correctness, and compares compressed outputs to assert whether content-size metadata changed the frame. It uses `diff ... && exit 1` where two outputs must differ.

## State, Dependencies, and Integration
Temporary files use the `tmp-lzc` prefix and are removed on EXIT. Dependencies are `datagen`, `lz4`, `diff`, `cat`, and shell redirection semantics. This integrates with frame-header behavior in the `lz4` CLI and frame decoder.

## Risks and Test Signals
The key signal is that `--content-size` only works when the input size is discoverable. The test also confirms compatibility of frames with content size by decoding and comparing against the original. It does not inspect frame headers directly, so failures report via output equality rather than an explicit metadata parser.
<!-- END_FILE_RESEARCH: sources/compression/lz4/tests/test-lz4-contentSize.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/tests/test-lz4-dict.sh -->
# sources/compression/lz4/tests/test-lz4-dict.sh

## Purpose
This shell test validates dictionary compression/decompression behavior, including normal dictionaries, empty dictionaries, stdin-loaded dictionaries, and dictionary tail truncation to the last 64 KiB.

## Important Control Flow
It builds sample files with `datagen`, compresses using `lz4 -D`, decompresses with `lz4 -dD`, and compares streams with `diff`. It measures compressed sizes with and without a dictionary to ensure the dictionary improves compression for the generated corpus. A loop tests dictionary lengths around important boundaries from 0 through 131073 bytes and uses `dd` to generate the expected 64 KiB tail.

## State, Dependencies, and Integration
State is temporary `tmp-dict*` files. Dependencies include `datagen`, `lz4`, `dd`, `wc`, `diff`, and shell arithmetic. The script tests CLI dictionary plumbing and indirectly validates frame dictionary-id-independent decoding behavior when the same dictionary bytes are provided.

## Risks and Test Signals
Strong signals include round-trip correctness, dictionary effectiveness, zero-length dictionary handling, and boundary behavior around 32 KiB/64 KiB/128 KiB. The compression-efficiency assertion depends on deterministic generated data and may be sensitive to algorithm changes that are correct but less favorable for this corpus.
<!-- END_FILE_RESEARCH: sources/compression/lz4/tests/test-lz4-dict.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/tests/test-lz4-fast-hugefile.sh -->
# sources/compression/lz4/tests/test-lz4-fast-hugefile.sh

## Purpose
This shell test is huge-file coverage for fast LZ4 paths and sparse decompression. It exercises data sizes beyond 32-bit boundaries and verifies two sparse outputs generated through different content-size settings are equivalent.

## Important Control Flow
The script streams 6 GiB through `lz4 -vB5` and test mode, then creates two 3 GiB sparse decompressed files using `--sparse`, one without and one with `--content-size`. It compares the two outputs with `diff -s` and prints block allocation via `ls -ls`.

## State, Dependencies, and Integration
Temporary files use `tmp-lfh` and are removed on EXIT. It depends on `datagen`, `lz4`, `diff`, and enough filesystem support for sparse files. It targets the CLI and frame size handling, especially paths that process inputs larger than 2 GiB.

## Risks and Test Signals
The test is resource-heavy and can be unsuitable for small CI machines. It gives strong regression signals for integer overflow, content-size handling on large streams, and sparse output creation, but does not compare against a full non-sparse reference to avoid disk cost.
<!-- END_FILE_RESEARCH: sources/compression/lz4/tests/test-lz4-fast-hugefile.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/tests/test-lz4-frame-concatenation.sh -->
# sources/compression/lz4/tests/test-lz4-frame-concatenation.sh

## Purpose
This shell test confirms that `lz4 -d` decodes concatenated LZ4 frames, including an empty frame between non-empty frames, into the concatenation of their original payloads.

## Important Control Flow
It creates empty and non-empty source files, builds a reference concatenation, compresses each source independently, concatenates the compressed frames, decodes the combined stream to a result file, and compares with `cmp`.

## State, Dependencies, and Integration
State is limited to `tmp-lfc*` files. Dependencies are `lz4`, `cat`, `cmp`, and POSIX shell behavior. The test integrates with frame decoder stream traversal and EOF handling.

## Risks and Test Signals
The signal is narrow and valuable: decoders must continue after each complete frame and not mishandle zero-length frames. It does not cover skippable or legacy frames; those are handled by other tests in this subset.
<!-- END_FILE_RESEARCH: sources/compression/lz4/tests/test-lz4-frame-concatenation.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/tests/test-lz4-list.py -->
# sources/compression/lz4/tests/test-lz4-list.py

## Purpose
This Python unittest validates `lz4 --list` output for single-frame, multi-frame, legacy, skippable, content-size, checksum, and block-mode cases. It constructs a controlled corpus in the system temp directory and checks both non-verbose and verbose list formats.

## Important APIs and Control Flow
`NVerboseFileInfo` parses the seven-column non-verbose rows and computes expected compressed/uncompressed sizes. `VerboseFileInfo` parses per-frame verbose rows. `execute()` wraps subprocess calls, optionally prepending `QEMU_SYS`. `generate_files()` creates sparse-ish random test payloads, LZ4 frames with options such as `--content-size`, `-BI`, `-BD`, `-BX`, `--no-frame-crc`, hand-written skippable frames, legacy frames, and concatenated files. Two unittest classes assert frame counts, types, block descriptors, checksums, ratios, and human-readable sizes.

## State, Dependencies, and Integration
State is `/tmp/test_list*` and is removed before and after the run. Dependencies include Python `unittest`, `tempfile`, `glob`, `os.urandom`, and the built `lz4` binary from either `../lz4` or `../programs/lz4`. It directly tests CLI presentation and parser-visible frame metadata.

## Risks and Test Signals
This is strong output-format regression coverage, but brittle because it parses whitespace-delimited CLI output and assumes filenames without spaces. One assertion in verbose block testing compares against the literal regex string for `--BI`, which may be intentional legacy behavior or a test typo. Random payloads make sizes deterministic only in aggregate expectations, not by content.
<!-- END_FILE_RESEARCH: sources/compression/lz4/tests/test-lz4-list.py -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/tests/test-lz4-multiple-legacy.sh -->
# sources/compression/lz4/tests/test-lz4-multiple-legacy.sh

## Purpose
This shell test validates multi-file mode with legacy LZ4 format enabled by `-l`. It checks one-output-per-input behavior, stdout concatenation behavior, decompression behavior, and partial failure handling.

## Important Control Flow
The script generates three inputs, compresses with `lz4 -f -l -m`, verifies `.lz4` artifacts, restores originals from compressed files, and compares with `cmp`. It then compares concatenated individual compressed files with `lz4 -l -m ... -c`, and verifies decompression of multiple legacy files to stdout. A final command includes a missing file and expects failure while confirming later valid outputs may still be created.

## State, Dependencies, and Integration
State is `tmp-lml*`; dependencies are `datagen`, `lz4`, `cat`, `cmp`, `rm`, and shell globbing. It integrates with CLI multi-file dispatch, legacy frame codec selection, and error aggregation.

## Risks and Test Signals
The test confirms `-l` does not interfere with `-d` behavior and that `-c` suppresses file artifact creation. It is sensitive to shell glob ordering and to any change in the policy for whether multi-file processing continues after non-blocking errors.
<!-- END_FILE_RESEARCH: sources/compression/lz4/tests/test-lz4-multiple-legacy.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/tests/test-lz4-multiple.sh -->
# sources/compression/lz4/tests/test-lz4-multiple.sh

## Purpose
This shell test validates standard multi-file mode for compression, decompression, test mode, stdout concatenation, and missing-file failure behavior.

## Important Control Flow
It generates three inputs, compresses with `lz4 -f -m`, verifies per-file artifacts, deletes originals, decompresses back, and compares. It then verifies `-m ... -c` emits concatenated compressed output without creating artifacts, and `-d -m ... -c` emits concatenated plaintext. Test mode `lz4 -tm` is checked for one or multiple compressed files and must not create decompressed outputs. Missing input cases are expected to fail.

## State, Dependencies, and Integration
State is `tmp-tml*`. The test depends on `datagen`, `lz4`, `cmp`, `cat`, and glob expansion. It exercises command-line multi-file control flow rather than library APIs.

## Risks and Test Signals
It gives strong signals for artifact creation policy and test-mode non-mutating behavior. It assumes deterministic glob matches and does not inspect exit codes beyond shell `set -e` plus explicit `&& exit 1` failure expectations.
<!-- END_FILE_RESEARCH: sources/compression/lz4/tests/test-lz4-multiple.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/tests/test-lz4-opt-parser.sh -->
# sources/compression/lz4/tests/test-lz4-opt-parser.sh

## Purpose
This shell test targets compact option parsing for high compression levels and block-size/checksum combinations, especially combined forms such as `-12B4D`, `-11vq`, and `-12BD`.

## Important Control Flow
It streams deterministic `datagen` data of several sizes and probabilities through `lz4` with high-compression options, then pipes to `lz4 -t` or `lz4 -qt` for validation. There is no temporary file state.

## State, Dependencies, and Integration
Dependencies are `datagen`, `lz4`, and the shell pipeline. It integrates with the CLI option parser and high-compression codec modes.

## Risks and Test Signals
The test catches regressions where numeric compression levels, verbosity flags, block sizes, block dependency, and quiet test mode interact incorrectly. It is narrow: success only proves valid streams are produced, not exact compression ratios or parser diagnostics for invalid options.
<!-- END_FILE_RESEARCH: sources/compression/lz4/tests/test-lz4-opt-parser.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/tests/test-lz4-skippable.sh -->
# sources/compression/lz4/tests/test-lz4-skippable.sh

## Purpose
This shell test verifies decoder handling of LZ4 skippable frames using the golden sample `goldenSamples/skip.bin` and a constructed stream containing skippable frames around a valid frame.

## Important Control Flow
It decodes the golden skippable file both as a named file and from stdin. It then compresses a small valid payload, concatenates skippable-valid-skippable, and decodes the combined stream.

## State, Dependencies, and Integration
Temporary output uses the `tmp-lsk` prefix and is removed on EXIT. Dependencies are `lz4`, `printf`, `cat`, and the golden sample. The test integrates with frame decoder logic that must identify and skip skippable frame magic values.

## Risks and Test Signals
This is focused decoder coverage for ignoring skippable data without losing subsequent valid frames. It does not assert exact stdout contents via `cmp`, so regressions that still exit successfully but emit wrong data might be less obvious in automated logs.
<!-- END_FILE_RESEARCH: sources/compression/lz4/tests/test-lz4-skippable.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/tests/test-lz4-sparse.sh -->
# sources/compression/lz4/tests/test-lz4-sparse.sh

## Purpose
This shell test validates sparse decompression behavior, `--no-sparse`, console compatibility, and append-to-existing-output use cases.

## Important Control Flow
It generates all-zero-style data with `datagen -P100`, compresses with block sizes `B4D` through `B7D`, decompresses with `--sparse`, and compares each output. It checks an odd-sized sparse payload, then verifies stdin/stdout console paths and appending a decompressed stream with `>>` to create a doubled file reference.

## State, Dependencies, and Integration
Temporary files use `tmp-tls*`. Dependencies are `datagen`, `lz4`, `diff`, `ls`, `cat`, `printf`, and shell redirection. The test integrates with CLI file I/O, sparse write optimization, and frame options.

## Risks and Test Signals
The test is valuable for filesystem allocation and last-block edge cases, but sparse allocation effectiveness is only printed with `ls -ls`; correctness is checked by content diffs. It assumes the platform supports sparse file semantics well enough for the mode to run.
<!-- END_FILE_RESEARCH: sources/compression/lz4/tests/test-lz4-sparse.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/tests/test-lz4-speed.py -->
# sources/compression/lz4/tests/test-lz4-speed.py

## Purpose
This long-running Python daemon monitors LZ4 branch performance. It periodically fetches branches, builds GCC, 32-bit GCC, and Clang variants, benchmarks configured test files, compares against prior results, and emails warnings for speed or ratio regressions.

## Important APIs and Control Flow
Helpers include `execute()`, `does_command_exist()`, `send_email()`, `git_get_branches()`, `git_get_changes()`, `get_last_results()`, `benchmark_and_compare()`, `update_config_file()`, `double_check()`, and `test_commit()`. Main parsing requires test filenames and email recipients, validates mail tools, clones the repo into `speedTest/lz4`, creates a `speedTest.pid`, then loops forever based on load average and `sleepTime`. Each new branch commit is checked out, built, benchmarked with `programs/lz4 -rqi5b1e<level>`, recorded, and compared.

## State, Dependencies, and Integration
Persistent state includes cloned repo, commit marker files, result files, log files, email temp files, and pidfile under `speedTest`. Dependencies include `git`, `make`, GCC, Clang, `mutt` or `mail`, and benchmark input files. It integrates with the command-line benchmark output format and branch workflow.

## Risks and Test Signals
The script is intentionally operational, not a unit test. It uses `shell=True`, whitespace-split filename limitations, load-average gating, and persistent mutable files. It provides high-value performance regression signals but can loop indefinitely, send repeated emails, and fail noisily if toolchains or mail are missing.
<!-- END_FILE_RESEARCH: sources/compression/lz4/tests/test-lz4-speed.py -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/tests/test-lz4-testmode.sh -->
# sources/compression/lz4/tests/test-lz4-testmode.sh

## Purpose
This shell test validates benchmark decode-only mode, test-mode rejection of uncompressed input, pass-through behavior under force flags, and clean errors for missing sources.

## Important Control Flow
It runs `lz4 -bi0`, creates a compressed file, tests decode-only benchmark modes with and without CRC, then expects `lz4 -t` and `lz4 -tf` on generated raw data to fail. It creates plaintext `.lz4` and normal files to check pass-through failures/successes for `-dc`, `-df`, `-dcf`, and multi-file force mode. Missing-file commands must fail.

## State, Dependencies, and Integration
Temporary files use `tmp-ltm*`. Dependencies are `datagen`, `lz4`, shell redirection, and `test`-style exit checks. It exercises CLI mode selection and error paths.

## Risks and Test Signals
The script gives clear signals that test mode is not pass-through mode and that force changes pass-through semantics. It does not compare pass-through output contents except by successful execution and visible stdout.
<!-- END_FILE_RESEARCH: sources/compression/lz4/tests/test-lz4-testmode.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/tests/test-lz4-versions.py -->
# sources/compression/lz4/tests/test-lz4-versions.py

## Purpose
This Python harness validates file-format interoperability across historical `lz4c` and `lz4c32` releases. It builds each tagged command, compresses a reference file at multiple levels and word sizes, deduplicates equivalent compressed outputs, then decompresses every remaining artifact with every built decoder.

## Important APIs and Control Flow
`env_or_empty()`, `proc()`, `make()`, `git()`, `get_git_tags()`, and `sha1_of_file()` wrap environment-sensitive builds, command execution, tag discovery, and content hashing. Main flow clones upstream into `tests/versionsTest/lz4`, copies `README.md` as `test_dat`, builds `lz4c` and `lz4c32` for old `rNNN` and `vX.Y.Z` tags plus current head, creates compressed files, removes duplicates with `filecmp.cmp`, then verifies all decompressed files match `test_dat`.

## State, Dependencies, and Integration
Persistent state lives in `tests/versionsTest`, including built binaries, compressed samples, and decompressed outputs. Dependencies are `git`, `make`, working C compilers for 32-bit/64-bit variants, and historical source buildability. It integrates with the CLI file format and older command names.

## Risks and Test Signals
This is very strong backward/forward compatibility coverage, but expensive and network-dependent on first run. It assumes old tags build on the current host and that lexical tag collection is suitable. It exits on subprocess failure and cleans only selected generated outputs.
<!-- END_FILE_RESEARCH: sources/compression/lz4/tests/test-lz4-versions.py -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/tests/test-lz4hc-hugefile.sh -->
# sources/compression/lz4/tests/test-lz4hc-hugefile.sh

## Purpose
This minimal shell test exercises high-compression mode on a multi-gigabyte stream. It streams 4200 MB from `datagen` through `lz4 -v3` and validates with `lz4 -qt`.

## Important Control Flow
There is no temporary file state; the test is a single pipeline under `set -e` and `set -x`.

## State, Dependencies, and Integration
Dependencies are `datagen`, `lz4`, and a host capable of processing a 4.2 GB stream. It integrates with high-compression streaming and test-mode decoding.

## Risks and Test Signals
The signal targets large-size counters and high-compression stability. It is resource-heavy but disk-light because the data remains in a pipeline. It does not compare output ratios or persist artifacts for inspection.
<!-- END_FILE_RESEARCH: sources/compression/lz4/tests/test-lz4hc-hugefile.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/tests/test_custom_block_sizes.sh -->
# sources/compression/lz4/tests/test_custom_block_sizes.sh

## Purpose
This shell test validates custom `-B<size>` parsing and mapping to LZ4 frame block-size IDs. It verifies lower-bound rejection and expected block descriptor classes for sizes spanning all supported ranges.

## Important Control Flow
It creates two deterministic input files in `/tmp`, expects `-B31` to fail, then loops over ranges that should map to `b4`, `b5`, `b6`, and `b7`. For each size it compresses both inputs, concatenates the frames, and runs `checkFrame -B<effective-size> -b<id>` to validate headers. A `failures` string accumulates failing block sizes and determines exit status.

## State, Dependencies, and Integration
State is `/tmp/test_custom_block_sizes*`. Dependencies are `../lz4`, `./checkFrame`, `./datagen`, `cat`, and shell loops. It integrates with CLI parsing and the frame checker utility.

## Risks and Test Signals
The test is strong for boundary values like 65535/65536/65537 and for clamping above 4 MiB. Cleanup is manual at the end, so an early failure under `set -e` can leave `/tmp` artifacts. It assumes fixed relative paths from the tests directory.
<!-- END_FILE_RESEARCH: sources/compression/lz4/tests/test_custom_block_sizes.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/tests/test_install.sh -->
# sources/compression/lz4/tests/test_install.sh

## Purpose
This shell test checks that uppercase and lowercase Make install variables produce identical installation and uninstallation results. It covers variables such as `PREFIX`, `LIBDIR`, `BINDIR`, and man/pkg-config paths.

## Important Control Flow
The script selects `make` or `gmake` based on `uname`, then for `install` and `uninstall` loops over a variable list. For each variable it installs into two separate `DESTDIR` roots using uppercase and lowercase forms, compares the trees with `diff -r`, and after uninstall asserts the lowercase tree contains no files.

## State, Dependencies, and Integration
It depends on an external `lz4_root` environment variable, Make/gmake, `diff`, `find`, `tr`, and shell command substitution. Temporary roots are under the current directory as `tmp-lower-*` and `tmp-upper-*`.

## Risks and Test Signals
The test provides packaging compatibility signals for Makefile variable aliases. It is sensitive to missing `lz4_root`, platform-specific make selection, and install side effects. It compares entire trees, so benign metadata/order differences are not an issue but generated content differences fail.
<!-- END_FILE_RESEARCH: sources/compression/lz4/tests/test_install.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/tests/unicode_lint.sh -->
# sources/compression/lz4/tests/unicode_lint.sh

## Purpose
This Bash lint script enforces ASCII-only C and header sources under `lib/`, `programs/`, and `tests/`, addressing the policy described in LZ4 issue 1018.

## Important Control Flow
It initializes `pass=true`, then for each directory runs `find` for `*.c` and `*.h` files and `grep -P -n "[^\x00-\x7F]"`. Any result is printed with a `FAIL` marker and flips `pass=false`. The script exits 0 with a PASS message or 1 with FAIL.

## State, Dependencies, and Integration
There is no persistent state. Dependencies are Bash, `find`, and a `grep` implementation with PCRE `-P`. It integrates with style/portability checks rather than compression behavior.

## Risks and Test Signals
The lint strongly catches accidental non-ASCII source bytes but excludes shell, Python, docs, and other file types. It may fail on systems where `grep -P` is unavailable, making it less portable than the policy it enforces.
<!-- END_FILE_RESEARCH: sources/compression/lz4/tests/unicode_lint.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/.github/workflows/ci.yml -->
# sources/compression/xz/.github/workflows/ci.yml

## Purpose
This GitHub Actions workflow is the primary POSIX CI matrix for XZ Utils. It runs autotools and CMake builds on Ubuntu x86_64, Ubuntu ARM, and macOS, covering full builds and many feature-disabled configurations.

## Important Control Flow
The `POSIX` job installs dependencies conditionally for OS and build system, then repeatedly calls `./build-aux/ci_build.bash` for build and test phases. Special lanes cover 32-bit GCC, sanitizers, Valgrind, musl, full features, no encoders, no decoders, no threads, no BCJ, no Delta, reduced check algorithms, and small mode. Failed runs upload `build-aux/artifacts`.

## State, Dependencies, and Integration
The workflow depends on GitHub-hosted runners, package managers, autotools/CMake, gettext/po4a/doxygen, musl tools, Valgrind, and the shared `ci_build.bash` contract. Build state is placed outside the source tree in `../xz_build` by the wrapper.

## Risks and Test Signals
This workflow is the broadest automated signal for build-option compatibility. Risk areas include runner package drift, timeouts, and feature-matrix gaps on non-POSIX systems handled by separate workflows. Artifact upload on failure preserves test logs for diagnosis.
<!-- END_FILE_RESEARCH: sources/compression/xz/.github/workflows/ci.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/.github/workflows/cifuzz.yml -->
# sources/compression/xz/.github/workflows/cifuzz.yml

## Purpose
This workflow runs OSS-Fuzz CIFuzz for XZ on pushes to master and manual dispatch. It builds and runs fuzzers under address, undefined, and memory sanitizers.

## Important Control Flow
The single `CIFuzz` job uses a matrix over sanitizer values. It invokes `google/oss-fuzz/infra/cifuzz/actions/build_fuzzers@master`, then `run_fuzzers@master` for 600 seconds with timeout and OOM reporting. If fuzzing fails after a successful build, artifacts from `./out/artifacts` are uploaded.

## State, Dependencies, and Integration
State is produced by OSS-Fuzz action containers under the runner workspace. The workflow depends on the external OSS-Fuzz GitHub actions and the `xz` project definition in OSS-Fuzz, using `language: c++` to match that definition even though XZ is C.

## Risks and Test Signals
It gives high-value sanitizer-backed fuzz regression signals but depends on external action behavior and a relatively short fuzzing window. Pinning to `@master` increases exposure to upstream action changes.
<!-- END_FILE_RESEARCH: sources/compression/xz/.github/workflows/cifuzz.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/.github/workflows/coverity.yml -->
# sources/compression/xz/.github/workflows/coverity.yml

## Purpose
This workflow submits Coverity Scan analysis for the special `coverity_scan` branch. It builds an autotools debug configuration and hands the build command to a pinned Coverity action.

## Important Control Flow
The job checks out the repo, installs autotools and multilib dependencies, runs `./autogen.sh --no-po4a`, configures with `--enable-debug --disable-silent-rules`, appends `#define LZMA_RANGE_DECODER_CONFIG 0` to `config.h` to avoid known inline-assembly false positives, and invokes `vapier/coverity-scan-action`.

## State, Dependencies, and Integration
It depends on Ubuntu packages, repository secrets for Coverity email/token, generated autotools files, and Coverity's build capture. State includes generated configure outputs and modified `config.h` within the ephemeral runner.

## Risks and Test Signals
The workflow provides static-analysis coverage, not runtime validation. It is branch-gated and secret-dependent, so it will not run for ordinary PRs. The explicit inline assembly disablement trades analysis precision for fewer false positives.
<!-- END_FILE_RESEARCH: sources/compression/xz/.github/workflows/coverity.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/.github/workflows/dragonflybsd.yml -->
# sources/compression/xz/.github/workflows/dragonflybsd.yml

## Purpose
This workflow validates XZ on DragonFly BSD through a VM action. It covers autotools bootstrap, configure, and `make check` on a non-Linux BSD platform.

## Important Control Flow
The job runs on Ubuntu, checks out the repo, starts `vmactions/dragonflybsd-vm`, installs autotools/gettext/libtool/m4, runs `./autogen.sh --no-po4a`, configures debug + Werror with a strict-overflow warning suppression, and runs `make -j4 check`.

## State, Dependencies, and Integration
It depends on the pinned VM action, DragonFly package availability, and autotools. All state is inside the VM and runner workspace.

## Risks and Test Signals
The test gives platform-portability signal for DragonFly system APIs and compiler warnings. It has a tight 10-minute timeout and skips po4a, so translated man-page generation is not covered.
<!-- END_FILE_RESEARCH: sources/compression/xz/.github/workflows/dragonflybsd.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/.github/workflows/freebsd.yml -->
# sources/compression/xz/.github/workflows/freebsd.yml

## Purpose
This workflow validates XZ on FreeBSD VM releases. It runs autotools bootstrap, configure, and `make check` with debug and Werror.

## Important Control Flow
The matrix defines FreeBSD versions and architectures, then uses `vmactions/freebsd-vm` to install autotools, gettext, libtool, m4, and po4a. The VM runs `./autogen.sh`, `./configure --disable-static --enable-debug --enable-werror`, and `make -j4 check`.

## State, Dependencies, and Integration
Dependencies are the pinned FreeBSD VM action and FreeBSD packages. It integrates with autotools build logic, translated manpage generation through po4a, and the test suite.

## Risks and Test Signals
The matrix currently references `matrix.release` while entries define `version`, which is a workflow risk unless the action defaults compensate. The job is valuable for Capsicum, sysctl, and BSD portability, but constrained by a 10-minute timeout.
<!-- END_FILE_RESEARCH: sources/compression/xz/.github/workflows/freebsd.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/.github/workflows/haiku.yml -->
# sources/compression/xz/.github/workflows/haiku.yml

## Purpose
This workflow validates XZ on Haiku through a VM action, covering autotools generation and test execution on a less common target OS.

## Important Control Flow
The job checks out the repo, starts `vmactions/haiku-vm`, installs autotools/gettext/libtool/m4 with `pkgman`, runs `./autogen.sh --no-po4a`, configures `--disable-static --enable-debug --enable-werror`, and executes `make -j4 check`.

## State, Dependencies, and Integration
State is ephemeral in the VM. Dependencies are the pinned Haiku VM action and Haiku package availability. It integrates with autotools portability and core test execution.

## Risks and Test Signals
This provides useful non-POSIX-edge portability signal but skips po4a and has a short timeout. Failures may reflect VM/package drift as much as source regressions.
<!-- END_FILE_RESEARCH: sources/compression/xz/.github/workflows/haiku.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/.github/workflows/msvc.yml -->
# sources/compression/xz/.github/workflows/msvc.yml

## Purpose
This workflow validates CMake builds with Microsoft Visual C++ and ClangCL on Windows. It covers Win32 and x64 Debug/Release configurations.

## Important Control Flow
The `MSVC` job checks out the repo, configures a Win32 build, builds/tests Debug and Release with `ctest`, repeats for x64, then configures `-T ClangCL -A x64` and tests Debug/Release. All builds use CMake's multi-config generator semantics.

## State, Dependencies, and Integration
Build directories are `build-msvc-win32`, `build-msvc-x64`, and `build-clangcl-x64`. Dependencies are Windows GitHub runners, Visual Studio CMake generators, CTest, and the top-level `CMakeLists.txt`.

## Risks and Test Signals
This is the main native Windows/MSVC signal for resource files, DLL/import library naming, manifests, and compiler compatibility. It does not exercise autotools or MSYS2 shell behavior; those are handled by the MSYS2 workflow.
<!-- END_FILE_RESEARCH: sources/compression/xz/.github/workflows/msvc.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/.github/workflows/msys2.yml -->
# sources/compression/xz/.github/workflows/msys2.yml

## Purpose
This workflow validates XZ under MSYS2 environments, covering both CMake and autotools builds across mingw32, ucrt64, clang64, msys, and clangarm64.

## Important Control Flow
The matrix chooses runner and MSYS2 system. Setup differs for `msys` versus mingw-like systems, then Git is configured to avoid CRLF conversion. The workflow runs CMake full shared, CMake small static on `windows-latest`, `autogen.sh --no-po4a`, autotools full shared, and autotools small static on `windows-latest`. On failure it uploads CTest and autotools logs.

## State, Dependencies, and Integration
State is in build directories `b-cmake-*` and `b-autotools-*`. Dependencies include `msys2/setup-msys2`, pacboy packages, Ninja, CMake, autotools, gettext, and a shell default of `msys2 {0}`. It exercises Windows/POSIX compatibility paths in both build systems.

## Risks and Test Signals
This workflow is high-value for path, symlink, CRLF, MinGW, UCRT, clang, and ARM64 Windows coverage. Risks include action version drift, package changes, and differences between MSYS and native Windows behavior.
<!-- END_FILE_RESEARCH: sources/compression/xz/.github/workflows/msys2.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/.github/workflows/netbsd.yml -->
# sources/compression/xz/.github/workflows/netbsd.yml

## Purpose
This workflow validates the CMake/Ninja build on NetBSD. It emphasizes generated translations and compiler-warning cleanliness on a BSD platform.

## Important Control Flow
The job checks out the repo, starts `vmactions/netbsd-vm`, installs CMake/gettext/ninja/po4a, runs `./po4a/update-po`, configures CMake with shared libs, debug-like C flags, Werror, and a strict-overflow warning suppression, then runs Ninja and CTest.

## State, Dependencies, and Integration
Dependencies are the pinned NetBSD VM action and packages. It integrates with CMake feature probes, gettext/po4a assets, Ninja build generation, and CTest.

## Risks and Test Signals
It provides signal for NetBSD headers, sysctl/proc detection, and translated man-page generation. It is CMake-only and limited by a 10-minute timeout.
<!-- END_FILE_RESEARCH: sources/compression/xz/.github/workflows/netbsd.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/.github/workflows/openbsd.yml -->
# sources/compression/xz/.github/workflows/openbsd.yml

## Purpose
This workflow validates XZ on OpenBSD using autotools. It is especially relevant for pledge sandboxing, OpenBSD SHA-256 interfaces, and autoconf/automake versioned tooling.

## Important Control Flow
The job starts `vmactions/openbsd-vm`, installs versioned autoconf and automake plus gettext/libtool/m4, exports `AUTOCONF_VERSION` and `AUTOMAKE_VERSION`, runs `./autogen.sh --no-po4a`, configures debug + Werror with `--disable-nls --enable-external-sha256`, and runs `make -j4 check`.

## State, Dependencies, and Integration
Dependencies include pinned VM action and OpenBSD packages. State is ephemeral. It integrates with autotools and platform feature detection for external SHA and sandboxing.

## Risks and Test Signals
This is strong OpenBSD portability coverage but skips NLS and po4a. External SHA-256 makes it sensitive to OS crypto API changes.
<!-- END_FILE_RESEARCH: sources/compression/xz/.github/workflows/openbsd.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/.github/workflows/solaris.yml -->
# sources/compression/xz/.github/workflows/solaris.yml

## Purpose
This workflow validates XZ on Solaris 11.4 with GCC through a VM action. It covers autotools bootstrap, configure, and test execution on Solaris-specific libc and shell paths.

## Important Control Flow
The job checks out the repo, runs `vmactions/solaris-vm`, prints `uname`, notes PATH because `/usr/xpg4/bin` is not default, runs `./autogen.sh --no-po4a`, configures debug + Werror without static libraries, and runs `make check`.

## State, Dependencies, and Integration
Dependencies are the pinned Solaris VM action and the image's preinstalled tools. It integrates with autotools and Solaris portability code such as system extension macros and possible `librt` use.

## Risks and Test Signals
The workflow gives valuable Solaris build/test signal but has no explicit package installation step, so image drift matters. It also skips po4a and has a 10-minute timeout.
<!-- END_FILE_RESEARCH: sources/compression/xz/.github/workflows/solaris.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/CMakeLists.txt -->
# sources/compression/xz/CMakeLists.txt

## Purpose
This is the top-level CMake build for XZ Utils. It configures package metadata, system feature probes, liblzma build composition, command-line tools, scripts, documentation, installation components, package config files, and optional tests.

## Important APIs, Options, and Functions
Important options include `BUILD_SHARED_LIBS`, `XZ_SYMBOL_VERSIONING`, `XZ_THREADS`, `XZ_SMALL`, `XZ_CHECKS`, `XZ_EXTERNAL_SHA256`, `XZ_MATCH_FINDERS`, `XZ_ENCODERS`, `XZ_DECODERS`, `XZ_MICROLZMA_ENCODER`, `XZ_MICROLZMA_DECODER`, `XZ_LZIP_DECODER`, `XZ_SANDBOX`, tool toggles, `XZ_NLS`, `XZ_DOC`, and `XZ_DOXYGEN`. Helper functions `my_install_symlinks()`, `my_install_man_lang()`, and `my_install_man()` centralize install-time symlink and man-page behavior. It imports tuklib CMake modules for large-file, integer, CPU core, physical memory, program-name, and multibyte-string detection.

## Control Flow and State
Configuration reads `version.h`, starts the `xz` C project, normalizes Release optimization, rejects old MSVC, sets common compile definitions, detects system extensions and platform APIs, then constructs `liblzma` incrementally from selected checks, match finders, encoders, decoders, threading, CRC acceleration, SHA implementation, symbol visibility, Windows resources, and symbol version scripts. It generates `liblzma-config*.cmake` and `liblzma.pc`, defines optional command tools (`xz`, `xzdec`, `lzmadec`, `lzmainfo`), configures scripts, installs docs, and includes `tests/tests.cmake` if present.

## Dependencies and Integration
The file depends on CMake 3.20+, GNUInstallDirs, CMake package helpers, C compiler/linker feature checks, gettext/Intl for NLS, Threads, platform SDK headers, and the repository's `src/`, `lib/`, `po/`, `po4a/`, `doc/`, `doxygen/`, and `tests/` trees. It is a peer to the autotools build, so option parity and installed ABI/package metadata are critical integration points.

## Risks and Test Signals
Risk concentrates in option interactions: disabled encoders/decoders must remove dependent formats, Landlock conflicts with sanitizers, Win95 threads plus small mode require constructor support, and symbol versioning must match platform/linker support. The CI matrix exercises many combinations through this file, including Windows, MSYS2, BSD, musl, sanitizers, and feature-disabled builds.
<!-- END_FILE_RESEARCH: sources/compression/xz/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/Makefile.am -->
# sources/compression/xz/Makefile.am

## Purpose
This Automake top-level file controls distribution content, documentation packaging, man-page conversion, release tarball generation, and top-level subdirectory traversal for the autotools build.

## Important Targets and Variables
It sets `GZIP_ENV=-9n`, `DIST_SUBDIRS`, conditional `SUBDIRS`, documentation and example install lists, `EXTRA_DIST`, `ACLOCAL_AMFLAGS`, and `manfiles`. `dist-hook` generates `ChangeLog`, converts man pages to ASCII text via `build-aux/manconv.sh`, and runs `license-check.sh`. `mydist` validates the liblzma map, updates translations, optionally derives a snapshot version from `git describe`, runs license checks, and creates a sorted owner-normalized gzip dist. `pdf-local` creates A4 and letter PDFs from man pages.

## State, Dependencies, and Integration
It depends on Automake conditionals such as `COND_GNULIB` and `COND_DOC`, `git`, `groff`, `po4a`, Make recursion, and build-aux scripts. Generated state includes distribution directories, `ChangeLog`, text/PDF man pages, and tarballs.

## Risks and Test Signals
This file is central to release reproducibility and packaging completeness. Risks include missing tools silently skipping some artifacts, stale translation generation, and license-check failures late in packaging. The `mydist` target is a strong release gate because it runs validation before `dist-gzip`.
<!-- END_FILE_RESEARCH: sources/compression/xz/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/autogen.sh -->
# sources/compression/xz/autogen.sh

## Purpose
This script bootstraps the autotools build files from a source checkout and optionally generates translated man pages with po4a.

## Important Control Flow
Under `set -e -x`, it runs `autopoint`, `libtoolize` or `glibtoolize`, `aclocal -I m4`, `autoconf`, `autoheader`, and `automake -acf --foreign`. It parses `--no-po4a` to skip translated man-page generation; otherwise it enters `po4a` and runs `sh update-po`.

## State, Dependencies, and Integration
The script generates or updates `configure`, `Makefile.in`, gettext infrastructure, libtool files, and po4a outputs. Dependencies are GNU autotools, gettext autopoint, libtoolize/glibtoolize, and optionally po4a. Many CI workflows call this before autotools configure.

## Risks and Test Signals
The script is intentionally simple and fail-fast. Tool version differences can change generated files, while `--no-po4a` is important for platforms lacking po4a. It has no cleanup behavior and assumes it is run from the repository root.
<!-- END_FILE_RESEARCH: sources/compression/xz/autogen.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/build-aux/ci_build.bash -->
# sources/compression/xz/build-aux/ci_build.bash

## Purpose
This Bash wrapper normalizes POSIX CI builds for autotools and CMake. It converts concise feature flags into configure/CMake options, separates build and test phases, and collects logs on failure.

## Important APIs and Control Flow
CLI options choose autogen flags, build system, checks, disabled features, CFLAGS, destination dir, compiler, artifacts subdir, phase, source dir, and a test wrapper. Helpers `add_extra_option()` and `add_to_filter_list()` build option strings. Build phase validates checksum names, computes separators for autotools versus CMake, generates configure when needed, configures/builds with selected encoders/decoders/filters/threading/shared/NLS/small/CLMUL/sandbox/doxygen settings, and handles an x32 config.guess workaround. Test phase runs `make check` or CMake `test`, copying logs to `build-aux/artifacts/<name>` on failure.

## State, Dependencies, and Integration
Default build state goes to `../xz_build`; source is `build-aux/../`. Dependencies include Bash, autotools or CMake, make, compiler toolchains, and optional wrappers like Valgrind. GitHub POSIX CI uses this script heavily.

## Risks and Test Signals
It is a key integration contract between CI YAML and build systems. Risks include string-built option quoting, stale CMake cache handling, and partial option parity between autotools and CMake. Its artifact-copying behavior improves failure diagnosis.
<!-- END_FILE_RESEARCH: sources/compression/xz/build-aux/ci_build.bash -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/build-aux/license-check.sh -->
# sources/compression/xz/build-aux/license-check.sh

## Purpose
This shell script checks for files lacking clear license information. It is not full REUSE compliance; instead it enforces project-specific SPDX and intentionally untagged file allowlists.

## Important Control Flow
It accepts optional `-v`, sets `LC_ALL=C`, defines regex allowlists for SPDX-tagged, intentionally untagged 0BSD/misc files, and generated tarball files. It gets the file list from `git ls-files` when possible, otherwise from `find`, detects files containing `SPDX-License-Identifier:`, splits 0BSD and non-0BSD tagged files, removes allowlisted untagged files and old public-domain `.po` translations, optionally reports all categories, and exits 1 if any unknown files remain.

## State, Dependencies, and Integration
The script changes to the repository root. Dependencies include POSIX shell tools plus non-POSIX `xargs -0`, `grep`, `sort`, `uniq`, `sed`, and optionally `git`. It is used by `Makefile.am` distribution hooks and `mydist`.

## Risks and Test Signals
This is a release hygiene gate. It can miss semantic license problems in allowlisted files but catches new files without SPDX tags. Tarball mode intentionally ignores generated files, so it relies on a clean extracted tree.
<!-- END_FILE_RESEARCH: sources/compression/xz/build-aux/license-check.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/build-aux/manconv.sh -->
# sources/compression/xz/build-aux/manconv.sh

## Purpose
This wrapper converts groff man-page input to ASCII, UTF-8, PostScript, or PDF, with consistent font and paragraph spacing for print formats.

## Important Control Flow
It reads `FORMAT` and optional `PAPER` arguments, defines `FONT=11`, `PD=0.8`, and a `sed` script that injects or normalizes `.PD`. A case statement pipes stdin through `groff -t -mandoc` and `col -bx` for text formats, or through `groff -Tps` and optionally `ps2pdf` for PDF. Unknown formats exit 1.

## State, Dependencies, and Integration
There is no persistent state; all content streams through stdin/stdout. Dependencies are `groff`, `col`, `sed`, and `ps2pdf` for PDFs. `Makefile.am` uses it in `dist-hook` and `pdf-local`.

## Risks and Test Signals
The script centralizes doc conversion behavior but assumes GNU-ish groff tooling. Errors surface during distribution or PDF targets rather than normal builds.
<!-- END_FILE_RESEARCH: sources/compression/xz/build-aux/manconv.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/build-aux/version.sh -->
# sources/compression/xz/build-aux/version.sh

## Purpose
This shell script extracts the XZ/liblzma version string from `src/liblzma/api/lzma/version.h` without a trailing newline, for use by `configure.ac`.

## Important Control Flow
A `sed -n` program maps stability macros to `alpha`, `beta`, or empty, extracts major/minor/patch/stability define values, then a second `sed` joins four lines into dotted form with the stability suffix. `tr` removes newline, carriage return, and a control byte.

## State, Dependencies, and Integration
It is a pure read/print helper depending on `sed` and `tr`. It integrates autotools version generation with the canonical C API version header.

## Risks and Test Signals
The script is brittle to formatting changes in `version.h`; macro naming or ordering changes would break extraction. Its value is avoiding duplicated version constants.
<!-- END_FILE_RESEARCH: sources/compression/xz/build-aux/version.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/cmake/remove-ordinals.cmake -->
# sources/compression/xz/cmake/remove-ordinals.cmake

## Purpose
This CMake script removes ordinal annotations from Windows DEF files generated by GNU ld or LLVM lld. It prevents consumers from linking by unstable ordinal numbers.

## Important Control Flow
It expects `INPUT_FILE` and `OUTPUT_FILE` definitions, reads the input into `STR`, applies `string(REGEX REPLACE " +@ *[0-9]+" "" ...)`, and writes the cleaned output.

## State, Dependencies, and Integration
It is invoked as a post-build command from `CMakeLists.txt` when building shared `liblzma` on non-MSVC Windows toolchains. It consumes `liblzma.def.in` and produces `liblzma.def`.

## Risks and Test Signals
The logic is intentionally narrow and equivalent to a simple sed expression. It assumes ordinal patterns do not appear in legitimate symbol names or comments. CI Windows/MSYS2 shared builds exercise this path.
<!-- END_FILE_RESEARCH: sources/compression/xz/cmake/remove-ordinals.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/cmake/tuklib_common.cmake -->
# sources/compression/xz/cmake/tuklib_common.cmake

## Purpose
This module provides shared helpers for the CMake versions of tuklib feature detection modules.

## Important APIs and Control Flow
`tuklib_add_definitions(TARGET_OR_ALL DEFINITIONS)` adds compile definitions either globally via `add_compile_definitions()` when passed `ALL`, or privately to a named target. `tuklib_add_definition_if(TARGET_OR_ALL VAR)` adds a definition only when the CMake variable evaluates true. `tuklib_use_system_extensions()` is a macro that adds common feature-test macros such as `_GNU_SOURCE`, `_DARWIN_C_SOURCE`, `_ALL_SOURCE`, and Solaris/NetBSD/OpenBSD variants, and appends matching `-D` entries to `CMAKE_REQUIRED_DEFINITIONS`.

## State, Dependencies, and Integration
It mutates global compile definitions and CMake check state. It is included by other `tuklib_*.cmake` modules and top-level `CMakeLists.txt`.

## Risks and Test Signals
Because system-extension macros affect feature checks and target compilation, ordering matters. The macro intentionally avoids MSVC. Cross-platform CI provides signal that these definitions expose needed APIs without breaking system headers.
<!-- END_FILE_RESEARCH: sources/compression/xz/cmake/tuklib_common.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/cmake/tuklib_cpucores.cmake -->
# sources/compression/xz/cmake/tuklib_cpucores.cmake

## Purpose
This module detects how tuklib should determine available CPU cores and applies the corresponding compile definitions.

## Important APIs and Control Flow
`tuklib_cpucores_internal_check()` tries platform methods in order: Windows/Cygwin handled in C, glibc `sched_getaffinity` with `CPU_COUNT`, FreeBSD `cpuset_getaffinity`, BSD `sysctl` excluding QNX, `sysconf`, and HP-UX `pstat_getdynamic`. It caches `TUKLIB_CPUCORES_DEFINITIONS`. `tuklib_cpucores(TARGET_OR_ALL)` runs detection once, caches `TUKLIB_CPUCORES_FOUND`, warns if none found, and adds definitions to a target or globally.

## State, Dependencies, and Integration
The module uses `CheckCSourceCompiles`, `CheckIncludeFile`, `CMakePushCheckState`, and `tuklib_common.cmake`. Results are CMake internal cache variables consumed by `src/common/tuklib_cpucores.c`.

## Risks and Test Signals
Detection ordering is important because some APIs compile but are wrong on specific systems. The top-level CMake build treats failure as a hard error for expected platforms, so CI across Linux, BSDs, macOS, Windows, and Solaris is meaningful coverage.
<!-- END_FILE_RESEARCH: sources/compression/xz/cmake/tuklib_cpucores.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/cmake/tuklib_integer.cmake -->
# sources/compression/xz/cmake/tuklib_integer.cmake

## Purpose
This module configures integer portability and optimization macros: endianness, byte swapping, fast unaligned access, unsafe type punning, and compiler alignment intrinsics.

## Important APIs and Control Flow
`tuklib_integer_internal_strict_align(OBJDUMP_REGEX)` compiles a static-library probe, disassembles it with `CMAKE_OBJDUMP`, and infers strict alignment from byte-load instruction patterns. `tuklib_integer(TARGET_OR_ALL)` uses `test_big_endian`, checks builtin byte-swap support or headers like `byteswap.h`, `sys/endian.h`, and `sys/byteorder.h`, then estimates `TUKLIB_FAST_UNALIGNED_ACCESS` from processor names and compiler macros for x86, PowerPC, ARM, ARM64, RISC-V, and LoongArch. It also exposes `TUKLIB_USE_UNSAFE_TYPE_PUNNING` and checks `__builtin_assume_aligned`.

## State, Dependencies, and Integration
It mutates target/global definitions and CMake cache options. Dependencies are CMake check modules, an object dump tool, and compile probes. It feeds low-level integer access code in tuklib and liblzma hot paths.

## Risks and Test Signals
This is performance- and correctness-sensitive: wrong unaligned-access detection can cause crashes or slow code. The ARM64/GCC and LoongArch heuristic paths are especially subtle. Cross-architecture CI, including ARM runners/MSYS2 ARM, helps validate assumptions.
<!-- END_FILE_RESEARCH: sources/compression/xz/cmake/tuklib_integer.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/cmake/tuklib_large_file_support.cmake -->
# sources/compression/xz/cmake/tuklib_large_file_support.cmake

## Purpose
This module adds large-file support for platforms where `off_t` is smaller than 64 bits by default but becomes 64-bit with `_FILE_OFFSET_BITS=64`.

## Important Control Flow
`tuklib_large_file_support(TARGET_OR_ALL)` returns immediately for MSVC. It compiles a probe requiring `sizeof(off_t) >= 8`; if that fails, it repeats with `-D_FILE_OFFSET_BITS=64`. When the second probe succeeds, it exposes the `LARGE_FILE_SUPPORT` option defaulting ON and adds `_FILE_OFFSET_BITS=64` when enabled.

## State, Dependencies, and Integration
It uses `CheckCSourceCompiles`, `CMakePushCheckState`, and `tuklib_common.cmake`. It is called globally near the start of `CMakeLists.txt` so all targets and later checks see consistent file-offset behavior.

## Risks and Test Signals
Incorrect detection could break files larger than 2 GiB, especially on 32-bit platforms and MinGW-w64. CI lanes for 32-bit and large-file tests in related suites provide indirect coverage.
<!-- END_FILE_RESEARCH: sources/compression/xz/cmake/tuklib_large_file_support.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/cmake/tuklib_mbstr.cmake -->
# sources/compression/xz/cmake/tuklib_mbstr.cmake

## Purpose
This module detects multibyte and formatting helper functions used by tuklib command-line presentation code.

## Important Control Flow
`tuklib_mbstr(TARGET_OR_ALL)` checks for `mbrtowc` and `wcwidth` in `wchar.h`, and `vasprintf` in `stdio.h`, adding `HAVE_MBRTOWC`, `HAVE_WCWIDTH`, and `HAVE_VASPRINTF` definitions when present.

## State, Dependencies, and Integration
It uses `CheckSymbolExists` and `tuklib_common.cmake`. It is applied to tools like `xz`, `xzdec`, and `lzmainfo`, where display width and printable string handling matter.

## Risks and Test Signals
Feature-test macro ordering matters because `wcwidth` and `vasprintf` require extension macros on some systems. The module relies on `tuklib_use_system_extensions()` having been called earlier in the top-level build.
<!-- END_FILE_RESEARCH: sources/compression/xz/cmake/tuklib_mbstr.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/cmake/tuklib_physmem.cmake -->
# sources/compression/xz/cmake/tuklib_physmem.cmake

## Purpose
This module detects how tuklib should determine total physical memory and applies compile definitions for the selected method.

## Important APIs and Control Flow
`tuklib_physmem_internal_check()` first handles Windows/Cygwin and other special platforms in C, then probes AIX `_system_configuration.physmem`, POSIX `sysconf(_SC_PAGESIZE/_SC_PHYS_PAGES)`, BSD `sysctl(CTL_HW, HW_PHYSMEM)`, and HP-UX `pstat_getstatic`. `tuklib_physmem(TARGET_OR_ALL)` caches found status and applies `TUKLIB_PHYSMEM_*` and `HAVE_SYS_PARAM_H` definitions.

## State, Dependencies, and Integration
It uses CMake compile checks, include checks, push/pop check state, and `tuklib_common.cmake`. Results drive `src/common/tuklib_physmem.c` and liblzma APIs such as `lzma_physmem()`.

## Risks and Test Signals
The module intentionally lacks some Autotools checks, such as Tru64, IRIX, and Linux `sysinfo()`, preferring `sysconf()` on GNU/Linux. Top-level CMake treats missing detection as an error for expected platforms, so portability workflows are the main signal.
<!-- END_FILE_RESEARCH: sources/compression/xz/cmake/tuklib_physmem.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/cmake/tuklib_progname.cmake -->
# sources/compression/xz/cmake/tuklib_progname.cmake

## Purpose
This module detects support for obtaining the program invocation name through a glibc extension.

## Important Control Flow
`tuklib_progname(TARGET_OR_ALL)` checks whether `program_invocation_name` exists in `errno.h` and adds `HAVE_PROGRAM_INVOCATION_NAME` when available.

## State, Dependencies, and Integration
It uses `CheckSymbolExists` and `tuklib_common.cmake`. The top-level build applies it to command-line tools that use `src/common/tuklib_progname.c`.

## Risks and Test Signals
The symbol requires `_GNU_SOURCE` on glibc, so this module depends on prior system-extension setup. If unavailable, C code must use fallback program-name handling.
<!-- END_FILE_RESEARCH: sources/compression/xz/cmake/tuklib_progname.cmake -->
