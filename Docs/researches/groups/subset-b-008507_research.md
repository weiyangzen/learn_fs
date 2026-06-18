# Group Research: subset-b-008507

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/docker/sidecar.py -->
# Research: sources/storage-engines/foundationdb/packaging/docker/sidecar.py

## Purpose
Implements the Kubernetes container sidecar used to project config-map input, dynamic monitor configuration, binaries, and client libraries into a shared output directory for the main FoundationDB container. It can run once as an init container or stay up as an HTTP control server.

## Important APIs, Types, And Functions
`Config` parses CLI flags and legacy config/environment input, derives substitutions such as `FDB_PUBLIC_IP`, `FDB_MACHINE_ID`, `BINARY_DIR`, and TLS settings, and exposes `extract_desired_ip`. `SidecarHandler` implements `GET /ready`, `/substitutions`, `/check_hash/<file>`, `/is_present/<file>` and `POST /copy_files`, `/copy_binaries`, `/copy_libraries`, `/copy_monitor_conf`, `/refresh_certs`, `/restart`. Helpers include `is_path_allowed`, `check_hash`, `is_present`, `CertificateEventHandler`, and the copy functions.

## Control Flow
Startup constructs a singleton config, performs all copy operations, exits in `--init-mode`, or starts a threaded HTTP server. Requests first pass certificate authorization unless they are `/ready`; copy endpoints delegate to filesystem helpers; TLS mode wraps the socket and installs watchdog observers that reload the SSL context after certificate file changes.

## State And Persistence Behavior
Persistent effects are writes under `output_dir`: copied config files, dynamic `fdbmonitor.conf`, versioned binaries under `bin/<primary_version>`, and client libraries under `lib/` and `lib/multiversion/`. Writes use temporary files and `os.replace` for atomic replacement. The server keeps process-local SSL context state and reads `/var/fdb/version`.

## Dependencies And Integration Points
Uses Python stdlib HTTP, SSL, tempfile, pathlib, ipaddress, and `watchdog` observers. Integrated with FoundationDB Docker/Kubernetes images, config maps, TLS material mounted into pods, and the main container shared dynamic-conf volume.

## Risks And Edge Cases
Path containment uses `startswith` on absolute paths, which can be subtle for sibling prefixes; endpoint filenames should remain untrusted. Deprecated environment variables are rejected for newer versions but still honored for older versions. Certificate reload sleeps for 10 seconds and reload errors would surface in the observer thread. `POST /restart` exits the process intentionally.

## Test Signals
Covered by `sidecar_test.py` for HTTP readiness, substitutions, hash/presence checks, nested paths, outside-path rejection, and copy endpoint basics. TLS, certificate rule matching, watchdog reload, and binary/library copy paths need separate integration coverage.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/docker/sidecar.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/docker/sidecar_test.py -->
# Research: sources/storage-engines/foundationdb/packaging/docker/sidecar_test.py

## Purpose
Unit/integration-style tests for the Docker sidecar HTTP handler and direct filesystem helper functions.

## Important APIs, Types, And Functions
`TestSidecar` starts a local `HTTPServer` with a `MagicMock` config. Tests exercise `SidecarHandler`, `check_hash`, and `is_present` using temporary output directories and `requests`.

## Control Flow
`setUp` allocates a free localhost port, configures no-TLS behavior, starts the server in a daemon thread, and each test makes real HTTP calls or direct helper calls. `tearDown` removes the temporary output directory.

## State And Persistence Behavior
Creates transient files under `tempfile.mkdtemp()` to verify hashes and nested file detection. No persistent repo state is changed.

## Dependencies And Integration Points
Depends on Python `unittest`, `requests`, `unittest.mock`, and the sibling `sidecar` module. This is the nearest automated signal for the sidecar HTTP contract used by Docker/Kubernetes startup probes and control calls.

## Risks And Edge Cases
The test server is not explicitly shut down, relying on daemon threads. TLS, certificate authorization, IPv6 binding, substitution rendering to monitor conf, and copy-binary/library behavior are not covered.

## Test Signals
Positive tests assert `/ready`, `/substitutions`, `/check_hash`, `/is_present`, and `POST /copy_files`; negative tests assert 404s and outside-path `RequestException`s.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/docker/sidecar_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/fdb.cluster.cmake -->
# Research: sources/storage-engines/foundationdb/packaging/fdb.cluster.cmake

## Purpose
CMake template for generating a default FoundationDB cluster file at build/package time.

## Important APIs, Types, And Functions
Contains a single cluster-file line with `${CLUSTER_DESCRIPTION1}` substituted into both the description and secret portions, pointing to `127.0.0.1:4500`.

## Control Flow
There is no executable flow; CMake configures the placeholder values into a concrete `fdb.cluster` file.

## State And Persistence Behavior
The generated cluster file is a persistent local coordinator connection string and secret. Its default localhost address is suitable for single-node/package initialization only.

## Dependencies And Integration Points
Consumed by CMake/package generation and later by `fdbcli`, `fdbserver`, and package scripts that install `/etc/foundationdb/fdb.cluster`. It aligns with package postinstall scripts that create new single-memory clusters on localhost.

## Risks And Edge Cases
The template must not be reused as a public cluster file without rewriting addresses and secrets. Placeholder expansion failures would create an invalid cluster file.

## Test Signals
No direct tests; downstream package install tests and `fdbcli -C` startup checks validate generated cluster-file usability.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/fdb.cluster.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/foundationdb.conf -->
# Research: sources/storage-engines/foundationdb/packaging/foundationdb.conf

## Purpose
Default Linux `fdbmonitor` configuration used by RPM and related packages.

## Important APIs, Types, And Functions
Defines `[fdbmonitor]` user/group, `[general]` restart and cluster-file settings, `[fdbserver]` command/public/listen/data/log defaults, `[fdbserver.4500]`, `[backup_agent]`, and `[backup_agent.1]`.

## Control Flow
`fdbmonitor` reads this file, starts `fdbserver` process `4500`, and starts one backup agent using inherited/default settings. Individual process sections override shared defaults.

## State And Persistence Behavior
Persists server data under `/var/lib/foundationdb/data/$ID`, logs under `/var/log/foundationdb`, and references `/etc/foundationdb/fdb.cluster`. Package managers mark it as config/noreplace in RPM flows.

## Dependencies And Integration Points
Integrated with `/usr/sbin/fdbmonitor`, `/usr/sbin/fdbserver`, `/usr/bin/backup_agent`, Linux service units, and package postinstall scripts that create the cluster file and service user. This is the package default for single-process local service startup.

## Risks And Edge Cases
Default `public-address = auto:$ID` and `listen-address = public` depend on runtime address detection. Changing commands, paths, or permissions in packages can break monitor startup. The backup section name differs from some Windows/macOS skeletons, so edits must preserve platform expectations.

## Test Signals
Validated indirectly by RPM/multiversion package install flows and FoundationDB service startup; no local unit test is attached to this static config.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/foundationdb.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/make_public.py -->
# Research: sources/storage-engines/foundationdb/packaging/make_public.py

## Purpose
Linux helper that rewrites a localhost-only FoundationDB cluster file to use a public IPv4 address and optionally append TLS address markers, then restarts the service.

## Important APIs, Types, And Functions
`getOrValidateAddress` selects or validates an address via UDP socket behavior. `makePublic` parses one non-comment cluster-file line, validates format and localhost coordinators with regexes, rewrites `127.0.0.1`, optionally adds `:tls`, and returns the selected address/TLS flag. `restartServer` invokes `service foundationdb restart`.

## Control Flow
CLI enforces Linux and root, parses `-C`, `-a`, and `-t`, calls `makePublic`, restarts the service, and prints the result. Invalid cluster files exit immediately.

## State And Persistence Behavior
Overwrites the cluster file in place and restarts the installed FoundationDB service. It does not back up the old cluster file.

## Dependencies And Integration Points
Depends on Python stdlib, root privileges, Linux service manager compatibility, DNS/network route to choose an address, and FoundationDB cluster-file syntax. Installed by RPM packaging under `/usr/lib/foundationdb` and used as an administrative utility after local package installation.

## Risks And Edge Cases
Regex validation accepts only IPv4-style coordinator addresses and assumes all coordinators are localhost. Automatic address selection attempts to connect to `www.foundationdb.org:80`, which can fail offline or choose an unexpected interface. In-place rewrite plus service restart makes partial failure operationally visible.

## Test Signals
No dedicated tests in this subset. Behavior should be covered by package/admin integration tests with sample cluster files, TLS and non-TLS cases, and invalid multi-line input.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/make_public.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/msi/CMakeLists.txt -->
# Research: sources/storage-engines/foundationdb/packaging/msi/CMakeLists.txt

## Purpose
CMake wiring for producing a Windows MSI installer with WiX when WiX tools are available.

## Important APIs, Types, And Functions
Finds `WIX`, configures `FDBInstaller.wxs` through `generate_wxs.cmake`, compiles it with `candle`, links with `light`, and registers custom targets `wix_file`, `wixobj`, and `installer` under the global `packages` target.

## Control Flow
The flow substitutes target paths for `fdbserver`, `fdbcli`, `fdbbackup`, optional `fdbmonitor`, and `fdb_c`, generates the WiX source, builds the WiX object, then emits `foundationdb-<version>[-SNAPSHOT]-<arch>.msi` into the package directory.

## State And Persistence Behavior
Writes generated installer intermediates under the CMake binary directory and final MSI under `packages`. It does not install system state itself.

## Dependencies And Integration Points
Depends on CMake generator expressions, `FindWIX`, WiX `candle`/`light`, built FoundationDB binaries, C client library, Python binding target, and the WiX template. Integrates the Windows packaging target with normal build artifacts and the repo-level `packages` target.

## Risks And Edge Cases
If WiX is missing, packaging silently downgrades to a warning. Optional `fdbmonitor` handling must match the template; missing or malformed target paths break MSI generation late. The template dependency references both `.wxs` and `.wxs.cmake`, so stale generated files are possible if dependency names drift.

## Test Signals
Validation is by CMake configure/build of the `installer` target on Windows with WiX installed; no unit test exists.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/msi/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/msi/FDBInstaller.wxs.cmake -->
# Research: sources/storage-engines/foundationdb/packaging/msi/FDBInstaller.wxs.cmake

## Purpose
WiX installer template for the Windows FoundationDB MSI, including client files, server service, config/data/log directories, registry values, environment variables, and Python binding installation.

## Important APIs, Types, And Functions
Defines product metadata, upgrade code, generated paths, known Python versions, component GUIDs, features, service install/control entries, IniFile edits, Python compile custom actions, random cluster-file creation, and new database configuration custom action.

## Control Flow
At install time WiX installs binaries and libraries under Program Files, creates CommonAppData `foundationdb` config/log/data directories, installs and starts `fdbmonitor` as a Windows service when the server feature is selected, optionally creates `fdb.cluster`, updates `foundationdb.conf`, compiles Python files, and runs `fdbcli configure new single memory; status` after services start.

## State And Persistence Behavior
Persistent state includes Program Files contents, PATH and `FOUNDATIONDB_INSTALL_PATH`, HKLM client/server version registry keys, CommonAppData config/data/log directories marked permanent, a Windows service, generated cluster file, and Python package files in detected Python installations.

## Dependencies And Integration Points
Depends on WiX schema/extensions, generated build paths, FoundationDB binaries, Python binding files, Python registry keys, and Windows service manager. This is the authoritative Windows MSI contract used by the CMake packaging target.

## Risks And Edge Cases
Permanent config/data/log components preserve state across uninstall and upgrade, which is intentional but can surprise tests. Python support lists old versions and custom install paths. Custom actions rely on command quoting and service readiness. Random cluster-file generation uses `%RANDOM%` rather than cryptographic entropy.

## Test Signals
Test signal is mainly MSI build/install smoke testing. The template has no direct parser tests; service startup and `ConfigureNewDatabase` success are the important acceptance checks.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/msi/FDBInstaller.wxs.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/msi/generate_wxs.cmake -->
# Research: sources/storage-engines/foundationdb/packaging/msi/generate_wxs.cmake

