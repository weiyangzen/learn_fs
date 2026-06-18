# Group Research: group_1321_nvme_cli_sources_virtualization_nvme_cli_checkpatch_conf_sources_vi_70bd1db9a7d4

Scope confirmed against `Docs/research_subset_a.md`: all files are under `sources/virtualization/nvme-cli`, which is included in subset A. Each listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/.checkpatch.conf -->
# File Research: sources/virtualization/nvme-cli/.checkpatch.conf

- Purpose: local configuration for Linux `checkpatch.pl` when reviewing nvme-cli patches.
- Key behavior: marks the tree as non-kernel with `--no-tree`, sets max line length to 80, and suppresses warnings that are unsuitable for this userspace project or Gerrit-derived history.
- Notable ignores: `EMAIL_SUBJECT`, `FILE_PATH_CHANGES`, `GERRIT_CHANGE_ID`, `GIT_COMMIT_ID`, `NOT_UNIFIED_DIFF`, and `PREFER_DEFINED_ATTRIBUTE_MACRO`.
- Integration: consumed by the checkpatch workflow and Makefile targets indirectly through kernel `checkpatch.pl`.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/.checkpatch.conf -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/.github/codeql/codeql-config.yml -->
# File Research: sources/virtualization/nvme-cli/.github/codeql/codeql-config.yml

- Purpose: CodeQL configuration used by the Python CodeQL job.
- Key behavior: names the config and excludes `subprojects/**` from analysis.
- Research note: keeps vendored Meson fallback dependencies out of CodeQL findings.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/.github/codeql/codeql-config.yml -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/.github/dependabot.yml -->
# File Research: sources/virtualization/nvme-cli/.github/dependabot.yml

- Purpose: Dependabot configuration for GitHub Actions.
- Key behavior: checks workflow action dependencies weekly in repository root.
- Update policy: ignores semver patch updates for all dependencies, reducing low-value action bump churn.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/.github/dependabot.yml -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/.github/workflows/build.yml -->
# File Research: sources/virtualization/nvme-cli/.github/workflows/build.yml

- Purpose: main CI build matrix for nvme-cli and libnvme integration.
- Triggers: push and pull request to `master`, plus manual dispatch.
- Coverage: builds Debian/Fedora/Tumbleweed containers with GCC/Clang and debug/release modes; separately builds libnvme, cross targets, fallback shared libraries, muon minimal static, Makefile static, musl, no-fabrics, Alpine, distro-style split builds, and Windows MSYS2 UCRT64.
- Key implementation: most Linux jobs run `scripts/build.sh`; cross jobs use GHCR cross containers and QEMU setup; Windows installs MSYS2 packages and runs the same build script.
- Artifacts: failing jobs upload Meson logs from `.build-ci/meson-logs`.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/.github/workflows/build.yml -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/.github/workflows/check-accessors.yml -->
# File Research: sources/virtualization/nvme-cli/.github/workflows/check-accessors.yml

- Purpose: verifies generated accessor files are in sync with generator output.
- Triggers: push and pull request to `master`, plus manual dispatch.
- Key behavior: runs in the Debian nvme container, configures Meson with `-Dcheck-accessors=true`, then compiles `update-accessors`.
- Policy note: `.h`, `.c`, and `.i` outputs must be byte-identical; `.ld` files are compared at symbol level according to file comments.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/.github/workflows/check-accessors.yml -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/.github/workflows/checkpatch.yml -->
# File Research: sources/virtualization/nvme-cli/.github/workflows/checkpatch.yml

- Purpose: pull-request style review using kernel `checkpatch.pl`.
- Trigger: pull requests only.
- Key behavior: checks out the PR head with full history, downloads `checkpatch.pl` from Linux `master`, and pipes `git format-patch origin/${{ github.base_ref }}..HEAD` into it.
- Dependency: behavior is influenced by `.checkpatch.conf` in the repository root.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/.github/workflows/checkpatch.yml -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/.github/workflows/codeql.yml -->
# File Research: sources/virtualization/nvme-cli/.github/workflows/codeql.yml

