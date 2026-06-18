# subset-b-009657 Research

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libnfs/lib/socket.c -->
# sources/user-network-fs/libnfs/lib/socket.c

Purpose: This file is libnfs's ONC RPC socket transport layer. It owns TCP and UDP socket creation, nonblocking connection setup, event-mask selection, socket reads/writes, RPC record-marker framing, zero-copy NFS READ receive paths, timeout scanning, and reconnect/requeue behavior for in-flight PDUs.

Important APIs and types: Public entry points include `rpc_get_fd`, `rpc_which_events`, `rpc_service`, `rpc_write_to_socket`, `rpc_connect_async`, `rpc_disconnect`, `rpc_bind_udp`, `rpc_set_udp_destination`, `rpc_queue_length`, `rpc_get_num_awaiting`, `rpc_set_awaiting_limit`, `rpc_set_fd`, and `rpc_is_udp_socket`. Internal helpers include `create_socket`, `set_nonblocking`, `set_keepalive`, `adjust_inbuf`, `rpc_reassemble_pdu`, `rpc_finished_pdu`, `rpc_timeout_scan`, `rpc_connect_sockaddr_async`, `rpc_set_sockaddr`, and `rpc_reconnect_requeue`. The state model is driven by `struct rpc_context`, `struct rpc_pdu`, `struct rpc_queue`, wait-pdu hash buckets, read states such as `READ_RM`, `READ_PAYLOAD`, `READ_IOVEC`, and optional TLS/Kerberos/multithreading fields.

Control flow: Callers poll the fd using `rpc_which_events`, then pass revents into `rpc_service`. Service first scans timeouts, handles socket errors and async connect completion, advances TLS handshake when enabled, drains readable data through `rpc_read_from_socket`, and writes queued PDUs through `rpc_write_to_socket`. TCP reads parse record markers, match replies by XID, decode or skip unknown PDUs, optionally copy a preamble then read bulk data into caller iovecs, and complete callbacks through `rpc_finished_pdu`. UDP reads receive whole datagrams and process them directly.

State and persistence behavior: There is no durable persistence, but runtime state is dense: fd/old_fd migration, connected flags, socket-disabled mode, input buffers/fragments, retransmission queues, wait-pdu length limits, timestamps, retry counters, UDP source/destination addresses, and stats counters. Reconnect moves queued and in-flight PDUs back to `outqueue`, resets input/fragments, optionally preserves an fd value with `dup2`, and restarts nonblocking connect until the configured retry policy is exhausted.

Dependencies and integration points: The file depends on platform socket APIs, `poll`, `fcntl`/`ioctl`, `writev`/`readv`, DNS resolution, TCP keepalive options, optional `SO_BINDTODEVICE`, optional TLS, optional Kerberos privacy mode, libnfs PDU encode/decode helpers, stats callbacks, and multithreading locks. It is the event-loop bridge used by higher NFS protocol code and by applications embedding libnfs in poll/select loops.

Risks: The code is highly platform-conditional and sensitive to partial I/O, EINTR/EAGAIN handling, buffer sizing, endian conversion, and callback ordering under locks. Fragment support explicitly returns an error path. UDP datagrams allocate 64 KiB per receive. Some error messages reuse existing error strings oddly, and reconnect safety depends on every in-flight PDU being safe to retransmit. TLS and zero-copy reads have special exclusions that can regress silently if security modes change.

Test signals: Useful signals are nonblocking connect success/failure, `rpc_which_events` changing with outqueue state, writev partial-send accounting, wait-pdu limit enforcement, timeout retransmit and major-timeout reconnect counters, unknown-XID skip behavior, oversized PDU rejection, zero-copy READ payload delivery, UDP broadcast/source address handling, `rpc_disconnect` callback cancellation, and reconnect preserving or exhausting retry state.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libnfs/lib/socket.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/.github/workflows/ccpp.yml -->
# sources/user-network-fs/libsmb2/.github/workflows/ccpp.yml

Purpose: This GitHub Actions workflow is the main C/C++ build matrix for libsmb2. It validates the project across Linux, Windows/MSVC, PS2, Vita, PS3 PPU, PS4, Switch, 3DS, Wii, GameCube, Wii-U, DS, and Amiga targets.

Important APIs and types: The file uses GitHub Actions jobs, `actions/checkout@v4`, platform containers such as `ps2dev/ps2dev`, `vitasdk/vitasdk`, `devkitpro/*`, and `amigadev/crosstools`, plus CMake and `Makefile.platform`/platform-specific makefiles. The Linux job installs `libkrb5-dev`, configures `cmake -S . -B build`, and builds the tree. Windows uses the Visual Studio 17 2022 generator.

Control flow: The workflow runs on push and pull request. Most jobs checkout sources, install platform dependencies or rely on a container, then invoke one or more platform build targets followed by `clean`. The PS3 and PS4 jobs manually fetch or configure SDK package sources before building.

State and persistence behavior: State is ephemeral CI workspace state: downloaded SDK archives, CMake build directories, package manager state, and environment variables such as `PS3DEV` and `PSL1GHT`. No artifacts are persisted by this workflow.

Dependencies and integration points: It integrates the root CMake build, `Makefile.platform`, console SDK images, distro package managers, and platform makefiles under `lib/`. It is a broad regression signal for conditional compile definitions in `CMakeLists.txt`, compatibility shims, and platform-specific source directories.

Risks: Several jobs depend on mutable `latest` container tags, external archive URLs, third-party package repositories, and unpinned checkout actions. Some jobs run `make ... clean` in the same command, which proves the target can build and clean but may hide artifact inspection opportunities. Platform SDK changes can break CI without code changes.

Test signals: A green matrix proves the project configures and compiles on mainstream and embedded/console targets. Failures localize portability regressions in compile definitions, missing compatibility APIs, SDK drift, package availability, or build-system target wiring.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/.github/workflows/ccpp.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/.github/workflows/codeql.yml -->
# sources/user-network-fs/libsmb2/.github/workflows/codeql.yml

Purpose: This workflow runs GitHub CodeQL analysis for C/C++ on master pushes, master pull requests, and a weekly Tuesday schedule.

Important APIs and types: It uses `github/codeql-action/init@v3`, `github/codeql-action/analyze@v3`, the `cpp` language matrix, `+security-and-quality` queries, and a manual CMake build step. Permissions are narrowed to read actions/contents and write security events.

Control flow: The job checks out the repository, initializes CodeQL for the matrix language, runs `cmake -S . -B build` and `cmake --build build`, then uploads analysis results with category `/language:cpp`.

State and persistence behavior: CodeQL's database and build outputs are transient within the workflow. Persistent output is the security alert data stored by GitHub's code scanning service.

Dependencies and integration points: The analysis path relies on the default CMake configuration being buildable on Ubuntu without extra packages beyond the runner image. It complements the broader `ccpp.yml` build matrix by adding static-analysis findings for the normal Linux CMake path.

Risks: CodeQL coverage follows only the default build options, so optional examples, platform-specific targets, and many conditional code paths are not analyzed. If CMake starts requiring packages not present on Ubuntu runners, analysis will fail before scanning.

Test signals: A successful run means CodeQL could trace the compiled C/C++ database. Findings in GitHub code scanning are the main output, especially security-and-quality alerts for memory, bounds, unchecked return values, and resource lifetime issues.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/.github/workflows/codeql.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/.github/workflows/esp_upload_component.yml -->
# sources/user-network-fs/libsmb2/.github/workflows/esp_upload_component.yml

Purpose: This workflow publishes libsmb2 to the Espressif Component Service when changes land on `master`.

Important APIs and types: It uses `actions/checkout@main` and `espressif/upload-components-ci-action@v1` with component name `libsmb2`, namespace `sahlberg`, and secret `ESP_IDF_COMPONENT_API_TOKEN`.

