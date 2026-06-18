# subset-b-007889 research

This grouped report covers the Tahoe-LAFS helper, monitoring, provisioning, Python 3 migration, integration vector, and simulator files assigned to `subset-b-007889`. Each section is bounded by the required source path markers so the reconciliation lane can split it into the mapped per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/integration/vectors/vectors.py -->
# sources/distributed-fs/tahoe-lafs/integration/vectors/vectors.py

## Purpose

This module loads and saves persisted integration test vectors for Tahoe-LAFS capability generation. It provides a small serialization layer around YAML test data, keeping byte strings JSON/YAML-safe with base64 and reconstructing `Case` objects that combine erasure-coding parameters, convergence secrets, sample data, object format, and expected capabilities.

## Important APIs, Types, and Functions

`DATA_PATH` points at sibling `test_vectors.yaml`, and `CURRENT_VERSION` gates compatibility with the persisted file. The frozen `Case` attrs class is the key domain type; its `data` property expands a seed into deterministic bytes via `stretch`, and `params` realizes abstract `SeedParam` values against the selected `CHK` or `SSK` format. `encode_bytes` and `decode_bytes` are the base64 transport helpers. `save_capabilities` writes a versioned YAML document from `(Case, capability)` pairs. `load_format` dispatches serialized format records to `CHK.load` or `SSK.load`, and `load_capabilities` validates the version then returns a `dict[Case, str]`.

## Control Flow

On import, the module tries to open `DATA_PATH` and initializes the module global `capabilities`; missing files produce an empty dict. Loading calls `yaml.safe_load`, treats an empty YAML document as no vectors, rejects mismatched versions by printing a diagnostic and returning `{}`, then builds `Case` keys from each vector entry. Saving performs the inverse transformation, deriving `required` and `total` from `case.params`, not directly from `seed_params`.

## State, Dependencies, Integration, Risks, and Tests

State is file-backed only when `save_capabilities` is called; import-time `capabilities` is an in-memory snapshot. Dependencies are `attrs`, PyYAML, Twisted `FilePath`, and local vector model/format classes. Integration points are the integration tests that compare generated capabilities with persisted expectations. Risks include import-time I/O, silent empty results on version mismatch, assertions in `stretch` being removable under optimized Python, and a requirement that `Case` remains hashable because it is used as a dict key. Test signals should cover round-trip save/load, unknown format errors, version mismatch behavior, base64 byte preservation, deterministic stretch output, and missing/empty YAML files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/integration/vectors/vectors.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/build_helpers/build-osx-pkg.sh -->
# sources/distributed-fs/tahoe-lafs/misc/build_helpers/build-osx-pkg.sh

## Purpose

This shell script builds the legacy macOS Tahoe-LAFS installer package. It creates a Python 2.7 virtualenv, installs the current project, rewrites the generated `tahoe` entry point so it resolves libraries from `/Applications/tahoe.app`, and invokes Apple packaging tools to produce `tahoe-lafs-$VERSION-osx.pkg`.

## Important APIs, Types, and Functions

The script is procedural. `VERSION` is extracted from `src/allmydata/_version.py` using shell text filters. `TARGET` is fixed to `/Applications/tahoe.app`. External tools are the effective API surface: `virtualenv`, `pip install .`, `pkgbuild`, and `productbuild`.

## Control Flow

It removes `_trial_temp`, creates `osx-venv`, installs Tahoe, removes all virtualenv bin scripts, writes a custom `bin/tahoe` launcher, creates a `zope/__init__.py` workaround, copies `misc/build_helpers/osx/Contents`, builds an intermediate component package with scripts and install location, wraps it with `Distribution.xml`, and deletes `tahoe-lafs.pkg`.

## State, Dependencies, Integration, Risks, and Tests

State is entirely filesystem side effects: `osx-venv`, generated launcher, intermediate package, final package, and cleanup. Integration points are `test-osx-pkg.py`, `Distribution.xml`, and the pre/postinstall scripts. Risks include hard-coded Python 2.7 and `/Applications/tahoe.app`, fragile version parsing, lack of `set -e`, shell word splitting on paths, and a launcher that is less isolated than a real virtualenv. Tests should verify the produced package installs the expected app tree and that `bin/tahoe --version-and-path` loads dependencies from the packaged tree.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/build_helpers/build-osx-pkg.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/build_helpers/check-build.py -->
# sources/distributed-fs/tahoe-lafs/misc/build_helpers/check-build.py

## Purpose

This helper validates build logs for the `test-desert-island` target. Its implemented mode checks that a build did not download packages from HTTP or HTTPS URLs.

## Important APIs, Types, and Functions

There are no reusable functions; it reads `sys.argv[1]` as a log file and `sys.argv[2]` as a mode. The only active mode is `no-downloads`, which flags lines beginning with `Downloading http:` or `Downloading https:`.

## Control Flow

The script initializes `good = True`, scans the build output line by line, prints offending download lines, and exits `0` with a success message or `1` with a failure message. It intentionally permits some `Reading` lines and local dependency references based on the comments.

## State, Dependencies, Integration, Risks, and Tests

There is no persistence beyond stdout and exit status. It depends only on Python stdlib and a build log path. Integration is Makefile/buildbot desert-island validation. Risks include trusting exact log prefixes, no argument validation, and no enforcement for metadata index reads. Test signals are small fixture logs with allowed local dependency references, disallowed HTTP/HTTPS downloads, and unknown modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/build_helpers/check-build.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/build_helpers/gen-package-table.py -->
# sources/distributed-fs/tahoe-lafs/misc/build_helpers/gen-package-table.py

## Purpose

This script generates an HTML dependency package table from directories containing Tahoe-LAFS dependency archives. It classifies archive filenames by package, Python version, and platform, then emits separate tables for platform-dependent and platform-independent packages.

## Important APIs, Types, and Functions

Global regexes `FILENAME_RE` and `FILENAME_RE2` parse egg/sdist/exe names. `platform_aliases` normalizes platform suffixes, and `min_supported_python` marks unsupported Windows Python versions. `add` appends values into a dict-of-lists. `file_list` sorts files using `pkg_resources.parse_version` and renders links.

## Control Flow

The script gathers filenames from `.` and `../tahoe-dep-sdists` unless arguments override the directories. For each supported extension, it parses package/version/Python/platform fields, normalizes platform names, records package membership, and populates `matrix[pythonver][platform]`. It then prints complete HTML 4.01 with one table per Python version for compiled/platform packages and one table for source or platform-independent artifacts.

## State, Dependencies, Integration, Risks, and Tests

State is in global sets and dictionaries during one run; output is stdout. Dependencies are `pkg_resources`, directory listings, and strict historical filename conventions. Integration is dependency mirror publishing. Risks include brittle regex parsing, direct HTML interpolation of filenames, assuming `matrix['']['']` exists, and old package naming assumptions. Tests should feed fixture directories with eggs, sdists, Windows installers, aliases, package-name continuations, and malformed files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/build_helpers/gen-package-table.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/build_helpers/icons/make-osx-icon.sh -->
# sources/distributed-fs/tahoe-lafs/misc/build_helpers/icons/make-osx-icon.sh

## Purpose

This Bash helper converts SVG icon inputs into macOS `.icns` files. It renders multiple PNG sizes into an `.iconset` directory and asks `iconutil` to build the final icon.

## Important APIs, Types, and Functions

The script has no functions. Its parameters are SVG paths. It uses resolution array `16 32 64 128 256 512 1024`, `inkscape` for rasterization, hard links or moves for retina `@2x` names, and `iconutil -c icns`.

## Control Flow

With no arguments it prints usage and exits successfully. Otherwise it creates `temp` under the current directory, loops over SVG inputs, renders all base sizes, constructs expected Apple iconset filenames, runs `iconutil`, and finally removes `temp`.

## State, Dependencies, Integration, Risks, and Tests

State is a temporary `./temp` tree and generated `.icns` files in the caller's working directory. Dependencies are Bash, Inkscape's legacy CLI options, and macOS `iconutil`. Risks include iterating over `"$*"` instead of `"$@"`, collisions in `./temp`, overwriting outputs, and hard-link failures across filesystems. Test signals are SVG fixtures with spaces in filenames, existing `temp`, and validation that generated `.icns` contains expected icon sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/build_helpers/icons/make-osx-icon.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/build_helpers/icons/make-windows-icon.sh -->
# sources/distributed-fs/tahoe-lafs/misc/build_helpers/icons/make-windows-icon.sh

## Purpose

This Bash helper converts SVG icon inputs into Windows `.ico` files. It renders several PNG sizes and combines them with ImageMagick.

## Important APIs, Types, and Functions

The parameter interface is a list of SVG files. Dependencies are `mktemp`, `inkscape`, and ImageMagick `convert`. The resolution set is `16 24 32 48 64 256`.

## Control Flow

With no arguments it prints usage and exits `0`. Otherwise it creates a temp directory, loops over SVG inputs, renders PNGs into a per-icon subdirectory, builds a list of generated PNG paths, calls `convert ... "${f%%.*}.ico"`, and removes the temp directory.

## State, Dependencies, Integration, Risks, and Tests

State is temporary raster files and generated `.ico` outputs. Integration is Windows packaging or icon asset preparation. Risks include `"$*"` collapsing multiple arguments, `${f%%.*}` stripping at the first dot in the whole path, dependency on legacy Inkscape flags, and no `set -e` despite destructive cleanup. Tests should cover multiple SVGs, dotted pathnames, filenames with spaces, and verifying the ICO contains all intended sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/build_helpers/icons/make-windows-icon.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/build_helpers/osx/Distribution.xml -->
# sources/distributed-fs/tahoe-lafs/misc/build_helpers/osx/Distribution.xml

## Purpose

This macOS installer distribution file describes the product archive created by `productbuild` for Tahoe-LAFS. It defines installer UI metadata, platform checks, component package selection, and license text.

## Important APIs, Types, and Functions

The important XML elements are `<options>`, `<installation-check>`, `<volume-check>`, `<choices-outline>`, `<choice>`, `<pkg-ref>`, and `<license>`. The embedded JavaScript installation check requires `system.sysctl('hw.machine') == 'x86_64'`. The volume check requires macOS 10.7 or newer.

