# Group Research: subset-b-008300

This grouped report covers the requested audit-userspace source files. Each file section is bounded by the exact reconciliation markers used to split source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/configure.ac -->
# sources/security-integrity/audit-userspace/configure.ac

Purpose: Autoconf entry point for audit-userspace 4.1.5. It configures compiler, libtool, generated headers, run-state paths, optional language bindings, optional daemon/plugin features, architecture syscall table support, sanitizer support, and generated Makefiles.

Important APIs and build outputs: Defines `AUDIT_RUN_DIR`, feature-detection macros for kernel audit headers (`AUDIT_FEATURE_VERSION`, `AUDIT_STATUS_BACKLOG_WAIT_TIME`, `AUDIT_STATUS_BACKLOG_WAIT_TIME_ACTUAL`), libc functions (`posix_fallocate`, `signalfd`, `rawmemchr`, `faccessat`, `mallinfo2`, `close_range`), atomic fallback typedef macros, GCC attribute support probes, and automake conditionals such as `USE_PYTHON3`, `HAVE_GOLANG`, `ENABLE_LISTENER`, `ENABLE_ZOS_REMOTE`, `ENABLE_GSSAPI`, `ENABLE_EXPERIMENTAL`, `USE_ARM`, `USE_AARCH64`, `USE_RISCV`, `HAVE_ASAN`, `BUILD_STATIC`, and `ENABLE_LISTENER`.

Control flow: Initializes package metadata, compiler tools, libev macro state, and runstatedir defaults. It then probes headers/functions, chooses optional Python3 and Go bindings, validates SWIG when Python bindings are enabled, configures network listener and plugin families, checks LDAP for `zos-remote`, conditionally enables GSSAPI, warning flags, ASAN, processor table support, AppArmor, tcp_wrappers, io_uring, nftables/iptables selection, and libcap-ng. It ends by generating Makefiles and systemd/init templates including `init.d/augenrules`.

State and persistence: Configuration decisions persist into `config.h`, substituted Makefiles, `audit.pc`, and generated service/script files. The default runtime directory is forced to `/run/audit` when the user has not overridden `runstatedir`.

Dependencies and integration: Integrates with Autoconf, Automake, Libtool, kernel audit headers, libev, Python `python3-config`, SWIG, Go, OpenLDAP, GSSAPI/Kerberos, tcp_wrappers, libcap-ng, and many subdirectories. Architecture options directly control generated syscall lookup tables in `lib/Makefile.am`.

Risks: Build behavior depends heavily on host headers and optional libraries, so missing kernel definitions or stale headers can silently disable newer audit features. `--with-*` options differ between hard failure and warning paths. The `__attr_access` and `__attr_dealloc_free` probes compile snippets that rely on libc/compiler attribute support. Optional `tcp_wrappers` path handling accepts custom library flags, which needs careful quoting in packaging.

Test signals: Run `autoreconf -fi`, `./configure --help`, and configure matrices with/without Python, Go, LDAP, GSSAPI, libwrap, io_uring, and architecture options. Confirm generated `config.h`, `init.d/auditd.service`, `init.d/audit-rules.service`, `init.d/augenrules`, and `lib/audit.pc` contain expected substitutions.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/configure.ac -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/contrib/avc_snap -->
# sources/security-integrity/audit-userspace/contrib/avc_snap

Purpose: Legacy Python 2 audisp-style SELinux AVC analyzer that reads audit messages from stdin, groups records by audit event signature, and dispatches AVCs to setroubleshoot plugins.

Important APIs and types: Defines class `avc_snap` with `audit_list`, `cur_sig`, and loaded `plugins`. Uses Python modules `audit`, `avc`, `AuditMsg`, `syslog`, `select`, `struct`, and `setroubleshoot.signature.AVC`. Main methods are `is_avc`, `out`, `process`, and `run`.

Control flow: `run` waits on stdin with `select` for up to five seconds. When input arrives, it reads an `AuditMsg`, extracts type/body, and calls `process`. `process` splits the body, treats the first token as an event signature, flushes the previous event if the signature changes, and appends the remaining fields. `out` ignores non-AVC events and granted AVCs, translates denied AVC field lists via `avc.SERules`, builds an `AVC`, and calls plugin `analyze` and `report` until a plugin handles it. Timeouts flush pending grouped records.

State and persistence: State is in memory only and reset after every flush. Persistent effects come from setroubleshoot plugin reporting and syslog messages under the `avc_snap` ident.

Dependencies and integration: Intended to be launched by auditd/audisp as a stdin-fed plugin. It depends on obsolete Python 2 syntax, setroubleshoot libraries, SELinux AVC parsing, and audit message framing from `AuditMsg`.

Risks: Python 2 exception syntax makes it incompatible with Python 3. Event grouping assumes `data_list[0]` exists and is a stable signature. It drops granted AVCs. Broad exception handling logs but may hide plugin failures. If stdin feeds malformed messages, `struct.error` exits the daemon loop.

Test signals: Feed raw AVC audit streams into stdin and verify plugin reports, timeout flushing, signature-boundary flushing, syslog error handling, and ignoring of `granted` AVC records. Python 2 runtime availability is itself a deployment signal.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/contrib/avc_snap -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/contrib/libauplugin/Makefile -->
# sources/security-integrity/audit-userspace/contrib/libauplugin/Makefile

Purpose: Minimal standalone build recipe for the `auplugin-example` sample using installed audit libraries rather than the autotools tree.

Important APIs and targets: Defines `CFLAGS=-g -W -Wall -Wundef`, `LIBS=-lauplugin -lauparse -laudit`, `all` compiling `auplugin-example.c`, and `clean` removing the binary and object files.

Control flow: `make` invokes a single `gcc` command. `make clean` deletes generated local artifacts.

State and persistence: Persists only the compiled `auplugin-example` binary and any `*.o` files.

Dependencies and integration: Requires system headers/libraries for `libauplugin`, `libauparse`, and `libaudit` in the compiler's default search paths. It is a contrib example, not an installed automake target in this file.

Risks: No include/library path customization, no dependency tracking, no hardening flags, and no install target. It assumes library ABI compatibility with the source example.

Test signals: `make clean && make` should link successfully against installed audit libraries. Running the binary with raw audit records should exercise `auplugin-example.c`.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/contrib/libauplugin/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/contrib/libauplugin/auplugin-example.c -->
# sources/security-integrity/audit-userspace/contrib/libauplugin/auplugin-example.c

Purpose: C example showing how to implement an audit dispatcher plugin with `libauplugin`, delegating stdin queueing and event feeding to the helper library while using `libauparse` callbacks for event inspection.

Important APIs and functions: Uses `auplugin_init`, `auplugin_event_feed`, `auplugin_stop`, `auparse_goto_record_num`, `auparse_get_type`, `auparse_get_record_text`, `auparse_get_num_fields`, `auparse_get_timestamp`, `auparse_first_record`, `auparse_next_record`, `auparse_first_field`, `auparse_next_field`, and `audit_msg_type_to_name`. Local functions are `term_handler`, `hup_handler`, `reload_config`, `dump_whole_event`, `dump_whole_record`, `dump_fields_of_record`, and callback `handle_event`.

Control flow: `main` installs SIGHUP and SIGTERM handlers, initializes `libauplugin` on stdin fd 0 with a 128-event in-memory queue, then starts `auplugin_event_feed` with a one-second timer. `term_handler` only honors SIGTERM from the parent process and calls `auplugin_stop` so the feed loop exits. `handle_event` reloads config when requested and iterates all records in a completed event; it prints AVC fields, syscall records, and whole MAC status events.

