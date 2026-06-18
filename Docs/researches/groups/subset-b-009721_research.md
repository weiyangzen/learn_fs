# Research: subset-b-009721

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/checkpatch.pl -->
# sources/user-network-fs/nfs-ganesha/src/scripts/checkpatch.pl

## Purpose
This is a Perl style and patch-quality checker derived from Linux `checkpatch.pl` version 0.32. In this NFS-Ganesha tree it is a developer/tooling script for validating patches or full source files against kernel-oriented coding conventions. It can read unified diffs from files or stdin, synthesize diffs for `--file` checks, expand `--git` revision expressions into `git format-patch` streams, filter message types, emit colorized reports, and optionally write experimental mechanical fixes.

## Important APIs, Types, And Functions
The script is an executable CLI, not a reusable Perl module. Its public interface is the option set parsed by `GetOptions`: `--patch`, `--file`, `--git`, `--strict`, `--ignore`, `--types`, `--show-types`, `--max-line-length`, `--root`, `--fix`, `--fix-inplace`, `--codespell`, `--typedefsfile`, `--color`, and related reporting switches. The central entry points are `process($filename)`, which scans one patch or generated diff, and the message helpers `ERROR`, `WARN`, and `CHK`, which funnel through `report`.

The core parsing helpers are regex-heavy and stateful. `sanitise_line_reset` and `sanitise_line` mask comments and string literals so style checks can reason about code tokens. `ctx_statement_block`, `ctx_statement_full`, `ctx_block_get`, `ctx_block`, `ctx_statement`, and related helpers collect multi-line C statements and brace/parenthesis contexts from diff hunks. `annotate_values` classifies a token stream into value/type/operator positions. `build_types`, `possible`, `seed_camelcase_file`, and `seed_camelcase_includes` maintain dynamic type/modifier/CamelCase recognition. Email and commit metadata helpers include `parse_email`, `format_email`, `reformat_email`, `same_email_addresses`, `find_standard_signature`, and `git_commit_info`.

The script relies on global state rather than objects. Important globals include CLI flags, message filters, type regex fragments, `@rawlines`, `@lines`, `@fixed`, insertion/deletion fix queues, spelling dictionaries, and current report counters. Regex pseudo-types such as `$Ident`, `$Type`, `$Declare`, `$Lval`, `$FuncArg`, and `$balanced_parens` act as the effective type system for the checker.

## Control Flow
Startup resolves the script directory, reads `.checkpatch.conf` from current directory, `$HOME`, or `.scripts`, applies command-line options, validates incompatible modes, configures color output, optionally loads verbose documentation, and validates the kernel-tree root unless `--no-tree` is used. It loads spelling and optional codespell dictionaries, optional typedefs, and const-struct names before constructing the main regexes with `build_types`.

Input dispatch happens per argument. In `--git` mode, revision expressions are expanded with `git log --no-merges`, then each commit is opened through `git format-patch -M --stdout -1`. In `--file` mode, the script runs `diff -u /dev/null <file>` so the normal patch scanner can be reused. Plain patch files and stdin are read directly into `@rawlines`.

`process` performs a pre-scan that builds sanitized `@lines`, tracks hunk line numbers, detects whether hunks start inside comments, and collects documentation lines for `__setup` checks. The second scan walks every sanitized line, updates real file/line context from `diff --git`, `+++`, and `@@` records, validates commit-log/signoff/header content, counts changed lines, tracks statement context, then runs a long set of anchored checks. Many checks only run for added lines, and deeper C checks are gated to `.h` and `.c` files after lighter checks also include `.pl`, `.dts`, and `.dtsi`.

At the end of `process`, mailback and non-patch suppression are applied, missing signoff and unified-diff errors are emitted, accumulated reports are printed, summaries are generated, and `--fix`/`--fix-inplace` writes a modified patch or source file after reconciling queued insertions/deletions.

