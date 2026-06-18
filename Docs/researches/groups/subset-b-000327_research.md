# subset-b-000327 research

Grouped research report for the exact subset-b-000327 source manifest. Each section is delimited for deterministic splitting into the source-tree-aligned `Docs/researches/<source_path>_research.md` artifacts.

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/compression/levels.sh -->
# sources/compression/zstd/tests/cli-tests/compression/levels.sh

## Purpose
This CLI regression test validates zstd compression level parsing and level semantics. It checks fast levels, regular levels, `--max`, default level behavior, oversized level rejection, environment-provided `ZSTD_CLEVEL`, and command-line override precedence.

## APIs, control flow, and integration
The script uses the CLI test harness environment where `datagen`, `zstd`, `cmp_size`, and `die` are on `PATH` or sourced by common setup. It generates `file`, captures `zstd -V`, compresses at `--fast=10`, `--fast=1`, `-1`, `-19`, and conditionally `--max`, then validates all outputs with `zstd -t`. Size ordering is asserted with `cmp_size`, and byte equality is asserted with `cmp`. The script then checks aliases/defaults: bare `--fast` must equal `--fast=1`, `-0` must equal default `zstd`, and `-99` must clamp to `-19`.

## State, persistence, dependencies, and risks
All state is scratch-local: `file` and multiple `file-*.zst` outputs. The 32-bit version check avoids `--max` address-space failure by copying the `-19` output. The test depends on deterministic output for identical level options and on generated input being compressible enough for monotonic size comparisons. Risks are platform/version wording in `zstd -V`, future compression tuning changing strict size ordering, and environment leakage; `run.py` normally strips `ZSTD*` variables, but this script intentionally sets `ZSTD_CLEVEL` for individual commands.

## Test signals
Pass signals are successful decompression tests, monotonic compressed sizes, exact output equality for level aliases and env selection, nonzero failure for too-large numeric levels, and command-line level overriding `ZSTD_CLEVEL`.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/compression/levels.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/compression/long-distance-matcher.sh -->
# sources/compression/zstd/tests/cli-tests/compression/long-distance-matcher.sh

## Purpose
This short CLI test exercises long-distance matching options in the compressor.

## APIs, control flow, and integration
It assumes `compression/setup` has created `file`. The script runs `zstd -f file --long` and `zstd -f file --long=20`, then validates the produced `file.zst` with `zstd -t` after each command. It uses only CLI entry points and the shell harness `set -e` failure model.

## State, dependencies, risks, and test signals
The only persistent scratch artifact is overwritten `file.zst`. The test depends on the built zstd supporting long-distance mode and on default memory limits being sufficient for `--long=20`. A pass confirms the option parser accepts both forms and the resulting frames decompress successfully.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/compression/long-distance-matcher.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/compression/multi-threaded.sh -->
# sources/compression/zstd/tests/cli-tests/compression/multi-threaded.sh

## Purpose
This test covers multi-threaded compression flags, rsyncable mode, automatic thread selection, job size configuration, and decompression warning behavior for explicit versus environment-sourced thread counts.

## APIs, control flow, and integration
Using `file` from setup, it runs compression with `--single-thread`, `-T2`, `--rsyncable`, `-T0`, `--auto-threads=logical`, `--auto-threads=physical`, and `--jobsize=1M`, testing each generated frame with `zstd -t`. It then compresses again and invokes decompression with explicit `-T0`, `-T2`, env `ZSTD_NBTHREADS=0/2`, and explicit `-T1` combinations to exercise warning/no-warning paths. The script relies on expectation files owned by the CLI harness for stderr matching.

## State, dependencies, risks, and test signals
Scratch outputs include `file.zst`, `file3`, and `file4`. Dependencies include multi-threading support in the binary and harness-provided stdout/stderr checks. Main risks are builds without thread support, platform CPU-count differences for `-T0`, and stderr wording churn. The functional signal is successful decompression; the behavioral signal is expected diagnostics under the runner.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/compression/multi-threaded.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/compression/multiple-files.sh -->
# sources/compression/zstd/tests/cli-tests/compression/multiple-files.sh

## Purpose
This test verifies mixed file and stdin handling for compression and decompression over multiple operands.

## APIs, control flow, and integration
It creates `file1` and `file2`, compresses `./file1`, stdin (`-`), and `./file2` in one command, pipes stdout to `zstd -d`, and separately checks `file1.zst` and `file2.zst`. It then removes originals and tests `zstd -d ./file1.zst - file2.zst` with a compressed stdin stream, confirming reconstructed files and stdout behavior. A final `-c` decompression case emits all outputs to stdout.

## State, dependencies, risks, and test signals
State is scratch-local files and `.zst` side effects. The test depends on default output naming, stdin marker semantics, and correct ordering of streamed outputs. Risks include subtle changes to mixed operand policy or overwrite behavior. Pass output demonstrates file outputs are created when expected and concatenated stdout data remains decodable.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/compression/multiple-files.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/compression/row-match-finder.sh -->
# sources/compression/zstd/tests/cli-tests/compression/row-match-finder.sh

## Purpose
This script tests option parsing and successful compression for the row match finder toggle.

## APIs, control flow, and integration
It assumes `file` exists and runs `zstd file -7f --row-match-finder` followed by `zstd file -7f --no-row-match-finder`. The `-7` level selects a strategy where the row match finder option is relevant; `-f` allows overwriting `file.zst`.

## State, dependencies, risks, and test signals
The test only checks command success, not output equality or ratio. It depends on the build exposing both options. The risk is limited coverage: parser acceptance and no crash are tested, while algorithmic selection is inferred from the CLI path.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/compression/row-match-finder.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/compression/setup -->
# sources/compression/zstd/tests/cli-tests/compression/setup

## Purpose
Per-test setup for the compression CLI suite. It creates reusable scratch input files for compression tests.

## APIs, control flow, and integration
Under `run.py`, this script runs before each test case in the `compression` suite. It uses `datagen` three times to create `file`, `file0`, and `file1` in the per-test scratch directory. `set -e` makes data generation failures abort setup before the test body starts.

## State, dependencies, risks, and test signals
The persistent state is exactly the generated input files. Tests in this folder assume these names exist. Risks are hidden coupling: changes in generated file size or compressibility can affect size-order tests and long-window tests. A setup failure is surfaced by the harness as a suite setup exception.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/compression/setup -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/compression/stream-size.sh -->
# sources/compression/zstd/tests/cli-tests/compression/stream-size.sh

## Purpose
This test validates CLI support for content-size metadata and compression size hints on streaming stdin input.

## APIs, control flow, and integration
It pipes `datagen -g7654` into `zstd --stream-size=7654` and into `zstd --size-hint=7000`, then pipes both compressed streams to `zstd -t`. The script does not create named files.

## State, dependencies, risks, and test signals
There is no persistent state beyond pipeline buffers. Dependencies are `datagen` and CLI option support. Risks are limited because it validates decompression, not metadata inspection; it catches malformed frames and parser failures but not necessarily incorrect optional size fields.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/compression/stream-size.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/compression/verbose-wlog.sh -->
# sources/compression/zstd/tests/cli-tests/compression/verbose-wlog.sh

## Purpose
This test checks verbose compression/listing output around high compression levels and long-distance mode, especially window-log reporting.

## APIs, control flow, and integration
It sources `COMMON/platform.sh`, then compresses stdin from `file` with `-vv -19` into `file.19.zst` and lists it with `zstd -vv -l`. It repeats with `--long` into `file.19.long.zst`. Expected stderr/stdout matching is handled by the CLI test harness.