## Purpose
Small CMake script that normalizes configured paths for Windows and renders the WiX template.

## Important APIs, Types, And Functions
Uses `string(REPLACE ...)` to convert slashes to backslashes, derives `fdbc_lib` by replacing `dll` with `lib`, prints a status line, and calls `configure_file(... @ONLY NEWLINE_STYLE DOS)`.

## Control Flow
Called by the MSI CMake custom command with `-D` variables, transforms path variables, then writes the generated `.wxs` file.

## State And Persistence Behavior
Writes only the configured WiX XML output path supplied as `OUT`.

## Dependencies And Integration Points
Depends on CMake variable injection from `packaging/msi/CMakeLists.txt` and the `.wxs.cmake` input. Bridges portable CMake build paths to WiX/Windows path syntax.

## Risks And Edge Cases
The simple `dll` to `lib` replacement can affect unexpected substrings if paths contain `dll` elsewhere. Missing variables become empty strings and may create a syntactically valid but unusable installer.

## Test Signals
Validated by successful generation and WiX compilation in the `installer` target.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/msi/generate_wxs.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/msi/skeleton.conf -->
# Research: sources/storage-engines/foundationdb/packaging/msi/skeleton.conf

## Purpose
Windows MSI seed `foundationdb.conf` used when no existing CommonAppData config file exists.

## Important APIs, Types, And Functions
Defines monitor restart delay, server public/listen address, `parentpid`, a default `fdbserver.4500` section, backup-agent defaults, and one backup-agent process section.

## Control Flow
The MSI first installs this file, then WiX `IniFile` entries patch cluster-file, command, data, log, parentpid, and backup-agent command paths to the chosen install locations.

## State And Persistence Behavior
Becomes persistent CommonAppData configuration and is marked permanent by the installer flow; data/log paths are also created there.

## Dependencies And Integration Points
Depends on WiX template logic and `fdbmonitor` on Windows. Integrated with `FDBInstaller.wxs.cmake` as the initial config payload.

## Risks And Edge Cases
The skeleton is incomplete by design until MSI patching runs. Manual use without installer substitutions would leave missing command and cluster-file settings.

## Test Signals
Validated indirectly by MSI install and service start tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/msi/skeleton.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/multiversion/clients/postinst -->
# Research: sources/storage-engines/foundationdb/packaging/multiversion/clients/postinst

## Purpose
Debian-style postinstall hook for multiversion client packages.

## Important APIs, Types, And Functions
Creates CMake and pkg-config directories if needed, then registers `fdbcli` as the master `update-alternatives` entry `fdbclients` with slaves for backup/restore/dr tools, `libfdb_c.so`, pkg-config metadata, CMake config, and headers.

## Control Flow
Runs after package unpack; directory creation precedes one large `update-alternatives --install` command using version/build-time placeholders and priority.

## State And Persistence Behavior
Persists alternatives symlinks under `/usr/bin`, `/usr/<lib>/`, `/usr/include/foundationdb`, and alternatives database state.

## Dependencies And Integration Points
Depends on Debian `update-alternatives`, configured `@LIB_DIR@`, `@FDB_VERSION@`, `@FDB_BUILDTIME_STRING@`, and package install layout under `/usr/lib/foundationdb-*`. Enables multiple installed FoundationDB client versions to coexist while one version owns public command/library/header paths.

## Risks And Edge Cases
Directory creation lacks `-p` and unquoted pkg-config mkdir, so parent existence and whitespace assumptions matter. A failed alternatives command can leave package installed but public client links absent.

## Test Signals
Validated by package install/upgrade/remove tests checking alternatives registration and command resolution.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/multiversion/clients/postinst -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/multiversion/clients/prerm -->
# Research: sources/storage-engines/foundationdb/packaging/multiversion/clients/prerm

## Purpose
Pre-remove hook for multiversion client packages.

## Important APIs, Types, And Functions
Runs `update-alternatives --remove fdbclients` for this versioned `fdbcli` path.

## Control Flow
Executed before package removal to detach this version from the alternatives group.

## State And Persistence Behavior
Mutates Debian alternatives database and may switch public links to another installed version.

## Dependencies And Integration Points
Depends on `update-alternatives` and the same version/build-time substitution path used at install. Complements the multiversion client postinstall hook.

## Risks And Edge Cases
If the installed path template changes, removal can fail to remove the old alternative. No explicit error handling is present.

## Test Signals
Validated by install/remove alternatives tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/multiversion/clients/prerm -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/multiversion/server/postinst-deb -->
# Research: sources/storage-engines/foundationdb/packaging/multiversion/server/postinst-deb

## Purpose
Debian postinstall hook for multiversion server packages.

## Important APIs, Types, And Functions
Ensures the `foundationdb` system group/user, creates data/log directories with owner and mode, installs server alternatives for `fdbserver`, `fdbmonitor`, and init script, and initializes `/etc/foundationdb` on first install.

## Control Flow
After alternatives registration, `mkdir /etc/foundationdb` acts as the first-install gate. On first install it generates a random localhost cluster file, copies default config, fixes permissions, starts the init service, and configures a new single-memory database.

## State And Persistence Behavior
Persists system user/group, `/var/lib/foundationdb/data`, `/var/log/foundationdb`, `/etc/foundationdb/fdb.cluster`, `/etc/foundationdb/foundationdb.conf`, alternatives entries, and a running service.

## Dependencies And Integration Points
Depends on Debian `addgroup`, `adduser`, `update-alternatives`, init.d service, `fdbcli`, and versioned package layout. Integrates multiversion server binaries with a single active system service.

## Risks And Edge Cases
Using `mkdir /etc/foundationdb` as a first-install sentinel skips config initialization if the directory already exists but files are missing. Service start/configure failures are not guarded with recovery.

## Test Signals
Acceptance signal is package install on Debian with service start and `fdbcli status` after configure.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/multiversion/server/postinst-deb -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/multiversion/server/postinst-rpm -->
# Research: sources/storage-engines/foundationdb/packaging/multiversion/server/postinst-rpm

## Purpose
RPM postinstall hook for multiversion server packages.

## Important APIs, Types, And Functions
Creates the service user/group, prepares data/log dirs, ensures `/usr/lib/foundationdb`, registers alternatives for server binaries and systemd unit, and initializes `/etc/foundationdb` on first install.

## Control Flow
First-install flow generates `fdb.cluster`, copies `foundationdb.conf`, fixes ownership/modes, enables and starts `foundationdb` with systemd, and configures single-memory mode with `fdbcli`.

## State And Persistence Behavior
Persists service account, data/log/config directories, alternatives state, systemd service link, cluster file, and running database state.

## Dependencies And Integration Points
Depends on RPM environment tools, `groupadd`, `useradd`, `systemctl`, `update-alternatives`, and versioned install paths. Connects multiversion RPM server payloads to public systemd service management.

## Risks And Edge Cases
Same first-install sentinel risk as Debian: preexisting `/etc/foundationdb` prevents cluster/config creation. There is no explicit daemon-reload call after service alternative changes.

## Test Signals
Validated by RPM install/upgrade smoke tests checking systemd service and `fdbcli` configure.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/multiversion/server/postinst-rpm -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/multiversion/server/prerm -->
# Research: sources/storage-engines/foundationdb/packaging/multiversion/server/prerm

## Purpose
Pre-remove hook for multiversion server packages.

## Important APIs, Types, And Functions
Removes this versioned `fdbserver` from the alternatives group.

## Control Flow
Executed before package removal; alternatives may fall back to another installed server version.

## State And Persistence Behavior
Mutates alternatives database only.

## Dependencies And Integration Points
Depends on `update-alternatives` and correct version/build-time substitutions. Pairs with server postinstall alternatives registration.

## Risks And Edge Cases
Does not stop services itself; package manager ordering must ensure active service behavior is safe during removal or upgrade.

## Test Signals
Validated by multiversion remove/upgrade package tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/multiversion/server/prerm -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/osx/Distribution.xml -->
# Research: sources/storage-engines/foundationdb/packaging/osx/Distribution.xml

## Purpose
macOS productbuild distribution manifest for the combined FoundationDB installer UI.

## Important APIs, Types, And Functions
Defines package refs, background/title, minimum macOS version, root-volume install options, choices for clients and server, dependencies making server selectable only with clients, and conclusion resource.

## Control Flow
Productbuild reads this XML and composes `FoundationDB-clients.pkg` and `FoundationDB-server.pkg` into a user-customizable installer.

## State And Persistence Behavior
No runtime state itself; it controls which pkg payloads and scripts will run.

## Dependencies And Integration Points
Depends on `productbuild`, the two component packages, resource files, and `buildpkg.sh` which injects `hostArchitectures` with `sed`. This is the macOS installer front-end contract.

## Risks And Edge Cases
The build script mutates this source file in place to add host architecture, creating potential dirty-tree/stale XML risk. Minimum OS and choice dependencies are static and may drift.

## Test Signals
Validated by successful `productbuild` and interactive/silent install tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/osx/Distribution.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/osx/buildpkg.sh -->
# Research: sources/storage-engines/foundationdb/packaging/osx/buildpkg.sh

## Purpose
Builds macOS FoundationDB client and server component packages and combines them into a product installer.

## Important APIs, Types, And Functions
Accepts build and source directories, reads `version.txt`, creates temporary roots, installs client binaries/libraries/headers/Python bindings/backup symlinks/uninstaller, builds `FoundationDB-clients.pkg`, installs server binaries/config/plist/data/log dirs, builds `FoundationDB-server.pkg`, edits `Distribution.xml`, then runs `productbuild`.

## Control Flow
The script exits on errors, removes temporary roots after each component build, and removes intermediate pkg files after productbuild.

## State And Persistence Behavior
Writes package artifacts into `<build>/packages`, temporary filesystem roots, symlinks inside payloads, and mutates `packaging/osx/Distribution.xml` in the source tree.

## Dependencies And Integration Points
Depends on macOS `pkgbuild`, `productbuild`, BSD `sed -i`, built FoundationDB binaries, Python binding files, and packaging resources/scripts. Integrates CMake build artifacts with native macOS installer tooling.

## Risks And Edge Cases
In-place editing of `Distribution.xml` is the main repo-state risk. Unquoted install destinations and legacy Python 2.7 payload paths can break on modern macOS assumptions. Temporary root cleanup is manual after package creation.

## Test Signals
Validated by running the script on macOS and installing the generated pkg, including LaunchDaemon startup.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/osx/buildpkg.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/osx/scripts-clients/postinstall -->
# Research: sources/storage-engines/foundationdb/packaging/osx/scripts-clients/postinstall

## Purpose
macOS clients package postinstall script for Python bindings.

## Important APIs, Types, And Functions
Runs `/usr/bin/python -m compileall /Library/Python/2.7/site-packages/fdb` and exits 0.

## Control Flow
Executed by Installer after client payload installation.

## State And Persistence Behavior
Creates `.pyc` files under the installed Python 2.7 site-packages directory.

## Dependencies And Integration Points
Depends on system Python at `/usr/bin/python` and the installed `fdb` package directory. Complements the macOS client payload from `buildpkg.sh`.

## Risks And Edge Cases
Modern macOS may not provide Python 2.7 at this path. Compile failures would fail the package unless Installer tolerates the script behavior.

## Test Signals
Validated by macOS package install smoke tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/osx/scripts-clients/postinstall -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/osx/scripts-server/postinstall -->
# Research: sources/storage-engines/foundationdb/packaging/osx/scripts-server/postinstall

## Purpose
macOS server package postinstall script that finalizes config, loads the LaunchDaemon, and configures a new local database on first install.

## Important APIs, Types, And Functions
Generates `/usr/local/etc/foundationdb/fdb.cluster` if absent, restores `.old` config or promotes `.new`, loads `com.foundationdb.fdbmonitor.plist`, and runs `fdbcli configure new single memory` for new databases.