## State And Persistence
Runtime state is held in process globals and is reset between top-level inputs. The script may create `.checkpatch-camelcase.git.<commit>` or `.checkpatch-camelcase.date.<timestamp>` caches in the current working directory after scanning include headers. `--fix` writes `<input>.EXPERIMENTAL-checkpatch-fixes`; `--fix-inplace` overwrites the original input after generating fixed content. It reads local configuration from `.checkpatch.conf`, spelling data from `spelling.txt`, optional codespell dictionaries, optional typedef files, `const_structs.checkpatch`, and Linux-style documentation files when verbose descriptions are requested.

## Dependencies And Integration Points
Perl dependencies are core/common modules: `strict`, `warnings`, `POSIX`, `File::Basename`, `Cwd`, `Term::ANSIColor`, `Encode`, and `Getopt::Long`. External integration includes `git`, `diff`, `find`, `grep`, `python`, `python3`, `codespell`, `scripts/spdxcheck.py`, and `scripts/get_maintainer.pl` when tree-aware checks are enabled. The script expects a Linux-kernel-like tree layout for full operation, which is notable because NFS-Ganesha is not itself the kernel tree; consumers commonly need `--no-tree` or a compatible root.

## Risks And Edge Cases
The implementation is intentionally heuristic. Large C grammar fragments are represented as Perl regexes, so false positives and false negatives are expected for complex macros, unusual declarations, generated code, or non-kernel style. Several shell commands interpolate paths or revision expressions; most inputs are ordinary developer-supplied paths, but command construction still deserves care in automated contexts. The dynamic type-learning path can affect later checks inside the same file. `--fix` is explicitly experimental and can rewrite hunks incorrectly when the parser misclassifies context. Curses or runtime behavior is not relevant here, but stdout coloring and terse/emacs/showfile modes can change output shape consumed by CI parsers.

## Test Signals
Useful validation signals are `perl -c scripts/checkpatch.pl`, `scripts/checkpatch.pl --list-types`, sample clean and intentionally-bad patches, `--file --no-tree` checks against representative C headers/sources, and comparison against Linux upstream `checkpatch.pl` behavior. For this repository, test both normal patch mode and `--no-tree`, because root detection expects kernel files such as `Kbuild`, `MAINTAINERS`, `arch`, `drivers`, and `fs`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/checkpatch.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/docker/Dockerfile-in.cmake -->
# sources/user-network-fs/nfs-ganesha/src/scripts/docker/Dockerfile-in.cmake

## Purpose
This CMake-templated Dockerfile builds a simple NFS-Ganesha container image. CMake substitutes `@DOCKER_DISTRO@`, `@DOCKER_DISTRO_VERSION@`, and `@CMAKE_INSTALL_PREFIX@`, then the Docker build installs runtime prerequisites, copies a prepared `root/` filesystem into the image, creates the Ganesha log directory, copies the generated entrypoint, and sets it as the container entrypoint.

## Important APIs, Types, And Functions
The file uses Dockerfile primitives only: `FROM`, `MAINTAINER`, `RUN`, `ADD`, and `ENTRYPOINT`. There are no functions or structured types. The meaningful template API is the set of CMake placeholders consumed during configure/generate time.

## Control Flow
At image build time Docker resolves the configured base image, runs two `dnf install -y` commands, adds `root/` to `/`, creates `@CMAKE_INSTALL_PREFIX@/var/log/ganesha`, adds `entrypoint.sh`, and records `ENTRYPOINT ["/entrypoint.sh"]`. At container runtime control passes to the entrypoint script rather than continuing in this file.

## State And Persistence
The image persists installed RPM packages, copied root filesystem content, `/entrypoint.sh`, and the log directory. It does not declare Docker volumes or runtime environment defaults itself. Logs are expected under the configured install prefix unless the entrypoint environment overrides the logfile path.