## State, dependencies, risks, and test signals
State is two `.zst` outputs. The test depends on verbose output stability and a large enough setup input to produce meaningful frame metadata. Risks are mostly diagnostic-output churn and platform-specific line endings or terminal behavior. Pass confirms both operations succeed and expected verbose metadata appears.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/compression/verbose-wlog.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/compression/window-resize.sh -->
# sources/compression/zstd/tests/cli-tests/compression/window-resize.sh

## Purpose
This test stresses long-window resizing by compressing a large generated file with an explicit long window and no content size.

## APIs, control flow, and integration
It generates a 1 GiB `file`, compresses with `zstd --long=30 -1 --single-thread --no-content-size -f file`, then lists the resulting frame with `zstd -l -v file.zst`. It removes `file` and `file.zst` at the end to keep scratch usage bounded.

## State, dependencies, risks, and test signals
The test temporarily consumes substantial disk and CPU. It depends on 64-bit address space or sufficient memory and on the CLI listing path. The major risk is resource pressure in constrained CI. A pass indicates the compressor can resize/encode the large window and the list command can inspect it.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/compression/window-resize.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/decompression/detectErrors.sh -->
# sources/compression/zstd/tests/cli-tests/decompression/detectErrors.sh

## Purpose
This decompression test verifies that known malformed golden samples are rejected.

## APIs, control flow, and integration
It sets `GOLDEN_DIR` to `$ZSTD_REPO_DIR/tests/golden-decompression-errors/`, iterates every file, and runs `zstd -t`. If any invalid sample tests successfully, it calls `die`. The runner supplies `ZSTD_REPO_DIR` and the shell helper `die`.

## State, dependencies, risks, and test signals
No files are modified. The test depends on the repository golden corpus existing and containing only invalid samples. Risks are shell glob behavior if the directory is missing and changes to error tolerance. Pass means every corpus member produced a decompression error.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/decompression/detectErrors.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/decompression/golden.sh -->
# sources/compression/zstd/tests/cli-tests/decompression/golden.sh

## Purpose
This test validates that all known-good golden decompression samples are accepted by the CLI.

## APIs, control flow, and integration
It sets `GOLDEN_DIR` to `$ZSTD_REPO_DIR/tests/golden-decompression/` and invokes `zstd -r -t "$GOLDEN_DIR"` to recursively test every compressed sample. `set -e` turns any failed test into a script failure.

## State, dependencies, risks, and test signals
The test is read-only. It depends on golden assets and recursive CLI traversal. Risks are missing corpus files or support changes for old/edge frames. Pass confirms compatibility with the golden decompression suite.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/decompression/golden.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/decompression/pass-through.sh -->
# sources/compression/zstd/tests/cli-tests/decompression/pass-through.sh

## Purpose
This test covers pass-through semantics for non-zstd data during decompression, including explicit `--pass-through`, cat-style symlinks, legacy `-fc` behavior, and `--no-pass-through` rejection.

## APIs, control flow, and integration
It sources platform helpers, creates short raw files and `file`, compresses `file`, then exercises `zstd -dc --pass-through`, `zstdcat`, symlinked `zcat`/`gzcat`, mixed compressed/uncompressed operands, output-to-file pass-through, and legacy forced stdout cases. It then verifies disabled pass-through paths fail for cat commands and regular `zstd -d`.

## State, dependencies, risks, and test signals
Scratch state includes raw files, `file.zst`, and pass-through output files. Dependencies include `ZSTD_SYMLINK_DIR`, `$DIFF`, and expected stderr behavior. Risks are policy changes around implicit pass-through and symlink mode detection. Pass signals include byte equality for file output and failure of raw input when pass-through is disabled.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/decompression/pass-through.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/determinism/basic.sh -->
# sources/compression/zstd/tests/cli-tests/determinism/basic.sh

## Purpose
This test locks single-threaded compression determinism across levels, long-distance settings, and fast mode by comparing md5 hashes against harness expectation files.

## APIs, control flow, and integration
After sourcing platform helpers, it skips by replaying the exact expected stdout if `NON_DETERMINISTIC` is set. Otherwise it loops levels 1 through 19 over `files/*`, prints a stable label, pipes `zstd --single-thread -q -$level ... -c` to `md5hash`, then covers `--long=18` at levels 1 and 19 and `--fast=1`.

## State, dependencies, risks, and test signals
It reads the `files` directory produced by setup and writes no durable outputs. Dependencies include deterministic `datagen` fixtures, `seq`, `ls`, `md5hash`, and exact stdout files. Risks are intentional compression format/tuning changes requiring golden hash updates. Pass confirms byte-for-byte reproducibility for the selected matrix.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/determinism/basic.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/determinism/multithread.sh -->
# sources/compression/zstd/tests/cli-tests/determinism/multithread.sh

## Purpose
This test checks deterministic output for multi-threaded compression and verifies that varying thread counts does not change selected outputs for representative inputs.

## APIs, control flow, and integration
It skips by replaying expected stdout when `NON_DETERMINISTIC` is set or `$hasMT` is empty. Otherwise it hashes `zstd -T2` output for levels 1, 3, 7, and 19 across `files/*`, hashes long-distance output at levels 1 and 19, then creates a single-thread reference for each file and compares `-T1`, `-T2`, and `-T4` outputs with `$DIFF`.

## State, dependencies, risks, and test signals
State includes temporary `*.zst` and `*.zst.good` files under the copied `files` directory. Dependencies are thread-enabled zstd, platform helper variables, and exact stdout fixtures. Risks are legitimate multi-thread format changes and CPU/thread availability differences. Pass confirms deterministic frame bytes across fixed multi-thread settings and thread-count equivalence for the tested level.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/determinism/multithread.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/determinism/reuse.sh -->
# sources/compression/zstd/tests/cli-tests/determinism/reuse.sh

## Purpose
This test ensures compression context reuse across multiple input files does not affect deterministic output.

## APIs, control flow, and integration
It creates four data files of different sizes, defines `validate()` to compare each generated `.zst` with a `.good` reference, and loops levels 1 through 19. For each level it creates independent single-file references, then compresses the four files together in several different orders with `--single-thread`, validating that each output matches its reference.

## State, dependencies, risks, and test signals
State consists of generated inputs and `.zst`/`.good` outputs. Dependencies are `datagen`, `$DIFF`, deterministic build behavior, and exact stdout expectations. The risk is high sensitivity to any intentional change in context reuse or output naming. Pass indicates per-file compression results are invariant to prior files compressed by the same CLI invocation.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/determinism/reuse.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/determinism/setup -->
# sources/compression/zstd/tests/cli-tests/determinism/setup

## Purpose
Per-test setup for determinism cases. It provides each test with a local copy of the shared deterministic fixture corpus.

## APIs, control flow, and integration
Under `run.py`, this script runs before each determinism test and executes `cp -r ../files .`. The source `../files` directory is produced by `setup_once` in the suite scratch root.

## State, dependencies, risks, and test signals
The state is a copied `files` directory inside each test scratch directory. The dependency on `setup_once` is strong; if the fixture corpus is missing, every determinism test fails before its body. Copying rather than sharing isolates tests from each other's `.zst` side effects.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/determinism/setup -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/determinism/setup_once -->
# sources/compression/zstd/tests/cli-tests/determinism/setup_once

## Purpose
Suite-level setup for determinism tests. It creates a stable matrix of generated inputs covering sizes and compressibility percentages.