Control flow: On a master push, one Ubuntu job checks out the repository and invokes the upload action. There is no build or validation step in this workflow itself.

State and persistence behavior: The only persistent effect is publishing a component version to Espressif's service. The API token is read from GitHub secrets and should not appear in logs.

Dependencies and integration points: It depends on Espressif component metadata in the repository, especially `idf_component.yml`, `component.mk`, and ESP-related include/source layout configured by `CMakeLists.txt`.

Risks: `actions/checkout@main` is not pinned to a version tag, and upload is triggered directly from master without an explicit ESP-IDF build gate in this workflow. Incorrect component metadata or a stale secret will fail publication after merge.

Test signals: Successful upload confirms the repository is accepted by the Espressif service. Build compatibility must be inferred from separate ESP/platform CI, not from this file.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/.github/workflows/esp_upload_component.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/CMakeLists.txt -->
# sources/user-network-fs/libsmb2/CMakeLists.txt

Purpose: This is libsmb2's primary CMake entry point. It configures project identity, install layout, feature options, platform compile definitions, dependency discovery, package metadata, examples, and the library subdirectory.

Important APIs and types: The file uses `project`, `option`, `find_package`, `include(cmake/ConfigureChecks.cmake)`, `include_directories`, `add_definitions`, `add_subdirectory`, `configure_file`, `write_basic_package_version_file`, and `install`. Feature controls include `ENABLE_EXAMPLES`, `ENABLE_LIBKRB5`, `ENABLE_GSSAPI`, `BUILD_SHARED_LIBS`, `PICO_BOARD`, `ESP_PLATFORM`, `IOP`, and `BUILD_IRX`.

Control flow: It picks a minimum CMake version based on the target platform, creates either `libsmb2` or PS2 `smb2man` project metadata, configures pkg-config data, sets install paths, chooses shared-library defaults, searches Kerberos or GSSAPI on Linux/iOS, runs configure checks, applies target-specific include paths and compatibility defines, optionally generates an MSVC `.def` file from `lib/libsmb2.syms`, adds examples when enabled, adds `lib`, and installs headers/pkg-config/CMake finder files for non-special targets.

State and persistence behavior: Generated state includes `config.h`, `libsmb2.pc`, `libsmb2-config-version.cmake`, and optionally a generated MSVC export definition. Install state includes headers, pkg-config data, and CMake package files.

Dependencies and integration points: It integrates with CMake helper modules, ESP-IDF component conventions, Raspberry Pi Pico SDK conventions, console SDK toolchains, Kerberos/GSSAPI libraries, Windows `ws2_32`, Solaris `socket`/`nsl`, examples, and `lib/CMakeLists.txt`.

Risks: The script uses many global `add_definitions` and `include_directories`, so platform settings can leak between subdirectories. Some target names and conditions are nonstandard (`EE`, `IOP`, `PS4`, `VITA`) and rely on external toolchain files. `CORE_LIBRARIES` and `core_DEPENDS` are global variables consumed by subdirectories, making ordering important.

Test signals: Good signals are successful configure/build on the CI platform matrix, generated `config.h` matching platform headers, correct optional Kerberos/GSSAPI enablement, examples linking with `smb2`, MSVC DLL export generation, and install/package discovery through the installed CMake/pkg-config metadata.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/Makefile.am -->
# sources/user-network-fs/libsmb2/Makefile.am

Purpose: This is the root Automake file for libsmb2's autotools build. It wires subdirectories, pkg-config installation, distribution extras, and a convenience `test` target.

Important APIs and types: It uses Automake variables `SUBDIRS`, `ACLOCAL_AMFLAGS`, `pkgconfigdir`, `pkgconfig_DATA`, and `EXTRA_DIST`, plus the conditional `ENABLE_EXAMPLES`.

Control flow: When examples are enabled, `MAYBE_EXAMPLES` expands to `examples`. Automake builds `include`, `lib`, `utils`, the root directory, and optionally examples. The custom `test` target depends on subdirs and then runs `make test` under `tests`.

State and persistence behavior: Build outputs are autotools-generated Makefiles, libtool artifacts, installed pkg-config file `libsmb2.pc`, and any test outputs from the tests directory.

Dependencies and integration points: This file depends on conditionals and substitutions declared in `configure.ac`, and it delegates most real compilation to `include/Makefile.am`, `lib/Makefile.am`, `utils/Makefile.am`, `tests/Makefile.am`, and optionally `examples/Makefile.am`.

Risks: The root `test` target assumes the tests directory has been configured even though `tests` is not in `SUBDIRS`; it is only a direct `cd tests; make test` invocation. Changes to example conditionals or pkg-config generation need matching updates in `configure.ac`.

Test signals: `autoreconf && ./configure && make && make test` should create all Makefiles, build the library/utilities, install or stage `libsmb2.pc`, and run the delegated tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/bootstrap -->
# sources/user-network-fs/libsmb2/bootstrap

Purpose: This tiny bootstrap script regenerates autotools infrastructure for libsmb2.

Important APIs and types: It is a POSIX shell script with a single command, `autoreconf -vif`.

Control flow: Running the script invokes autoreconf in verbose, install, and force modes so local `configure`, aclocal files, libtool helper files, and Automake support files are regenerated from `configure.ac` and `Makefile.am` inputs.

State and persistence behavior: The script writes generated autotools files into the source tree. It does not track state itself.

Dependencies and integration points: It requires Autoconf, Automake, libtoolize/aclocal support, and the macros referenced by `configure.ac`, including local `m4` macros.

Risks: `autoreconf -i -f` can overwrite generated files and can produce different output depending on installed autotools versions. It should be run intentionally, not as an opaque build step in a dirty tree.

Test signals: Success is a zero exit status and a usable `./configure` script. Follow-up validation is `./configure && make`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/bootstrap -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/cmake/ConfigureChecks.cmake -->
# sources/user-network-fs/libsmb2/cmake/ConfigureChecks.cmake

Purpose: This CMake module performs portability checks and generates the CMake version of `config.h`.

Important APIs and types: It uses `CheckIncludeFile`, `CheckIncludeFiles`, `CheckStructHasMember`, `CheckCCompilerFlag`, `check_include_file`, `check_include_files`, `check_struct_has_member`, `check_c_compiler_flag`, `configure_file`, and `add_definitions`.

Control flow: It checks common POSIX/network headers, optional GSSAPI/Kerberos headers based on feature flags, `netinet/tcp.h` with `sys/types.h`, platform exceptions for PS4 and Nintendo Wii/GameCube linger checks, struct members for `sa_len`, `ss_family`, and `l_linger`, adds `-Wall` when GCC accepts it, forces `_FILE_OFFSET_BITS=64`, writes `${CMAKE_CURRENT_BINARY_DIR}/config.h`, and defines `HAVE_CONFIG_H`.

State and persistence behavior: The generated `config.h` is the persistent build-tree state consumed by C sources. Compile definitions are global to the directory tree after inclusion.

Dependencies and integration points: It feeds macros used by socket, platform, crypto, and compatibility code. It is included by the root `CMakeLists.txt` except for ESP early expansion.

Risks: Header checks can be unreliable for cross-compilers without correct sysroots. Global `add_definitions` can affect external or embedded subdirectories. The `HAVE_LIBKRB5` CMake check only tests for `krb5/krb5.h`, while the autotools path checks GSSAPI headers and links `gssapi_krb5`, so feature semantics can differ.

Test signals: Inspect generated `config.h`, build all platform targets, and verify code paths guarded by `HAVE_*` compile correctly. CI across console and desktop targets is the strongest signal for this file.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/cmake/ConfigureChecks.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/cmake/FindSMB2.cmake -->
# sources/user-network-fs/libsmb2/cmake/FindSMB2.cmake

Purpose: This is a CMake find-module for consumers that want to locate an installed libsmb2 library.

