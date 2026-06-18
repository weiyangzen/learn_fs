# subset-b-009243 research

Grouped research report for selected iozone and kdevops files under `sources/test-tools`. Each section title preserves the exact source path and is wrapped for reconciliation into the source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/iozone/src/current/iozone_visualizer.pl -->
# sources/test-tools/iozone/src/current/iozone_visualizer.pl

Purpose: modernized Perl visualizer for one or more iozone text reports. It extracts numeric 15-column benchmark rows, writes normalized 3D and filtered 2D `.dat` files, generates gnuplot scripts for every throughput metric, invokes gnuplot, and writes an `index.html` page linking all generated PNG graphs.

Important APIs/types/functions: uses `Getopt::Long` for `--3d`, `--2d`, and `--nooffset`, `Readonly` for constants, `List::MoreUtils::any` for validation, `Carp`/`English` for errors, and Perl filehandles for report/data/html/script output. The metric map `%columns` indexes iozone columns `KB`, `reclen`, `write`, `rewrite`, `read`, `reread`, `randread`, `randwrite`, `bkwdread`, `recrewrite`, `strideread`, `fwrite`, `frewrite`, `fread`, and `freread`.

Control flow: parse options and default graph sizes; reject missing arguments, option-looking report names, or report paths containing `/`; derive an output directory named `report_<report basenames>`; remove any existing directory with `rm -rf`; create per-report `.dat` and `2d-.dat` files; skip nonnumeric lines and rows that do not have exactly 15 fields; insert blank separators when the file-size column changes; write 2D rows only when record length is `16384` or equals file size; build an HTML menu and graph sections; for each non-axis metric, write 3D and 2D gnuplot scripts, run `gnuplot`, and report per-graph success.

State/persistence behavior: destructive output state is the generated `report_*` directory. It persists `.dat`, `2d-*.dat`, `*.do`, graph PNGs, and `index.html`; it does not mutate source reports. Existing output directory contents are unconditionally deleted before regeneration.

Dependencies/integration: depends on non-core Perl modules `Readonly` and `List::MoreUtils`, local shell `rm`, and `gnuplot` with PNG terminal support. It integrates with iozone `-a` style output where the benchmark table has 15 numeric columns.

Risks/test signals: report filenames are interpolated into shell commands and gnuplot script strings, so the current-directory restriction reduces but does not eliminate quoting risks. `system "rm -rf $outdir"` is destructive if name construction is ever widened. Hash iteration order makes graph order nondeterministic. A practical test is running against a small captured iozone report and checking non-empty `.dat`, `index.html`, `.do`, and PNG outputs plus stderr `(ok)` messages.
<!-- END_FILE_RESEARCH: sources/test-tools/iozone/src/current/iozone_visualizer.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/iozone/src/current/libasync.c -->
# sources/test-tools/iozone/src/current/libasync.c

Purpose: iozone support library for POSIX AIO-assisted reads and writes. It provides two read models, one that copies completed async data into a caller buffer and another that returns the internal aligned buffer to the caller, plus buffered and no-copy async write helpers for benchmark paths that want a bounded queue of outstanding I/O.

Important APIs/types/functions: exported entry points are `async_init`, `end_async`, `async_read`, `async_read_no_copy`, `async_release`, `async_write`, and `async_write_no_copy`. Internal helpers include `async_suspend`, `alloc_cache`, `incache`, `takeoff_cache`, `del_cache`, `putoninuse`, `takeoffinuse`, `allocate_write_buffer`, `async_put_on_write_queue`, `async_wait_for_write`, `async_write_finish`, and byte-copy helper `mbcopy`. `struct cache_ent` wraps `aiocb` or `aiocb64`, file descriptor, size, linked-list fields, ownership flags, real allocation address, and no-copy "old" fields used to detect in-flight mutation. `struct cache` holds read cache head/tail/count, no-copy in-use head, and write queue head/tail/count.

Control flow: `async_init` optionally enables VXFS direct cache behavior, allocates and zeroes a cache, and sets global `max_depth` from `_SC_AIO_MAX` or platform constants. `async_read` first checks whether the requested `(fd, offset, size)` exists in the cache; cache hits wait for completion, copy the result into `ubuffer`, and remove the entry. Cache misses purge outstanding read-ahead, allocate and submit the mandatory first read, optionally queue stride-based read-ahead up to `depth`, then wait for the first read and copy it. `async_read_no_copy` follows the same scheduling logic but returns the completed AIO buffer pointer and moves the cache entry to `inuse_head`; callers must later call `async_release`. Writes allocate an aligned buffer or wrap a caller buffer, copy when needed, append to the write queue, issue `aio_write`/`aio_write64`, and drain older writes on queue-depth pressure or AIO `EAGAIN`. `end_async` purges reads, finishes writes, and frees the cache object.

State/persistence behavior: the library maintains process-local linked lists of pending reads, no-copy buffers handed to the caller, and pending writes. It allocates page-size-padded buffers aligned manually from `real_address`. It persists only through submitted filesystem I/O; there is no durable metadata. Error handling commonly prints to stdout/stderr and exits with fixed codes for allocation or write failures.