## APIs, control flow, and integration
It sources platform helpers, creates `files/`, and writes `datagen` outputs for sizes 0 through 1,000,000 bytes plus `-P0`, `-P10`, `-P25`, `-P50`, `-P75`, `-P90`, and `-P100` at size 10,000. `run.py` runs this once per determinism suite scratch directory before individual test setup.

## State, dependencies, risks, and test signals
The state persists for the suite and is copied into each test. Dependencies are deterministic `datagen` defaults and platform helper availability. Risks are fixture drift causing checksum updates and disk usage from copying. Setup success enables the downstream exact-output determinism checks.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/determinism/setup_once -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/dict-builder/empty-input.sh -->
# sources/compression/zstd/tests/cli-tests/dict-builder/empty-input.sh

## Purpose
This dictionary-builder test verifies that training handles an empty sample alongside valid samples.

## APIs, control flow, and integration
It generates 50 files with seeds 1 through 50, creates an empty file with `touch empty`, enables verbose shell tracing, and runs `zstd -q --train empty file*`. The command is expected to succeed.

## State, dependencies, risks, and test signals
Scratch state is the generated sample set, the empty file, and default dictionary output side effects. Dependencies are `datagen`, `seq`, and dictionary trainer support. Risks include sample glob ordering and future stricter trainer validation. A pass confirms empty input samples are ignored or handled without fatal errors.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/dict-builder/empty-input.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/dict-builder/no-inputs.sh -->
# sources/compression/zstd/tests/cli-tests/dict-builder/no-inputs.sh

## Purpose
This negative CLI test exercises dictionary training with no inputs.

## APIs, control flow, and integration
It turns on shell tracing and runs `zstd --train`. There is no `set -e`, so the expected result is controlled by the harness `.exit`/stderr expectation files rather than shell abort behavior.

## State, dependencies, risks, and test signals
The test writes no inputs. It depends on the CLI emitting stable diagnostics and returning the expected nonzero status. It catches regressions where `--train` without samples silently succeeds or crashes.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/dict-builder/no-inputs.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/dictionaries/dictionary-mismatch.sh -->
# sources/compression/zstd/tests/cli-tests/dictionaries/dictionary-mismatch.sh

## Purpose
This test verifies that a frame compressed with one dictionary can be tested with the matching dictionary but is rejected with a different or missing dictionary.

## APIs, control flow, and integration
It sources platform helpers and uses fixtures copied by `dictionaries/setup`: `files/0`, `dicts/0`, and `dicts/1`. It compresses `files/0` with `-D dicts/0`, tests the result with the same dictionary, then asserts `zstd -t` fails with `dicts/1` and with no dictionary. A disabled block documents how the dictionaries were originally generated.

## State, dependencies, risks, and test signals
State is `files/0.zst`. The test depends on the two fixture dictionaries having different IDs/content and on the decompressor enforcing dictionary identity. Risks include fixture regeneration accidentally producing compatible dictionaries. Pass confirms mismatch detection and missing-dictionary failure paths.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/dictionaries/dictionary-mismatch.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/dictionaries/golden.sh -->
# sources/compression/zstd/tests/cli-tests/dictionaries/golden.sh

## Purpose
This test validates dictionary compression/decompression behavior with golden dictionary assets, specifically a dictionary missing symbols.

## APIs, control flow, and integration
It locates `$ZSTD_REPO_DIR/tests/golden-compression/` and `$ZSTD_REPO_DIR/tests/golden-dictionaries/`, compresses the golden `http` input with `http-dict-missing-symbols`, writes `http.zst`, and tests the frame using the same dictionary.

## State, dependencies, risks, and test signals
Scratch state is `http.zst`. Dependencies are golden input/dictionary assets and stable dictionary handling in the CLI. The test is narrow but targets an edge case in dictionary entropy tables. Pass means the compressor can emit and the decompressor can read a frame for that golden dictionary case.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/dictionaries/golden.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/dictionaries/setup -->
# sources/compression/zstd/tests/cli-tests/dictionaries/setup

## Purpose
Per-test setup for dictionary CLI tests. It copies suite-generated files and dictionaries into each test scratch directory.

## APIs, control flow, and integration
The script runs `cp -r ../files .` and `cp -r ../dicts .` under `set -e`. It is invoked by `run.py` before each test in the dictionaries suite.

## State, dependencies, risks, and test signals
The copied `files/` and `dicts/` directories isolate tests from one another. The script depends on `setup_once` having completed. Risks are hidden fixture coupling and stale generated dictionaries. Setup failure prevents the test body from running.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/dictionaries/setup -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/dictionaries/setup_once -->
# sources/compression/zstd/tests/cli-tests/dictionaries/setup_once

## Purpose
Suite-level fixture generation for dictionary CLI tests. It creates two intentionally different dictionaries and a sample input.

## APIs, control flow, and integration
The script sources platform helpers, creates `files/` and `dicts/`, generates seeds 1-50, trains `dicts/0`, generates seeds 51-100 into the same files directory, trains `dicts/1`, asserts the two dictionaries differ with `cmp ... && die`, and finally writes `files/0`.

## State, dependencies, risks, and test signals
Persistent suite state is `files/` and `dicts/`. Dependencies are `datagen`, `zstd --train`, `seq`, `cmp`, and `die`. Risks include nondeterministic or changed trainer behavior causing equal dictionaries or dictionary IDs. A pass creates the mismatch fixtures used by downstream tests.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/dictionaries/setup_once -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/file-handling/directory-mirror.sh -->
# sources/compression/zstd/tests/cli-tests/file-handling/directory-mirror.sh

## Purpose
This test validates `--output-dir-mirror` path reconstruction across relative, cwd-relative, absolute, and dotted paths, including hidden files and directories.

## APIs, control flow, and integration
It creates `src` with visible/hidden files, `mid`, and `dst`. It compresses recursively with `zstd -q -r --output-dir-mirror`, decompresses recursively with the same option, and compares source/destination trees with `diff --brief --recursive --new-file`. The sequence is repeated from inside `src`, with absolute `$BASE_PATH`, and with paths containing `./` components.

## State, dependencies, risks, and test signals
State is the `src`, `mid`, and `dst` directory trees, reset between cases. Dependencies are recursive CLI mode and POSIX `diff`. Risks are platform path normalization differences, absolute path handling on non-Unix systems, and hidden-file traversal regressions. Pass means compressed and decompressed mirrored trees preserve structure and content.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/file-handling/directory-mirror.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/file-stat/compress-file-to-dir-without-write-perm.sh -->
# sources/compression/zstd/tests/cli-tests/file-stat/compress-file-to-dir-without-write-perm.sh

## Purpose
This regression test, motivated by issue 3523, exercises file-stat tracing when output targets a directory without write permission.

## APIs, control flow, and integration
It generates `file`, creates `out`, applies `chmod 000 out`, runs `zstd file -q --trace-file-stat -o out/file.zst`, tests `out/file.zst`, and restores permissions with `chmod 777 out`. The expected behavior depends on the test environment permissions; under some privileged users, writes can still succeed.

## State, dependencies, risks, and test signals
State includes `file`, `out/`, and `out/file.zst`. The test depends on permission semantics and `--trace-file-stat` instrumentation. The major risk is running as root or on filesystems that ignore mode bits, which can change the intended coverage. A pass indicates the trace path does not break compression/output validation in this scenario.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/file-stat/compress-file-to-dir-without-write-perm.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/file-stat/compress-file-to-file.sh -->
# sources/compression/zstd/tests/cli-tests/file-stat/compress-file-to-file.sh

## Purpose
This file-stat test covers normal file-to-file compression with trace instrumentation enabled.

