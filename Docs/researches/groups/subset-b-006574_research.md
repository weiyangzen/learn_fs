# subset-b-006574 Research

Grouped research for the listed Linux kernel tool files under the ceph-client source snapshot. Each section preserves its original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/docs/get_feat.py -->
# sources/distributed-fs/ceph-client/tools/docs/get_feat.py

Purpose: CLI front end for parsing `Documentation/features` feature files and rendering architecture support information as ReST tables or machine-readable lists.

Important APIs/types/functions: `GetFeature` owns the command implementation. `get_current_arch()` normalizes `uname -m` values (`x86_64`/`i386` to `x86`, `s390x` to `s390`). `run_parser()` constructs `feat.parse_features.ParseFeature`. `run_rest()`, `run_current()`, `run_list()`, and `validate_args()` drive parser output. `parser()` builds argparse subcommands `current`, `rest`, `list`, and `validate` plus shared `--directory`, `--debug`, and `--enable-fname`.

Control flow: `main()` parses command-line arguments, requires a subcommand, then dispatches to the function stored in `args.func`. All output flows through `ParseFeature` methods: matrix, per-architecture table, single-feature view, validation-only parse, or list output.

State and persistence: No persistent state is created. Runtime state is the parsed feature tree and the mutable argparse namespace, where `run_current()` and `run_list()` may fill in `args.arch` from the host architecture.

Dependencies/integration: Imports kernel-local `tools/lib/python/feat/parse_features.py` by adding `../../tools/lib/python` relative to this script. It integrates with documentation builds through ReST output and with dependency tracking through `--enable-fname`.

Risks/tests: Risks are stale architecture normalization, missing `get_feat.pl` compatibility expectations from callers, and parser failures hidden behind ReST generation. Test signals include `validate` over the default feature directory, `rest` for all/arch/feature combinations, `list --arch`, and current-architecture behavior on x86 and s390 hosts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/docs/get_feat.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/docs/kdoc_diff -->
# sources/distributed-fs/ceph-client/tools/docs/kdoc_diff

Purpose: Compares `kernel-doc` output between two Git commits, with optional full-tree scanning, explicit file selection, cache cleanup, and YAML regression checking.

Important APIs/types/functions: `GitHelper` validates repository state and checks out commits. `CacheManager` creates `.doc_diff_cache` subdirectories and maps refs to short-hash cache paths. `KernelDocRunner` finds `.. kernel-doc::` references, generates man/RST logs, emits YAML, and runs `tools/unittests/test_kdoc_parser.py`. `DiffManager` compares cached output directories. `SignalHandler` restores the original branch on normal exit or signals. `parse_commit_range()` accepts `old..new` or `old`.

Control flow: `main()` parses commits and file options, refuses `--full` with explicit file lists, initializes cache, validates clean Git state, picks scan mode (`full`, `partial`, or `no-cache`), then within `SignalHandler` checks out old and new commits to generate or reuse outputs. Non-regression mode diffs cached directories; regression mode generates YAML from the old commit and runs unit tests against the new commit.

State and persistence: Persistent state lives in `.doc_diff_cache/full`, `.doc_diff_cache/partial`, and `.doc_diff_cache/no_cache`, plus temporary `__tmp__`. The script temporarily mutates the working tree by forced Git checkout, but refuses to run with uncommitted changes and restores the original branch.

Dependencies/integration: Depends on Git, `tools/docs/kernel-doc`, kernel `Documentation/**/*.rst`, `diff`, and the kernel-doc parser unit test. It is a developer validation tool rather than a build step.

Risks/tests: The highest risk is destructive checkout behavior if repository cleanliness detection misses ignored or external state. Other risks include stale caches hiding changes, unhandled detached-HEAD restoration, and `run_unittest()` returning success even when the subprocess returns nonzero. Test signals are clean-repo dry runs over a small file set, `--clean`, `--full`, `--regression`, signal interruption, and cache reuse.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/docs/kdoc_diff -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/docs/kernel-doc -->
# sources/distributed-fs/ceph-client/tools/docs/kernel-doc

Purpose: Python implementation of the kernel-doc extractor. It reads C source/header files, parses `/** ... */` documentation comments, and prints ReST, manpage, YAML, or warnings-only output.

Important APIs/types/functions: `MsgFormatter` preserves legacy capitalized warning/error prefixes. `main()` defines the CLI. Selection flags include `--export`, `--internal`, `--symbol`, `--nosymbol`, and `--no-doc-sections`; warning controls include `--wreturn`, `--wshort-desc`, `--wall`, and `--werror`; output controls include `--man`, `--rst`, `--none`, `--yaml`, and `--kdoc`. After Python-version checks it imports `kdoc.kdoc_files.KernelFiles` and output formatters `RestFormat`/`ManFormat`.

Control flow: Argparse normalizes warning flags, logging is configured, Python versions below 3.6 are rejected except for `--none`, and output mode is chosen. `KernelFiles.parse()` indexes input and export files, then `kfiles.msg()` yields selected rendered messages which are printed to stdout. Exit code is `3` only when warnings exist and `--werror` is set.

State and persistence: No persistent local state unless `--yaml` writes a requested YAML file. Runtime state includes parsed comments, export-symbol maps, warning counters, and selected output formatter.