Important APIs and types: It optionally uses `pkg_check_modules(PC_SMB2 libsmb2 QUIET)` when `PKG_CONFIG_FOUND` is already true, then uses `find_path`, `find_library`, and `find_package_handle_standard_args`. Output variables are `SMB2_FOUND`, `SMB2_INCLUDE_DIRS`, `SMB2_LIBRARIES`, `SMB2_DEFINITIONS`, and `SMB2_VERSION`.

Control flow: The module looks for `smb2/libsmb2.h`, records the pkg-config version, finds library `smb2`, invokes standard package handling, and, when found, maps the singular include/library values into plural consumer variables and sets `-DHAVE_LIBSMB2=1`.

State and persistence behavior: It only mutates CMake cache variables such as `SMB2_INCLUDE_DIR` and `SMB2_LIBRARY`; there is no filesystem output.

Dependencies and integration points: It is installed by the root CMake script and consumed by downstream projects with `find_package(SMB2)`.

Risks: The module references pkg-config variables only if `PKG_CONFIG_FOUND` was set by the caller; it does not call `find_package(PkgConfig)` itself. It provides variables rather than an imported target, so downstream consumers must manually apply include dirs, libraries, and definitions.

Test signals: Install libsmb2, configure a small downstream project with `find_package(SMB2 REQUIRED)`, and verify the include directory, library path, version, and compile definition are populated.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/cmake/FindSMB2.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/cmake/Modules/FindGSSAPI.cmake -->
# sources/user-network-fs/libsmb2/cmake/Modules/FindGSSAPI.cmake

Purpose: This module locates GSSAPI for platforms where libsmb2 can use GSSAPI authentication support, notably the iOS branch in the root CMake file.

Important APIs and types: It uses `find_library(GSSAPI_LIBRARY NAMES gssapi_krb5)`, `find_path(GSSAPI_INCLUDE_DIR NAMES gssapi.h gssapi/gssapi.h)`, and `find_package_handle_standard_args`.

Control flow: The module searches for the library and header, runs standard required-variable handling, and, if found, assigns `GSSAPI_LIBRARIES` and `GSSAPI_INCLUDE_DIRS`.

State and persistence behavior: It writes only CMake cache variables and normal variables. There is no generated file.

Dependencies and integration points: It is loaded from the custom CMake module path when `ENABLE_GSSAPI` is on for iOS. Its output feeds `CORE_LIBRARIES` in the root build.

Risks: The condition `if (GSSAPI_LIBRARY AND GSSAPI_INCLUDE_DIRS)` checks the plural include variable before it is assigned; the standard package handler still sets `GSSAPI_FOUND`, but the extra condition is ineffective or misleading. The module searches only `gssapi_krb5`, which may not match all platform GSSAPI library names.

Test signals: Configure with `ENABLE_GSSAPI=ON` on a target sysroot containing GSSAPI and verify `GSSAPI_FOUND`, include path, and library path are set and linked into the core target.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/cmake/Modules/FindGSSAPI.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/cmake/Modules/FindLibKrb5.cmake -->
# sources/user-network-fs/libsmb2/cmake/Modules/FindLibKrb5.cmake

Purpose: This module locates Kerberos 5 headers and library for optional libsmb2 Kerberos support on Linux.

Important APIs and types: It exposes `LibKrb5_ROOT_DIR`, `LibKrb5_LIBRARY`, `LibKrb5_INCLUDE_DIR`, and `LibKrb5_FOUND`. It uses `find_path`, `find_library`, `find_package_handle_standard_args`, and `mark_as_advanced`.

Control flow: The module first searches for a root directory containing `include/krb5.h`, then searches `${root}/lib` for `krb5` and `${root}/include` for `krb5.h`. It requires both library and include directory through standard package handling.

State and persistence behavior: It only populates CMake variables/cache entries. It does not generate files.

Dependencies and integration points: The root CMake file calls this module on Linux when `ENABLE_LIBKRB5` is enabled, and assigns `LIBKRB5_LIBRARY` to `core_DEPENDS`. `ConfigureChecks.cmake` separately defines `HAVE_LIBKRB5` based on header presence.

Risks: The root file uses `${LIBKRB5_LIBRARY}` while this module defines `LibKrb5_LIBRARY`; depending on CMake variable case behavior, this can produce an empty dependency value. It also finds `krb5` but not necessarily `gssapi_krb5`, while the autotools path links `-lgssapi_krb5`.

Test signals: Configure with Kerberos installed and inspect CMake cache/output for `LibKrb5_FOUND` and the actual link line. Authentication tests using Kerberos are needed to prove the dependency is not just detected but linked correctly.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/cmake/Modules/FindLibKrb5.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/cmake/config.h.cmake -->
# sources/user-network-fs/libsmb2/cmake/config.h.cmake

Purpose: This is the CMake template for generated `config.h`, mirroring the portability and package macros that C sources expect from autotools builds.

Important APIs and types: It uses CMake `#cmakedefine` directives for header availability, struct feature macros, package metadata, and version metadata. Macros include `HAVE_ARPA_INET_H`, `HAVE_NETINET_TCP_H`, `HAVE_SYS_UIO_H`, `HAVE_LIBKRB5`, `HAVE_SOCKADDR_LEN`, `HAVE_SOCKADDR_STORAGE`, `HAVE_LINGER`, `STDC_HEADERS`, `PACKAGE_*`, and `VERSION`.

Control flow: `ConfigureChecks.cmake` substitutes the template into `${CMAKE_CURRENT_BINARY_DIR}/config.h`; C sources include it when `HAVE_CONFIG_H` is defined.

State and persistence behavior: The generated header becomes build-tree state and controls conditional compilation for network, file, auth, and platform compatibility code.

Dependencies and integration points: This template is tightly coupled to checks in `ConfigureChecks.cmake` and package variables set in the root `CMakeLists.txt`. It also provides compatibility with sources shared between autotools and CMake builds.

Risks: `#cmakedefine HAVE_X "@HAVE_X@"` can define macros with string-like substitution values rather than a simple `1`, depending on CMake behavior and consumers' expectations. Missing parity with `configure.ac` can make CMake builds exercise different conditional paths than autotools builds.

Test signals: Generated `config.h` should be inspected for expected macros on each target, and both CMake and autotools builds should compile the same core files with equivalent feature availability.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/cmake/config.h.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/cmake/libsmb2.pc.cmake -->
# sources/user-network-fs/libsmb2/cmake/libsmb2.pc.cmake

Purpose: This template generates the pkg-config file for CMake installs of libsmb2.

Important APIs and types: It defines pkg-config fields `prefix`, `exec_prefix`, `libdir`, `includedir`, `Name`, `Description`, `Version`, `Requires`, `Conflicts`, `Libs`, and `Cflags`, using CMake substitutions such as `@CMAKE_INSTALL_PREFIX@`, `@INSTALL_LIB_DIR@`, `@INSTALL_INC_DIR@`, and `@PROJECT_VERSION@`.

Control flow: The root `CMakeLists.txt` configures this template into the build directory and installs it under the configured pkg-config directory for normal non-Pico/non-special builds.

State and persistence behavior: The generated `.pc` file is installed metadata consumed by downstream build systems. It records the install prefix and link/include flags.

Dependencies and integration points: Downstream consumers using `pkg-config --libs --cflags libsmb2` rely on this file. `FindSMB2.cmake` can also use pkg-config values indirectly.

Risks: `Requires` is empty even when optional Kerberos/GSSAPI or platform libraries are linked, so static consumers may miss transitive dependencies. The template hardcodes `-lsmb2` and does not expose optional compile definitions.

Test signals: After install, `pkg-config --modversion libsmb2`, `--cflags`, and `--libs` should return usable values, and a small external program should compile and link using those flags.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/cmake/libsmb2.pc.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/component.mk -->
# sources/user-network-fs/libsmb2/component.mk