## Control Flow
First-install detection is based on absent cluster file. Config selection happens before service load; database configuration runs after launchctl load.

## State And Persistence Behavior
Persists cluster file, config file, loaded LaunchDaemon state, and initialized database state under `/usr/local/foundationdb`.

## Dependencies And Integration Points
Depends on launchctl, `/usr/local/bin/fdbcli`, package-installed plist, and config payload. Complements server `preinstall` and server payload generation.

## Risks And Edge Cases
Uses `$NEWDB` without initialization under `set -u` absent, so empty is okay but shellcheck would flag it. Service readiness before `fdbcli` configure is assumed. Existing broken config/cluster files skip recovery.

## Test Signals
Validated by macOS server install tests checking LaunchDaemon and single-memory configure.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/osx/scripts-server/postinstall -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/osx/scripts-server/preinstall -->
# Research: sources/storage-engines/foundationdb/packaging/osx/scripts-server/preinstall

## Purpose
macOS server package preinstall script that prepares for replacing the service/config.

## Important APIs, Types, And Functions
Attempts to create data/log directories using `$SERVERDIR`, unloads an existing LaunchDaemon plist, and moves existing config to `.old`.

## Control Flow
Runs before payload install, stopping the old service first and preserving config for postinstall restoration.

## State And Persistence Behavior
Mutates LaunchDaemon runtime state and renames `/usr/local/etc/foundationdb/foundationdb.conf` to `.old`.

## Dependencies And Integration Points
Depends on launchctl and existing macOS installation paths. Pairs with server postinstall which restores `.old` or promotes `.new`.

## Risks And Edge Cases
`$SERVERDIR` is not normally defined in installer script context, so the initial `mkdir` lines look ineffective or dangerous if unset. Config rename is not atomic across failures between preinstall and postinstall.

## Test Signals
Validated by upgrade/reinstall package tests, especially config preservation.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/osx/scripts-server/preinstall -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/osx/uninstall-FoundationDB.sh -->
# Research: sources/storage-engines/foundationdb/packaging/osx/uninstall-FoundationDB.sh

## Purpose
Manual macOS uninstall script for FoundationDB binaries, libraries, headers, bindings, LaunchDaemon, and receipts.

## Important APIs, Types, And Functions
Removes installed executables, `libfdb_c.dylib`, headers, backup agent directory, uninstall script, Python 2.7 bindings, unloads/removes the LaunchDaemon plist, and removes package receipts.

## Control Flow
Performs destructive file removals first with shell tracing, then reports preserved data/config directories if data remains.

## State And Persistence Behavior
Deletes installed program files but intentionally preserves `/usr/local/foundationdb/data` and `/usr/local/etc/foundationdb` unless the user removes them manually.

## Dependencies And Integration Points
Depends on macOS filesystem layout and launchctl. Installed into `/usr/local/foundationdb` by the client package.

## Risks And Edge Cases
Brace expansion and broad receipt globbing assume bash and expected package IDs. Running as non-root may partially remove files. It does not remove `/usr/local/bin/backup_agent` if only symlink names listed omit it.

## Test Signals
Validated manually or by install/uninstall smoke tests checking no service remains and data preservation message appears.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/osx/uninstall-FoundationDB.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/rpm/buildrpms.sh -->
# Research: sources/storage-engines/foundationdb/packaging/rpm/buildrpms.sh

## Purpose
Builds FoundationDB RPMs from an already-built tree by staging install files and running `rpmbuild` with a generated spec.

## Important APIs, Types, And Functions
Accepts `VERSION` and `RELEASE`, creates temp RPM topdir and install root, installs config, init/systemd service, binaries, libraries, C headers, docs, backup-agent symlinks, and `make_public.py`, tars the install root, expands `foundationdb.spec.in` through `m4`, builds with `fakeroot rpmbuild`, and copies RPMs to `packages`.

## Control Flow
The script runs linearly under `set` default behavior, with trap cleanup for temp dirs and a fixed `.el9` release suffix.

## State And Persistence Behavior
Writes staged files in temp dirs and final RPMs into `packages`; no system install state is modified by build.

## Dependencies And Integration Points
Depends on bash, mktemp, install, dos2unix, tar, m4, fakeroot, rpmbuild, and build outputs in `bin/`, `lib/`, `bindings/c`, and docs. Connects source/build artifacts to `foundationdb.spec.in` package metadata and scriptlets.

## Risks And Edge Cases
Lacks explicit argument validation and `set -e`; missing files may lead to partial or late failures. Hard-coded `/usr/lib64` and `.el9` limit portability.

## Test Signals
Validated by RPM build and subsequent install tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/rpm/buildrpms.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/rpm/foundationdb-init -->
# Research: sources/storage-engines/foundationdb/packaging/rpm/foundationdb-init

## Purpose
Legacy SysV init script for running `fdbmonitor` on RPM systems without systemd or for compatibility.

## Important APIs, Types, And Functions
Defines `start`, `stop`, `restart`, `condrestart`, and `status` using `/etc/rc.d/init.d/functions`, `/usr/sbin/fdbmonitor`, config `/etc/foundationdb/foundationdb.conf`, and pidfile `/var/run/fdbmonitor.pid`.

## Control Flow
Case dispatch maps service commands to daemon start/killproc/status behavior and maintains `/var/lock/subsys/foundationdb`.

## State And Persistence Behavior
Mutates process state, pidfile/lockfile state, and starts/stops monitor-managed FDB server processes.

## Dependencies And Integration Points
Depends on Red Hat init functions and the installed monitor/config paths. Included in RPM staging and referenced by non-systemd scriptlets.

## Risks And Edge Cases
`eval daemon` expands command text and should remain tightly controlled. Long stop delay is 300 seconds. Systems with systemd primarily use the unit instead.

## Test Signals
Validated by service start/stop/status smoke tests on SysV-compatible systems.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/rpm/foundationdb-init -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/rpm/foundationdb.service -->
# Research: sources/storage-engines/foundationdb/packaging/rpm/foundationdb.service

## Purpose
systemd unit for the RPM-installed FoundationDB service.

## Important APIs, Types, And Functions
Declares network-online ordering, forking service type, pidfile, `ExecStart` invoking `fdbmonitor` with config and lockfile, mixed kill mode, and restart-on-failure with 60 second delay.

## Control Flow
systemd starts the monitor, tracks the pidfile, and restarts the service on failures.

## State And Persistence Behavior
Maintains runtime process/pidfile state and controls monitor-managed server processes; persistent config lives in `/etc/foundationdb`.

## Dependencies And Integration Points
Depends on systemd, `/usr/sbin/fdbmonitor`, config file, and writable `/var/run` pidfile path. Installed by RPM and enabled/started by postinstall scripts.

## Risks And Edge Cases
For `Type=forking`, pidfile creation must be reliable. No hardening directives are present. `After=network-online.target` does not guarantee DNS or coordinator reachability.

## Test Signals
Validated by systemctl enable/start/status during package install tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/rpm/foundationdb.service -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/rpm/foundationdb.spec.in -->
# Research: sources/storage-engines/foundationdb/packaging/rpm/foundationdb.spec.in

## Purpose
RPM spec template defining FoundationDB server and clients subpackages, scriptlets, file ownership, and package metadata.

## Important APIs, Types, And Functions
Contains `%package server`, `%package clients`, `%prep`, `%pre/%post/%preun` scriptlets, `%files` manifests, service/config/data/log ownership, and placeholders `FDBVERSION`/`FDBRELEASE` expanded by `m4`.

## Control Flow
Build prep extracts staged files. Server pre creates service user and handles old-version config. Server post creates cluster file on first install, enables/starts systemd service, and configures new single-memory database. Preun stops/disables on erase. Client pre creates user/group and post removes stale Python 2.6 files.

## State And Persistence Behavior
Persistent install state includes service account, config/cluster file, service unit, binaries/libraries/headers, docs, data/log dirs with FoundationDB ownership, and running service/database state.

## Dependencies And Integration Points
Depends on RPM scriptlet semantics, systemd, fdbcli/fdbmonitor, staged `install-files.tar.gz`, and RPM macros. Generated and consumed by `buildrpms.sh` for EL9-style RPM packages.

## Risks And Edge Cases
`AutoReq: 0` suppresses automatic dependency discovery broadly. Scriptlets assume systemd paths and do not handle non-systemd in this inlined version. `$NEWDB` is tested even if unset but shell permits it. First-install recovery is limited.

## Test Signals
Validated by rpmbuild plus install/upgrade/remove tests checking files, service, and database configure.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/rpm/foundationdb.spec.in -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/rpm/scripts/postclients.sh -->
# Research: sources/storage-engines/foundationdb/packaging/rpm/scripts/postclients.sh

## Purpose
Standalone client postinstall script fragment for RPM packaging.

## Important APIs, Types, And Functions
Deletes stale `/usr/lib64/python2.6/fdb` from old packages and exits 0.

## Control Flow
Runs after client package installation.

## State And Persistence Behavior
Removes old Python binding directory if present.

## Dependencies And Integration Points
Depends on RPM scriptlet execution and legacy Python path assumptions. Mirrors the `%post clients` fragment in the spec.

## Risks And Edge Cases
Broad `rm -rf` is scoped to a specific legacy directory but still destructive. No check is made for symlinks.

## Test Signals
Validated by upgrade tests from affected old packages.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/rpm/scripts/postclients.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/rpm/scripts/postserver.sh -->
# Research: sources/storage-engines/foundationdb/packaging/rpm/scripts/postserver.sh

## Purpose
Standalone server postinstall script fragment for RPM packaging.

## Important APIs, Types, And Functions
On initial install, creates cluster file if absent, fixes ownership/mode, enables and starts systemd service, and configures single-memory mode for new DBs; on upgrade, conditionally restarts service.

## Control Flow
Uses RPM `$1` scriptlet argument to distinguish install from upgrade.

## State And Persistence Behavior
Persists cluster file and service enable/start state; may initialize database.

## Dependencies And Integration Points
Depends on `systemctl`, `fdbcli`, `/etc/foundationdb`, and `foundationdb` user/group. Equivalent to the server `%post` body in spec-style packaging.

## Risks And Edge Cases
Assumes `/etc/foundationdb` exists. `$NEWDB` is unset in non-new cases but shell permits test. Configure output is suppressed, hiding diagnostics.

## Test Signals
Validated by RPM install/upgrade service smoke tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/rpm/scripts/postserver.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/rpm/scripts/preclients.sh -->
# Research: sources/storage-engines/foundationdb/packaging/rpm/scripts/preclients.sh

## Purpose
Standalone client preinstall script fragment for RPM packaging.

## Important APIs, Types, And Functions
Ensures `foundationdb` group and user exist, with home `/var/lib/foundationdb`, shell `/bin/false`, and exits 0.

## Control Flow
Runs before client package install so shared config directories can be owned by the service user/group.

## State And Persistence Behavior
Persists system group/user if absent.

## Dependencies And Integration Points
Depends on `getent`, `groupadd`, and `useradd`. Mirrors the `%pre clients` scriptlet.

## Risks And Edge Cases
Does not validate existing user attributes if a `foundationdb` account already exists.

## Test Signals
Validated by package install tests on clean and preexisting-account systems.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/rpm/scripts/preclients.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/rpm/scripts/preserver.sh -->
# Research: sources/storage-engines/foundationdb/packaging/rpm/scripts/preserver.sh

## Purpose
Standalone server preinstall/preun-style fragment handling user creation, legacy cleanup, config migration, and service removal on erase.

## Important APIs, Types, And Functions
Creates service account, removes old bundled `argparse.py` on upgrade, saves very old configs, and when `$1 -eq 0` stops/disables the service via systemd or SysV tools.

## Control Flow
Uses RPM `$1` to distinguish upgrade/install/erase actions and probes `pidof systemd` for service manager.