Dependencies/integration: Integrated into Sphinx documentation builds through `.. kernel-doc::` directives and wrapper scripts. Depends on kernel-local `tools/lib/python/kdoc` modules and C/UAPI source files.

Risks/tests: Parser behavior is compatibility-sensitive because many documentation builds depend on legacy Perl-compatible output and exit semantics. Test signals include the kernel-doc parser unit tests, representative C files with functions/structs/enums/DOC sections, export/internal filtering, YAML round trips, old Python graceful-failure behavior, and `--werror` return-code checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/docs/kernel-doc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/docs/list-arch.sh -->
# sources/distributed-fs/ceph-client/tools/docs/list-arch.sh

Purpose: Small shell wrapper that prints feature support status for a requested architecture or the normalized host architecture.

Important APIs/types/functions: Exposes one optional positional argument, `ARCH`. It normalizes `uname -m` for x86 and s390 variants, then invokes `$(dirname $0)/get_feat.pl list --arch $ARCH`.

Control flow: Shell parameter expansion picks the supplied architecture or computes one from `uname -m`; execution is delegated entirely to `get_feat.pl`.

State and persistence: No state is stored. Output is whatever the feature-list command prints.

Dependencies/integration: Depends on `sed`, `uname`, and an adjacent `get_feat.pl` script. In this snapshot the Python replacement `get_feat.py` is present, so this wrapper is an integration compatibility point that may be stale if `get_feat.pl` is absent.

Risks/tests: The main risk is broken delegation to `get_feat.pl` when only `get_feat.py` exists. Test signals are running the wrapper with no args and with `x86`, `s390`, and another explicit architecture, verifying it matches `get_feat.py list --arch`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/docs/list-arch.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/docs/parse-headers.py -->
# sources/distributed-fs/ceph-client/tools/docs/parse-headers.py

Purpose: Converts a C source/header into ReST containing a parsed-literal or TOC table, enriching detected C API names with cross-references and optional override rules.

Important APIs/types/functions: `main()` parses `file_in`, `file_out`, optional `file_rules`, `--debug`, and `--toc`. It uses kernel-local `kdoc.parse_data_structs.ParseDataStructs` to identify defines, ioctls, functions, structs, typedefs, enums, and enum symbols. `kdoc.enrich_formatter.EnrichFormatter` formats argparse help from the module docstring.

Control flow: The script constructs a parser object, reads and applies optional rules through `parse_file()`, optionally emits debug data, then writes the converted RST with `write_output()`.

State and persistence: The input parse tree is transient. Persistent output is the requested RST file. Rule files can suppress or replace generated references, making output dependent on external policy files.

Dependencies/integration: Used by kernel documentation to include UAPI/header listings with stable cross references. Depends on `tools/docs/lib/python/kdoc` modules and source/rules files.

Risks/tests: Risks include incorrect C construct detection, rule-file drift, and generated cross-reference churn that breaks Sphinx builds. Test signals are golden output for representative headers, `--toc` mode, rules for `ignore` and `replace`, and Sphinx nitpicky build warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/docs/parse-headers.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/docs/sphinx-build-wrapper -->
# sources/distributed-fs/ceph-client/tools/docs/sphinx-build-wrapper

Purpose: Kernel-specific Sphinx build launcher that translates make targets into `sphinx-build`, handles build directories, parallelism, venv activation, man/PDF/info post-processing, Rust docs, locale fixes, and static asset copying.

Important APIs/types/functions: `SphinxBuilder` contains `get_path()`, `check_rust()`, `get_sphinx_extra_opts()`, `run_sphinx()`, `handle_html()`, `handle_pdf()`, `pdf_parallel_build()`, `handle_info()`, `handle_man()`, `cleandocs()`, and `build()`. `TARGETS` maps kernel make targets to Sphinx builders and output subdirectories. `jobs_type()` validates `-j`. `main()` checks Python version and dispatches.

Control flow: Initialization reads environment such as `KERNELVERSION`, `KERNELRELEASE`, `PDFLATEX`, `PYTHON3`, `LATEXOPTS`, `srctree`, `SPHINXBUILD`, and `KERNELDOC`. `build()` prepares Sphinx arguments for each `SPHINXDIRS` entry, runs `sphinx-build` with jobserver-aware parallelism, handles `mandocs` directly via `kernel-doc`, then performs target-specific post-steps for HTML/EPUB, PDF, info, and Rust docs.

State and persistence: Persistent output is under `--builddir` with per-directory Sphinx output and `.doctrees`; `cleandocs` deletes that tree. The process mutates environment passed to subprocesses, optionally activates a venv by changing `PATH`/`VIRTUAL_ENV`, and may set `LC_ALL` or `XDG_CONFIG_HOME`.

Dependencies/integration: Integrated with the kernel documentation Makefile. Depends on `sphinx-build`, local `tools/docs/kernel-doc`, GNU make jobserver support through `jobserver.JobserverExec`, LaTeX tools for PDF, `kdoc.python_version`, and `kdoc.latex_fonts`.

Risks/tests: Risks include incorrect jobserver claims, broken cross-directory references from per-directory builds, LaTeX false failures, locale-sensitive Sphinx crashes, and manpage splitting based on `.TH`. Test signals include all target mappings (`htmldocs`, `mandocs`, `pdfdocs`, `infodocs`, `cleandocs`), venv mode, `SPHINXOPTS` parsing, missing tool paths, Rust-enabled `.config`, and parallel PDF output checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/docs/sphinx-build-wrapper -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/docs/sphinx-pre-install -->
# sources/distributed-fs/ceph-client/tools/docs/sphinx-pre-install