State and persistence: Uses process globals `stop` and `hup` as signal state. The queue is in memory only. Output is demonstration stdout text; real plugins would normally write elsewhere because stdout is often `/dev/null` under auditd.

Dependencies and integration: Includes `<auplugin.h>` and expects auditd/audisp plugin stdin framing. It is functionally comparable to `contrib/plugin/audisp-example.c` but moves manual select/feed logic into `libauplugin`.

Risks: It is an example, so processing is synchronous and prints records directly. The callback does not check `cb_event_type`, so it assumes `auplugin_event_feed` calls it only for complete events or that non-ready callbacks are harmless. Parent-only SIGTERM handling avoids arbitrary termination but can surprise manual testing.

Test signals: Build via the contrib Makefile, feed `ausearch --raw` output, send SIGHUP to exercise reload state, send SIGTERM from the parent/dispatcher path, and verify stdout for `AUDIT_AVC`, `AUDIT_SYSCALL`, and `AUDIT_MAC_STATUS`.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/contrib/libauplugin/auplugin-example.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/contrib/libauplugin/auplugin-example.conf -->
# sources/security-integrity/audit-userspace/contrib/libauplugin/auplugin-example.conf

Purpose: Example audit plugin configuration for the `libauplugin` sample binary.

Important fields: `active = no`, `path = /sbin/auplugin-example`, `type = always`, `args = 1`, and `format = string`.

Control flow: No executable control flow; auditd/audisp reads this declarative file to decide whether to start the plugin, which binary to execute, and how to format events.

State and persistence: Persistent configuration under a plugin config directory when installed by an administrator. Default inactive state prevents accidental dispatch.

Dependencies and integration: Integrates with auditd plugin configuration semantics and the sample binary from `contrib/libauplugin`.

Risks: The path is hard-coded to `/sbin/auplugin-example`, which may not match distro layout. Enabling it without installing the binary or validating queue behavior can create auditd plugin errors.

Test signals: Place under an audit plugin directory, set `active = yes`, restart/reconfigure auditd, and confirm auditd starts the example and passes string-formatted events.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/contrib/libauplugin/auplugin-example.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/contrib/plugin/Makefile -->
# sources/security-integrity/audit-userspace/contrib/plugin/Makefile

Purpose: Minimal standalone build recipe for the older manual `audisp-example` plugin.

Important APIs and targets: Defines warning/debug `CFLAGS`, links with `-lauparse -laudit`, compiles `audisp-example.c`, and cleans the binary and object files.

Control flow: Single `gcc` invocation for `all`; simple file deletion for `clean`.

State and persistence: Produces the `audisp-example` executable in the contrib directory.

Dependencies and integration: Requires installed libaudit and libauparse development files. This is a contrib sample outside the main automake build.

Risks: No hardening, no dependency tracking, no include path control, and no installation handling. It may fail if local source headers differ from installed library headers.

Test signals: Run `make clean && make`, then feed raw audit logs to the executable and verify output from the manual event loop.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/contrib/plugin/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/contrib/plugin/audisp-example.c -->
# sources/security-integrity/audit-userspace/contrib/plugin/audisp-example.c

Purpose: Manual audit dispatcher plugin example using `libauparse` directly. It demonstrates stdin nonblocking reads, event aging, callback registration, signal handling, and basic record inspection.

Important APIs and functions: Uses `auparse_init(AUSOURCE_FEED)`, `auparse_set_eoe_timeout`, `auparse_add_callback`, `auparse_feed_has_data`, `auparse_feed_age_events`, `auparse_feed`, `auparse_flush_feed`, `auparse_destroy`, record/field iteration APIs, and `audit_msg_type_to_name`. Local functions mirror the libauplugin example: signal handlers, `reload_config`, `dump_whole_event`, `dump_whole_record`, `dump_fields_of_record`, and `handle_event`.

Control flow: `main` installs SIGHUP/SIGTERM handlers, sets stdin nonblocking, initializes auparse feed mode, and enters a loop. It waits indefinitely when no partial event exists, or waits one second when auparse has buffered data so aged events can be flushed. Read data is fed to auparse until EOF or a stop request. The callback ignores non-`AUPARSE_CB_EVENT_READY` notifications and branches on record types.

State and persistence: Globals `stop`, `hup`, and `au` hold runtime state. No durable state is stored. Demonstration output goes to stdout.

Dependencies and integration: Includes local `libaudit.h` and `auparse.h`; intended for auditd/audisp string format stdin. Comments warn that real plugins should add an internal queue to avoid backing up auditd and the kernel backlog.

Risks: This example manually manages nonblocking IO and event aging, so production copies can easily get queueing wrong. `stop` and `hup` are `volatile int` rather than `sig_atomic_t`. The read loop uses fixed `MAX_AUDIT_MESSAGE_LENGTH` buffers and stdout diagnostics unsuitable for daemon deployment.

Test signals: Build with the contrib Makefile, feed `ausearch --raw` output, test EOF flushing, timeout event aging, SIGHUP reload path, SIGTERM parent check, and callback output for AVC/syscall/MAC status records.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/contrib/plugin/audisp-example.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/contrib/plugin/audisp-example.conf -->
# sources/security-integrity/audit-userspace/contrib/plugin/audisp-example.conf

Purpose: Example audit plugin configuration for the manual `audisp-example` sample.

Important fields: `active = no`, `path = /sbin/audisp-example`, `type = always`, `args = 1`, and `format = string`.

Control flow: Declarative only; auditd plugin manager reads it to decide plugin activation and event delivery format.

State and persistence: Persistent plugin config if installed. Inactive by default to prevent accidental sample execution.

Dependencies and integration: Integrates with auditd plugin config syntax and the sample binary built from `contrib/plugin/audisp-example.c`.

Risks: Comment text calls it an example syslog plugin even though the code prints to stdout. The hard-coded path may be wrong for current systems, and enabling it without the binary causes auditd plugin errors.

Test signals: Enable in a test audit plugin directory, reconfigure auditd, and confirm the sample starts and receives string events.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/contrib/plugin/audisp-example.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/docs/Makefile.am -->
# sources/security-integrity/audit-userspace/docs/Makefile.am

Purpose: Automake manifest for audit-userspace manual pages and documentation tests.

Important variables and targets: `EXTRA_DIST=$(man_MANS)`, `dist_check_SCRIPTS=check-manpages.sh`, `TESTS=check-manpages.sh`, and a long `man_MANS` list covering libaudit, auparse, auplugin, auditd, auditctl, ausearch, aureport, augenrules, config files, and plugin man pages.

Control flow: Automake installs listed man pages and includes them in distribution archives. `make check` runs `check-manpages.sh` over manpage sources.

State and persistence: No runtime state; controls install/distribution artifacts and test registration.

Dependencies and integration: Integrates with automake, generated `docs/Makefile` from `configure.ac`, and manpage test script. The manpage list should track exported APIs and installed binaries.

Risks: Missing a new public function from `man_MANS` can ship undocumented APIs. Stale entries can break dist or install. The list is manually maintained and sensitive to filename spelling.

Test signals: `make -C docs check`, `make distcheck`, and package install file lists should confirm every listed page exists and formats cleanly.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/docs/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/docs/check-manpages.sh -->
# sources/security-integrity/audit-userspace/docs/check-manpages.sh

Purpose: POSIX shell test that validates every local manpage source with formatter warnings enabled.

Important behavior: Honors `MAN` and `srcdir` environment variables. Skips with exit 77 if `man` is unavailable, `C.UTF-8` locale is unavailable, or the `man` command lacks `--warnings`. For each `*.[0-9]` page it runs `man --warnings -E UTF-8 -l -Tutf8 -Z` with `LC_ALL=C.UTF-8`, empty `MANROFFSEQ`, and fixed `MANWIDTH=80`.