## Control Flow

Installer.app evaluates the architecture check first, validates allowed OS versions, displays a non-customizable single-package install choice, and installs `tahoe-lafs.pkg` as `com.leastauthority.tahoe` with root authorization.

## State, Dependencies, Integration, Risks, and Tests

The XML itself is static packaging metadata. It integrates with `build-osx-pkg.sh` and the package scripts. Risks include a hard-coded `version="1.10.0"` that may diverge from the package build version, x86_64-only assumptions, and stale license text. Tests should run `productbuild`, inspect the produced distribution, and attempt installer validation on supported and unsupported target metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/build_helpers/osx/Distribution.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/build_helpers/osx/scripts/postinstall -->
# sources/distributed-fs/tahoe-lafs/misc/build_helpers/osx/scripts/postinstall

## Purpose

This macOS package postinstall hook registers Tahoe's application binary and manpage directories with system path lookup mechanisms.

## Important APIs, Types, and Functions

The script is procedural Bash. It appends `/Applications/tahoe.app/bin/` to `/etc/paths.d/tahoe` and `/Applications/tahoe.app/docs/man/` to `/etc/manpaths.d/tahoe`.

## Control Flow

After package payload installation, Installer runs this script as root. It captures `PWD` but does not use it, then appends the two path records.

## State, Dependencies, Integration, Risks, and Tests

Persistent state is in `/etc/paths.d/tahoe` and `/etc/manpaths.d/tahoe`. Integration is the macOS package built by `pkgbuild --scripts`. Risks include appending duplicate lines on repeated installs, no error handling, and mismatch with preinstall cleanup path `/etc/manpaths.d/tahoe.1`. Tests should install twice and verify idempotence or duplicate behavior, then confirm shells and `manpath` can discover the installed app paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/build_helpers/osx/scripts/postinstall -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/build_helpers/osx/scripts/preinstall -->
# sources/distributed-fs/tahoe-lafs/misc/build_helpers/osx/scripts/preinstall

## Purpose

This macOS package preinstall hook removes an existing Tahoe application tree and stale system path registration before a new package install.

## Important APIs, Types, and Functions

The script is Bash with three direct filesystem operations: recursively remove `/Applications/tahoe.app`, remove `/etc/paths.d/tahoe`, and remove `/etc/manpaths.d/tahoe.1` if each exists.

## Control Flow

Installer runs this before payload installation. Each path is checked and removed independently.

## State, Dependencies, Integration, Risks, and Tests

Persistent effects are destructive removal of the app bundle and path files. Integration is `pkgbuild --scripts`. Risks include deleting local user modifications under `/Applications/tahoe.app`, no quoting issue for these constant paths but no error handling, and the likely typo/mismatch where postinstall writes `/etc/manpaths.d/tahoe` but preinstall removes `/etc/manpaths.d/tahoe.1`. Tests should simulate upgrade installs and verify old app files and both possible manpath files are handled as expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/build_helpers/osx/scripts/preinstall -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/build_helpers/run-deprecations.py -->
# sources/distributed-fs/tahoe-lafs/misc/build_helpers/run-deprecations.py

## Purpose

This Twisted-based wrapper runs a command, captures stdout/stderr, and fails the build if relevant Python deprecation warnings are seen. It can restrict warning collection to a specific package path and optionally write the collected warnings to a file.

## Important APIs, Types, and Functions

`Options` parses `--warnings`, `--package`, command, and command args. `RunPP` is a `ProcessProtocol` that mirrors child output to parent stdout/stderr while buffering bytes. `make_matcher` builds a regex matcher for deprecation-looking file/line records. `run_command` resolves the executable with `twisted.python.procutils.which`, spawns it, de-duplicates matching lines, writes the warnings log, and exits with command status or failure.

## Control Flow

`task.react(run_command)` drives the whole script. The child process runs under `reactor.spawnProcess`. After process completion, the script scans both buffered streams, preserving order within each stream and suppressing duplicates. Any warning forces `sys.exit(1)` regardless of the command's own return code; otherwise the wrapper exits with the child signal or exit code.

## State, Dependencies, Integration, Risks, and Tests

State is transient buffers plus optional warnings output file. Dependencies are Twisted reactor/process APIs and Python encoding settings. Integration is buildbot/test commands run with warnings enabled. Risks include regex overmatching any `.py:line:` record, decoding with `sys.stdout.encoding`, stdout/stderr ordering not preserved across streams, and signal exit values being used directly. Tests should use child commands emitting duplicate warnings, non-warning tracebacks, package-filtered paths, nonzero exits, and missing executables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/build_helpers/run-deprecations.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/build_helpers/show-tool-versions.py -->
# sources/distributed-fs/tahoe-lafs/misc/build_helpers/show-tool-versions.py

## Purpose

This diagnostic script prints platform, Python, locale, compiler/tool, and selected Python package versions for build logs.

## Important APIs, Types, and Functions

`foldlines` collapses multi-line command output. `print_platform`, `print_python_ver`, and `print_python_encoding_settings` report interpreter and locale metadata. `print_stdout` runs an external command and prints a compact label. `print_as_ver` handles assembler version probing while avoiding clobbering an existing `a.out`. `print_setuptools_ver` and `print_py_pkg_ver` use `importlib.metadata.version` and optional module imports.

## Control Flow

The script runs all print helpers at import/execution time in a fixed order. Missing external commands are reported as "no such file or directory"; other `EnvironmentError`s print tracebacks but the script continues.

## State, Dependencies, Integration, Risks, and Tests

State is stdout/stderr logging and possible deletion of `a.out` only if the assembler creates it. Dependencies are many external tools (`virtualenv`, `tox`, `gcc`, `git`, `openssl`, etc.) and Python package metadata. Integration is CI/buildbot environment capture. Risks include stale package list, duplicate `cryptography` entry, command hangs because no timeout is used, and deprecated `locale.getdefaultlocale`. Tests should monkeypatch `subprocess.Popen` and metadata lookups to verify missing commands, multi-line folding, and PackageNotFound behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/build_helpers/show-tool-versions.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/build_helpers/test-git-ignore.py -->
# sources/distributed-fs/tahoe-lafs/misc/build_helpers/test-git-ignore.py

## Purpose

This helper checks whether the current working tree is clean according to `git status --porcelain`.

## Important APIs, Types, and Functions

It uses `subprocess.Popen(["git", "status", "--porcelain"], stdout=PIPE)` and compares the captured output with an empty string.

## Control Flow

The script runs the command, prints raw output, exits `0` if it thinks the output is empty, otherwise exits `1`.

## State, Dependencies, Integration, Risks, and Tests

There is no persistent state. Dependency is Git in the current repository. Integration is build validation for generated or ignored files. The major risk is Python 3 behavior: `communicate()[0]` is bytes, so comparing to `""` is always false; in Python 3 this script reports dirty even for clean output. Tests should run under Python 2 and Python 3 or compare to `b""`, with clean, modified, and untracked fixtures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/build_helpers/test-git-ignore.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/build_helpers/test-osx-pkg.py -->
# sources/distributed-fs/tahoe-lafs/misc/build_helpers/test-osx-pkg.py

## Purpose

This package test unpacks a macOS `.pkg` archive and verifies that `bin/tahoe --version-and-path` resolves packaged dependencies from the extracted app tree, except for a small set allowed from the OS installation.

## Important APIs, Types, and Functions

`test_osx_pkg(pkgfile)` is the main reusable function. It creates a temp directory, runs `xar`, extracts `Payload` through `gunzip` and `cpio`, runs `bin/tahoe --version-and-path`, then applies `PKG_VER_PATH_RE` to dependency lines. The script entry point selects the single `*-osx.pkg` in the current directory.

## Control Flow

Failures raise exceptions or exit nonzero. The temp directory is removed in `finally` after package extraction and command validation. Dependency path checks reject any parsed package path not under the extraction directory unless the package is `zope.interface`, `python`, `platform`, or `pyOpenSSL`.

## State, Dependencies, Integration, Risks, and Tests

State is temporary filesystem extraction under `/tmp`. Dependencies are macOS `xar`, `gunzip`, `cpio`, and the packaged `bin/tahoe`. Integration is the output from `build-osx-pkg.sh`. Risks include `os.chdir` side effects, no return-code checks for `gunzip`/`cpio`, regex type mismatch under Python 3 because `stdouttxt` is bytes but the regex is text, and hard-coded allowed system packages. Tests should mock subprocesses, validate cleanup, include dependency paths inside and outside basedir, and exercise missing/multiple package detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/build_helpers/test-osx-pkg.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/build_helpers/update-version.py -->
# sources/distributed-fs/tahoe-lafs/misc/build_helpers/update-version.py

## Purpose

This release helper computes the next Tahoe-LAFS release version from existing Git tags and optionally creates an annotated signed tag.

## Important APIs, Types, and Functions

`existing_tags(git)` reads Dulwich tags beginning with `tahoe-lafs-` and parses them as `packaging.version.Version`. `create_new_version(git)` increments the highest tag's minor version and resets patch to zero. `main(reactor)` checks repository cleanliness, handles `--no-tag`, computes a UTC-day-quantized tag timestamp, and calls `dulwich.porcelain.tag_create`.

## Control Flow

The script runs under Twisted `react`. It aborts on staged or unstaged changes. With `--no-tag`, it prints the computed version only. Otherwise it prints existing tags, creates `tahoe-lafs-X.Y.0` on `HEAD`, and prints a push hint.

## State, Dependencies, Integration, Risks, and Tests

Persistent state is a new local Git tag. Dependencies are Dulwich, Twisted, and `packaging`. Integration is manual release workflow. Risks include failure when no matching tags exist, minor-only version policy, hard-coded signing identity, local-time `datetime.now()` mixed with UTC tuple conversion, and a push hint missing the `tahoe-lafs-` prefix. Tests should use temporary Dulwich repos for clean/dirty states, tag parsing, `--no-tag`, and timestamp/signing arguments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/build_helpers/update-version.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/checkers/check_grid.py -->
# sources/distributed-fs/tahoe-lafs/misc/checkers/check_grid.py

## Purpose