Purpose: Dependency checker and install-hint generator for kernel Sphinx documentation builds, including system tools, Python modules, Sphinx versions, virtual environments, and optional PDF/LaTeX dependencies.

Important APIs/types/functions: `DepManager` tracks missing dependency classes. `AncillaryMethods` provides compatibility wrappers for `which()` and `subprocess.run()`. `MissingCheckers` implements file, program, Perl, Python, RPM, pacman, TeX, Sphinx-version, and distro-release checks. `SphinxDependencyChecker` adds distro-specific hint methods for Debian, Red Hat, openSUSE, Mageia/OpenMandriva, Arch, and Gentoo, plus venv recommendation logic and `check_needs()`.

Control flow: `main()` parses `--no-virtualenv`, `--no-pdf`, and `--version-check`, checks Python compatibility, then runs `check_needs()`. That method reads `Documentation/conf.py` for `needs_sphinx`, detects the OS, checks current and venv Sphinx versions, probes mandatory/optional dependencies, emits package-manager commands, and exits nonzero when mandatory dependencies remain missing.

State and persistence: It does not install packages itself. It reads OS metadata, `Documentation/conf.py`, requirements files, `/etc/portage/package.use` on Gentoo, and possible existing `sphinx_*` or `Sphinx_*` virtualenv directories. State is in dependency counters and printed recommendations.

Dependencies/integration: Integrated with kernel documentation setup workflows and Makefile diagnostics. Depends on distro package tools (`rpm`, `pacman`, etc. when available), `kpsewhich`, Perl, Python imports, and kernel-local `kdoc.python_version`.

Risks/tests: Risks include stale distro mappings, wrong package names, false PDF dependency failures, Python-version recommendation bugs, and command suggestions that are unsafe for unusual systems. Test signals are container smoke tests for supported distros, `--version-check`, `--no-pdf`, missing-Sphinx scenarios, existing venv selection, and mandatory/optional dependency counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/docs/sphinx-pre-install -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/docs/test_doc_build.py -->
# sources/distributed-fs/ceph-client/tools/docs/test_doc_build.py

Purpose: Creates version-specific Sphinx virtual environments and optionally runs kernel documentation builds against them to validate supported Sphinx/version dependency combinations.

Important APIs/types/functions: `DEFAULT_VERSIONS_TO_TEST`, `SPHINX_REQUIREMENTS`, and `PYTHON_VER_CHANGES` encode tested Sphinx/dependency/Python combinations. `AsyncCommands` runs subprocesses asynchronously while teeing output. `SphinxVenv` drives venv creation, pip installs, requirement freezing, optional `make cleandocs` and target builds. `parse_version()` parses CLI versions; `main()` handles version ranges and build options.

Control flow: The script chooses the oldest available Python 3.9-3.12 binary when possible, accumulates incremental package requirements as Sphinx versions increase, then for each requested version creates `Sphinx_<version>`, installs pinned dependencies plus Sphinx, optionally writes `requirements_<version>.txt`, and optionally runs make targets with the venv on `PATH`.

State and persistence: Persistent outputs include `Sphinx_*` virtualenv directories, optional requirements files, optional logs, and build output directories from make. Runtime state tracks elapsed build times.

Dependencies/integration: Depends on `python -m venv`, `pip`, network/package indexes unless cached, `make`, and kernel doc targets. It complements `sphinx-pre-install` by generating/test-driving exact venvs rather than just recommending them.

Risks/tests: Risks include heavy network and build cost, old Sphinx memory behavior, partially created venvs after failure, and dependency pins becoming unavailable. Test signals are dry creation for one version, `--req-file` freeze contents, `--build` on constrained `SPHINXDIRS`, `--min/--max`, `--full`, and log review.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/docs/test_doc_build.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/firewire/Makefile -->
# sources/distributed-fs/ceph-client/tools/firewire/Makefile

Purpose: Builds, cleans, and installs the FireWire `nosy-dump` userspace sniffer tool.

Important APIs/types/functions: Make targets are `all`, `nosy-dump`, `clean`, and `install`. It sets `nosy-dump-version = 0.4`, compiles with `-Wall -O2 -g`, defines `VERSION`, includes `../../drivers/firewire`, links `nosy-dump.o` and `decode-fcp.o`, and links against `-lpopt`.

Control flow: Default target builds `nosy-dump`; object generation uses make built-ins plus the target-specific variables. `install` copies the binary to `$(prefix)/bin/nosy-dump`.

State and persistence: Build artifacts are `*.o` and `nosy-dump`; install persists a binary under `prefix`, default `/usr`.

Dependencies/integration: Depends on a C compiler, libpopt development files, kernel FireWire headers, `nosy-user.h`, and Linux FireWire constants. It is a standalone tools build rather than Kbuild proper.

Risks/tests: Risks include missing libpopt, stale include path to driver headers, and install without `DESTDIR`. Test signals are `make`, `make clean`, `make install DESTDIR=...`, and running `nosy-dump --version`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/firewire/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/firewire/decode-fcp.c -->
# sources/distributed-fs/ceph-client/tools/firewire/decode-fcp.c