## State And Persistence Behavior
Mutates service account state, `/usr/lib/foundationdb` cleanup files, `/etc/foundationdb/foundationdb.conf.rpmsave`, and service enable/running state.

## Dependencies And Integration Points
Depends on RPM arguments, rpm query command, systemd/SysV service tools, and account tools. Overlaps with spec `%pre server` and `%preun server` logic for split script packaging.

## Risks And Edge Cases
Moving config for only versions 0.1.4/0.1.5 is narrow. `pidof systemd` is an imprecise container/systemd check. Service stop errors are suppressed.

## Test Signals
Validated by upgrade from old versions and uninstall tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/rpm/scripts/preserver.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/rpm/scripts/preunserver.sh -->
# Research: sources/storage-engines/foundationdb/packaging/rpm/scripts/preunserver.sh

## Purpose
Standalone server preuninstall script fragment for RPM packaging.

## Important APIs, Types, And Functions
On erase (`$1 -eq 0`), stops and disables the `foundationdb` service using systemd when present or SysV service/chkconfig otherwise.

## Control Flow
Runs before package removal to prevent `fdbmonitor` from continuing after binaries are removed.

## State And Persistence Behavior
Mutates service running/enabled state only.

## Dependencies And Integration Points
Depends on RPM scriptlet argument, `pidof`, `systemctl`, `/sbin/service`, and `chkconfig`. Complements RPM server package removal.

## Risks And Edge Cases
Service manager detection is simplistic and all service errors are suppressed, so removal can proceed with a still-running process.

## Test Signals
Validated by RPM erase tests checking service is stopped/disabled.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/rpm/scripts/preunserver.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/go-recipes/blob.go -->
# Research: sources/storage-engines/foundationdb/recipes/go-recipes/blob.go

## Purpose
Go recipe example that stores a large logical value by splitting it into fixed-size chunks keyed by chunk offset.

## Important APIs, Types, And Functions
`write_blob`, `read_blob`, `CHUNK_SIZE`, and `main` using `directory.CreateOrOpen`.

## Control Flow
`main` selects FoundationDB API version 800, opens the default database, creates/opens a directory or subspace, clears demo state where needed, performs a small smoke scenario, and prints results. Core operations run inside `Transact` or `ReadTransact`; write helpers split non-empty input into chunks and read helpers scan the blob subspace in key order and concatenate values.

## State And Persistence Behavior
Persistent state is one key per chunk in a blob subspace; callers must clear old chunks before overwriting with shorter data or stale chunks can remain.

## Dependencies And Integration Points
Depends on the Go FoundationDB bindings (`fdb`, `directory`, `subspace`, `tuple`) and a reachable default cluster. These examples integrate with the recipe-book style API demonstrations rather than production packages.

## Risks And Edge Cases
Example code favors clarity over robustness: many errors are ignored or panicked, transaction conflicts are left to binding retries, and some type assertions are narrow. It should not be treated as a production library without stronger validation.

## Test Signals
The file contains an executable smoke test in `main`, but no automated assertion harness in this subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/go-recipes/blob.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/go-recipes/doc.go -->
# Research: sources/storage-engines/foundationdb/recipes/go-recipes/doc.go

## Purpose
Go recipe example that maps nested JSON/document structures to tuple-addressed leaves.

## Important APIs, Types, And Functions
`ToTuples`, `FromTuples`, `Doc.InsertDoc`, `Doc.GetDoc`, `_GetNewID`, `clear_subspace`, `print_subspace`.

## Control Flow
`main` selects FoundationDB API version 800, opens the default database, creates/opens a directory or subspace, clears demo state where needed, performs a small smoke scenario, and prints results. Core operations run inside `Transact` or `ReadTransact`; conversion helpers flatten arrays/maps into path tuples, insert assigns or preserves `doc_id`, and retrieval scans a document prefix and reconstructs the object.

## State And Persistence Behavior
Persistent state is one key per document leaf under `(doc_id, path...)`; random ID allocation scans for collisions but is example-grade.

## Dependencies And Integration Points
Depends on the Go FoundationDB bindings (`fdb`, `directory`, `subspace`, `tuple`) and a reachable default cluster. These examples integrate with the recipe-book style API demonstrations rather than production packages.

## Risks And Edge Cases
Example code favors clarity over robustness: many errors are ignored or panicked, transaction conflicts are left to binding retries, and some type assertions are narrow. It should not be treated as a production library without stronger validation.

## Test Signals
The file contains an executable smoke test in `main`, but no automated assertion harness in this subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/go-recipes/doc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/go-recipes/graph.go -->
# Research: sources/storage-engines/foundationdb/recipes/go-recipes/graph.go

## Purpose
Go recipe example that models directed graph adjacency with forward and inverse indexes.

## Important APIs, Types, And Functions
`Graph.NewGraph`, `set_edge`, `del_edge`, `get_out_neighbors`, `get_in_neighbors`, `clear_subspace`.

## Control Flow
`main` selects FoundationDB API version 800, opens the default database, creates/opens a directory or subspace, clears demo state where needed, performs a small smoke scenario, and prints results. Core operations run inside `Transact` or `ReadTransact`; edge setters write both forward and inverse keys, delete clears both, and neighbor reads scan the relevant prefix.

## State And Persistence Behavior
Persistent state duplicates each edge in two subspaces, so both writes must remain transactionally paired.

## Dependencies And Integration Points
Depends on the Go FoundationDB bindings (`fdb`, `directory`, `subspace`, `tuple`) and a reachable default cluster. These examples integrate with the recipe-book style API demonstrations rather than production packages.

## Risks And Edge Cases
Example code favors clarity over robustness: many errors are ignored or panicked, transaction conflicts are left to binding retries, and some type assertions are narrow. It should not be treated as a production library without stronger validation.

## Test Signals
The file contains an executable smoke test in `main`, but no automated assertion harness in this subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/go-recipes/graph.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/go-recipes/indirect.go -->
# Research: sources/storage-engines/foundationdb/recipes/go-recipes/indirect.go

## Purpose
Go recipe example that demonstrates directory-layer indirection for atomic workspace replacement.

## Important APIs, Types, And Functions
`Workspace.GetCurrent`, `Workspace.Session`, `_Update`, `clear_subspace`, `print_subspace`.

## Control Flow
`main` selects FoundationDB API version 800, opens the default database, creates/opens a directory or subspace, clears demo state where needed, performs a small smoke scenario, and prints results. Core operations run inside `Transact` or `ReadTransact`; a workspace writes to a `new` directory and then removes `current` and moves `new` to `current` inside a transaction.

## State And Persistence Behavior
Persistent state is directory-layer metadata plus data under current/new directories; failures before the move leave old current intact.

## Dependencies And Integration Points
Depends on the Go FoundationDB bindings (`fdb`, `directory`, `subspace`, `tuple`) and a reachable default cluster. These examples integrate with the recipe-book style API demonstrations rather than production packages.

## Risks And Edge Cases
Example code favors clarity over robustness: many errors are ignored or panicked, transaction conflicts are left to binding retries, and some type assertions are narrow. It should not be treated as a production library without stronger validation.

## Test Signals
The file contains an executable smoke test in `main`, but no automated assertion harness in this subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/go-recipes/indirect.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/go-recipes/multi.go -->
# Research: sources/storage-engines/foundationdb/recipes/go-recipes/multi.go

## Purpose
Go recipe example that implements a multimap/multiset using atomic add counters.

## Important APIs, Types, And Functions
`MultiMap.NewMultiMap`, `MultiAdd`, `MultiSubtract`, `MultiGet`, `MultiGetCounts`, `MultiIsElement`.

## Control Flow
`main` selects FoundationDB API version 800, opens the default database, creates/opens a directory or subspace, clears demo state where needed, performs a small smoke scenario, and prints results. Core operations run inside `Transact` or `ReadTransact`; add increments a tuple key, subtract decrements or clears at zero, and reads scan an index prefix for members and counts.

## State And Persistence Behavior
Persistent state stores little-endian counters by `(index, value)`; counter encoding and zero cleanup are correctness-sensitive.

## Dependencies And Integration Points
Depends on the Go FoundationDB bindings (`fdb`, `directory`, `subspace`, `tuple`) and a reachable default cluster. These examples integrate with the recipe-book style API demonstrations rather than production packages.

## Risks And Edge Cases
Example code favors clarity over robustness: many errors are ignored or panicked, transaction conflicts are left to binding retries, and some type assertions are narrow. It should not be treated as a production library without stronger validation.

## Test Signals
The file contains an executable smoke test in `main`, but no automated assertion harness in this subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/go-recipes/multi.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/go-recipes/priority.go -->
# Research: sources/storage-engines/foundationdb/recipes/go-recipes/priority.go

## Purpose
Go recipe example that implements a priority queue ordered by tuple keys.

## Important APIs, Types, And Functions
`Priority.Push`, `_NextCount`, `Pop`, `Peek`, `_pack`, `_unpack`.

## Control Flow
`main` selects FoundationDB API version 800, opens the default database, creates/opens a directory or subspace, clears demo state where needed, performs a small smoke scenario, and prints results. Core operations run inside `Transact` or `ReadTransact`; push writes `(priority, sequence, random)` keys, `peek` and `pop` scan one key from the front or back, and pop clears the selected key.

## State And Persistence Behavior
Persistent state is queue entries in priority order; sequence generation uses snapshot/range reads and random suffixes to reduce collisions.

## Dependencies And Integration Points
Depends on the Go FoundationDB bindings (`fdb`, `directory`, `subspace`, `tuple`) and a reachable default cluster. These examples integrate with the recipe-book style API demonstrations rather than production packages.

## Risks And Edge Cases
Example code favors clarity over robustness: many errors are ignored or panicked, transaction conflicts are left to binding retries, and some type assertions are narrow. It should not be treated as a production library without stronger validation.

## Test Signals
The file contains an executable smoke test in `main`, but no automated assertion harness in this subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/go-recipes/priority.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/go-recipes/queue.go -->
# Research: sources/storage-engines/foundationdb/recipes/go-recipes/queue.go

## Purpose
Go recipe example that implements a FIFO queue on ordered tuple keys.

## Important APIs, Types, And Functions
`Queue.Enqueue`, `Dequeue`, `LastIndex`, `FirstItem`, `EmptyQueueError`.

## Control Flow
`main` selects FoundationDB API version 800, opens the default database, creates/opens a directory or subspace, clears demo state where needed, performs a small smoke scenario, and prints results. Core operations run inside `Transact` or `ReadTransact`; enqueue finds the last index with a snapshot reverse read and writes the next key with random tie-breaker where available; dequeue reads and clears the first item.

## State And Persistence Behavior
Persistent state is queue entries ordered by index; concurrent enqueue contention and empty queue behavior are example-level concerns.

## Dependencies And Integration Points
Depends on the Go FoundationDB bindings (`fdb`, `directory`, `subspace`, `tuple`) and a reachable default cluster. These examples integrate with the recipe-book style API demonstrations rather than production packages.

## Risks And Edge Cases
Example code favors clarity over robustness: many errors are ignored or panicked, transaction conflicts are left to binding retries, and some type assertions are narrow. It should not be treated as a production library without stronger validation.

## Test Signals
The file contains an executable smoke test in `main`, but no automated assertion harness in this subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/go-recipes/queue.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/go-recipes/table.go -->
# Research: sources/storage-engines/foundationdb/recipes/go-recipes/table.go

## Purpose
Go recipe example that implements a two-dimensional table with row and column indexes.

## Important APIs, Types, And Functions
`Table.NewTable`, `TableSetCell`, `TableGetCell`, `TableSetRow`, `TableGetRow`, `TableGetCol`.

## Control Flow
`main` selects FoundationDB API version 800, opens the default database, creates/opens a directory or subspace, clears demo state where needed, performs a small smoke scenario, and prints results. Core operations run inside `Transact` or `ReadTransact`; set cell writes both row and column keys, row/column reads scan prefixes, and row replacement clears a row prefix before rewriting cells.