Dependencies/integration: depends on POSIX AIO (`aio_read`, `aio_suspend`, `aio_error`, `aio_return`, `aio_cancel`, `aio_write` and 64-bit variants), platform feature macros such as `_LARGEFILE64_SOURCE`, `__LP64__`, `__CrayX1__`, `linux`, `solaris`, and `VXFS`, and external globals `page_size` and `one` from iozone. The makefile compiles this only for targets that enable `ASYNC_IO` and usually links with `-lrt`/thread libraries.

Risks/test signals: it is non-thread-safe unless externally serialized. The manual alignment casts pointers through `long`, which is fragile on unusual data models. Several paths spin on `EAGAIN`, ignore short reads after logging, and call `aio_return` after cancellation without detailed status handling. `takeoffinuse` appears to expect only one outstanding no-copy buffer and logs if more remain. There are duplicated and malformed-looking preprocessor-adjacent lines, so compile coverage across all platform targets is important. Test signals are successful iozone async read/write modes under large-file builds, no leaks under no-copy read/release cycles, bounded outstanding write depth, and clean behavior when AIO returns `EAGAIN`.
<!-- END_FILE_RESEARCH: sources/test-tools/iozone/src/current/libasync.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/iozone/src/current/libbif.c -->
# sources/test-tools/iozone/src/current/libbif.c

Purpose: tiny BIFF2 writer used by iozone to create simple Excel-compatible worksheet files containing integer, floating-point, and string cells.

Important APIs/types/functions: public API is `create_xls(char *)`, `close_xls(int)`, `do_int(int,int,int,int)`, `do_float(int,double,int,int)`, and `do_label(int,char *,int,int)` when `HAVE_ANSIC_C` is set, with K&R fallback definitions otherwise. Internal helpers are `do_header`, `do_eof`, and `endian`. BIFF record structs model BOF, integer, label, and float cells, with constants `BOF`, `INTEGER`, `FLOAT`, `LABEL`, `EXCEL_VERS`, and `WORKSHEET`.

Control flow: `create_xls` unlinks the target, opens it, writes a BOF record, and returns the file descriptor. Cell writers construct BIFF records with little-endian row, column, and value fields, then write them directly. `do_float` converts the in-memory double to little-endian byte order for little, big, and one middle-endian layout before writing the fixed header and double separately to avoid structure padding. `do_label` zeroes a 255-byte string array, truncates overlong input by modifying `string[254]`, copies it into the record, and writes the full label struct. `close_xls` writes EOF and closes the descriptor.

State/persistence behavior: each call appends binary BIFF records to the worksheet file. There is no buffering beyond stack structs and no workbook state besides the file descriptor. Existing output files are removed on create. Global `junk` receives write return values but they are not validated.

Dependencies/integration: depends on low-level POSIX/Windows-like `open`, `write`, `close`, and `unlink`, plus platform include branches for AIX/BSD/Linux/macOS/Windows. It integrates with iozone reporting code that wants legacy `.xls` output without an external spreadsheet library.

Risks/test signals: row and column limits are effectively 8-bit/BIFF2 era and comments warn values above 255 behave poorly. `do_label` can mutate the caller's string when truncating and does not re-check writable storage. Writes are unchecked, so disk/full or descriptor failures can silently corrupt output. A test signal is opening generated files in a spreadsheet tool and checking integer, float byte order on big/little endian, labels at expected cells, and EOF presence.
<!-- END_FILE_RESEARCH: sources/test-tools/iozone/src/current/libbif.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/iozone/src/current/makefile -->
# sources/test-tools/iozone/src/current/makefile

Purpose: platform matrix makefile for building iozone, `fileop`, and `pit_server` across legacy Unix, Linux, BSD, Solaris, Windows/Cygwin/SUA, and other targets. The default `all` target prints supported explicit targets rather than building.

Important APIs/types/functions: make variables include `CC`, `C89`, `GCC`, `CCS`, `NACC`, `CFLAGS`, `LDFLAGS`, `S10GCCFLAGS`, `S10CCFLAGS`, and `FLAG64BIT`. User-facing targets include `linux`, `linux-AMD64`, `linux-arm`, `linux-powerpc*`, `linux-S390*`, `Solaris*`, `AIX*`, `freebsd`, `openbsd`, `macosx`, `Windows`, `SUA`, `clean`, `rpm`, and `pantheon`. Object rules compile `iozone.c`, `libasync.c`, `libbif.c`, `fileop.c`, and `pit_server.c` with per-platform macro sets such as `ASYNC_IO`, `NO_THREADS`, `SHARED_MEM`, `_LARGEFILE64_SOURCE`, `_FILE_OFFSET_BITS=64`, `HAVE_PREAD`, `DONT_HAVE_O_DIRECT`, and platform `NAME` strings.

Control flow: each platform target depends on a set of object files, then links the needed binaries with platform-specific libraries. Object rules echo the build target, compile iozone and support libraries with the relevant macros, and reuse common output names like `libasync.o` and `libbif.o`. Targets that support `fileop` and `pit_server` build those additional binaries. `clean` removes object files and three binaries; `rpm` copies source tarballs into RPM build dirs and runs `rpmbuild -ba spec.in`.

State/persistence behavior: builds write object files and binaries directly into `src/current`; many targets share object names, so switching targets without `make clean` can mix incompatible objects. The `rpm` target writes to `/usr/src/red*/SO*` and invokes system RPM build state.