## APIs, control flow, and integration
It generates `file`, sets mode `642`, runs `zstd file -q --trace-file-stat -o file.zst`, and validates the output with `zstd -tq file.zst`.

## State, dependencies, risks, and test signals
State is `file` and `file.zst`. The chmod checks stat propagation paths without making the file unreadable. Risks are platform permission differences and diagnostic expectation churn. Pass confirms traced file input/output compression still creates a valid frame.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/file-stat/compress-file-to-file.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/file-stat/compress-file-to-stdout.sh -->
# sources/compression/zstd/tests/cli-tests/file-stat/compress-file-to-stdout.sh

## Purpose
This test covers file-input to stdout-output compression with `--trace-file-stat`.

## APIs, control flow, and integration
It generates `file`, runs `zstd file -cq --trace-file-stat > file.zst`, and tests the redirected output. The `-c` path avoids normal output file naming while still tracing the input file stat.

## State, dependencies, risks, and test signals
State is `file` and redirected `file.zst`. The test depends on stdout binary data not being polluted by trace diagnostics. Pass indicates diagnostics remain on stderr and the compressed stdout stream is valid.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/file-stat/compress-file-to-stdout.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/file-stat/compress-stdin-to-file.sh -->
# sources/compression/zstd/tests/cli-tests/file-stat/compress-stdin-to-file.sh

## Purpose
This test covers stdin-input to named file-output compression with file-stat tracing.

## APIs, control flow, and integration
It generates `file`, pipes it into `zstd < file -q --trace-file-stat -o file.zst`, and validates with `zstd -tq`. This exercises the code path where input stat information is unavailable or stream-based while output stat tracing remains relevant.

## State, dependencies, risks, and test signals
State is `file` and `file.zst`. Risks include trace code assuming file-backed input. Pass confirms stdin compression with trace instrumentation produces a valid file.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/file-stat/compress-stdin-to-file.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/file-stat/compress-stdin-to-stdout.sh -->
# sources/compression/zstd/tests/cli-tests/file-stat/compress-stdin-to-stdout.sh

## Purpose
This test covers the fully streamed compression path with `--trace-file-stat`.

## APIs, control flow, and integration
It generates `file`, runs `zstd < file -cq --trace-file-stat > file.zst`, and tests the output. Both input and output are shell streams from zstd's perspective.

## State, dependencies, risks, and test signals
State is limited to the source fixture and redirected compressed output. The important signal is that trace diagnostics do not contaminate stdout and stream-only stat handling does not fail.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/file-stat/compress-stdin-to-stdout.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/file-stat/decompress-file-to-file.sh -->
# sources/compression/zstd/tests/cli-tests/file-stat/decompress-file-to-file.sh

## Purpose
This test covers traced decompression from a named compressed file to the default output file.

## APIs, control flow, and integration
It creates `file.zst` from `datagen | zstd -q`, sets mode `642`, then runs `zstd -dq --trace-file-stat file.zst`. The default output path is derived by stripping `.zst`.

## State, dependencies, risks, and test signals
State includes `file.zst` and decompressed `file`. The test depends on permission/stat handling for compressed inputs. Pass confirms traced file-to-file decompression succeeds and output naming remains intact.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/file-stat/decompress-file-to-file.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/file-stat/decompress-file-to-stdout.sh -->
# sources/compression/zstd/tests/cli-tests/file-stat/decompress-file-to-stdout.sh

## Purpose
This test covers traced decompression from a named file to stdout.

## APIs, control flow, and integration
It creates `file.zst`, runs `zstd -dcq --trace-file-stat file.zst > file`, and relies on shell redirection for the decompressed output.

## State, dependencies, risks, and test signals
State is `file.zst` and redirected `file`. The key risk is diagnostics leaking to stdout. Pass confirms the binary stdout stream remains clean and decompression succeeds with trace enabled.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/file-stat/decompress-file-to-stdout.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/file-stat/decompress-stdin-to-file.sh -->
# sources/compression/zstd/tests/cli-tests/file-stat/decompress-stdin-to-file.sh

## Purpose
This test covers traced decompression from stdin to a named output file.

## APIs, control flow, and integration
It creates `file.zst`, runs `zstd -dcq --trace-file-stat < file.zst -o file`, and expects a valid decompressed `file`. This combines stdin source handling with explicit output path handling.

## State, dependencies, risks, and test signals
State is `file.zst` and `file`. Risks are stat code assuming file input and stdout/file option interaction. Pass confirms stream input plus named output works under trace instrumentation.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/file-stat/decompress-stdin-to-file.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/file-stat/decompress-stdin-to-stdout.sh -->
# sources/compression/zstd/tests/cli-tests/file-stat/decompress-stdin-to-stdout.sh

## Purpose
This test covers the fully streamed decompression path with file-stat tracing.

## APIs, control flow, and integration
It creates `file.zst`, runs `zstd -dcq --trace-file-stat < file.zst > file`, and writes decompressed bytes through stdout redirection.

## State, dependencies, risks, and test signals
State is `file.zst` and `file`. Pass confirms trace diagnostics do not corrupt stdout and decompression handles non-file input/output descriptors.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/file-stat/decompress-stdin-to-stdout.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/progress/no-progress.sh -->
# sources/compression/zstd/tests/cli-tests/progress/no-progress.sh

## Purpose
This test validates cases where progress information must not be printed, even when stderr is faked as a console or verbosity/progress flags interact.

## APIs, control flow, and integration
It sources platform helpers, creates `hello` and `world`, precompresses them, and loops over argument sets including empty, quiet, explicit no-progress, and verbose no-progress combinations. For each set it exercises compression and decompression across file-to-file, pipe-to-pipe, pipe-to-file, file-to-pipe, and multi-file cases. Output descriptions are printed to stderr for exact/glob matching by the harness.

## State, dependencies, risks, and test signals
State includes raw and compressed `hello`/`world` files. Dependencies are `$INTOVOID`, helper `println`, and expected stderr output files. Risks are progress-rendering policy changes and terminal simulation differences. Pass means no progress lines appear in the negative matrix while operations still succeed.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/progress/no-progress.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/progress/progress.sh -->
# sources/compression/zstd/tests/cli-tests/progress/progress.sh

## Purpose
This test validates cases where progress information should be printed.

## APIs, control flow, and integration
It sources platform helpers, creates `hello`/`world`, precompresses them, and loops over `--progress`, `--fake-stderr-is-console`, and `--progress --fake-stderr-is-console -q`. For each argument set it runs the same compression/decompression matrix as `no-progress.sh`: file/file, pipe/pipe, pipe/file, file/pipe, and multi-file in both directions.

## State, dependencies, risks, and test signals
State is local raw/compressed fixtures. Dependencies are terminal/progress simulation flags and harness expectation files. Risks are progress output formatting changes. Pass confirms expected progress diagnostics appear without breaking data paths.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/progress/progress.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/run.py -->
# sources/compression/zstd/tests/cli-tests/run.py

## Purpose
`run.py` is the zstd CLI test runner. It discovers shell test cases, creates isolated scratch directories, runs suite/test setup and teardown hooks, executes each test, and checks stdout, stderr, and exit status against sidecar expectation files.

## Important APIs, types, and functions
The main public structures are `Options`, `TestCase`, and `TestSuite`. `Options` carries environment, timeout, verbosity, preservation, scratch/test paths, and exact-output update mode. `TestCase` owns one executable test file, exposes `launch()`, `analyze()`, and `run()`, and implements `_launch_test()`, `_join_test()`, `_check_exit()`, `_check_output_exact()`, `_check_output_glob()`, and `_analyze_results()`. `TestSuite` is a context manager that runs `setup_once`/`teardown_once`, creates per-test scratch directories, and wraps each test in `setup`/`teardown`.

