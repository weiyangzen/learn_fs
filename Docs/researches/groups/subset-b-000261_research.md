# subset-b-000261 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/.github/ISSUE_TEMPLATE/feature-request.yaml -->
# sources/cloud-native/overlaybd/.github/ISSUE_TEMPLATE/feature-request.yaml

Purpose: GitHub issue form for OverlayBD enhancement requests. It collects version, desired behavior, justification, and contributor willingness, then applies the `enhancement` label.

APIs and control flow: This is declarative GitHub issue-form YAML. The `body` sequence defines markdown, input, textarea, and checkbox widgets. The two substantive textareas are required.

State and persistence: Submitted answers become issue body content in GitHub; there is no repository runtime state.

Dependencies and integration: GitHub Issues consumes the schema. Links point users to OverlayBD releases and CNCF Slack.

Risks and test signals: The final checkbox option lacks an explicit `required` block by design. YAML linting and creating a test issue are the main validation signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/.github/ISSUE_TEMPLATE/feature-request.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/.github/workflows/cmake.yml -->
# sources/cloud-native/overlaybd/.github/workflows/cmake.yml

Purpose: Main CI workflow for CMake builds, TCMU smoke coverage, raw image application, turboOCI v1 mounting, and unit tests on `ubuntu-22.04`.

APIs and control flow: On pushes and PRs to `main`, it installs system libraries, builds googletest, configures with `BUILD_TESTING=1`, `ENABLE_DSA=1`, and `ENABLE_ISAL=1`, then runs `make -j64`. E2E steps install OverlayBD, enable `overlaybd-tcmu.service`, create configfs TCMU devices, discover SCSI devices with `lsscsi`, mount read-only, and compare generated filesystem content.

State and persistence: It writes under `/etc/overlaybd`, `/opt/overlaybd`, `/var/lib/overlaybd/test`, `/sys/kernel/config/target`, local build dirs, and `/var/log/overlaybd.log`.

Dependencies and integration: Requires root-level configfs, target_core_user, libtcmu, libaio, curl, OpenSSL, ext2fs, zstd, json-c, kmod, systemd, gtest, and downloadable Azure blob test data.

Risks and test signals: High parallel build and kernel configfs assumptions make CI host-sensitive. Strong signals are successful mount, recursive diff, `overlaybd-apply` deterministic output, turboOCI mount, and `ctest`.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/.github/workflows/cmake.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/.github/workflows/project-checks.yml -->
# sources/cloud-native/overlaybd/.github/workflows/project-checks.yml

Purpose: Repository hygiene workflow for DCO, short subject, dangling whitespace, and license/header validation.

APIs and control flow: Runs on pushes to `main` and all pull requests. It checks out the repository under a GOPATH-style path, installs `git-validation` and `ltag`, computes the commit range from PR commits API or push event JSON, then runs `git-validation` and `ltag`.

State and persistence: Only uses the Actions workspace and environment variables such as `GOPATH`, `GITHUB_COMMIT_URL`, and `GITHUB_EVENT_PATH`.

Dependencies and integration: Depends on Go 1.19, `jq`, `curl`, `git-validation`, `containerd/ltag`, and the local `script/validate/template`.

Risks and test signals: Empty `REPO_ACCESS_TOKEN` relies on unauthenticated API access for PR commit lookup. Validation passes when commit metadata and headers meet containerd project rules.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/.github/workflows/project-checks.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/.github/workflows/release.yml -->
# sources/cloud-native/overlaybd/.github/workflows/release.yml

Purpose: Multi-distro, multi-architecture release packaging and GitHub release publication.

APIs and control flow: On pushes to `main` and `v*` tags, matrix builds cover Ubuntu 18.04 through 24.04, CentOS 8, CBL-Mariner 2.0, Azure Linux 3.0, and amd64/arm64. Untagged builds derive the next patch `rc`; tagged builds strip the leading `v`. Docker buildx invokes the release Dockerfile with build args, filters irrelevant package type per OS, uploads artifacts, then creates either a prerelease `latest` or tagged release.

State and persistence: Produces `releases/overlaybd-*.*` artifacts and GitHub release assets.

Dependencies and integration: Uses Docker buildx, QEMU, artifact actions, and `marvinpinto/action-automatic-releases`.

Risks and test signals: Version derivation assumes semantic `vX.Y.Z` tags. Package correctness is validated by successful Docker builds, expected RPM/DEB pruning, and uploaded artifact names.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/.github/workflows/release.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/.github/workflows/release/Dockerfile -->
# sources/cloud-native/overlaybd/.github/workflows/release/Dockerfile

Purpose: Buildx packaging wrapper that runs the distro-specific release build in a chosen base image and exports only package artifacts.

APIs and control flow: The first stage accepts `BUILD_IMAGE`, copies the repository into `/src`, receives OS, version, release number, and commit ID build args, chmods `build.sh`, and executes it. The final scratch stage copies `/src/build/overlaybd-*.*` to the image root for `docker buildx -o`.

State and persistence: Build outputs are left in `/src/build` in the builder and exported from scratch.

Dependencies and integration: Called by `release.yml`; depends on the shell script handling all package-manager and CMake work.

Risks and test signals: A missing package glob makes the scratch copy fail. Build arg sanitation and script exit status are the main controls.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/.github/workflows/release/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/.github/workflows/release/build.sh -->
# sources/cloud-native/overlaybd/.github/workflows/release/build.sh

Purpose: Distro-aware package build script used inside release containers.

APIs and control flow: Positional args are `OS`, `PACKAGE_VERSION`, `RELEASE_NO`, and `COMMIT_ID`. The script installs dependencies with `apt`, `yum`, or `tdnf`, handles CentOS vault repos and toolset compilers, downloads a fixed CMake binary by architecture, configures CMake with package version/release and `OBD_VER`, builds, then runs `cpack --verbose`.

State and persistence: Creates `/usr/local/cmake-*`, a repository-local `build` directory, and generated RPM/DEB packages.

Dependencies and integration: Needs package managers, compilers, libaio, curl, OpenSSL, libnl3, e2fsprogs, zstd, rpm-build/dpkg tooling, and network access to cmake.org.

Risks and test signals: `--no-check-certificate` and external downloads reduce supply-chain assurance. Test signal is successful CMake configure, `make -j8`, and CPack output.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/.github/workflows/release/build.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/CMake/FindCURL.cmake -->
# sources/cloud-native/overlaybd/CMake/FindCURL.cmake

Purpose: Custom libcurl resolver with optional static-from-source build.

APIs and control flow: When `BUILD_CURL_FROM_SOURCE` is true, FetchContent clones curl tag `curl-7_42_1`, runs autotools configure with HTTP-only static options and OpenSSL root, creates `libcurl_static_build`, and defines/imports `CURL::libcurl`. Otherwise it delegates to CMake's built-in FindCURL.

State and persistence: Builds curl into the FetchContent binary tree and exposes include/lib variables.