Dependencies/integration: tightly coupled to `iozone.c`, `libasync.c`, `libbif.c`, `fileop.c`, `pit_server.c`, and RPM `spec.in`. Platform link dependencies include pthreads, realtime/AIO libraries, Solaris networking libraries, HP/AIX/SCO specialty libraries, and optional VXFS headers. Downstream packaging and CI likely select architecture-specific targets rather than the default.

Risks/test signals: the file encodes many legacy targets with repeated commands, duplicated compile lines, target-specific object reuse, and some apparent copy/paste defects; broad compile coverage is the main safety net. Linux smoke tests should run `make clean && make linux` or `linux-AMD64`, then execute `iozone`, `fileop`, and `pit_server` basics. Cross-target tests should always clean first to avoid stale objects.
<!-- END_FILE_RESEARCH: sources/test-tools/iozone/src/current/makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/iozone/src/current/pit_server.c -->
# sources/test-tools/iozone/src/current/pit_server.c

Purpose: IPv4/IPv6 TCP and UDP "Programmable Interdimensional Timer" server that returns the current timestamp in microseconds as a decimal string. It is used by iozone as a lightweight timing service.

Important APIs/types/functions: `main` parses `-v` and required `-p service`; `openSckt` uses `getaddrinfo`, `socket`, `setsockopt(IPV6_V6ONLY)`, `bind`, and `listen` to open passive sockets; `pit` uses `poll`, `accept`, `shutdown`, `write`, `recvfrom`, `sendto`, `gettimeofday`, and Windows `QueryPerformanceCounter` alternatives. Macros include `DFLT_SERVICE`, `MAXTCPSCKTS`, `MAXUDPSCKTS`, `VALIDOPTS`, `USAGE`, and `CHK`.

Control flow: `main` defaults the service name to `PIT` but requires `-p`, opens both TCP and UDP socket arrays for the requested service, and enters `pit` when at least one socket exists. `openSckt` clears descriptor slots, sets hints for TCP or UDP, walks address records, optionally prints address metadata, creates sockets, enforces IPv6-only behavior when available, binds, listens for TCP, and records descriptors. `pit` builds a `pollfd` array covering TCP sockets followed by UDP sockets, waits forever, computes the current microsecond counter once per poll wakeup, and sends that string to each ready TCP connection or UDP sender.

State/persistence behavior: process-local state includes global verbose flag, host/service formatting buffers, `timeStr`, and socket descriptors. The server has no durable state and never returns from the main loop under normal operation. Each request gets the timestamp captured before the ready-socket loop, so multiple ready clients in one poll cycle receive the same value.

Dependencies/integration: depends on network database APIs, POSIX sockets, `poll`, `gettimeofday`, and platform branches for Windows and SUA. `/etc/services` may define `PIT`, but `-p` can pass a numeric or named service to `getaddrinfo`. The iozone makefile builds this helper for many platform targets.

Risks/test signals: global `service_name[20]` is filled with `strcpy(optarg)` and can overflow on long service names. `CHK` exits the whole daemon on many transient network errors. Partial TCP/UDP send loops advance `wBytes` but always pass `timeStr` rather than `timeStr + bytes_sent`, so rare partial writes can repeat the beginning of the timestamp. Verbose code contains duplicated fragments that may affect compilation. Smoke tests should bind an ephemeral port, query over TCP and UDP, validate numeric microsecond strings, and verify IPv4/IPv6 behavior when available.
<!-- END_FILE_RESEARCH: sources/test-tools/iozone/src/current/pit_server.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/iozone/src/current/report.pl -->
# sources/test-tools/iozone/src/current/report.pl

Purpose: older Perl report generator for iozone output. It extracts benchmark rows, creates gnuplot scripts for 3D and 2D graphs per metric, and runs gnuplot to produce PNG files in a `report_*` directory.

Important APIs/types/functions: script-level variables `@Reports`, `%columns`, `$outdir`, `@datafiles`, and per-column gnuplot filehandles drive behavior. `%columns` maps throughput metrics to iozone output columns 3 through 15; unlike `iozone_visualizer.pl`, it omits axis columns from the map.

Control flow: reject no reports, option-looking names, or paths containing `/`; derive and recreate the output directory; for each report, write `<basename>.dat` and `2d-<basename>.dat` from numeric rows with at least eight fields; put rows in the 2D file when record length is `16384` or equals file size; for every metric, write `$column.do` and `2d-$column.do`, run both through gnuplot in the output directory, and print `(ok)` or `(failed)`.

State/persistence behavior: destructively removes a same-named `report_*` output directory and persists `.dat`, `2d-*.dat`, `.do`, and PNG files. It does not write HTML and does not mutate the input reports.

Dependencies/integration: depends on core Perl, shell `rm -rf`, and gnuplot. It expects iozone text output in the historical numeric table format and is effectively superseded by the stricter `iozone_visualizer.pl`.

Risks/test signals: no `use strict`/warnings, two-argument `open`, shell interpolation, and permissive row width (`>= 8`) make it less robust than the newer visualizer. It also uses hash iteration order for graph generation. Test with a known report should produce all metric PNGs and correctly filtered 2D data.
<!-- END_FILE_RESEARCH: sources/test-tools/iozone/src/current/report.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/iozone/src/current/spec.in -->
# sources/test-tools/iozone/src/current/spec.in