- Purpose: CodeQL security/static analysis workflow.
- Triggers: push and pull request on `master`, plus weekly Friday schedule.
- Languages: matrix over `c-cpp` and `python`.
- Key behavior: installs Meson, initializes CodeQL per language, builds with `meson setup --force-fallback-for=json-c .build` and `ninja -C .build`, then runs CodeQL analyze.
- Python config: uses `.github/codeql/codeql-config.yml` to ignore `subprojects`.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/.github/workflows/codeql.yml -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/.github/workflows/coverage.yml -->
# File Research: sources/virtualization/nvme-cli/.github/workflows/coverage.yml

- Purpose: manual Codecov upload workflow.
- Trigger: `workflow_dispatch`.
- Key behavior: runs only for `linux-nvme/nvme-cli`, builds coverage with `scripts/build.sh -p`, then uploads `coverage.xml`.
- Policy: `continue-on-error: true` and `fail_ci_if_error: false`, so coverage upload does not block CI.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/.github/workflows/coverage.yml -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/.github/workflows/coverity.yml -->
# File Research: sources/virtualization/nvme-cli/.github/workflows/coverity.yml

- Purpose: scheduled/manual Coverity Scan submission.
- Triggers: weekly Monday 00:00 UTC and manual dispatch with optional ref.
- Key behavior: downloads Coverity build tools using secrets, configures Meson, runs `cov-build --dir cov-int ninja -C .build`, archives results, and uploads them to Coverity.
- Guard: runs only in `linux-nvme/nvme-cli`.
- Artifacts: on failure, uploads `cov-int/` and `nvme-cli-coverity.tgz`.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/.github/workflows/coverity.yml -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/.github/workflows/docs.yaml -->
# File Research: sources/virtualization/nvme-cli/.github/workflows/docs.yaml

- Purpose: documentation build CI.
- Triggers: push and pull request to `master` only when `Documentation/**` or `libnvme/doc/**` changes, plus manual dispatch.
- Key behavior: runs in Debian container and executes `scripts/build.sh docs`.
- Scope: validates nvme-cli and libnvme documentation generation paths.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/.github/workflows/docs.yaml -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/.github/workflows/libnvme-cleanup-python.yml -->
# File Research: sources/virtualization/nvme-cli/.github/workflows/libnvme-cleanup-python.yml

- Purpose: manual cleanup of libnvme development releases on TestPyPI.
- Inputs: `keep-last` defaults to 5; `dry-run` defaults to true.
- Key behavior: installs `pypi-cleanup`, enters `libnvme`, and deletes versions matching `.*\.dev[0-9]+` from TestPyPI unless dry-run is selected.
- Secret: uses `TEST_PYPI_API_TOKEN`.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/.github/workflows/libnvme-cleanup-python.yml -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/.github/workflows/libnvme-release-python.yml -->
# File Research: sources/virtualization/nvme-cli/.github/workflows/libnvme-release-python.yml

- Purpose: builds and publishes libnvme Python source distributions.
- Triggers: push to `master`, any tag push, and manual dispatch with optional tag input.
- Jobs: builds release sdist, builds dev/test sdist, uploads branch builds to TestPyPI, and uploads tagged release builds to PyPI.
- Dev versioning: derives `BASE_VERSION.devREV` from latest tag and commit count, patches `meson.build`, commits the CI-only bump, then builds sdist.
- Release gate: PyPI upload only for `refs/tags/v*` in `linux-nvme/nvme-cli` and only if tag matches the release regex.
- Note: uses deprecated `::set-output` syntax in the tag-check step.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/.github/workflows/libnvme-release-python.yml -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/.github/workflows/release.yml -->
# File Research: sources/virtualization/nvme-cli/.github/workflows/release.yml