This operational checker exercises a pre-existing Tahoe grid through the CLI to verify that a new client can read old data, modify old and recent directories, upload new immutable data, and update mutable files.

## Important APIs, Types, and Functions

`GridTesterOptions` parses `--no`, a node directory, and a `tahoe` executable. `GridTester.command` wraps `subprocess.Popen` and return-code validation. `cli` prefixes commands with `tahoe -d NODEDIR`. Workflow helpers include `read_and_check`, `delete_and_check`, `listdir`, `put`, `put_mutable`, `update`, and `makefile`. `do_test` is the scenario driver.

## Control Flow

The script lists `testgrid:`, reads and checksum-validates `old.*` and `recent.*` files, deletes recent files, repeats similar checks in `recentdir`, recreates `recentdir`, uploads fresh random files named by MD5, appends timestamps to mutable logs, deletes `recentlog`, and recreates it as mutable.

## State, Dependencies, Integration, Risks, and Tests

State is remote Tahoe grid mutation plus local random data. Dependencies are Twisted `usage`, Python 2 `md5`, the Tahoe CLI, a running client node, and configured `testgrid` alias. Risks include destructive deletes, Python 2 string/bytes assumptions, no timeout around CLI commands, and md5 values embedded in filenames as the correctness oracle. Test signals are best provided by an isolated test grid fixture, with dry-run coverage for command construction and integration coverage for each CLI operation class.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/checkers/check_grid.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/checkers/check_load.py -->
# sources/distributed-fs/tahoe-lafs/misc/checkers/check_load.py

## Purpose

This load-generating client randomly reads and writes through Tahoe WebAPI nodes, maintaining atomic stats files that can be aggregated by a separate `--stats` mode.

## Important APIs, Types, and Functions

Top-level config files are `server-URLs`, `root.cap`, `delay`, and `operation-mix`. `listdir` fetches `?t=json` directory metadata. `choose_random_descendant` recursively chooses a file. `read_and_discard` streams file bytes. `create_random_directory`, `generate_filename`, and `choose_size` generate write targets. `parse_url` is copied URL parsing. `generate_and_put` uses `httplib` to stream a zero-filled PUT.

## Control Flow

In `--stats` mode, the script samples stats files every ten seconds and prints per-second deltas plus a moving average. In load mode, it repeatedly sleeps, randomly selects read or write according to configured weights, chooses a server URL, performs the operation, updates counters, writes `stats_out.tmp`, and atomically renames it to `stats_out`.

## State, Dependencies, Integration, Risks, and Tests

Persistent state is Tahoe grid content and the stats file. Dependencies are Python 2 networking modules, JSON WebAPI responses, and local config files. Integration is grid load testing and aggregate monitoring. Risks include infinite loops, no HTTP status validation after PUT, recursion into empty directories, bytes/text issues in Python 3 despite future annotations, and never incrementing `directories_written`. Tests should mock `urllib`/`httplib`, verify stats aggregation deltas, URL construction, atomic stats rename, and operation-mix selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/checkers/check_load.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/coding_tools/check-debugging.py -->
# sources/distributed-fs/tahoe-lafs/misc/coding_tools/check-debugging.py

## Purpose

This Python 3 coding check rejects production use of `defer.setDebugging(True)` in Python source files.

## Important APIs, Types, and Functions

There are no functions. It walks each `sys.argv[1:]` starting directory with `os.walk`, filters `.py` files except itself, and applies regex `\.setDebugging\(True\)`.

## Control Flow

The first match prints a policy error and the file/line, then exits `1`. If the scan completes, it prints a success message and exits `0`.

## State, Dependencies, Integration, Risks, and Tests

State is only process exit status. Dependencies are stdlib `os`, `re`, and source paths. Integration is CI linting. Risks include matching comments or strings, missing alternate whitespace/call forms, and not pruning virtualenv/build directories unless caller scopes the scan. Tests should use fixture files with real calls, comments, strings, and varied whitespace.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/coding_tools/check-debugging.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/coding_tools/check-interfaces.py -->
# sources/distributed-fs/tahoe-lafs/misc/coding_tools/check-interfaces.py

## Purpose

This legacy checker monkeypatches `zope.interface.implements` to verify class/interface conformance while importing Tahoe and Foolscap modules. It is intended to report all interface violations, not just the first.

## Important APIs, Types, and Functions

`strictly_implements` installs a class advisor that calls a forked `verifyClass` for classes in interesting modules. `check` monkeypatches `zi.implements`, walks a source directory, imports modules, and reports modules outside the interesting set. The forked verifier consists of `_verify`, `verifyClass`, `verifyObject`, and `_incompat`, using Zope interface method metadata.

## Control Flow

The script sets `sys.argv` to `['', '--help']` to reduce command-script side effects, imports every non-excluded `.py` module under `src` by default, warns for orphan `.pyc/.pyo`, handles Windows-only imports specially, and prints collected non-interesting module violations. On direct execution it calls `check()` then `os._exit(0)`.

## State, Dependencies, Integration, Risks, and Tests

State is global monkeypatching of `zope.interface.implements` and `_other_modules_with_violations`. Dependencies are old Zope interface APIs, Python 2 method attributes (`im_func`), and importability of the source tree. Risks include arbitrary import side effects, incompatibility with modern `zope.interface`, noisy false positives, and hard process exit. Tests should use small fixture packages with matching/mismatching interfaces and import failures, preferably in subprocess isolation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/coding_tools/check-interfaces.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/coding_tools/check-umids.py -->
# sources/distributed-fs/tahoe-lafs/misc/coding_tools/check-umids.py

## Purpose

This Python 3 checker ensures Foolscap/Tahoe `umid=` logging identifiers are unique across Python source files.

## Important APIs, Types, and Functions

The script walks supplied roots, scans `.py` files, skips lines without the substring `umid`, and extracts IDs with regex `umid=["']([^"']+)["']`. It stores first-use locations in `umids`.

## Control Flow

Every duplicate prints the duplicate location and first-use location and flips `ok` false. At the end, it prints either an all-clear message or a duplicate summary and exits `1`.

## State, Dependencies, Integration, Risks, and Tests

State is the in-memory `umids` dict. Integration is CI linting for incident classification maintainability. Risks include matching comments/strings, missing whitespace around `=`, and not validating ID length/charset. Tests should include unique IDs, duplicates, commented examples, alternate quoting, and spacing variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/coding_tools/check-umids.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/coding_tools/coverage2el.py -->
# sources/distributed-fs/tahoe-lafs/misc/coding_tools/coverage2el.py

## Purpose

This helper converts `.coverage` data into an Emacs Lisp-readable hash table stored in `.coverage.el`, mapping absolute filenames to executable, covered, and uncovered line lists.

## Important APIs, Types, and Functions

`ElispReporter` subclasses `coverage.summary.SummaryReporter` and overrides `report`. It calls `find_code_units`, uses `self.coverage.analysis(cu)`, skips `coverage.misc.NoSource`, and writes Elisp `puthash` forms. `main` loads default coverage data, calls private `_harvest_data`, restricts include paths to `src/*`, and invokes the reporter.

## Control Flow

Execution is linear: instantiate coverage, load data, harvest, set config, write `.coverage.el`. For each code unit, executable lines and missing lines are turned into sorted numeric lists; covered lines are computed as `executable - missing`.

## State, Dependencies, Integration, Risks, and Tests

Persistent state is `.coverage.el`. Dependencies are an older coverage.py API and Emacs Lisp consumers. Risks include private `_harvest_data`, unescaped quote/backslash characters in filenames, stale coverage API names, and overwriting `.coverage.el`. Tests should use a tiny coverage database fixture, a missing-source file, and filenames requiring Elisp string escaping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/coding_tools/coverage2el.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/coding_tools/fixshebangs.py -->
# sources/distributed-fs/tahoe-lafs/misc/coding_tools/fixshebangs.py

## Purpose

This script rewrites exact `#!/usr/bin/python` shebangs to `#!/usr/bin/env python` for files named on the command line.

## Important APIs, Types, and Functions

It uses regex `^#! */usr/bin/python *$`, `allmydata.util.fileutil.ReopenableNamedTemporaryFile`, and `shutil.move`.

## Control Flow

For each file, it opens the input in universal newline mode, writes either a replacement first line or original lines to a temp file, closes it, then tries to atomically move the temp file over the target. If overwrite fails, it moves the original to `.bak` and then is expected to continue with fallback logic in the omitted continuation; the visible code highlights non-atomic fallback risk.

## State, Dependencies, Integration, Risks, and Tests

State is rewritten source files plus possible `.bak` files. Dependencies are Tahoe `fileutil` and filesystem move semantics. Risks include truncation if interrupted in fallback, no preservation of file mode metadata in the visible path, Python 2-only `"rU"`, and matching only one exact shebang shape. Tests should cover matching and nonmatching first lines, permissions, atomic move failure, and newline preservation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/coding_tools/fixshebangs.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/coding_tools/graph-deps.py -->
# sources/distributed-fs/tahoe-lafs/misc/coding_tools/graph-deps.py

## Purpose

This dependency visualization tool builds or loads wheels for a target package, parses wheel metadata for runtime requirements and extras, emits a Graphviz DOT dependency graph, and renders it to `out.png`.

## Important APIs, Types, and Functions

`build_wheels` runs `pip wheel` and infers a root package name. `parse_metadata_json`, `parse_METADATA`, and `parse_wheels` populate global `all_packages`, `all_reqs`, and `all_pure`. `parse_spec` splits requirement strings into package, extras, and constraints. `scan` recursively marks base and extra dependency nodes. `generate_dot` writes package/extra nodes and colored edges. `dot_to_png` invokes `dot`. The Click command `go` coordinates all phases.

## Control Flow

If `--wheeldir` is an existing directory, wheels are reused; if it names a missing path, wheels are built there; otherwise a temporary directory is used. After metadata parsing, all base package nodes are shown, the root dependency tree is recursively scanned including requested extras, DOT is optionally written to `out.dot`, and Graphviz renders `out.png`.

## State, Dependencies, Integration, Risks, and Tests