## Control flow
At startup the script resolves repository paths, parses CLI flags, creates symlinks for zstd-compatible command names under `bin/symlinks`, builds a sanitized environment, and creates `Options`. With no positional tests it calls `get_all_tests()` to walk `test_dir`, filtering helper directories and sidecar files; otherwise it calls `resolve_listed_tests()`. `run_tests()` iterates suites, enters a `TestSuite`, runs sorted unique test files through `test_suite.test_case()`, records pass/fail, and returns a process exit code.

## State, persistence, dependencies, and integration
State is mostly under `TEST_DIR/scratch/`, plus symlinks under `TEST_DIR/bin/symlinks`. Test subprocess environments remove inherited variables beginning with `ZSTD`, then inject paths such as `ZSTD_REPO_DIR`, `DATAGEN_BIN`, `ZSTD_SYMLINK_DIR`, `COMMON`, and `PATH`. Output expectations are file-sidecar contracts: `.stdout.exact`, `.stderr.exact`, `.stdout.glob`, `.stderr.glob`, `.ignore`, and `.exit`. Dependencies include Python 3, POSIX subprocess behavior, `diff`, executable test scripts, and zstd build artifacts.

## Risks and test signals
The runner is intentionally serial despite `TestCase.launch()` supporting asynchronous execution; setup/teardown behavior assumes one test at a time per suite. `_check_output()` currently treats missing expectation files and `.ignore` the same as ignored output, so unanticipated output is not failed unless exact/glob files exist. Timeout exceptions are not caught, so they fail the runner directly. Pass signals are per-test `PASS` lines and final `PASSED all N tests!`; failures include detailed per-check diagnostics and diffs.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/run.py -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/zstd-symlinks/setup -->
# sources/compression/zstd/tests/cli-tests/zstd-symlinks/setup

## Purpose
Per-test setup for zstd symlink behavior tests. It prepares both raw and compressed fixtures.

## APIs, control flow, and integration
The script writes `hello` and `world` using `println`, then runs `zstd hello world`, which creates `hello.zst` and `world.zst`. It is run inside the per-test scratch directory by `run.py`.

## State, dependencies, risks, and test signals
State includes two raw files and two compressed outputs. Dependencies are the platform helper `println` and zstd default output naming. Downstream symlink tests rely on this setup to cover mixed compressed/raw operands.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/zstd-symlinks/setup -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/zstd-symlinks/zstdcat.sh -->
# sources/compression/zstd/tests/cli-tests/zstd-symlinks/zstdcat.sh

## Purpose
This test verifies zstdcat behavior through both installed harness symlinks and a local symlink to the zstd binary.

## APIs, control flow, and integration
Using setup fixtures, it runs `zstdcat` over compressed-only and mixed compressed/raw operands, then creates `./zstdcat` as a symlink to `$(which zstd)` and runs it on `hello.zst`. The behavior relies on program-name dispatch in the zstd CLI.

## State, dependencies, risks, and test signals
State adds a local `zstdcat` symlink. Dependencies are `which`, symlink support, `PATH`, and zstdcat pass-through policy. Risks are platforms without symlinks and changes to argv[0]-based mode selection. Pass confirms symlink invocation decompresses/prints as expected.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/zstd-symlinks/zstdcat.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/datagencli.c -->
# sources/compression/zstd/tests/datagencli.c

## Purpose
`datagencli.c` implements the standalone `datagen` test utility. It generates deterministic synthetic data to stdout for zstd tests, either lorem-style text or randomized data with a requested compressibility.

## APIs, functions, and control flow
The executable has `usage()` and `main()`. `main()` parses aggregated short options: `-g#` size with optional `K`, `M`, `G`, `B`; `-s#` seed; `-P#` compressibility percent clamped to 100; hidden `-L#` literal distribution probability; `-v`; and `-h`. If `-P` is supplied it calls `RDG_genStdout(size, proba, litProba, seed)`, otherwise it calls `LOREM_genOut(size, seed)`.

## State, dependencies, integration, and risks
There is no persisted state; output is written to stdout and diagnostics to stderr depending on `displayLevel`. Dependencies are `datagen.h`, `loremOut.h`, and `util.h` types. It is integrated throughout CLI tests and corpus generation scripts. Risks include permissive numeric parsing without invalid suffix diagnostics, overflow in very large sizes, and hidden `-L` behavior being coupled to tests without help output.

## Test signals
Downstream tests use `datagen` success, deterministic seed behavior, and output size/compressibility as setup signals. Failures usually surface as bad test fixtures rather than direct unit assertions in this file.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/datagencli.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/decodecorpus.c -->
# sources/compression/zstd/tests/decodecorpus.c

## Purpose
`decodecorpus.c` is a synthetic zstd frame/block corpus generator and self-tester. It creates valid but randomized compressed frames, raw compressed blocks, optional dictionaries, and original outputs for decompressor fuzzing and regression tests.

## Important APIs, types, and global state
Core types include `frameHeader_t`, `cblockStats_t`, `frame_t`, `dictInfo`, and `genType_e`. Global buffers (`CONTENT_BUFFER`, `FRAME_BUFFER`, `LITERAL_BUFFER`, sequence buffers, FSE/HUF workspaces) hold generated content and compressed output. Command-line state is in `opts`, `g_displayLevel`, `g_maxDecompressedSizeLog`, and `g_maxBlockSize`. Random generation is driven by `RAND()`, `RAND_buffer*()`, `RAND_range()`, and `RAND_exp()`.

## Control flow and algorithms
Generation starts with `writeFrameHeader()`, then writes raw, RLE, or compressed blocks. Literal paths include `writeLiteralsBlockSimple()`, `writeHufHeader()`, and `writeLiteralsBlockCompressed()` with repeat-mode state in `frame->stats`. Sequence paths initialize and populate zstd internal sequence storage, choose symbol sets and FSE modes, then write sequence headers and bitstreams. `writeCompressedBlock()`, `writeBlock()`, `writeBlocks()`, and `writeChecksum()` assemble complete frames. Dictionary support uses `genRandomDict()` and `initDictInfo()` to create valid dictionary headers/content and to drive dictionary-based frame/block generation.

## Validation, I/O, and CLI integration
Self-test paths include `testDecodeSimple()`, `testDecodeStreaming()`, `testDecodeWithDict()`, and `testDecodeRawBlock()`, which compare decompressed bytes against `frame->srcStart`. `runTestMode()` repeatedly runs frame or block tests for a count or duration. File-generation paths are `generateFile()`, `generateCorpus()`, and `generateCorpusWithDict()`, writing `z%06u.zst`, optional originals, and optional dictionary files. `main()` parses `-p`, `-o`, `-s`, `-n`, `-t`, `-T`, verbosity, `--content-size`, `--use-dict=`, `--gen-blocks`, max-size limits, forced block/literal type, `--frame-header-only`, and `--no-magic`.

## Dependencies, risks, and test signals
The file directly includes internal zstd compression implementation and deprecated block decompression APIs, so it is tightly coupled to libzstd internals. Risks include global buffer bounds, option validation gaps (`--max-block-size-log` compares against a size constant after parsing a log), path length truncation, allocation failures, and format-spec drift. Strong test signals are successful self-test mode, generated corpora accepted by fuzz harnesses, and dictionary/raw-block round trips matching original buffers.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/decodecorpus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/external_matchfinder.c -->
# sources/compression/zstd/tests/external_matchfinder.c

