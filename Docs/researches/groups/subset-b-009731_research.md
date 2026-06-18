# subset-b-009731 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/nfs-iostat/nfs-iostat.py -->
# sources/user-network-fs/nfs-utils/tools/nfs-iostat/nfs-iostat.py

## Purpose

`nfs-iostat.py` is an iostat-like NFS client reporting tool. It reads `/proc/self/mountstats`, isolates NFS and NFSv4 mount entries, parses per-mount VFS, byte, transport, and per-RPC-operation counters, and prints interval or since-mount summaries for file I/O, attribute cache, directory cache, or page cache activity.

## Important APIs, Types, and Functions

`DeviceData` owns parsed NFS and RPC dictionaries for one mount. `__parse_nfs_line` handles mount identity, age, options, capabilities, security, event counters, and byte counters; `__parse_rpc_line` handles RPC header, transport statistics for `udp`, `tcp`, and `rdma`, and per-op rows. `compare_iostats` computes deltas against an older snapshot. `display_iostats`, `__print_rpc_op_stats`, and cache/page helper printers format reports. `parse_stats_file`, `list_nfs_mounts`, `print_iostat_summary`, and `iostat_command` are the command-level parsing and reporting pipeline.

## Control Flow

Startup parses the current mountstats file, interprets positional arguments as mountpoints, interval, and count, and configures display mode through `optparse`. The first report shows counters since mount age. If an interval is provided, the loop sleeps, reparses mountstats, filters current NFS mounts again to handle mount churn, computes deltas against the previous snapshot, optionally sorts by operations per second, and prints up to `--list` entries.

## State and Persistence Behavior

The script keeps only in-memory snapshots. It does not persist state or modify the system. The durable source of truth is the kernel-generated `/proc/self/mountstats`; interval reports are derived by subtracting previous in-process counters.

## Dependencies and Integration Points

It depends on Python 3 standard modules, `/proc/self/mountstats` format, NFS client stat versions, and shell invocation as the installed `nfsiostat` tool. It integrates with nfs-utils packaging and user diagnostics rather than daemon control paths.

## Risks and Edge Cases

Parsing is tightly coupled to mountstats field positions, including older non-`device` lines and `statvers` handling. `parse_stats_file` misses `f.close()` parentheses, relying on process cleanup. Several cache views assume operations such as `LOOKUP`, `READDIR`, `READ`, or `WRITE` exist in parsed RPC data. Counter wrap, remounts, transport field changes, or malformed proc data can produce bad deltas or `KeyError`s. The argument parser treats an argument as a mountpoint only if its normalized path exists in the initial snapshot, so newly mounted paths cannot be selected later in the same run.

## Test Signals

Useful tests should feed fixture mountstats data for NFSv3, NFSv4, TCP, UDP, and RDMA; verify first-sample and delta math; cover zero-age and zero-operation divisions; check sort/list behavior; test mount disappearance; and exercise each display mode against missing optional ops such as `READDIRPLUS`.

<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/nfs-iostat/nfs-iostat.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/nfsconf/Makefile.am -->
# sources/user-network-fs/nfs-utils/tools/nfsconf/Makefile.am

## Purpose

This Automake fragment builds and installs the `nfsconf` administrative binary and its man page.

## Important APIs, Types, and Functions

It declares `man8_MANS = nfsconf.man`, `sbin_PROGRAMS = nfsconf`, `nfsconf_SOURCES = nfsconfcli.c`, and links `nfsconf` against `../../support/nfs/libnfsconf.la`.

## Control Flow

Automake turns this into build rules that compile `nfsconfcli.c`, link the support nfs configuration library, install the program into `sbindir`, install the manual page, and clean generated `Makefile.in` during maintainer cleanup.

## State and Persistence Behavior

The file has no runtime state. Its install layout determines where the CLI and documentation persist on target systems.

## Dependencies and Integration Points

It integrates the tool with the top-level nfs-utils build and depends on the local nfs configuration support library that provides `conf_*` APIs used by `nfsconfcli.c`.

## Risks and Edge Cases

Build failures here usually indicate the support library was not configured or generated correctly. Because the binary is installed in `sbindir`, packaging must preserve privileged-admin path expectations.

## Test Signals

Build tests should confirm `make`, `make install DESTDIR=...`, and maintainer cleanup include `nfsconf`, `nfsconf.man`, and the support library dependency.

<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/nfsconf/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/nfsconf/nfsconfcli.c -->
# sources/user-network-fs/nfs-utils/tools/nfsconf/nfsconfcli.c

## Purpose

`nfsconfcli.c` implements the `nfsconf` command-line editor/query tool for nfs-utils configuration files. It can dump a parsed config, retrieve interpreted or raw entries, check for presence, set a value, or unset a value.

## Important APIs, Types, and Functions

`confmode_t` enumerates mutually intended modes: get, entry, isset, dump, set, and unset. `usage` documents arguments. `main` parses long options with `getopt_long`, configures xlog, calls `conf_init_file`, `conf_report`, `conf_get_section`, `conf_get_entry`, `conf_write`, and `conf_cleanup`. It also writes through the global `modified_by` header string used by the config writer.

## Control Flow

The CLI selects a mode from options, records an optional config path, optional subsection argument, verbosity, dump output file, and modified-header text. Read-only modes initialize the config parser before use. Dump writes the complete report to stdout or a named file. Get, entry, and isset require section and tag and return success only when a value exists. Set and unset require section/tag and optional value, treating an empty string set as unset, then call `conf_write`.

## State and Persistence Behavior

Read modes are transient. Set and unset modify the target config file through `conf_write`, using the support library's preservation and modified-header behavior. The process keeps parsed config state until `conf_cleanup`.

## Dependencies and Integration Points

The file depends on `config.h`, `conffile.h`, and `xlog.h`, and on `NFS_CONFFILE`. It is the user-facing CLI for the same nfs configuration parser used by other nfs-utils components.

## Risks and Edge Cases

Multiple mode options are not rejected; the last parsed mode wins. Set/unset deliberately skip `conf_init_file`, so correctness depends on `conf_write` doing the necessary file read/update itself. Optional-argument handling for `--dump` manually consumes the next positional filename. Argument validation is minimal and returns status 2 for usage errors, 1 for missing values or write failures.

## Test Signals

Tests should cover every mode, custom `--file`, subsection `--arg`, empty-string set-as-unset, `--modified ""`, dump to file failures, last-mode-wins behavior, return codes for missing tags, and verbose logging.

<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/nfsconf/nfsconfcli.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/nfsdclddb/Makefile.am -->
# sources/user-network-fs/nfs-utils/tools/nfsdclddb/Makefile.am

## Purpose

This Automake file packages the Python `nfsdclddb` sqlite database maintenance tool and its manual page.

## Important APIs, Types, and Functions

It sets `PYTHON_FILES = nfsdclddb.py`, includes `nfsdclddb.man` in `man8_MANS`, adds both to `EXTRA_DIST`, and installs the Python script as executable `$(sbindir)/nfsdclddb` in `install-data-hook`.

## Control Flow

The build keeps the script as data rather than compiling it, and install copies it with mode `755`. Maintainer cleanup removes generated `Makefile.in`.

## State and Persistence Behavior

No runtime state exists here. The install hook determines the persistent executable path and permissions.

## Dependencies and Integration Points

It integrates the standalone Python sqlite tool with nfs-utils install and documentation paths.

## Risks and Edge Cases

The install hook assumes `$(sbindir)` exists or is created by surrounding install machinery. Since the script is copied directly, shebang correctness and Python dependencies are runtime packaging concerns.

## Test Signals

Validate `make install DESTDIR=...` produces executable `sbindir/nfsdclddb` and installs the man page and distributed Python file.

<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/nfsdclddb/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/nfsdclddb/nfsdclddb.py -->
# sources/user-network-fs/nfs-utils/tools/nfsdclddb/nfsdclddb.py

## Purpose