Purpose: RPM spec template for packaging iozone version 3 release 414 into `/opt/iozone`.

Important APIs/types/functions: RPM sections include header metadata, `%description`, `%prep`, `%setup -n iozone3_414/src/current`, `%build`, `%install`, `%files`, and `%clean`. The build section selects make targets by `%ifarch` for x86, x86_64, ia64, ppc, ppc64, s390, s390x, and arm.

Control flow: during build, choose an architecture-specific iozone make target or fail with "No idea how to build for your arch...". During install, create `/opt/iozone/bin`, docs, and man directories under `$RPM_BUILD_ROOT`; copy `iozone`, `fileop`, `pit_server`, graph scripts/demos, PDFs/docs, and the man page; `%files` packages `/opt/` with root ownership and executable mode; `%clean` removes the build root.

State/persistence behavior: RPM build writes into `$RPM_BUILD_ROOT` and assumes source extraction under `$RPM_BUILD_DIR/iozone3_414`. It packages an entire `/opt` subtree rather than enumerating individual files.

Dependencies/integration: integrated with the iozone makefile `rpm` target and RPM tooling. It assumes tarball naming `%{name}%{version}_%{release}.tar`, docs outside `src/current`, and matching make targets for each supported architecture.

Risks/test signals: hard-coded version/release and paths must track source layout. `%files /opt/` is broad and may be undesirable for packaging hygiene. The `%ifarch %(arm)` syntax looks suspicious and needs rpm macro validation. Test signals are `rpmbuild -ba spec.in` on supported architectures and verification that expected binaries/docs/man pages appear in the RPM payload.
<!-- END_FILE_RESEARCH: sources/test-tools/iozone/src/current/spec.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/.github/actions/archive/action.yml -->
# sources/test-tools/kdevops/.github/actions/archive/action.yml

Purpose: composite GitHub Action that collects and uploads kdevops CI results for archiving.

Important APIs/types/functions: inputs are optional `ci_workflow` defaulting to `demo` and required `ssh_private_key`. Steps use `webfactory/ssh-agent@v0.9.0`, run `make journal-dump`, run `make ci-archive CI_WORKFLOW=...`, and upload `archive/*.zip` with `actions/upload-artifact@v4`.

Control flow: start an SSH agent with the private key for the external results repository; dump systemd journals; build the archive zip via make; upload the generated zips as a workflow artifact named with the workflow id.

State/persistence behavior: produces local `archive/*.zip` and likely CI metadata/commit artifacts through the make target. It reads SSH private key secret but does not persist it itself.

Dependencies/integration: depends on kdevops make targets `journal-dump` and `ci-archive`, GitHub artifacts, and an SSH key with access to `linux-kdevops/kdevops-results-archive.git`.

Risks/test signals: missing secrets or archive files fail the action. `set -euxo pipefail` can expose command lines but not key contents from the action input. Test signal is a workflow run with a generated zip artifact and successful archive make target.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/.github/actions/archive/action.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/.github/actions/bringup/action.yml -->
# sources/test-tools/kdevops/.github/actions/bringup/action.yml

Purpose: composite GitHub Action that resets and brings up kdevops guests.

Important APIs/types/functions: has no inputs. Single bash step runs `make destroy` followed by `make bringup` with `set -euxo pipefail`.

Control flow: destroy any existing VM state first, then create/provision guests through the repository make targets.

State/persistence behavior: intentionally mutates external virtualization state by destroying and recreating guests. It also updates generated local state produced by bringup.

Dependencies/integration: depends on configured `.config`, generated inventory/vars, hypervisor/provider tooling, and kdevops make targets.

Risks/test signals: `make destroy` is destructive and runs unconditionally, so this action is only appropriate for disposable CI host prefixes. Test signals are successful guest creation, reachable inventory, and cleanup later in the workflow.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/.github/actions/bringup/action.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/.github/actions/build-test/action.yml -->
# sources/test-tools/kdevops/.github/actions/build-test/action.yml

Purpose: composite GitHub Action that installs or builds test suites required for a selected kdevops CI workflow.

Important APIs/types/functions: optional `ci_workflow` input defaulting to `demo`; single step runs `make ci-build-test CI_WORKFLOW=${{ inputs.ci_workflow }}`.

Control flow: delegates all workflow-specific test setup to the repository make target after configuration, bringup, and Linux install have completed.

State/persistence behavior: mutates guest or workspace state through the make target, such as installing fstests, blktests, or selftests dependencies.

Dependencies/integration: depends on `scripts/ci.Makefile`/workflow make plumbing and the selected `CI_WORKFLOW`.

Risks/test signals: lack of quoting around the substituted workflow is typical in actions but would be risky if input choices widened beyond controlled values. Test signal is a successful `ci-build-test` target before the test action runs.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/.github/actions/build-test/action.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/.github/actions/cleanup/action.yml -->
# sources/test-tools/kdevops/.github/actions/cleanup/action.yml

Purpose: composite GitHub Action for final kdevops VM cleanup.

Important APIs/types/functions: no inputs. Single bash step runs `make destroy` with strict shell flags.

Control flow: invoked with `if: always()` in the main workflow to destroy guests even after failures.