Control flow: Resolves `srcdir`, performs skip checks, loops over manpage files, captures stderr and exit status, prints failures, errors if no pages were found, and exits with aggregate failure state.

State and persistence: No persistent state. It only reads manpage files and emits diagnostics.

Dependencies and integration: Registered as an automake `TESTS` entry by `docs/Makefile.am`. Depends on a GNU/man-db style `man` with `--warnings`.

Risks: Environments without `C.UTF-8` or compatible `man` skip coverage. It treats any stderr as failure because `man` may return success despite formatter warnings. Shell glob `*.[0-9]` covers one-digit sections only, matching this tree's convention.

Test signals: Run directly from `docs` and from a VPATH build with `srcdir` set. Inject a malformed roff page to verify stderr causes failure.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/docs/check-manpages.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/gcc-attributes.h -->
# sources/security-integrity/audit-userspace/gcc-attributes.h

Purpose: Private compatibility header that supplies fallback definitions for GCC/glibc function-attribute macros and branch prediction helpers when libc headers do not provide them.

Important macros: Defines `__has_attribute`, `__attr_access`, `__attribute_malloc__`, `__attr_dealloc`, `__attr_dealloc_free`, `__attribute_const__`, `__attribute_pure__`, `__nonnull`, `__wur`, `likely`, and `unlikely` if missing.

Control flow: Preprocessor-only header guarded by `AUDIT_GCC_ATTRIBUTES_H`. It conditionally defines macros to no-ops or `__builtin_expect` expressions.

State and persistence: No state. Affects compile-time diagnostics, analyzer annotations, and optimization hints.

Dependencies and integration: Intended for internal sources that need portability across glibc and non-glibc libc implementations such as musl. Comments explicitly prohibit including it from public API headers (`audit-records.h`, `audit_logging.h`, `auparse-defs.h`, `auparse.h`, `auplugin.h`, `libaudit.h`) because it is not shipped.

Risks: If public headers accidentally depend on this private file, installed development packages break. No-op fallbacks reduce static analyzer coverage on platforms without native attributes. `likely`/`unlikely` assume GCC-compatible builtins.

Test signals: Build on glibc and musl-like environments, confirm public headers compile standalone after installation, and run compiler warning tests for attribute probes in `configure.ac`.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/gcc-attributes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/init.d/Makefile.am -->
# sources/security-integrity/audit-userspace/init.d/Makefile.am

Purpose: Automake rules for auditd system integration files: systemd units, default configs, tmpfiles config, augenrules script, bash completion, and optional legacy action scripts.

Important variables and targets: Installs `auditd.conf` and `audit-stop.rules` into `$(sysconfdir)/audit`, builds `auditd.service`, `audit-rules.service`, and `augenrules` from templates, installs units under `$(prefix)/lib/systemd/system`, installs `libaudit.conf` directly under `$(sysconfdir)`, and installs tmpfiles config as `$(prefix)/lib/tmpfiles.d/audit.conf`. Conditional `INSTALL_LEGACY_ACTIONS` installs rotate/resume/reload/state/stop/restart/condrestart scripts.

Control flow: Pattern rule substitutes `@runstatedir@`, `@sbindir@`, and `@sysconfdir@` into service templates. `install-data-hook` creates config/tmpfiles destinations. `install-exec-hook` creates unit and bash completion directories, installs generated units, chmods `augenrules`, and optionally installs legacy actions. `uninstall-hook` removes installed artifacts.

State and persistence: Persists system config files, generated systemd units, tmpfiles declaration, bash completion, and optional legacy scripts into target filesystem during install.

Dependencies and integration: Driven by `configure.ac` substitutions and automake conditionals. Integrates with systemd, tmpfiles.d, auditd config layout, and package install/uninstall steps.

Risks: Unit directory is fixed to `$(prefix)/lib/systemd/system`, which can differ by distro. `libaudit.conf` is installed with mode 640 and path `${sysconfdir}` because libaudit expects `/etc/libaudit.conf`. Uninstall removes files without `-f`, so partial installs may error. Packaging must preserve config semantics and not overwrite administrator changes carelessly.

Test signals: `make -C init.d install DESTDIR=...`, inspect generated substitutions, file modes, install paths, and `make uninstall` behavior. Confirm `INSTALL_LEGACY_ACTIONS` toggles legacy scripts.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/init.d/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/init.d/audit-rules.service.in -->
# sources/security-integrity/audit-userspace/init.d/audit-rules.service.in

Purpose: systemd oneshot unit template that loads audit rules during boot or service start via `augenrules --load`.

Important fields: `ConditionKernelCommandLine=!audit=0` and `!audit=off`, `DefaultDependencies=no`, `After=local-fs.target systemd-tmpfiles-setup.service`, `Type=oneshot`, `ExecStart=@sbindir@/augenrules --load`, and optional commented `ExecStopPost=@sbindir@/auditctl -R @sysconfdir@/audit/audit-stop.rules`.

Control flow: systemd runs the unit once after local filesystems and tmpfiles setup, ensuring `/tmp` and rule files are available. It is wanted by `multi-user.target`.

State and persistence: Loads kernel audit rules and may optionally clear/disable rules on stop if the admin enables `ExecStopPost`.

Dependencies and integration: Template substitutions come from `init.d/Makefile.am`. It is wanted by `auditd.service` and integrates with `augenrules`, `auditctl`, `/etc/audit/rules.d`, and `/etc/audit/audit.rules`.

Risks: Security sandboxing is deliberately disabled because rule loading needs broad access. If rules are invalid, the unit can fail while `auditd.service` only has a weak `Wants` dependency. Optional stop behavior can remove audit coverage if enabled without policy intent.

Test signals: `systemd-analyze verify` on generated unit, boot/start ordering checks, `systemctl start audit-rules.service`, and inspection of loaded `auditctl -l` rules.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/init.d/audit-rules.service.in -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/init.d/audit-stop.rules -->
# sources/security-integrity/audit-userspace/init.d/audit-stop.rules

Purpose: Optional auditctl rules file used when administrators want audit rules cleared as auditd stops.

Important commands: `-e 0` disables auditing; `-D` deletes all audit rules.

Control flow: No script control flow. If referenced by the commented `ExecStopPost` in `audit-rules.service.in` or manually loaded with `auditctl -R`, auditctl applies commands in order.

State and persistence: Mutates kernel audit state by disabling auditing and deleting rules. Does not persist state beyond kernel runtime except by being installed as a config file.

Dependencies and integration: Installed with `auditd.conf` under `/etc/audit` by `init.d/Makefile.am`. Intended for `auditctl`.

Risks: Loading this file removes audit coverage. It should remain opt-in and protected by root-owned config permissions.

Test signals: In a controlled VM, run `auditctl -R audit-stop.rules` and confirm `auditctl -s` shows disabled state and `auditctl -l` is empty.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/init.d/audit-stop.rules -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/init.d/audit-tmpfiles.conf -->
# sources/security-integrity/audit-userspace/init.d/audit-tmpfiles.conf

Purpose: systemd-tmpfiles declaration that creates the audit log directory.

Important entry: `d /var/log/audit 0700 root root - -` creates `/var/log/audit` as a root-owned directory with mode 0700.

Control flow: Declarative only; systemd-tmpfiles processes it during boot or manual tmpfiles creation.

State and persistence: Ensures persistent log directory exists with restrictive permissions.

