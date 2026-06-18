# subset-b-007338 Research

Grouped source research for Hadoop Common build metadata, native build configuration, shell launch/runtime scripts, baseline configuration files, and small Java configuration APIs. Each source file has its own marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/pom.xml -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/pom.xml

Purpose: Maven descriptor for the `hadoop-common` jar in the Hadoop 3.6.0-SNAPSHOT tree. It declares the component identity, runtime and test dependencies, generated-resource handling, native build profiles, Windows build hooks, shell documentation generation, shell test integration, protobuf compatibility paths, and release/site support. The file was read as a complete 1248-line POM.

Important APIs/functions: there are no runtime APIs, but the important build contracts are the `hadoop-common` artifact, resource filtering split for `common-version-info.properties`, protobuf compile/test-compile executions, `hadoop-maven-plugins` goals `version-info`, `resource-gz`, `cmake-compile`, and `cmake-test`, surefire timeout listener wiring, Avro test source generation, RAT excludes, `exec-maven-plugin` shell documentation and release-doc executions, and profiles `native`, `native-win`, `parallel-tests`, `releasedocs`, `shelltest`, `non-x86_64`, and `x86_64`.

Control flow: Maven first resolves the parent `hadoop-project-dist`, then applies dependencies and resource filtering. Generate-resource phases create version info and gzip static web assets. The `native` profile enforces Unix or macOS, passes native dependency requirements into CMake, and runs native tests. The `native-win` profile detects or accepts a Visual Studio platform toolset and invokes `msbuild` for winutils and the native DLL. The x86 and non-x86 protobuf profiles either generate legacy protobuf 2.5.0 classes or add checked-in generated source roots. The `shelltest` profile runs BATS script tests during Maven test.

State and persistence: build state is emitted under `target/`, `src/site/resources`, generated Java source directories, native result directories, and generated docs such as `UnixShellAPI.md`. Test setup deletes and recreates `${test.build.data}` and creates `${hadoop.log.dir}`.

Dependencies and integration: this POM is the dependency hub for Hadoop Common, including shaded protobuf/guava, servlet/Jersey/Jetty HTTP stack, auth, curator/ZooKeeper/Netty, compression libraries, crypto providers, JUnit/Mockito/AssertJ, native compression bindings, and Hadoop test helpers. It integrates directly with `src/CMakeLists.txt`, shell sources under `src/main/bin`, configuration files under `src/main/conf`, protobuf sources, native code, and site documentation tooling.

Risks: build behavior is profile-sensitive and platform-sensitive. Native optional libraries can silently disable features unless `require.*` flags are set. The Windows profile depends on external Visual Studio/MSBuild conventions. Protobuf 2.5.0 compatibility generation is split by architecture and can drift from shaded protobuf replacement rules. RAT excludes and generated-doc copy/clean rules need maintenance when files move.

Test signals: `mvn test` for Java/unit coverage, `mvn -Pnative test` for CMake native tests (`test_bulk_crc32`, optional erasure code test), `mvn -Pshelltest test` for BATS shell coverage, `mvn -Pparallel-tests test` for forked test isolation, Windows CI for `native-win`, and site generation for shell docs and release docs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/pom.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/CMakeLists.txt -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/CMakeLists.txt

Purpose: CMake build script for Hadoop Common native code and native tests. It configures JNI, probes compression/crypto/native acceleration libraries, generates `config.h`, builds the dual `hadoop` shared library, sets RPATH behavior, and creates the CRC32 test binary. The source was read as a complete 259-line file.

Important APIs/functions: CMake entry points include `cmake_minimum_required`, `include(HadoopCommon)`, `include(HadoopJNI)`, `find_package(ZLIB REQUIRED)`, `find_package(BZip2 QUIET)`, `find_library` for ISA-L, PMDK, and OpenSSL/libcrypto, `check_c_source_compiles` for `EVP_aes_256_ctr`, `check_function_exists`, `check_library_exists`, `configure_file`, `hadoop_add_dual_library`, `hadoop_target_link_dual_libraries`, `hadoop_dual_output_directory`, `set_target_properties`, and `add_executable` for native tests.

Control flow: the script requires `GENERATED_JAVAH`, initializes JNI, then probes zlib as mandatory and bzip2, ISA-L, PMDK, and OpenSSL as optional unless their `REQUIRE_*` variables demand failure. It selects a hardware CRC32 source for x86, aarch64, or RISC-V, checks platform APIs such as `sync_file_range` and `posix_fadvise`, configures include paths, emits `config.h`, builds `libhadoop` from native IO, compression, crypto, domain socket, security, and CRC sources, then links `dl` and JVM libraries where needed.

State and persistence: build outputs live in the CMake/Maven target tree, including generated `config.h`, `libhadoop.so` or platform equivalent, `target/usr/local/lib`, and `test_bulk_crc32`. No runtime persistence is owned by CMake, but compile-time feature state is persisted into `config.h`.

Dependencies and integration: integrates with Maven's `cmake-compile` goal, generated JNI headers, Hadoop native C sources, zlib, optional bzip2, ISA-L, PMDK, OpenSSL, `dl`, JVM libraries, and `src/config.h.cmake`. Java native loaders use the configured library names and feature macros at runtime.