State/persistence behavior: destroys external VM/provider state and may remove local generated state according to the make target.

Dependencies/integration: depends on the same kdevops configuration and provider tooling used for bringup.

Risks/test signals: cleanup failure can leave CI resources running. Test signal is a successful destroy target and no surviving CI-prefixed guests.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/.github/actions/cleanup/action.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/.github/actions/configure/action.yml -->
# sources/test-tools/kdevops/.github/actions/configure/action.yml

Purpose: composite GitHub Action that prepares a kdevops workspace for a CI workflow by selecting a defconfig, writing CI metadata, merging CI-safe config fragments, and running the top-level make.

Important APIs/types/functions: inputs include `ci_workflow`, `kernel_tree`, `kernel_ref`, `test_mode`, and `guest_os`. Important steps configure git identity/safe-directory, validate `defconfigs/<ci_workflow>`, write GitHub output via `scripts/github_output.sh`, create `ci.trigger`, `ci.subject`, `ci.ref`, `ci.result`, and `ci.commit_extra`, run `make defconfig-...` with `KDEVOPS_HOSTS_PREFIX`, `LINUX_TREE`, and `LINUX_TREE_REF`, merge config fragments with `scripts/kconfig/merge_config.sh`, and run `make -j$(nproc)`.

Control flow: fail early if the requested defconfig is missing; initialize pessimistic CI metadata; compute a unique host prefix from GitHub run identifiers and test mode; optionally set `KMOD_TIMEOUT` on specific hosts/workflows; run the selected defconfig; merge base DIY/CI config plus optional VM sizing and guest OS config; run the build/generation make target.

State/persistence behavior: writes `.config`, generated ansible variables/inventory files through make, CI metadata files, and GitHub step output. It also relies on `/mirror/<kernel_tree>.git` for kernel source references.

Dependencies/integration: integrates with defconfigs, kconfig merge tooling, GitHub context variables, local mirror layout, scripts for GitHub outputs, and the top-level Makefile dependency graph.

Risks/test signals: inputs are inserted into shell variables and make arguments; the workflow constrains many values but `kernel_ref` is free-form. Missing guest OS config fails intentionally. Test signals are generated `.config`, `.extra_vars_auto.yaml`, `extra_vars.yaml`, `ansible.cfg`, `hosts`, and a successful parallel `make`.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/.github/actions/configure/action.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/.github/actions/linux/action.yml -->
# sources/test-tools/kdevops/.github/actions/linux/action.yml

Purpose: composite GitHub Action that installs/builds the configured Linux kernel and records the resulting git reference for CI reporting.

Important APIs/types/functions: no inputs. Steps run `make linux`, then `cd linux/`, compute `git rev-parse --short=12 HEAD`, write it to `../ci.git_ref`, and echo it.

Control flow: delegate kernel checkout/build/boot work to `make linux`, then record the exact checked-out kernel commit after the `linux/` tree exists.

State/persistence behavior: mutates or creates the local `linux/` checkout and writes `ci.git_ref`.

Dependencies/integration: depends on workflow configuration from the configure action, kdevops Linux make targets, and `git` in the Linux checkout.

Risks/test signals: assumes `linux/` exists after `make linux`; if the make target succeeds without a checkout, metadata generation fails. Test signal is a valid 12-character commit hash in `ci.git_ref`.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/.github/actions/linux/action.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/.github/actions/test/action.yml -->
# sources/test-tools/kdevops/.github/actions/test/action.yml

Purpose: composite GitHub Action that runs a selected kdevops test workflow, classifies results, and generates commit-message metadata for the archive.

Important APIs/types/functions: inputs are `ci_workflow`, `test_mode`, and optional `tests`. Step `ci_test` determines `TESTS`, writes it to GitHub output, records `ci.start_time`, and runs `make ci-test CI_WORKFLOW=...`. Step `setpath` maps workflow names to result paths. The final step reads result files, writes `ci.commit_extra`, sets `ci.result`, exports CI context, and runs `scripts/generate_ci_commit_message.sh` to create `ci.commit_message_enhanced`.

Control flow: if `tests` input is provided, use it; otherwise in `kdevops-ci` mode choose a small representative test by workflow pattern (`generic/003`, `block/003`, or `kmod/test_001`); in `linux-ci` mode leave `TESTS` empty for full suites. After tests run, map workflow to `workflows/blktests`, `workflows/fstests`, or `workflows/selftests`. Result classification is workflow-specific: fstests reads `xunit_results.txt` or dmesg fallback and greps failure/error counts; blktests counts unique result files and `.out.bad`; selftests reads `*.userspace.log` and scans pass/fail strings; default mode tails dmesg/userspace logs and greps for failure.

State/persistence behavior: writes `ci.start_time`, `ci.commit_extra`, `ci.result`, and `ci.commit_message_enhanced`, and reads test results from `workflows/*/results/last-run`. The make target mutates guest and workflow result state.

Dependencies/integration: depends on prior configure/bringup/linux/build-test actions, `scripts/github_output.sh`, kdevops `ci-test` target, workflow result directory conventions, and `scripts/generate_ci_commit_message.sh`.