## Dependencies And Integration Points
The Dockerfile assumes a DNF-based distribution image. Runtime packages include `libcap`, `libblkid`, `libuuid`, `dbus`, `nfs-utils`, `rpcbind`, `libnfsidmap`, and `libattr`; build/prerequisite packages include `tar` and `redhat-lsb-core`. It integrates with the CMake install tree through `root/` and with `entrypoint.sh-in.cmake` through the generated `/entrypoint.sh`.

## Risks And Edge Cases
The package manager is hard-coded to `dnf`, so configured base images must be Fedora/RHEL-like. `MAINTAINER` is deprecated in modern Dockerfiles. The `ADD root/ /` step may unintentionally bake broad build artifacts into the image if `root/` is not curated. There is no cleanup of DNF metadata, so images may be larger than necessary. The Dockerfile does not expose ports, set a user, or define volumes, so the container likely runs privileged/root-oriented NFS services and depends on external runtime flags.

## Test Signals
Validate by running the CMake configure step that substitutes all `@...@` tokens, then `docker build` or `podman build` with the generated Dockerfile. Runtime smoke tests should check that `/entrypoint.sh` exists and is executable, `ganesha.nfsd` exists under the substituted install prefix, `rpcbind`/NFS helper programs are installed, and the configured log directory exists.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/docker/Dockerfile-in.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/docker/entrypoint.sh-in.cmake -->
# sources/user-network-fs/nfs-ganesha/src/scripts/docker/entrypoint.sh-in.cmake

## Purpose
This CMake-templated Bash entrypoint starts either an interactive shell or the NFS-Ganesha daemon inside the container. CMake substitutes filesystem paths for log, config, install prefix, and library directory defaults.

## Important APIs, Types, And Functions
The externally visible API is the container command argument and environment. If the first argument is `shell`, it runs `/bin/bash`; otherwise it starts Ganesha. Environment variables control launch parameters: `GANESHA_LOGFILE`, `GANESHA_CONFFILE`, `GANESHA_OPTIONS`, `GANESHA_EPOCH`, and `GANESHA_LIBPATH`. The only shell function is `rpc_init`, which starts `rpcbind`, `rpc.statd -L`, and `rpc.idmapd`.

## Control Flow
The script sets default values with shell parameter expansion, defines `rpc_init`, checks `$1`, and either opens a shell or initializes RPC services and execs the configured daemon command. The daemon command runs `@CMAKE_INSTALL_PREFIX@/bin/ganesha.nfsd -F -L ${GANESHA_LOGFILE} -f ${GANESHA_CONFFILE} ${GANESHA_OPTIONS} ${GANESHA_EPOCH}` with `LD_LIBRARY_PATH` set from `GANESHA_LIBPATH`.

## State And Persistence
The script starts background system services in the container namespace and runs `ganesha.nfsd` in the foreground via `-F`. It writes logs to the configured `GANESHA_LOGFILE`. There is no PID-file management, signal trap, or cleanup logic in the script; container lifecycle management is delegated to the foreground daemon and Docker/Podman.

## Dependencies And Integration Points
Runtime dependencies are Bash, `/bin/bash`, `rpcbind`, `rpc.statd`, `rpc.idmapd`, the generated Ganesha install tree, and the runtime libraries named by `GANESHA_LIBPATH`. It integrates directly with the generated Dockerfile and CMake placeholders `@SYSSTATEDIR@`, `@SYSCONFDIR@`, `@LIB_INSTALL_DIR@`, and `@CMAKE_INSTALL_PREFIX@`.

## Risks And Edge Cases
The variable defaults use `: ${VAR:=...}` and the daemon command expands unquoted variables. This permits intentional multi-word options in `GANESHA_OPTIONS`, but it also means paths with spaces or shell metacharacters are unsafe. `rpc_init` does not check command failures before starting Ganesha. Because the daemon is not launched with `exec`, signal handling may be less direct than a typical container PID 1 pattern. The comment misspells Ganesha, but behavior is unaffected. If `GANESHA_EPOCH` is empty, expansion is harmless; if it contains multiple arguments, they are passed through word splitting.