Persistent state may include wheel dirs, `root_pkgname`, `out.dot`, and `out.png`. Dependencies are `pip`, wheel metadata formats, Click, and Graphviz. Risks include fragile root-name inference from pip output, global mutable state across invocations, incomplete PEP 508 marker parsing, recursion KeyErrors for missing dependency wheels, and unclosed zip files. Tests should use synthetic wheels with METADATA and metadata.json, extras, pure/non-pure WHEEL records, missing metadata, and DOT snapshot checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/coding_tools/graph-deps.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/coding_tools/make-canary-files.py -->
# sources/distributed-fs/tahoe-lafs/misc/coding_tools/make-canary-files.py

## Purpose

This operational tool generates per-server canary files whose storage index permutation places the first share on a desired Tahoe storage node for a chosen convergence secret and node list.

## Important APIs, Types, and Functions

`Options` parses convergence path, nodeids path, `k`, `N`, and verbosity. `get_permuted_peers(key)` reproduces Tahoe peer permutation with `sha1(key + nodeid)`. `find_share_for_target(target)` repeatedly constructs random content, asks Tahoe upload code for the storage index, checks the first permuted peer, and writes a `canaries/<nodeid>-<nickname>.txt` file on success.

## Control Flow

The script reads base32 node IDs and optional nicknames, decodes the convergence secret, warns if non-default k/N is used, creates `canaries`, and searches independently for each target node. It uses a Deferred-returning upload helper but relies on synchronous completion by inspecting `d.result`.

## State, Dependencies, Integration, Risks, and Tests

Persistent state is the generated `canaries` directory and files. Dependencies are Tahoe internals, Twisted usage, base32 helpers, SHA-1 permutation, and local convergence/nodeid files. Risks include Python 2 string/bytes mismatches, infinite expected search time for bad assumptions, failure if `canaries` already exists, reliance on Deferred internals, and needing patched Tahoe encoding parameters for non-default k/N. Tests should fix node IDs/convergence, monkeypatch storage index generation, and verify filename sanitization and permutation targeting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/coding_tools/make-canary-files.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/coding_tools/make_umid -->
# sources/distributed-fs/tahoe-lafs/misc/coding_tools/make_umid

## Purpose

This script creates short random message IDs for Foolscap `umid=` logging arguments so incidents can be traced back to source code.

## Important APIs, Types, and Functions

`make_id` reads four random bytes, base64 encodes them, rejects IDs containing `/` or `+`, removes padding, and returns the six-character-ish ID. The optional first command-line argument is a count.

## Control Flow

The script defaults to one ID, parses a count if supplied, and prints that many generated IDs. It loops inside `make_id` until the base64 alphabet produces an acceptable value.

## State, Dependencies, Integration, Risks, and Tests

There is no persistence except stdout. Dependencies are `os.urandom` and base64. Integration is developer/editor workflows plus `check-umids.py`. Risks include Python 3 bytes/string mismatches (`"/" in m` where `m` is bytes), no uniqueness check against the repository, and probabilistic collisions. Tests should monkeypatch `os.urandom` to cover rejection and padding removal, and verify count handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/coding_tools/make_umid -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/incident-gatherer/classify_tahoe.py -->
# sources/distributed-fs/tahoe-lafs/misc/incident-gatherer/classify_tahoe.py

## Purpose

This incident-gatherer classifier maps Tahoe Foolscap incident trigger dictionaries to stable category strings for known failure patterns.

## Important APIs, Types, and Functions

`umidmap` maps selected UMIDs to categories. `classify_incident(trigger)` checks `message`, `format`, `umid`, `facility`, `isError`, and `failure` fields, then returns a category or `None`.

## Control Flow

UMID matches win first. Message regexes classify mutable publish surprise shares, mutable query failures by source path and error type, mutable retrieve failures, bad private keys, and introducer connection loss/failure. Unrecognized triggers fall through to `None`.

## State, Dependencies, Integration, Risks, and Tests

State is static map data. Dependency is `re`. Integration is Foolscap incident classification, aided by `make_umid` and `check-umids.py`. Risks include brittle substring/traceback matching, stale UMIDs, conflating multiple cut-and-paste error sites, and missing structured fields. Tests should feed representative trigger dictionaries for every branch, including unknown mutable query locations and introducer failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/incident-gatherer/classify_tahoe.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/operations_helpers/cpu-watcher-poll.py -->
# sources/distributed-fs/tahoe-lafs/misc/operations_helpers/cpu-watcher-poll.py

## Purpose

This small Foolscap client polls a CPU watcher remote object for average CPU data and prints it.

## Important APIs, Types, and Functions

`fetch(furl)` creates a `Tub`, starts it, obtains a reference with `getReference`, calls remote `get_averages`, pretty-prints the result, and returns the Deferred. `oops` prints errors.

## Control Flow

The script schedules `fetch` from `eventual.fireEventually(sys.argv[1])`, attaches error and stop callbacks, and runs the Twisted reactor.

## State, Dependencies, Integration, Risks, and Tests

There is no persistence. Dependencies are Foolscap, Twisted reactor/eventual, and a watcher FURL argument. Integration is CPU watcher operations tooling. Risks include no argument validation, no timeout, and a Tub service that is not explicitly stopped. Tests should use a fake remote reference or Foolscap test tub to verify `get_averages`, formatting, and reactor shutdown on success/failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/operations_helpers/cpu-watcher-poll.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/operations_helpers/cpu-watcher-subscribe.py -->
# sources/distributed-fs/tahoe-lafs/misc/operations_helpers/cpu-watcher-subscribe.py

## Purpose

This Foolscap service subscribes to CPU watcher updates and prints average CPU records as they arrive.

## Important APIs, Types, and Functions

`RICPUWatcherSubscriber` defines remote `averages`. `CPUWatcherSubscriber` is both `service.MultiService` and `Referenceable`; it loads a FURL from a direct `pb://` string, a file, or `watcher.furl` inside a directory, connects via `Tub.connectTo`, requests current averages, subscribes itself, and prints remote updates in `remote_averages`.

## Control Flow

At top level, the subscriber is created from `sys.argv[1]`, started as a service, and the reactor runs indefinitely. On connection it fetches initial data and registers for callbacks; errors go to Twisted logging.

## State, Dependencies, Integration, Risks, and Tests

State is the live Foolscap connection and service tree. Dependencies are Foolscap schemas, Twisted service/reactor/log, and old `zope.interface.implements`. Integration is CPU watcher monitoring. Risks include Python 3 incompatibility from `implements`, no reconnect policy visible here, no argument validation, and no authentication policy beyond the FURL. Tests should use a fake watcher remote reference to check FURL loading, initial call, subscription call, and callback printing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/operations_helpers/cpu-watcher-subscribe.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/operations_helpers/find-share-anomalies.py -->
# sources/distributed-fs/tahoe-lafs/misc/operations_helpers/find-share-anomalies.py

## Purpose

This command analyzes `tahoe catalog-shares` outputs from storage servers to find storage indexes with inconsistent CHK/SDMF encodings or multiple SDMF versions.

## Important APIs, Types, and Functions

The script uses dictionaries keyed by storage index. For CHK and SDMF records, each value stores a set of observed encoding/version keys and the original catalog lines.

## Control Flow

It scans every input catalog file, splits each line, records CHK `(si, kN)` encodings, SDMF `(si, kN)` encodings, and SDMF versions. After scanning, it filters keys with more than one encoding or version and prints grouped reports with original lines.

## State, Dependencies, Integration, Risks, and Tests

State is in-memory anomaly maps. Dependencies are exact `catalog-shares` output fields. Integration is storage operations diagnostics. Risks include crashing on blank/malformed lines, ignoring MDMF or newer formats, and tuple shapes that redundantly include `si`. Tests should use small catalog fixtures for normal shares, duplicate encodings, duplicate versions, malformed lines, and mixed CHK/SDMF data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/operations_helpers/find-share-anomalies.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/operations_helpers/munin/tahoe_cpu_watcher -->
# sources/distributed-fs/tahoe-lafs/misc/operations_helpers/munin/tahoe_cpu_watcher

## Purpose

This Munin plugin graphs five-minute CPU averages reported by a CPU watcher JSON endpoint.

## Important APIs, Types, and Functions

It reads endpoint `url` from the environment, parses JSON as `(name, avg1, avg5, avg15)` records, sanitizes Munin field names with `re.sub(r'[^\w]', '_', name)`, and emits config or values.

## Control Flow

The script fetches current data before checking for `config`. It builds config labels for every process and value lines only when `avg5` is not `None`. With `config`, it prints graph metadata and exits; otherwise it prints current values.

## State, Dependencies, Integration, Risks, and Tests

There is no persistence. Dependencies are Munin environment conventions and Python 2 `urllib`. Integration is the CPU watcher service. Risks include network fetch during config calls, field-name collisions after sanitization, no timeout, and JSON shape assumptions. Tests should mock URL data, config/value modes, `None` averages, and colliding process names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/operations_helpers/munin/tahoe_cpu_watcher -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/operations_helpers/munin/tahoe_diskleft -->
# sources/distributed-fs/tahoe-lafs/misc/operations_helpers/munin/tahoe_diskleft

## Purpose

This Munin plugin graphs total available disk space reported by the diskwatcher web endpoint.

## Important APIs, Types, and Functions

The plugin reads `url` from the environment and expects JSON containing an `available` field.

## Control Flow

If invoked with `config`, it prints static Munin graph metadata and exits. Otherwise it fetches JSON from `url` and prints `disk_left.value`.

## State, Dependencies, Integration, Risks, and Tests

No persistent state is kept. Dependencies are Munin, Python 2 `urllib`, JSON, and the diskwatcher schema. Risks are missing env vars, no network timeout, and KeyError on schema changes. Tests should cover config mode, mocked endpoint data, and missing fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/operations_helpers/munin/tahoe_diskleft -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/operations_helpers/munin/tahoe_disktotal -->
# sources/distributed-fs/tahoe-lafs/misc/operations_helpers/munin/tahoe_disktotal

## Purpose

This Munin plugin graphs total and used disk capacity across the grid from diskwatcher JSON.

## Important APIs, Types, and Functions

It reads `url`, expects JSON keys `total` and `used`, and emits Munin fields `disk_total` and `disk_used`.

## Control Flow