- Purpose: creates GitHub releases for version tags.
- Trigger: push to `master` and all tags.
- Guard: job only runs for `refs/tags/v*` in `linux-nvme/nvme-cli`.
- Key behavior: uses `gh release create "${GITHUB_REF_NAME}" --generate-notes` with repository `GITHUB_TOKEN`.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/.github/workflows/release.yml -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/.github/workflows/run-nightly-tests.yml -->
# File Research: sources/virtualization/nvme-cli/.github/workflows/run-nightly-tests.yml

- Purpose: nightly hardware/VM regression and coverage workflow.
- Triggers: manual dispatch and daily schedule at 01:00 UTC.
- Main job: runs on self-hosted `arc-vm-nvme-cli`, checks out `linux-blktests/blktests-ci`, and uses a KubeVirt action with NVMe host devices.
- Test coverage: installs dependencies, builds mdadm from a pinned known-good commit, builds nvme-cli with coverage, runs blktests `nvme` and `md/001`, then runs nvme-cli’s own nvmetests in a privileged podman container.
- Artifacts/coverage: collects coverage XML reports and uploads them to Codecov in a follow-up job.
- Environment sensitivity: depends on `BDEV0`, host NVMe devices, custom runner, KubeVirt action, and GHCR containers.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/.github/workflows/run-nightly-tests.yml -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/.github/workflows/upload.yml -->
# File Research: sources/virtualization/nvme-cli/.github/workflows/upload.yml

- Purpose: builds and distributes static nvme-cli binaries.
- Triggers: pushes to `master`, `v*` tags, and published releases.
- Build job: computes `git describe` version, runs `scripts/build.sh static`, and packages `nvme-cli-latest-x86_64` plus versioned tag binary when applicable.
- Upload jobs: sends test binaries to an SFTP server and attaches release assets to GitHub releases.
- Secrets: SFTP upload uses username, server, host key, and private key secrets.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/.github/workflows/upload.yml -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/.readthedocs.yaml -->
# File Research: sources/virtualization/nvme-cli/.readthedocs.yaml

- Purpose: Read the Docs build configuration.
- Platform: Ubuntu 24.04 with Python 3.14 and Meson apt package.
- Key behavior: installs `asciidoc` and `sphinx`, runs `scripts/build.sh html_docs`, copies generated HTML from `.build-ci/Documentation`, and renames `nvme.html` to `index.html`.
- Output: disables extra formats with `formats: []`.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/.readthedocs.yaml -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/Documentation/asciidoc.conf -->
# File Research: sources/virtualization/nvme-cli/Documentation/asciidoc.conf

- Purpose: AsciiDoc configuration for nvme-cli documentation.
- Key behavior: defines the `linknvme:command[section]` macro for DocBook and XHTML output.
- Manpage integration: custom DocBook header emits `NVMe` source, `{nvme_version}`, and `NVMe Manual` metadata.
- Compatibility: includes workarounds for older docbook-xsl/listing and verse block handling.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/Documentation/asciidoc.conf -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/Documentation/asciidoctor-extensions.rb -->
# File Research: sources/virtualization/nvme-cli/Documentation/asciidoctor-extensions.rb

- Purpose: Asciidoctor Ruby extension for `linknvme`.
- Key behavior: registers an inline macro processor that renders links differently for HTML, manpage, and DocBook backends.
- HTML output: emits `<a href="target.html">target(section)</a>`.
- DocBook output: emits `citerefentry/refentrytitle/manvolnum`.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/Documentation/asciidoctor-extensions.rb -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/Documentation/install-webdoc.sh -->
# File Research: sources/virtualization/nvme-cli/Documentation/install-webdoc.sh

- Purpose: shell installer/synchronizer for generated web documentation.
- Key behavior: copies changed `.txt`, `.html`, and `.css` documentation into target directory while ignoring `Last updated` differences via `$DIFF`.
- Cleanup: removes stale generated docs from target except release notes and `index.html`.
- Final step: symlinks `git.html` to target `index.html`.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/Documentation/install-webdoc.sh -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/Documentation/meson.build -->
# File Research: sources/virtualization/nvme-cli/Documentation/meson.build