## Purpose
This file provides a test sequence producer for zstd's external matchfinder/sequence producer API. It can emit valid simple sequences or intentionally invalid/error cases.

## APIs, functions, and control flow
`simpleSequenceProducer()` implements a small hash-table match finder over the current source using `ZSTD_hashPtr()` and `ZSTD_count()`, emitting `ZSTD_Sequence` entries when matches are within `windowSize` and finishing with a final literals-only sequence. `zstreamSequenceProducer()` is the exported callback; it reads an `EMF_testCase` from `sequenceProducerState`, zeroes the output buffer, and switches among cases: zero sequences, one big literals sequence, many valid sequences, invalid offset/match/literal lengths, invalid final literals, capacity+1 small error, or `ZSTD_SEQUENCE_PRODUCER_ERROR`.

## State, dependencies, risks, and test signals
State is callback-local except for constants `HLOG`, `MLS`, and `BADIDX`. The file depends on `external_matchfinder.h`, `zstd_compress_internal.h`, and the static-linking zstd sequence API. Risks include ignoring `outSeqsCapacity` in several paths and assuming `srcSize` is large enough for invalid-case arithmetic; those are deliberate stress behaviors but dangerous if reused outside tests. Test signals come from consumers verifying accepted valid sequences and rejected invalid producer outputs.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/external_matchfinder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/external_matchfinder.h -->
# sources/compression/zstd/tests/external_matchfinder.h

## Purpose
This header declares the external matchfinder test cases and the sequence producer callback used by zstd tests.

## APIs and integration
It defines `EMF_testCase` values for valid and invalid producer behaviors and declares `zstreamSequenceProducer()` with the `ZSTD_sequenceProducer_F` compatible signature. It defines `ZSTD_STATIC_LINKING_ONLY` before including `zstd.h` so `ZSTD_Sequence` and advanced APIs are visible.

## State, risks, and test signals
The header contains no state. Its risk is API coupling to static zstd definitions and enum/order coupling with test callers. Correct integration is signaled by test code being able to pass enum values as callback state and observe expected compression API behavior.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/external_matchfinder.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/fullbench.c -->
# sources/compression/zstd/tests/fullbench.c

## Purpose
`fullbench.c` is a standalone zstd speed analyzer. It benchmarks many compression, decompression, streaming, block-internal, and sequence APIs over generated samples or user-provided files.

## Important APIs, types, and scenarios
The benchmark framework centers on `PrepResult`, function-pointer types `PrepFunction_f`, `BenchedFunction_f`, `VerifFunction_f`, and `BenchScenario`. `kScenarios` maps numeric scenario IDs to named benchmark functions such as `compress`, `decompress`, `compress_freshCCtx`, `decompressDCtx`, `compressContinue`, streaming variants, `compress2`, multi-thread `compressStream2`, sequence compression, sequence/literal conversion, and internal literal/sequence header decode scenarios when not built as a DLL import.

## Control flow and state
Global contexts `g_zcc`, `g_zdc`, `g_cstream`, and `g_dstream` are lazily allocated in `benchMem()` and freed after each scenario. Prep functions build suitable input: compressed frames for decompression, first-block literal/sequence slices for internal decoders, generated sequence buffers for sequence APIs, copied input for normal compression, or intentionally shortened output capacity. `benchMem()` configures compression parameters on contexts, prepares data, warms the destination buffer, runs `BMK_benchTimedFn()`, tracks the best ns/run, optionally verifies output with `check_compressedSequences`, and prints MB/s.

## CLI, dependencies, and integration
`main()` parses `-b#`, `-l#`, `-P#`, `-B#`, `-i#`, help flags, pause, and `--zstd=` parameter strings for window/hash/chain/search/minMatch/targetLength/strategy/level. With no files it calls `benchSample()` using lorem or RDG-generated data; with files it calls `benchFiles()`, loading as much as memory allows via `BMK_findMaxMem()`. Dependencies include zstd public and internal headers, `benchfn`, `benchzstd`, `datagen`, `lorem`, and platform `util`.

## Risks and test signals
This is benchmark code, so global contexts and process-level state are acceptable but not thread-safe. Risks include internal API churn, skipped scenarios when prep cannot produce compressed internals, large memory allocation, and benchmark results being sensitive to CPU/load. Validation signals are no zstd errors, optional sequence verification passing, and coherent speed output for selected scenarios.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/fullbench.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/fuzz/Makefile -->
# sources/compression/zstd/tests/fuzz/Makefile

## Purpose
This Makefile builds zstd fuzz targets and seed corpora support artifacts. It can build regression-driver linked targets by default or link against an external fuzzing engine.

## Targets, variables, and control flow
It includes `../../lib/libzstd.mk`, derives include flags for lib, programs, seekable format, and external sequence producer code, and defines warning/sanitizer-friendly compile flags. `FUZZ_SRC` combines fuzz helpers, zstd common/compress/decompress/dict/legacy sources, `util.c`, and the default sequence producer. It builds two object families: round-trip objects with `-DFUZZING_ASSERT_VALID_SEQUENCE` and decompression objects without it. `FUZZ_TARGETS` lists all fuzz binaries, including the targets researched in this subset. Pattern rules compile source-origin-prefixed object names; target rules link each fuzzer with C++ and `$(LIB_FUZZING_ENGINE)`. It also builds `libregression.a` from `regression_driver.o`, downloads/unzips corpora, and cleans generated objects/binaries.

## State, dependencies, risks, and test signals
State includes many generated `.o` files, fuzzer executables, `libregression.a`, and optional `corpora/` archives. Dependencies are make, C/C++ compilers, archiver, zstd source layout, optional network tools for corpora, and optional `THIRD_PARTY_SEQ_PROD_OBJ`. Risks include object-name substitution fragility, stale object families after flag changes, and C files linked by C++ requiring compatibility flags. Pass signals are successful `make all`, individual target builds, and regression execution via `fuzz.py`.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/fuzz/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/fuzz/block_decompress.c -->
# sources/compression/zstd/tests/fuzz/block_decompress.c

## Purpose
This libFuzzer target throws arbitrary input at `ZSTD_decompressBlock()` to ensure block decompression rejects or handles malformed raw blocks without crashing.

## APIs, control flow, and state
`LLVMFuzzerTestOneInput()` creates a `FUZZ_dataProducer_t` from the input only to randomize allocation behavior, ensures a reusable `rBuf` of `ZSTD_BLOCKSIZE_MAX`, creates/reuses `ZSTD_DCtx`, calls `ZSTD_decompressBegin()`, and invokes `ZSTD_decompressBlock(dctx, rBuf, neededBufSize, src, size)`. In non-`STATEFUL_FUZZING` builds it frees `dctx` after each input; `rBuf` remains process-global unless grown/replaced.

## Dependencies, risks, and test signals
Dependencies are zstd static APIs, `fuzz_helpers`, and `fuzz_data_producer`. The target intentionally ignores decompression return errors, treating only sanitizer/assert crashes as findings. Risks are persistent globals under stateful fuzzing and the block API requiring initialized history. A pass means no crash, assert, or sanitizer finding for the input.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/fuzz/block_decompress.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/fuzz/block_round_trip.c -->
# sources/compression/zstd/tests/fuzz/block_round_trip.c

## Purpose
This fuzz target validates raw block compression/decompression round trips.