Risks: optional dependencies can produce different native feature sets across machines. Required-library flags intentionally fail the build, so CI matrices must set them consistently. OpenSSL detection depends on a compile probe for `EVP_aes_256_ctr`. RPATH uses `$ORIGIN` only for Linux/SunOS and may need extra RPATH for nonstandard deployments. A typo-like variable name `BULK_CRC_ARCH_SOURCE_FIlE` is internally consistent but easy to misuse in future edits.

Test signals: CMake configure output for found/missing native libraries, Maven `-Pnative` build, `test_bulk_crc32`, optional `erasure_code_test`, NativeLibraryChecker behavior, and Java tests that exercise native compression, native IO, domain sockets, and crypto loading.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/config.h.cmake -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/config.h.cmake

Purpose: CMake template for the generated native `config.h` consumed by Hadoop Common C/JNI sources. It records which optional native libraries and platform functions were detected during the native build. The source was read as a complete 30-line file.

Important APIs/functions: preprocessor definitions produced through `#cmakedefine`: `HADOOP_ZLIB_LIBRARY`, `HADOOP_BZIP2_LIBRARY`, `HADOOP_SNAPPY_LIBRARY`, `HADOOP_OPENSSL_LIBRARY`, `HADOOP_ISAL_LIBRARY`, `HADOOP_PMDK_LIBRARY`, `HAVE_SYNC_FILE_RANGE`, and `HAVE_POSIX_FADVISE`.

Control flow: this file has no runtime control flow. CMake substitutes detected library names and function booleans into the template, and native C code compiles conditional paths based on the generated macros.

State and persistence: the generated header persists native feature detection into the build directory. At runtime, the JNI library can use these macros to expose native library names or gate optional code paths, but the template owns no mutable state.

Dependencies and integration: generated by `src/CMakeLists.txt` using `configure_file`. It is included by native Hadoop sources for compression, crypto, erasure coding, persistent memory, and native IO features.

Risks: macro drift between CMake probes and C source expectations can silently disable or misreport native functionality. `HADOOP_SNAPPY_LIBRARY` is templated here but not set by the visible CMake file in this subset, so consumers must tolerate an undefined macro.

Test signals: native compile with different dependency combinations, NativeLibraryChecker output, platform API tests for native IO, and C preprocessor/build failures when a macro is missing or misspelled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/config.h.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/contrib/bash-tab-completion/hadoop.sh -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/contrib/bash-tab-completion/hadoop.sh

Purpose: Bash completion script for the top-level `hadoop` command. It executes and parses the installed Hadoop script to complete subcommands, command options, JAR/local paths, and HDFS paths. The source was read as a complete 119-line file.

Important APIs/functions: defines `_hadoop` and registers it with `complete -F _hadoop hadoop`. Uses Bash completion globals `COMP_WORDS`, `COMP_CWORD`, and `COMPREPLY`, plus `compgen`, `which`, `grep`, `awk`, `cut`, `sort`, and Hadoop command output.

Control flow: completion first resolves the executable for the current command and exits unless it is an executable file. For the first argument it parses the usage output before the `or` usage line and extracts leading command names. For the second argument it has command-specific parsers for `dfs`, `dfsadmin`, `fs`, `job`, `pipes`, `jar`, and `namenode`. For later arguments, it infers parameter names for `dfs`/`fs` subcommands and completes HDFS paths via `-ls -d` or local filesystem paths via `compgen -A file`.

State and persistence: all state is shell-local and transient in `COMPREPLY`. It does not write files or cache completions.

Dependencies and integration: depends on the installed `hadoop` shell launcher and the stability of usage/help output from Hadoop commands. It integrates with Bash completion infrastructure on systems that source scripts from `/etc/bash_completion.d/`.

Risks: completion executes the target script repeatedly, so slow or side-effectful command help paths affect interactive shells. Several expansions are unquoted, command output parsing is fragile, and only a subset of subcommands receives deep argument completion. HDFS path completion depends on the active cluster and user credentials.

Test signals: manual tab-completion checks for first-level commands, option completion for `fs` and `dfsadmin`, local JAR path completion, HDFS path completion against a test cluster, and shellcheck/BATS coverage for quoting regressions where feasible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/contrib/bash-tab-completion/hadoop.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/bin/hadoop -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/bin/hadoop

Purpose: primary Unix shell launcher for Hadoop Common commands. It declares user-facing `hadoop` subcommands, maps them to Java main classes or compatibility delegates, initializes the shared shell runtime, handles worker mode, and executes Java through the generic command handler. The source was read as a complete 244-line script.

Important APIs/functions: defines `hadoop_usage` and `hadoopcmd_case`. Important subcommands include `checknative`, `classpath`, `conftest`, `credential`, `daemonlog`, `dtutil`, `envvars`, `fs`, `jar`, `jnipath`, `kerbname`, `kdiag`, `key`, `registrydns`, `version`, and `rbfbalance`. It relies on shared functions such as `hadoop_add_option`, `hadoop_add_subcommand`, `hadoop_exit_with_usage`, `hadoop_need_reexec`, `hadoop_uservar_su`, `hadoop_verify_user_perm`, `hadoop_add_client_opts`, `hadoop_subcommand_opts`, and `hadoop_generic_java_subcmd_handler`.