Purpose: This file describes libsmb2 as an ESP-IDF component for legacy Make-based ESP-IDF builds.

Important APIs and types: It sets `COMPONENT_SRCDIRS=lib`, `COMPONENT_PRIV_INCLUDEDIRS=lib include/esp`, and `COMPONENT_ADD_INCLUDEDIRS=include include/smb2`.

Control flow: ESP-IDF's build system reads these variables to compile sources under `lib`, expose public include directories, and include private implementation headers for the component.

State and persistence behavior: There is no state in this file; it influences generated ESP-IDF build artifacts.

Dependencies and integration points: It complements the ESP branch in `CMakeLists.txt`, `idf_component.yml`, and ESP-specific headers under `include/esp`.

Risks: Only `lib` is listed as a source directory, so new source directories must be reflected here for legacy ESP builds. Private/public include separation must stay aligned with ESP-IDF expectations.

Test signals: Build an ESP-IDF project that depends on libsmb2 and verify public headers resolve while private includes remain available to component sources.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/component.mk -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/configure.ac -->
# sources/user-network-fs/libsmb2/configure.ac

Purpose: This is the autotools configuration source for libsmb2. It declares package metadata, feature flags, compiler/linker setup, portability checks, and generated Makefiles.

Important APIs and types: It uses `AC_INIT`, `AC_PREREQ`, `AC_CONFIG_HEADERS`, `AM_INIT_AUTOMAKE`, `AC_CANONICAL_HOST`, `AC_PROG_CC`, `LT_INIT`, `AC_ARG_ENABLE`, `AC_ARG_WITH`, `AC_DEFINE`, `AC_CHECK_HEADERS`, `AC_CHECK_LIB`, `AC_CHECK_MEMBER`, `AM_CONDITIONAL`, `AC_SUBST`, and `AC_CONFIG_FILES`.

Control flow: The script initializes package version 6.1.0, sets up Automake/libtool, forces `_FILE_OFFSET_BITS=64`, handles `--enable-examples`, handles `--without-libkrb5`, handles TCP linger behavior, builds warning flags with optional `-Werror`, handles Solaris and Windows socket libraries, requires `libdl`, checks headers and socket struct members, then generates root/examples/include/lib/tests/utils Makefiles and `libsmb2.pc`.

State and persistence behavior: Generated state includes `configure`, `config.h`, Makefiles, libtool files, substituted variables such as `MAYBE_LIBKRB5`, `WARN_CFLAGS`, and `LIBSOCKET`, and conditional build directories.

Dependencies and integration points: This file drives the autotools build used by `bootstrap`, `Makefile.am`, examples, tests, utilities, and pkg-config generation. It overlaps with the CMake configure checks and must remain semantically aligned.

Risks: Kerberos support is enabled by default and errors out if GSSAPI headers are missing unless disabled. `AC_CHECK_LIB([dl], [dlsym])` makes libdl mandatory, which can be awkward on systems where dlsym is in libc or unavailable. The CMake and autotools feature checks are not perfectly equivalent, creating risk of divergent builds.

Test signals: `./bootstrap && ./configure`, `./configure --without-libkrb5`, `./configure --enable-examples`, `make`, `make test`, and host-specific builds for Windows/Solaris are the main validation signals.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/configure.ac -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/examples/CMakeLists.txt -->
# sources/user-network-fs/libsmb2/examples/CMakeLists.txt

Purpose: This CMake file builds a curated set of libsmb2 example executables when `ENABLE_EXAMPLES` is on.

Important APIs and types: It appends `${POPT_LIBRARY}` to `CORE_LIBRARIES`, defines a `SOURCES` list of executable basenames, loops with `foreach`, calls `add_executable`, `target_link_libraries`, `add_dependencies`, and adds `-Werror` plus `_U_=__attribute__((unused))`.

Control flow: Each source basename becomes an executable from `<name>.c`, links against `smb2` and `CORE_LIBRARIES`, and depends on the `smb2` target.

State and persistence behavior: Build outputs are example binaries in the CMake build tree. No files are installed here.

Dependencies and integration points: It depends on the root build having defined `smb2`, include directories, `CORE_LIBRARIES`, and potentially `POPT_LIBRARY`. The examples exercise public sync, async, raw, DCE/RPC, notify, and server APIs.

Risks: The CMake examples list differs from `examples/Makefile.am`; CMake omits some autotools examples such as `smb2-ls-epoll`, share enum sync, stat/statvfs/truncate/rename. `POPT_LIBRARY` is appended without local discovery in this file.

Test signals: Configure with `-DENABLE_EXAMPLES=ON` and verify each listed executable compiles and links. Comparing CMake and autotools example lists helps catch accidental coverage drift.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/examples/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/examples/Makefile.am -->
# sources/user-network-fs/libsmb2/examples/Makefile.am

Purpose: This Automake file builds the example programs for autotools builds.

Important APIs and types: It defines `noinst_PROGRAMS`, `AM_CPPFLAGS`, `COMMON_LIBS`, and per-program `_LDADD` variables. It compiles with include paths for `include` and `include/smb2`, `_U_=__attribute__((unused))`, `-Wall`, and `-Werror`.

Control flow: Automake builds each listed example as a non-installed executable and links it to `../lib/libsmb2.la`.

State and persistence behavior: Outputs are local example binaries in the build tree; they are not installed.

Dependencies and integration points: It integrates with the libtool library target from `lib/Makefile.am` and exercises examples for cat, put, ls, epoll, raw stat/fsstat/getsd, readlink, LSA, seek, share enum/info, stat/statvfs, truncate, rename, CMD-FIND, server, and notify.

Risks: The autotools list is broader than the CMake list, so a source can compile under one build system but not the other. `-Werror` makes examples sensitive to compiler warning drift and platform-specific warnings.

Test signals: `./configure --enable-examples && make` is the primary signal. A cross-check against CMake `ENABLE_EXAMPLES` catches missing example wiring.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/examples/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/examples/picow/CMakeLists.txt -->
# sources/user-network-fs/libsmb2/examples/picow/CMakeLists.txt

Purpose: This standalone CMake file demonstrates building libsmb2 and a directory-listing example for Raspberry Pi Pico W with FreeRTOS and lwIP.

Important APIs and types: It sets `PICO_SDK_PATH`, `FREERTOS_KERNEL_PATH`, `LIBSMB2_PATH`, Wi-Fi credentials, `SMB2_URL`, `PICO_BOARD=pico_w`, includes Pico SDK and FreeRTOS import scripts, calls `pico_sdk_init`, adds libsmb2 as a subdirectory, builds `smb2-ls-sync` from `main.cpp`, enables USB stdio, and links Pico, CYW43 lwIP FreeRTOS, FreeRTOS heap, and libsmb2 libraries.

Control flow: Users edit the configuration block, CMake initializes the embedded SDKs, libsmb2 is built with Pico-specific settings from the root CMake file, then the example executable is compiled and extra Pico output formats are generated.

State and persistence behavior: Build output includes Pico firmware artifacts, CMake cache values containing Wi-Fi/SMB URL strings, and generated config headers.

Dependencies and integration points: It integrates Pico SDK, FreeRTOS Kernel, lwIP, CYW43 Wi-Fi, libsmb2 includes, and `examples/picow/main.cpp`.

Risks: The file contains placeholder paths and credentials that must be edited locally. Wi-Fi password and SMB URL become compile definitions and can leak through build artifacts. The comment has a typo in the default Pico SDK path (`pick-sdk`). It requires relatively recent CMake 3.24.

Test signals: A successful Pico W build, serial/USB output showing Wi-Fi connection, and a remote SMB directory listing from the configured `SMB2_URL` validate the integration.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/examples/picow/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/examples/picow/main.cpp -->
# sources/user-network-fs/libsmb2/examples/picow/main.cpp