## Test Signals
After CMake generation, verify no unsubstituted `@...@` placeholders remain. Container smoke tests should run the image with `shell`, run it with a minimal valid `ganesha.conf`, and assert RPC helpers start before `ganesha.nfsd`. Tests should also cover overriding `GANESHA_LOGFILE`, `GANESHA_CONFFILE`, `GANESHA_OPTIONS`, and `GANESHA_LIBPATH`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/docker/entrypoint.sh-in.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/ganesha-top/CMakeLists.txt -->
# sources/user-network-fs/nfs-ganesha/src/scripts/ganesha-top/CMakeLists.txt

## Purpose
This CMake file builds and installs the `ganesha-top` Python administration tool when `USE_ADMIN_TOOLS` and `Python3_FOUND` are true. It converts `ganesha-top.py` into an extensionless command script, generates a `setup.py`, builds either through legacy distutils or modern Python wheel tooling, and installs the resulting package/script.

## Important APIs, Types, And Functions
The relevant CMake APIs are `set`, `foreach`, `string(REPLACE)`, `add_custom_command`, `list(APPEND)`, `configure_file`, `add_custom_target`, and `install(CODE ...)`. Inputs are `setup.py.in` and `ganesha-top.py`. Generated build outputs are the extensionless `ganesha-top`, `setup.py`, `build/ganesha_top_timestamp`, and, in modern mode, `dist/ganesha_top-<major><minor>-py3-none-any.whl`.

## Control Flow
The file is gated first by `USE_ADMIN_TOOLS`, then by `Python3_FOUND`. It declares `GANESHA_TOP_SRC`, loops over it to add copy commands that strip `.py`, builds `SCRIPTS_STRING` for `setup.py.in`, configures `setup.py`, and creates a timestamp-producing custom command. Legacy mode runs `${Python3_EXECUTABLE} setup.py build`; non-legacy mode runs `${Python3_EXECUTABLE} -m build --wheel --no-isolation .`. `python_ganesha_top` depends on the timestamp and is built by default. Install logic either runs `setup.py install --skip-build --no-compile --prefix=$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}` or invokes `python -m installer --destdir $ENV{DESTDIR}` on the generated wheel.

## State And Persistence
The build tree persists a copied executable script, generated `setup.py`, Python build directories, wheel output, and timestamp file. Install writes into the CMake install prefix or DESTDIR staging area. The source tree is read-only from this file's perspective.

## Dependencies And Integration Points
This integrates with top-level CMake options `USE_ADMIN_TOOLS`, `USE_LEGACY_PYTHON_INSTALL`, `GANESHA_MAJOR_VERSION`, `GANESHA_MINOR_VERSION`, `GANESHA_VERSION`, `CMAKE_INSTALL_PREFIX`, and Python discovery variables. Modern mode requires Python modules `build` and `installer`; legacy mode depends on distutils behavior in `setup.py.in`. At runtime the installed script depends on the `ganeshactl`/`Ganesha` Python package infrastructure for DBus utilities.

## Risks And Edge Cases
The dependency list uses `${GANESHA_TOP_SRCS}`, but the file defines `GANESHA_TOP_SRC`; that mismatch can make the custom build command fail to rebuild when the source changes, although the copied script target in `${SCRIPTS}` still depends on the source. `COMMAND mkdir -p build/lib` uses the shell-visible `mkdir` instead of `${CMAKE_COMMAND} -E make_directory`, making it less portable. The wheel filename is manually constructed from major/minor variables and may diverge from the package version generated by `setup.py.in`. Modern mode assumes `python -m build` and `python -m installer` are installed in the selected interpreter.

## Test Signals
Configure with `USE_ADMIN_TOOLS=ON` and `Python3_FOUND` true, then build `python_ganesha_top`. Validate both `USE_LEGACY_PYTHON_INSTALL=ON` and `OFF` paths if supported. Check that the generated `setup.py` contains a `scripts = ['ganesha-top']` list, the extensionless script exists, the expected wheel filename is present in modern mode, and `cmake --install` places the script in the staging prefix.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/ganesha-top/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/ganesha-top/ganesha-top.py -->
# sources/user-network-fs/nfs-ganesha/src/scripts/ganesha-top/ganesha-top.py