`config` mode prints graph title, vlabel, category, and field draw styles. Normal mode fetches the endpoint and prints both values.

## State, Dependencies, Integration, Risks, and Tests

State is none. Integration is diskwatcher-to-Munin monitoring. Risks include endpoint failure causing plugin failure, no validation of numeric values, and Python 2 dependencies. Tests should mock JSON responses for config and normal paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/operations_helpers/munin/tahoe_disktotal -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/operations_helpers/munin/tahoe_diskusage -->
# sources/distributed-fs/tahoe-lafs/misc/operations_helpers/munin/tahoe_diskusage

## Purpose

This Munin plugin graphs estimated disk usage growth rates across one-hour, one-day, two-week, and four-week windows.

## Important APIs, Types, and Functions

It expects diskwatcher JSON key `rates`, where each item is `(name, timespan, growth, timeleft)`. It maps names to growth bytes per second and emits `rate_1hr`, `rate_1day`, `rate_2wk`, and `rate_4wk` when present.

## Control Flow

Config mode prints static graph metadata with lower-limit settings. Normal mode fetches rates, builds a name-to-growth dict, and conditionally prints available windows.

## State, Dependencies, Integration, Risks, and Tests

No persistence. Dependencies are diskwatcher rate schema and Munin. Risks include silently omitting windows, no timeout, and division/typing assumptions delegated to diskwatcher. Tests should cover partial rate sets, all windows, and malformed tuples.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/operations_helpers/munin/tahoe_diskusage -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/operations_helpers/munin/tahoe_diskused -->
# sources/distributed-fs/tahoe-lafs/misc/operations_helpers/munin/tahoe_diskused

## Purpose

This Munin plugin graphs total disk bytes used across the grid from diskwatcher.

## Important APIs, Types, and Functions

It reads env `url`, loads JSON, and emits the `used` value as `disk_used.value`.

## Control Flow

`config` prints static metadata. Normal mode fetches and prints one value.

## State, Dependencies, Integration, Risks, and Tests

There is no persistent state. Integration is diskwatcher monitoring. Risks are missing env/config, network failures, and schema KeyError. Tests should validate config output and mocked `used` JSON.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/operations_helpers/munin/tahoe_diskused -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/operations_helpers/munin/tahoe_doomsday -->
# sources/distributed-fs/tahoe-lafs/misc/operations_helpers/munin/tahoe_doomsday

## Purpose

This Munin plugin graphs estimated days remaining before storage exhaustion, using diskwatcher growth-rate projections.

## Important APIs, Types, and Functions

It reads `rates` from JSON and maps each rate name to `timeleft` seconds when nonzero. It converts seconds to days with `DAY = 24*60*60`.

## Control Flow

Config mode prints four days-left series. Normal mode fetches rates, filters falsy `timeleft`, and emits present windows divided by `DAY`.

## State, Dependencies, Integration, Risks, and Tests

No state is persisted. Integration is capacity planning in Munin. Risks include omitting zero/None projections, no timeout, Python 2 integer division depending on value types, and stale assumptions about rate names. Tests should cover zero, None, and positive timeleft values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/operations_helpers/munin/tahoe_doomsday -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/operations_helpers/munin/tahoe_estimate_files -->
# sources/distributed-fs/tahoe-lafs/misc/operations_helpers/munin/tahoe_estimate_files

## Purpose

This Munin plugin estimates total files/directories in a grid by sampling storage-index directories from a configured subset of storage servers.

## Important APIs, Types, and Functions

The script uses hard-coded `node_dirs`, sampled two-character `sections`, encoding parameter `N = 10`, and `num_servers = 20`. It counts unique storage index strings and applies a correction based on probability that a file is absent from sampled servers.

## Control Flow

Config mode prints one graph field. Normal mode lists storage share sections under each node dir, builds a set of index strings, computes `chance = N / num_servers`, `no_chance = (1 - chance) ** len(node_dirs)`, extrapolates across all 1024 sections, and prints `files.value`.

## State, Dependencies, Integration, Risks, and Tests

State is local filesystem reads only. Integration is rough operational estimation. Risks include hard-coded production paths, unhandled missing directories, simplistic correction formula, and assumptions about Tahoe share directory fanout and encoding. Tests should build temporary share trees and validate extrapolation for known samples, plus missing sections.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/operations_helpers/munin/tahoe_estimate_files -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/operations_helpers/munin/tahoe_files -->
# sources/distributed-fs/tahoe-lafs/misc/operations_helpers/munin/tahoe_files

## Purpose

This Munin plugin counts share files under one or more Tahoe node storage directories.

## Important APIs, Types, and Functions

It discovers node directories from environment variables named `basedir_NODE`, emits one Munin series per node, and walks `storage/shares`, excluding the top-level `incoming` directory.

## Control Flow

The script builds sorted `(nodename, basedir)` pairs. Config mode prints labels/draw styles. Normal mode walks each storage root and prints the count of filenames.

## State, Dependencies, Integration, Risks, and Tests

State is local filesystem traversal. Integration is per-node Munin monitoring. Risks include field names taken directly from env suffixes, expensive full tree walks, symlink traversal behavior inherited from `os.walk`, and no handling for missing roots. Tests should use temporary share trees with `incoming`, multiple nodes, and empty/missing directories.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/operations_helpers/munin/tahoe_files -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/operations_helpers/munin/tahoe_helperstats_active -->
# sources/distributed-fs/tahoe-lafs/misc/operations_helpers/munin/tahoe_helperstats_active

## Purpose

This Munin plugin graphs the number of active upload-helper files.

## Important APIs, Types, and Functions

It reads JSON from env `url` and emits `chk_upload_helper.active_uploads` as `fetched.value`; the field name is historically `fetched` despite representing active files.

## Control Flow

Config mode prints graph metadata. Normal mode fetches JSON and prints the active upload count.

## State, Dependencies, Integration, Risks, and Tests

No persistence. Integration is Tahoe upload-helper statistics monitoring. Risks include misleading graph vlabel/field name, no timeout, and KeyError on stats changes. Tests should cover config output and JSON fixtures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/operations_helpers/munin/tahoe_helperstats_active -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/operations_helpers/munin/tahoe_helperstats_fetched -->
# sources/distributed-fs/tahoe-lafs/misc/operations_helpers/munin/tahoe_helperstats_fetched

## Purpose

This Munin plugin graphs bytes fetched by the Tahoe CHK upload helper.

## Important APIs, Types, and Functions

It fetches JSON from env `url` and emits `chk_upload_helper.fetched_bytes` as a GAUGE field named `fetched`.

## Control Flow

Config mode prints static metadata including min zero. Normal mode prints the fetched byte value.

## State, Dependencies, Integration, Risks, and Tests

State is none. Integration is upload-helper Munin monitoring. Risks include treating what may be a counter as a gauge, endpoint failures, and Python 2 urllib reliance. Tests should mock stats JSON and verify both modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/operations_helpers/munin/tahoe_helperstats_fetched -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/operations_helpers/munin/tahoe_introstats -->
# sources/distributed-fs/tahoe-lafs/misc/operations_helpers/munin/tahoe_introstats

## Purpose

This Munin plugin graphs introducer announcement/subscription counts for storage service participants.

## Important APIs, Types, and Functions

It reads JSON from env `url` and expects `announcement_summary`, `announcement_distinct_hosts`, and `subscription_summary`, each with a `storage` key.

## Control Flow

Config mode prints three series: storage servers, distinct storage hosts, and clients. Normal mode fetches JSON and prints values for those keys.

## State, Dependencies, Integration, Risks, and Tests

No persistent state. Integration is Tahoe introducer stats endpoint monitoring. Risks include schema KeyError, no timeout, and only storage service support. Tests should use fixture JSON for normal output and missing-key behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/operations_helpers/munin/tahoe_introstats -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/operations_helpers/munin/tahoe_nodememory -->
# sources/distributed-fs/tahoe-lafs/misc/operations_helpers/munin/tahoe_nodememory

## Purpose

This Munin plugin reads Tahoe node `twistd.pid` files and graphs process memory from `/proc/<pid>/status`.

## Important APIs, Types, and Functions

It discovers nodes from env vars named `nodememory_NODE`, reads `twistd.pid`, extracts `VmSize` and `VmRSS`, and emits byte values by multiplying reported kB by 1024.

## Control Flow

After collecting pids, config mode prints one series per node/field. Normal mode reads `/proc` status for live pids and prints available field values.

## State, Dependencies, Integration, Risks, and Tests

State is local procfs and pid files. Integration is Linux Munin monitoring. Risks include Python 3 failure from `list.sort(lambda...)`, stale pids, permission/read races, unsanitized node names, and Linux-only `/proc` assumptions. Tests should use temporary pid files with mocked `/proc` paths or refactorable reader fixtures, including vanished pids.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/operations_helpers/munin/tahoe_nodememory -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/operations_helpers/munin/tahoe_overhead -->
# sources/distributed-fs/tahoe-lafs/misc/operations_helpers/munin/tahoe_overhead

## Purpose

This Munin plugin estimates Tahoe storage overhead by comparing actual disk usage with ideal encoded deep size and inactive-account size metrics.

## Important APIs, Types, and Functions

It reads `diskwatcher_url` for JSON `used` and `deepsize_url` for JSON keys `all` and `active`. It assumes `k=3`, `N=10`, computes ideal expansion, overhead percentage, effective expansion, and inactive savings.

## Control Flow

Config mode prints overhead, inactive, and hidden effective-expansion fields. Normal mode fetches both endpoints, prints overhead and effective expansion only if overhead is positive, and always prints inactive savings.

## State, Dependencies, Integration, Risks, and Tests

No persistence. Integration is capacity/garbage monitoring. Risks include hard-coded 3-of-10, division by zero for empty active/all values, suppressing negative overhead, no timeout, and external PHP/deepsize dependency. Tests should cover positive/negative overhead, inactive calculations, and zero deep-size guards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/operations_helpers/munin/tahoe_overhead -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/operations_helpers/munin/tahoe_rootdir_space -->
# sources/distributed-fs/tahoe-lafs/misc/operations_helpers/munin/tahoe_rootdir_space

## Purpose