Dependencies and integration: Depends on `FindOpenSSL.cmake`, zlib, autotools, make, and CMake target dependencies. `src/CMakeLists.txt` consumes `CURL_LIBRARIES` and `CURL_INCLUDE_DIRS`.

Risks and test signals: Old curl plus disabled protocols are intentional but security-sensitive. Static target correctness is verified by successful link of registryfs and image service.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/CMake/FindCURL.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/CMake/FindOpenSSL.cmake -->
# sources/cloud-native/overlaybd/CMake/FindOpenSSL.cmake

Purpose: Custom OpenSSL resolver that can build OpenSSL 1.0.2 static libraries for bundled curl builds.

APIs and control flow: If `BUILD_CURL_FROM_SOURCE` is true, FetchContent clones `OpenSSL_1_0_2-stable`, runs `sh config -fPIC no-unit-test no-shared`, builds and installs into the binary tree, then defines imported targets `OpenSSL::SSL` and `OpenSSL::Crypto`. Otherwise it includes CMake's standard FindOpenSSL.

State and persistence: Produces static libssl/libcrypto and include directories under the FetchContent build output.

Dependencies and integration: `FindCURL.cmake` depends on `openssl102_static_build`.

Risks and test signals: OpenSSL 1.0.2 is obsolete and only acceptable for controlled compatibility. Link success and TLS registry access are the key functional signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/CMake/FindOpenSSL.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/CMake/FindRapidJSON.cmake -->
# sources/cloud-native/overlaybd/CMake/FindRapidJSON.cmake

Purpose: Locates RapidJSON via pkg-config or fetches a pinned Tencent RapidJSON revision.

APIs and control flow: `pkg_check_modules(RAPIDJSON RapidJSON)` is tried first. If not found, FetchContent populates `rapidjson` at commit `80b6d1...` without submodules and sets `RAPIDJSON_INCLUDE_DIRS`.

State and persistence: Only provides header include paths; RapidJSON is header-only.

Dependencies and integration: Config structs in `src/config.h` depend on RapidJSON through `ConfigUtils`.

Risks and test signals: FetchContent requires network unless dependency is cached. JSON config parsing in service and image configs exercises this path.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/CMake/FindRapidJSON.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/CMake/Findaio.cmake -->
# sources/cloud-native/overlaybd/CMake/Findaio.cmake

Purpose: Minimal finder for Linux libaio.

APIs and control flow: Uses `find_path` for `libaio.h`, `find_library` for `aio`, and `find_package_handle_standard_args` to populate `AIO_INCLUDE_DIR` and `AIO_LIBRARIES`.

State and persistence: No generated files or runtime state.

Dependencies and integration: `src/CMakeLists.txt` links `${AIO_LIBRARIES}` into image library and `overlaybd-tcmu`; direct IO paths in `ImageFile` select `ioengine_libaio`.

Risks and test signals: Header/library mismatch would appear at compile or link time. CI installs `libaio-dev`.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/CMake/Findaio.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/CMake/Finde2fs.cmake -->
# sources/cloud-native/overlaybd/CMake/Finde2fs.cmake

Purpose: Resolves ext2fs either from the system or from a pinned fork build.

APIs and control flow: If `ORIGIN_EXT2FS` is false, FetchContent clones `data-accelerator/e2fsprogs`, runs its `build.sh`, creates target `libext2fs_build`, and imports `${LIBEXT2FS_INSTALL_DIR}/lib/libext2fs.so`. Otherwise it finds `ext2fs/ext2fs.h` and library `ext2fs`.

State and persistence: Bundled builds create an installed lib/include tree under the e2fsprogs source build directory and later install lib files into `/opt/overlaybd`.

Dependencies and integration: `Findphoton.cmake` adds `photon_obj` dependency on `libext2fs` when bundled.

Risks and test signals: The custom build script and shared library path are fragile. Ext4 base layer and mkfs/apply workflows validate this dependency.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/CMake/Finde2fs.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/CMake/Findphoton.cmake -->
# sources/cloud-native/overlaybd/CMake/Findphoton.cmake

Purpose: Fetches PhotonLibOS and wires it into OverlayBD.

APIs and control flow: Sets `PHOTON_ENABLE_EXTFS ON`, fetches PhotonLibOS `v0.6.17`, temporarily disables `BUILD_TESTING` while bringing Photon in, then records `PHOTON_INCLUDE_DIR`. It adds dependency edges from `photon_obj` to bundled CURL/OpenSSL and ext2fs targets when those options are active.

State and persistence: Photon is built as a CMake dependency and later linked as `photon_static`.

Dependencies and integration: Nearly all runtime code uses Photon filesystems, threads, HTTP, curl, metrics, and event loops.

Risks and test signals: Global `BUILD_TESTING` mutation is order-sensitive. Compile/link of all runtime targets is the primary signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/CMake/Findphoton.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/CMake/Findtcmu.cmake -->
# sources/cloud-native/overlaybd/CMake/Findtcmu.cmake

Purpose: Fetches the Photon-adapted libtcmu fork used by `overlaybd-tcmu`.

APIs and control flow: FetchContent clones `data-accelerator/photon-libtcmu` at a pinned commit and temporarily disables nested testing. It exposes `TCMU_INCLUDE_DIR`.

State and persistence: Builds a CMake subdependency consumed as `tcmu_static`.

Dependencies and integration: `src/main.cpp` includes libtcmu and SCSI headers to register the `overlaybd` TCMU subtype.

Risks and test signals: Kernel/user ABI mismatches appear at daemon startup or configfs device creation. CI E2E configfs tests validate it.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/CMake/Findtcmu.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/CMake/pack.cmake -->
# sources/cloud-native/overlaybd/CMake/pack.cmake

Purpose: Defines CPack metadata for RPM and DEB packages.

APIs and control flow: Sets package version, name, release, contact/vendor, install prefix, filename pattern, RPM license/summary/description, and Debian version/shlibdeps before including `CPack`.

State and persistence: Generates RPM/DEB package files during `cpack`.

Dependencies and integration: Release script passes `PACKAGE_VERSION` and `PACKAGE_RELEASE`; installation rules in CMakeLists supply daemon binary, service unit, configs, base layer, and bundled ext2fs libs.

Risks and test signals: `CPACK_DEBIAN_PACKAGE_SHLIBDEPS` depends on distro tooling. Package file naming and release assets validate the path.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/CMake/pack.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/CMakeLists.txt -->
# sources/cloud-native/overlaybd/CMakeLists.txt

Purpose: Top-level build definition for OverlayBD.

APIs and control flow: Requires CMake 3.14, enables C/C++, restricts CPU architectures to x86_64/aarch64/arm64, sets output paths, module path, warning and version flags, optional static libstdc++, locates zstd, and declares options for bundled curl, stream convertor, and ext2fs source. It fetches Photon and TCMU, optionally yaml-cpp, enables CTest, adds `src` and `baselayers`, and includes packaging.

State and persistence: Uses `build/output` for runtime binaries and base layer extraction.

Dependencies and integration: Centralizes external dependency configuration for all runtime and tools.