## Purpose
`ganesha-top.py` is an interactive curses dashboard for a running `ganesha.nfsd` process. It enables all Ganesha stats, samples process memory/CPU through `psutil`, queries NFS-Ganesha DBus management/statistics interfaces, and displays version, process, export, client, cache, and NFSv4 operation data with keyboard-controlled views.

## Important APIs, Types, And Functions
The top-level CLI accepts `-i/--interval` in seconds. Constants define DBus/process identity: `GaneshaProcess = 'ganesha.nfsd'`, `GaneshaService = 'org.ganesha.nfsd'`, `DefaultInterval = 5`, and `DEFAULT_CONTENT_POS_Y = 7`.

Utility functions include `enbale_all_stats` (typo in name, invokes `ganesha_stats enable all`), `get_ganesha_pid` (`pidof -s ganesha.nfsd`), `setup_color`, `convert_memory_size`, and `generate_version`. `SingleTon` implements a one-instance-per-class pattern.

DBus wrapper classes are `ClientInterface` and `ExportInterface`, which bind to `org.ganesha.nfsd.clientmgr`, `clientstats`, `exportmgr`, and `exportstats` methods. Manager classes are `ClientMgr`, `ExportMgr`, and `GaneshaPSInfo`. `ClientMgr` caches clients and fetches per-client I/O counters. `ExportMgr` caches export metadata, global ops, cache LRU info, NFSv4 detail stats, and per-export totals. `GaneshaPSInfo` wraps a `psutil.Process` and exposes status, RSS, VMS, swap, and CPU percent.

Rendering functions include `draw_header`, `draw_footbar`, `draw_client_page`, `draw_client_stats`, `draw_export_page`, `draw_export_stats`, `draw_help_page`, `draw_help_content`, `draw_v4_full_stats`, `draw_default_page`, and `draw_menu`.

## Control Flow
`main` parses the interval, converts it to milliseconds for curses timeout handling, verifies the Ganesha process exists, enables all stats, and enters `curses.wrapper(draw_menu, interval)`. `draw_menu` initializes colors, then loops until `q`; it redraws the default detailed NFSv4 page, client page (`c`), export page (`e`), or help page (`h`) based on keyboard input. Invalid input and timeout preserve the previous screen.

Each page clears the screen, gathers fresh display data through the singleton managers, draws a header, draws page-specific content, and draws the footer. Header generation instantiates `GaneshaPSInfo`, `ExportMgr`, and `ClientMgr`, calls the admin interface for version data, then prints fixed-position fields for memory, CPU, export/client counts, global NFSv4 ops, and cache inode data. Client and export pages query DBus operation totals and render row-oriented summaries. The default page calls `GetFULLV4Stats` and renders per-operation total/error/min/avg/max rows.

## State And Persistence
The tool does not persist files. Runtime state lives in singleton instances and dictionaries. Because `ExportMgr`, `ClientMgr`, and `GaneshaPSInfo` are singletons and `__init__` is not guarded, construction on each draw can reinitialize cached dictionaries and DBus objects, while `GaneshaPSInfo.memory_info` is captured only during initialization and may not update unless initialization reruns. DBus calls may enable server-side statistics through `ganesha_stats enable all`, which changes live Ganesha statistics collection behavior.

## Dependencies And Integration Points
Python dependencies are `curses`, `argparse`, `subprocess`, `datetime`, `psutil`, `dbus`, and the in-tree `Ganesha` package modules `ganesha_mgr_utils.AdminInterface`, `glib_dbus_stats.Export`, and `glib_dbus_stats.Client`. External commands are `pidof` and `ganesha_stats`. Runtime integration requires a running `ganesha.nfsd`, system DBus access to `org.ganesha.nfsd`, and a terminal capable of curses display.