Dependencies and integration: Installed as `audit.conf` in the tmpfiles.d directory by `init.d/Makefile.am`. `auditd.service.in` and `audit-rules.service.in` order after `systemd-tmpfiles-setup.service`.

Risks: Incorrect permissions would expose audit logs. The hard-coded `/var/log/audit` must match `auditd.conf` `log_file` default and packaging expectations.

Test signals: `systemd-tmpfiles --create audit.conf`, then check directory ownership/mode and auditd log write success.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/init.d/audit-tmpfiles.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/init.d/auditd.conf -->
# sources/security-integrity/audit-userspace/init.d/auditd.conf

Purpose: Default audit daemon configuration controlling local logging, log rotation, disk-space actions, network listener defaults, plugin queueing, and event timeout behavior.

Important settings: Enables local events and logs, writes `/var/log/audit/audit.log`, uses `ENRICHED` format, async incremental flushing, 8 MB log rotation with 5 logs, root log group, disk thresholds/actions, `use_libwrap = yes`, TCP listener placeholders, `transport = TCP`, `distribute_network = no`, `q_depth = 2000`, `overflow_action = SYSLOG`, `plugin_dir = /etc/audit/plugins.d`, and `end_of_event_timeout = 2`.

Control flow: Declarative config consumed by auditd at startup/reconfigure. Values drive internal daemon behavior for logging, rotation, queue overflow, network listener, and plugin dispatch.

State and persistence: Persistent system policy under `/etc/audit/auditd.conf` when installed. Controls audit log files and daemon runtime behavior.

Dependencies and integration: Used by `auditd`, systemd service, plugin directory, libwrap support from configure/build, optional Kerberos key file, and log directory created by tmpfiles.

Risks: Defaults like `disk_full_action = SUSPEND` and `disk_error_action = SUSPEND` can stop logging under storage failure. Network listener options are mostly commented but must be secured if enabled. `use_libwrap = yes` is meaningful only when built with tcp_wrappers. Queue depth and overflow action shape event loss behavior.

Test signals: `auditd -f` config parse, `auditd -s` reconfigure, log rotation tests, disk threshold simulations, plugin queue load tests, and listener startup tests when TCP options are enabled.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/init.d/auditd.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/init.d/auditd.service.in -->
# sources/security-integrity/audit-userspace/init.d/auditd.service.in

Purpose: systemd service template for the audit daemon with boot ordering, restart policy, pid file, and selective hardening.

Important fields: Conditions skip service when kernel command line disables audit. `DefaultDependencies=no`, weak `Wants=audit-rules.service`, `After=local-fs.target systemd-tmpfiles-setup.service`, `Before=sysinit.target shutdown.target audit-rules.service`, `Conflicts=shutdown.target`, `RefuseManualStop=yes`, `Type=forking`, `PIDFile=@runstatedir@/audit/auditd.pid`, `ExecStart=@sbindir@/auditd`, `Restart=on-failure`, `KillMode=mixed`, and `RestartPreventExitStatus=2 4 6`.

Control flow: systemd starts auditd early after local filesystem and tmpfiles setup, before sysinit and rule loading. Remote logging comments describe override requirements to avoid ordering cycles. Restart policy avoids intentional exits.

State and persistence: Manages the auditd daemon process and pid file under the configured runstatedir. Persistent audit logs and rules are controlled by related config files.

Dependencies and integration: Generated by `init.d/Makefile.am`; integrates with systemd, `audit-rules.service`, tmpfiles, `auditd.conf`, and auditd exit-code semantics.

Risks: Early boot ordering is sensitive, especially with remote logging and `systemd-update-utmp` cycles. `RefuseManualStop=yes` protects audit continuity but can surprise administrators. Hardening settings avoid some restrictions because audit rules may target kernel/module/control paths.

Test signals: `systemd-analyze verify`, boot ordering validation, restart behavior for known auditd exit statuses, pid file creation under `@runstatedir@/audit`, and remote logging override tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/init.d/auditd.service.in -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/init.d/augenrules.in -->
# sources/security-integrity/audit-userspace/init.d/augenrules.in

Purpose: Shell utility that concatenates `/etc/audit/rules.d/*.rules` into `/etc/audit/audit.rules`, normalizes special directives, optionally checks for changes, and optionally loads rules with auditctl.

Important variables and functions: `DestinationFile=/etc/audit/audit.rules`, `SourceRulesDir=/etc/audit/rules.d`, `TmpRules=$(mktemp /tmp/aurules.XXXXXXXX)`, `auditctl_bin=@sbindir@/auditctl`, `try_load`, and `check_immutable`.

Control flow: Parses `--check` and `--load`. Verifies source rules directory, creates a restrictive temporary file under `umask 0137`, concatenates version-sorted `.rules` files, strips blank/comment lines, normalizes CR endings, and uses awk to move the last bare `-D` to the first output line, last `-b` second, last `-f` third, and last `-e` last. It compares the temporary rules with destination, exits unchanged when identical, reports change-only mode for `--check`, refuses modifications when audit is immutable (`enabled 2`), backs up existing destination to `.prev`, copies the new file, chmods 0640, restorecons if available, and optionally loads it.

State and persistence: Writes `/etc/audit/audit.rules`, creates `/etc/audit/audit.rules.prev`, and may mutate kernel audit rules through `auditctl -R`.

Dependencies and integration: Generated with substituted auditctl path by configure/make. Used by `audit-rules.service.in` and administrators. Depends on `awk`, `ls -1v`, `grep`, `cmp`, `mktemp`, `restorecon` optionally, and auditctl.

Risks: It iterates `for rules in $(ls ... | grep ...)`, so filenames with whitespace are unsafe. `mktemp` under `/tmp` is mitigated by `mktemp` and restrictive `umask`, but MLS systems require `restorecon` after copy. Immutable mode causes a no-change exit without modifying rules, which is correct but can confuse automation. Rule ordering semantics depend on the awk normalization.

Test signals: Unit tests with multiple `.rules` files covering comments, CRLF, repeated `-D`, `-b`, `-f`, and `-e`; `--check` changed/unchanged behavior; immutable audit state; SELinux label restoration; and `--load` exit status propagation.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/init.d/augenrules.in -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/init.d/libaudit.conf -->
# sources/security-integrity/audit-userspace/init.d/libaudit.conf

Purpose: Default libaudit tunables file, currently used only for `failure_action`.

Important setting: `failure_action = ignore`, with documented allowed values `log`, `ignore`, and `terminate`.

Control flow: Declarative only; parsed by `lib/libaudit.c` through `get_auditfail_action` and `load_libaudit_config`.

State and persistence: Persistent system-level libaudit behavior under `/etc/libaudit.conf`.

Dependencies and integration: Installed by `init.d/Makefile.am` to `${sysconfdir}`. Parsed with strict ownership/permission checks in libaudit.

Risks: File must be root-owned and not writable by group/others or libaudit rejects it. Only one tunable is accepted; unknown keys are errors.

Test signals: Call `get_auditfail_action` with valid, missing, permission-bad, and unknown-key config files; validate default ignore behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/init.d/libaudit.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/lib/Makefile.am -->
# sources/security-integrity/audit-userspace/lib/Makefile.am

Purpose: Automake build rules for `libaudit.la`, public headers, pkg-config metadata, generated lookup tables, and build-host table generator programs.

Important APIs and targets: Builds `libaudit.la` from `libaudit.c`, `netlink.c`, `lookup_table.c`, `audit_logging.c`, `deprecated.c`, and private headers. Installs `libaudit.h`, `audit_logging.h`, and `audit-records.h`. Generates `actiontabs.h`, `errtabs.h`, `fieldtabs.h`, `flagtabs.h`, `fstypetabs.h`, `ftypetabs.h`, syscall architecture tables, machine/message/op/perm/io_uring tables using `gen_tables.c` and `gen_tables.h`.