Risks/test signals: the action uses heuristic grep-based result classification that can misclassify unusual logs. The final step references `inputs.kernel_tree` even though this action does not declare that input, so it falls back to `linux` via expression defaulting; this is intentional-looking but easy to misunderstand. A test signal is correct `ci.result` for known passing/failing fixture result directories and a generated enhanced commit message.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/.github/actions/test/action.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/.github/workflows/config-tests.yml -->
# sources/test-tools/kdevops/.github/workflows/config-tests.yml

Purpose: GitHub-hosted workflow that validates kdevops configuration generation and Linux A/B setup in containers without provisioning real infrastructure.

Important APIs/types/functions: triggers on push to `main` and `ci-testing/**`, pull requests to `main`, and manual dispatch. Environment variables define GHCR image naming. Jobs are `build-kdevops-containers`, `linux-ab-config-tests`, and `quick-config-validation`.

Control flow: the first job builds Debian testing, Fedora latest, and openSUSE Tumbleweed containers with Ansible/build dependencies, smoke-runs `make mrproper`, pushes images to GHCR, and exposes image tags as outputs. `linux-ab-config-tests` runs `make check-linux-ab` in each built image. `quick-config-validation` runs a matrix of defconfigs (`blktests_nvme`, `xfs_reflink_4k`, `lbs-xfs`, `linux-ab-testing`) across the same distros, verifies `.config` and `.extra_vars_auto.yaml`, manually generates container-safe core files (`.kdevops.depcheck`, `extra_vars.yaml`, `ansible.cfg`, `hosts`), and asserts they exist.

State/persistence behavior: builds and pushes transient container images tagged by commit SHA, writes Dockerfiles in the workflow workspace, and generates kdevops config artifacts inside job containers.

Dependencies/integration: uses `actions/checkout@v4`, `docker/login-action@v3`, GHCR package permissions, Docker build/run, and kdevops make targets. It depends on package manager names across Debian/Fedora/openSUSE.

Risks/test signals: echo strings include emoji/non-ASCII but shell behavior is otherwise straightforward. Output image steps are conditional per matrix row, so downstream jobs depend on those outputs being set correctly. Test signals are successful container pushes and config file existence checks across all matrix combinations.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/.github/workflows/config-tests.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/.github/workflows/kdevops.yml -->
# sources/test-tools/kdevops/.github/workflows/kdevops.yml

Purpose: main kdevops CI workflow for scheduled, push, pull request, and manual runs on self-hosted runners. It configures kdevops, brings up guests, installs Linux/tests, runs tests, archives results, and cleans up.

Important APIs/types/functions: triggers include daily cron, push, pull request, and `workflow_dispatch` inputs for workflow, kernel tree/ref, test mode, guest OS, and custom tests. Jobs are `generate_kernel_ref`, `check_ref`, and matrix job `ci-matrix`. The workflow composes local actions `configure`, `bringup`, `linux`, `build-test`, `test`, `archive`, and `cleanup`.

Control flow: scheduled runs generate a kernel ref from `scripts/korg-releases.py`, using mainline on Mondays and linux-next otherwise. Manual runs validate `kernel_ref` against `/mirror/<tree>.git`. The matrix selects `blktests` for schedule, one requested workflow for manual dispatch, or a small default push/PR matrix. Each matrix lane fresh-cleans the workspace, clones the repository with optional local mirror reference, checks out PR head or event ref, reports commit metadata, then runs the local composite actions. Test timeout is 24 hours for linux-ci/schedule and 2 hours for kdevops-ci. Cleanup always runs.

State/persistence behavior: deliberately deletes workspace contents at job start, creates guests and workflow state through kdevops, writes CI metadata files, uploads archive artifacts, and destroys guests in cleanup.

Dependencies/integration: depends on self-hosted runner labels `kdevops-ci` and `linux-ci`, local mirrors under `/mirror`, secrets `SSH_PRIVATE_KEY`, local action files, kdevops defconfigs, and all CI make targets.

Risks/test signals: the manual ref check assigns `contains_tag` using `git branch --contains` rather than tag inspection, so tag validation may be weaker than intended. `rm -rfv ./* ./.*` is intentionally aggressive inside the runner workspace. Test signal is a full successful matrix lane with archive artifact and cleanup, plus skipped/success needs logic allowing non-applicable preparatory jobs.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/.github/workflows/kdevops.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/.gitlab-ci.yml -->
# sources/test-tools/kdevops/.gitlab-ci.yml

Purpose: minimal GitLab CI configuration for simple container-based dependency and make-target validation.

Important APIs/types/functions: defines one stage `simple-docker-tests`, a hidden `.parallel-distro-template` matrix for Debian testing and Fedora latest, and job `setup-distro-deps` using `$DISTRO_CONTAINER`.

Control flow: for each distro matrix row, print environment metadata, install kdevops dependencies with either apt or dnf, and run `make mrproper`.

State/persistence behavior: mutates only the CI container by installing packages and generated clean state from `make mrproper`.

Dependencies/integration: depends on Debian/Fedora package names for Ansible, make, gcc, ncurses, bison, and flex. It provides a GitLab counterpart to the GitHub config smoke tests.

Risks/test signals: `PACKAGER` includes command arguments and is expanded as shell text; the values are static in the matrix. The job is a shallow smoke test, not a full configuration build. Success signal is package installation and `make mrproper` passing in both containers.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/.gitlab-ci.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/.pre-commit-config.yaml -->
# sources/test-tools/kdevops/.pre-commit-config.yaml