## APIs, control flow, and state
`roundTripTest()` starts block compression with `ZSTD_compressBegin_advanced()`, calls `ZSTD_compressBlock()`, and if the block is uncompressible (`ret == 0`) copies the source directly to the result. Otherwise it calls `ZSTD_decompressBegin()` and `ZSTD_decompressBlock()`. `LLVMFuzzerTestOneInput()` reserves a prefix for randomized parameters, chooses a compression level, caps source size to `ZSTD_BLOCKSIZE_MAX`, allocates reusable `cBuf`/`rBuf`, creates contexts, and asserts decompressed size and bytes equal the input.

## Dependencies, risks, and test signals
Dependencies include `zstd_helpers`, `fuzz_third_party_seq_prod`, and the sequence producer setup/teardown macros. Risks include buffer sizing based on original input before cap, block-only semantics not including frame checksums, and global contexts under stateful fuzzing. Strong findings are zstd errors in expected-success paths, size mismatch, or byte corruption.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/fuzz/block_round_trip.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/fuzz/decompress_cross_format.c -->
# sources/compression/zstd/tests/fuzz/decompress_cross_format.c

## Purpose
This target cross-checks standard zstd frame decompression against magicless zstd frame decompression.

## APIs, control flow, and state
The fuzzer reserves a prefix for parameter data, treats the remaining bytes as magicless compressed data, prepends `ZSTD_MAGICNUMBER` to create a standard frame candidate, and uses `ZSTD_findFrameCompressedSize()` to truncate to one frame. It then reuses a `ZSTD_DCtx` to test one-shot `ZSTD_decompressDCtx()` in `ZSTD_f_zstd1` and `ZSTD_f_zstd1_magicless` modes, followed by streaming `ZSTD_decompressStream()` in both modes. If both accept, it asserts equal decompressed size and bytes; if one accepts, the other is expected to accept in the checked direction.

## Dependencies, risks, and test signals
Dependencies are zstd static format parameter APIs and allocation helpers. State is the reusable `dctx` plus per-input buffers. Risks include assuming little-endian magic-number memory layout and very large `dstSize` selection (`0..10*size`). Test signals are cross-format accept/reject consistency and identical output for accepted frames.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/fuzz/decompress_cross_format.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/fuzz/decompress_dstSize_tooSmall.c -->
# sources/compression/zstd/tests/fuzz/decompress_dstSize_tooSmall.c

## Purpose
This target verifies behavior when decompression destination capacity is smaller than the original input size.

## APIs, control flow, and state
It uses global `ZSTD_CCtx` and `ZSTD_DCtx`. For each input it compresses data into a buffer sized by `ZSTD_compressBound(size)`, chooses or derives a destination capacity smaller than `size`, and calls decompression APIs to ensure they fail safely rather than writing past the destination. It uses `FUZZ_dataProducer_t` for parameter choices.

## Dependencies, risks, and test signals
Dependencies are zstd one-shot compression/decompression APIs and fuzz helpers. State is reusable contexts, freed when not stateful. The important signal is that undersized destinations produce zstd errors or safe behavior under sanitizers. Risks are low coverage for exact boundary sizes unless corpus generation explores them.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/fuzz/decompress_dstSize_tooSmall.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/fuzz/dictionary_decompress.c -->
# sources/compression/zstd/tests/fuzz/dictionary_decompress.c

## Purpose
This fuzz target attempts dictionary-aware decompression of arbitrary input to catch crashes and invalid memory access in dictionary decompression paths. It trains a dictionary from the fuzz input rather than fuzzing an unrelated external dictionary file.

## APIs, control flow, and state
It keeps a global `ZSTD_DCtx`. `LLVMFuzzerTestOneInput()` reserves a data prefix for compressed bytes, calls `FUZZ_train(src, size, producer)` to create a `FUZZ_dict_t`, then randomly chooses between creating a `ZSTD_DDict`, loading a dictionary into the dctx with `ZSTD_DCtx_loadDictionary_advanced()`, or referencing a prefix with `ZSTD_DCtx_refPrefix_advanced()`. It allocates a random destination size in `0..10*size`, then calls either `ZSTD_decompress_usingDDict()` or `ZSTD_decompressDCtx()`. Return errors are acceptable; sanitizer failures are findings. Non-stateful builds free the dctx after each input.

## Dependencies, risks, and test signals
Dependencies are `zstd_helpers`, `fuzz_helpers`, `fuzz_data_producer`, and optional third-party sequence producer setup macros. Risks include limited semantic assertions because arbitrary compressed data is often invalid, and very large destination choices for large inputs. The target is valuable for dictionary loader modes, dictionary header handling, and dctx reuse/reset behavior. Pass means no crash or sanitizer report.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/fuzz/dictionary_decompress.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/fuzz/dictionary_loader.c -->
# sources/compression/zstd/tests/fuzz/dictionary_loader.c

## Purpose
This target fuzzes dictionary loading paths by trying to use fuzz input as dictionary data for compression and decompression.

## APIs, control flow, and state
It defines helper functions `compress()` and `decompress()`. `compress()` creates a fresh `ZSTD_CCtx`, then either calls `ZSTD_CCtx_refPrefix_advanced()` or `ZSTD_CCtx_loadDictionary_advanced()` before `ZSTD_compress2()`. `decompress()` mirrors the choice with `ZSTD_DCtx_refPrefix_advanced()` or `ZSTD_DCtx_loadDictionary_advanced()`, then calls `ZSTD_decompressDCtx()`. `LLVMFuzzerTestOneInput()` uses `FUZZ_dataProducer_reserveDataPrefix()` so the prefix is source data and the suffix controls dictionary sizes, load method, content type, and prefix mode; it then asserts successful decompression size and byte equality when compression succeeds.

## Dependencies, risks, and test signals
Dependencies are zstd dictionary APIs and fuzz helpers. The target stresses dictionary validation more than compression ratio. Risks include many invalid dictionaries causing shallow coverage unless seeded with generated dictionaries. Findings include crashes, zstd assertions, and inconsistent successful round trips.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/fuzz/dictionary_loader.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/fuzz/dictionary_round_trip.c -->
# sources/compression/zstd/tests/fuzz/dictionary_round_trip.c

## Purpose
This target verifies one-shot dictionary compression/decompression round trips with trained or fuzz-derived dictionaries.

## APIs, control flow, and state
It keeps global `ZSTD_CCtx` and `ZSTD_DCtx`. `roundTripTest()` trains a `FUZZ_dict_t`, randomly chooses prefix-reference versus loaded-dictionary mode and dictionary content type, applies `FUZZ_setRandomParameters()`, disables checksums so slightly undersized compression buffers can still succeed, and compresses with `ZSTD_compress2()`. It then rolls back the producer to reapply the same parameters and asserts deterministic compressed size/hash for a second compression. Decompression uses the matching prefix/load mode and validates the regenerated bytes.

## Dependencies, risks, and test signals
Dependencies include zstd dictionary APIs, `zstd_helpers` training helpers, and fuzz allocation/assert helpers. Risks include corpus inputs too small to train useful dictionaries and stateful context reuse hiding reproduction details. Strong test signals are successful decompression size equality and `FUZZ_memcmp()` equality with the original.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/fuzz/dictionary_round_trip.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/fuzz/dictionary_stream_round_trip.c -->
# sources/compression/zstd/tests/fuzz/dictionary_stream_round_trip.c

## Purpose
This target validates streaming compression/decompression round trips when dictionaries are involved.

## APIs, control flow, and state
It defines stream buffer helpers and uses global `ZSTD_CCtx`, `ZSTD_DCtx`, `cBuf`, `rBuf`, and `bufSize`. The compression path feeds selected chunk sizes through `ZSTD_compressStream2()`/end semantics with dictionary parameters; the decompression path reads back through streaming APIs with the matching dictionary. `LLVMFuzzerTestOneInput()` reserves bytes for the data producer, sizes buffers, chooses dictionary and streaming parameters, and asserts regenerated content matches input.