Purpose: This Pico W example connects to Wi-Fi under FreeRTOS, initializes libsmb2, connects to an SMB share, and lists a directory synchronously.

Important APIs and types: It uses Pico APIs `cyw43_arch_init`, `cyw43_arch_enable_sta_mode`, `cyw43_arch_wifi_connect_timeout_ms`, `stdio_init_all`, FreeRTOS `xTaskCreate`, `vTaskStartScheduler`, `vTaskDelete`, and libsmb2 APIs `smb2_init_context`, `smb2_parse_url`, `smb2_set_security_mode`, `smb2_connect_share`, `smb2_opendir`, `smb2_readdir`, `smb2_readlink`, `smb2_closedir`, and cleanup functions.

Control flow: `main` starts a FreeRTOS task. The task initializes Wi-Fi, connects with compile-time SSID/password, logs the assigned IPv4 address, then calls `smb2_ls_sync`. The listing function parses the compile-time SMB URL, connects, iterates directory entries, prints type and size, optionally resolves symlink targets, and destroys all SMB resources.

State and persistence behavior: Persistent configuration is compiled into the binary through CMake definitions. Runtime state includes the Wi-Fi connection, IP address, libsmb2 context, parsed URL, directory handle, and stack buffers for symlink paths.

Dependencies and integration points: It depends on the Pico W CYW43 Wi-Fi stack, lwIP in `NO_SYS=0` mode, FreeRTOS scheduling, and libsmb2's synchronous API working in an embedded environment.

Risks: Error paths call `exit`, which is not always appropriate for embedded firmware. The symlink path uses `sprintf` into a fixed 1024-byte buffer and the readlink target uses 256 bytes. The FreeRTOS task uses `configMINIMAL_STACK_SIZE`, which may be tight for SMB parsing and printing.

Test signals: Serial output should show Wi-Fi connection details, directory entries, symlink targets if present, and no scheduler crash. Testing long paths and authentication failures would exercise the risky branches.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/examples/picow/main.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/examples/picow/smb-ls-sync.c -->
# sources/user-network-fs/libsmb2/examples/picow/smb-ls-sync.c

Purpose: This file is currently empty. Its name suggests it may have been intended as a C version of the Pico W synchronous SMB listing example, but the functional implementation lives in `examples/picow/main.cpp`.

Important APIs and types: There are no declarations, functions, includes, or build-system references visible in the empty file.

Control flow: None.

State and persistence behavior: None.

Dependencies and integration points: The file can only matter if a build system or external documentation references it directly. The local Pico CMake file builds `main.cpp`, not this file.

Risks: Empty source files can confuse researchers or users looking for the implementation implied by the filename. If it is accidentally added to a target, it contributes no symbols.

Test signals: `wc -l` reports zero lines. Build validation should confirm no target expects symbols from this file.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/examples/picow/smb-ls-sync.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/examples/smb2-CMD-FIND.c -->
# sources/user-network-fs/libsmb2/examples/smb2-CMD-FIND.c

Purpose: This example is a protocol probe for SMB2 `QUERY_DIRECTORY` behavior, especially `SMB2_RESTART_SCANS` and `SMB2_INDEX_SPECIFIED`.

Important APIs and types: It uses raw libsmb2 types `smb2_create_request`, `smb2_query_directory_request`, `smb2_query_directory_reply`, `smb2_fileidfulldirectoryinformation`, `smb2_pdu`, file IDs, `smb2_cmd_create_async`, `smb2_cmd_query_directory_async`, `smb2_queue_pdu`, `smb2_decode_fileidfulldirectoryinformation`, fd event callbacks, and `poll`.

Control flow: The program initializes an SMB2 context, registers fd/event callbacks, parses a URL, connects asynchronously, opens the share root, scans directory entries, stores the first two names and indexes, restarts the scan from the beginning, then attempts to restart at the second index. The main loop polls the callback-provided fd/events and calls `smb2_service`.

State and persistence behavior: Runtime state is held in global `is_finished`, callback fd/event globals, and `struct app_data` containing file ID, two indexes, and duplicated names. There is no persistent state.

Dependencies and integration points: It exercises low-level create/query-directory commands rather than the higher-level `smb2_opendir` wrapper, and it is useful for testing server conformance around directory index semantics.

Risks: `is_finished` is never set on the successful path, so the program can continue polling indefinitely unless a later service error occurs. `qd_2_cb` appears to queue the index-specified request with `qd_2_cb` again rather than `qd_3_cb`, so the intended third-stage validation may not run. Duplicated names are never freed.

Test signals: Expected output includes first and second entries, restart returning the first entry, and index-specified restart returning the second entry. A hanging process or repeated second-stage callback indicates the control-flow risks above.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/examples/smb2-CMD-FIND.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/examples/smb2-cat-async.c -->
# sources/user-network-fs/libsmb2/examples/smb2-cat-async.c

Purpose: This example asynchronously reads a remote SMB file and writes it to stdout.

Important APIs and types: It uses `smb2_init_context`, `smb2_parse_url`, `smb2_set_security_mode`, `smb2_connect_share_async`, `smb2_open_async`, `smb2_pread_async`, `smb2_close_async`, `smb2_disconnect_share_async`, `smb2_get_fd`, `smb2_which_events`, `smb2_service`, and POSIX `poll`/`write`. A global buffer and position track reads.

Control flow: Connect callback opens the file, open callback starts a read at offset zero, read callback writes bytes to stdout and queues the next read, and EOF triggers async close and disconnect. The main loop polls the libsmb2 fd until the disconnect callback sets `is_finished`.

State and persistence behavior: Runtime state is a global 256 KiB buffer, `pos`, `is_finished`, and the file handle passed through callbacks. The program writes only stdout and does not persist local files.

Dependencies and integration points: It demonstrates libsmb2's async file API and its integration with a manual poll loop. It includes Amiga/AROS poll compatibility stubs.

Risks: The read size constant is 102400 while the buffer is larger. Error branches often call `exit`, skipping normal SMB cleanup. `write` errors abort. The callback chain assumes the file handle remains valid until close.

Test signals: Reading a known remote file should produce byte-for-byte stdout output and exit after disconnect. Network failures, EOF, and permission errors validate callback status handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/examples/smb2-cat-async.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/examples/smb2-cat-sync.c -->
# sources/user-network-fs/libsmb2/examples/smb2-cat-sync.c

Purpose: This synchronous example reads a remote SMB file and writes it to stdout.

Important APIs and types: It uses `smb2_init_context`, `smb2_parse_url`, `smb2_connect_share`, `smb2_open`, `smb2_pread`, `smb2_close`, `smb2_disconnect_share`, and cleanup APIs. It uses a 16 MiB static buffer and tracks the read offset in `pos`.

Control flow: The program parses the URL, connects, opens the path read-only, loops on `smb2_pread`, retries on `-EAGAIN`, writes successful reads to stdout, then closes and disconnects.

State and persistence behavior: State is only in memory and stdout. No local files are modified.

Dependencies and integration points: It exercises the blocking wrapper API, which internally drives the async service loop. It is a simple utility-style test for read correctness.

Risks: The 16 MiB static buffer is large for constrained systems. Some early error exits skip cleanup. Partial stdout writes are not handled beyond checking for negative return.

Test signals: Compare stdout to the source file content. Exercise EOF, `-EAGAIN`, missing path, and permission-denied cases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/examples/smb2-cat-sync.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/examples/smb2-ftruncate-sync.c -->
# sources/user-network-fs/libsmb2/examples/smb2-ftruncate-sync.c

Purpose: This synchronous example opens a remote SMB file and changes its length through a file handle.

Important APIs and types: It uses `smb2_connect_share`, `smb2_open` with `O_RDWR`, `smb2_ftruncate`, `smb2_close`, and URL/context cleanup. The new length is parsed with `strtoll`.