`nfsdclddb.py` inspects and repairs the sqlite database used by `nfsdcld` for NFSv4 client recovery epochs. It can print database summary/client records, repair short recovery table names, and downgrade schema version 4 tables to version 3 by dropping principal hash data.

## Important APIs, Types, and Functions

`CldDb` opens the sqlite database, reads `parameters.version` and the `grace` epoch row, and exposes print, validation, repair, and downgrade methods. `_print_clients` prints ids and, for schema v4, `princhash`. `check_bad_table_names` finds malformed `rec-*` table names; `fix_bad_table_names` renames tables matching current/recovery epochs and drops unknown short tables. `has_princ_data`, `_downgrade_table_v4_to_v3`, and `downgrade_schema_v4_to_v3` implement guarded v4-to-v3 migration. Command handlers add active-daemon warnings.

## Control Flow

`main` builds argparse subcommands, defaults no-argument invocation to `print --summary`, verifies the database path exists, constructs `CldDb`, and dispatches the selected handler. Repair and downgrade commands warn if `nfsdcld` appears in `ps -C`, ask for confirmation, then run exclusive sqlite transactions.

## State and Persistence Behavior

Print mode is read-only. `fix_bad_table_names` mutates sqlite schema names and may drop unknown malformed tables. Downgrade creates replacement epoch tables with only `id`, drops v4 tables, renames replacements, and updates `parameters.version` to `3`, committing or rolling back as one transaction.

## Dependencies and Integration Points

The script depends on Python `sqlite3`, `/var/lib/nfs/nfsdcld/main.sqlite` by default, the `parameters`, `grace`, and `rec-%016x` schema, and the external `nfsdcld` service. It is an offline administrative companion to the NFSv4 server client recovery daemon.

## Risks and Edge Cases

`__init__` assumes version and grace rows exist. `has_princ_data` appears to query the current epoch twice when recovery is present, which can miss principal data in the recovery table. SQL uses formatted table names from trusted database metadata and epoch values; malformed names are partly handled by the repair command. The daemon-active check uses `ps -C`, which is heuristic. If a command is omitted but arguments are not empty, `args.func` may be absent.

## Test Signals

Tests should use temporary sqlite databases for v3 and v4 schemas, current-only and current+recovery epochs, malformed short table names, unknown epoch tables, rollback on injected sqlite errors, principal-data warnings, default summary behavior, and missing-path usage output.

<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/nfsdclddb/nfsdclddb.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/nfsdclnts/Makefile.am -->
# sources/user-network-fs/nfs-utils/tools/nfsdclnts/Makefile.am

## Purpose

This Automake file packages the Python `nfsdclnts` NFSv4 client-state inspection tool and its manual page.

## Important APIs, Types, and Functions

It declares `PYTHON_FILES = nfsdclnts.py`, `man8_MANS = nfsdclnts.man`, distributes both, and installs `nfsdclnts.py` as executable `$(sbindir)/nfsdclnts`.

## Control Flow

The build treats the script as a runtime file; installation copies it with executable permissions. Maintainer cleanup removes `Makefile.in`.

## State and Persistence Behavior

There is no runtime state here. Persistent effects are installed files and permissions.

## Dependencies and Integration Points

It integrates the procfs/YAML inspection script into nfs-utils administrative tooling.

## Risks and Edge Cases

Runtime dependencies such as Python and PyYAML are not encoded in this Automake fragment, so packaging must supply them separately.

## Test Signals

Install tests should verify executable placement, man page installation, and inclusion of the Python source in distribution archives.

<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/nfsdclnts/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/nfsdclnts/nfsdclnts.py -->
# sources/user-network-fs/nfs-utils/tools/nfsdclnts/nfsdclnts.py

## Purpose

`nfsdclnts.py` reads NFS server client state exported under `/proc/fs/nfsd/clients` and prints a tabular view of NFSv4 opens, delegations, locks, and layouts, optionally including client identity details.

## Important APIs, Types, and Functions

`file_to_dict` parses colon-separated `info` files. `getpaths` enumerates each client's `states` file. `opener` YAML-loads a `states` file and appends the matching `info` path. `printer` combines state YAML and client info into formatted rows. `print_cols` renders headers based on requested state type and client fields. `nfsd4_show` owns argparse setup, multiprocessing, signal handling, and output orchestration.

## Control Flow

The CLI accepts a type filter, optional explicit files, hostname/client-info display choices, verbosity, and quiet mode. It chooses explicit `--file` paths or discovers `/proc/fs/nfsd/clients/*/states`, uses a multiprocessing pool to parse YAML in parallel, filters out failed parses, prints headers unless quiet, and prints rows for matching object types.

## State and Persistence Behavior

The script is read-only. State exists only as parsed YAML/list/dict objects in worker and parent processes. The authoritative runtime source is procfs state exported by the kernel NFS server.

## Dependencies and Integration Points

It depends on Python multiprocessing, signals, `PyYAML`, `/proc/fs/nfsd/clients`, and the kernel's `states` YAML-like format and `info` files. It is an admin diagnostic tool for nfsd state rather than a control path.

## Risks and Edge Cases

`verbose` is a global used by helpers. YAML is loaded with `BaseLoader`, so all values are strings, matching display needs but not typed validation. Many broad `except` blocks hide malformed state unless verbose. `getpaths` has indentation irregularities but valid Python in this file. `printer` mutates its `data_list` by popping the info path. Output column width truncates long hostnames but not filenames. Multiprocessing can be expensive for small client sets.

## Test Signals

Fixture tests should cover procfs discovery failure, empty clients, explicit file mode, malformed YAML, missing info keys, all state types, quiet header suppression, hostname truncation, clientinfo columns, and interrupt handling that terminates workers.

<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/nfsdclnts/nfsdclnts.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/nfsrahead/99-nfs.rules -->
# sources/user-network-fs/nfs-utils/tools/nfsrahead/99-nfs.rules

## Purpose

`99-nfs.rules` is the generated udev rule that invokes `nfsrahead` when a backing-device-info (`bdi`) device is added, then writes the program output into `read_ahead_kb`.

## Important APIs, Types, and Functions

The rule matches `SUBSYSTEM=="bdi"` and `ACTION=="add"`, runs `/usr/libexec/nfsrahead %k`, and assigns `ATTR{read_ahead_kb}="%c"` from the program's stdout.

## Control Flow

On bdi add events, udev calls the helper with the kernel device key. If the helper prints a value and exits successfully enough for udev assignment, the bdi readahead value is changed.

## State and Persistence Behavior

The rule itself is installed persistently under the udev rules directory. Runtime state is the kernel bdi `read_ahead_kb` attribute, which is not a config-file persistence layer.

## Dependencies and Integration Points

It depends on udev rule semantics, the installed `/usr/libexec/nfsrahead` path in this generated file, and sysfs bdi attributes. It integrates NFS mount detection with kernel readahead tuning.

## Risks and Edge Cases

The generated path can be wrong if install `libexecdir` differs from `/usr/libexec` without regeneration. Helper latency can block udev event processing, which is why the C helper contains mountinfo wait limits and fast non-NFS rejection.

## Test Signals

Packaging tests should verify the installed rule path matches the installed helper path, and udev integration tests should simulate bdi add events for NFS and non-NFS device numbers.

<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/nfsrahead/99-nfs.rules -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/nfsrahead/99-nfs.rules.in -->
# sources/user-network-fs/nfs-utils/tools/nfsrahead/99-nfs.rules.in

## Purpose

`99-nfs.rules.in` is the install-time template for the generated udev rule that calls `nfsrahead`.

## Important APIs, Types, and Functions

It uses `_libexecdir_` as a substitution token in `PROGRAM="_libexecdir_/nfsrahead %k"` and assigns stdout to `ATTR{read_ahead_kb}="%c"`.

## Control Flow

Automake's rule in `Makefile.am` substitutes `_libexecdir_` with `@libexecdir@` to produce `99-nfs.rules`, which udev later evaluates on bdi add events.

## State and Persistence Behavior

The template has no runtime state. Its content controls the persistent installed udev rule generated during build.