## Risks And Edge Cases
`enbale_all_stats` and `get_ganesha_pid` use `subprocess.run` without `check=True`, so `CalledProcessError` will not be raised; failed commands can instead yield empty stdout or nonzero return codes that are not handled as intended. Converting empty `pidof` output with `int(...)` can raise `ValueError`. Fixed-position `curses.addstr` calls can fail on narrow terminals or when generated content exceeds width/height. DBus response parsing uses positional indexes such as `stats[4][9]` and `stat[3][7]`, making it sensitive to interface schema changes or disabled stats. `ClientMgr.get_total_client_ops` mutates `io_content` while assuming four protocol blocks and may misparse unexpected DBus layouts. The singleton pattern is not thread-safe and does not prevent repeated `__init__` work. `psutil.memory_full_info().swap` may not exist on all platforms. The UI has no exception boundary around DBus or curses drawing failures.

## Test Signals
Static checks can run `python3 -m py_compile ganesha-top.py`, though imports may require the build/install Python path. Unit tests should mock DBus objects, `psutil.Process`, `subprocess.run`, and curses screens to cover parsing and drawing without a live daemon. Integration tests should run against a test Ganesha instance with DBus enabled, validate each keyboard page (`d`, `c`, `e`, `h`, `q`), and test narrow terminal behavior. Regression tests should specifically cover command failures from `pidof` and `ganesha_stats`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/ganesha-top/ganesha-top.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/ganesha-top/setup.py.in -->
# sources/user-network-fs/nfs-ganesha/src/scripts/ganesha-top/setup.py.in

## Purpose
This is a CMake-configured Python packaging template for the `ganesha-top` command. CMake substitutes package version, source directory, and script list, producing a `setup.py` consumed by either distutils legacy build/install or modern wheel build commands from the companion CMake file.

## Important APIs, Types, And Functions
The file imports `setup` and `Extension` from `distutils.core`, although `Extension` is unused. Its only runtime behavior is `setup(...)` under `if __name__ == '__main__'`. Template variables are `${GANESHA_VERSION}`, `${CMAKE_CURRENT_SOURCE_DIR}`, and `${SCRIPTS_STRING}`.

## Control Flow
When executed, the generated script calls `setup` with package metadata and a `scripts` list. There are no packages or modules declared here; the packaging payload is the generated extensionless command script or scripts.

## State And Persistence
The template itself has no persistent state. Generated `setup.py` participates in build artifacts under the CMake binary directory, and install commands persist the generated command into the Python/script install destination chosen by distutils or wheel installation.

## Dependencies And Integration Points
It depends on CMake to substitute all `${...}` placeholders and on Python distutils/setuptools-compatible tooling to interpret the generated script. It is tightly coupled to `ganesha-top/CMakeLists.txt`, which constructs `SCRIPTS_STRING` and decides whether to invoke `setup.py build`, `setup.py install`, or wheel-building tooling.

## Risks And Edge Cases
`distutils` is deprecated/removed in newer Python distributions, which makes the legacy path increasingly fragile. `package_dir` is set even though no `packages` list is supplied, so it has little effect for `ganesha-top` unless packaging is later expanded. The wheel name used by CMake install logic must match normalized project naming and version behavior from this file; mismatches can break non-legacy installs. The indentation is unusual but valid Python.

## Test Signals
After CMake configure, inspect generated `setup.py` for unsubstituted placeholders, run `python3 setup.py --name`, and build through both legacy and modern CMake branches where supported. Confirm the generated package name/version produce the wheel filename expected by `CMakeLists.txt`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/ganesha-top/setup.py.in -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/CMakeLists.txt -->
# sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/CMakeLists.txt

## Purpose
This CMake file builds and installs the broader Python DBus administration tool suite under `scripts/ganeshactl`. It handles core `Ganesha` Python modules, command-line scripts, optional Qt GUI scripts and generated UI Python files, Python package/wheel build commands, install commands, and the `ganesha_conf.8` man page.