- Purpose: Meson documentation build/install definition.
- Main content: declares the large `adoc_sources` list of nvme command manpage/documentation stems, including core NVMe, fabrics, ZNS, SED, and vendor plugin commands.
- Includes: copies shared include fragments such as `cmd-plugins.txt`, `cmds-main.txt`, `global-options.txt`, and `fabrics-options.txt`.
- Build behavior: when docs are enabled and `asciidoc`/`xmlto` are available, generates DocBook, man pages, and XHTML via `custom_target`.
- Fallback behavior: if docs build tools are absent, installs precompiled `.1` and `.html` files.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/Documentation/meson.build -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/Makefile -->
# File Research: sources/virtualization/nvme-cli/Makefile

- Purpose: convenience wrapper around Meson for common developer/package tasks.
- Targets: build, clean/purge, install/uninstall, update-accessors, dist, test, test-strict, rpm, debug, static, checkpatch, and checkpatch-diff.
- Build behavior: creates `.build` with `meson setup`; `PLUGINS` maps to `-Dplugins=`.
- Static target: configures release static build with fallback wraps and disables keyutils, liburing, Python, OpenSSL, tests, and examples.
- Checkpatch: downloads kernel `checkpatch.pl` to `/tmp/checkpatch.pl` and checks either commit range or local diff/untracked files.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/ccan/ccan/array_size/array_size.h -->
# File Research: sources/virtualization/nvme-cli/ccan/ccan/array_size/array_size.h

- Purpose: CCAN macro for compile-time-safe visible array length.
- Key API: `ARRAY_SIZE(arr)`.
- Safety: with `typeof` and `__builtin_types_compatible_p`, rejects pointer arguments by comparing array type to `&arr[0]` pointer type.
- Dependency: uses `BUILD_ASSERT_OR_ZERO`.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/ccan/ccan/array_size/array_size.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/ccan/ccan/build_assert/build_assert.h -->
# File Research: sources/virtualization/nvme-cli/ccan/ccan/build_assert/build_assert.h

- Purpose: compile-time assertion helpers.
- Key APIs: `BUILD_ASSERT(cond)` for statement context and `BUILD_ASSERT_OR_ZERO(cond)` for expression context.
- Mechanism: uses invalid char array size to force compile failure when condition is false.
- Use: foundational helper for CCAN type/size checking macros.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/ccan/ccan/build_assert/build_assert.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/ccan/ccan/check_type/check_type.h -->
# File Research: sources/virtualization/nvme-cli/ccan/ccan/check_type/check_type.h

- Purpose: macro-level type checking for C APIs.
- Key APIs: `check_type(expr, type)` and `check_types_match(expr1, expr2)`.
- Fast path: uses `typeof` pointer comparison to produce warnings/errors without evaluating expressions.
- Fallback: checks only `sizeof` equality when `typeof` is unavailable.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/ccan/ccan/check_type/check_type.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/ccan/ccan/compiler/compiler.h -->
# File Research: sources/virtualization/nvme-cli/ccan/ccan/compiler/compiler.h

- Purpose: portability layer for compiler attributes and builtins.
- Defines: `COLD`, `NORETURN`, `PRINTF_FMT`, `CONST_FUNCTION`, `PURE_FUNCTION`, `UNNEEDED`, `NEEDED`, `UNUSED`, `WARN_UNUSED_RESULT`, `WARN_DEPRECATED`, `NO_NULL_ARGS`, `NON_NULL_ARGS`, `RETURNS_NONNULL`, `LAST_ARG_NULL`, and `cpu_supports`.
- Feature gates: all macros depend on `HAVE_ATTRIBUTE_*`, `HAVE_BUILTIN_*`, and related config symbols.
- Research value: centralizes optional compiler diagnostics/optimization annotations used by other CCAN modules.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/ccan/ccan/compiler/compiler.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/ccan/ccan/container_of/container_of.h -->
# File Research: sources/virtualization/nvme-cli/ccan/ccan/container_of/container_of.h