Control flow: `BUILT_SOURCES` drives generated headers before library compilation. Each generator target compiles with `CC_FOR_BUILD` and build flags, includes a specific `_table.h` input through `TABLE_H`, and invokes the generator with options such as `--lowercase`, `--uppercase`, `--duplicate-ints`, `--i2s`, `--s2i`, or `--i2s-transtab`. Architecture table generation is conditional on `USE_ARM`, `USE_AARCH64`, and `USE_RISCV`.

State and persistence: Produces generated header files consumed by `lookup_table.c` and libaudit translation APIs. Installs library, headers, and `audit.pc`.

Dependencies and integration: Depends on configure conditionals, libcap-ng link flags, common library, kernel headers, and generated table inputs. Cross-compilation support depends on `AX_PROG_CC_FOR_BUILD`.

Risks: Generator inputs and flags define public translation behavior, so stale tables or wrong conditional inclusion causes incorrect syscall/name mapping. Cross builds need build-host generator binaries, not target binaries. `VERSION_INFO` controls libtool ABI versioning and must be handled carefully.

Test signals: `make -C lib`, cross-build generation checks, `make distcheck`, translation API unit tests, and diffing generated headers after table updates.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/lib/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/lib/aarch64_table.h -->
# sources/security-integrity/audit-userspace/lib/aarch64_table.h

Purpose: Source table mapping AArch64 Linux syscall numbers to names for generated libaudit lookup code.

Important structure: A sequence of `_S(number, "name")` entries from low-number syscalls such as `io_setup`, `setxattr`, and `openat` through newer syscalls such as `landlock_*`, `mseal`, `setxattrat`, `open_tree_attr`, `file_getattr`, `listns`, and `rseq_slice_yield`.

Control flow: No runtime control flow. `lib/Makefile.am` builds `gen_aarch64_tables_h` with `TABLE_H="aarch64_table.h"` and emits `aarch64_tables.h` with lower-case string-to-int and int-to-string helpers.

State and persistence: Static source data that persists into generated headers and ultimately libaudit syscall translation APIs.

Dependencies and integration: Enabled only when configured with AArch64 support. Used by `audit_name_to_syscall`, `audit_syscall_to_name`, rule parsing for `arch=aarch64`, and permission-to-syscall expansion.

Risks: Syscall numbering must match the kernel ABI. Missing or wrong entries break audit rule parsing and user display for AArch64. Architecture-specific syscall absence matters because generic permission syscall lists may include names unavailable on this architecture.

Test signals: Generated table builds, `audit_name_to_syscall("openat2", MACH_AARCH64)`, reverse lookup checks, and comparison with current kernel syscall tables.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/lib/aarch64_table.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/lib/actiontab.h -->
# sources/security-integrity/audit-userspace/lib/actiontab.h

Purpose: Lookup input mapping audit rule actions to textual names.

Important entries: `_S(AUDIT_NEVER, "never")`, `_S(AUDIT_POSSIBLE, "possible")`, and `_S(AUDIT_ALWAYS, "always")`.

Control flow: No runtime logic; consumed by `gen_tables.c` to generate `actiontabs.h`.

State and persistence: Static mapping compiled into libaudit translation functions.

Dependencies and integration: Depends on kernel audit constants from `<linux/audit.h>`. Used by `audit_name_to_action` and `audit_action_to_name` for rule parsing/display.

Risks: The deprecated or less-common `possible` action must remain if kernel/user ABI still exposes it. Text changes affect CLI compatibility.

Test signals: Translation tests for all three action strings and constants, including case behavior from generator flags.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/lib/actiontab.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/lib/arm_table.h -->
# sources/security-integrity/audit-userspace/lib/arm_table.h

Purpose: Source table mapping 32-bit ARM EABI syscall numbers to names for generated libaudit lookup code.

Important structure: `_S(number, "name")` entries beginning with legacy syscalls (`restart_syscall`, `exit`, `fork`, `read`, `open`) and extending through modern syscalls (`clone3`, `openat2`, `landlock_*`, `futex_*`, `mseal`, `setxattrat`, `file_getattr`, `listns`, `rseq_slice_yield`). Some numbers are absent where the ARM ABI has gaps or unavailable calls.

Control flow: No runtime control flow; `gen_arm_tables_h` generates `arm_tables.h` when `USE_ARM` is enabled.

State and persistence: Static ABI mapping used by libaudit rule parsing and display.

Dependencies and integration: Enabled by `--with-arm`. Integrated with `audit_determine_machine`, `audit_machine_to_elf`, and syscall name translation for `MACH_ARM`.

Risks: ARM syscall availability differs from AArch64 and x86; stale entries can create invalid rules or poor diagnostics. Gaps must be preserved accurately rather than compressed.

Test signals: Generated table compile, name/number round trips for representative old and new syscalls, and comparison with kernel ARM syscall headers.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/lib/arm_table.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/lib/audit-records.h -->
# sources/security-integrity/audit-userspace/lib/audit-records.h

Purpose: Public header containing audit record type constants and fallback definitions for kernel/user-space audit message ranges.

Important constants: Defines user message ranges (`AUDIT_FIRST_USER_MSG`, `AUDIT_LAST_USER_MSG`), daemon messages, event ranges, SELinux, AppArmor, crypto, anomaly, anomaly response, LSPP, virtualization, and newer kernel record fallbacks such as `AUDIT_BPF`, `AUDIT_EVENT_LISTENER`, `AUDIT_URINGOP`, `AUDIT_OPENAT2`, `AUDIT_DM_CTRL`, `AUDIT_DM_EVENT`, and `AUDIT_ANOM_CREAT`.

Control flow: Preprocessor-only public ABI header with `extern "C"` guards. Uses `#ifndef` around newer kernel constants so system headers can provide canonical values.

State and persistence: No runtime state. It persists compile-time ABI for applications including libaudit headers.

Dependencies and integration: Includes `<linux/audit.h>` and is included by `audit_logging.h` and user applications. `libaudit.h` notes that record type definitions moved here as of audit 4.0.

Risks: Public header stability is critical. Wrong fallback numeric values break interoperability with kernel audit records and logs. It must not include private `gcc-attributes.h` because it is installed.

Test signals: Public header standalone compile in C and C++, comparison against current kernel audit constants, and application builds using `AUDIT_USER_*` and newer fallback constants.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/lib/audit-records.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/lib/audit.pc.in -->
# sources/security-integrity/audit-userspace/lib/audit.pc.in

Purpose: pkg-config template for applications linking against libaudit.

Important fields: Substitutes `prefix`, `exec_prefix`, `libdir`, `includedir`, `Version`, `Libs=-L${libdir} -laudit`, `Libs.private=@CAPNG_LDADD@`, `Cflags=-I${includedir}`, and `Requires.private=@CAPNG_PKG@`.

Control flow: Declarative template processed by configure into `audit.pc`.

State and persistence: Installed pkg-config metadata under `$(libdir)/pkgconfig`.

Dependencies and integration: Reflects libcap-ng private dependencies discovered by configure and consumed by downstream builds using `pkg-config --libs audit`.

Risks: Incorrect private deps break static linking. Incorrect include/lib paths break downstream builds.

Test signals: `pkg-config --cflags --libs audit`, `pkg-config --static --libs audit`, and downstream compile/link smoke tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/lib/audit.pc.in -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/lib/audit_logging.c -->
# sources/security-integrity/audit-userspace/lib/audit_logging.c