## State And Persistence Behavior
Persistent state duplicates cell values in row and column indexes, so mutations must update both indexes in one transaction.

## Dependencies And Integration Points
Depends on the Go FoundationDB bindings (`fdb`, `directory`, `subspace`, `tuple`) and a reachable default cluster. These examples integrate with the recipe-book style API demonstrations rather than production packages.

## Risks And Edge Cases
Example code favors clarity over robustness: many errors are ignored or panicked, transaction conflicts are left to binding retries, and some type assertions are narrow. It should not be treated as a production library without stronger validation.

## Test Signals
The file contains an executable smoke test in `main`, but no automated assertion harness in this subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/go-recipes/table.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/java-recipes/MicroBlob.java -->
# Research: sources/storage-engines/foundationdb/recipes/java-recipes/MicroBlob.java

## Purpose
Java recipe example that stores a string blob as chunked FoundationDB values.

## Important APIs, Types, And Functions
`writeBlob`, `readBlob`, `clearSubspace`, `CHUNK_SIZE`

## Control Flow
Static initializer selects API 300 and opens DB/subspace; main clears the blob, writes alphabet data, reads by scanning chunk keys, and prints.

## State And Persistence Behavior
Persistent state is stored in fixed FoundationDB subspaces selected by tuple prefixes; most examples clear those subspaces before the smoke scenario. Multi-index examples duplicate values/edges across indexes inside one transaction.

## Dependencies And Integration Points
Depends on Java FoundationDB bindings (`com.foundationdb.*`, `Subspace`, `Tuple`, async `Function`) and a reachable default cluster. Part of the language recipe collection and mirrors concepts also shown in Go, Python, and Ruby recipes.

## Risks And Edge Cases
Example code uses old Java FoundationDB API 300, static global database/subspaces, minimal error handling, and fixed demo subspaces. It is suitable as documentation/sample code, not a reusable library without transaction/error hardening.

## Test Signals
Each class has a `main` or smoke-test path except the skeletal `MicroSpatial`; there is no JUnit harness in this subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/java-recipes/MicroBlob.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/java-recipes/MicroDoc.java -->
# Research: sources/storage-engines/foundationdb/recipes/java-recipes/MicroDoc.java

## Purpose
Java recipe example that serializes nested maps/lists to tuple-addressed document leaves.

## Important APIs, Types, And Functions
`toTuples`, `fromTuples`, `insertDoc`, `getDoc`, `getNewID`, `printSubspace`, `clearSubspace`, `smokeTest`

## Control Flow
Smoke test builds nested user data, inserts it under a random or supplied `doc_id`, scans prefixes to reconstruct documents, and prints paths.

## State And Persistence Behavior
Persistent state is stored in fixed FoundationDB subspaces selected by tuple prefixes; most examples clear those subspaces before the smoke scenario. Multi-index examples duplicate values/edges across indexes inside one transaction.

## Dependencies And Integration Points
Depends on Java FoundationDB bindings (`com.foundationdb.*`, `Subspace`, `Tuple`, async `Function`) and a reachable default cluster. Part of the language recipe collection and mirrors concepts also shown in Go, Python, and Ruby recipes.

## Risks And Edge Cases
Example code uses old Java FoundationDB API 300, static global database/subspaces, minimal error handling, and fixed demo subspaces. It is suitable as documentation/sample code, not a reusable library without transaction/error hardening.

## Test Signals
Each class has a `main` or smoke-test path except the skeletal `MicroSpatial`; there is no JUnit harness in this subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/java-recipes/MicroDoc.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/java-recipes/MicroGraph.java -->
# Research: sources/storage-engines/foundationdb/recipes/java-recipes/MicroGraph.java

## Purpose
Java recipe example that models directed, weighted, and derived graph indexes.

## Important APIs, Types, And Functions
`setEdge`, `deleteEdge`, `getOutNeighbors`, `getInNeighbors`, `setEdgeWeighted`, `updateEdgeWeight`, `getWeight`, `setNeighborNeighbors`, `smokeTest`

## Control Flow
Operations write forward/inverse adjacency keys, weighted edge values with little-endian mutation ADD, and path-two examples; smoke test prints graph and weight changes.

## State And Persistence Behavior
Persistent state is stored in fixed FoundationDB subspaces selected by tuple prefixes; most examples clear those subspaces before the smoke scenario. Multi-index examples duplicate values/edges across indexes inside one transaction.

## Dependencies And Integration Points
Depends on Java FoundationDB bindings (`com.foundationdb.*`, `Subspace`, `Tuple`, async `Function`) and a reachable default cluster. Part of the language recipe collection and mirrors concepts also shown in Go, Python, and Ruby recipes.

## Risks And Edge Cases
Example code uses old Java FoundationDB API 300, static global database/subspaces, minimal error handling, and fixed demo subspaces. It is suitable as documentation/sample code, not a reusable library without transaction/error hardening.

## Test Signals
Each class has a `main` or smoke-test path except the skeletal `MicroSpatial`; there is no JUnit harness in this subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/java-recipes/MicroGraph.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/java-recipes/MicroIndexes.java -->
# Research: sources/storage-engines/foundationdb/recipes/java-recipes/MicroIndexes.java

## Purpose
Java recipe example that demonstrates maintaining a secondary zipcode index for users.

## Important APIs, Types, And Functions
`setUser`, `getUser`, `getUserIDsInRegion`, `clearSubspace`

## Control Flow
Writes primary `(ID, zipcode)->name` and secondary `(zipcode, ID)` keys, then reads either by primary prefix or index prefix.

## State And Persistence Behavior
Persistent state is stored in fixed FoundationDB subspaces selected by tuple prefixes; most examples clear those subspaces before the smoke scenario. Multi-index examples duplicate values/edges across indexes inside one transaction.

## Dependencies And Integration Points
Depends on Java FoundationDB bindings (`com.foundationdb.*`, `Subspace`, `Tuple`, async `Function`) and a reachable default cluster. Part of the language recipe collection and mirrors concepts also shown in Go, Python, and Ruby recipes.

## Risks And Edge Cases
Example code uses old Java FoundationDB API 300, static global database/subspaces, minimal error handling, and fixed demo subspaces. It is suitable as documentation/sample code, not a reusable library without transaction/error hardening.

## Test Signals
Each class has a `main` or smoke-test path except the skeletal `MicroSpatial`; there is no JUnit harness in this subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/java-recipes/MicroIndexes.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/java-recipes/MicroIndirect.java -->
# Research: sources/storage-engines/foundationdb/recipes/java-recipes/MicroIndirect.java

## Purpose
Java recipe example that demonstrates directory-layer workspace replacement.

## Important APIs, Types, And Functions
`Workspace.getCurrent`, `getNew`, `replaceWithNew`, `clearSubspace`, `printSubspace`

## Control Flow
Creates current/new directory subspaces, writes demo data, then removes current and moves new to current using chained futures in a transaction.

## State And Persistence Behavior
Persistent state is stored in fixed FoundationDB subspaces selected by tuple prefixes; most examples clear those subspaces before the smoke scenario. Multi-index examples duplicate values/edges across indexes inside one transaction.

## Dependencies And Integration Points
Depends on Java FoundationDB bindings (`com.foundationdb.*`, `Subspace`, `Tuple`, async `Function`) and a reachable default cluster. Part of the language recipe collection and mirrors concepts also shown in Go, Python, and Ruby recipes.

## Risks And Edge Cases
Example code uses old Java FoundationDB API 300, static global database/subspaces, minimal error handling, and fixed demo subspaces. It is suitable as documentation/sample code, not a reusable library without transaction/error hardening.

## Test Signals
Each class has a `main` or smoke-test path except the skeletal `MicroSpatial`; there is no JUnit harness in this subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/java-recipes/MicroIndirect.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/java-recipes/MicroMulti.java -->
# Research: sources/storage-engines/foundationdb/recipes/java-recipes/MicroMulti.java

## Purpose
Java recipe example that implements a multiset-style multimap with atomic counters.

## Important APIs, Types, And Functions
`add`, `subtract`, `get`, `getCounts`, `isElement`, `addHelp`, `getLong`, `clearSubspace`

## Control Flow
Atomic ADD changes 8-byte little-endian counters, subtract clears at count <= 1, reads scan `(index,value)` prefixes, and main times add/subtract operations.

## State And Persistence Behavior
Persistent state is stored in fixed FoundationDB subspaces selected by tuple prefixes; most examples clear those subspaces before the smoke scenario. Multi-index examples duplicate values/edges across indexes inside one transaction.

## Dependencies And Integration Points
Depends on Java FoundationDB bindings (`com.foundationdb.*`, `Subspace`, `Tuple`, async `Function`) and a reachable default cluster. Part of the language recipe collection and mirrors concepts also shown in Go, Python, and Ruby recipes.

## Risks And Edge Cases
Example code uses old Java FoundationDB API 300, static global database/subspaces, minimal error handling, and fixed demo subspaces. It is suitable as documentation/sample code, not a reusable library without transaction/error hardening.

## Test Signals
Each class has a `main` or smoke-test path except the skeletal `MicroSpatial`; there is no JUnit harness in this subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/java-recipes/MicroMulti.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/java-recipes/MicroPriority.java -->
# Research: sources/storage-engines/foundationdb/recipes/java-recipes/MicroPriority.java

## Purpose
Java recipe example that implements a tuple-ordered priority queue.

## Important APIs, Types, And Functions
`push`, `nextCount`, `pop`, `peek`, `clearSubspace`, `smokeTest`

## Control Flow
Push writes `(priority,count,random)` keys, peek/pop scan first or last entry, and pop clears selected key.

## State And Persistence Behavior
Persistent state is stored in fixed FoundationDB subspaces selected by tuple prefixes; most examples clear those subspaces before the smoke scenario. Multi-index examples duplicate values/edges across indexes inside one transaction.

## Dependencies And Integration Points
Depends on Java FoundationDB bindings (`com.foundationdb.*`, `Subspace`, `Tuple`, async `Function`) and a reachable default cluster. Part of the language recipe collection and mirrors concepts also shown in Go, Python, and Ruby recipes.

## Risks And Edge Cases
Example code uses old Java FoundationDB API 300, static global database/subspaces, minimal error handling, and fixed demo subspaces. It is suitable as documentation/sample code, not a reusable library without transaction/error hardening.

## Test Signals
Each class has a `main` or smoke-test path except the skeletal `MicroSpatial`; there is no JUnit harness in this subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/java-recipes/MicroPriority.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/java-recipes/MicroQueue.java -->
# Research: sources/storage-engines/foundationdb/recipes/java-recipes/MicroQueue.java

## Purpose
Java recipe example that implements a FIFO queue.

## Important APIs, Types, And Functions
`enqueue`, `dequeue`, `firstItem`, `lastIndex`, `clearSubspace`

## Control Flow
Enqueue reverse-scans the queue for last index and writes the next index with random tie-breaker; dequeue reads/clears first item.

## State And Persistence Behavior
Persistent state is stored in fixed FoundationDB subspaces selected by tuple prefixes; most examples clear those subspaces before the smoke scenario. Multi-index examples duplicate values/edges across indexes inside one transaction.

## Dependencies And Integration Points
Depends on Java FoundationDB bindings (`com.foundationdb.*`, `Subspace`, `Tuple`, async `Function`) and a reachable default cluster. Part of the language recipe collection and mirrors concepts also shown in Go, Python, and Ruby recipes.

## Risks And Edge Cases
Example code uses old Java FoundationDB API 300, static global database/subspaces, minimal error handling, and fixed demo subspaces. It is suitable as documentation/sample code, not a reusable library without transaction/error hardening.

## Test Signals
Each class has a `main` or smoke-test path except the skeletal `MicroSpatial`; there is no JUnit harness in this subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/java-recipes/MicroQueue.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/java-recipes/MicroRange.java -->
# Research: sources/storage-engines/foundationdb/recipes/java-recipes/MicroRange.java