Risks and test signals: Architecture and static library detection are host-sensitive. CI configure and package builds are the main tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/baselayers/CMakeLists.txt -->
# sources/cloud-native/overlaybd/baselayers/CMakeLists.txt

Purpose: Builds and installs the bundled ext4 base layer artifact.

APIs and control flow: A custom command extracts `ext4_64.tar.gz` into `${EXECUTABLE_OUTPUT_PATH}` as `ext4_64`; target `baselayer` is built by default and installs the file to `/opt/overlaybd/baselayers`.

State and persistence: Produces `build/output/ext4_64` and package/install content.

Dependencies and integration: Used by image creation/apply paths that need a filesystem base layer.

Risks and test signals: Tarball integrity and extraction destination are the critical risks. CI `overlaybd-apply --mkfs` exercises this asset indirectly.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/baselayers/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/CMakeLists.txt -->
# sources/cloud-native/overlaybd/src/CMakeLists.txt

Purpose: Builds the image service library and the `overlaybd-tcmu` daemon.

APIs and control flow: Finds CURL, OpenSSL, aio, and RapidJSON, links common system libs, adds `overlaybd`, compiles `overlaybd_image_lib` from image file/service, background download, prefetch, switch file, API server, and tools, then builds `overlaybd-tcmu` from `main.cpp`.

State and persistence: Installs daemon to `/opt/overlaybd/bin`, service unit to `/opt/overlaybd`, default config to `/etc/overlaybd`, credentials example to `/opt/overlaybd`, and bundled ext2fs libs when applicable.

Dependencies and integration: Links Photon, overlaybd libraries, tcmu, curl, OpenSSL, and aio.

Risks and test signals: Library order and imported variables are sensitive. Build, install, systemd start, and CTest validate it.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/api_server.cpp -->
# sources/cloud-native/overlaybd/src/api_server.cpp

Purpose: Optional HTTP API for live snapshot creation on an existing image device.

APIs and control flow: `ApiHandler::handle_request` parses `/snapshot?dev_id=...&config=...`, validates parameters, locates the `ImageFile` in `ImageService`, calls `ImageFile::create_snapshot`, and writes a JSON success/error body. `parse_params` URL-decodes query pairs. `ApiServer::init` binds a Photon TCP server from `serviceConfig.address`, registers the `/snapshot` handler, and starts the loop.

State and persistence: Mutates active image state via snapshot restack and config rename; keeps a handler params map in memory.

Dependencies and integration: Uses Photon HTTP/socket/URL APIs and `ImageService::find_image_file`.

Risks and test signals: The handler map is not cleared per request, so stale params can survive on reused handler instances. Snapshot API tests should cover missing params, unknown dev_id, bad config, and repeated requests.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/api_server.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/api_server.h -->
# sources/cloud-native/overlaybd/src/api_server.h

Purpose: Declares API server lifecycle functions for the optional live snapshot HTTP service.

APIs and control flow: `start_api_server(ApiServer *&, ImageService *, const std::string &)` allocates and initializes an `ApiServer`; `stop_api_server(ApiServer *)` destroys it. `ApiServer` is forward-declared elsewhere.

State and persistence: Holds no state itself, but the pointer contract transfers heap object ownership to callers.

Dependencies and integration: Included by `image_service.cpp`, which starts the server when `serviceConfig.enable` is true.

Risks and test signals: The header relies on prior declarations of `ApiServer`, `ImageService`, and `std::string`; include order matters. Build failures catch signature drift.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/api_server.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/bk_download.cpp -->
# sources/cloud-native/overlaybd/src/bk_download.cpp

Purpose: Implements delayed background download of remote layer blobs into local layer directories.

APIs and control flow: `check_downloaded` checks for `overlaybd.commit`. `BkDownload::download` short-circuits existing committed blobs, otherwise downloads into `.download`, verifies SHA256, renames to `overlaybd.commit`, and switches the active `ISwitchFile` to the local file. `download_blob` reads the source file in aligned blocks, optionally throttled, resumes sparse holes via `SEEK_HOLE`, and retries read/write failures. `bk_download_proc` delays startup, serializes per-dir locks, retries failed downloads, and exits when the owning image status changes.

State and persistence: Writes `.download` and `overlaybd.commit` under each layer dir; in-memory static `lock_files` guards duplicate downloads.

Dependencies and integration: Uses Photon localfs, throttled files, audit logging, `switch_file`, and `sha256file`.

Risks and test signals: `lock_files` is unsynchronized across threads. Sparse-file resume depends on filesystem `SEEK_HOLE`. Tests should corrupt `.download`, simulate retries, and verify switch-to-local behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/bk_download.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/bk_download.h -->
# sources/cloud-native/overlaybd/src/bk_download.h

Purpose: Public interface for background layer download.

APIs and types: Defines `BKDL::DOWNLOAD_TMP_NAME`, `check_downloaded`, class `BkDownload`, and `bk_download_proc`. `BkDownload` owns a source `IFile`, references an `ISwitchFile`, keeps file size, digest, URL, throttle, block size, retry count, target dir, and a reference to image running status.

State and persistence: The destructor unlocks the dir and deletes the source file. Downloaded state is represented by files on disk.

Dependencies and integration: `ImageFile::__open_ro_remote` creates `BkDownload` items when per-image download config is enabled.

Risks and test signals: Constructor takes `running` by reference, so lifetime must remain valid until thread completion; `ImageFile` destructor joins the thread to enforce this.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/bk_download.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/config.h -->
# sources/cloud-native/overlaybd/src/config.h

Purpose: Declarative JSON configuration schema for image files, global service behavior, credentials, caching, logging, metrics, prefetch, TLS, and API service.

APIs and types: Uses `ConfigUtils::Config` and `APPCFG_PARA` macros. Key structs are `LayerConfig`, `UpperConfig`, `DownloadConfig`, `ImageConfig`, `P2PConfig`, `GzipCacheConfig`, `ExporterConfig`, `CredentialConfig`, `CacheConfig`, `LogConfig`, `PrefetchConfig`, `CertConfig`, `ServiceConfig`, `GlobalConfig`, `AuthConfig`, and `ImageAuthResponse`.

State and persistence: Configs are parsed from `/etc/overlaybd/overlaybd.json`, image config files, and credential JSON; snapshot code renames a new image config over the active config.

Dependencies and integration: Read by `ImageService`, `ImageFile`, credential loading, exporter setup, and API setup.

Risks and test signals: Defaults preserve backward compatibility between legacy top-level cache/log fields and nested configs. Tests should parse old and new example configs.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/config.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/example_config/cred.json -->
# sources/cloud-native/overlaybd/src/example_config/cred.json

Purpose: Example Docker-style credential file.

APIs and control flow: Contains top-level `auths` keyed by registry host, with explicit `username` and `password` fields. `load_cred_from_file` parses this into `AuthConfig`, and `parse_auths` matches host/path prefixes against requested blob URLs.

State and persistence: Installed to `/opt/overlaybd/cred.json` as sample data unless replaced.

Dependencies and integration: Referenced by default `credentialConfig` examples.