Purpose: Adds FCP/AV-C protocol decoding to `nosy-dump` transactions so FireWire control frames are printed as human-readable command summaries.

Important APIs/types/functions: Data tables map AV/C `ctype`, subunit types, opcodes, and selected fields. `struct avc_frame` overlays the FCP payload. `decode_avc()` prints AV/C command type, subunit, opcode name, and field names. `decode_fcp()` is the exported decoder called with `struct link_transaction *`.

Control flow: `decode_fcp()` accepts only write-block requests to CSR FCP command/response offsets. It switches on `frame->cts`; CTS 0 routes to `decode_avc()`, other known CTS values print protocol names, and unknown/reserved values print a fallback. It returns `1` only when it handled an FCP frame.

State and persistence: No persistent state. It reads the current transaction request packet and prints to stdout.

Dependencies/integration: Depends on `linux/firewire-constants.h`, `nosy-dump.h`, and transaction assembly in `nosy-dump.c`. Integrated through the `protocol_decoders` table.

Risks/tests: Risks include unchecked payload size before casting to `avc_frame`, compiler-dependent bitfield layout, incomplete field value decoding, and assuming FCP offset constants. Test signals are captured FCP command/response logs, unknown opcode coverage, non-FCP write-block rejection, and big/little-endian smoke testing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/firewire/decode-fcp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/firewire/list.h -->
# sources/distributed-fs/ceph-client/tools/firewire/list.h

Purpose: Minimal intrusive doubly linked list helpers used by the FireWire sniffer to track pending transactions and subactions.

Important APIs/types/functions: Defines `struct list` and inline helpers `list_init()`, `list_empty()`, `list_insert()`, `list_append()`, `list_prepend()`, and `list_remove()`. Macros `list_entry`, `list_head`, `list_tail`, `list_next`, and `list_for_each_entry` provide container traversal.

Control flow: Lists are circular with the head pointing to itself when empty. Insertions splice before the supplied link; append/prepend are small wrappers.

State and persistence: State is embedded in caller-owned structs. Removal only rewires neighbors and does not poison or clear the removed link.

Dependencies/integration: Used by `nosy-dump.c` and `nosy-dump.h` structures. Relies on GNU `typeof` in traversal macros.

Risks/tests: Risks include double removal, iterating empty lists with `list_head()`, and use-after-free if callers free nodes during unsafe traversal. Test signals are transaction list add/remove sequences, empty-list checks, and compilation with the intended GNU C dialect.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/firewire/list.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/firewire/nosy-dump.c -->
# sources/distributed-fs/ceph-client/tools/firewire/nosy-dump.c

Purpose: Userspace decoder/logger for the `/dev/nosy` FireWire snoop driver, supporting packet, transaction, and statistics views plus replay from captured binary logs.

Important APIs/types/functions: CLI options are defined with `popt`. Transaction state uses `struct subaction` and `struct link_transaction` from `nosy-dump.h`, stored in `pending_transaction_list`. Core functions include `subaction_create()`, `link_transaction_lookup()`, `handle_request_packet()`, `handle_response_packet()`, `handle_packet()`, `decode_link_packet()`, `print_packet()`, `print_stats()`, terminal mode helpers, and `main()`.

Control flow: Live mode opens `/dev/nosy`, configures noncanonical stdin, applies a tcode filter with `NOSY_IOC_FILTER`, starts capture with `NOSY_IOC_START`, then polls the device and stdin. Replay mode reads records from an input file. Packet view decodes each packet immediately; transaction view assembles requests/responses by node and tlabel before protocol decoding; stats view updates counters periodically.

State and persistence: Runtime state includes global options, pending transaction lists, terminal attributes, stats counters, and output file handles. Persistent state is optional binary capture output containing length-prefixed packet records.

Dependencies/integration: Depends on Linux FireWire constants, `nosy-user.h` ioctls from the driver include path, libpopt, terminal APIs, and the FCP decoder. It integrates directly with the kernel nosy driver and FireWire packet formats.

Risks/tests: Risks include raw packet length trust, bitfield/endian assumptions, terminal restoration on abrupt exit, infinite pending transaction growth for incomplete captures, and limited transaction decoding because `handle_transaction()` currently returns after FCP handling. Test signals are live capture, replay input, `--hex`, `--stats`, `--transaction`, iso/cycle filters, SIGINT behavior, and malformed/short packet logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/firewire/nosy-dump.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/firewire/nosy-dump.h -->
# sources/distributed-fs/ceph-client/tools/firewire/nosy-dump.h

Purpose: Shared packet and transaction structure definitions for `nosy-dump` and protocol decoders.

Important APIs/types/functions: Defines ACK helper macros, `TCODE_PHY_PACKET`, PHY packet identifiers, `struct phy_packet`, `struct link_packet`, `struct subaction`, and `struct link_transaction`. Declares `int decode_fcp(struct link_transaction *t)`.

Control flow: This header has no executable flow, but its unions/bitfields define how packet decoding code interprets captured quadlets. Flexible-array members in block packet layouts model variable payload data followed by CRC/ACK.

State and persistence: The structs represent in-memory decoded packet state and pending transactions. No persistence is defined here.

Dependencies/integration: Includes `<stdint.h>` and `list.h`; uses Linux FireWire tcode constants indirectly through C files. It is the contract between `nosy-dump.c` and `decode-fcp.c`.