Control flow: the script locates `libexec`, sources `hadoop-config.sh`, validates that a subcommand exists, optionally re-execs as a configured user, checks per-subcommand permissions, dispatches to a dynamic `hadoop_subcommand_<name>` function or the `hadoopcmd_case` switch, applies client options, handles `--workers` fan-out, applies subcommand-specific options, and finally calls the generic Java/daemon launcher. Deprecated HDFS and MapReduce command names are delegated to `hdfs` or `mapred`.

State and persistence: the script mutates process-global shell variables such as `HADOOP_CLASSNAME`, `HADOOP_SUBCMD`, `HADOOP_SUBCMD_ARGS`, `HADOOP_SECURE_CLASSNAME`, classpath/native-library paths, and daemonization flags. It persists no files directly, but downstream daemon mode writes logs and PID files.

Dependencies and integration: sourced runtime comes from `hadoop-config.sh` and `hadoop-functions.sh`. Java classes named here live in Hadoop Common, HDFS, tools, or security packages. It delegates deprecated commands to `HADOOP_HDFS_HOME` and `HADOOP_MAPRED_HOME` scripts and augments tools classpath for `rbfbalance`.

Risks: backwards-compatible delegation depends on sibling project installations. Unknown subcommands containing a dot are accepted as user Java class names, so validation is intentionally shallow. Shell state is global, so subproject extensions must avoid variable collisions. The `jar` path warns but still permits YARN application launch through the legacy command.

Test signals: BATS shell tests under the shelltest profile, `hadoop envvars`, `hadoop classpath`, `hadoop jnipath`, command-specific smoke tests, deprecated command delegation tests, and daemon/worker-mode integration tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/bin/hadoop -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/bin/hadoop-config.sh -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/bin/hadoop-config.sh

Purpose: shared bootstrap script sourced by Hadoop shell entry points. It locates and imports the function library, layout overrides, configuration directory, environment files, shell profiles, OS/Java setup, native paths, classpath, and user rc hooks. The source was read as a complete 165-line file.

Important APIs/functions: this file mostly executes shared functions rather than defining them. It calls `hadoop_deprecate_envvar`, `hadoop_bootstrap`, `hadoop_parse_args`, `hadoop_find_confdir`, `hadoop_exec_hadoopenv`, `hadoop_import_shellprofiles`, `hadoop_exec_userfuncs`, `hadoop_exec_user_hadoopenv`, `hadoop_verify_confdir`, `hadoop_os_tricks`, `hadoop_java_setup`, `hadoop_basic_init`, optional `hadoop_subproject_init`, `hadoop_shellprofiles_init`, `hadoop_add_javalibpath`, `hadoop_add_common_to_classpath`, `hadoop_shellprofiles_classpath`, and `hadoop_exec_hadooprc`.

Control flow: it enforces Bash 3.2+, determines `HADOOP_LIBEXEC_DIR`, sources `hadoop-functions.sh`, applies deprecated environment variable aliases, optionally sources layout, bootstraps defaults, saves original user parameters, parses generic shell options and shifts consumed arguments, loads site and user configuration in a deliberate order, runs OS and Java checks, initializes project homes and shell profiles, adds native library paths and common jars, then finalizes immediately for legacy callers unless `HADOOP_NEW_CONFIG` is set.

State and persistence: it mutates the caller's shell environment, including `HADOOP_HOME`, `HADOOP_CONF_DIR`, `JAVA_HOME`, `CLASSPATH`, `JAVA_LIBRARY_PATH`, `HADOOP_USER_PARAMS`, and parsed option counters. It persists no files directly.

Dependencies and integration: sourced by `hadoop`, `workers.sh`, `start-all.sh`, `stop-all.sh`, and other project-specific wrappers. It integrates with `hadoop-env.sh`, `${HOME}/.hadoop-env`, `${HOME}/.hadooprc`, `hadoop-layout.sh`, and `shellprofile.d` plugin hooks.

Risks: because it is sourced by non-Hadoop scripts for compatibility, argument parsing and global variable side effects are part of its public contract. User-provided code is sourced from configuration and home directories, so ordering matters for security and override behavior. Missing or incomplete configuration directories warn rather than always fail.

Test signals: shell BATS tests for option parsing and environment derivation, `hadoop envvars`, classpath and native path smoke tests, user rc/profile override tests, and compatibility tests for scripts that source this file directly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/bin/hadoop-config.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/bin/hadoop-daemon.sh -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/bin/hadoop-daemon.sh

Purpose: deprecated compatibility wrapper for starting, stopping, or checking HDFS daemons through the old `hadoop-daemon.sh` interface. The source was read as a complete 59-line script.

Important APIs/functions: defines `hadoop_usage`; sources `hdfs-config.sh`; uses `hadoop_exit_with_usage` and `hadoop_error`; dispatches to `hdfs --daemon`.

Control flow: the script locates `libexec`, sources HDFS configuration, requires at least one argument, treats the first argument as daemon mode, chooses `HADOOP_HDFS_HOME/bin/hdfs` or `HADOOP_HOME/bin/hdfs`, emits deprecation warnings, then `exec`s `hdfs --config "$HADOOP_CONF_DIR" --daemon "$daemonmode" "$@"`.