## Dependencies and Integration Points

It depends on the build system substitution rule and udev's `PROGRAM`/`%c` behavior. It integrates the helper with kernel bdi sysfs tuning.

## Risks and Edge Cases

Any mismatch between substitution, configured `libexecdir`, and actual helper installation will break runtime invocation. The template assumes bdi `read_ahead_kb` exists and can be written by udev.

## Test Signals

Tests should check substitution output for configured prefix/libexecdir values and confirm the rule calls the installed helper path.

<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/nfsrahead/99-nfs.rules.in -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/nfsrahead/Makefile.am -->
# sources/user-network-fs/nfs-utils/tools/nfsrahead/Makefile.am

## Purpose

This Automake file builds the `nfsrahead` udev helper, installs its manual page, and generates/installs the udev rule.

## Important APIs, Types, and Functions

It declares `libexec_PROGRAMS = nfsrahead`, builds `main.c`, links with `$(LIBMOUNT_LIBS)` and `../../support/nfs/libnfsconf.la`, installs `nfsrahead.man`, defines `udev_rulesdir = /usr/lib/udev/rules.d/`, and generates `99-nfs.rules` from the `.in` file via `$(SED)`.

## Control Flow

Build compiles the helper and substitutes `_libexecdir_` in the template. Install places the helper in `libexecdir`, the rule in the udev rules directory, and the man page. `clean-local` removes the generated rule.

## State and Persistence Behavior

No runtime state exists in the build file. It controls persistent installed paths for the helper, documentation, and udev rule.

## Dependencies and Integration Points

It integrates libmount-based mount discovery, nfsconf configuration parsing, and udev. It depends on generated `builddefs` and configured `LIBMOUNT_LIBS`.

## Risks and Edge Cases

The hard-coded udev rules directory may not match all distributions. Linker flags use `nfsrahead_LDFLAGS = $(LIBMOUNT_LIBS)` rather than `LDADD` for libmount, which packaging/build environments should verify.

## Test Signals

Build and install tests should verify helper linkage, generated rule substitution, clean removal of generated rules, and correct install directories under `DESTDIR`.

<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/nfsrahead/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/nfsrahead/main.c -->
# sources/user-network-fs/nfs-utils/tools/nfsrahead/main.c

## Purpose

`main.c` implements the `nfsrahead` udev helper. Given a bdi device number, it determines whether the device belongs to an NFS mount and prints the configured readahead value for that NFS kind so udev can write it to `read_ahead_kb`.

## Important APIs, Types, and Functions

`struct device_info` stores the device number string, `dev_t`, mountpoint, and fstype. `fill_device_number` parses `major:minor`. `get_mountinfo` uses libmount to parse mountinfo and find the mount by device number. `get_device_info` fast-rejects non-anonymous-block devices, waits up to `MNT_NM_TIMEOUT` for mountinfo changes through a libmount monitor, and falls back to short sleeps. `conf_get_readahead` reads `[nfsrahead]` config keys for the fstype or default. `main` handles `-d`/`-F`, logging, config initialization, lookup, fstype validation, and stdout output.

## Control Flow

udev invokes the helper with one bdi key. The helper initializes nfsconf and xlog, validates exactly one remaining argument, resolves that device to a mount, skips non-NFS devices, rejects non-`nfs*` filesystems, reads a configured `nfs`, `nfs4`, or default readahead value, prints the integer, frees allocations, and exits with the lookup/validation status.

## State and Persistence Behavior

The helper does not persist data. It reads `NFS_CONFFILE`, `/proc/self/mountinfo`, and mount notifications, then emits a value for udev to persist into a kernel sysfs attribute for the lifetime of that bdi.

## Dependencies and Integration Points

It depends on libmount table/monitor APIs, sysmacros `makedev`, nfs-utils xlog and conffile support, udev calling conventions, and anonymous block-device numbering for network filesystems.

## Risks and Edge Cases

`get_mountinfo` frees `device_number` on exit even though `free_device_info` later tolerates NULL. Major-number fast rejection assumes NFS bdi devices always begin with `0:`. Waiting in udev is bounded but still can delay event handling. `strtol` parsing does not validate trailing junk. Any fstype beginning with `nfs` passes, intentionally covering `nfs4` but also relying on prefix semantics.

## Test Signals

Tests should cover valid NFS and NFSv4 mountinfo fixtures, non-`0:` fast rejection, malformed device strings, delayed mountinfo appearance, missing fstype, non-NFS fstype rejection, config-specific and default readahead values, and `-d`/`-F` logging paths.

<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/nfsrahead/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/nlmtest/Makefile.am -->
# sources/user-network-fs/nfs-utils/tools/nlmtest/Makefile.am

## Purpose

This Automake fragment distributes the legacy `nlmtest` sources but does not build an installed program.

## Important APIs, Types, and Functions

`EXTRA_DIST` includes `README`, `host.h`, `nlm_prot.x`, and `nlmtest.c`.

## Control Flow

Automake includes these files in release tarballs. No compile or install target is declared here.

## State and Persistence Behavior

No runtime state exists. The persistent effect is source distribution only.

## Dependencies and Integration Points

It keeps a manual NLM test harness and its RPC protocol input available to developers, separate from normal tool builds.

## Risks and Edge Cases

Because the program is not built by default and `nlmtest.c` contains a compile-time `#error`, it can silently rot unless a developer explicitly repairs it.

## Test Signals

Distribution tests should confirm all four files are present. Any attempt to re-enable the tool should add an explicit build target and compile test.

<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/nlmtest/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/nlmtest/host.h -->
# sources/user-network-fs/nfs-utils/tools/nlmtest/host.h

## Purpose

`host.h` provides local, edit-before-use defaults for the legacy `nlmtest` lock-manager test program.

## Important APIs, Types, and Functions

It defines `NLMTEST_HOST`, `NLMTEST_DIR`, `NLMTEST_FILE`, and `NLMTEST_VERSION`, guarded by `NLMTEST_HOST_H`.

## Control Flow

There is no executable control flow. `nlmtest.c` includes this header to choose the lockd host, NFS mount path, default file, and file-handle version constant.

## State and Persistence Behavior

The values are compile-time constants. Changing them requires editing/rebuilding rather than runtime persistence.

## Dependencies and Integration Points

It integrates the old test harness with a developer's specific NFS test environment. The defaults are placeholders, not portable deployment settings.

## Risks and Edge Cases

The hard-coded host `crutch`, relative mount directory, and version value are unlikely to match modern systems. The comments acknowledge the program cannot discover all file-handle data itself.

## Test Signals

If resurrecting the harness, tests should verify command-line overrides supersede these defaults and that generated file handles match the configured NFS export.

<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/nlmtest/host.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/nlmtest/nlmtest.c -->
# sources/user-network-fs/nfs-utils/tools/nlmtest/nlmtest.c

## Purpose

`nlmtest.c` is a legacy manual test client for the Network Lock Manager protocol. It creates an RPC client to lockd, constructs NLM test/lock/unlock requests, and reports lock status and conflicts.

## Important APIs, Types, and Functions

`main` parses `-b`, `-f`, `-h`, `-l`, `-o`, `-p`, `-u`, and `-x`, creates an `NLM_PROG`/`NLM_VERS` UDP client, prepares `nlm_testargs`, `nlm_lockargs`, or `nlm_unlockargs`, and calls generated RPC stubs `nlm_test_1`, `nlm_lock_1`, and `nlm_unlock_1`. `makelock`, `makeowner`, and `makefileh` build protocol structures. `nlm_stat_name` and `holderstr` format responses.

## Control Flow

The tool first sends `NLM_TEST` for the requested range. If the test is denied it prints holder details. Unless the test failed and the user did not request blocking or unlock behavior, it then sends either `NLM_UNLOCK` or `NLM_LOCK` and prints the result.

## State and Persistence Behavior

The program does not persist local state. It can create or remove remote lock state in lockd through NLM calls. Cookie, owner handle, PID, and file handle content are process-local request fields.