Purpose: Implements public helper APIs for formatting and sending common user-space audit records: generic user messages, command messages, account changes, SELinux AVC/user-role changes, and safe audit value encoding.

Important APIs and functions: Public functions include `audit_value_needs_encoding`, `audit_encode_value`, `audit_encode_nv_string`, `audit_log_user_message`, `audit_log_user_comm_message`, `audit_log_acct_message`, `audit_log_user_avc_message`, `audit_log_semanage_message`, and `audit_log_user_command`. Internal helpers resolve hostnames, determine executable path, command name, tty, and local hostname.

Control flow: Encoding helpers decide whether values need hex encoding when they contain quotes, control/space characters, or non-printable bytes. Logging functions assemble bounded `MAX_AUDIT_MESSAGE_LENGTH` records with standard key/value fields, derive missing address/tty/exe/comm/cwd values from the local process, and call `audit_send_user_message`. AVC logging has a special `-EPERM` path that syslogs instead of failing when the process cannot write audit records.

State and persistence: Uses static cached executable-name buffers and a cached hostname. Persistent effects are audit netlink messages and possible syslog fallback/error messages. It reads `/proc/self/exe`, `/proc/self/comm`, tty metadata, current working directory, and resolver state.

Dependencies and integration: Depends on `libaudit.h`, `private.h`, netlink send APIs from libaudit/deprecated path, libc resolver APIs, `/proc`, syslog, and audit record constants. These helpers are exported through `audit_logging.h` and included by `libaudit.h`.

Risks: Logging format is ABI-like because parsers consume key/value fields. Caller-provided strings must be encoded consistently with kernel audit conventions. Static caches are not fully thread-specific. Hostname resolution can block and logs resolver errors. `strncat` into `addrbuf` assumes initialized empty buffer and truncates silently.

Test signals: Unit tests for encoding/quoting, NULL and empty input handling, oversized command trimming, cwd encoding, tty validation, audit send failure handling, and golden audit record strings for each public logging function.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/lib/audit_logging.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/lib/audit_logging.h -->
# sources/security-integrity/audit-userspace/lib/audit_logging.h

Purpose: Public header for libaudit connection lifecycle and standardized audit logging helper APIs.

Important declarations: Declares `audit_open`, `audit_close`, value encoding helpers, `audit_encode_nv_string` with deallocation annotation, and message logging functions for generic user messages, command messages, account changes, user AVCs, SELinux management, and user commands.

Control flow: Header-only declarations with C++ linkage guards and fallback attribute macro definitions.

State and persistence: No state itself. Declared functions send persistent audit records to the kernel and may log errors.

Dependencies and integration: Includes `<features.h>`, `<sys/types.h>`, and `<audit-records.h>`. Included by `libaudit.h` and installed as a public API header.

Risks: Public ABI and source compatibility constraints are high. Attribute macros must be safe on non-glibc systems. The header must remain self-contained after installation.

Test signals: C and C++ compile tests including only `audit_logging.h`, ABI symbol checks, and static analyzer validation for annotated buffer/deallocation functions.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/lib/audit_logging.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/lib/deprecated.c -->
# sources/security-integrity/audit-userspace/lib/deprecated.c

Purpose: Holds compatibility APIs that are deprecated but still exported, currently `audit_send_user_message`.

Important API: `audit_send_user_message(int fd, int type, hide_t hide_error, const char *message)` sends a user-space audit message with compatibility error handling.

Control flow: Calls `audit_send` with a NUL-terminated message length. Returns success-like `0` for `-ECONNREFUSED` to tolerate kernels built without audit. Returns `0` for hidden `-EPERM` when the process lacks audit write capability. On `-EINVAL`, retries one time as legacy `AUDIT_USER` for user message types in the first user message range. Otherwise returns the audit send result.

State and persistence: No internal state. Sends audit netlink records when successful.

Dependencies and integration: Depends on `audit_send`, capability helpers, audit record ranges, and `hide_t` from private headers. Used by `audit_logging.c`.

Risks: Compatibility behavior intentionally hides some failures, which is useful for unprivileged applications but can mask audit delivery issues. The fallback to `AUDIT_USER` is limited to older kernels and first-range user messages.

Test signals: Mock `audit_send` results for success, `ECONNREFUSED`, hidden/non-hidden `EPERM`, `EINVAL` retry, and non-user message `EINVAL`.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/lib/deprecated.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/lib/dso.h -->
# sources/security-integrity/audit-userspace/lib/dso.h

Purpose: Private helper header for controlling symbol visibility inside the shared library.

Important macros: Defines `AUDIT_HIDDEN_START` as `_Pragma("GCC visibility push(hidden)")` and `AUDIT_HIDDEN_END` as `_Pragma("GCC visibility pop")` if not already defined.

Control flow: Preprocessor-only.

State and persistence: No state. Affects compiled shared object symbol visibility.

Dependencies and integration: Used by internal libaudit sources/headers to hide implementation details from the public ABI.

Risks: Incorrect placement can hide intended public symbols or expose internal symbols. Assumes GCC-compatible pragma support.

Test signals: Inspect `nm -D`/ABI symbol lists and compile with compilers used by supported platforms.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/lib/dso.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/lib/errormsg.h -->
# sources/security-integrity/audit-userspace/lib/errormsg.h

Purpose: Defines internal libaudit rule-parser error numbers and printable error message metadata.

Important types and constants: `struct msg_tab` maps error keys to output positioning and message text. `EAU_*` constants cover missing operations, unknown fields/architectures/message types, unsupported filters/features, string length problems, incompatible comparisons, and permission syscall expansion failures. `err_msgtab[]` maps negative error values to diagnostics used by `audit_number_to_errmsg`.

Control flow: Header data is compiled when `NO_TABLES` is not defined. `audit_number_to_errmsg` in `libaudit.c` scans this table and formats messages according to `position`.

State and persistence: Static in-process diagnostic table only.

Dependencies and integration: Tightly coupled to return values from `audit_rule_fieldpair_data`, `audit_rule_interfield_comp_data`, and related parser helpers.

Risks: Error code numbers are reused by callers and diagnostics; comments mark deprecated holes that must not be reused. Missing entries produce silent no-output behavior in `audit_number_to_errmsg`.

Test signals: Parser negative-path tests that assert specific `EAU_*` return values and expected stderr from `audit_number_to_errmsg`.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/lib/errormsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/lib/errtab.h -->
# sources/security-integrity/audit-userspace/lib/errtab.h

Purpose: Lookup input mapping errno constants to symbolic names for audit rule parsing and display.

Important entries: Covers generic Linux errno-base and errno values from `EPERM` through `EHWPOISON`, including duplicate aliases such as `EWOULDBLOCK` and `EDEADLOCK`.

Control flow: No runtime control flow; `gen_errtabs_h` generates uppercase string-to-int and int-to-string helpers with duplicate integer support.

State and persistence: Static mapping compiled into libaudit.

Dependencies and integration: Depends on system errno constants from headers. Used by `audit_name_to_errno`, `audit_errno_to_name`, and `AUDIT_EXIT` field parsing.

Risks: Errno numeric values can vary on some architectures. The comment notes generic asm headers are the source, so portability must be verified. Duplicate aliases need `--duplicate-ints` or generation aborts.

Test signals: Round-trip tests for common errnos and aliases, and architecture build checks.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/lib/errtab.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/lib/fieldtab.h -->
# sources/security-integrity/audit-userspace/lib/fieldtab.h

Purpose: Lookup input mapping audit rule field constants to command-line/textual field names.