## Purpose
Java recipe example that demonstrates bounded range iteration and continuation with key selectors.

## Important APIs, Types, And Functions
`stopRangeSoon`, `getRangeLimited`, `populate`, `clearSubspace`, `haltingCondition`

## Control Flow
Populates more than one batch of keys, scans with a limit, advances begin selector after each batch, and prints readable key batches.

## State And Persistence Behavior
Persistent state is stored in fixed FoundationDB subspaces selected by tuple prefixes; most examples clear those subspaces before the smoke scenario. Multi-index examples duplicate values/edges across indexes inside one transaction.

## Dependencies And Integration Points
Depends on Java FoundationDB bindings (`com.foundationdb.*`, `Subspace`, `Tuple`, async `Function`) and a reachable default cluster. Part of the language recipe collection and mirrors concepts also shown in Go, Python, and Ruby recipes.

## Risks And Edge Cases
Example code uses old Java FoundationDB API 300, static global database/subspaces, minimal error handling, and fixed demo subspaces. It is suitable as documentation/sample code, not a reusable library without transaction/error hardening.

## Test Signals
Each class has a `main` or smoke-test path except the skeletal `MicroSpatial`; there is no JUnit harness in this subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/java-recipes/MicroRange.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/java-recipes/MicroSpatial.java -->
# Research: sources/storage-engines/foundationdb/recipes/java-recipes/MicroSpatial.java

## Purpose
Java recipe example that sketches a geospatial label-to-Z-order index.

## Important APIs, Types, And Functions
`xyToZ`, `zToXy`, `setLocation`

## Control Flow
Intended flow converts coordinates to Z value, removes any previous label/Z keys, and writes both `labelZ` and `zLabel` indexes.

## State And Persistence Behavior
Persistent state is stored in fixed FoundationDB subspaces selected by tuple prefixes; most examples clear those subspaces before the smoke scenario. Multi-index examples duplicate values/edges across indexes inside one transaction.

## Dependencies And Integration Points
Depends on Java FoundationDB bindings (`com.foundationdb.*`, `Subspace`, `Tuple`, async `Function`) and a reachable default cluster. Part of the language recipe collection and mirrors concepts also shown in Go, Python, and Ruby recipes.

## Risks And Edge Cases
This file is pseudocode-like and not directly compilable as written: coordinate variables and the previous-location conditional are placeholders. `MicroSpatialTest.java` supplies a concrete implementation.

## Test Signals
Each class has a `main` or smoke-test path except the skeletal `MicroSpatial`; there is no JUnit harness in this subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/java-recipes/MicroSpatial.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/java-recipes/MicroSpatialTest.java -->
# Research: sources/storage-engines/foundationdb/recipes/java-recipes/MicroSpatialTest.java

## Purpose
Java recipe example that implements and smoke-tests the geospatial Z-order index sketched in `MicroSpatial`.

## Important APIs, Types, And Functions
`xyToZ`, `zToXy`, `setLocation`, `getLocation`, `printSubspace`, `main`

## Control Flow
Clears indexes, inserts labels at positions, reads a missing and present label, moves a label, and prints resulting Z locations.

## State And Persistence Behavior
Persistent state is stored in fixed FoundationDB subspaces selected by tuple prefixes; most examples clear those subspaces before the smoke scenario. Multi-index examples duplicate values/edges across indexes inside one transaction.

## Dependencies And Integration Points
Depends on Java FoundationDB bindings (`com.foundationdb.*`, `Subspace`, `Tuple`, async `Function`) and a reachable default cluster. Part of the language recipe collection and mirrors concepts also shown in Go, Python, and Ruby recipes.

## Risks And Edge Cases
Example code uses old Java FoundationDB API 300, static global database/subspaces, minimal error handling, and fixed demo subspaces. It is suitable as documentation/sample code, not a reusable library without transaction/error hardening.

## Test Signals
Each class has a `main` or smoke-test path except the skeletal `MicroSpatial`; there is no JUnit harness in this subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/java-recipes/MicroSpatialTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/java-recipes/MicroTable.java -->
# Research: sources/storage-engines/foundationdb/recipes/java-recipes/MicroTable.java

## Purpose
Java recipe example that implements a table with row and column indexes.

## Important APIs, Types, And Functions
`setCell`, `getCell`, `setRow`, `setColumn`, `getRow`, `getColumn`, `clearSubspace`, `smokeTest`

## Control Flow
Writes every cell to row and column indexes, supports row/column replacement by clearing an index prefix then rewriting, and smoke-tests a larger sample table.

## State And Persistence Behavior
Persistent state is stored in fixed FoundationDB subspaces selected by tuple prefixes; most examples clear those subspaces before the smoke scenario. Multi-index examples duplicate values/edges across indexes inside one transaction.

## Dependencies And Integration Points
Depends on Java FoundationDB bindings (`com.foundationdb.*`, `Subspace`, `Tuple`, async `Function`) and a reachable default cluster. Part of the language recipe collection and mirrors concepts also shown in Go, Python, and Ruby recipes.

## Risks And Edge Cases
Example code uses old Java FoundationDB API 300, static global database/subspaces, minimal error handling, and fixed demo subspaces. It is suitable as documentation/sample code, not a reusable library without transaction/error hardening.

## Test Signals
Each class has a `main` or smoke-test path except the skeletal `MicroSpatial`; there is no JUnit harness in this subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/java-recipes/MicroTable.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/java-recipes/MicroVector.java -->
# Research: sources/storage-engines/foundationdb/recipes/java-recipes/MicroVector.java

## Purpose
Java recipe example that implements a sparse vector keyed by numeric index.

## Important APIs, Types, And Functions
`get`, `set`, `clearSubspace`, `main`

## Control Flow
Sets tuple-packed values under `(index)` keys, reads them back, updates one value, and prints the vector.

## State And Persistence Behavior
Persistent state is stored in fixed FoundationDB subspaces selected by tuple prefixes; most examples clear those subspaces before the smoke scenario. Multi-index examples duplicate values/edges across indexes inside one transaction.

## Dependencies And Integration Points
Depends on Java FoundationDB bindings (`com.foundationdb.*`, `Subspace`, `Tuple`, async `Function`) and a reachable default cluster. Part of the language recipe collection and mirrors concepts also shown in Go, Python, and Ruby recipes.

## Risks And Edge Cases
Example code uses old Java FoundationDB API 300, static global database/subspaces, minimal error handling, and fixed demo subspaces. It is suitable as documentation/sample code, not a reusable library without transaction/error hardening.

## Test Signals
Each class has a `main` or smoke-test path except the skeletal `MicroSpatial`; there is no JUnit harness in this subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/java-recipes/MicroVector.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/python-recipes/micro_blob.py -->
# Research: sources/storage-engines/foundationdb/recipes/python-recipes/micro_blob.py

## Purpose
Python recipe example that stores a large logical value by splitting it into fixed-size chunks keyed by chunk offset.

## Important APIs, Types, And Functions
`clear_subspace`, `write_blob`, `read_blob`, module-level `blob` subspace.

## Control Flow
The module selects FoundationDB API version 300, opens the default database, defines transactional helpers with `@fdb.transactional`, and either runs a smoke test or leaves callable recipe functions. write helpers split non-empty input into chunks and read helpers scan the blob subspace in key order and concatenate values.

## State And Persistence Behavior
Persistent state is one key per chunk in a blob subspace; callers must clear old chunks before overwriting with shorter data or stale chunks can remain.

## Dependencies And Integration Points
Depends on legacy Python FoundationDB bindings and a default cluster; several files use Python 2 syntax (`print` statements, `iteritems`, `xrange`). These are tutorial recipes parallel to the Go/Java/Ruby examples.

## Risks And Edge Cases
Not production-hardened: examples clear fixed top-level subspaces, rely on old API version 300, and sometimes use Python 2 integer division or string/bytes behavior that differs on Python 3.

## Test Signals
Smoke-test code is inline in most files, but there are no formal tests in this subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/python-recipes/micro_blob.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/python-recipes/micro_doc.py -->
# Research: sources/storage-engines/foundationdb/recipes/python-recipes/micro_doc.py

## Purpose
Python recipe example that maps nested JSON/document structures to tuple-addressed leaves.

## Important APIs, Types, And Functions
`to_tuples`, `from_tuples`, `insert_doc`, `_get_new_id`, `get_doc`, `print_subspace`, `clear_subspace`, `smoke_test`.

## Control Flow
The module selects FoundationDB API version 300, opens the default database, defines transactional helpers with `@fdb.transactional`, and either runs a smoke test or leaves callable recipe functions. conversion helpers flatten arrays/maps into path tuples, insert assigns or preserves `doc_id`, and retrieval scans a document prefix and reconstructs the object.

## State And Persistence Behavior
Persistent state is one key per document leaf under `(doc_id, path...)`; random ID allocation scans for collisions but is example-grade.

## Dependencies And Integration Points
Depends on legacy Python FoundationDB bindings and a default cluster; several files use Python 2 syntax (`print` statements, `iteritems`, `xrange`). These are tutorial recipes parallel to the Go/Java/Ruby examples.

## Risks And Edge Cases
Not production-hardened: examples clear fixed top-level subspaces, rely on old API version 300, and sometimes use Python 2 integer division or string/bytes behavior that differs on Python 3.

## Test Signals
Smoke-test code is inline in most files, but there are no formal tests in this subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/python-recipes/micro_doc.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/python-recipes/micro_graph.py -->
# Research: sources/storage-engines/foundationdb/recipes/python-recipes/micro_graph.py

## Purpose
Python recipe example that models directed graph adjacency with forward and inverse indexes.

## Important APIs, Types, And Functions
`set_edge`, `del_edge`, `get_out_neighbors`, `get_in_neighbors`, `clear_subspace` with `edge` and `inverse` subspaces.

## Control Flow
The module selects FoundationDB API version 300, opens the default database, defines transactional helpers with `@fdb.transactional`, and either runs a smoke test or leaves callable recipe functions. edge setters write both forward and inverse keys, delete clears both, and neighbor reads scan the relevant prefix.

## State And Persistence Behavior
Persistent state duplicates each edge in two subspaces, so both writes must remain transactionally paired.

## Dependencies And Integration Points
Depends on legacy Python FoundationDB bindings and a default cluster; several files use Python 2 syntax (`print` statements, `iteritems`, `xrange`). These are tutorial recipes parallel to the Go/Java/Ruby examples.

## Risks And Edge Cases
Not production-hardened: examples clear fixed top-level subspaces, rely on old API version 300, and sometimes use Python 2 integer division or string/bytes behavior that differs on Python 3.

## Test Signals
Smoke-test code is inline in most files, but there are no formal tests in this subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/python-recipes/micro_graph.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/python-recipes/micro_indirect.py -->
# Research: sources/storage-engines/foundationdb/recipes/python-recipes/micro_indirect.py

## Purpose
Python recipe example that demonstrates directory-layer indirection for atomic workspace replacement.

## Important APIs, Types, And Functions
`Workspace.__enter__`, `__exit__`, `_update`, `current`, plus `clear_subspace`, `print_subspace`, `smoke_test`.

## Control Flow
The module selects FoundationDB API version 300, opens the default database, defines transactional helpers with `@fdb.transactional`, and either runs a smoke test or leaves callable recipe functions. a workspace writes to a `new` directory and then removes `current` and moves `new` to `current` inside a transaction.

## State And Persistence Behavior
Persistent state is directory-layer metadata plus data under current/new directories; failures before the move leave old current intact.

## Dependencies And Integration Points
Depends on legacy Python FoundationDB bindings and a default cluster; several files use Python 2 syntax (`print` statements, `iteritems`, `xrange`). These are tutorial recipes parallel to the Go/Java/Ruby examples.

## Risks And Edge Cases
Not production-hardened: examples clear fixed top-level subspaces, rely on old API version 300, and sometimes use Python 2 integer division or string/bytes behavior that differs on Python 3.