Control flow: After argument and URL parsing, the program connects to the share, opens the remote path read/write, calls `smb2_ftruncate` with the requested length, closes the handle, disconnects, and exits.

State and persistence behavior: The persistent effect is remote file size mutation on the SMB server. Local state is limited to the SMB context, URL, and file handle.

Dependencies and integration points: It demonstrates handle-based truncation and validates create/open access rights required for file-size modification.

Risks: Length parsing has no validation for invalid strings, overflow, or negative values. Error branches may exit without disconnecting. The operation is destructive to remote file contents beyond the new EOF.

Test signals: Stat the remote file before and after truncation, test expansion and shrinkage, and verify access-denied behavior on read-only files.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/examples/smb2-ftruncate-sync.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/examples/smb2-ls-async.c -->
# sources/user-network-fs/libsmb2/examples/smb2-ls-async.c

Purpose: This example asynchronously lists a remote SMB directory.

Important APIs and types: It uses `smb2_connect_share_async`, `smb2_opendir_async`, `smb2_readdir`, `smb2_closedir`, `smb2_disconnect_share_async`, fd/event callbacks, `smb2_service`, `smb2dir`, `smb2dirent`, and stat fields such as `smb2_type`, `smb2_size`, and `smb2_mtime`.

Control flow: The connect callback starts async directory open. The open callback iterates all cached directory entries synchronously through `smb2_readdir`, prints type/size/time, closes the directory, and disconnects asynchronously. The main loop polls callback-maintained fd/events until disconnect marks completion.

State and persistence behavior: Runtime state is global `is_finished`, current fd/events, the parsed URL, and the directory handle. It only prints to stdout.

Dependencies and integration points: It demonstrates libsmb2 async connection and fd event callback integration with `poll`. It includes Amiga/AROS poll compatibility.

Risks: Output uses `asctime(localtime())`, which is not thread-safe and embeds a newline. Error paths exit immediately. The fd callback model assumes a single active fd.

Test signals: Directory listings should include correct names, file/directory/link type labels, sizes, and mtimes. Async fd event changes should drive the program without busy looping.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/examples/smb2-ls-async.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/examples/smb2-ls-epoll.c -->
# sources/user-network-fs/libsmb2/examples/smb2-ls-epoll.c

Purpose: This Linux-only example shows how to integrate libsmb2's async fd callbacks with `epoll` while listing a directory.

Important APIs and types: It uses Linux `epoll_create1`, `epoll_ctl`, `epoll_wait`, libsmb2 fd/event callbacks, `smb2_set_opaque`, `smb2_get_opaque`, async connect/opendir/disconnect APIs, and directory entry iteration.

Control flow: On Linux, the program creates an SMB2 context, stores an `e_data` structure as opaque data, creates an epoll fd, registers fd/event callbacks that add/delete/modify epoll interest, starts async share connect, then waits in `epoll_wait` and calls `smb2_service` for returned events. Non-Linux builds compile a stub that reports epoll is required.

State and persistence behavior: Runtime state is `e_data`, epoll interest state, `is_finished`, URL/context, and directory handles. It persists nothing.

Dependencies and integration points: It exercises the same listing path as `smb2-ls-async.c` but with edge integration expected by high-performance Linux event loops.

Risks: `ed` is a stack object referenced through the SMB2 context; this is safe only while `main` is active. The callback exits on epoll errors. The initial event registration before connect may have fd `-1` and is guarded only by a nonnegative check.

Test signals: On Linux, directory listing should complete while epoll add/mod/del calls succeed. On non-Linux, the stub should compile and print the unsupported message.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/examples/smb2-ls-epoll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/examples/smb2-lsa-lookupsids.c -->
# sources/user-network-fs/libsmb2/examples/smb2-lsa-lookupsids.c

Purpose: This example connects to the LSA DCE/RPC service over SMB IPC and performs a `LookupSids2` request for built-in administrator SID data.

Important APIs and types: It uses `dcerpc_context`, `lsa_interface`, `lsa_OpenPolicy2`, `lsa_LookupSids2`, `lsa_Close`, `RPC_SID`, `ndr_context_handle`, `POLICY_LOOKUP_NAMES`, `POLICY_VIEW_LOCAL_INFORMATION`, and libsmb2 IPC connection APIs.

Control flow: The program connects to `IPC$`, creates a DCE/RPC context, asynchronously binds to `lsarpc`, opens a policy handle for `\\server`, builds SID `S-1-5-32-544`, calls `LookupSids2`, prints referenced domains and translated names, closes the policy handle, and drives all async DCE/RPC calls via the SMB2 poll loop.

State and persistence behavior: Runtime state includes global `is_finished`, `PolicyHandle`, allocated SID arrays, and DCE/RPC decoded replies. There is no persistence.

Dependencies and integration points: It validates the DCE/RPC layer, LSA generated coders, IPC$ tree connect, authentication/user propagation, and SMB2 event servicing.

Risks: The same SID pointer is inserted twice into the request array, which is acceptable for this probe but not a general pattern. Error paths exit without full cleanup. It assumes the target server supports LSA over named pipes and permits the lookup.

Test signals: Successful output lists referenced domains and translated names for the built-in administrators SID. Failures distinguish IPC connect, DCE bind, policy open, lookup, and close stages.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/examples/smb2-lsa-lookupsids.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/examples/smb2-lseek-sync.c -->
# sources/user-network-fs/libsmb2/examples/smb2-lseek-sync.c

Purpose: This synchronous example demonstrates file-size discovery and `smb2_lseek` behavior.

Important APIs and types: It uses `smb2_open`, `smb2_fstat`, `smb2_lseek`, `smb2_close`, and `struct smb2_stat_64`.

Control flow: The program connects to a share, opens the requested file read-only, obtains size with `smb2_fstat`, seeks to EOF with `SEEK_SET`, seeks back to BOF, then seeks to EOF with `SEEK_END`, printing each resulting offset before cleanup.

State and persistence behavior: It does not mutate the remote file. Runtime state is the SMB context, file handle, stat structure, and current offset.

Dependencies and integration points: It tests the high-level file-handle seek abstraction, which depends on cached file size and offset semantics in libsmb2.

Risks: It prints negative errors using unsigned `PRIu64` formatting in some cases, which can make failures misleading. Error paths can skip some cleanup.

Test signals: For a file of known size, EOF seeks should equal that size and BOF should be zero. Missing path and unsupported seek modes should produce readable errors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/examples/smb2-lseek-sync.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/examples/smb2-notify.c -->
# sources/user-network-fs/libsmb2/examples/smb2-notify.c

Purpose: This example exercises SMB2 change-notification support in synchronous and asynchronous modes.

Important APIs and types: It uses `smb2_notify_change`, `smb2_notify_change_async`, `free_smb2_file_notify_change_information`, `struct sync_cb_data`, `struct smb2_file_notify_change_information`, change notify flags, completion filters, `poll`, and `smb2_service`.

Control flow: The program parses a URL and optional `sync|async` mode, connects to the share, builds a watch-tree flag and broad completion filter, then either performs one synchronous notify request or starts an async notify request configured to execute repeatedly. Async mode waits until callback data indicates completion and checks callback status.

State and persistence behavior: It watches remote server state but does not mutate it. Runtime state includes notification callback data and returned notify structures, which are freed after printing.

Dependencies and integration points: It integrates public notify APIs with the internal sync callback pattern and the event loop. It includes `libsmb2-private.h` to reuse internal `sync_cb_data`, which makes it less purely public than most examples.

Risks: Async mode sets `execute_in_loop=1`, so completion behavior depends on the library marking the callback data finished despite reissuing notifications. A notify request may block indefinitely until server-side changes occur. The mode parser silently defaults to sync for unrecognized third arguments.