## Dependencies and Integration Points

It depends on generated `nlm_prot.h` stubs, ONC RPC client APIs, `<nfs/nfs.h>`, `host.h` defaults, and an NFS/lockd test server. It is distributed but not built in the normal tree.

## Risks and Edge Cases

`makefileh` contains `#error this needs updating if it is still wanted`, so the file intentionally does not compile as-is. File-handle construction is stale and partly hard-coded. The `-f` filename option is parsed but not used by `makefileh`. Integer formatting uses `%d` for offsets/lengths that may be wider than int. UDP and NLMv1-only behavior limit modern coverage.

## Test Signals

Before any runtime testing, compilation must be restored. Then tests should cover granted, denied, unlock, blocking flags, exclusive/shared locks, owner encoding, file-handle generation, and server unavailability paths.

<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/nlmtest/nlmtest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/rpcctl/Makefile.am -->
# sources/user-network-fs/nfs-utils/tools/rpcctl/Makefile.am

## Purpose

This Automake file packages the Python `rpcctl` sysfs administration tool and its manual page.

## Important APIs, Types, and Functions

It declares `PYTHON_FILES = rpcctl.py`, `man8_MANS = rpcctl.man`, distributes both, and installs the script executable as `$(sbindir)/rpcctl`.

## Control Flow

The build preserves the Python source as a script and install copies it with mode `755`.

## State and Persistence Behavior

No build-time runtime state exists. Installed script and man page are persistent artifacts.

## Dependencies and Integration Points

It integrates the sunrpc sysfs control CLI into nfs-utils packaging.

## Risks and Edge Cases

Runtime availability depends on Python 3 and kernel sunrpc sysfs support, neither of which is represented directly in this file.

## Test Signals

Install tests should verify executable placement, permission mode, man page installation, and distribution archive contents.

<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/rpcctl/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/rpcctl/rpcctl.py -->
# sources/user-network-fs/nfs-utils/tools/rpcctl/rpcctl.py

## Purpose

`rpcctl.py` is a sysfs inspection/control utility for Linux SunRPC clients, xprt switches, and individual transports. It shows connection state and can alter transport state, destination addresses, add transports, or remove non-main transports.

## Important APIs, Types, and Functions

Top-level initialization locates the sysfs mount from `/proc/mounts` and verifies `kernel/sunrpc`. Helpers `read_sysfs_file`, `write_sysfs_file`, and `read_info_file` handle sysfs data. `Xprt` models one transport and supports display, `set_dstaddr`, `set_state`, `remove`, lookup, and argparse command registration. `XprtSwitch` models an xprt switch, supports display, `add_xprt`, and dstaddr changes across contained xprts. `RpcClient` models an RPC client and links to its switch. `show_small_help` handles no-command invocation.

## Control Flow

Import-time code fails early if sysfs or sunrpc sysfs is unavailable. The parser adds `client`, `switch`, and `xprt` command families. Lookups traverse `sunrpc/rpc-clients` and `sunrpc/xprt-switches`. Mutating commands write sysfs control files and then refresh or print affected objects.

## State and Persistence Behavior

The script persists no files. Mutations write kernel sysfs attributes such as `xprt_state`, `dstaddr`, and `add_xprt`, changing live RPC transport state. Object instances cache some info from construction and refresh state selectively.

## Dependencies and Integration Points

It depends on Python 3, pathlib, argparse, DNS resolution via `socket.gethostbyname`, `/proc/mounts`, and the kernel SunRPC sysfs ABI. It is tightly integrated with RPC client transport management and NFS multipath/session diagnostics.

## Risks and Edge Cases

Import-time sysfs validation makes unit testing harder unless `/proc/mounts` is mocked. Path parsing assumes xprt directory names contain the transport type at `split("-")[2]`. Some lookup paths construct objects without explicit existence checks and can fail later. Mutating main xprts is blocked in code, but races with kernel removal are only partly handled by `__str__`. `except Exception` at top-level prints only the message.

## Test Signals

Tests should build fake sysfs trees for clients, switches, and xprts; cover missing sysfs/sunrpc; verify show output, missing files as `(enoent)`/custom labels, main-xprt mutation rejection, xprt removal sequence, dstaddr resolution, add-xprt writes, and kernel removal races.

<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/rpcctl/rpcctl.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/rpcdebug/Makefile.am -->
# sources/user-network-fs/nfs-utils/tools/rpcdebug/Makefile.am

## Purpose

This Automake file builds and installs the `rpcdebug` debug-flag utility and its manual page.

## Important APIs, Types, and Functions

It declares `man8_MANS = rpcdebug.man`, `sbin_PROGRAMS = rpcdebug`, and `rpcdebug_SOURCES = rpcdebug.c`.

## Control Flow

Automake compiles `rpcdebug.c`, installs the binary under `sbindir`, installs the man page, and removes `Makefile.in` during maintainer cleanup.

## State and Persistence Behavior

No runtime state is stored here. Install state consists of the executable and manual page.

## Dependencies and Integration Points

It integrates the proc-sysctl debug flag editor with the nfs-utils build.

## Risks and Edge Cases

The source depends on kernel/user headers exposing NFS debug flag constants; build portability depends on those headers matching the target environment.

## Test Signals

Build tests should compile `rpcdebug` and install its manual page. Runtime tests need a controlled `/proc/sys/sunrpc` environment or mocks.

<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/rpcdebug/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/rpcdebug/rpcdebug.c -->
# sources/user-network-fs/nfs-utils/tools/rpcdebug/rpcdebug.c

## Purpose

`rpcdebug.c` implements a command-line tool for viewing, setting, and clearing Linux RPC/NFS/NFSD/NLM debug flag bitmasks exposed under `/proc/sys/sunrpc`.

## Important APIs, Types, and Functions

The `flagmap` table maps module/flag names to constants from `<nfs/debug.h>`. `find_flag` resolves names and detects ambiguous cross-module flags when no module is specified. `get_flags` and `set_flags` read/write `/proc/sys/sunrpc/<module>_debug`. `print_flags` formats active or all valid flags. `strtolower` lowercases names into a static buffer. `usage` prints command help. `main` parses `-c`, `-s`, `-m`, `-v`, and program-name aliases `nfsdebug`/`nfsddebug`.

## Control Flow

The tool determines a default module from argv[0] aliases, validates at most one of clear/set modes, resolves any supplied flags, defaults to showing all current flags when no flags are specified, reads the current bitmask, optionally writes a set or cleared bitmask, then prints resulting active flags and optionally the valid flag list.

## State and Persistence Behavior

It persists no user files. Writing debug masks changes live kernel sysctl state under `/proc/sys/sunrpc`, which remains until changed again or reset by kernel/module lifecycle.

## Dependencies and Integration Points

It depends on Linux proc sysctl files and NFS debug constants. It integrates with kernel RPC/NFS debugging for administrators and can be symlinked/renamed to default specific modules.

## Risks and Edge Cases

Writes require privileges and procfs support. `strtolower` uses a 64-byte static buffer and `strcpy`, so unexpectedly long names would overflow, though table/module names are controlled. `cdename` is allocated but never freed. The value is written with `%d` despite unsigned semantics. Flag aliases with duplicate values are suppressed unless `show_all`.

## Test Signals

Tests should mock proc sysctl files, verify module validation, alias behavior, ambiguous flag detection, set/clear masks, verbose valid flag output, unknown names, short writes, and permission/read errors.

<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/rpcdebug/rpcdebug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/rpcgen/Makefile.am -->
# sources/user-network-fs/nfs-utils/tools/rpcgen/Makefile.am

## Purpose

This Automake file builds the bundled `rpcgen` RPC protocol compiler and installs its manual page.

## Important APIs, Types, and Functions

It declares `bin_PROGRAMS = rpcgen`, `man_MANS = rpcgen.1`, `noinst_HEADERS = proto.h rpc_parse.h rpc_scan.h rpc_util.h`, and compiles all `rpc_*.c` generator, parser, scanner, and utility sources. It links with `$(LIBINTL)`.