Purpose: pre-commit configuration that enables codespell checking for repository spelling hygiene.

Important APIs/types/functions: declares repository `https://github.com/codespell-project/codespell`, revision `v2.2.5`, hook id `codespell`, and additional dependency `tomli`.

Control flow: pre-commit installs the pinned hook environment and runs codespell on changed files according to pre-commit defaults.

State/persistence behavior: no repository state is changed except developer pre-commit caches; hook failures block commits locally.

Dependencies/integration: integrates with the Python pre-commit framework and codespell. `tomli` supports config parsing on older Python versions.

Risks/test signals: a single broad hook can flag third-party/vendor terms unless ignored elsewhere. Test signal is `pre-commit run --all-files` completing with expected spelling results.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/.pre-commit-config.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/.rustfmt.toml -->
# sources/test-tools/kdevops/.rustfmt.toml

Purpose: rustfmt configuration for any Rust code in kdevops.

Important APIs/types/functions: sets `edition = "2021"` and `newline_style = "Unix"`. Several unstable options are documented but commented out, including formatting doc comments, impl item reordering, comment width, wrapping comments, and normalizing comments.

Control flow: rustfmt reads this file when formatting Rust sources and applies only stable active settings.

State/persistence behavior: affects formatting output when rustfmt is run; no runtime state.

Dependencies/integration: depends on rustfmt and Rust 2021 edition expectations.

Risks/test signals: commented unstable options are not active, so developers may see different results if they manually enable nightly-only formatting. Test signal is `cargo fmt --check` or `rustfmt --check` using Unix newlines and 2021 parsing.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/.rustfmt.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/.travis.yml -->
# sources/test-tools/kdevops/.travis.yml

Purpose: legacy Travis CI configuration for running Python-oriented make tests.

Important APIs/types/functions: selects `language: python`, Python `3.6`, script `make python-tests`, and email notifications to `mcgrof@kernel.org` on failure only.

Control flow: Travis creates a Python 3.6 job, runs the make target, and sends notification according to the configured policy.

State/persistence behavior: only CI workspace state produced by `make python-tests`.

Dependencies/integration: depends on Travis CI, Python 3.6 availability, and a `python-tests` make target from the repository include graph.

Risks/test signals: Python 3.6 is end-of-life and may no longer be available on modern CI images. This file may be historical if Travis is not active. Test signal is a Travis job successfully invoking `make python-tests`.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/.travis.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/Kconfig -->
# sources/test-tools/kdevops/Kconfig

Purpose: root Kconfig menu for kdevops. It defines top-level project menu text, a few global config symbols, and includes the rest of the kdevops configuration tree.

Important APIs/types/functions: `mainmenu "$(PROJECT) $(PROJECTRELEASE)"`; config symbols `HAVE_KDEVOPS_CUSTOM_DEFAULTS`, `NEEDS_LOCAL_DEVELOPMENT_PATH`, `KDEVOPS_FIRST_RUN`, and `LOCAL_DEVELOPMENT_PATH`; `source` entries for defaults, distro, SSH, storage, git sources, email, hypervisor, mirror, bringup, sysctl, workflows, monitors, and kdevops options.

Control flow: Kconfig frontends load this file, expose "first run" and local development path prompts when dependencies match, and recursively include submenu files. `KDEVOPS_FIRST_RUN` uses `output yaml`, so selected values feed generated YAML configuration.

State/persistence behavior: selections are stored in `.config` and converted to `.extra_vars_auto.yaml` through kdevops kconfig tooling. `LOCAL_DEVELOPMENT_PATH` defaults to `$HOME/devel/` when local development is needed.

Dependencies/integration: used by `scripts/kconfig/kconfig.Makefile`, the top-level Makefile, defconfig targets, and YAML generation. Source paths must remain valid for menuconfig/oldconfig.

Risks/test signals: missing sourced Kconfig files break all configuration. Shell-derived defaults can vary by user environment. Test signals include `make oldconfig`, `make menuconfig`, and defconfig generation producing expected `.config` and YAML.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/Makefile -->
# sources/test-tools/kdevops/Makefile

Purpose: top-level orchestration Makefile for kdevops. It wires Kconfig-generated configuration into ansible inventory/vars, dependency checks, provisioning, workflow targets, Linux/test/archive helpers, cleanup, and user help.

Important APIs/types/functions: project version variables produce `PROJECTRELEASE`; exported paths include `KCONFIG_DIR`, `KCONFIG_YAMLCFG`, `KDEVOPS_EXTRA_VARS`, `KDEVOPS_PLAYBOOKS_DIR`, `TOPDIR_PATH`, and `ANSIBLE_CONFIG`. Includes pull in `kconfig.Makefile`, `Makefile.subtrees`, refs, minimum deps, extra vars, ansible, provision, firstconfig, service setup, workflow, protocol, devconfig, Linux mirror/docker mirror, gen-hosts/nodes, tests, CI, archive, defconfig, and style makefiles. Key targets are `.config`, `$(ANSIBLE_CFG_FILE)`, `$(KDEVOPS_EXTRA_VARS)`, `playbooks/secret.yml`, `$(ANSIBLE_INVENTORY_FILE)`, `$(KDEVOPS_NODES)`, `contrib-graph`, `clean`, `version-check`, `mrproper`, `kconfig-help-menu`, `help`, `deps`, and `install`.