This Munin plugin graphs the deep size of files reachable from a configured Tahoe root directory, as exposed by an external URL.

## Important APIs, Types, and Functions

It reads env `url`, expects the response body to be an integer, and emits `space.value`.

## Control Flow

Config mode prints one graph field. Normal mode fetches, strips, converts to `int`, and prints the value.

## State, Dependencies, Integration, Risks, and Tests

State is none. Integration depends on another service producing root-directory size. Risks include no timeout, unvalidated response text, and Python 2 urllib. Tests should cover config output, valid integer bodies, and invalid body failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/operations_helpers/munin/tahoe_rootdir_space -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/operations_helpers/munin/tahoe_server_latency_ -->
# sources/distributed-fs/tahoe-lafs/misc/operations_helpers/munin/tahoe_server_latency_

## Purpose

This symlink-target Munin plugin graphs a selected storage-server latency metric and percentile for multiple Tahoe nodes.

## Important APIs, Types, and Functions

The script discovers node stats URLs from env vars named `url_NODE`. It derives `operation` and `percentile` from its executable basename after prefix `tahoe_server_latency_`. Percentiles map to stats keys like `storage_server.latencies.<operation>.<percentile>_percentile`; `mean` maps to `mean`.

## Control Flow

It builds config labels for each node. Config mode prints graph metadata based on the derived operation/percentile. Normal mode fetches each node's `statistics?t=json`, reads `data["stats"][key]`, and prints one Munin value per node.

## State, Dependencies, Integration, Risks, and Tests

No persistence. Integration is via symlinks such as `tahoe_server_latency_allocate_99_9`. Risks include assertion failure on wrong symlink name, `split("_", 1)` ambiguity if operation names contain underscores, no timeout, unsanitized node names, and KeyError on missing stats. Tests should invoke through fake `argv[0]` names for mean and percentile cases and fixture JSON per node.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/operations_helpers/munin/tahoe_server_latency_ -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/operations_helpers/munin/tahoe_server_operations_ -->
# sources/distributed-fs/tahoe-lafs/misc/operations_helpers/munin/tahoe_server_operations_

## Purpose

This symlink-target Munin plugin graphs per-second storage server operation counters for multiple Tahoe nodes.

## Important APIs, Types, and Functions

It discovers env `url_NODE` endpoints and derives `operation` from basename prefix `tahoe_server_operations_`. It reads `data["counters"]["storage_server.<operation>"]` and emits DERIVE fields with min zero.

## Control Flow

Config mode prints graph metadata and one series per node. Normal mode fetches every node stats endpoint and prints current counter values.

## State, Dependencies, Integration, Risks, and Tests

State is none. Integration is Munin symlinks such as `tahoe_server_operations_allocate`. Risks include bad symlink assertions, no network timeouts, node-name field issues, and missing counter keys. Tests should cover config/value modes, multiple nodes, and bad `argv[0]`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/operations_helpers/munin/tahoe_server_operations_ -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/operations_helpers/munin/tahoe_spacetime -->
# sources/distributed-fs/tahoe-lafs/misc/operations_helpers/munin/tahoe_spacetime

## Purpose

This Munin plugin estimates days until storage exhaustion by fetching remote RRD files, summing disk-free data, extrapolating recent growth, and writing a JSON sidecar for web use.

## Important APIs, Types, and Functions

Constants define a Munin host, RRD filenames, local paths, and `WEBFILE`. `rsync_rrd` copies remote RRDs. `format_time` formats timestamps. `predict_future(past_s)` uses `rrdtool.fetch` to compute average start/end disk usage and remaining days. `write_to_file(samples)` atomically writes JSON-like output.

## Control Flow

Config mode prints two series. Normal mode currently does not call `rsync_rrd`; it predicts four-week and two-week remaining days from local RRDs, prints values when available, and writes available samples to `/var/www/tahoe/spacetime.json`.

## State, Dependencies, Integration, Risks, and Tests

Persistent state is `WEBFILE` and local RRD reads. Dependencies are `rrdtool`, rsync if enabled, hard-coded production RRD paths, and Munin. Risks include hard-coded infrastructure, `os.system` shell command construction, assertions for rsync failures, assuming the fourth-from-last RRD point is valid, and writing non-general JSON manually. Tests should mock `rrdtool.fetch`, cover None data paths, positive/negative growth, and atomic write content.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/operations_helpers/munin/tahoe_spacetime -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/operations_helpers/munin/tahoe_stats -->
# sources/distributed-fs/tahoe-lafs/misc/operations_helpers/munin/tahoe_stats

## Purpose

This generic Munin plugin renders many Tahoe stats/counter graphs from a shared JSON stats file. The specific graph is selected by the plugin executable name or symlink name.

## Important APIs, Types, and Functions

`PLUGINS` maps graph names to a stats key, category (`stats` or `counters`), config header, per-node config template, and value template. `smash_name` sanitizes node names. `open_stats` loads JSON. `main(argv)` selects plugin config, finds the first env var beginning with `statsfile`, filters stale node records with `STAT_VALIDITY = 300`, and emits config or values.

## Control Flow

The basename of `argv[0]` determines the plugin entry. The stats file is loaded once. Config mode prints graph header and per-node labels without age filtering. Normal mode skips nodes whose `timestamp` is older than five minutes and prints values only when the requested stat exists.

## State, Dependencies, Integration, Risks, and Tests

State is the external stats JSON file. Integration is Munin symlinks for runtime load, storage, helper, uploader, and mutable-file metrics. Risks include `plugin_conf` being `None` for unknown names, arbitrary first `statsfile*` env selection, stale filtering based on local clock, field-name collisions, and manual string interpolation. Tests should cover known/unknown plugin names, stale and fresh nodes, missing stat IDs, `.py` basename stripping, and config output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/operations_helpers/munin/tahoe_stats -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/operations_helpers/munin/tahoe_storagespace -->
# sources/distributed-fs/tahoe-lafs/misc/operations_helpers/munin/tahoe_storagespace

## Purpose

This Munin plugin reports disk bytes consumed by each configured Tahoe node's `storage` directory.

## Important APIs, Types, and Functions

It discovers env vars named `basedir_NODE`, builds config fields, and runs `du --bytes --summarize <basedir>/storage` through Python 2 `commands.getstatusoutput`.

## Control Flow

Config mode emits one series per node. Normal mode runs `du` for each node, exits with `du`'s return code on failure, parses the byte count, and prints `<node>.value`.

## State, Dependencies, Integration, Risks, and Tests

State is local filesystem measurement. Dependencies are GNU `du --bytes`, Python 2 `commands`, and Munin. Risks include shell injection or breakage from unquoted paths in the command string, portability issues on non-GNU systems, expensive scans, and unsanitized node names. Tests should mock command output, paths with spaces/shell metacharacters, and nonzero return codes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/operations_helpers/munin/tahoe_storagespace -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/operations_helpers/provisioning/provisioning.py -->
# sources/distributed-fs/tahoe-lafs/misc/operations_helpers/provisioning/provisioning.py

## Purpose

This Nevow page implements a provisioning calculator for Tahoe grids. It estimates user data volume, shares, server storage, ownership/lease overhead, rates, costs, drive replacement load, availability, and repair-survival properties from form-selected parameters.

## Important APIs, Types, and Functions

`div_ceil`, `factorial`, and `binomial` provide math helpers. `ProvisioningTool` is a `rend.Page` with `docFactory` pointing at `provisioning.xhtml`. `render_forms` adapts Nevow requests to `do_forms`. `do_forms(getarg)` builds all input selectors and conditional output sections. `file_availability(k, n, server_dBA)` approximates file availability in dBA, and `many_files_availability(file_dBA, num_files)` approximates aggregate availability across many files.

## Control Flow

For non-POST or unfilled forms, it builds inputs with defaults. When `filled` is true, it computes file and space totals, erasure expansion, per-server buckets/shares, share metadata overheads, client/server operation rates, drive/server cost estimates, drive failure rates, dBA availability, and worst-case check-interval survival. It returns a Nevow form assembled from generated sections and optionally links to the reliability page if importable.

## State, Dependencies, Integration, Risks, and Tests

State is request-local except for template loading. Dependencies are Nevow, local `util.sibling`, and math. Integration is `run.py`, `test_provisioning.py`, and the XHTML template. Risks include Python 2 division in `div_ceil`, many hard-coded historical constants/costs, approximation validity only for high availability, branchy form code with little validation, and hidden assumptions about 3-of-10 overhead sizes. Tests should cover default rendering, filled rendering for wraparound and ownership modes, binomial math, invalid encoding strings, and availability monotonicity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/operations_helpers/provisioning/provisioning.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/operations_helpers/provisioning/reliability.py -->
# sources/distributed-fs/tahoe-lafs/misc/operations_helpers/provisioning/reliability.py

## Purpose

This module simulates erasure-coded file reliability over time using Markov transition matrices for share loss and repair.

## Important APIs, Types, and Functions

Constants define day/month/year seconds. `ReliabilityModel.run` builds and advances unmaintained and maintained probability vectors. `p_in_period` computes exponential survival probability. `build_decay_matrix` and `build_decay_row` build share-count transition probabilities using `allmydata.util.statistics.binomial_distribution_pmf`. `build_repair_matrix` models deterministic repair when shares fall below `R` but remain at least `k`. `ReliabilityReport` stores sampled rows via `add_sample`.

## Control Flow

`run` computes drive survival per delta, creates decay and repair matrices, initializes all probability at `N` shares, then iterates through simulated time. Each delta decays both states; at check periods it computes repair probability/new-share expectation and applies repair to the maintained state; at report periods it records dead probabilities and cumulative repair metrics. A final sample is always added.

## State, Dependencies, Integration, Risks, and Tests

State is the returned `ReliabilityReport.samples` list. Dependencies are NumPy and Tahoe statistics utilities. Integration is `web_reliability.py` and `test_provisioning.py`. Risks include matrix/array shape sensitivity, `check_period = check_period - 1` timing subtlety, optimistic independence assumptions, Python 2 integer behavior, and old NumPy matrix APIs. Tests should assert row counts, matrix rows sum to one, repair matrix transitions, known probability outputs, and behavior for edge k/R/N values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/operations_helpers/provisioning/reliability.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/operations_helpers/provisioning/run.py -->
# sources/distributed-fs/tahoe-lafs/misc/operations_helpers/provisioning/run.py