Risks/tests: Risks are ABI/layout assumptions from C bitfields, zero-length arrays, and host endian differences. Test signals include compilation on target architectures, packet decode comparisons against known FireWire traces, and sanitizers for variable-length packet access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/firewire/nosy-dump.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/firmware/Makefile -->
# sources/distributed-fs/ceph-client/tools/firmware/Makefile

Purpose: Builds and cleans the `ihex2fw` firmware conversion utility.

Important APIs/types/functions: Targets are `all`, pattern rule `%: %.c`, and `clean`. It uses `CFLAGS = -Wall -Wextra -g`, builds `ihex2fw` from `ihex2fw.c`, and removes the binary via `$(RM)`.

Control flow: Default `all` depends on `ihex2fw`; the generic C pattern invokes `$(CC) $(CFLAGS) -o $@ $^`.

State and persistence: Build output is the `ihex2fw` binary. No install target is present.

Dependencies/integration: Depends only on a C compiler and standard C/POSIX headers used by `ihex2fw.c`.

Risks/tests: Risks are limited to generic pattern-rule collisions and missing custom `LDFLAGS`. Test signals are `make`, `make clean`, and running conversion fixtures through the built binary.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/firmware/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/firmware/ihex2fw.c -->
# sources/distributed-fs/ceph-client/tools/firmware/ihex2fw.c

Purpose: Converts Intel HEX firmware data into the binary firmware record format consumed by the Linux kernel firmware loader.

Important APIs/types/functions: `struct ihex_binrec` stores linked records with address, length, and data. Helpers `nybble()` and `hex()` parse bytes while accumulating checksum. `process_ihex()` parses records; `file_record()` inserts into the global list, optionally sorted; `ihex_binrec_size()` calculates serialized size; `output_records()` writes network-endian records and a zero-length EOF record. Options are `-w` for 16-bit length fields, `-s` sorting, and `-j` including start-address records.

Control flow: `main()` parses options, opens or uses stdin/stdout, mmaps the input, parses records, then serializes the accumulated list. `process_ihex()` scans for `:`, validates length/checksum, handles data records, EOF, extended segment/linear address records, and optional start address records.

State and persistence: Runtime globals control sorting, wide records, and jump inclusion; `records` is a global linked list. Persistent output is the binary `.fw` stream. Input is memory-mapped and records are heap allocated until process exit.

Dependencies/integration: Uses POSIX file APIs, `mmap`, endian conversions from `<arpa/inet.h>`, and Linux-style alignment macros. It integrates with firmware build workflows that need `.HEX` to kernel binary firmware conversion.

Risks/tests: Risks include stdin with `mmap` when size is not meaningful, unchecked short `fread` equivalent absent because of mmap, memory leaks on parse errors, wide-record compatibility, checksum edge cases, and integer/address wraparound. Test signals are known Intel HEX fixtures for record types 00-05, bad checksum, unsorted vs sorted output, `-j`, stdin/stdout, and binary EOF record validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/firmware/ihex2fw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/gpio/Makefile -->
# sources/distributed-fs/ceph-client/tools/gpio/Makefile

Purpose: Builds, cleans, and installs Linux GPIO character-device helper tools: `lsgpio`, `gpio-hammer`, `gpio-event-mon`, and `gpio-watch`.

Important APIs/types/functions: Uses `tools/build/Makefile.include` and per-tool `$(build)=...` invocations. `prepare` symlinks `../../include/uapi/linux/gpio.h` into `$(OUTPUT)include/linux/gpio.h`. `ALL_TARGETS` maps to `ALL_PROGRAMS`; `install` copies binaries to `$(DESTDIR)$(bindir)`.

Control flow: The Makefile computes `srctree` for in-tree or selftest-style builds, disables built-in rules, exports build variables, builds a shared `gpio-utils-in.o` where needed, then links each final tool.

State and persistence: Build artifacts live under `$(OUTPUT)`, including generated include symlink, intermediate `*-in.o` files, `.cmd`/dependency files, and final binaries. `clean` removes binaries, generated include directory, and object/dependency files.

Dependencies/integration: Depends on the kernel tools build system, UAPI GPIO header, C compiler, and standard Linux userspace headers. It can be built inside tools or from selftests.

Risks/tests: Risks include incorrect `srctree` inference, stale symlinked UAPI header, and clean rules deleting unexpected files if `OUTPUT` is unusual. Test signals are in-tree and out-of-tree builds, `make clean`, `make install DESTDIR=...`, and execution against a test gpiochip or mock device.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/gpio/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/gpio/gpio-event-mon.c -->
# sources/distributed-fs/ceph-client/tools/gpio/gpio-event-mon.c

Purpose: Monitors GPIO line edge events from userspace using the GPIO v2 character-device API.

Important APIs/types/functions: `monitor_device()` requests one or more input lines with event flags, reads initial values, then reads `struct gpio_v2_line_event` records. `main()` parses `-n`, repeated `-o`, `-r`, `-f`, `-d`, `-s`, `-w`, `-t`, `-b`, and `-c`. `EDGE_FLAGS` defaults to both rising and falling edges.

Control flow: CLI parsing fills a `gpio_v2_line_config`; debounce is added as a line attribute over all selected lines. `monitor_device()` opens `/dev/<gpiochip>`, requests the event line fd through `gpiotools_request_line()`, prints initial values, then blocks reading events until the optional loop count is reached or an error occurs.