Test signals: Trigger file creation, deletion, rename, attribute, or security changes under the watched path and verify printed action/name data. Test both sync and async modes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/examples/smb2-notify.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/examples/smb2-put-async.c -->
# sources/user-network-fs/libsmb2/examples/smb2-put-async.c

Purpose: This example uploads a local file to an SMB path using asynchronous writes.

Important APIs and types: It uses POSIX `open`, `read`, `close`, libsmb2 `smb2_connect_share`, `smb2_open`, `smb2_pwrite_async`, `smb2_service`, and a callback state structure containing local fd, remote handle, position, and completion flag.

Control flow: The program opens the local file, connects synchronously to the SMB share, opens/creates the remote file, reads the first 1024-byte block locally, queues an async pwrite, then polls until write callbacks read and queue subsequent chunks. A status of zero marks upload completion before cleanup.

State and persistence behavior: Persistent effects are a remote file created or overwritten/extended at the destination path. Runtime state includes local fd, SMB file handle, offset, buffer, and callback completion.

Dependencies and integration points: It demonstrates mixing synchronous connect/open with asynchronous write and event servicing.

Risks: `argc` validation checks only `< 2` even though `argv[2]` is required, so missing URL can access out of bounds. The write callback treats local EOF (`read <= 0`) as fatal instead of closing cleanly after the final successful write; completion relies on an async write status of zero. It writes fixed 1024-byte chunks despite a larger buffer.

Test signals: Upload a known local file and compare remote contents. Test zero-length files, missing URL, local EOF after last chunk, and network write errors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/examples/smb2-put-async.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/examples/smb2-put-sync.c -->
# sources/user-network-fs/libsmb2/examples/smb2-put-sync.c

Purpose: This synchronous example uploads a local file to an SMB path.

Important APIs and types: It uses POSIX `open`, `read`, `close`, libsmb2 `smb2_connect_share`, `smb2_open` with `O_WRONLY|O_CREAT`, `smb2_write`, `smb2_close`, and cleanup APIs.

Control flow: The program opens the local file, initializes SMB2, parses the destination URL from `argv[2]`, connects, opens/creates the remote path, reads local 1024-byte chunks, writes each chunk synchronously, then closes and disconnects.

State and persistence behavior: The persistent effect is writing remote file content. Local state is the input fd, static buffer, context, URL, and remote file handle.

Dependencies and integration points: It validates the blocking write wrapper and remote file creation path.

Risks: Argument validation checks only `< 2` despite requiring two arguments, so missing destination can access `argv[2]`. Return values from `smb2_write` are ignored, so short writes or errors during the loop are not detected. Existing remote files may not be truncated before overwrite.

Test signals: Compare remote file bytes with the local file, including files larger than one chunk, and test missing URL, permission denied, and existing larger destination files.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/examples/smb2-put-sync.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/examples/smb2-raw-fsstat-async.c -->
# sources/user-network-fs/libsmb2/examples/smb2-raw-fsstat-async.c

Purpose: This raw async example sends a compound CREATE/QUERY_INFO/CLOSE sequence to retrieve filesystem information at a selectable info level.

Important APIs and types: It uses `smb2_create_request`, `smb2_query_info_request`, `smb2_close_request`, `smb2_cmd_create_async`, `smb2_cmd_query_info_async`, `smb2_cmd_close_async`, `smb2_add_compound_pdu`, `compound_file_id`, filesystem info structs, `nterror_to_errno`, and a poll-driven wait helper.

Control flow: The program parses the info level, connects to the share, allocates `stat_cb_data`, builds a compound request where query and close refer to the compound file id, queues it, waits for callback completion, prints fields based on the selected filesystem info class, frees decoded data, and disconnects.

State and persistence behavior: It does not mutate remote state except transient open/close. Runtime state is callback status, decoded query output, and compound status accumulation.

Dependencies and integration points: It tests libsmb2's raw command builders, compound request chaining, filesystem info decoders, and sync-style wait loop over async commands.

Risks: Unsupported info levels can leave output handling ambiguous. The final `fs = cb_data.ptr` is freed even though the generic callback receives `0` from `stat_cb_3`, so freeing `NULL` is expected for this code path. Error paths can leak already allocated PDUs or context state.

Test signals: Run against known shares for volume, size, device, control, and full-size info levels and verify printed values match server properties. Compound status errors should surface as nonzero callback status.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/examples/smb2-raw-fsstat-async.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/examples/smb2-raw-getsd-async.c -->
# sources/user-network-fs/libsmb2/examples/smb2-raw-getsd-async.c

Purpose: This raw async example retrieves and prints a file or directory security descriptor over SMB2.

Important APIs and types: It uses compound CREATE/QUERY_INFO/CLOSE, `SMB2_0_INFO_SECURITY`, `SMB2_READ_CONTROL`, owner/group/DACL security flags, `struct smb2_security_descriptor`, `smb2_sid`, `smb2_acl`, `smb2_ace`, and helper printers for SID, ACE, ACL, and descriptor control flags.

Control flow: The program connects to the target share, queues a compound request that opens the path with read-control access, queries security info into a decoded descriptor, closes the handle, waits via poll/service, prints descriptor revision/control/owner/group/DACL entries, frees decoded data, and disconnects.

State and persistence behavior: It only reads remote security metadata. Runtime state includes callback status, retained security descriptor pointer, and temporary compound request data.

Dependencies and integration points: It validates raw security info querying, security descriptor decoding, compound PDU file-id substitution, and DACL/SID data structures.

Risks: It requests owner, group, and DACL only, not SACL, so auditing information is not covered. Printer support handles common ACE types and emits "can't print this type" for others. Error paths call `exit`, skipping cleanup.

Test signals: Against files with known ACLs, printed SIDs, ACE counts, masks, and control bits should match server ACL tools. Access-denied tests validate `SMB2_READ_CONTROL` handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/examples/smb2-raw-getsd-async.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/examples/smb2-raw-stat-async.c -->
# sources/user-network-fs/libsmb2/examples/smb2-raw-stat-async.c

Purpose: This raw async example retrieves `SMB2_FILE_ALL_INFORMATION` for a remote path using a compound request and prints detailed metadata.

Important APIs and types: It uses raw create/query-info/close requests, `SMB2_0_INFO_FILE`, `SMB2_FILE_ALL_INFORMATION`, `struct smb2_file_all_info`, access flag constants, file attribute constants, compound PDUs, `compound_file_id`, and poll-driven async completion.

Control flow: The program connects, sends compound CREATE/QUERY_INFO/CLOSE, waits for callback completion, checks status, then prints attributes, timestamps, allocation/end-of-file size, link count, delete-pending/directory flags, index number, EA size, access flags, current byte offset, mode flags, alignment requirement, and name.

State and persistence behavior: It opens and closes the remote object transiently and reads metadata only. Decoded metadata is freed through `smb2_free_data`.

Dependencies and integration points: It exercises libsmb2 raw metadata decoders and compound command sequencing, making it a strong integration example for lower-level users.

Risks: The mode printer checks `fs->access_flags` instead of `fs->mode`, which can mislabel mode flags. Many print paths assume decoded pointers are valid after successful status. Error handling exits without structured cleanup.

Test signals: Compare printed metadata against OS/server stat tools. Validate directory vs file paths, hidden/system/read-only attributes, sparse/compressed flags, and failure behavior for missing paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/examples/smb2-raw-stat-async.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/examples/smb2-readlink.c -->
# sources/user-network-fs/libsmb2/examples/smb2-readlink.c

Purpose: This synchronous example resolves a remote SMB reparse-point/symlink target.

Important APIs and types: It uses `smb2_connect_share`, `smb2_readlink`, fixed local buffer `char buf[256]`, and normal URL/context cleanup.