## Dependencies, risks, and test signals
Dependencies are zstd streaming/dictionary APIs, `zstd_helpers`, and `fuzz_data_producer`. Risks include chunk-size choices hiding edge cases and global buffers under stateful fuzzing. Pass signals are no zstd errors on expected-success paths and exact round-trip equality.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/fuzz/dictionary_stream_round_trip.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/fuzz/fse_read_ncount.c -->
# sources/compression/zstd/tests/fuzz/fse_read_ncount.c

## Purpose
This fuzz target round-trips FSE normalized-count serialization and parsing.

## APIs, control flow, and state
`LLVMFuzzerTestOneInput()` chooses `tableLog` and `maxSymbolValue`, fills a `short ncount[256]` distribution whose normalized weights sum to `1 << tableLog`, writes it with `FSE_writeNCount()`, appends a fuzz-selected amount of random trailing bytes, reads it back with `FSE_readNCount()`, and asserts the consumed byte count, max symbol value, table log, and all normalized counts match the original.

## Dependencies, risks, and test signals
Dependencies are static FSE APIs, zstd helper assertions, and `fuzz_data_producer` for parameter selection. The key risk is that generated distributions must maintain FSE invariants; otherwise the target would test writer precondition failures rather than reader correctness. The signal is exact read/write equality with sanitizer/assertion cleanliness.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/fuzz/fse_read_ncount.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/fuzz/fuzz.h -->
# sources/compression/zstd/tests/fuzz/fuzz.h

## Purpose
`fuzz.h` declares the common libFuzzer entrypoint signature used by the regression driver and fuzz target build.

## APIs and integration
It includes standard integer/size types and declares `int LLVMFuzzerTestOneInput(const uint8_t *src, size_t size);`. Each fuzz target defines this function, while `regression_driver.c` or libFuzzer provides the caller.

## State, dependencies, risks, and test signals
The header contains no state. Its main dependency is signature compatibility with libFuzzer. Any mismatch would fail to link or prevent regression-driver execution.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/fuzz/fuzz.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/fuzz/fuzz.py -->
# sources/compression/zstd/tests/fuzz/fuzz.py

## Purpose
`fuzz.py` is the command-line orchestrator for building fuzz targets, running libFuzzer/AFL/regression modes, generating seed corpora with `decodecorpus`, minimizing corpora, zipping corpora, and listing targets.

## Important APIs, types, and command flow
Small classes/enums `InputType`, `FrameType`, and `TargetInfo` describe each target's expected corpus type and frame/block mode. `TARGET_INFO` maps all supported target names. Parsing helpers include `parse_targets()`, `targets_parser()`, `parse_env_flags()`, `compiler_version()`, and `overflow_ubsan_flags()`. Command implementations are `build()`, `libfuzzer_cmd()`/`libfuzzer()`, `afl()`, `regression()`, `gen()`, `minimize()`, `zip_cmd()`, `list_cmd()`, and `main()`.

## State, persistence, dependencies, and integration
The script derives `FUZZ_DIR`, `CORPORA_DIR`, compiler flags, sanitizer flags, `LIB_FUZZING_ENGINE`, `AFL_FUZZ`, `DECODECORPUS`, and `ZSTD` from environment defaults. `build()` shells out to `make clean` and `make -j` with constructed `CC`, `CXX`, `CPPFLAGS`, `CFLAGS`, `CXXFLAGS`, and `LDFLAGS`. Runtime commands create corpora/artifact/seed directories. `gen()` invokes `decodecorpus`, optionally trains dictionaries with `zstd --train`, and copies generated samples into the seed corpus.

## Risks and test signals
The script is shell-command heavy and trusts compiler/version output, make, zip, unzip, AFL, and corpus paths. `gen()` documentation says fuzz RNG seeds are prepended, but the current copy loop writes sample bytes directly, so seed-prefix expectations should be checked against target behavior. `minimize()` assumes a crash directory exists. Pass signals are successful builds, fuzzer process startup, regression target exits, generated corpus files, minimized corpus directories, and created zip archives.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/fuzz/fuzz.py -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/fuzz/fuzz_data_producer.c -->
# sources/compression/zstd/tests/fuzz/fuzz_data_producer.c

## Purpose
This file implements the byte-stream data producer used by fuzz targets to derive randomized parameters from the same input as payload data.

## APIs, functions, and control flow
`FUZZ_dataProducer_create()` allocates a producer with `data`, `size`, and current read position semantics; `FUZZ_dataProducer_free()` releases it. The implementation provides byte consumption primitives through macros/templates in the included header path and exported functions for `remainingBytes`, `rollBack`, `empty`, `contract`, and `reserveDataPrefix`. `contract()` reduces the producer's active size, while `reserveDataPrefix()` leaves a prefix for target payload and uses the suffix for parameter generation.

## State, dependencies, risks, and test signals
State is one heap allocation per producer plus immutable references into the fuzz input. Dependencies are standard allocation and assertions in fuzz helpers. Risks are off-by-one cursor arithmetic and callers misunderstanding whether consumed bytes come from the front or back. Test signals are deterministic parameter derivation from a given input and sanitizer-clean operation when targets consume many parameter types.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/fuzz/fuzz_data_producer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/fuzz/fuzz_data_producer.h -->
# sources/compression/zstd/tests/fuzz/fuzz_data_producer.h

## Purpose
This header exposes the fuzz data producer abstraction for turning input bytes into bounded integers, booleans, and reserved payload slices.

## APIs and integration
It forward-declares `FUZZ_dataProducer_t` and declares lifecycle/control functions: `create`, `free`, `remainingBytes`, `rollBack`, `empty`, `contract`, and `reserveDataPrefix`. The header also provides typed producer helpers/macros used by targets, such as integer-range selection, so fuzz inputs can choose compression levels, buffer sizes, dictionary sizes, and streaming chunk sizes reproducibly.

## State, dependencies, risks, and test signals
The header itself has no state but defines the contract for producer cursor state in the `.c` file. Risks include range helpers being called with invalid min/max values and target code depending on byte consumption order. Correctness is signaled by deterministic reproduction: the same fuzz input must derive the same parameter sequence.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/fuzz/fuzz_data_producer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/fuzz/fuzz_helpers.c -->
# sources/compression/zstd/tests/fuzz/fuzz_helpers.c

## Purpose
This helper implementation provides fuzz-specific utility functions shared across zstd fuzz targets.

## APIs and behavior
The implementation defines `FUZZ_malloc()`, `FUZZ_malloc_rand()`, and `FUZZ_memcmp()`. `FUZZ_malloc()` returns `NULL` for zero-size allocations and asserts successful allocation otherwise. `FUZZ_malloc_rand()` behaves similarly for nonzero sizes, but for zero-size requests it may return either `NULL` or a fuzz-selected junk pointer to stress APIs that must ignore zero-capacity buffers. `FUZZ_memcmp()` treats zero-size comparisons as equal before delegating to `memcmp()`.

## State, dependencies, risks, and test signals
There is no persistent state. Dependencies are standard allocation/memory behavior, assertions from the companion header, and `FUZZ_dataProducer_t` for randomized zero-size pointers. The main risk is global blast radius: allocation or comparison semantics affect many fuzz targets. Test signals include immediate assertion on unexpected allocation failure and round-trip targets aborting/asserting when `FUZZ_memcmp()` reports corruption.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/fuzz/fuzz_helpers.c -->