Risks and test signals: Placeholder credentials must not be used in production. Tests should verify both explicit username/password and base64 `auth` variants.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/example_config/cred.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/example_config/overlaybd-registryv2.json -->
# sources/cloud-native/overlaybd/src/example_config/overlaybd-registryv2.json

Purpose: Registry v2 global service config optimized for CI E2E.

APIs and control flow: Enables file cache, file credential mode, ioEngine 0, delayed background download, disabled P2P, audit logging, and `registryFsVersion` v2.

State and persistence: Directs logs to `/var/log/overlaybd.log`, audit logs to `/var/log/overlaybd-audit.log`, cache to `/opt/overlaybd/registry_cache`, and credentials to `/opt/overlaybd/cred.json`.

Dependencies and integration: Copied to `/etc/overlaybd/overlaybd.json` in CI before starting `overlaybd-tcmu`.

Risks and test signals: Download delay is 600 seconds, so CI mostly validates open/mount and not full background download completion. Config parsing and daemon startup validate shape.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/example_config/overlaybd-registryv2.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/example_config/overlaybd-tcmu.service -->
# sources/cloud-native/overlaybd/src/example_config/overlaybd-tcmu.service

Purpose: systemd unit for the OverlayBD TCMU daemon.

APIs and control flow: Loads `target_core_user` before start, runs `/opt/overlaybd/bin/overlaybd-tcmu`, restarts always, raises NOFILE, preserves core dumps, and keeps the process alive independently of shutdown ordering.

State and persistence: systemd owns restart state; daemon writes logs and configfs state separately.

Dependencies and integration: Installed by CMake and enabled in CI. Requires root privileges and kernel target_core_user support.

Risks and test signals: `KillMode=process` may leave child/thread cleanup to daemon behavior. Validation is `systemctl start/status` and successful configfs device creation.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/example_config/overlaybd-tcmu.service -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/example_config/overlaybd.json -->
# sources/cloud-native/overlaybd/src/example_config/overlaybd.json

Purpose: General default global config for installed OverlayBD.

APIs and control flow: Configures file registry cache, optional gzip cache enabled by default, file credentials, ioEngine 0, delayed background download, disabled P2P, disabled metrics exporter, audit logging, registryfs v2, and disabled snapshot service.

State and persistence: Uses `/opt/overlaybd/registry_cache`, `/opt/overlaybd/gzip_cache`, `/opt/overlaybd/cred.json`, `/var/log/overlaybd.log`, and `/var/log/overlaybd-audit.log`.

Dependencies and integration: Installed to `/etc/overlaybd/overlaybd.json` and parsed by `ImageService::read_global_config_and_set`.

Risks and test signals: Gzip cache consumes extra disk when enabled. Tests should start daemon with this default and verify cache directory creation.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/example_config/overlaybd.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/example_config/redis.obd.config.json -->
# sources/cloud-native/overlaybd/src/example_config/redis.obd.config.json

Purpose: Example image config for a read-only Redis image backed by remote registry blobs.

APIs and control flow: Sets `repoBlobUrl`, seven lower layer records with `digest`, `size`, and local `dir`, empty upper config for read-only behavior, and a `resultFile`.

State and persistence: Background download may populate `/var/lib/overlaybd/test/<n>/.download` and `overlaybd.commit`; init status is written to `/var/lib/overlaybd/init-debug.log`.

Dependencies and integration: Used by CI configfs command `dev_config=overlaybd/.../redis.obd.config.json`.

Risks and test signals: Remote Docker Hub availability and credentials can affect opens. Mounting read-only and listing files validate the config.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/example_config/redis.obd.config.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/example_config/stream-conv.yaml -->
# sources/cloud-native/overlaybd/src/example_config/stream-conv.yaml

Purpose: Example YAML config for the stream convertor component.

APIs and control flow: Defines `globalConfig` fields for work dir, Unix socket address, optional HTTP address, HTTP port, reusePort, and log config.

State and persistence: Points work to `/tmp/stream_conv`, UDS to `/var/run/stream_conv.sock`, and logs to `/var/log/overlaybd/stream_convertor.log`.

Dependencies and integration: Parsed by the stream convertor subdirectory when `BUILD_STREAM_CONVERTOR` is enabled.

Risks and test signals: This subset only builds the option through CMake; functional signals belong to stream convertor tests and startup with yaml-cpp.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/example_config/stream-conv.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/exporter_handler.h -->
# sources/cloud-native/overlaybd/src/exporter_handler.h

Purpose: Prometheus text handler for OverlayBD metrics.

APIs and control flow: `ExposeMetrics::ExposeRender` stores tagged metric pointers for throughput, qps, latency, count, and cache values. `render` emits an alive gauge and each registered metric in Prometheus text format. `handle_request` returns HTTP 200 with content type `text/plain; version=0.0.4`.

State and persistence: Metrics live in memory and are sampled from Photon counters; no persisted state.

Dependencies and integration: Used by `OverlayBDMetric` and `ExporterServer` when exporter config is enabled.

Risks and test signals: Metric name typo `Throughtput` is externally visible. Tests should GET `/metrics` and verify alive plus read/download counters after IO.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/exporter_handler.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/exporter_server.h -->
# sources/cloud-native/overlaybd/src/exporter_server.h

Purpose: HTTP server wrapper and metric registry for Prometheus export.

APIs and types: `OverlayBDMetric` owns `MetricMeta pread` and `download`, then registers them with `ExposeRender`. `ExporterServer` binds a Photon TCP socket on configured port, creates an HTTP server, installs the metrics handler under `uriPrefix`, starts the loop, and marks `ready`.

State and persistence: Holds live socket and HTTP server pointers; all state is in memory.

Dependencies and integration: `ImageService::init` wraps registry/cache filesystems with `MetricFS` and starts this server when enabled.

Risks and test signals: Bind failures abort image service initialization. Validation is startup with exporter enabled and HTTP scrape response.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/exporter_server.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/image_file.cpp -->
# sources/cloud-native/overlaybd/src/image_file.cpp

Purpose: Builds the per-device image file by opening remote/local lower layers, optional writable upper layer, gzip target data, prefetch traces, and background download.

APIs and control flow: Local lower paths prefer explicit `file`, then downloaded `overlaybd.commit`, then `overlaybd.sealed`; otherwise remote URLs are opened through `global_fs.remote_fs`. Remote layers set local dir and size via ioctl for download cache, wrap blob streams as tar, then as switch files. `open_lower_layer` optionally adds prefetch, target file/digest, gzip index, gzip cache, and LSMT warp. `open_lowers` opens layers in parallel Photon threads and stacks them with `LSMT::open_files_ro`. `open_upper` opens LSMT RW files or turboOCI target data. `init_image_file` handles acceleration layers, trace record/replay, read-only or RW stacking, and starts background download. `create_snapshot` opens a new upper, restacks the live RW file, moves the old upper into lowers, updates combo indices, and renames the new config over the active config.

State and persistence: Uses layer dirs, commit/sealed files, upper index/data/target files, trace files, and active config rename. `m_status` controls lifecycle and download cancellation.