State and persistence: Holds chip and line fds during monitoring; no persistent state. Event output is printed to stdout with timestamp, offset, line sequence, global sequence, and edge type.

Dependencies/integration: Depends on `<linux/gpio.h>` v2 ioctls and shared `gpio-utils` helpers. Integrates with GPIO chardev event facilities and optional hardware timestamp engine clock selection.

Risks/tests: Risks include an ineffective `errno == -EAGAIN` check, missing nonblocking setup despite mentioning no data, line-count bounds, debounce attribute mask mistakes, and open drain/source combinations on input lines. Test signals are rising/falling event generation, multiple lines, debounce, realtime/HTE timestamps, loop termination, and invalid chip/offset handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/gpio/gpio-event-mon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/gpio/gpio-hammer.c -->
# sources/distributed-fs/ceph-client/tools/gpio/gpio-hammer.c

Purpose: Example tool that repeatedly toggles one or more GPIO output lines and reports their observed states.

Important APIs/types/functions: `hammer_device()` requests selected lines as outputs, initializes a `gpio_v2_line_values` mask, toggles bits with `gpiotools_change_bit()`, writes with `gpiotools_set_values()`, reads back with `gpiotools_get_values()`, and releases the line fd. `main()` parses `-n`, repeated `-o`, optional `-c`, and `-?`.

Control flow: After validation, the tool requests all selected lines together, prints initial states, then sleeps one second per toggle iteration. `loops == 0` means infinite operation.

State and persistence: Runtime state is the held line request fd, values mask/bits, loop counter, and spinner output. There is no persisted configuration.

Dependencies/integration: Depends on GPIO v2 chardev UAPI and `gpio-utils`. It is an interactive/manual exerciser rather than a library.

Risks/tests: Risks include using legacy `GPIOHANDLES_MAX` while v2 APIs use `GPIO_V2_LINES_MAX`, off-by-one reporting for too many `-o` options, and toggling real hardware outputs without safety interlocks. Test signals are loop-limited toggles on dummy GPIO, multiple-line masks, invalid line offsets, and clean release on ioctl failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/gpio/gpio-hammer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/gpio/gpio-sloppy-logic-analyzer.sh -->
# sources/distributed-fs/ceph-client/tools/gpio/gpio-sloppy-logic-analyzer.sh

Purpose: Shell helper for the kernel sloppy GPIO logic analyzer debugfs interface; configures sampling, optional CPU isolation, optional triggers, and packages captures as Sigrok `.sr` archives.

Important APIs/types/functions: Functions include `parse_si()` for SI-number parsing, `init_cpu()` for cpuset/IRQ/workqueue/task affinity isolation, `parse_triggerdat()` for trigger string encoding, `do_capture()` for capture and archive generation, and helpers `fail()`/`set_newmask()`. CLI options cover CPU, duration, instance, debugfs path, list instances, sample count/frequency, output directory, and trigger patterns.

Control flow: The script validates required commands, finds or mounts cpuset cgroups, locates `/sys/kernel/debug/gpio-sloppy-logic-analyzer/<instance>`, optionally isolates a CPU, writes delay/buffer/trigger sysfs attributes, computes an isolated CPU mask, and launches `do_capture()` in the background.

State and persistence: Mutates system state: cpuset directories, IRQ affinities, workqueue masks, task CPU affinities, RCU stall suppression, and CPU frequency governor. Persistent capture output is a timestamped `.sr` zip containing metadata and binary sample data.

Dependencies/integration: Depends on root/debugfs access, kernel sloppy logic analyzer debugfs files, cpuset cgroup support, `taskset`, `zip`, `awk`, `find`, `ps`, and shell arithmetic.

Risks/tests: Risks are significant because it changes global CPU/IRQ/workqueue affinity and does not restore it, uses background capture after the parent exits, and writes debugfs/sysfs attributes directly. Test signals are `--list-instances`, dry validation on a test instance, trigger encoding for levels/edges, sample frequency capping output, `.sr` archive load in PulseView, and post-run CPU affinity audits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/gpio/gpio-sloppy-logic-analyzer.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/gpio/gpio-utils.c -->
# sources/distributed-fs/ceph-client/tools/gpio/gpio-utils.c

Purpose: Shared helper library for the GPIO tools, wrapping GPIO v2 character-device ioctls for requesting, reading, writing, and releasing lines.

Important APIs/types/functions: `gpiotools_request_line()` opens `/dev/<gpiochip>` and issues `GPIO_V2_GET_LINE_IOCTL`. `gpiotools_set_values()` and `gpiotools_get_values()` wrap line value ioctls. `gpiotools_release_line()` closes a line fd. Convenience APIs `gpiotools_get()`, `gpiotools_gets()`, `gpiotools_set()`, and `gpiotools_sets()` request, operate, and release in one call.

Control flow: Request fills offsets, copies config and consumer, closes the chip fd, and returns the new line fd. Get helpers request input lines, set value masks, read bits, copy results to caller arrays, then release. Set helpers build output-value line attributes, request output lines with initial values, then release immediately.

State and persistence: No persistent state. State exists only in file descriptors and caller-provided `gpio_v2_line_*` structs. Convenience setters do not hold outputs after returning because the line fd is released.