Control flow: default `all` depends on `deps`. If `.config` is missing, a friendly error prints configuration options. With `.config`, verbosity settings can set `Q`/`NQ`. The Makefile accumulates `DEFAULT_DEPS` from config-dependent includes, ansible extra vars, ansible config, inventory, localhost setup work, and workflow/provision dependencies. File targets generate ansible config and hosts through local ansible-playbook runs using generated YAML. `mrproper` delegates cleanups and removes generated config, inventory, terraform state fragments, secrets, include/guestfs directories, and refs defaults.

State/persistence behavior: writes and removes `.config`, `.config.old`, `.extra_vars_auto.yaml`, `extra_vars.yaml`, `.kdevops.depcheck`, `ansible.cfg`, `hosts`, generated node files, `playbooks/secret.yml`, extra addon destinations, `include`, `guestfs`, terraform generated files, and workflow-specific artifacts through included makefiles.

Dependencies/integration: central integration point for kconfig, ansible playbooks, shell scripts, defconfigs, workflows, CI actions, and hypervisor/provider tooling. GitHub/GitLab CI call many targets defined here or in its includes.

Risks/test signals: the Makefile is highly include-order sensitive; duplicated include of `scripts/devconfig.Makefile` may be harmless but deserves awareness. Many variables are derived from `.config`, so stale generated files can mislead if not cleaned. Test signals are `make defconfig-...`, `make deps`, `make mrproper`, GitHub config-tests file existence checks, and successful CI action target execution.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/callback_plugins/__init__.py -->
# sources/test-tools/kdevops/callback_plugins/__init__.py

Purpose: package marker for kdevops Ansible callback plugins.

Important APIs/types/functions: the file is empty and exports no symbols.

Control flow: none.

State/persistence behavior: none.

Dependencies/integration: allows Python/Ansible tooling to treat `callback_plugins` as an importable package on runtimes that still care about package markers, and colocates `lucid.py` as a callback plugin.

Risks/test signals: no direct risks. Test signal is Ansible discovering the adjacent callback plugin when this directory is on the callback plugin path.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/callback_plugins/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/callback_plugins/lucid.py -->
# sources/test-tools/kdevops/callback_plugins/lucid.py

Purpose: custom Ansible stdout callback plugin that provides compact static output, optional dynamic terminal display, and full timestamped logs independent of display verbosity.

Important APIs/types/functions: defines `CallbackModule(CallbackBase)` with `CALLBACK_TYPE = "stdout"` and `CALLBACK_NAME = "lucid"`. Configuration option `output_mode` supports `auto`, `static`, and `dynamic` via `callback_lucid` ini or `ANSIBLE_LUCID_OUTPUT_MODE`. Class state tracks running tasks, recent completed tasks, play hosts, pending play headers, dynamic display thread/event/locks, failed loop items, log path, and standard default callback options such as `display_ok_hosts`, `display_skipped_hosts`, `display_failed_stderr`, `check_mode_markers`, `show_custom_stats`, and `show_task_path_on_failure`.

Control flow: `set_options` caches options, detects interactivity, creates logging state, and starts the dynamic update thread when selected. Playbook/play/task callbacks create logs, defer static play banners until first task, suppress noisy empty arg-spec validation tasks, and update current task state. Runner callbacks route ok/failed/skipped/unreachable and async completions through `_handle_result`, which removes running state, logs full results, records recent completions, and either updates dynamic display or prints static lines. Include, notify, no-hosts, vars-prompt, retry, diff, loop-item, and handler hooks fill gaps in the default callback. Final stats stop the thread, clear dynamic display, print recap/custom stats/check-mode markers, and write a log footer.

State/persistence behavior: persistent output is a log file named `.ansible/logs/<playbook>-<timestamp>.log` when writable, otherwise under `~/.ansible/logs` or `/var/log/ansible`. Logs include task lines, commands, stdout/stderr/msg, exceptions, task paths for failures, and full cleaned structured results. Dynamic mode owns terminal cursor repainting via ANSI clear sequences and stops on failures to show static output. The plugin uses thread locks around task and output state.

Dependencies/integration: depends on Ansible callback APIs, `ansible.constants`, `ansible.context`, Python standard modules, terminal TTY behavior, and callback documentation fragments `default_callback` and `result_format_callback`. It is intended to be selected as Ansible's stdout callback in kdevops ansible configuration.

Risks/test signals: the file contains apparent syntax hazards in the viewed source, including a broken `_should_display_output` docstring area and duplicated `if task_path:` line, which should be verified by Python compilation before enabling. Dynamic output uses a background thread and direct `sys.stdout` writes, so prompt handling and failure freezes are important. Full logs intentionally collect maximum detail, so no-log redaction and `_clean_results` behavior are security-critical. Test signals include `python -m py_compile callback_plugins/lucid.py`, Ansible playbook runs in static and dynamic modes, loop failure display, async task cleanup, `--diff`, `--check`, `display_failed_stderr`, custom stats, and no-log redaction checks.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/callback_plugins/lucid.py -->