Dependencies and integration: Heavy use of Photon FS, registry/cache fs, LSMT, gzip/gzindex, tar adaptor, prefetcher, switch file, and `ImageService`.

Risks and test signals: ParallelOpenTask increments without locking, so real concurrency depends on Photon scheduling safety. Snapshot index manipulation is delicate. Tests should cover RO mount, RW writes, gzip target layers, failed auth, background download, prefetch, and snapshot restart.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/image_file.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/image_file.h -->
# sources/cloud-native/overlaybd/src/image_file.h

Purpose: Defines the `ImageFile` abstraction exposed to TCMU as a Photon `ForwardFile`.

APIs and types: Constants `COMMIT_FILE_NAME` and `SEALED_FILE_NAME` name local layer states. `ImageFile` overrides `fstat`, `preadv`, `pwritev`, `fdatasync`, and `fallocate`, exposes `get_base`, `compact`, `create_snapshot`, `open_lower_layer`, and `set_auth_failed`, and privately manages lower/upper opening plus background download.

State and persistence: Stores copied image config, config path, download list/thread, lower/upper backing files, dev id, block size, size, LBA count, read-only flag, status, and exception message.

Dependencies and integration: Constructed by `ImageService::create_image_file`; used by `main.cpp` SCSI command handlers.

Risks and test signals: Constructor registers the object before init completes and unregisters in destructor. Lifetime tests should verify duplicate dev id rejection and download thread join.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/image_file.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/image_service.cpp -->
# sources/cloud-native/overlaybd/src/image_service.cpp

Purpose: Owns global configuration, registry access, cache layers, metrics/exporter, API server, credentials, and active image file registry.

APIs and control flow: Helpers parse blob URLs and auth entries, load credentials from file/http/https with optional mTLS, set result files, derive cache names, and probe P2P accelerator connectivity. `init` reads config, configures logging/audit, creates registryfs v1/v2 with CA certs and user agent, wraps metrics, creates file/ocf/download cache, optional gzip cache, and optional snapshot API server. `enable_acceleration` toggles registry acceleration and chooses `remote_fs`. `create_image_file` merges default download config, parses image config, creates `ImageFile`, and writes success/failure to `resultFile`. Register/find/unregister manage dev_id mapping.

State and persistence: Creates cache dirs/media files, OCF namespace/media, log/audit files, gzip cache dir, result files, and in-memory active-image map.

Dependencies and integration: RegistryFS, cache factories, MetricFS, ExporterServer, ApiServer, ConfigUtils, Photon curl/socket/localfs.

Risks and test signals: Destructor deletes `srcfs` after `cached_fs`, but metric wrapping ownership needs care. Credential URL query is not escaped. Tests should cover cache modes, auth modes, exporter/API startup, and duplicate dev ids.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/image_service.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/image_service.h -->
# sources/cloud-native/overlaybd/src/image_service.h

Purpose: Public service interface and shared global filesystem state for OverlayBD image creation.

APIs and types: `GlobalFs` stores underlay registry fs, remote/source/cache fs, gzip cache fs, OCF media/namespace filesystems, and IO allocator. `ImageService` exposes `init`, `create_image_file`, `enable_acceleration`, image registration lookup methods, global config, metrics, exporter, and API server. Free functions create the service and load credentials.

State and persistence: `m_config_path` selects the global JSON; `m_image_files` maps dev_id to live images.

Dependencies and integration: Included by `main.cpp`, API server, image file, and metrics code.

Risks and test signals: `ImageAuthResponse` is also declared in `config.h`, a duplication that can drift. Compile and credential parsing tests catch schema mismatch.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/image_service.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/main.cpp -->
# sources/cloud-native/overlaybd/src/main.cpp

Purpose: `overlaybd-tcmu` daemon entry point and SCSI command bridge from kernel TCMU devices to `ImageFile` operations.

APIs and control flow: Initializes Photon, signals, image service, rlimit, and TCMU netlink block/reset. Registers TCMU handler subtype `overlaybd`. `dev_open` parses `dev_config=overlaybd/<config>[;<dev_id>]`, creates an image file, sets TCMU capacity/write-protect, and starts per-device event loop. `TCMULoop` watches the master fd; `TCMUDevLoop` reads commands and dispatches through a Photon thread pool. `cmd_handler` emulates inquiry/capacity/mode commands, maps READ to retried `preadv`, WRITE to `pwritev`, sync to `fdatasync`, and WRITE SAME unmap to `fallocate`.

State and persistence: Holds global `imgservice`, main loop, per-device `obd_dev`, configfs device state, inflight counts, and thread objects.

Dependencies and integration: libtcmu, SCSI headers, Photon event loop/thread pool, systemd unit, kernel target_core_user.

Risks and test signals: `sure` can retry for seven days, masking stuck IO. Netlink buffer tuning requires privileges. E2E configfs mount/read/write-protect tests are essential.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/main.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/metrics_fs.h -->
# sources/cloud-native/overlaybd/src/metrics_fs.h

Purpose: Filesystem and file wrappers that record read metrics.

APIs and types: `MetricMeta` groups latency, throughput, qps, total, and interval counters. `MetricFile` wraps `pread`, `preadv`, and `preadv2`, incrementing qps, latency, throughput, and total on positive reads. `MetricFS` wraps `open` calls to return `MetricFile`.

State and persistence: Metrics are in-memory Photon counters.

Dependencies and integration: `ImageService` wraps underlay registryfs for download metrics and cached fs for pread metrics when exporter is enabled.

Risks and test signals: Only read paths are tracked, and interval counter is not rendered by current exporter. Tests should assert counter changes after remote and cached reads.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/metrics_fs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/CMakeLists.txt -->
# sources/cloud-native/overlaybd/src/overlaybd/CMakeLists.txt

Purpose: Aggregates OverlayBD sublibraries into an interface target.

APIs and control flow: Adds registryfs, lsmt, zfile, zstd, cache, tar, gzip, gzindex, and optional stream convertor subdirectories, then defines `overlaybd_lib` as an interface library with Photon include dirs and links to all component libs.

State and persistence: No runtime state; establishes build graph.

Dependencies and integration: Consumed by `overlaybd_image_lib`, daemon, tools, and tests.

Risks and test signals: Interface target hides link ordering complexity. Full build and tool linking validate component coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/base64.h -->
# sources/cloud-native/overlaybd/src/overlaybd/base64.h

Purpose: Header-only base64 encode/decode helpers.

APIs and control flow: Defines `base64_chars`, `is_base64`, `base64_encode(BYTE const*, unsigned int)`, and `base64_decode(std::string const&)`. Encoding groups bytes into 3-to-4 chunks and pads with `=`; decoding stops at `=` or non-base64 input and reconstructs bytes.

State and persistence: Stateless pure helpers.

Dependencies and integration: `ImageService::parse_auths` decodes Docker-style `auth` values into `username:password`.

Risks and test signals: Decode silently stops at invalid characters rather than reporting errors. Unit tests should cover padding, empty input, malformed auth, and colon splitting.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/base64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/CMakeLists.txt -->
# sources/cloud-native/overlaybd/src/overlaybd/cache/CMakeLists.txt