Dependencies/integration: Depends on `/dev/gpiochip*`, `<linux/gpio.h>` v2 ABI, `asprintf`, and helper bit functions from `gpio-utils.h`. Used by `lsgpio`, `gpio-hammer`, and `gpio-event-mon`.

Risks/tests: Risks include unchecked `strcpy()` into `req.consumer`, uninitialized `gpio_v2_line_values` masks if callers fail to zero them, immediate release semantics surprising users of `gpiotools_set()`, and inconsistent legacy ioctl names in error text. Test signals are request/get/set/release against gpio-sim, multi-line masks, invalid consumer lengths, permission failures, and close-error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/gpio/gpio-utils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/gpio/gpio-utils.h -->
# sources/distributed-fs/ceph-client/tools/gpio/gpio-utils.h

Purpose: Declares the GPIO tool helper API and inline bit operations for GPIO v2 line value masks.

Important APIs/types/functions: Declares request/value/release APIs and one-shot get/set helpers. Defines `ARRAY_SIZE`, `check_prefix()`, and inline bit helpers `gpiotools_set_bit()`, `gpiotools_change_bit()`, `gpiotools_clear_bit()`, `gpiotools_test_bit()`, and `gpiotools_assign_bit()` over `__u64`.

Control flow: Header-only helpers perform direct bit manipulation using `_BITULL(n)` from Linux type/bit headers.

State and persistence: No persistent state; helpers mutate caller-provided mask/value words.

Dependencies/integration: Includes `<linux/types.h>` and relies on GPIO v2 structs from translation units that include `<linux/gpio.h>`. Shared by all GPIO C tools.

Risks/tests: Risks include undefined shifts for out-of-range bit indices and `check_prefix()` intentionally requiring the tested string to be longer than the prefix. Test signals are mask helper unit tests for indices 0 and max line count, prefix matching for `gpiochip`, and compiler coverage with current UAPI headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/gpio/gpio-utils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/gpio/gpio-watch.c -->
# sources/distributed-fs/ceph-client/tools/gpio/gpio-watch.c

Purpose: Watches unrequested GPIO lines for line-info changes such as request, release, or configuration changes.

Important APIs/types/functions: `main()` opens a gpiochip path supplied as argv[1], issues `GPIO_V2_GET_LINEINFO_WATCH_IOCTL` for each supplied line offset, then polls the chip fd and reads `struct gpio_v2_line_info_changed` events.

Control flow: After registering watches, the process loops forever with a 5-second poll timeout. When an event arrives it maps event type to text and prints line offset, event name, and timestamp.

State and persistence: Runtime state is the chip fd and kernel watch registrations associated with it. No persistent state is written.

Dependencies/integration: Depends on GPIO v2 line-info watch ABI and poll/read on the gpiochip character device. Unlike the other GPIO tools, it does not use `gpio-utils`.

Risks/tests: Risks include no way to unregister except process exit, infinite loop without signal cleanup needs, sparse argument validation, and failure if lines are requested before watch setup. Test signals are watching a gpio-sim chip while another process requests/releases/configures lines, invalid offset parsing, and read-size error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/gpio/gpio-watch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/gpio/lsgpio.c -->
# sources/distributed-fs/ceph-client/tools/gpio/lsgpio.c

Purpose: Lists GPIO chips and their lines, including names, consumers, flags, edge settings, and debounce attributes.

Important APIs/types/functions: `struct gpio_flag` and `flagnames[]` map GPIO v2 flags to text. `print_attributes()` prints flag and debounce attributes. `list_device()` opens `/dev/<gpiochip>`, issues `GPIO_GET_CHIPINFO_IOCTL`, then loops over line offsets with `GPIO_V2_GET_LINEINFO_IOCTL`. `main()` parses optional `-n` or scans `/dev` for `gpiochip*`.

Control flow: With `-n`, it lists exactly one chip. Without `-n`, it opens `/dev`, filters entries with `check_prefix()`, and lists each chip until failure, then closes the directory.

State and persistence: No persistent state. It opens each chip temporarily and prints inspection output.

Dependencies/integration: Depends on GPIO UAPI, `/dev/gpiochip*`, `gpio-utils.h` for `ARRAY_SIZE` and `check_prefix()`, and standard directory/ioctl APIs.

Risks/tests: Risks include races while scanning `/dev`, line info changing while listed, incomplete flag-name coverage for newer UAPI flags, and treating no devices as success after scan. Test signals are gpio-sim chips with named/unnamed lines, active-low/bias/edge/debounce flags, `-n` invalid device, and multi-chip scans.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/gpio/lsgpio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/hv/Makefile -->
# sources/distributed-fs/ceph-client/tools/hv/Makefile

Purpose: Builds and installs Hyper-V guest userspace daemons and helper scripts.

Important APIs/types/functions: Targets build `hv_kvp_daemon` and `hv_vss_daemon`, plus `hv_fcopy_uio_daemon` on x86/x86_64. `ALL_SCRIPTS` includes DHCP, DNS, and ifconfig helper scripts. The Makefile uses `tools/build/Makefile.include`, sets `-D_GNU_SOURCE`, includes `$(OUTPUT)include`, and suppresses packed-member address warnings.