State and persistence: it owns no persistent state. The replacement `hdfs --daemon` command writes any daemon logs and PID files.

Dependencies and integration: depends on HDFS being installed beside Hadoop Common and on `hdfs-config.sh` providing the shared shell runtime. It preserves old command-line shapes while transferring control to the modern HDFS launcher.

Risks: invalid daemon modes are not validated locally and are left to the replacement command. If HDFS is not installed or `hdfs-config.sh` is missing, the wrapper fails early. Existing automation may rely on exact warning or argument behavior.

Test signals: compatibility smoke tests for `start`, `stop`, and `status`, missing HDFS installation tests, and checks that arguments after daemon mode are passed through to `hdfs`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/bin/hadoop-daemon.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/bin/hadoop-daemons.sh -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/bin/hadoop-daemons.sh

Purpose: deprecated compatibility wrapper for running HDFS daemon operations across worker hosts through the old `hadoop-daemons.sh` interface. The source was read as a complete 77-line script.

Important APIs/functions: defines `hadoop_usage`; sources `hdfs-config.sh`; uses `hadoop_exit_with_usage` and `hadoop_error`; rewrites `HADOOP_USER_PARAMS`; invokes `hdfs --workers --daemon`.

Control flow: the script locates `libexec`, sources HDFS configuration, requires arguments, extracts the daemon mode, chooses the HDFS launcher, warns about deprecation, removes `start`, `stop`, or `status` tokens from the saved original user parameter array, then runs `hdfs --workers --daemon "$daemonmode" "${HADOOP_USER_PARAMS[@]}"`.

State and persistence: it mutates the transient `HADOOP_USER_PARAMS` array to avoid duplicating the daemon mode. Persistent logs, PID files, and remote process state are owned by the replacement HDFS worker/daemon command.

Dependencies and integration: depends on HDFS shell configuration and the shared worker fan-out behavior behind `hdfs --workers`. It preserves old multi-host operational scripts while delegating to the modern HDFS CLI.

Risks: token removal scans all saved user parameters, so an argument value equal to `start`, `stop`, or `status` could be dropped. Unlike the single-host wrapper, it does not `exec`, so exit/status propagation depends on the final command invocation. Missing HDFS installation fails at execution time.

Test signals: compatibility tests for multi-host start/stop/status, preservation of `--hosts` and daemon options, worker list handling, and regression tests for argument values that match daemon mode names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/bin/hadoop-daemons.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/bin/hadoop-functions.sh -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/bin/hadoop-functions.sh

Purpose: central Bash function library for Hadoop Unix command launchers. It implements diagnostics, usage generation, environment bootstrap, configuration loading, shell profile hooks, classpath/native path assembly, remote worker execution, OS and Java checks, daemon lifecycle management, privileged daemon support, per-subcommand security/user handling, argument parsing, and final Java execution. The source was read as a complete 2775-line file.

Important APIs/functions: public and integration functions include `hadoop_error`, `hadoop_debug`, `hadoop_abs`, `hadoop_add_subcommand`, `hadoop_add_option`, `hadoop_generate_usage`, `hadoop_deprecate_envvar`, `hadoop_mkdir`, `hadoop_bootstrap`, `hadoop_find_confdir`, `hadoop_exec_hadoopenv`, `hadoop_import_shellprofiles`, `hadoop_basic_init`, `hadoop_populate_workers_file`, `hadoop_connect_to_hosts`, `hadoop_common_worker_mode_execute`, `hadoop_validate_classname`, `hadoop_add_param`, `hadoop_add_profile`, `hadoop_add_classpath`, `hadoop_add_javalibpath`, `hadoop_add_ldlibpath`, `hadoop_add_common_to_classpath`, `hadoop_os_tricks`, `hadoop_java_setup`, `hadoop_finalize`, `hadoop_java_exec`, `hadoop_daemon_handler`, `hadoop_secure_daemon_handler`, `hadoop_build_custom_subcmd_var`, `hadoop_verify_user_perm`, `hadoop_need_reexec`, `hadoop_subcommand_opts`, `hadoop_parse_args`, and `hadoop_generic_java_subcmd_handler`.

Control flow: command scripts source this file, then bootstrap defaults and parse generic options. Configuration and profile hooks populate global variables. The classpath and native paths are assembled with dedupe and existence checks. Commands either run locally as Java, fan out through worker mode, or enter daemon handling. Non-secure daemons write PID files, rotate logs, fork, renice, and disown. Secure daemons use `jsvc`, privileged wrapper PID files, secure user variables, and secure log/PID directories. The generic Java handler detects secure subcommands, sets log files and daemon root logger when needed, finalizes environment variables and JPMS options, then dispatches to Java or daemon handlers.

State and persistence: state is mostly global shell variables and arrays: usage arrays, `CLASSPATH`, `JAVA_LIBRARY_PATH`, `LD_LIBRARY_PATH`, `HADOOP_OPTS`, `HADOOP_*_HOME`, `HADOOP_CONF_DIR`, worker variables, daemon mode, log/pid paths, and security users. Persistent side effects include creating log and PID directories, rotating daemon logs, writing PID files, removing stale PID files, and executing remote commands over SSH or pdsh.