Purpose: Build definition for the cache subsystem.

APIs and control flow: Adds full-file, OCF, download, and gzip cache subdirectories, globs local cache cpp files into `cache_lib`, links cache implementations plus Photon, and includes cache tests when testing is enabled.

State and persistence: No runtime state; controls which cache factories link into `overlaybd_lib`.

Dependencies and integration: `cache_lib` exports `new_full_file_cached_fs`, `new_ocf_cached_fs`, `new_download_cached_fs`, and gzip cache support through linked sublibraries.

Risks and test signals: `file(GLOB)` can miss new source files until CMake reconfigure. Cache tests and daemon cache-mode startup cover it.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/cache.cpp -->
# sources/cloud-native/overlaybd/src/overlaybd/cache/cache.cpp

Purpose: Implements common cache factory wiring and the base `ICachePool` store object cache.

APIs and control flow: `new_full_file_cached_fs` validates refill alignment and power-of-two constraints, creates `FileCachePool`, initializes it, and wraps it with `new_cached_fs`. `ICachePool` owns an `ObjectCache` of stores, optional thread pool, and source-name translation. `open` transforms names, creates or acquires cache stores, initializes metadata and pool linkage, tracks refcounts, and records size from `fstat`. `stores_clear`, `set_trans_func`, and `store_release` manage lifecycle.

State and persistence: Store cache keys map to persistent cache files managed by concrete pools.

Dependencies and integration: Used by full-file and gzip cache factories.

Risks and test signals: Refcount/ObjectCache interaction is subtle. Tests should open the same path concurrently and ensure release, eviction, and metadata remain consistent.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/cache.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/cache.h -->
# sources/cloud-native/overlaybd/src/overlaybd/cache/cache.h

Purpose: Public cache interfaces and factory declarations.

APIs and types: Defines cache open flags, read/write v2 flags, stat marker helpers, `IOCTL_GET_PAGE_SIZE`, `ICachedFileSystem`, `ICachedFile`, and factories for generic, full-file, OCF, and download caches. `ICachedFile` maps refill to writes, prefetch to `fadvise(WILLNEED)`, query to `fiemap`, and eviction to `trim`.

State and persistence: Interface abstracts persistent cache stores and source filesystems.

Dependencies and integration: Consumed by `ImageService`, cache implementations, and wrappers.

Risks and test signals: Some methods are `UNIMPLEMENTED` in interfaces and only valid through concrete types. Build and cache-mode smoke tests verify factory linkage.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/cache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/cached_fs.cpp -->
# sources/cloud-native/overlaybd/src/overlaybd/cache/cached_fs.cpp

Purpose: Generic cached filesystem and cached file implementation over an `ICachePool`.

APIs and control flow: `CachedFs::open` opens a cache store, binds source filesystem, page size, allocator, and returns `CachedFile`. It proxies many filesystem metadata/xattr operations to the source and evicts cache on unlink. `CachedFile` routes preads/pwrites to the cache store, `fstat` uses actual size or source fstat, `query` asks for refill ranges, `fallocate` evicts aligned ranges, and `fadvise(WILLNEED)` prefetches in chunks up to 32 MiB.

State and persistence: Cache contents live in stores; read/write offsets support sequential APIs.

Dependencies and integration: Backing implementation for full-file and gzip cache wrappers.

Risks and test signals: Source ownership is external while pool ownership is internal, so deletion ordering matters. Tests should cover partial misses, xattrs, unlink eviction, and prefetch EOF.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/cached_fs.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/download_cache/CMakeLists.txt -->
# sources/cloud-native/overlaybd/src/overlaybd/cache/download_cache/CMakeLists.txt

Purpose: Builds the on-demand download cache library.

APIs and control flow: Globs `*.cpp` into static library `download_cache_lib` and exposes Photon include directories.

State and persistence: No direct runtime state.

Dependencies and integration: Linked into `cache_lib`; factory `new_download_cached_fs` is selected by `ImageService` for `cacheType=download`.

Risks and test signals: Single-file glob is simple but reconfigure-dependent. Startup with download cache and layer reads validate it.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/download_cache/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/download_cache/download_cache.cpp -->
# sources/cloud-native/overlaybd/src/overlaybd/cache/download_cache/download_cache.cpp

Purpose: Implements a cache mode that lazily downloads registry data into per-layer local `.download` files as reads occur.

APIs and control flow: `DownloadCacheFs::open` opens the remote source and returns `DownloadCacheFile`. The file waits for `SET_LOCAL_DIR` and `SET_SIZE` ioctls before caching; until then it reads source directly. `preadv` aligns requested ranges, locks local ranges, queries holes with fiemap, reads missing refill ranges from source into an `IOVector`, writes them to local file, then serves from local. `DownloadCacheStore::query_refill_range` computes the missing hole and expands it to `refill_size`. `fallocate` evicts aligned ranges by trimming local sparse extents.

State and persistence: Persistent data is `dir/.download`, pooled by path in `ObjectCache`; range locks protect concurrent refills.

Dependencies and integration: `ImageFile::__open_ro_remote` sends local dir and size through ioctls.

Risks and test signals: `open(const char*,int,mode_t)` recursively calls itself, a likely bug if that overload is used. Tests should cover ioctl ordering, concurrent reads, sparse fiemap, and eviction.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/download_cache/download_cache.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/forwardcfs.h -->
# sources/cloud-native/overlaybd/src/overlaybd/cache/forwardcfs.h

Purpose: Forwarding wrappers that preserve cache-specific methods while delegating to Photon forward filesystems/files.

APIs and types: `ForwardCachedFileBase` forwards `get_source`, `set_source`, `get_store`, and `query`. `ForwardCachedFSBase` forwards `get_source`, `set_source`, `get_pool`, and `set_pool`. Type aliases provide ownership and non-ownership variants.

State and persistence: No state beyond wrapped `m_file` or `m_fs`.

Dependencies and integration: Useful for instrumentation or layering around `ICachedFile`/`ICachedFileSystem` without losing cache APIs.

Risks and test signals: Template protected inheritance assumes Photon forward base layout. Compile-time use catches API drift.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/forwardcfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/full_file_cache/CMakeLists.txt -->
# sources/cloud-native/overlaybd/src/overlaybd/cache/full_file_cache/CMakeLists.txt

Purpose: Builds the full-file cache implementation.

APIs and control flow: Globs `*.cpp` into static library `full_file_cache_lib` and exposes Photon include dirs.

State and persistence: No direct runtime state.

Dependencies and integration: Linked into `cache_lib`; `new_full_file_cached_fs` instantiates `FileCachePool` and `FileCacheStore`.

Risks and test signals: Build graph depends on reconfigure after adding source files. Cache unit tests and file cache mode daemon reads validate it.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/full_file_cache/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/full_file_cache/cache_pool.cpp -->
# sources/cloud-native/overlaybd/src/overlaybd/cache/full_file_cache/cache_pool.cpp