Control flow: It computes `srctree` when unset, disables built-in rules, exports build variables, invokes per-daemon build recipes, links final binaries, and installs binaries to `sbindir`, scripts to `libexecdir)/hypervkvpd` without `.sh`, and creates `sharedstatedir`.

State and persistence: Build artifacts are under `$(OUTPUT)`. Install persists system binaries/scripts under `/usr/sbin`, `/usr/libexec/hypervkvpd`, and `/var/lib` by default.

Dependencies/integration: Depends on kernel tools build infrastructure, Hyper-V UAPI headers, compiler/linker, and `lsvmbus`. It integrates with Hyper-V guest services and distro packaging.

Risks/tests: Risks include architecture gating for fcopy, install paths not matching distro policy, and script renaming expectations from daemons. Test signals are x86 and non-x86 builds, `make clean`, staged install with `DESTDIR`, and service packaging checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/hv/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/hv/hv_fcopy_uio_daemon.c -->
# sources/distributed-fs/ceph-client/tools/hv/hv_fcopy_uio_daemon.c

Purpose: Implements Hyper-V host-to-guest file copy service using the VMBus UIO channel for the fcopy integration component.

Important APIs/types/functions: `get_ring_buffer_size()` discovers channel ring size from sysfs. File operations are `hv_fcopy_create_file()`, `hv_copy_data()`, `hv_copy_finished()`, `hv_fcopy_start()`, and `hv_fcopy_send_data()`. Protocol negotiation uses `vmbus_prep_negotiate_resp()`. `fcopy_pkt_process()` parses incoming VMBus packets and sends responses through `rte_vmbus_chan_send()`. `fcopy_get_first_folder()` discovers UIO instance; `main()` daemonizes, maps rings, and runs the receive loop.

Control flow: On startup the daemon optionally forks, opens syslog, discovers ring size and UIO device, mmaps Tx/Rx rings, unmasks interrupts, then waits on `pread()` from `/dev/uio*`. Each notification receives a raw VMBus packet, handles negotiate or fcopy message, writes a response into the Tx ring, and signals the host by writing to the UIO fd.

State and persistence: Global state includes the packet buffer `desc`, current `target_fd`, `target_fname`, and `filesize`. Persistent side effects are files/directories created from host-supplied path/name and copy flags. It writes syslog records and keeps the daemon process running indefinitely.

Dependencies/integration: Depends on Hyper-V kernel UAPI (`linux/hyperv.h`), `vmbus_bufring` helpers, sysfs paths for the fcopy VMBus device UUID, `/dev/uio*`, locale/wide-character conversion, and syslog. It is installed only on x86/x86_64 by the Makefile.

Risks/tests: Risks include trusting host-supplied paths, limited UTF-16 conversion replacing non-ASCII with `X`, path creation by mutating `path_name`, target fd lifecycle if a copy aborts, race-prone first-folder discovery, and packet-length validation gaps beyond the fcopy header. Test signals are negotiation version match/mismatch, create/no-overwrite/create-path flags, writes with offsets, ENOSPC mapping, complete-copy close, UIO disconnect/error paths, foreground `--no-daemon`, and sysfs discovery retries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/hv/hv_fcopy_uio_daemon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/hv/hv_get_dhcp_info.sh -->
# sources/distributed-fs/ceph-client/tools/hv/hv_get_dhcp_info.sh

Purpose: Example external helper for the Hyper-V KVP daemon to report whether DHCP is enabled on a network interface.

Important APIs/types/functions: Takes one positional interface name. Builds `/etc/sysconfig/network-scripts/ifcfg-$1`, greps for `dhcp`, and prints `Enabled` if found or `Disabled` otherwise.

Control flow: A single grep decides the output. Missing files or grep errors are ignored through stderr redirection and treated as disabled.

State and persistence: No state is modified. Output is a single status string consumed by the KVP daemon.

Dependencies/integration: Assumes Red Hat-style network-scripts configuration files. It is installed by the Hyper-V Makefile under `hypervkvpd/hv_get_dhcp_info` for daemon invocation.

Risks/tests: Risks include unquoted interface-derived path, false positives for any `dhcp` substring, incompatibility with NetworkManager/systemd-networkd/netplan, and no distinction between static config and missing config. Test signals are fixtures for DHCP/static/missing ifcfg files and interface names with unusual characters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/hv/hv_get_dhcp_info.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/hv/hv_get_dns_info.sh -->
# sources/distributed-fs/ceph-client/tools/hv/hv_get_dns_info.sh

Purpose: Example external helper for the Hyper-V KVP daemon to print configured DNS nameserver addresses.

Important APIs/types/functions: Runs `awk '/^nameserver/ { print $2 }' /etc/resolv.conf` and redirects awk stderr to `/dev/null`.

Control flow: The script replaces itself with awk via `exec`; every `nameserver` line emits the second field.

State and persistence: No state is modified. Output is a newline-separated list of resolver addresses.

Dependencies/integration: Depends on `/etc/resolv.conf` semantics and awk. It is installed by the Hyper-V Makefile under `hypervkvpd/hv_get_dns_info`.

Risks/tests: Risks include resolver state managed elsewhere, comments/spacing not handled beyond lines starting exactly with `nameserver`, and no validation of printed addresses. Test signals are resolv.conf fixtures with IPv4/IPv6, leading whitespace, comments, missing file, and daemon consumption of multiple lines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/hv/hv_get_dns_info.sh -->