Dependencies and integration: all Hadoop shell frontends depend on this library. It integrates with `hadoop-env.sh`, user rc files, shell profiles, optional tools modules under `libexec/tools`, Java, `sudo`, `ssh`, optional `pdsh`, `jsvc`, `renice`, `ps`, `kill`, `id`, `tput`, and OS-specific commands such as `/sbin/sysctl` and `cygpath`.

Risks: the library intentionally relies on mutable global shell state and `eval` for variable indirection, so quoting, spacing, and variable naming regressions can affect many commands. User-provided files are sourced as code. PID-file checks rely on process command lines containing `-Dproc_<daemon>`. Remote execution command construction is shell-sensitive. Secure daemon behavior depends on `jsvc` availability and correct user variables. Linux IPv6 bind-only settings abort startup unless explicitly allowed.

Test signals: BATS shell tests for parsing, classpath/path functions, daemon modes, worker mode, user re-exec, and shell profile hooks; daemon integration tests for start/stop/status and PID cleanup; secure daemon tests with `jsvc`; `hadoop classpath`, `hadoop envvars`, and `hadoop --debug` smoke tests; shellcheck-style review for quoting changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/bin/hadoop-functions.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/bin/start-all.sh -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/bin/start-all.sh

Purpose: legacy convenience script for starting all available Hadoop daemons from one host. It loads common configuration, warns when starting as a non-privileged user, then delegates to HDFS and YARN start scripts if present. The source was read as a complete 65-line script.

Important APIs/functions: defines `hadoop_abort_startall`; uses `hadoop_privilege_check`, `hadoop_error`, and shared config loading from `hadoop-config.sh`; invokes `start-dfs.sh` and `start-yarn.sh`.

Control flow: after locating and sourcing `hadoop-config.sh`, it checks privileges. If the user is not privileged, it installs an interrupt trap, emits warnings, sleeps for 10 seconds to allow abort, then removes the trap. It then calls `${HADOOP_HDFS_HOME}/sbin/start-dfs.sh --config "$HADOOP_CONF_DIR"` if present and `${HADOOP_YARN_HOME}/sbin/start-yarn.sh --config "$HADOOP_CONF_DIR"` if present.

State and persistence: this wrapper writes no state directly. Delegated HDFS/YARN scripts create daemon processes, logs, and PID files.

Dependencies and integration: depends on `hadoop-config.sh`, the shared privilege check, HDFS and YARN homes, and sibling `sbin` scripts. It is a top-level orchestration shim over project-specific daemon managers.

Risks: it encourages a single-user all-daemon deployment that the script itself warns is not recommended for production. Missing HDFS or YARN scripts are silently skipped. It does not aggregate or check downstream failure statuses beyond normal shell command behavior.

Test signals: smoke tests with HDFS-only, YARN-only, both present, and neither present; interrupt behavior during the warning delay; propagation of `--config`; and integration tests verifying daemon logs/PID files are created by delegated scripts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/bin/start-all.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/bin/stop-all.sh -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/bin/stop-all.sh

Purpose: legacy convenience script for stopping all available Hadoop daemons from one host. It loads common configuration, warns before stopping as a non-privileged user, then delegates to HDFS and YARN stop scripts if present. The source was read as a complete 65-line script.

Important APIs/functions: defines `hadoop_abort_stopall`; uses `hadoop_privilege_check`, `hadoop_error`, and shared config loading from `hadoop-config.sh`; invokes `stop-dfs.sh` and `stop-yarn.sh`.

Control flow: the script locates and sources `hadoop-config.sh`, warns and delays for 10 seconds when not privileged, then calls `${HADOOP_HDFS_HOME}/sbin/stop-dfs.sh --config "$HADOOP_CONF_DIR"` if present. It then attempts to call a YARN stop script, but the path check uses `${HADOOP_HDFS_HOME}/sbin/stop-yarn.sh` rather than `${HADOOP_YARN_HOME}` in the source read here.

State and persistence: the wrapper has no direct persistent state. Delegated stop scripts terminate daemons and remove or update PID files.

Dependencies and integration: depends on shared shell configuration, privilege checks, and project-specific stop scripts. It is part of the legacy top-level operational interface.

Risks: the apparent YARN path check against `HADOOP_HDFS_HOME` can skip YARN shutdown in layouts where YARN is separate from HDFS. Like `start-all.sh`, it is coarse-grained and does not provide strong downstream status aggregation. Missing project scripts are silently skipped.

Test signals: smoke tests in combined and split HDFS/YARN layouts, especially verifying that YARN stop runs when only `HADOOP_YARN_HOME` contains `stop-yarn.sh`; interrupt behavior during warning delay; and daemon status checks after stop.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/bin/stop-all.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/bin/workers.sh -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/bin/workers.sh

Purpose: helper script to run an arbitrary shell command across configured Hadoop worker hosts. It is the generic worker fan-out frontend used by administrators and higher-level scripts. The source was read as a complete 60-line script.

Important APIs/functions: defines `hadoop_usage`; sources `hadoop-config.sh`; uses `hadoop_exit_with_usage` and `hadoop_connect_to_hosts`.