Purpose: Implements disk-backed full-file cache pool with LRU eviction.

APIs and control flow: Constructor computes water/risk marks from capacity and free-space targets. `Init` indexes existing media files and starts a periodic Photon timer. `do_open` creates media parent dirs, opens local cache files, inserts/accesses LRU entries, and returns `FileCacheStore`. `updateSpace` tracks disk-block usage and forces recycle near risk mark. `eviction` compares cache usage and filesystem free space, marks full, walks LRU from the back, truncates unopened or open files under locks, unlinks zero-size closed files, and updates total usage.

State and persistence: Maintains `fileIndex_`, LRU entries, total used bytes, and persistent cache files under `mediaFs_`.

Dependencies and integration: Used by generic full-file cache and gzip cache.

Risks and test signals: `afterFtrucate` logs unlink failure even when no error occurred. Eviction with open files and ENOSPC conditions need targeted tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/full_file_cache/cache_pool.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/full_file_cache/cache_pool.h -->
# sources/cloud-native/overlaybd/src/overlaybd/cache/full_file_cache/cache_pool.h

Purpose: Declares the `FileCachePool` LRU disk cache pool.

APIs and types: Exposes `Init`, `do_open`, `stat`, `evict`, `rename`, `isFull`, `removeOpenFile`, `forceRecycle`, `updateLru`, and `updateSpace`. `LruEntry` stores LRU iterator, open count, size, rwlock, and truncate flag; `FileNameMap` maps cache path to entries.

State and persistence: Owns media filesystem, timer, capacity thresholds, LRU container, file index, and usage counters.

Dependencies and integration: Creates `FileCacheStore` instances for generic cache reads/writes.

Risks and test signals: Iterator validity comments rely on map semantics and destruction order. Tests should simulate open file eviction and pool destruction.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/full_file_cache/cache_pool.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/full_file_cache/cache_store.cpp -->
# sources/cloud-native/overlaybd/src/overlaybd/cache/full_file_cache/cache_store.cpp

Purpose: Implements per-file media operations for full-file cache stores.

APIs and control flow: Reads take an LRU entry read lock, update LRU, and read from local media. Writes check pool fullness, truncate media to actual size after eviction, range-lock the target, write, fstat disk blocks, update LRU and usage, and trigger recycle on ENOSPC. `queryRefillRange` uses fiemap over aligned 4 KiB range to find the first/last hole and expands to `refillUnit_`. `evict` truncates or punches holes.

State and persistence: Owns local media file; updates shared pool entry size/open count and sparse extents.

Dependencies and integration: Called by `CachedFile` for cache hit/miss handling.

Risks and test signals: Fiemap extent cap of 1000 can fail large fragmented reads. Tests should cover fragmented files, truncation after eviction, and concurrent refills.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/full_file_cache/cache_store.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/full_file_cache/cache_store.h -->
# sources/cloud-native/overlaybd/src/overlaybd/cache/full_file_cache/cache_store.h

Purpose: Declares the concrete `FileCacheStore` used by the full-file cache pool.

APIs and types: Overrides `try_preadv2`, `do_preadv2`, `do_pwritev2`, `set_quota`, `stat`, `evict`, `queryRefillRange`, and `fstat`. Internal helpers cover cache-full checks, merged extents, hole calculation, and raw writes.

State and persistence: Holds pool pointer, owned local media file, refill unit, LRU file iterator, and range lock.

Dependencies and integration: Constructed by `FileCachePool::do_open`; implements `ICacheStore`.

Risks and test signals: Several admin APIs return ENOSYS. Unit tests should focus on read/write/query/evict behavior rather than unsupported quota/stat.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/full_file_cache/cache_store.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/gzip_cache/CMakeLists.txt -->
# sources/cloud-native/overlaybd/src/overlaybd/cache/gzip_cache/CMakeLists.txt

Purpose: Builds gzip target-file cache support.

APIs and control flow: Globs local cpp files into `gzip_cache_lib`, links `gzindex_lib`, and exposes Photon include dirs.

State and persistence: No direct runtime state.

Dependencies and integration: Used when global `gzipCacheConfig.enable` is true and a layer has `targetDigest` plus `gzipIndex`.

Risks and test signals: Requires gzindex linkage. Tests should open gzip-indexed target layers with gzip cache enabled.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/gzip_cache/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/gzip_cache/cached_fs.cpp -->
# sources/cloud-native/overlaybd/src/overlaybd/cache/gzip_cache/cached_fs.cpp

Purpose: Wraps gzip-decoded target files with the generic cache store.

APIs and control flow: `GzipCachedFsImpl` owns an `ICachePool`. `open_cached_gzip_file` normalizes cache key to an absolute path, opens/creates a store, binds the source gzfile, allocator, and page size, then returns `FileSystem::new_cached_file`.

State and persistence: Stores cached decompressed data in a `FileCachePool` backed by the configured gzip cache directory.

Dependencies and integration: `ImageFile::open_lower_layer` calls this after building `new_gzfile` for remote target data.

Risks and test signals: On cache store open failure the source file is deleted. Tests should verify digest-key naming and repeated opens share cache.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/gzip_cache/cached_fs.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/gzip_cache/cached_fs.h -->
# sources/cloud-native/overlaybd/src/overlaybd/cache/gzip_cache/cached_fs.h

Purpose: Public interface for gzip target-file cache.

APIs and types: Abstract `GzipCachedFs` declares `open_cached_gzip_file(IFile*, const char*)`. Factory `new_gzip_cached_fs` accepts media fs, refill unit, capacity, timer period, disk availability target, and allocator.

State and persistence: Implementations own a cache pool and persist cached data under the media filesystem.

Dependencies and integration: Held in `GlobalFs::gzcache_fs` and used by `ImageFile`.

Risks and test signals: Caller transfers source file ownership into the returned cached file. Tests should verify cleanup on error and successful cached reads.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/gzip_cache/cached_fs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/CMakeLists.txt -->
# sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/CMakeLists.txt

Purpose: Builds Open CAS Framework based cache integration.

APIs and control flow: Optionally adds tests, builds `ocf_env_lib` from ease binding environment cpp files, builds `ocf_lib` from OCF C sources with OCF and env includes plus zlib, then builds `ocf_cache_lib` from cache wrapper and ease bindings linked to OCF and Photon.

State and persistence: Build only; runtime state is OCF metadata/media managed by implementation files outside this subset plus ease bindings.

Dependencies and integration: Requires vendored OCF source, zlib, Photon, and env bindings.

Risks and test signals: C and C++ ABI boundaries and include ordering are fragile. OCF cache startup and reload tests are key.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/ease_bindings/ctx.cpp -->
# sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/ease_bindings/ctx.cpp

Purpose: Supplies OCF context operations for data buffers, cleaner stubs, and logging.

APIs and control flow: Implements iovec/buffer copy helpers, `ctx_data_alloc/free`, read/write/zero/seek/copy operations, no-op mlock/munlock/secure erase, no-op cleaner callbacks, and logger printing through Photon logging. `get_context_config` returns a static `ocf_ctx_config` with these ops.