Control flow: The program parses an SMB URL, connects to the share, calls `smb2_readlink` on the path, prints either the target or the error string plus mapped errno text, then disconnects.

State and persistence behavior: It reads remote metadata only and persists nothing. Runtime state is the SMB context, parsed URL, and readlink buffer.

Dependencies and integration points: It exercises libsmb2's symlink/reparse-point handling through the public sync API.

Risks: The target buffer is fixed at 256 bytes, so long link targets may be truncated or fail depending on library behavior. It does not set user explicitly beyond URL parse/connect.

Test signals: Run against known symlinks/reparse points and normal files. Successful output should print `Link:<target>`, while non-links should produce a clear error.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/examples/smb2-readlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/examples/smb2-rename-sync.c -->
# sources/user-network-fs/libsmb2/examples/smb2-rename-sync.c

Purpose: This synchronous example renames a remote path within an SMB share.

Important APIs and types: It uses `smb2_connect_share`, `smb2_rename`, URL parsing, and cleanup APIs.

Control flow: The program expects a share URL plus source and destination path arguments, connects to the share, logs the rename operation, calls `smb2_rename`, disconnects, and exits.

State and persistence behavior: The persistent effect is remote namespace mutation on the SMB server.

Dependencies and integration points: It validates the high-level rename wrapper and server permissions/share mode handling.

Risks: Rename is destructive if the destination exists or if server semantics replace existing entries. Error exits skip some cleanup. Source and destination are raw argv strings, not normalized against URL path.

Test signals: Verify source disappears and destination appears with preserved content/metadata where expected. Test cross-directory rename, existing destination, missing source, and permission denied.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/examples/smb2-rename-sync.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/examples/smb2-server-sync.c -->
# sources/user-network-fs/libsmb2/examples/smb2-server-sync.c

Purpose: This example implements a minimal synchronous SMB2 server using libsmb2 server callbacks, primarily as a protocol harness rather than a real filesystem server.

Important APIs and types: It defines `struct smb2_server_request_handlers`, `struct smb2_server`, and handlers for authorization, session, tree connect/disconnect, create, close, flush, read, write, lock, ioctl, cancel, echo, query directory, and query info. It uses server helpers such as `smb2_serve_port`, `smb2_set_version`, `smb2_register_error_callback`, `smb2_utf8_to_utf16`, and many SMB2 reply structs.

Control flow: `main` sets signing and anonymous access, assigns a port, and calls `smb2_serve_port`. New clients are configured by `on_new_client`. Request handlers synthesize fixed responses: a disk or pipe share type, normal file attributes, a 32-byte read payload, write count echoing input length, fixed directory entries, and selected file/filesystem info structures.

State and persistence behavior: The server is stateless and does not persist file data. Query directory uses a static counter to alternate between two-entry output and end-of-directory. Allocated response buffers are handed to the server framework for response encoding/freeing.

Dependencies and integration points: It exercises libsmb2's server-side API, decoder/encoder paths, authentication hooks, signing, named-pipe share detection, and client compatibility against synthetic file data.

Risks: This is not a secure or complete server. Anonymous access is enabled, file data is synthetic, directory info construction is minimal, and some allocations on error are not fully unwound. `fill_dir_info` sets names as string pointers after UTF-16 conversion work, so correctness depends on server encoders' expectations.

Test signals: Connect a libsmb2 or OS SMB client to the chosen port, list the share, read the synthetic file, query metadata, and verify handlers produce stable replies. Server logs should show selected dialect and client errors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/examples/smb2-server-sync.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/examples/smb2-share-enum-sync.c -->
# sources/user-network-fs/libsmb2/examples/smb2-share-enum-sync.c

Purpose: This synchronous example enumerates SMB shares on a server through the SRVSVC RPC helper.

Important APIs and types: It uses `getopt`, `smb2_connect_share` to `IPC$`, `smb2_share_enum_sync`, `srvsvc_NetrShareEnum_rep`, share info levels 0 and 1, share type constants, and `smb2_free_data`.

Control flow: The program parses optional `-l level`, validates level 0 or 1, parses the SMB URL, sets user when supplied, connects to `IPC$`, calls synchronous share enumeration, prints share names and optional remarks/types, frees the decoded response, and disconnects.

State and persistence behavior: It reads server share metadata only and persists nothing.

Dependencies and integration points: It validates the high-level synchronous wrapper around DCE/RPC SRVSVC share enumeration over IPC$.

Risks: Only levels 0 and 1 are supported. It exits with code 0 for invalid levels and parse failures in some branches, which can be misleading for scripts. It depends on IPC$ access and server permissions.

Test signals: Compare output against server share-listing tools. Test anonymous, authenticated, level 0, level 1, and access-denied cases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/examples/smb2-share-enum-sync.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/examples/smb2-share-enum.c -->
# sources/user-network-fs/libsmb2/examples/smb2-share-enum.c

Purpose: This asynchronous example enumerates SMB shares and also prints a YAML encoding of the SRVSVC response.

Important APIs and types: It uses `smb2_share_enum_async`, `srvsvc_NetrShareEnum_rep`, DCE/RPC YAML encoding with `dcerpc_allocate_pdu`, `dcerpc_do_coder`, `srvsvc_NetrShareEnum_rep_coder`, and the normal SMB2 poll loop.

Control flow: The program parses optional level, connects to `IPC$`, starts async share enumeration, services the SMB fd until callback completion, prints shares by level, creates a DCE/RPC context to encode the response as YAML, frees decoded data, then cleans up.

State and persistence behavior: Runtime state includes global `is_finished`, selected level, decoded response, and a static YAML buffer. There is no persistence.

Dependencies and integration points: It exercises async SRVSVC helpers, DCE/RPC generated coders, YAML encoding, and SMB event-loop integration.

Risks: The comment says it always uses Level1, but the code supports level 0 and 1 via global `level`. YAML buffer size is fixed at 65536. Error paths exit without full cleanup.

Test signals: Output should match synchronous share enumeration plus valid YAML for the decoded response. Large share lists test YAML buffer sufficiency.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/examples/smb2-share-enum.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/examples/smb2-share-info.c -->
# sources/user-network-fs/libsmb2/examples/smb2-share-info.c

Purpose: This asynchronous example fetches information about one SMB share through SRVSVC `NetrShareGetInfo` and prints both human-readable and YAML output.

Important APIs and types: It uses `dcerpc_connect_context_async`, `SRVSVC_NETRSHAREGETINFO`, `srvsvc_NetrShareGetInfo_req_coder`, `srvsvc_NetrShareGetInfo_rep_coder`, `srvsvc_NetrShareGetInfo_req`, `srvsvc_NetrShareGetInfo_rep`, share type constants, DCE/RPC YAML encoding, and the SMB2 poll loop.

Control flow: The program parses optional `-l level`, parses a URL whose share component is the target share, connects to `IPC$`, binds to `srvsvc`, allocates a request with `\\server` and share name, calls `NetrShareGetInfo`, prints the level-1 style summary, YAML-encodes the request and response, frees allocated request/server strings and decoded data, and marks completion.

State and persistence behavior: It reads server share metadata only. Runtime state includes global request pointer, server string, selected level, DCE context, and static YAML buffer.

Dependencies and integration points: It validates lower-level DCE/RPC usage for SRVSVC, request/response coders, and YAML encoding beyond the convenience `smb2_share_enum` APIs.

Risks: Default `level` is uninitialized unless `-l` is supplied, which can send an unintended request level. The callback creates a new DCE context using the SMB2 context and then calls `dcerpc_free_data(dce, rep)` after destroying that new context, which is a suspicious lifetime pattern. It prints fields as `ShareInfo1` regardless of selected level.

Test signals: Run with explicit `-l 1` and compare output/YAML to server share properties. Invalid or unsupported levels should be tested because the code does little validation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/examples/smb2-share-info.c -->