## Test Signals
Smoke-test code is inline in most files, but there are no formal tests in this subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/python-recipes/micro_indirect.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/python-recipes/micro_multi.py -->
# Research: sources/storage-engines/foundationdb/recipes/python-recipes/micro_multi.py

## Purpose
Python recipe example that implements a multimap/multiset using atomic add counters.

## Important APIs, Types, And Functions
`multi_add`, `multi_subtract`, `multi_get`, `multi_get_counts`, `multi_is_element`, timing helpers.

## Control Flow
The module selects FoundationDB API version 300, opens the default database, defines transactional helpers with `@fdb.transactional`, and either runs a smoke test or leaves callable recipe functions. add increments a tuple key, subtract decrements or clears at zero, and reads scan an index prefix for members and counts.

## State And Persistence Behavior
Persistent state stores little-endian counters by `(index, value)`; counter encoding and zero cleanup are correctness-sensitive.

## Dependencies And Integration Points
Depends on legacy Python FoundationDB bindings and a default cluster; several files use Python 2 syntax (`print` statements, `iteritems`, `xrange`). These are tutorial recipes parallel to the Go/Java/Ruby examples.

## Risks And Edge Cases
Not production-hardened: examples clear fixed top-level subspaces, rely on old API version 300, and sometimes use Python 2 integer division or string/bytes behavior that differs on Python 3.

## Test Signals
Smoke-test code is inline in most files, but there are no formal tests in this subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/python-recipes/micro_multi.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/python-recipes/micro_priority.py -->
# Research: sources/storage-engines/foundationdb/recipes/python-recipes/micro_priority.py

## Purpose
Python recipe example that implements a priority queue ordered by tuple keys.

## Important APIs, Types, And Functions
`push`, `_next_count`, `pop`, `peek`, `clear_subspace`, `smoke_test`.

## Control Flow
The module selects FoundationDB API version 300, opens the default database, defines transactional helpers with `@fdb.transactional`, and either runs a smoke test or leaves callable recipe functions. push writes `(priority, sequence, random)` keys, `peek` and `pop` scan one key from the front or back, and pop clears the selected key.

## State And Persistence Behavior
Persistent state is queue entries in priority order; sequence generation uses snapshot/range reads and random suffixes to reduce collisions.

## Dependencies And Integration Points
Depends on legacy Python FoundationDB bindings and a default cluster; several files use Python 2 syntax (`print` statements, `iteritems`, `xrange`). These are tutorial recipes parallel to the Go/Java/Ruby examples.

## Risks And Edge Cases
Not production-hardened: examples clear fixed top-level subspaces, rely on old API version 300, and sometimes use Python 2 integer division or string/bytes behavior that differs on Python 3.

## Test Signals
Smoke-test code is inline in most files, but there are no formal tests in this subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/python-recipes/micro_priority.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/python-recipes/micro_queue.py -->
# Research: sources/storage-engines/foundationdb/recipes/python-recipes/micro_queue.py

## Purpose
Python recipe example that implements a FIFO queue on ordered tuple keys.

## Important APIs, Types, And Functions
`enqueue`, `dequeue`, `last_index`, `first_item`, `clear_subspace`, `smoke_test`.

## Control Flow
The module selects FoundationDB API version 300, opens the default database, defines transactional helpers with `@fdb.transactional`, and either runs a smoke test or leaves callable recipe functions. enqueue finds the last index with a snapshot reverse read and writes the next key with random tie-breaker where available; dequeue reads and clears the first item.

## State And Persistence Behavior
Persistent state is queue entries ordered by index; concurrent enqueue contention and empty queue behavior are example-level concerns.

## Dependencies And Integration Points
Depends on legacy Python FoundationDB bindings and a default cluster; several files use Python 2 syntax (`print` statements, `iteritems`, `xrange`). These are tutorial recipes parallel to the Go/Java/Ruby examples.

## Risks And Edge Cases
Not production-hardened: examples clear fixed top-level subspaces, rely on old API version 300, and sometimes use Python 2 integer division or string/bytes behavior that differs on Python 3.

## Test Signals
Smoke-test code is inline in most files, but there are no formal tests in this subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/python-recipes/micro_queue.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/python-recipes/micro_table.py -->
# Research: sources/storage-engines/foundationdb/recipes/python-recipes/micro_table.py

## Purpose
Python recipe example that implements a two-dimensional table with row and column indexes.

## Important APIs, Types, And Functions
`_pack`, `_unpack`, `table_set_cell`, `table_get_cell`, `table_set_row`, `table_get_row`, `table_get_col`, `clear_subspace`.

## Control Flow
The module selects FoundationDB API version 300, opens the default database, defines transactional helpers with `@fdb.transactional`, and either runs a smoke test or leaves callable recipe functions. set cell writes both row and column keys, row/column reads scan prefixes, and row replacement clears a row prefix before rewriting cells.

## State And Persistence Behavior
Persistent state duplicates cell values in row and column indexes, so mutations must update both indexes in one transaction.

## Dependencies And Integration Points
Depends on legacy Python FoundationDB bindings and a default cluster; several files use Python 2 syntax (`print` statements, `iteritems`, `xrange`). These are tutorial recipes parallel to the Go/Java/Ruby examples.

## Risks And Edge Cases
Not production-hardened: examples clear fixed top-level subspaces, rely on old API version 300, and sometimes use Python 2 integer division or string/bytes behavior that differs on Python 3.

## Test Signals
Smoke-test code is inline in most files, but there are no formal tests in this subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/python-recipes/micro_table.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/ruby-recipes/micro_blob.rb -->
# Research: sources/storage-engines/foundationdb/recipes/ruby-recipes/micro_blob.rb

## Purpose
Ruby recipe example that stores a large logical value by splitting it into fixed-size chunks keyed by chunk offset.

## Important APIs, Types, And Functions
`clear_subspace`, `write_blob`, `read_blob`, `CHUNK_SIZE`, `@blob`.

## Control Flow
The file selects FoundationDB API version 300, opens the default database, defines transaction-wrapped helper methods, and usually runs an inline smoke scenario. write helpers split non-empty input into chunks and read helpers scan the blob subspace in key order and concatenate values.

## State And Persistence Behavior
Persistent state is one key per chunk in a blob subspace; callers must clear old chunks before overwriting with shorter data or stale chunks can remain.

## Dependencies And Integration Points
Depends on the Ruby FoundationDB binding, tuple/subspace helpers, and a reachable default cluster. Parallels the recipe patterns in Python and Go for documentation and experimentation.

## Risks And Edge Cases
Several files have example-grade issues: fixed global subspaces are cleared, errors are not surfaced, and a few snippets appear to contain typos (`json.loads`, `tr.clear(v)`, `v` variable in `multi_get_counts`, column unpacking from value). They should be read as recipe sketches unless verified.

## Test Signals
Inline smoke output gives manual signal; no automated Ruby test harness is included here.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/ruby-recipes/micro_blob.rb -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/ruby-recipes/micro_doc.rb -->
# Research: sources/storage-engines/foundationdb/recipes/ruby-recipes/micro_doc.rb

## Purpose
Ruby recipe example that maps nested JSON/document structures to tuple-addressed leaves.

## Important APIs, Types, And Functions
`to_tuples`, `from_tuples`, `insert_doc`, `get_new_id`, `get_doc`, `clear_subspace`.

## Control Flow
The file selects FoundationDB API version 300, opens the default database, defines transaction-wrapped helper methods, and usually runs an inline smoke scenario. conversion helpers flatten arrays/maps into path tuples, insert assigns or preserves `doc_id`, and retrieval scans a document prefix and reconstructs the object.

## State And Persistence Behavior
Persistent state is one key per document leaf under `(doc_id, path...)`; random ID allocation scans for collisions but is example-grade.

## Dependencies And Integration Points
Depends on the Ruby FoundationDB binding, tuple/subspace helpers, and a reachable default cluster. Parallels the recipe patterns in Python and Go for documentation and experimentation.

## Risks And Edge Cases
Several files have example-grade issues: fixed global subspaces are cleared, errors are not surfaced, and a few snippets appear to contain typos (`json.loads`, `tr.clear(v)`, `v` variable in `multi_get_counts`, column unpacking from value). They should be read as recipe sketches unless verified.

## Test Signals
Inline smoke output gives manual signal; no automated Ruby test harness is included here.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/ruby-recipes/micro_doc.rb -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/ruby-recipes/micro_graph.rb -->
# Research: sources/storage-engines/foundationdb/recipes/ruby-recipes/micro_graph.rb

## Purpose
Ruby recipe example that models directed graph adjacency with forward and inverse indexes.

## Important APIs, Types, And Functions
`set_edge`, `del_edge`, `get_out_neighbors`, `get_in_neighbors`, `clear_subspace`.

## Control Flow
The file selects FoundationDB API version 300, opens the default database, defines transaction-wrapped helper methods, and usually runs an inline smoke scenario. edge setters write both forward and inverse keys, delete clears both, and neighbor reads scan the relevant prefix.

## State And Persistence Behavior
Persistent state duplicates each edge in two subspaces, so both writes must remain transactionally paired.

## Dependencies And Integration Points
Depends on the Ruby FoundationDB binding, tuple/subspace helpers, and a reachable default cluster. Parallels the recipe patterns in Python and Go for documentation and experimentation.

## Risks And Edge Cases
Several files have example-grade issues: fixed global subspaces are cleared, errors are not surfaced, and a few snippets appear to contain typos (`json.loads`, `tr.clear(v)`, `v` variable in `multi_get_counts`, column unpacking from value). They should be read as recipe sketches unless verified.

## Test Signals
Inline smoke output gives manual signal; no automated Ruby test harness is included here.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/ruby-recipes/micro_graph.rb -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/ruby-recipes/micro_indirect.rb -->
# Research: sources/storage-engines/foundationdb/recipes/ruby-recipes/micro_indirect.rb

## Purpose
Ruby recipe example that demonstrates directory-layer indirection for atomic workspace replacement.

## Important APIs, Types, And Functions
`Workspace#enter`, `#exit`, `#update`, `#current`, `clear_subspace`, `print_subspace`, `smoke_test`.

## Control Flow
The file selects FoundationDB API version 300, opens the default database, defines transaction-wrapped helper methods, and usually runs an inline smoke scenario. a workspace writes to a `new` directory and then removes `current` and moves `new` to `current` inside a transaction.

## State And Persistence Behavior
Persistent state is directory-layer metadata plus data under current/new directories; failures before the move leave old current intact.

## Dependencies And Integration Points
Depends on the Ruby FoundationDB binding, tuple/subspace helpers, and a reachable default cluster. Parallels the recipe patterns in Python and Go for documentation and experimentation.

## Risks And Edge Cases
Several files have example-grade issues: fixed global subspaces are cleared, errors are not surfaced, and a few snippets appear to contain typos (`json.loads`, `tr.clear(v)`, `v` variable in `multi_get_counts`, column unpacking from value). They should be read as recipe sketches unless verified.

## Test Signals
Inline smoke output gives manual signal; no automated Ruby test harness is included here.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/ruby-recipes/micro_indirect.rb -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/ruby-recipes/micro_multi.rb -->
# Research: sources/storage-engines/foundationdb/recipes/ruby-recipes/micro_multi.rb

## Purpose
Ruby recipe example that implements a multimap/multiset using atomic add counters.

## Important APIs, Types, And Functions
`multi_add`, `multi_sub`, `multi_get`, `multi_get_counts`, `multi_is_element`, timing helpers.

## Control Flow
The file selects FoundationDB API version 300, opens the default database, defines transaction-wrapped helper methods, and usually runs an inline smoke scenario. add increments a tuple key, subtract decrements or clears at zero, and reads scan an index prefix for members and counts.

## State And Persistence Behavior
Persistent state stores little-endian counters by `(index, value)`; counter encoding and zero cleanup are correctness-sensitive.

## Dependencies And Integration Points
Depends on the Ruby FoundationDB binding, tuple/subspace helpers, and a reachable default cluster. Parallels the recipe patterns in Python and Go for documentation and experimentation.