## Control Flow

Automake compiles the scanner/parser, main driver, output generators, and shared utilities into one `rpcgen` binary. `CLEANFILES = *~` removes editor backups.

## State and Persistence Behavior

No runtime state exists in the build file. It controls installed compiler/manual artifacts.

## Dependencies and Integration Points

It integrates the ONC RPC code generator with nfs-utils and depends on intl support when configured.

## Risks and Edge Cases

Generated build rules must compile older C code with modern compiler warnings and headers. `EXTRA_DIST=${MANS}` appears to use `MANS`, while the file declares `man_MANS`; build tooling should verify distribution contents.

## Test Signals

Build tests should compile `rpcgen`, install the binary and man page, and run smoke generation for a small `.x` file covering header, XDR, client, server, and table outputs.

<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/rpcgen/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/rpcgen/proto.h -->
# sources/user-network-fs/nfs-utils/tools/rpcgen/proto.h

## Purpose

`proto.h` centralizes cross-translation-unit prototypes for the bundled `rpcgen` implementation and supplies build-host compatibility shims when compiling for glibc build tooling.

## Important APIs, Types, and Functions

It declares output generator entry points (`write_stubs`, `emit`, `print_datadef`, `write_sample_svc`, `write_tables`, service helpers), parser/scanner utility functions (`get_definition`, `reinitialize`, `error`, `crash`, `tabify`, `make_argname`, `add_type`), and shared declaration printers such as `printarglist`, `pdeclaration`, and `pprocdef`.

## Control Flow

The header has no runtime flow; it permits the modular `rpc_*.c` files to call each other's generator helpers after including AST definitions.

## State and Persistence Behavior

It declares no storage directly, but exposes functions that operate on global parser/output state from `rpc_util.c` and option globals from `rpc_main.c`.

## Dependencies and Integration Points

It depends on types from `rpc_parse.h` and standard `FILE`. It is included late by generator files and contains an `IS_IN_build` block disabling gettext macros for cross-rpcgen builds.

## Risks and Edge Cases

Some prototypes overlap with `rpc_util.h`/`rpc_output.h`, and signatures differ in const-qualification in places, so compiler strictness matters. Because it is the common internal interface, mismatched declarations can affect multiple generator modes.

## Test Signals

Compile with strict warnings where possible, and exercise every output mode to ensure declared functions match definitions across C and K&R compatibility branches.

<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/rpcgen/proto.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/rpcgen/rpc_clntout.c -->
# sources/user-network-fs/nfs-utils/tools/rpcgen/rpc_clntout.c

## Purpose

`rpc_clntout.c` emits client-side RPC stub functions for `rpcgen` program definitions.

## Important APIs, Types, and Functions

`write_stubs` prints the default timeout and iterates global `defined` entries for `DEF_PROGRAM`. `write_program` emits one client function per procedure version. `printarglist` is shared with sample/server emitters and formats K&R, ANSI C, oldstyle by-reference, newstyle by-value, and MT-safe argument lists. `printbody` emits `clnt_call` invocations, static result storage for non-MT mode, multi-argument packing structs, and result/error returns. `ampr` decides when vector typedefs should not be addressed.

## Control Flow

After parsing, the main driver calls `write_stubs` for client output. For each procedure, the emitter chooses return type and signature based on `mtflag`, `newstyle`, and `Cflag`, then emits a body that marshals arguments with the correct `xdr_*`, calls `clnt_call`, and returns either a pointer to static result storage or an `enum clnt_stat`.

## State and Persistence Behavior

The file emits source text to global `fout` and reads global AST/options. Generated non-MT stubs contain static result storage, making generated client functions not reentrant by default. The generator itself persists only output files managed by `rpc_main.c`.

## Dependencies and Integration Points

It depends on `rpc_parse.h`, `rpc_util.h`, and `proto.h`, and integrates with `rpc_main.c` client output and header declarations generated by `rpc_hout.c`.

## Risks and Edge Cases

Generated non-MT code uses static result buffers. Newstyle multi-argument support relies on argument structs emitted elsewhere. Void result handling uses `char` placeholders. Option combinations such as K&R plus MT are maintained for compatibility and need regression coverage.

## Test Signals

Generate stubs for void, single, multi-argument, string, vector typedef, and MT-safe procedures; compile generated C in ANSI and K&R modes if supported; verify `clnt_call` argument/result XDR functions and return behavior.

<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/rpcgen/rpc_clntout.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/rpcgen/rpc_cout.c -->
# sources/user-network-fs/nfs-utils/tools/rpcgen/rpc_cout.c

## Purpose

`rpc_cout.c` emits XDR encode/decode/free functions for data definitions and generated multi-argument program structs.

## Important APIs, Types, and Functions

`emit` dispatches definitions to `emit_union`, `emit_enum`, `emit_struct`, `emit_typedef`, or `emit_program`. `print_generic_header`, `print_header`, and `print_trailer` frame `bool_t xdr_*` functions. `print_ifstat` chooses `xdr_pointer`, `xdr_vector`, `xdr_array`, `xdr_bytes`, `xdr_string`, or direct `xdr_type` calls based on `relation`. `emit_struct`, `inline_struct`, `emit_inline`, and `emit_single_in_line` generate optional `XDR_INLINE` fast paths for basic types. `undefined` and `findtype` help print prefixed struct/enum sizes.

## Control Flow

For each parsed definition, constants are skipped, program definitions emit XDR routines only for newstyle multi-argument structs, and type definitions avoid self-alias duplicate routines. Each emitted function serializes each member or union arm, returning `FALSE` on the first failed XDR helper and `TRUE` at the end.

## State and Persistence Behavior

The generator writes to global `fout` and reads `defined`, `Cflag`, `inlineflag`, and the basic type list initialized by `c_initialize`. Generated code contains no persistence beyond marshaling caller-provided data.

## Dependencies and Integration Points

It relies on AST structures from `rpc_parse.h`, type helpers in `rpc_util.c`, and generated headers from `rpc_hout.c`. Output compiles against ONC/TIRPC XDR APIs and IXDR macros.

## Risks and Edge Cases

Manual string allocation and fixed buffers are common. Inline generation is complex and sensitive to basic type size metadata, vector lengths, and XDR operation modes. `print_ifstat` has separate object naming paths for arrays and vectors that can be fragile for unusual typedef chains. Generated code quality depends on valid parser restrictions.

## Test Signals

Generate and compile XDR code for structs with basic runs, arrays, vectors, strings, opaque data, pointers, unions with continued cases and defaults, typedef chains, self typedefs, and inline thresholds including `-i 0`.

<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/rpcgen/rpc_cout.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/rpcgen/rpc_hout.c -->
# sources/user-network-fs/nfs-utils/tools/rpcgen/rpc_hout.c

## Purpose

`rpc_hout.c` emits C header content for RPCL definitions: constants, structs, unions, enums, typedefs, program/version/procedure macros, client/server prototypes, argument structs, table declarations, free-result prototypes, and XDR prototypes.

## Important APIs, Types, and Functions

`print_datadef` emits non-program data definitions and records XDR declarations via `storexdrfuncdecl`. `print_funcdef` emits program declarations. `pstructdef`, `puniondef`, `penumdef`, `ptypedef`, and `pdeclaration` render C type syntax. `pprogramdef`, `pprocdef`, `pargdef`, and `parglist` render RPC program macros and prototypes. `print_xdr_func_def` emits ANSI or K&R XDR prototypes. `undefined2` controls whether to print struct/enum prefixes before types are defined.

## Control Flow

Header output first prints data definitions as the parser produces them, storing XDR function declarations. Then the main driver iterates the completed `defined` list to print program function declarations. Finally it prints all stored XDR declarations and optional dispatch table struct declarations.

## State and Persistence Behavior

The file appends `xdrfunc` nodes to global `xdrfunc_head`/`xdrfunc_tail` and writes to global `fout`. Generated headers persist type and function declarations for generated and user-written RPC code.