## Purpose

This launcher starts a local Nevow web app exposing the provisioning and reliability calculators.

## Important APIs, Types, and Functions

`Root` is a Nevow `rend.Page` with links and child resources `child_reliability` and `child_provisioning`. `run(portnum)` creates the root, serves `tahoe.css`, starts a Twisted `strports` TCP service, opens a browser after one second, and runs the reactor.

## Control Flow

When executed directly, it defaults to port `8070` unless an argument overrides it, then calls `run`. The web server remains active until the reactor stops externally.

## State, Dependencies, Integration, Risks, and Tests

State is the live Twisted service and browser side effect. Dependencies are Twisted, Nevow, local calculator modules, and `webbrowser`. Risks include no error handling for occupied ports, automatic browser launch in noninteractive environments, and import failure if NumPy/Nevow are unavailable. Tests should instantiate `Root`, verify child resources, and exercise `run` with a fake reactor/service/browser.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/operations_helpers/provisioning/run.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/operations_helpers/provisioning/test_provisioning.py -->
# sources/distributed-fs/tahoe-lafs/misc/operations_helpers/provisioning/test_provisioning.py

## Purpose

This unittest module smoke-tests the provisioning calculator and reliability model.

## Important APIs, Types, and Functions

`Provisioning.getarg` reads values from `self.fields`. `test_load` calls `ProvisioningTool.do_forms` with empty and filled fields, including server wraparound and ownership modes. `test_provisioning_math` verifies selected binomial outputs. `Reliability.test_basic` checks NumPy vector/matrix multiplication, dot products, runs `ReliabilityModel`, and asserts known final probabilities.

## Control Flow

Reliability tests are skipped if the NumPy-backed model cannot be imported. Otherwise tests run under stdlib unittest and can be executed directly.

## State, Dependencies, Integration, Risks, and Tests

State is per-test `self.fields`. Dependencies are old import names `allmydata.provisioning` and `allmydata.reliability`, Nevow interface imports, NumPy, and unittest. Risks include tests importing modules from package locations different from the misc directory, Python 2 unittest methods (`failUnless*`), and brittle floating expected values. These tests themselves are the strongest signal for calculator smoke coverage but do not validate rendered HTML content or many invalid inputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/operations_helpers/provisioning/test_provisioning.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/operations_helpers/provisioning/util.py -->
# sources/distributed-fs/tahoe-lafs/misc/operations_helpers/provisioning/util.py

## Purpose

This utility module provides a path helper for files adjacent to the provisioning modules.

## Important APIs, Types, and Functions

`sibling(filename)` returns `os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)`.

## Control Flow

There is no control flow beyond the helper function.

## State, Dependencies, Integration, Risks, and Tests

No state is persisted. Dependency is `os.path`. Integration is template loading in `provisioning.py` and `web_reliability.py`. Risks are minimal; it assumes `__file__` is meaningful. Tests should verify it returns absolute paths in the module directory for known template filenames.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/operations_helpers/provisioning/util.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/operations_helpers/provisioning/web_reliability.py -->
# sources/distributed-fs/tahoe-lafs/misc/operations_helpers/provisioning/web_reliability.py

## Purpose

This Nevow page wraps `ReliabilityModel` in a web form and renders simulation results.

## Important APIs, Types, and Functions

`get_arg` reads query args and form fields through `IRequest`. `is_available` reports whether the imported reliability module is present. `yandm` formats seconds into years/months. `ReliabilityTool` defines `DEFAULT_PARAMETERS`, `parse_time`, `format_time`, `get_parameters`, `renderHTTP`, `make_input`, `render_forms`, `data_simulation_table`, and renderers for rows and summary values.

## Control Flow

On each HTTP render, it parses parameters from the request, runs `ReliabilityModel.run`, stores parameters/results on `self`, and delegates to Nevow rendering. Form rendering echoes parameter inputs. Data/render methods fill slots from `self.results.samples`, especially the last row for summary loss and repair metrics.

## State, Dependencies, Integration, Risks, and Tests

State is stored on the page instance per request, which can be risky if shared across concurrent requests. Dependencies are Nevow, NumPy-backed reliability, and templates. Integration is `run.py` and `reliability.xhtml`. Risks include division by zero when cumulative repairs are zero, Python 2 division in time formatting, unvalidated parameters, and concurrency leakage through instance attributes. Tests should exercise `parse_time`/`format_time`, default parameter parsing, render methods with synthetic reports, and zero-repair cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/operations_helpers/provisioning/web_reliability.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/operations_helpers/spacetime/diskwatcher.py -->
# sources/distributed-fs/tahoe-lafs/misc/operations_helpers/spacetime/diskwatcher.py

## Purpose

This Axiom model defines persisted disk usage samples for the diskwatcher subsystem and upgrades older samples to include total disk space.

## Important APIs, Types, and Functions

`Sample` is an `axiom.item.Item` with explicit `typeName = "diskwatcher_sample"` and `schemaVersion = 2`. Attributes are indexed `url`, indexed `when`, and integer `total`, `used`, and `avail`. `upgradeSample1to2(old)` calls `old.upgradeVersion` to add `total=0` while preserving existing fields. `registerUpgrader` registers the migration.

## Control Flow

Importing the module defines the item and registers the upgrader. Axiom invokes the upgrader when opening stores with version-1 `diskwatcher_sample` items.

## State, Dependencies, Integration, Risks, and Tests

Persistent state is the Axiom store schema and sample rows. Dependencies are Axiom item/attributes/upgrades. Integration is diskwatcher storage and Munin plugins consuming its aggregated JSON. Risks include defaulting `total` to zero for upgraded historical samples, schema name compatibility with auto-generated old names, and Axiom dependency age. Tests should create a version-1 item in a store, run upgrade, and verify all fields and indexes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/operations_helpers/spacetime/diskwatcher.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/python3/audit-dict-for-loops.py -->
# sources/distributed-fs/tahoe-lafs/misc/python3/audit-dict-for-loops.py

## Purpose

This Python 3 migration audit script runs `futurize`'s dict-loop fixer over all modules declared ported to Python 3, so developers can inspect diffs for unsafe mutation while iterating over dictionary views.

## Important APIs, Types, and Functions

`fix_potential_issue()` iterates `_python3.PORTED_MODULES + _python3.PORTED_TEST_MODULES`, maps module names to `src/...py` or package `__init__.py`, and runs `check_call(["futurize", "-f", "lib2to3.fixes.fix_dict", "-w", filename])`.

## Control Flow

When executed directly, it rewrites files in place and prints a reminder to inspect the diff. Missing `.py` module files are treated as packages.

## State, Dependencies, Integration, Risks, and Tests

Persistent state is modified source files. Dependencies are Tahoe `_python3` port lists and external `futurize`. Integration is manual Python 3 porting audits. Risks include broad in-place rewrites, typo in final message, failure if port lists include non-files, and no dry-run mode. Tests should monkeypatch `_python3` lists and `check_call`, and use a temporary fixture to verify module-to-path mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/python3/audit-dict-for-loops.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/python3/depgraph.sh -->
# sources/distributed-fs/tahoe-lafs/misc/python3/depgraph.sh

## Purpose

This CI shell script builds and publishes Tahoe dependency graph JSON files to the `gh-pages` branch of `tahoe-lafs/tahoe-depgraph`.

## Important APIs, Types, and Functions

It uses `git clone -b gh-pages`, runs `misc/python3/tahoe-depgraph.py`, checks `git diff-index --quiet HEAD`, configures a bot identity, commits `tahoe-deps.json` and `tahoe-ported.json`, and pushes only on CircleCI `master`.

## Control Flow

With `set -x` and `set -eo pipefail`, it clones the publishing repo, generates data from the current Tahoe checkout, exits without commit if unchanged, commits with source repo/SHA in the message, refuses to push on non-master branches, and pushes to `gh-pages` on master.

## State, Dependencies, Integration, Risks, and Tests

Persistent state is a cloned `tahoe-depgraph` directory and possibly a pushed commit. Dependencies are Git, CircleCI env vars, SSH credentials, and Python dependencies of `tahoe-depgraph.py`. Risks include fixed GitHub SSH target, no cleanup, publishing branch assumptions, and commit message depending on env vars. Tests should run in a temp repo with fake env vars and a mocked `git push`, verifying unchanged and changed cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/python3/depgraph.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/python3/tahoe-depgraph.py -->
# sources/distributed-fs/tahoe-lafs/misc/python3/tahoe-depgraph.py

## Purpose

This script generates JSON data describing internal `allmydata` module dependencies and Python 3 porting status.

## Important APIs, Types, and Functions

`mymf` subclasses `modulefinder.ModuleFinder`, recording `_depgraph`, `_types`, and `_last_caller`. It overrides `import_hook`, `import_module`, and `load_module` to capture imports between `allmydata` modules and module load types while skipping names ending `_py3`. `as_json` returns serializable dependency/type maps. `main(target)` discovers modules under `src/allmydata`, imports them via a temporary script, writes `tahoe-deps.json`, executes `_python3.py` to read port lists, and writes `tahoe-ported.json`.

## Control Flow

The walker excludes `test` directories, `setup.py`, and filenames containing hyphens. It uses Twisted `reflect.filenameToModuleName` to convert paths. The temporary script imports all discovered modules, causing modulefinder callbacks to populate the graph. Output JSON is sorted and indented.

## State, Dependencies, Integration, Risks, and Tests

Persistent state is `tahoe-deps.json` and `tahoe-ported.json` in the current directory. Dependencies are stdlib `modulefinder`, Twisted reflect, and executable Tahoe source. Integration is `depgraph.sh` publishing. Risks include executing `_python3.py` with `exec`, import side effects during analysis, old `modulefinder` APIs, skipped tests, and load-type values that may not be JSON-stable across Python versions. Tests should use a tiny package tree, assert dependency edges, skip behavior, and port-status extraction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/python3/tahoe-depgraph.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/simulators/bench_spans.py -->
# sources/distributed-fs/tahoe-lafs/misc/simulators/bench_spans.py