## Risks And Edge Cases
Several files have example-grade issues: fixed global subspaces are cleared, errors are not surfaced, and a few snippets appear to contain typos (`json.loads`, `tr.clear(v)`, `v` variable in `multi_get_counts`, column unpacking from value). They should be read as recipe sketches unless verified.

## Test Signals
Inline smoke output gives manual signal; no automated Ruby test harness is included here.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/ruby-recipes/micro_multi.rb -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/ruby-recipes/micro_priority.rb -->
# Research: sources/storage-engines/foundationdb/recipes/ruby-recipes/micro_priority.rb

## Purpose
Ruby recipe example that implements a priority queue ordered by tuple keys.

## Important APIs, Types, And Functions
`push`, `next_count`, `pop`, `peek`, `clear_subspace`, `smoke_test`.

## Control Flow
The file selects FoundationDB API version 300, opens the default database, defines transaction-wrapped helper methods, and usually runs an inline smoke scenario. push writes `(priority, sequence, random)` keys, `peek` and `pop` scan one key from the front or back, and pop clears the selected key.

## State And Persistence Behavior
Persistent state is queue entries in priority order; sequence generation uses snapshot/range reads and random suffixes to reduce collisions.

## Dependencies And Integration Points
Depends on the Ruby FoundationDB binding, tuple/subspace helpers, and a reachable default cluster. Parallels the recipe patterns in Python and Go for documentation and experimentation.

## Risks And Edge Cases
Several files have example-grade issues: fixed global subspaces are cleared, errors are not surfaced, and a few snippets appear to contain typos (`json.loads`, `tr.clear(v)`, `v` variable in `multi_get_counts`, column unpacking from value). They should be read as recipe sketches unless verified.

## Test Signals
Inline smoke output gives manual signal; no automated Ruby test harness is included here.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/ruby-recipes/micro_priority.rb -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/ruby-recipes/micro_queue.rb -->
# Research: sources/storage-engines/foundationdb/recipes/ruby-recipes/micro_queue.rb

## Purpose
Ruby recipe example that implements a FIFO queue on ordered tuple keys.

## Important APIs, Types, And Functions
`enqueue`, `dequeue`, `last_index`, `first_item`, `clear_subspace`.

## Control Flow
The file selects FoundationDB API version 300, opens the default database, defines transaction-wrapped helper methods, and usually runs an inline smoke scenario. enqueue finds the last index with a snapshot reverse read and writes the next key with random tie-breaker where available; dequeue reads and clears the first item.

## State And Persistence Behavior
Persistent state is queue entries ordered by index; concurrent enqueue contention and empty queue behavior are example-level concerns.

## Dependencies And Integration Points
Depends on the Ruby FoundationDB binding, tuple/subspace helpers, and a reachable default cluster. Parallels the recipe patterns in Python and Go for documentation and experimentation.

## Risks And Edge Cases
Several files have example-grade issues: fixed global subspaces are cleared, errors are not surfaced, and a few snippets appear to contain typos (`json.loads`, `tr.clear(v)`, `v` variable in `multi_get_counts`, column unpacking from value). They should be read as recipe sketches unless verified.

## Test Signals
Inline smoke output gives manual signal; no automated Ruby test harness is included here.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/ruby-recipes/micro_queue.rb -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/ruby-recipes/micro_table.rb -->
# Research: sources/storage-engines/foundationdb/recipes/ruby-recipes/micro_table.rb

## Purpose
Ruby recipe example that implements a two-dimensional table with row and column indexes.

## Important APIs, Types, And Functions
`_pack`, `_unpack`, `table_set_cell`, `table_get_cell`, `table_set_row`, `table_get_row`, `table_get_col`, `clear_subspace`.

## Control Flow
The file selects FoundationDB API version 300, opens the default database, defines transaction-wrapped helper methods, and usually runs an inline smoke scenario. set cell writes both row and column keys, row/column reads scan prefixes, and row replacement clears a row prefix before rewriting cells.

## State And Persistence Behavior
Persistent state duplicates cell values in row and column indexes, so mutations must update both indexes in one transaction.

## Dependencies And Integration Points
Depends on the Ruby FoundationDB binding, tuple/subspace helpers, and a reachable default cluster. Parallels the recipe patterns in Python and Go for documentation and experimentation.

## Risks And Edge Cases
Several files have example-grade issues: fixed global subspaces are cleared, errors are not surfaced, and a few snippets appear to contain typos (`json.loads`, `tr.clear(v)`, `v` variable in `multi_get_counts`, column unpacking from value). They should be read as recipe sketches unless verified.

## Test Signals
Inline smoke output gives manual signal; no automated Ruby test harness is included here.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/ruby-recipes/micro_table.rb -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/swift_build_support/headeroverlay.yaml -->
# Research: sources/storage-engines/foundationdb/swift_build_support/headeroverlay.yaml

## Purpose
YAML template for Swift build support header overlay configuration.

## Important APIs, Types, And Functions
Defines `use-external-names: false`, `version: 0`, and a `roots` array populated by `@VFS_ROOTS@`.

## Control Flow
A build step substitutes virtual filesystem roots into this YAML for Swift tooling.

## State And Persistence Behavior
No runtime state; generated overlay files influence compiler header lookup.

## Dependencies And Integration Points
Depends on the Swift/CMake build support that supplies `@VFS_ROOTS@`. Integrates C/C++ headers with Swift compiler virtual filesystem overlays.

## Risks And Edge Cases
Malformed root substitution will break Swift compilation. The template is intentionally minimal, so schema drift in Swift tooling must be tracked elsewhere.

## Test Signals
Validated by Swift build configuration and compilation paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/swift_build_support/headeroverlay.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/swift_get_latest_toolchain.sh -->
# Research: sources/storage-engines/foundationdb/swift_get_latest_toolchain.sh

## Purpose
Convenience script to download the latest successful Swift 5.9 CentOS 7 snapshot toolchain from Swift CI.

## Important APIs, Types, And Functions
Runs `curl` against the Swift Jenkins console log, greps for `tmp-ci-nightly`, rewrites the blobstore URL to `download.swift.org`, and passes the selected URL to `wget`.

## Control Flow
Single pipeline command; commented command shows a main-branch snapshot variant.

## State And Persistence Behavior
Downloads a toolchain archive into the current directory; no repo state unless run inside the repo.

## Dependencies And Integration Points
Depends on network access, Swift CI console format, `curl`, `grep`, `sed`, `tail`, and `wget`. Supports developers/build automation needing a compatible Swift toolchain for FoundationDB Swift work.

## Risks And Edge Cases
Fragile HTML/log scraping with no `set -e`, quoting, checksum validation, or version pinning. It can download an unexpected artifact if CI log format changes.

## Test Signals
No tests; validation is successful download and toolchain use in subsequent builds.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/swift_get_latest_toolchain.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/CMakeLists.txt -->
# Research: sources/storage-engines/foundationdb/tests/CMakeLists.txt

## Purpose
Central CMake registry and configuration for FoundationDB correctness, simulation, restart, unit, status, multiversion-client, and packaging-related tests.

## Important APIs, Types, And Functions
Defines cache options such as `ENABLE_BUGGIFY`, `ENABLE_SIMULATION_TESTS`, `RUN_IGNORED_TESTS`, log retention controls, include/exclude regexes; finds an old fdbserver for restart tests; configures the Python test runner; calls `configure_testing`, many `add_fdb_test` entries, `verify_testing`, package creation helpers, and optional unit-test discovery.

## Control Flow
When Python is available, it configures test metadata, computes ignore patterns based on multiregion/restart/RocksDB/UBSAN/Valgrind options, registers fast/slow/rare/negative/status/restarting tests, and adds direct CTest unit commands. If Python is absent it warns and skips CTest setup. At the end, optional `AUTO_DISCOVER_UNIT_TESTS` collects unit tests.

## State And Persistence Behavior
Writes configured test runner files into the build tree, registers CTest targets, and controls generated correctness packages. Test execution later writes logs/sim dirs according to cache options.

## Dependencies And Integration Points
Depends on local CMake modules (`AddFdbTest`), Python, built `fdbserver`, many `.toml`/`.txt` tests, optional RocksDB/multiregion/restart build flags, and package helper macros. This file is the main integration point between FoundationDB simulation workloads and CTest/CI.

## Risks And Edge Cases
Large manually maintained test list can drift from filesystem contents; `configure_testing(... ERROR_ON_ADDITIONAL_FILES)` mitigates that. Many tests are explicitly ignored pending fixes or environment needs. Old-fdbserver fallback to current binary weakens upgrade coverage.

## Test Signals
The file itself defines the test signal: registered CTest names, ignored markers, restart sequences, RocksDB-gated tests, direct unit filters, and verification via `verify_testing`.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/CTestCustom.ctest.cmake -->
# Research: sources/storage-engines/foundationdb/tests/CTestCustom.ctest.cmake

## Purpose
CTest customization template that prepares a per-run test directory before tests execute.

## Important APIs, Types, And Functions
Sets `CTEST_CUSTOM_PRE_TEST` to invoke `TestDirectory.py` with the configured Python interpreter and project binary directory.

## Control Flow
CTest runs this command before tests, causing a timestamped directory to be created under the build tree.

## State And Persistence Behavior
Persists build-tree `test_runs/<timestamp>` directories.

## Dependencies And Integration Points
Depends on Python and `tests/TestRunner/fdb_test_runner/TestDirectory.py`. Configured by `tests/CMakeLists.txt` into the build tree.

## Risks And Edge Cases
If the pre-test command fails, test execution setup can fail broadly. It assumes the build directory is writable.

## Test Signals
Validated whenever CTest starts a configured test run.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/CTestCustom.ctest.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/PerfUnitTests.toml -->
# Research: sources/storage-engines/foundationdb/tests/PerfUnitTests.toml

## Purpose
TOML workload definition for running performance unit tests through the FoundationDB test runner.

## Important APIs, Types, And Functions
Defines one `[[test]]` named `PerfUnitTests`, `useDB = false`, no start delay, and a `UnitTests` workload with `testsMatching = #`.

## Control Flow
The test runner reads this file and runs a unit-test workload without starting/using a database.

## State And Persistence Behavior
No persistent state aside from normal test output/logs.

## Dependencies And Integration Points
Depends on FoundationDB test runner TOML schema and `UnitTests` workload implementation. Registered by `tests/CMakeLists.txt` as an ignored test file.

## Risks And Edge Cases
The broad `testsMatching = #` selector relies on workload interpretation. Being marked ignored means it will not run unless ignored tests are enabled.

## Test Signals
Test signal is explicit but disabled by default via `IGNORE` in CMake.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/PerfUnitTests.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/TestRunner/fdb_test_runner/TestDirectory.py -->
# Research: sources/storage-engines/foundationdb/tests/TestRunner/fdb_test_runner/TestDirectory.py

## Purpose
Utility script for creating and locating timestamped FoundationDB test run directories in a build tree.

## Important APIs, Types, And Functions
`TestDirectory.get_test_root` creates `<builddir>/test_runs`, `create_new_test_dir` creates a timestamped subdirectory, `get_current_test_dir` returns the lexicographically latest run directory, and `main` parses `builddir` and creates a new directory.

## Control Flow
When run, it ensures the root exists then creates a directory named with current date/time down to microseconds.

## State And Persistence Behavior
Persists directories under the supplied build directory. It does not write files beyond directory creation.

## Dependencies And Integration Points
Depends on Python stdlib `os`, `datetime`, and `argparse`. Used by `CTestCustom.ctest.cmake` before CTest runs.

## Risks And Edge Cases
`get_current_test_dir` assumes at least one run directory exists and will fail on empty roots. Concurrent invocations could collide only at microsecond-level timestamp names, but no retry exists.

## Test Signals
Validated by CTest pre-test invocation; no direct unit test in this subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/TestRunner/fdb_test_runner/TestDirectory.py -->