- Purpose: Linux-style enclosing-structure helpers.
- Key APIs: `container_of`, `container_of_or_null`, `container_off`, `container_of_var`, and `container_off_var`.
- Type safety: uses `check_types_match` when possible.
- Use: supports intrusive data structures such as CCAN list wrappers.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/ccan/ccan/container_of/container_of.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/ccan/ccan/endian/endian.h -->
# File Research: sources/virtualization/nvme-cli/ccan/ccan/endian/endian.h

- Purpose: endian-aware integer typedefs and conversion helpers.
- Key APIs: constant byte-swap macros, runtime `bswap_*` fallbacks, `CPU_TO_LE*`, `LE*_TO_CPU`, `CPU_TO_BE*`, `BE*_TO_CPU`, and inline `cpu_to_*`/`*_to_cpu` functions.
- Types: defines `leint16_t`, `leint32_t`, `leint64_t`, `beint16_t`, `beint32_t`, and `beint64_t`; integrates with `short_types.h` for `le16/be16` aliases.
- Safety: errors out if target endian is unknown or both big/little are selected.
- Sparse support: uses bitwise/force attributes under `__CHECKER__`.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/ccan/ccan/endian/endian.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/ccan/ccan/hash/hash.c -->
# File Research: sources/virtualization/nvme-cli/ccan/ccan/hash/hash.c

- Purpose: Bob Jenkins lookup3-derived hash implementation for CCAN.
- Key implementations: `hash_u32`, endian-selecting byte hash via `hashlittle`/`hashbig`, stable 64/32/16/8-bit element hashing, `hash_any`, and `hash64_any`.
- Endian behavior: internal hashes may differ by machine; stable hashes process integer elements to preserve cross-endian results.
- Collision domain: intended for hash table lookup, explicitly not cryptographic.
- Notes: disabled `SELF_TEST` block contains upstream test code with older function names; normal nvme-cli build compiles the production functions.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/ccan/ccan/hash/hash.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/ccan/ccan/hash/hash.h -->
# File Research: sources/virtualization/nvme-cli/ccan/ccan/hash/hash.h

- Purpose: public hash API and convenience macros.
- Key APIs: `hash`, `hash_stable`, `hash_u32`, `hash_string`, `hash64`, `hash64_stable`, `hashl`, `hash_pointer`, and underlying function declarations.
- Type policy: stable hash macros assert element sizes of 1, 2, 4, or 8 bytes.
- Pointer hashing: safely aliases pointer representation through a union when possible.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/ccan/ccan/hash/hash.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/ccan/ccan/htable/htable.c -->
# File Research: sources/virtualization/nvme-cli/ccan/ccan/htable/htable.c

- Purpose: open-addressed pointer hash table implementation.
- Key behavior: stores metadata in common pointer bits, uses `(void *)1` as deleted marker, tracks deleted slots, and grows/rehashes when table is too full.
- APIs implemented: init, sized init, clear, copy, add, delete, iterator traversal, random pick, custom allocator, and consistency check.
- Invariants: elements must be non-NULL and not `(void *)1`; caller supplies hashes and a rehash callback.
- Debugging: `htable_check` validates that every element can find itself via its rehash.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/ccan/ccan/htable/htable.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/ccan/ccan/htable/htable.h -->
# File Research: sources/virtualization/nvme-cli/ccan/ccan/htable/htable.h

- Purpose: public raw pointer hash table interface.
- Key structs: `struct htable` and `struct htable_iter`.
- Key APIs: `HTABLE_INITIALIZER`, `htable_init`, `htable_init_sized`, `htable_count`, `htable_clear`, `htable_check`, `htable_copy`, `htable_add`, `htable_del`, `htable_firstval`, `htable_nextval`, `htable_get`, `htable_first`, `htable_next`, `htable_prev`, `htable_delval`, `htable_pick`, and `htable_set_allocator`.
- Debug mode: `CCAN_HTABLE_DEBUG` wraps calls with `htable_check`.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/ccan/ccan/htable/htable.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/ccan/ccan/htable/htable_type.h -->
# File Research: sources/virtualization/nvme-cli/ccan/ccan/htable/htable_type.h