Control flow: the script locates `libexec`, sources common configuration, requires at least one command argument, then passes the command to `hadoop_connect_to_hosts`, which uses `pdsh` if available or falls back to SSH with bounded parallelism.

State and persistence: no local persistent state is written. Remote commands may change state on worker hosts. Runtime state is derived from `HADOOP_WORKERS`, `HADOOP_WORKER_NAMES`, `HADOOP_CONF_DIR`, `HADOOP_SSH_OPTS`, and `HADOOP_SSH_PARALLEL`.

Dependencies and integration: integrates with the worker list file `${HADOOP_CONF_DIR}/workers` or deprecated `slaves`, optional `pdsh`, SSH, and the common config parser for `--hosts`, `--hostnames`, and `--config`.

Risks: command quoting and remote-shell interpretation are sensitive. Worker file contents and SSH options directly control target hosts. There is no high-level success aggregation beyond the underlying fan-out command. Running arbitrary commands across workers is operationally powerful and risky.

Test signals: local tests for missing arguments and worker-file resolution, integration tests with mock SSH/pdsh, hostnames versus hosts-file behavior, parallelism limits, and command/argument quoting cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/bin/workers.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/conf/core-site.xml -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/conf/core-site.xml

Purpose: default site-specific Hadoop Common configuration placeholder. It provides an XML `configuration` root and stylesheet reference but no properties, signaling that deployments should place site overrides here. The source was read as a complete 20-line XML file.

Important APIs/functions: configuration keys are not defined in this file. The important contract is the Hadoop XML configuration format consumed by `Configuration`.

Control flow: no executable control flow. At runtime Hadoop's configuration loader reads this file from `HADOOP_CONF_DIR` and merges any properties with defaults and other site files.

State and persistence: this file is persistent configuration state, but in the checked-in version it stores no property values.

Dependencies and integration: consumed by Hadoop Common, HDFS, YARN, MapReduce, command-line tools, and daemons through the standard `Configuration` resource loading path. It is copied into test classes by the POM's test resource setup.

Risks: an empty file is safe as a template, but deployments that forget to provide required properties elsewhere will fall back to defaults. XML syntax errors or misplaced site-specific properties would affect every Hadoop component using the config directory.

Test signals: configuration parser smoke tests, `hadoop conftest`, service startup with a minimal config directory, and tests that verify site overrides are loaded from `HADOOP_CONF_DIR`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/conf/core-site.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/conf/hadoop-env.sh -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/conf/hadoop-env.sh

Purpose: master shell environment template for all Hadoop projects. It documents and, for a few values, sets common environment variables controlling Java, Hadoop home/config paths, classpath behavior, daemon logging, SSH fan-out, secure daemon execution, HDFS daemon options, and registry DNS secure options. The source was read as a complete 434-line file.

Important APIs/functions: no functions are defined. Key variables documented or exported include `JAVA_HOME`, `LANG`, `HADOOP_HOME`, `HADOOP_CONF_DIR`, `HADOOP_HEAPSIZE_MAX`, `HADOOP_HEAPSIZE_MIN`, `HADOOP_OPTS`, `HADOOP_OS_TYPE`, `HADOOP_CLIENT_OPTS`, `HADOOP_CLASSPATH`, `HADOOP_USER_CLASSPATH_FIRST`, `HADOOP_USE_CLIENT_CLASSLOADER`, `HADOOP_OPTIONAL_TOOLS`, `HADOOP_SSH_OPTS`, `HADOOP_SSH_PARALLEL`, `HADOOP_WORKERS`, `HADOOP_LOG_DIR`, `HADOOP_IDENT_STRING`, `HADOOP_STOP_TIMEOUT`, `HADOOP_PID_DIR`, `HADOOP_ROOT_LOGGER`, `HADOOP_DAEMON_ROOT_LOGGER`, `HADOOP_SECURITY_LOGGER`, `JSVC_HOME`, and many `HDFS_*_OPTS` and secure-user variables.

Control flow: execution is limited to shell assignments when the file is sourced. It exports `LANG=en_US.UTF-8` and sets `HADOOP_OS_TYPE` to `uname -s` if unset. Most lines are commented examples intentionally left for site customization.

State and persistence: the file is persistent site configuration. When sourced by `hadoop-config.sh`, active exports mutate the launcher's environment and influence every child Java process or daemon.

Dependencies and integration: read by all Hadoop command wrappers after `HADOOP_CONF_DIR` is located. It is the documented site-level override point below project-specific files such as `hdfs-env.sh` and `yarn-env.sh`, and above hard-coded shell defaults.

Risks: because this file is sourced as shell code, syntax errors or unsafe commands can break or alter every Hadoop command. Misconfigured `JAVA_HOME`, PID/log directories, secure users, or classpath variables can prevent startup or create security issues. The template's comments are part of the admin contract and must stay aligned with `hadoop-functions.sh`.

Test signals: `hadoop envvars`, command startup with customized `JAVA_HOME` and config directory, daemon start/stop tests with custom log/PID directories, secure datanode/registry DNS tests, and documentation checks against shell behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/conf/hadoop-env.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/conf/hadoop-policy.xml -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/conf/hadoop-policy.xml