## Dependencies and Integration Points

It depends on parser AST definitions, type helpers from `rpc_util.c`, option flags (`newstyle`, `Cflag`, `CCflag`, `tblflag`, `mtflag`), and is coordinated by `rpc_main.c` header output.

## Risks and Edge Cases

Forward/prefix handling is order-sensitive. `storexdrfuncdecl` stores the name pointer directly rather than copying. Some generated prototypes support legacy K&R branches, increasing compatibility complexity. `define_printed` aborts if procedure ordering assumptions are violated internally.

## Test Signals

Generate headers for enums with implicit/explicit values, unions, typedef arrays/pointers/vectors, recursive-ish struct tags, multiple program versions, duplicate procedure names across versions, `-N`, `-M`, `-T`, `-k`, and C++ guard modes.

<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/rpcgen/rpc_hout.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/rpcgen/rpc_main.c -->
# sources/user-network-fs/nfs-utils/tools/rpcgen/rpc_main.c

## Purpose

`rpc_main.c` is the top-level driver for the bundled `rpcgen` compiler. It parses command-line options, runs the C preprocessor, coordinates parsing, selects output modes, opens/closes generated files, and manages cleanup on fatal errors.

## Important APIs, Types, and Functions

`struct commandline` records selected output mode and paths. `main` dispatches to `c_output`, `h_output`, `l_output`, `s_output`, `t_output`, `svc_output`, `clnt_output`, or `mkfile_output`. `open_input` forks/execs `cpp` with `-C` and mode defines; `close_input` checks preprocessor status. `open_output`, `close_output`, `record_open`, and `checkfiles` protect output files. `parseargs` owns option validation and global flags. `do_registers` emits service registrations. `generate_guard`, `extendfile`, `mkfile_output`, and `c_initialize` provide support.

## Control Flow

The driver parses options, checks input/output conflicts, and either generates one requested artifact or the default set of XDR, header, client, server, optional table, sample, and Makefile outputs. Between default outputs it calls `reinitialize` because preprocessing/parsing is repeated per artifact. Each output mode opens preprocessed input, emits a warning banner and includes, parses definitions into global `defined`, calls the relevant emitter, and closes input/output.

## State and Persistence Behavior

Global option flags (`inetdflag`, `pmflag`, `newstyle`, `tirpcflag`, `mtflag`, etc.), output tracking arrays, preprocessor process id, and parser globals are process state. Persistent effects are generated output files; `crash` unlinks files recorded by `record_open` on fatal errors.

## Dependencies and Integration Points

It depends on POSIX process/file APIs, a C preprocessor at `/lib/cpp` or `cpp`, gettext/nls, parser/scanner modules, and all output modules. Generated code targets ONC RPC/TIRPC APIs depending on options.

## Risks and Edge Cases

`checkfiles` refuses existing output files, including sample and Makefile outputs, with an overwrite warning then crash. Argument parsing uses a fixed `arglist` length for cpp defines. Default TIRPC/inetd interactions are subtle: `pmflag` is derived from `tirpcflag` and `inetdflag`. Some output modes may unlink generated files when no applicable definitions are found. `parseargs` restricts `-s` to `udp`/`tcp` early even though later TIRPC valid nettypes are broader for other paths.

## Test Signals

Run smoke tests for every generation flag, default generation, `-a`, `-N`, `-M`, `-T`, `-I`, `-K`, `-5`, `-b`, `-Y`, `-D`, stdin/stdout modes, existing-output failures, missing cpp, cpp failures, and cleanup of partial outputs.

<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/rpcgen/rpc_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/rpcgen/rpc_output.h -->
# sources/user-network-fs/nfs-utils/tools/rpcgen/rpc_output.h

## Purpose

`rpc_output.h` is a small declaration header for selected rpcgen output helper functions.

## Important APIs, Types, and Functions

It declares `write_msg_out`, `nullproc`, `printarglist`, and `pdeclaration` behind include guard `RPCGEN_NEW_OUTPUT_H`.

## Control Flow

There is no runtime flow. Translation units can include it to call output helpers shared between client, server, header, and service generation.

## State and Persistence Behavior

No state is declared here. The functions operate on global output/parser state defined elsewhere.

## Dependencies and Integration Points

It depends on `proc_list` and `declaration` types being visible before inclusion. In this source tree, `proto.h` provides a broader and more actively used internal prototype set.

## Risks and Edge Cases

The signatures here are less const-correct/differently typed than the prototypes in `proto.h`, so including both under strict C modes could expose conflicts. Its limited use suggests it may be legacy residue.

## Test Signals

Compile all rpcgen translation units with warnings enabled and check for prototype conflicts or unused-header drift.

<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/rpcgen/rpc_output.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/rpcgen/rpc_parse.c -->
# sources/user-network-fs/nfs-utils/tools/rpcgen/rpc_parse.c

## Purpose

`rpc_parse.c` implements the hand-written parser for RPCL input, converting scanner tokens into `definition` AST nodes for constants, structs, unions, enums, typedefs, and RPC programs.

## Important APIs, Types, and Functions

`get_definition` is the parser entry point. `def_struct`, `def_union`, `def_enum`, `def_const`, `def_typedef`, and `def_program` parse each top-level construct. `get_declaration`, `get_prog_declaration`, `get_type`, and `unsigned_dec` parse type/declarator forms. `check_type_name` rejects names that would conflict with XDR helpers. Parsed nodes are appended to global `defined` through `isdefined`.

## Control Flow

The parser reads one top-level keyword, dispatches to the matching parser, consumes the trailing semicolon, records the definition, and returns it. Program parsing handles versions, procedures, result types, positional or optional argument names, newstyle multi-argument restrictions, generated argument struct names, procedure numbers, version numbers, and program numbers.

## State and Persistence Behavior

The parser allocates AST nodes and strings that live for the process and are stored in global `defined`. No on-disk state is changed directly; output modules later consume the AST.

## Dependencies and Integration Points

It depends on `rpc_scan.c` token APIs and `rpc_util.c` list/error helpers. It integrates with all output generators through the shared AST types in `rpc_parse.h`.

## Risks and Edge Cases

The parser uses manual allocation and little recovery; `error` exits. `def_const` accepts identifiers or string constants but not numeric token kinds beyond scanner representation as identifiers. Program arguments prohibit opaque and pointer-to-string forms, and arrays as procedure args require typedef except strings. Fixed buffers are used for generated argument names in `get_prog_declaration`.

## Test Signals

Parser tests should cover every grammar construct, invalid reserved names, void rules, multiple arguments with and without `-N`, arrays/vectors/pointers, unsigned numeric types, unions with default and continued cases, malformed punctuation, and generated argument names.

<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/rpcgen/rpc_parse.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/rpcgen/rpc_parse.h -->
# sources/user-network-fs/nfs-utils/tools/rpcgen/rpc_parse.h

## Purpose

`rpc_parse.h` defines the AST and core semantic enums used by the rpcgen scanner, parser, and output generators.

## Important APIs, Types, and Functions

It defines `defkind`, `relation`, `typedef_def`, `enumval_list`, `enum_def`, `declaration`, `decl_list`, `struct_def`, `case_list`, `union_def`, `arg_list`, `proc_list`, `version_list`, `program_def`, `definition`, and `bas_type`. It declares `definition *get_definition(void)`.

## Control Flow

The header has no executable flow. It establishes the in-memory schema that `rpc_parse.c` fills and output modules traverse.

## State and Persistence Behavior

AST objects are heap-allocated by the parser and stored in global lists declared in `rpc_util.h`. The structures represent source definitions only during a single rpcgen process.

## Dependencies and Integration Points

Every rpcgen C file depends on these types. `relation` drives output choices for alias, pointer, fixed vector, and variable array forms.

## Risks and Edge Cases

Many fields are raw `const char *` pointers to scanner-allocated strings or static token names, with no ownership model. Program argument declarations reuse struct declaration lists, so output code must honor `arg_num` and `newstyle` semantics.