Important entries: Includes process/user/group fields (`pid`, `uid`, `auid`, `loginuid`), subject/object SELinux fields, session, device/inode/exit/success, watch/path/dir/perm/filetype/fstype, interfield compare marker, syscall args `a0`-`a3`, `key`, `exe`, and `saddr_fam`.

Control flow: No runtime logic; generated into `fieldtabs.h` with lower-case string-to-int and int-to-string helpers and duplicate-int support. Duplicate `AUDIT_LOGINUID` maps both `auid` and `loginuid`.

State and persistence: Static mapping used by libaudit rule parser/display.

Dependencies and integration: Constants come from kernel audit headers. Used heavily by `audit_rule_fieldpair_data` and `audit_rule_interfield_comp_data`.

Risks: Text names are user-facing CLI syntax, so renaming breaks rule compatibility. Duplicate aliases must preserve preferred reverse mapping order.

Test signals: Parser tests for each field name, alias handling, and reverse display for duplicated fields.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/lib/fieldtab.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/lib/flagtab.h -->
# sources/security-integrity/audit-userspace/lib/flagtab.h

Purpose: Lookup input mapping audit filter list constants to textual names.

Important entries: `task`, `exit`, `user`, `exclude`, `filesystem`, and conditional `io_uring` when `WITH_IO_URING` is configured.

Control flow: Includes `config.h` to see `WITH_IO_URING`; generated into `flagtabs.h`.

State and persistence: Static mapping compiled into translation APIs.

Dependencies and integration: Used by `audit_name_to_flag` and `audit_flag_to_name`, and by rule parsing for filter lists. Conditional `AUDIT_FILTER_URING_EXIT` depends on io_uring support.

Risks: Build-time condition changes accepted rule syntax. Missing io_uring table support while kernel supports it may reject rules.

Test signals: Translation tests with and without `--with-io_uring`; parser tests for `filesystem` and `io_uring` filters.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/lib/flagtab.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/lib/fstypetab.h -->
# sources/security-integrity/audit-userspace/lib/fstypetab.h

Purpose: Lookup input mapping selected filesystem magic numbers to names for audit filesystem filters.

Important entries: `tracefs`, `debugfs`, `cgroup`, and `cgroup2` magic values from Linux `magic.h`.

Control flow: No runtime logic; generated into `fstypetabs.h` with lower-case lookup helpers.

State and persistence: Static mapping used when parsing/displaying `fstype` audit rule fields.

Dependencies and integration: Used by `audit_name_to_fstype`, `audit_fstype_to_name`, and `AUDIT_FSTYPE` handling in `audit_rule_fieldpair_data`. Requires kernel support for filesystem filter feature bits.

Risks: Small explicit table means unsupported filesystem names are rejected unless numeric values are used. Magic values must stay in sync with Linux headers.

Test signals: Parse `fstype=tracefs` and `fstype=cgroup2`, reverse lookups, and feature-gated filesystem filter tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/lib/fstypetab.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/lib/ftypetab.h -->
# sources/security-integrity/audit-userspace/lib/ftypetab.h

Purpose: Lookup input mapping POSIX file type mode bits to audit file type names.

Important entries: `socket`, `link`, `file`, `block`, `dir`, `character`, and `fifo` mapped from `S_IF*` constants.

Control flow: No runtime logic; generated into `ftypetabs.h`.

State and persistence: Static mapping compiled into libaudit.

Dependencies and integration: Used by `audit_name_to_ftype`, `audit_ftype_to_name`, and `AUDIT_FILETYPE` rule parsing.

Risks: Names are user-facing rule syntax. Constants must come from appropriate system stat headers through generator includes.

Test signals: Parse and reverse lookup all file types; validate `filetype` is accepted only for exit filters.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/lib/ftypetab.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/lib/gen_tables.c -->
# sources/security-integrity/audit-userspace/lib/gen_tables.c

Purpose: Build-time generator that converts `_S(value, "string")` mapping headers into compact C lookup tables and helper functions.

Important functions: `cmp_value_strings`, `cmp_value_vals`, `cmp_value_orig_index`, `output_strings`, `output_s2i`, `output_i2s`, `output_i2s_transtab`, and `main`. Options include `--i2s`, `--s2i`, `--i2s-transtab`, `--uppercase`, `--lowercase`, and `--duplicate-ints`.

Control flow: Includes the selected `TABLE_H` into a `values[]` array, records original indexes, sorts lexicographically for string tables, emits a packed NUL-separated string blob, optionally emits string-to-int binary-search tables with case normalization, optionally sorts by numeric value and emits either direct-index or binary-search int-to-string tables based on density, and optionally emits `struct transtab` arrays in original order.

State and persistence: No runtime state in the generator. Generated headers are persistent build artifacts and compiled into libaudit.

Dependencies and integration: Built as multiple `gen_*` programs by `lib/Makefile.am` with `CC_FOR_BUILD`. Depends on `gen_tables.h`, audit headers, auparse definitions, and platform constants included for table inputs.

Risks: Uses `assert` for input validation and aborts on duplicates unless allowed. Generated code assumes ASCII for case transforms. Direct table density decisions affect memory footprint. Bad table input breaks build or creates wrong translation behavior.

Test signals: Regenerate all table headers, compare deterministic output, test duplicate handling, case-insensitive lookups, direct versus bsearch generation, and cross-build use of build compiler.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/lib/gen_tables.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/lib/gen_tables.h -->
# sources/security-integrity/audit-userspace/lib/gen_tables.h

Purpose: Header emitted into/used by generated 32-bit lookup table code.

Important APIs and types: Defines ASCII helpers `GT_ISUPPER` and `GT_ISLOWER`, inline lookup functions `s2i__`, `i2s_direct__`, `i2s_bsearch__`, and `struct transtab`.

Control flow: `s2i__` performs binary search over sorted string offsets and integer values, reusing previously matched prefix lengths. `i2s_direct__` indexes a dense table by `v - min`. `i2s_bsearch__` binary-searches sorted integer tables.

State and persistence: Header-only helpers compiled into generated table consumers.

Dependencies and integration: Included by `gen_tables.c` output and by `gen_tables64.h` for 32-bit compatibility. Used indirectly by libaudit translation functions.

Risks: Functions use `ssize_t` but include only standard size headers here; consumers must compile in an environment where it is available. Binary search relies on generated sorted tables. Direct table offsets use `-1u` sentinel.

Test signals: Unit tests for successful/missing string lookups, dense and sparse int lookups, boundary min/max values, and alias behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/lib/gen_tables.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/lib/gen_tables64.c -->
# sources/security-integrity/audit-userspace/lib/gen_tables64.c

Purpose: 64-bit-capable variant of the lookup-table generator for mapping values that may exceed 32-bit `int`.

Important functions and options: Mirrors `gen_tables.c` and adds `use_64bit` plus `--64bit`. Emits `int64_t` value arrays and lookup functions when 64-bit mode is selected, otherwise emits 32-bit-compatible code with range warnings for out-of-range values.

Control flow: Parses generator options, sorts by string/value/original index, emits packed strings, emits s2i tables using either `s2i__` or `s2i_64__`, emits i2s direct tables only for manageable 64-bit ranges below 1024 entries and density threshold, otherwise emits bsearch tables, and emits 32-bit or 64-bit transtab structures.

State and persistence: Generates persistent C headers for build artifacts; no runtime state beyond local generator flags.

Dependencies and integration: Includes `gen_tables64.h`, `libaudit.h`, `auparse-defs.h`, platform constants, and inttypes support. It is listed in `EXTRA_DIST` in `lib/Makefile.am`; specific Makefile rules in this subset mostly use the 32-bit generator.