- Purpose: macro generator for type-safe hash table wrappers.
- Key macro: `HTABLE_DEFINE_TYPE(type, keyof, hashfn, eqfn, name)`.
- Generated API: typed init, sized init, count, clear, copy, add, delete, delete by key, get, getfirst/getnext, delval, pick, first/next/prev.
- Type handling: `HTABLE_KTYPE` uses `typeof(keyof((const type *)NULL))` when available.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/ccan/ccan/htable/htable_type.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/ccan/ccan/ilog/ilog.c -->
# File Research: sources/virtualization/nvme-cli/ccan/ccan/ilog/ilog.c

- Purpose: callable implementations of integer binary logarithm functions.
- Key APIs implemented: `ilog32`, `ilog32_nz`, `ilog64`, and `ilog64_nz`.
- Algorithms: uses de Bruijn sequence fallback by default, with branch-based fallback when `ILOG_NODEBRUIJN` is defined.
- Note: compiled even when header macros use compiler builtins, so address-taking still works.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/ccan/ccan/ilog/ilog.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/ccan/ccan/ilog/ilog.h -->
# File Research: sources/virtualization/nvme-cli/ccan/ccan/ilog/ilog.h

- Purpose: integer binary logarithm API and compile-time helpers.
- Key APIs: `ilog32`, `ilog32_nz`, `ilog64`, `ilog64_nz`, `STATIC_ILOG_32`, and `STATIC_ILOG_64`.
- Compiler optimization: maps to `__builtin_clz`, `__builtin_clzl`, or `__builtin_clzll` when available.
- Constant handling: uses nested macros `STATIC_ILOG0` through `STATIC_ILOG6` for compile-time values.
- Notable quirk: in the `builtin_ilog64_nz` block, the header redefines `ilog32(_v)` instead of `ilog64(_v)`, which is worth reviewing if editing this file.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/ccan/ccan/ilog/ilog.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/ccan/ccan/likely/likely.c -->
# File Research: sources/virtualization/nvme-cli/ccan/ccan/likely/likely.c

- Purpose: debug-mode runtime tracing for `likely()` and `unlikely()`.
- Build condition: only active under `CCAN_LIKELY_DEBUG`.
- Key behavior: records branch condition, file, line, expectation, hit count, and correct count in a typed hash table.
- APIs implemented: `_likely_trace`, `likely_stats`, and `likely_stats_reset`.
- Dependency: uses CCAN hash and htable typed wrappers.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/ccan/ccan/likely/likely.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/ccan/ccan/likely/likely.h -->
# File Research: sources/virtualization/nvme-cli/ccan/ccan/likely/likely.h

- Purpose: branch prediction macros.
- Normal mode: maps `likely(cond)` and `unlikely(cond)` to `__builtin_expect` when available, otherwise boolean normalization.
- Debug mode: redirects macros through `_likely_trace` with stringified condition, source file, and line.
- Extra debug APIs: `likely_stats` reports worst prediction sites; `likely_stats_reset` frees trace memory.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/ccan/ccan/likely/likely.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/ccan/ccan/list/list.c -->
# File Research: sources/virtualization/nvme-cli/ccan/ccan/list/list.c

- Purpose: runtime consistency checks for CCAN intrusive lists.
- Key APIs: `list_check_node` and `list_check`.
- Behavior: traverses forward links and validates each node’s `prev`; reports corruption to stderr and aborts when an abort string is provided.
- Used by: `list.h` debug wrappers under `CCAN_LIST_DEBUG`.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/ccan/ccan/list/list.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/ccan/ccan/list/list.h -->
# File Research: sources/virtualization/nvme-cli/ccan/ccan/list/list.h