## Test Signals

Compile coverage and parser/output integration tests should verify all AST variants are populated and consumed consistently, especially union defaults, multi-argument programs, and typedef relation chains.

<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/rpcgen/rpc_parse.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/rpcgen/rpc_sample.c -->
# sources/user-network-fs/nfs-utils/tools/rpcgen/rpc_sample.c

## Purpose

`rpc_sample.c` emits optional sample client and server implementation templates for parsed RPC programs.

## Important APIs, Types, and Functions

`write_sample_svc` emits server templates for `DEF_PROGRAM` definitions. `write_sample_clnt` emits sample client functions per version and returns a count. `write_sample_client` declares arguments/results, creates a client handle, calls generated stubs, and reports failures. `write_sample_server` emits placeholder service routines and MT free-result helpers. `add_sample_msg` prints the sample-code banner. `write_sample_clnt_main` emits a simple `main` that calls all generated sample clients. `return_type` wraps shared `ptype`.

## Control Flow

Sample output modes parse definitions, then for each program version emit either client demo functions or server skeleton functions. Client sample generation also emits a main function when at least one program exists.

## State and Persistence Behavior

The generator writes template C source to `fout` and reads global AST/options. Generated sample programs contain placeholder local variables and user-fill sections; they do not persist runtime state by themselves.

## Dependencies and Integration Points

It depends on `printarglist`, `pvname`, `pvname_svc`, `ptype`, and flags such as `Cflag`, `newstyle`, `mtflag`, and `tirpcflag`. It is invoked by `rpc_main.c` for `-Sc`, `-Ss`, and `-a`.

## Risks and Edge Cases

Generated samples are scaffolding, not complete applications. Some declarations are uninitialized by design. Transport choice differs for TIRPC (`netpath`) versus legacy (`udp`). The string comparison `strcmp(l->decl.type, "string") == 1` looks suspicious and likely intended nonzero comparison, though output impact is limited formatting.

## Test Signals

Generate sample clients/servers for void, string, multi-argument, MT-safe, and multiple-version programs; compile the templates enough to catch syntax errors; inspect placeholder result and free-result code.

<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/rpcgen/rpc_sample.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/rpcgen/rpc_scan.c -->
# sources/user-network-fs/nfs-utils/tools/rpcgen/rpc_scan.c

## Purpose

`rpc_scan.c` is rpcgen's lexical scanner. It reads preprocessed RPCL input, skips whitespace/comments, preserves `%` directives into output, tracks `#line` information, and returns tokens to the parser.

## Important APIs, Types, and Functions

Public scanner functions are `scan`, `scan2`, `scan3`, `scan_num`, `peek`, `peekscan`, and `get_token`. Internal helpers include `unget_token`, `findstrconst`, `findchrconst`, `findconst`, `findkind`, `cppline`, `directive`, `printdirective`, and `docppline`. The `symbols` table maps reserved words to token kinds.

## Control Flow

`get_token` first returns a pushed token if present, otherwise reads lines from global `fin`, updates `linenum`, processes cpp line markers and `%` output directives, skips whitespace and C block comments, then recognizes punctuation, string/char constants, numeric constants, identifiers, or reserved keywords. Parser wrappers enforce expected tokens and delegate error reporting.

## State and Persistence Behavior

Scanner state is global: `curline`, `where`, `linenum`, `infilename`, and one-token pushback state. It writes passthrough directives to `fout`. It persists no files directly.

## Dependencies and Integration Points

It depends on preprocessed input from `rpc_main.c`, error helpers from `rpc_util.c`, gettext macros, and token/AST headers. It feeds `rpc_parse.c`.

## Risks and Edge Cases

Comment state is local to one `get_token` call and still handles multiline comments through the internal read loop, but scanner recovery is minimal. String and char constant parsing does not process escapes deeply and char constants require exactly three bytes including quotes. Numeric constants are returned as identifiers. Illegal characters abort generation and cleanup outputs.

## Test Signals

Scanner tests should cover comments across lines, `%` directives, cpp line markers, identifiers adjacent to keywords, hex/decimal constants, negative constants, strings, invalid/unterminated strings, char constants, pushback, and parser expectation errors.

<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/rpcgen/rpc_scan.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/rpcgen/rpc_scan.h -->
# sources/user-network-fs/nfs-utils/tools/rpcgen/rpc_scan.h

## Purpose

`rpc_scan.h` defines rpcgen token kinds, token representation, and scanner API declarations.

## Important APIs, Types, and Functions

`enum tok_kind` enumerates identifiers, constants, punctuation, RPCL keywords, primitive types, program/version keywords, and EOF. `struct token` carries a kind and string pointer. The header declares scanner functions and noreturn expectation-error helpers.

## Control Flow

No executable flow exists. Parser code uses these declarations to consume and validate tokens.

## State and Persistence Behavior

No state is declared here. Scanner globals live in `rpc_util.c` and scanner-local statics live in `rpc_scan.c`.

## Dependencies and Integration Points

It is shared by `rpc_scan.c`, `rpc_parse.c`, and `rpc_util.c` for token names and expected-token diagnostics.

## Risks and Edge Cases

The token set reflects the supported RPCL grammar. Adding syntax requires coordinated updates to this enum, scanner keyword tables, parser logic, and diagnostic string tables.

## Test Signals

Compile tests and scanner/parser fixtures should verify each token kind is reachable and diagnostics render expected token names.

<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/rpcgen/rpc_scan.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/rpcgen/rpc_svcout.c -->
# sources/user-network-fs/nfs-utils/tools/rpcgen/rpc_svcout.c

## Purpose

`rpc_svcout.c` emits server-side RPC dispatch code, registration code, inetd/port-monitor support, timeout helpers, logging helpers, and MT-safe result cleanup scaffolding.

## Important APIs, Types, and Functions

`write_most` emits globals, auxiliaries, dispatchers, and `main` setup. `write_programs`, `write_real_program`, and `write_program` emit newstyle wrappers and per-version dispatch functions. `write_inetd_register`, `write_netid_register`, and `write_nettype_register` emit transport registration code. `write_rest` emits `svc_run`. `write_svc_aux`, `write_msg_out`, and `write_timeout_func` emit support functions. Helpers include `p_xdrfunc`, `internal_proctype`, `printerr`, `printif`, `nullproc`, `write_inetmost`, `write_pm_most`, `write_rpc_svc_fg`, and `open_log_file`.

## Control Flow

Service output parses all definitions, emits includes in `rpc_main.c`, then this file writes dispatch helpers and optionally a full `main`. Generated dispatchers switch on `rq_proc`, select argument/result XDR functions and local routines, decode args, invoke the local procedure, send replies, free args/results, and return or exit according to timer/inetd flags.

## State and Persistence Behavior

The generator writes C source to `fout` and reads global AST/options. Generated servers maintain runtime service state such as `_rpcpmstart`, `_rpcfdtype`, timeout state, and optional mutex-protected `_rpcsvcstate`; they register with portmapper/rpcb and run until `svc_run` exits or timeout logic closes them.

## Dependencies and Integration Points

It depends on ONC RPC/TIRPC server APIs, syslog, netconfig, inetd/port-monitor conventions, and shared rpcgen AST/utilities. It is coordinated by `rpc_main.c` service output and header/client emitters.

## Risks and Edge Cases

The code supports many historical modes, making option interactions high risk. Generated daemonization closes file descriptors and redirects to `/dev/console`. Timer state differs for MT and non-MT. Newstyle wrappers unpack arguments by value, so generated prototypes must match header output. Transport registration paths differ between legacy inetd and TIRPC nettype/netid modes.

## Test Signals

Generate/compile service code for legacy UDP/TCP, TIRPC netpath, explicit netid, inetd `-I`, timeout `-K`, logging `-L`, MT `-M`, newstyle `-N`, no-main `-m`, and procedures with and without explicit NULLPROC.

<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/rpcgen/rpc_svcout.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/rpcgen/rpc_tblout.c -->
# sources/user-network-fs/nfs-utils/tools/rpcgen/rpc_tblout.c