State and persistence: Allocates OCF IO data through global `g_io_alloc`; each context data owns iov arrays and buffers.

Dependencies and integration: Used by `ease_ocf_provider::start` when creating OCF context.

Risks and test signals: `ctx_logger_print` uses `vsprintf` into a 512-byte buffer, risking overflow. Tests should stress large OCF log lines and data copy offsets.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/ease_bindings/ctx.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/ease_bindings/ctx.h -->
# sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/ease_bindings/ctx.h

Purpose: Shared OCF context data types for ease bindings.

APIs and types: Defines rounding macros, `OcfSrcFileCtx` owning a source Photon file plus namespace info/provider/path, `ease_ocf_io_data` carrying iovs, size, seek, block address, source ctx, error, semaphore, and prefetch flag, `ease_ocf_config`, `ease_ocf_queue`, and `get_context_config`.

State and persistence: Source file context deletes its source file on destruction; IO data semaphores synchronize async OCF completions.

Dependencies and integration: Included by provider, volume, and environment bindings.

Risks and test signals: Ownership is raw-pointer based. Tests should verify source file deletion and callback signaling on error paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/ease_bindings/ctx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/ease_bindings/env/ocf_env.cpp -->
# sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/ease_bindings/env/ocf_env.cpp

Purpose: Implements the userspace/Photon environment functions required by OCF.

APIs and control flow: Provides allocator create/new/delete/destroy, stack trace, crc32, optional execution-context mutexes, rwlock, mutex, completion, recursive mutex, spinlock, rwsem, and sleep operations. Most synchronization primitives wrap Photon locks/semaphores; CRC delegates to zlib.

State and persistence: Allocators track outstanding object count; synchronization objects allocate Photon primitives on heap.

Dependencies and integration: Linked into `ocf_env_lib` and used by vendored OCF C code.

Risks and test signals: Some trylock wrappers return `-OCF_ERR_NO_LOCK` when Photon `try_lock()` returns true, which may invert semantics depending on Photon API. OCF stress tests with contention are needed.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/ease_bindings/env/ocf_env.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/ease_bindings/env/ocf_env.h -->
# sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/ease_bindings/env/ocf_env.h

Purpose: Header compatibility layer that maps OCF environment requirements to userspace C/C++ and Photon-backed functions.

APIs and types: Defines Linux-like integer types, memory flags, debug/assert macros, container/list helpers, string/memory wrappers, secure memory stubs, allocator prototypes, mutex/rmutex/rwlock/rwsem/completion/atomic/spinlock APIs, bit ops, tick/time conversion, sort, sleep, crc32, and execution context APIs.

State and persistence: No persistent state; declarations back runtime state in `ocf_env.cpp`.

Dependencies and integration: Included by vendored OCF and ease bindings.

Risks and test signals: Many macros simplify kernel semantics, including interrupt context and secure memory. OCF unit and cache reload tests should exercise expected semantics.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/ease_bindings/env/ocf_env.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/ease_bindings/env/ocf_env_headers.h -->
# sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/ease_bindings/env/ocf_env_headers.h

Purpose: Minimal OCF environment version/header constants.

APIs and types: Includes stdint/stddef/stdbool and defines `OCF_LOGO`, short/long prefixes, and OCF version numbers `20.3.0`.

State and persistence: Stateless constants.

Dependencies and integration: Included by `ocf_env.h` and OCF code for logging/version compatibility.

Risks and test signals: Version constants must match vendored OCF expectations. Compile and OCF cache startup validate compatibility.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/ease_bindings/env/ocf_env_headers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/ease_bindings/env/ocf_env_list.h -->
# sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/ease_bindings/env/ocf_env_list.h

Purpose: Linux-kernel-style intrusive list helpers for OCF userspace environment.

APIs and control flow: Defines `list_head`, poison values, init, add, add_tail, empty, delete, move, entry, first_entry, and several iteration macros including safe variants.

State and persistence: List membership is embedded in caller-owned structs; no allocation.

Dependencies and integration: Used by OCF C code expecting kernel list APIs.

Risks and test signals: Iteration macros rely on nonstandard `typeof` and pointer arithmetic; C/C++ compiler compatibility matters. OCF build and list-heavy OCF tests validate behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/ease_bindings/env/ocf_env_list.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/ease_bindings/env/utils_mpool.cpp -->
# sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/ease_bindings/env/utils_mpool.cpp

Purpose: Implements OCF memory-pool allocation buckets.

APIs and control flow: `env_mpool_create` allocates an `env_mpool`, creates per-power-of-two allocators for element counts up to `mpool_max`, and records header/element sizes. `env_mpool_get_allocator` rounds requested count up to a power-of-two bucket. `env_mpool_new_f` allocates from that bucket or falls back to zero allocation if allowed. `env_mpool_del` frees via allocator or fallback free.

State and persistence: Owns allocator array and allocation size policy; no disk state.

Dependencies and integration: Used by OCF environment allocator paths.

Risks and test signals: `name_perfix` typo is API-compatible but confusing. Tests should cover count 0, bucket boundaries, fallback, and destroy with outstanding allocations.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/ease_bindings/env/utils_mpool.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/ease_bindings/env/utils_mpool.h -->
# sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/ease_bindings/env/utils_mpool.h

Purpose: Declares OCF memory-pool API.

APIs and types: Defines bucket enum `env_mpool_1` through `env_mpool_128`, opaque `env_mpool`, and functions to create, destroy, allocate, allocate with flags, and delete items.

State and persistence: Runtime allocator state is private to the implementation.

Dependencies and integration: Included by `ocf_env.h` and OCF code that requests variable-size arrays from pools.

Risks and test signals: Caller must pass the same count to delete that was used for allocation. Boundary tests around powers of two validate bucket selection.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/ease_bindings/env/utils_mpool.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/ease_bindings/provider.cpp -->
# sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/ease_bindings/provider.cpp

Purpose: Manages OCF cache/core lifecycle and submits aligned read IO through OCF.

APIs and control flow: `start` creates OCF context, registers volume type, sets write-through cache mode and cache-line size, starts cache, creates management and IO queues, initializes queues, loads or attaches media, and reloads or adds the core. `stop` disables logging, stops cache asynchronously, releases queues, cleans volumes, and releases context. `prepare_aligned_iov` and `copy_aligned_iov` adapt unaligned caller buffers to 512-byte sector-aligned IO. `ocf_pread` builds `ease_ocf_io_data`, creates an OCF read IO against the core, sets data/completion, submits, waits on a semaphore, handles errors, and copies padding-adjusted data back.

State and persistence: OCF metadata lives on media file via volume implementation; provider owns context, cache, core, queues, and volume params pointer.

Dependencies and integration: Used by OCF cached filesystem factory selected by `ImageService` for `cacheType=ocf`.

Risks and test signals: Error exits in `start` can leak partially created OCF objects. Tests should cover fresh attach, reload existing media, unaligned reads, prefetch flag path, and stop after failed start.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/ease_bindings/provider.cpp -->