- Purpose: intrusive doubly linked list implementation.
- Key structs: `struct list_node` and `struct list_head`.
- Key APIs: initialization, add before/after/head/tail, delete, delete-init, delete-from, swap, top/pop/tail, forward/reverse iteration, safe iteration, next/prev, append/prepend whole lists, and offset-based low-level iteration.
- Type safety: uses `container_of`, `check_type`, and offset helpers.
- Debug mode: `CCAN_LIST_DEBUG` enables structural checks and use-after-delete nulling.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/ccan/ccan/list/list.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/ccan/ccan/minmax/minmax.h -->
# File Research: sources/virtualization/nvme-cli/ccan/ccan/minmax/minmax.h

- Purpose: type-checked min/max/clamp macros.
- Key APIs: `min`, `max`, `clamp`, `min_t`, `max_t`, and `clamp_t`.
- Requirements: hard errors unless statement expressions and `typeof` are available.
- Safety: stores arguments in temporaries to avoid double evaluation and checks type compatibility when supported.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/ccan/ccan/minmax/minmax.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/ccan/ccan/short_types/short_types.h -->
# File Research: sources/virtualization/nvme-cli/ccan/ccan/short_types/short_types.h

- Purpose: short aliases for fixed-width integer types.
- Aliases: `u64/s64/u32/s32/u16/s16/u8/s8`.
- Endian integration: if `endian.h` is already included, also aliases `be64/be32/be16` and `le64/le32/le16`.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/ccan/ccan/short_types/short_types.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/ccan/ccan/str/debug.c -->
# File Research: sources/virtualization/nvme-cli/ccan/ccan/str/debug.c

- Purpose: debug wrappers for ctype and string functions.
- Build condition: only active under `CCAN_STR_DEBUG`.
- Key behavior: asserts ctype inputs are in `[-1, 255)` before calling libc ctype functions.
- Const handling: provides out-of-line wrappers for `strstr`, `strchr`, and `strrchr` used by debug macros.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/ccan/ccan/str/debug.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/ccan/ccan/str/str.c -->
# File Research: sources/virtualization/nvme-cli/ccan/ccan/str/str.c

- Purpose: implementation file for CCAN string helpers.
- Key API: `strcount`.
- Behavior: counts non-overlapping occurrences of `needle` in `haystack` using `strstr` and advances by needle length.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/ccan/ccan/str/str.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/ccan/ccan/str/str.h -->
# File Research: sources/virtualization/nvme-cli/ccan/ccan/str/str.h

- Purpose: string utility macros and safer character helpers.
- Key APIs: `streq`, `strstarts`, `strends`, `stringify`, `strcount`, `STR_MAX_CHARS`, and `cis*` wrappers around ctype.
- Debug mode: under `CCAN_STR_DEBUG`, replaces libc ctype macros with checked wrappers and makes `strstr/strchr/strrchr` const-preserving with GNU `typeof`.
- Safety: `cis*` wrappers cast through `unsigned char`, avoiding common signed-char ctype misuse.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/ccan/ccan/str/str.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/ccan/ccan/str/str_debug.h -->
# File Research: sources/virtualization/nvme-cli/ccan/ccan/str/str_debug.h

- Purpose: declarations for CCAN string debug wrappers.
- Build condition: declarations are exposed only under `CCAN_STR_DEBUG`.
- Declares: checked ctype wrappers and string wrappers used by `str.h` macro substitutions.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/ccan/ccan/str/str_debug.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/ccan/ccan/strset/strset.c -->
# File Research: sources/virtualization/nvme-cli/ccan/ccan/strset/strset.c

- Purpose: crit-bit string set implementation.
- Key APIs implemented: `strset_get`, `strset_add`, `strset_del`, `strset_iterate_`, `strset_prefix`, and `strset_clear`.
- Storage policy: stores caller-provided string pointers; it does not duplicate strings.
- Special cases: uses a special empty-string node because strings and internal nodes are distinguished by leading zero byte.
- Error policy: sets `errno` to `ENOENT`, `EEXIST`, or `ENOMEM` for common failure cases.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/ccan/ccan/strset/strset.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/ccan/ccan/strset/strset.h -->
# File Research: sources/virtualization/nvme-cli/ccan/ccan/strset/strset.h