## Important APIs, Types, And Functions
The file defines three major source lists: `GANESHA_BASE_SRCS` for Python package modules, `SCRIPT_SRC` for command-line tools such as `ganesha_stats.py` and `ganesha_conf.py`, and `GUI_SCRIPT_SRC` for Qt-oriented tools such as `ganeshactl.py` and `manage_exports.py`. `UI_SRC` lists Qt Designer `.ui` files compiled through `${PYUIC}`. CMake APIs include `add_custom_command`, `add_custom_target`, `configure_file`, `install(CODE ...)`, and `install(FILES ...)`.

## Control Flow
When `Python3_FOUND` is true, the file configures `setup.py` from `setup.py.in`. If `USE_GUI_ADMIN_TOOLS` is enabled, it populates `GANESHA_SRCS` with base modules and adds custom commands to compile each `.ui` file into `build/lib/Ganesha/QtUI/*.py`. It always creates extensionless copies of `SCRIPT_SRC`; GUI script copies are added only when GUI tools are enabled. It builds `SCRIPTS_STRING` from the selected script lists for setup substitution. Legacy Python install mode runs `setup.py build`; modern mode runs `python -m build --wheel --no-isolation .`; both touch `build/ganeshactl_timestamp` and feed the `python_ganeshactl` all-target. Install mode either executes `setup.py install --skip-build --no-compile --prefix=$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}` or `python -m installer --destdir $ENV{DESTDIR}` on the expected wheel.

Outside the Python block, the file copies `ganesha_conf.man` to `ganesha_conf.8`, builds a `man` target by default, and installs the generated man page under `${CMAKE_INSTALL_PREFIX}/share/man/man8/`.

## State And Persistence
Generated state in the binary directory includes copied extensionless scripts, generated Qt UI Python modules, generated `setup.py`, Python build directories, wheel files, timestamp files, and the copied man page. Installed state includes Python modules/scripts and the man page in the configured prefix or DESTDIR staging root.

## Dependencies And Integration Points
This file depends on top-level Python discovery, `USE_GUI_ADMIN_TOOLS`, `USE_LEGACY_PYTHON_INSTALL`, `${PYUIC}`, Python modules `build` and `installer` in modern mode, and package metadata variables such as `GANESHA_MAJOR_VERSION` and `GANESHA_MINOR_VERSION`. Runtime modules integrate with NFS-Ganesha DBus services through the Python files listed in `GANESHA_BASE_SRCS`. The man page target integrates with standard Unix manpage layout.

## Risks And Edge Cases
Core `GANESHA_BASE_SRCS` are only assigned to `GANESHA_SRCS` when `USE_GUI_ADMIN_TOOLS` is enabled. If non-GUI command-line tools import the `Ganesha` package, the non-GUI packaging path depends on `setup.py.in` or other packaging behavior to include modules; the CMake dependency list may not notice module changes. The script copy commands do not create directories because the script outputs are flat, but UI generation assumes `build/lib/Ganesha/QtUI` and creates it with shell `mkdir -p` rather than a portable CMake command. As with `ganesha-top`, the modern install command hard-codes the expected wheel filename from major/minor variables, which can diverge from Python packaging normalization. The custom `man` target name is generic and could collide in a larger build. The install destination prepends `${CMAKE_INSTALL_PREFIX}` inside `DESTINATION`, which is unusual because CMake install destinations are normally prefix-relative.

## Test Signals
Configure and build with `Python3_FOUND` true, then test four matrix entries where feasible: GUI on/off and legacy install on/off. Verify extensionless command scripts are generated, Qt UI `.py` files are generated only when GUI tools are enabled, the wheel or legacy build exists, and `cmake --install` stages all expected scripts/modules. Confirm changes to package modules trigger rebuilds in both GUI and non-GUI modes. Build the `man` target and verify `ganesha_conf.8` installs to the expected man8 directory.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/CMakeLists.txt -->