Purpose: default service-level authorization policy file for Hadoop RPC protocols. It defines ACL properties for HDFS, MapReduce, YARN, HA, journal, refresh, router, and timeline-related protocols, with checked-in defaults allowing all users. The source was read as a complete 325-line XML file.

Important APIs/functions: properties include `security.client.protocol.acl`, `security.client.datanode.protocol.acl`, `security.datanode.protocol.acl`, `security.inter.datanode.protocol.acl`, `security.datanode.lifeline.protocol.acl`, `security.namenode.protocol.acl`, `security.admin.operations.protocol.acl`, refresh protocol ACLs, `security.ha.service.protocol.acl`, router and ZKFC ACLs, qjournal ACLs, MapReduce history/client/task ACLs, and many YARN protocol ACLs. All visible values are `*`.

Control flow: no executable control flow. Hadoop authorization code loads this XML by the `hadoop.policy.file` system property or default `HADOOP_POLICYFILE` and checks protocol ACLs when service-level authorization is enabled.

State and persistence: persistent policy state. In this default form it is permissive; production deployments are expected to override values with users and groups.

Dependencies and integration: integrated through the Hadoop `Configuration` loader and service authorization manager. The shell layer defaults `HADOOP_POLICYFILE` to `hadoop-policy.xml`, and admin refresh commands can reload policy at runtime.

Risks: default `*` ACLs are intentionally broad and must be tightened for secured clusters. Property-name drift between protocol implementations and this file can leave a service with unintended defaults. XML syntax errors can break policy loading or refresh.

Test signals: XML validation, service authorization unit tests for each protocol key, `dfsadmin`/`rmadmin` policy refresh tests, secure cluster integration tests with restrictive ACLs, and negative tests verifying unauthorized users are rejected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/conf/hadoop-policy.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/conf/shellprofile.d/example.sh -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/conf/shellprofile.d/example.sh

Purpose: commented example of Hadoop's pluggable shell profile API. It documents how administrators or optional tools can register shell profiles and hook into initialization, classpath, native library path, and final option construction. The source was read as a complete 106-line file.

Important APIs/functions: the example references `hadoop_add_profile`, `_example_hadoop_init`, `_example_hadoop_classpath`, `_example_hadoop_nativelib`, `_example_hadoop_finalize`, `hadoop_add_classpath`, `hadoop_add_javalibpath`, `hadoop_add_ldlibpath`, `hadoop_add_param`, and `hadoop_translate_cygwin_path`. All example functions are commented out.

Control flow: the checked-in file performs no active registration or execution. If uncommented or adapted, `hadoop_import_shellprofiles` would source the profile, `hadoop_shellprofiles_init` would call init hooks, classpath/native hooks would run during path construction, and finalize hooks would run immediately before Java execution.

State and persistence: no active state changes in the template. Real profiles mutate environment variables such as `HADOOP_SHELL_PROFILES`, `CLASSPATH`, `JAVA_LIBRARY_PATH`, `LD_LIBRARY_PATH`, and `HADOOP_OPTS`.

Dependencies and integration: demonstrates extension points implemented in `hadoop-functions.sh` and sourced from `HADOOP_LIBEXEC_DIR/shellprofile.d` or `HADOOP_CONF_DIR/shellprofile.d`.

Risks: profile files are sourced as shell code, so active profiles can break command launchers or introduce unsafe behavior. Hook ordering matters because user `.hadooprc` and common finalization may override or append values. Direct manipulation of `CLASSPATH` bypasses dedupe and existence checks.

Test signals: shell tests with a small active profile that registers all four hooks, classpath/native path ordering checks, Cygwin path translation tests, and negative tests for malformed profile files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/conf/shellprofile.d/example.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/HadoopIllegalArgumentException.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/HadoopIllegalArgumentException.java

Purpose: Hadoop-specific subclass of `IllegalArgumentException` used to distinguish invalid arguments raised by Hadoop implementation code from plain JDK argument exceptions. The source was read as a complete 40-line Java file.

Important APIs/functions: public stable class `HadoopIllegalArgumentException extends IllegalArgumentException`, `serialVersionUID = 1L`, and constructor `HadoopIllegalArgumentException(String message)`.

Control flow: construction delegates directly to `super(message)`. There is no additional behavior.

State and persistence: stores only the inherited exception message and stack trace. Serializable identity is fixed by `serialVersionUID`.

Dependencies and integration: annotated with `InterfaceAudience.Public` and `InterfaceStability.Stable`, so it is part of Hadoop's public API surface. Used by Hadoop callers that want to catch Hadoop-originated invalid argument failures.

Risks: because it subclasses `IllegalArgumentException`, broad JDK exception handlers will still catch it. Adding constructors or behavior would be API-visible. The class carries no cause-taking constructor, so callers that need exception chaining must use another exception or lose cause information.

Test signals: compile/API compatibility checks, serialization compatibility if exposed across boundaries, and unit tests that assert Hadoop APIs throw this type for documented invalid arguments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/HadoopIllegalArgumentException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/conf/ConfServlet.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/conf/ConfServlet.java