## Purpose

`rpc_tblout.c` emits optional `struct rpcgen_table` dispatch tables for RPC programs.

## Important APIs, Types, and Functions

`write_tables` iterates global definitions and calls `write_table` for each program. `write_table` emits one table per version, inserts a NULLPROC entry if needed, emits action pointers and argument/result XDR/size metadata, and warns when procedure numbers are out of order. `printit` formats one XDR function/size pair with tab alignment.

## Control Flow

After parsing, table output emits all program tables. For each version, expected procedure numbers start at 0 if a NULLPROC exists or 1 with an inserted null entry otherwise. Each procedure contributes a routine pointer, argument metadata, and result metadata.

## State and Persistence Behavior

The generator writes C initializer text to `fout`. It sets global `nonfatalerrors` if table order is wrong, causing rpcgen to exit nonzero while still producing output.

## Dependencies and Integration Points

It depends on `nullproc` from service output, `ptype`, `stringfix`, `locase`, AST definitions, and header support for `struct rpcgen_table` when `tblflag` is enabled.

## Risks and Edge Cases

Dispatch tables are incompatible with newstyle mode, enforced in `parseargs`. Procedure numbers are parsed with `atoi`, so symbolic procedure numbers may not sort as intended. Tab alignment assumes bounded type name lengths.

## Test Signals

Generate tables for versions with explicit and missing NULLPROC, ordered and out-of-order numeric procedures, void and non-void args/results, and verify `nonfatalerrors` behavior.

<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/rpcgen/rpc_tblout.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/rpcgen/rpc_util.c -->
# sources/user-network-fs/nfs-utils/tools/rpcgen/rpc_util.c

## Purpose

`rpc_util.c` provides shared global state and utility functions for rpcgen parsing, type handling, output formatting, diagnostics, cleanup, and basic type metadata.

## Important APIs, Types, and Functions

It defines scanner globals (`curline`, `where`, `linenum`, `infilename`), IO globals (`fin`, `fout`), output tracking (`outfiles`, `nfiles`), and the global AST list `defined`. `reinitialize`, `findval`, and `storeval` manage parser state. `fixtype`, `stringfix`, `ptype`, and `isvectordef` guide C type output. `locase`, `pvname`, and `pvname_svc` form generated symbol names. `error`, `crash`, `expected1/2/3`, `printwhere`, and `record_open` handle diagnostics and cleanup. `make_argname`, `add_type`, and `find_type` support newstyle args and inline XDR generation.

## Control Flow

Parser and generator modules call these helpers throughout generation. Fatal errors print source context and invoke `crash`, which unlinks recorded output files and exits. Default generation calls `reinitialize` between passes to reset scanner and AST state.

## State and Persistence Behavior

Most rpcgen shared state lives here for the lifetime of the process. Persistent effects are cleanup-related: generated output paths recorded by `record_open` may be unlinked on fatal errors.

## Dependencies and Integration Points

It depends on token and AST headers, POSIX `unlink`, and all generator modules. `rpc_main.c` initializes basic types and uses output tracking, while parser/scanner use diagnostics and globals.

## Risks and Edge Cases

Memory ownership is intentionally process-lifetime and not freed between passes beyond resetting pointers, so long-running embedding would leak. `locase` uses a static 100-byte buffer. `record_open` tracks only seven files. `streq` assumes non-NULL inputs. Fatal cleanup can unlink outputs from current generation if paths were recorded.

## Test Signals

Tests should cover fatal cleanup, source-position diagnostics, typedef chain fixing, vector typedef detection, basic type lookup, output file tracking limits, generated symbol casing, and reinitialization between multi-output generation passes.

<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/rpcgen/rpc_util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/rpcgen/rpc_util.h -->
# sources/user-network-fs/nfs-utils/tools/rpcgen/rpc_util.h

## Purpose

`rpc_util.h` declares rpcgen's shared utility macros, global variables, option flags, internal lists, and cross-module generator entry points.

## Important APIs, Types, and Functions

It defines allocation and printing macros, `struct list`, `struct xdrfunc`, `PUT`/`GET`, scanner/IO globals, the global `defined` AST list, basic type and XDR function lists, option flags, parser utility declarations, and output entry points such as `emit`, `print_datadef`, `write_most`, `write_stubs`, and `write_tables`.

## Control Flow

There is no executable flow. Including modules use the declarations to share one process-wide compiler context.

## State and Persistence Behavior

The header exposes mutable globals rather than opaque contexts. This makes rpcgen a single-compilation-at-a-time process and couples scanner, parser, and emitters.

## Dependencies and Integration Points

It depends on `definition`, `bas_type`, and `relation` from `rpc_parse.h` and standard `FILE`. It is one of the central internal interfaces for all `rpc_*.c` files.

## Risks and Edge Cases

Global mutable state prevents reentrant or parallel use. Macros wrap raw `malloc` without consistent NULL checking. Some declarations duplicate `proto.h`, so signature drift is a maintenance risk.

## Test Signals

Compile all generator modules together under strict warnings; run multi-output generation to verify global state is reset correctly between passes.

<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/rpcgen/rpc_util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/Makefile.am -->
# sources/user-network-fs/nfs-utils/utils/Makefile.am

## Purpose

This Automake file orchestrates which nfs-utils utility subdirectories are built, based on configure-time feature flags.

## Important APIs, Types, and Functions

`OPTDIRS` is conditionally extended for `idmapd`, `nfsidmap`, `exportd`, `blkmapd`, `gssd`, `mount`, `nfsdcld`, `nfsdcltrack`, `nfsref`, and `nfsdctl`. `SUBDIRS` always includes `exportfs`, `mountd`, `nfsd`, `nfsstat`, `showmount`, and `statd`, followed by `$(OPTDIRS)`.

## Control Flow

Automake recurses into the listed subdirectories during build/install. Configure feature variables decide which optional daemons/tools participate.

## State and Persistence Behavior

There is no runtime state. Build/install persistence is determined by which subdirectories produce binaries, config files, and man pages.

## Dependencies and Integration Points

It is the central build integration point for the `utils` subtree and maps configure options to built NFS client/server utilities.

## Risks and Edge Cases

Mandatory subdirectories build regardless of optional feature flags. Optional ordering can matter when subdirectories depend on generated headers or support libraries, so changes to `OPTDIRS` order should be reviewed.

## Test Signals

Configure/build matrices should toggle each feature flag and verify expected subdirectories are included or excluded, with `make dist` and `make install` still succeeding.

<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/blkmapd/Makefile.am -->
# sources/user-network-fs/nfs-utils/utils/blkmapd/Makefile.am

## Purpose

This Automake file builds and installs the `blkmapd` pNFS block layout daemon and its manual page.

## Important APIs, Types, and Functions

It declares `man8_MANS = blkmapd.man`, adds `-D_LARGEFILE64_SOURCE` to `AM_CFLAGS`, builds `sbin_PROGRAMS = blkmapd`, compiles device discovery/inquiry/process and device-mapper sources, and links `-ldevmapper` plus `../../support/nfs/libnfs.la`.

## Control Flow

Automake compiles `device-discovery.c`, `device-inq.c`, `device-process.c`, `dm-device.c`, and `device-discovery.h` into the daemon when the parent includes this directory.

## State and Persistence Behavior

The build file has no runtime state. It controls installed daemon and man page artifacts.

## Dependencies and Integration Points

It depends on libdevmapper and nfs-utils support library code. The parent `utils/Makefile.am` includes this directory only under `CONFIG_BLKMAPD`.

## Risks and Edge Cases

Systems without device-mapper development headers/libraries will fail this optional build. Large-file macro consistency matters because the daemon inspects block devices and device-mapper metadata.

## Test Signals

Build with `CONFIG_BLKMAPD` enabled and disabled, verify libdevmapper linkage, install the daemon/man page, and run daemon-level tests against mocked or isolated device discovery where available.

<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/blkmapd/Makefile.am -->