- Purpose: public API for the crit-bit string set.
- Key struct: `struct strset`, exposing a union of node pointer or string pointer for embedding/inlining.
- Key APIs: `strset_init`, `strset_empty`, `strset_get`, `strset_add`, `strset_del`, `strset_clear`, `strset_iterate`, `strset_iterate_`, and `strset_prefix`.
- Type safety: `strset_iterate` uses `typesafe_cb_preargs` to validate callback argument type.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/ccan/ccan/strset/strset.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/ccan/ccan/typesafe_cb/typesafe_cb.h -->
# File Research: sources/virtualization/nvme-cli/ccan/ccan/typesafe_cb/typesafe_cb.h

- Purpose: compile-time-assisted callback casting macros.
- Key APIs: `typesafe_cb_cast`, `typesafe_cb_cast3`, `typesafe_cb`, `typesafe_cb_preargs`, and `typesafe_cb_postargs`.
- Mechanism: when supported, uses `typeof`, `__builtin_choose_expr`, and `__builtin_types_compatible_p` to cast only matching callback types.
- Fallback: unconditional casts when compiler support is unavailable.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/ccan/ccan/typesafe_cb/typesafe_cb.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/ccan/meson.build -->
# File Research: sources/virtualization/nvme-cli/ccan/meson.build

- Purpose: Meson build definition for bundled CCAN static library.
- Sources: includes hash, htable, ilog, likely, list, str debug/string, and strset C files.
- Debug behavior: debug build type adds `-DCCAN_LIST_DEBUG=1` and `-DCCAN_STR_DEBUG=1`.
- Output: builds non-installed static library `ccan` and exposes `ccan_dep` with include directory and `config_dep`.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/ccan/meson.build -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/cmd.h -->
# File Research: sources/virtualization/nvme-cli/cmd.h

- Purpose: neutralizes plugin/command list macros before including command definition files.
- Key behavior: undefines and replaces `PLUGIN(n, c)` and variadic `COMMAND_LIST(args...)` with empty definitions.
- Research note: likely used as a preprocessing include to avoid emitting declarations/definitions for a specific include pass.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/cmd.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/cmd_handler.h -->
# File Research: sources/virtualization/nvme-cli/cmd_handler.h

- Purpose: multi-pass macro expansion framework for nvme-cli command plugins.
- Stage 1: emits static function prototypes for each `ENTRY`.
- Stage 2: emits `struct command` instances, supporting optional aliases through `ENTRY_W_ALIAS`/`ENTRY_WO_ALIAS`.
- Stage 3: builds a `commands[]` array of command pointers.
- Stage 4: constructs a `struct plugin` and registers it from a constructor function via `register_extension(&plugin)`.
- Dependency: repeatedly includes `CMD_INCLUDE(CMD_INC_FILE)` with different macro definitions.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/cmd_handler.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/codecov.yml -->
# File Research: sources/virtualization/nvme-cli/codecov.yml

- Purpose: Codecov repository configuration.
- Ignore list: excludes `subprojects`, `ccan`, `tests`, `unit`, `libnvme/test`, `libnvme/libnvme/tests`, and `libnvme/examples`.
- Policy: disables both project and patch coverage status checks.
- Research note: Codecov is used for reporting rather than gating.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/codecov.yml -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/common.h -->
# File Research: sources/virtualization/nvme-cli/common.h

- Purpose: shared portability and MMIO helper header.
- General helpers: defines `ARRAY_SIZE`, simple `min/max`, `__packed`, and Windows wrappers for `mkdir`, `fsync`, and `getpagesize`.
- Endian dependency: includes CCAN endian helpers and uses `leint32_t/leint64_t`.
- MMIO behavior: provides raw read/write helpers; on AArch64 uses inline assembly `ldr/str` with `Qo` constraints to avoid MMIO instructions that hypervisors may not decode.
- Register access: `mmio_read64` reads two 32-bit little-endian halves because some devices fail 64-bit MMIO; `mmio_write64` can either write two 32-bit halves or one 64-bit little-endian value depending on `write32`.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/common.h -->