Purpose: HTTP servlet that exposes the running daemon `Configuration` as XML or JSON, optionally for a single property. It is used by Hadoop web UIs and instrumentation endpoints. The source was read as a complete 120-line Java file.

Important APIs/functions: class `ConfServlet extends HttpServlet`; constants `FORMAT_JSON` and `FORMAT_XML`; private `getConfFromContext()`; servlet method `doGet`; testing-visible `parseAcceptHeader`; static `writeResponse(Configuration, Writer, String, String)` and overload without property name; nested `BadFormatException`.

Control flow: `doGet` first asks `HttpServer2.isInstrumentationAccessAllowed`; denied access returns immediately. It chooses JSON when the Accept header contains `json`, otherwise XML. It sets the content type, reads optional request parameter `name`, obtains the response writer, and calls `writeResponse`. `writeResponse` delegates JSON to `Configuration.dumpConfiguration` and XML to `conf.writeXml`; bad format produces HTTP 400 and an unknown property path can produce HTTP 404 via `IllegalArgumentException`.

State and persistence: the servlet reads the `Configuration` stored in the servlet context under `HttpServer2.CONF_CONTEXT_ATTRIBUTE`. It does not mutate configuration or persist data; it writes a transient HTTP response.

Dependencies and integration: integrates with Hadoop `HttpServer2`, servlet APIs, Hadoop `Configuration`, shaded Guava `HttpHeaders`, and web UI/instrumentation access controls. It is limited-private to HDFS and MapReduce and marked unstable.

Risks: Accept negotiation is simplistic and treats any header containing `json` as JSON. Configuration exposure must rely on `HttpServer2` access checks and `Configuration` redaction behavior to avoid leaking secrets. The code obtains a writer before handling some errors and closes it after `sendError`, so servlet-container behavior should be covered by tests.

Test signals: unit tests for Accept parsing, XML and JSON response generation, property filtering by `name`, bad-format handling through `writeResponse`, 404 behavior for missing properties, and web server integration tests for instrumentation ACL enforcement and redaction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/conf/ConfServlet.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/conf/ConfigRedactor.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/conf/ConfigRedactor.java

Purpose: utility that redacts sensitive configuration values before configurations are displayed in logs, JSON/plaintext, or XML. The source was read as a complete 103-line Java file.

Important APIs/functions: class `ConfigRedactor`; constants `REDACTED_TEXT = "<redacted>"` and `REDACTED_XML = "******"`; field `compiledPatterns`; constructor `ConfigRedactor(Configuration conf)`; public methods `redact(String key, String value)` and `redactXml(String key, String value)`; private `configIsSensitive(String key)`.

Control flow: construction reads `HADOOP_SECURITY_SENSITIVE_CONFIG_KEYS` from configuration with `HADOOP_SECURITY_SENSITIVE_CONFIG_KEYS_DEFAULT`, splits it with `StringUtils.getTrimmedStrings`, compiles each regex, and stores the patterns. Redaction loops over the patterns and returns the redaction token if any regex finds a match in the key; otherwise it returns the original value.

State and persistence: state is an in-memory list of compiled regex patterns per redactor instance. It writes no persistent data and does not mutate the supplied `Configuration`.

Dependencies and integration: depends on `Configuration`, common security config constants from `org.apache.hadoop.fs.CommonConfigurationKeys`, Java regex `Pattern`, and Hadoop `StringUtils`. Used by configuration-dumping paths such as `Configuration.dumpConfiguration` and XML output helpers.

Risks: invalid regexes in configuration throw during construction. Redaction depends only on key names, not value content, so secrets under unexpected keys can leak. Overbroad regexes can hide useful non-secret values. Pattern matching uses `find`, so partial matches are intentional but may surprise administrators.

Test signals: unit tests for default sensitive key patterns, custom regex lists, plaintext versus XML redaction tokens, non-sensitive keys preserving values, invalid regex handling, and integration tests through configuration servlet/dump output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/conf/ConfigRedactor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/conf/Configurable.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/conf/Configurable.java

Purpose: public stable interface for objects that can receive and expose a Hadoop `Configuration`. It is a core contract used by tools, filesystems, services, and plugin objects that need late-bound configuration. The source was read as a complete 40-line Java file.

Important APIs/functions: interface `Configurable`; methods `void setConf(Configuration conf)` and `Configuration getConf()`. The type is annotated `InterfaceAudience.Public` and `InterfaceStability.Stable`.

Control flow: no implementation control flow; implementors decide how to store, validate, or react to configuration.

State and persistence: the interface defines an in-memory configuration association but owns no state itself. Implementations commonly store the `Configuration` in a field and may derive additional runtime state from it.

Dependencies and integration: depends on `org.apache.hadoop.conf.Configuration` and classification annotations. It integrates with Hadoop object factories, reflection utilities, and APIs that configure user-supplied components after construction.

Risks: implementations may accept null, retain mutable configuration references, or perform expensive side effects in `setConf`; the interface does not constrain those behaviors. API stability means method signatures cannot be changed without breaking many downstream implementations.

Test signals: compile/API compatibility checks, implementation tests verifying `setConf`/`getConf` round trips, and factory/reflection tests that configure `Configurable` instances.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/conf/Configurable.java -->