Risks: 64-bit direct table generation must avoid enormous sparse arrays, hence the additional range cap. Mixed 32/64 modes can silently truncate if warnings are ignored. Generated headers may require `<inttypes.h>` when using `--64bit`.

Test signals: Generate tables with values around `INT_MAX`, negative 64-bit values, sparse huge ranges, duplicate aliases, and case-normalized string lookups.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/lib/gen_tables64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/lib/gen_tables64.h -->
# sources/security-integrity/audit-userspace/lib/gen_tables64.h

Purpose: Header providing 64-bit lookup helpers and compatibility with the original 32-bit generated table helpers.

Important APIs and types: Declares 32-bit helper prototypes, defines `s2i_64__`, `i2s_64_direct__`, `i2s_64_bsearch__`, `struct transtab64`, and includes `gen_tables.h` for original implementations.

Control flow: 64-bit string-to-int and int-to-string functions use binary/direct search patterns equivalent to `gen_tables.h`, with `int64_t` values. Direct lookup checks value range and casts index to `uint64_t`/`size_t` after bounds checks.

State and persistence: Header-only generated-code support; no mutable state.

Dependencies and integration: Used by `gen_tables64.c` output and includes `<stdint.h>` and `gen_tables.h`.

Risks: Contains inline prototypes before including `gen_tables.h`; compiler compatibility should be checked. Direct lookup guards must prevent overflow when converting `v - min` to an index. The comment has a typo ("Base on") but no functional effect.

Test signals: Compile generated 64-bit and 32-bit tables with strict warnings, exercise direct and bsearch lookup boundaries, and run static analysis for integer conversions.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/lib/gen_tables64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/lib/i386_table.h -->
# sources/security-integrity/audit-userspace/lib/i386_table.h

Purpose: Source table mapping i386 Linux syscall numbers to names for generated libaudit lookup code.

Important structure: `_S(number, "name")` entries include legacy i386 syscalls (`fork`, `oldstat`, `stty`, `gtty`, `mpx`) and modern additions up to `rseq_slice_yield`.

Control flow: No runtime control flow. `gen_i386_tables_h` generates `i386_tables.h` with duplicate-int support and lower-case name lookups.

State and persistence: Static syscall ABI mapping compiled into libaudit.

Dependencies and integration: Always part of `BUILT_SOURCES` in `lib/Makefile.am`. Used when parsing/displaying rules for `MACH_X86` or 32-bit `b32` rules on x86_64.

Risks: i386 has legacy and obsolete syscall names that must remain for ABI compatibility. Wrong numbers break audit rules on 32-bit x86 and compat syscalls.

Test signals: Round-trip lookups for legacy and modern syscalls, `arch=b32` parsing on x86_64, and generated table comparison with kernel syscall definitions.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/lib/i386_table.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/lib/libaudit.c -->
# sources/security-integrity/audit-userspace/lib/libaudit.c

Purpose: Core libaudit implementation for kernel audit control requests, feature discovery, libaudit configuration, audit rule construction/parsing, watch helpers, loginuid/session helpers, machine detection, parser diagnostics, and capability checks.

Important APIs and state: Exports status/control functions (`audit_request_status`, `audit_is_enabled`, `audit_set_enabled`, `audit_set_failure`, `audit_set_pid`, backlog/rate/feature setters), list/signal requests, watch/rule functions, rule allocation/init/free, syscall/io_uring rule helpers, field and interfield parser helpers, loginuid/session accessors, machine detection, `audit_number_to_errmsg`, `audit_can_control`, `audit_can_write`, `audit_can_read`, and temporary `set_aumessage_mode`. Global parser state includes `_audit_permadded`, `_audit_archadded`, `_audit_syscalladded`, `_audit_exeadded`, `_audit_filterfsadded`, and `_audit_elf`. Feature cache `features_bitmap` avoids repeated kernel queries.

Control flow: Configuration parsing opens `/etc/libaudit.conf` with `O_NOFOLLOW`, validates root ownership and write permissions, tokenizes `name = value` lines, and dispatches known keywords. Kernel control functions build `audit_status` or `audit_features` structures and send netlink messages via `audit_send`/`__audit_send`, with polling loops for status/feature replies where needed. Rule helpers build `audit_rule_data`, grow string buffers for path/key/exe/SELinux fields, validate operator/filter combinations, translate names through generated tables, use kernel feature bits for newer fields, expand permissions into architecture-specific syscall masks, and map interfield comparisons to kernel comparison constants.

State and persistence: Mutates kernel audit state through netlink, reads/writes `/proc/self/loginuid`, reads `/proc/self/sessionid`, reads `/etc/libaudit.conf`, and caches feature bitmap in process memory. Rule-building state globals make parse ordering significant, especially `arch` before `-S` and `key` after syscall/watch/exe/filesystem filter context.

Dependencies and integration: Depends on kernel audit headers, generated lookup tables through translation functions, netlink code, `private.h`, `common.h`, `errormsg.h`, optional libcap-ng, optional io_uring, libc passwd/group databases, `/proc`, and `audit_logging`/deprecated send APIs. It is the main implementation behind declarations in `libaudit.h`.

Risks: Parser state is global and not thread-safe for concurrent rule construction. `filter_supported_syscalls` uses a fixed 512-byte buffer for comma-separated syscall lists, so future long permission expansions would need scrutiny. Feature probing gracefully degrades but can reject newer rule fields when kernel support is absent or unreadable. Rule buffer realloc failures free the old rule and null the caller pointer. Config parsing is intentionally strict; permission errors cause fallback/default failure action.

Test signals: Unit tests for config parsing and permission checks, mocked netlink send/reply paths, feature cache behavior, rule parser success/failure cases for every `EAU_*` path, architecture/syscall parsing, permission expansion per architecture, watch/exe/key buffer growth, loginuid/session procfs access, and capability checks with/without libcap-ng.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/lib/libaudit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/lib/libaudit.h -->
# sources/security-integrity/audit-userspace/lib/libaudit.h

Purpose: Primary public libaudit header declaring low-level audit ABI structures, dispatcher protocol structures, machine/failure enums, translation APIs, kernel control APIs, rule-building APIs, watch helpers, and capability helpers.

Important types and APIs: Defines `AUDIT_KEY_SEPARATOR`, audit filter compatibility macros, `AUDIT_INTERP_SEPARATOR`, `MAX_AUDIT_MESSAGE_LENGTH`, `struct audit_message`, `struct audit_reply`, `struct audit_dispatcher_header`, dispatcher protocol versions, `machine_t`, `auditfail_t`, `reply_t`, `rep_wait_t`, and declarations for all main libaudit functions. Includes `audit_logging.h`, making logging APIs available through this header.

Control flow: Header-only declarations and ABI definitions with C++ guards. Some macros provide fallback definitions for libc attribute annotations and newer audit filter constants.

State and persistence: No direct state, but declared APIs mutate kernel audit state, procfs loginuid/session state, and rule structures supplied by callers.

Dependencies and integration: Includes `<asm/types.h>`, `<stdint.h>`, socket/netlink headers, `<linux/audit.h>`, syslog, and `audit_logging.h`. Used by auditctl, auditd, plugins, PAM integrations, and downstream applications.

Risks: Explicit comments mark structures as external ABI; field layout and dispatcher header size/versioning are compatibility-critical. Public header must remain self-contained and cannot rely on private compatibility headers. Changes to enum values, structure layouts, or function signatures can break compiled applications.

Test signals: ABI compliance checks, C/C++ standalone compile, downstream application build tests, symbol/version checks, and struct size/layout tests for dispatcher protocol and audit reply/message structures.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/lib/libaudit.h -->