## Purpose

This benchmark replays recorded `DataSpans` operation traces and measures microsecond-level performance for increasing operation counts.

## Important APIs, Types, and Functions

Regex constants recognize `.get`, `.pop`, `.remove`, and `.add` trace lines; string constants recognize `.dump`, `.get_spans`, and initialization. Class `B` holds an input file and `DataSpans` instance. `B.init` resets state. `B.run(N)` reads up to `N` trace lines and invokes matching `DataSpans` methods.

## Control Flow

The script prints a benchmark footer/header, then for `N` values 600, 6000, and 60000 opens the trace file, creates `B`, and calls `benchutil.rep_bench` with `B.run` and `B.init`.

## State, Dependencies, Integration, Risks, and Tests

State is in-memory `DataSpans` mutation during replay. Dependencies are `pyutil.benchutil`, Tahoe `DataSpans`, regex trace format, and Python 2 `"rU"`. Risks include warning noise for unrecognized lines, replaying only a prefix for each benchmark, no validation of operation results, and allocating `'x' * length`. Tests should use tiny trace fixtures for every operation and assert calls on a fake spans object.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/simulators/bench_spans.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/simulators/count_dirs.py -->
# sources/distributed-fs/tahoe-lafs/misc/simulators/count_dirs.py

## Purpose

This estimator scans a native directory tree and approximates Tahoe directory metadata storage overhead under several hypothetical directory encoding modes.

## Important APIs, Types, and Functions

Constants `URI_SIZE` and `SLOTNAME_SIZE` model encoded targets. `slotsize(mode, numfiles, numdirs)` computes per-directory metadata size for modes `A`, `B1`, `B2`, `C1`, and `C2`. `scan(root)` walks the filesystem, adds filename string sizes and slot sizes, and prints totals.

## Control Flow

For each directory visited by `os.walk`, the script counts files/subdirs, adds joined filename lengths, accumulates all mode totals, then prints directory count, file count, and bytes per mode. Direct execution scans `sys.argv[1]`.

## State, Dependencies, Integration, Risks, and Tests

State is read-only filesystem traversal and in-memory counters. Integration is design exploration for Tahoe directory formats. Risks include approximate constants, no handling for filename encoding length versus Python string length, following `os.walk` defaults, and no argument validation. Tests should construct small directory trees and verify per-mode arithmetic for known file/subdir counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/simulators/count_dirs.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/simulators/hashbasedsig.py -->
# sources/distributed-fs/tahoe-lafs/misc/simulators/hashbasedsig.py

## Purpose

This exploratory simulator searches parameter combinations for a hash-based signature scheme combining GMSS-like Merkle layers, HORS leaf signatures, and generalized Winternitz signatures under size and CPU-cost limits.

## Important APIs, Types, and Functions

Global constants define hash length, signature-count security target, byte/cost limits, hash block parameters, and cycles per byte. Math helpers include `lg`, `ln`, `ceil_log`, `ceil_div`, `floor_div`, `compressions`, and `sum_powers`. `make_candidate` computes Mcycle costs and filters candidates. `calculate` searches `T`, `q`, Winternitz base `B`, and tree costs for one `(K, K1, K2)` combination. `search` precomputes efficient mixed binary/ternary Merkle tree shapes, scans candidate ranges, bins by cost, and prints Pareto-like best rows.

## Control Flow

The script prints global constraints, then `search()` iterates hash lengths. For each length it garbage-collects, precomputes tree shape costs up to `K_max`, loops over `K`, `K2`, and `K1`, calls `calculate`, filters candidates into cost bins, selects smallest signatures per nearby cost bin, sorts by signature size/cost, and prints rows that improve signing or verification cost.

## State, Dependencies, Integration, Risks, and Tests

State is CPU-heavy in-memory candidate lists and stderr progress. Dependencies are only stdlib math/gc/sys. Integration is research/design, not production Tahoe runtime. Risks include huge runtime, floating-point approximations for security probabilities, hard-coded search ranges, Python 2/3 differences from `pow` and print behavior mostly handled, and no unit tests. Test signals should target helper arithmetic, candidate filtering, small bounded `calculate` cases, and deterministic output with reduced ranges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/simulators/hashbasedsig.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/simulators/ringsim.py -->
# sources/distributed-fs/tahoe-lafs/misc/simulators/ringsim.py

## Purpose

This simulator compares Tahoe share placement on a simple ring versus per-file permuted peer lists, tracking usage spread and the point where servers fill or uploads wrap.

## Important APIs, Types, and Functions

`abbreviate_space` formats byte counts. `make_up_a_file_size` deterministically maps seeds to exponential file sizes using MD5. `Server` tracks node ID, capacity, used bytes, share count, and first-full tick. `Ring` builds sorted servers, returns either permuted or linear server order for a storage index, and reports usage distribution. `Options` parses k/N, server count, seeds, and permute flag. `do_run` performs uploads until the grid is full; `do_ring` prints expected upload count and initializes the ring.

## Control Flow

A global sample computes average file size. The run creates a ring, then for each generated file computes storage index, file size, share size, and server order. It tries to place `N` shares, skipping full servers and wrapping as needed. It reports first full server, first wrapped file, periodic usage stats, and final grid-full state.

## State, Dependencies, Integration, Risks, and Tests

State is simulated server usage only. Dependencies are Twisted `usage`, MD5, and deterministic seeds. Integration is design discussion for share placement behavior. Risks include Python 3 bytes/string hashing errors, integer division differences, fixed 1 TB capacity, and no direct return metrics except printed output. Tests should use small server counts/capacities, deterministic seeds, permuted vs linear orders, and full-grid termination.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/simulators/ringsim.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/simulators/simulate_load.py -->
# sources/distributed-fs/tahoe-lafs/misc/simulators/simulate_load.py

## Purpose

This discrete-event simulator models a Tahoe-like grid with nodes accepting shares, publishing/deleting files, and tracking total utilization over time in an RRD graph.

## Important APIs, Types, and Functions

`sha` and `randomid` generate IDs. `Node` tracks shares, capacity, utilization, and files; key methods are `permute_peers`, `publish_file`, `accept_share`, `make_space`, `delete_share`, `retrieve_file`, and `delete_file`. `Introducer` tracks living files and utilization and coordinates deletion. `Simulator` defines event rates, initializes PyRRD storage, schedules events, handles add/delete file events, records stats, and writes graphs.

## Control Flow

`main` creates a `Simulator`, then processes 1000 scheduled events. Events are exponentially distributed by type; add-file chooses a random node and size, publishes shares through permuted peers, and records success/failure; delete-file asks shuffled nodes to delete one known file. Utilization is buffered into `/tmp/utilization.rrd` and can be graphed to `/tmp/utilization.png`.

## State, Dependencies, Integration, Risks, and Tests

Persistent state is `/tmp/utilization.rrd` and optional PNG output. Dependencies are PyRRD/pkg_resources, random, hashlib, and RRD tooling. Risks include Python 2 division, bytes/string hashing, `random.choice(self.shares.keys())` under Python 3, incomplete ADDNODE/DELNODE events, possible `delete` KeyError if metadata drifts, and hard-coded `/tmp` output. Tests should seed randomness, use tiny NUM_NODES/event counts, validate share accounting, deletion accounting, and RRD calls through fakes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/simulators/simulate_load.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/simulators/simulator.py -->
# sources/distributed-fs/tahoe-lafs/misc/simulators/simulator.py

## Purpose

This older share-placement simulator models servers filling as files are uploaded, then renders an ASCII graph of when servers become full. It appears to support both simple ring placement and permuted peer placement for comparison.

## Important APIs, Types, and Functions

The file defines server/ring simulation helpers, a `go(permutedpeerlist)` upload loop returning servers and doubled-up share counts, `div_ceil`, and `test(permutedpeerlist, iters)`, which runs multiple simulations, aggregates each server's `full_at_tick`, compresses the timeline to about 70 columns, and prints an ASCII chart. The main block parses `--iters=` and `--permute`.

## Control Flow

Direct execution chooses permuted or simple-ring mode, runs `test`, which repeatedly calls `go`, records how many servers fill at each file count, computes cumulative full-server counts per compressed bucket, averages across iterations, and prints a y-axis of servers full against uploaded file counts.

## State, Dependencies, Integration, Risks, and Tests

State is simulated server capacity and aggregate `filledat` arrays. Dependencies are stdlib random/hash/math behavior from the file's earlier definitions. Integration is design analysis around peer permutation and capacity spread. Risks include Python 2 division, likely long runtimes, no structured output, and potential index errors if no server fills. Tests should use reduced server/file constants, deterministic seeds, and validate `div_ceil` plus aggregation behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/simulators/simulator.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/simulators/sizes.py -->
# sources/distributed-fs/tahoe-lafs/misc/simulators/sizes.py

## Purpose

This simulator estimates storage overhead and "alacrity" for several immutable-share block validation schemes across file sizes.

## Important APIs, Types, and Functions

`Args` parses mode and hash-tree arity. `Sizes` computes segment counts, share sizes, validation tree depth, storage overhead, transmission overhead, total overhead percentage, and bytes needed before some data can be validated. Modes are `alpha` (no block hash tree), `beta` (flat per-block hashes), and `gamma` (k-ary block hash tree). `fmt` formats sizes. `text` prints a table, while `graph` is an unfinished Gnuplot path.

## Control Flow

Direct execution calls `text`. It parses options, prints headers, generates file sizes by powers of two, constructs `Sizes` for each, and prints share size, overhead, k, depth, and alacrity. `charttest` is a separate gdchart experiment not used by default.

## State, Dependencies, Integration, Risks, and Tests

State is computed in memory and printed. Dependencies are Twisted `usage` and optional gdchart/Gnuplot for unused graphing helpers. Integration is design exploration for Tahoe validation overhead. Risks include Python 2 division semantics, `opt_arity` signature likely wrong for Twisted usage callbacks, unqualified `k` variable in gamma mode is assigned from `arity` but easy to misread, and no tests. Test signals should instantiate `Sizes` for known file sizes/modes, verify monotonic overhead, invalid mode errors, and formatting boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/simulators/sizes.py -->
