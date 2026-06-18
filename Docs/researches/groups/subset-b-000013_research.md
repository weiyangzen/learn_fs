# Research: subset-b-000013

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/dockerfile_heredoc_test.go -->
# sources/cloud-native/buildkit/frontend/dockerfile/dockerfile_heredoc_test.go

## Purpose
This Go integration-test file validates Dockerfile heredoc support in BuildKit's Dockerfile frontend. It registers `hdTests` into the broader `heredocTests` matrix and covers heredocs used by `COPY`, `RUN`, shebang scripts, shell redirections, tab-stripping (`<<-EOF`), ARG interpolation, quoted delimiters, and `ONBUILD` triggers. The tests are platform-aware: Linux paths exercise BusyBox shell semantics and POSIX metadata, while Windows paths use `nanoserver`, `cmd`, CRLF/UTF-16LE expectations, and skip Unix-only shell features.

## Important APIs, Types, and Functions
The file relies on `integration.TestFuncs`, `integration.UnixOrWindows`, `integration.SkipOnPlatform`, `workers.CheckFeatureCompat`, `client.New`, `f.Solve`, `client.SolveOpt`, local exporter entries, `dockerui.DefaultLocalNameDockerfile`, `dockerui.DefaultLocalNameContext`, `fstest.CreateFile`, `integration.Tmpdir`, and `fsutil.FS` local mounts. The core test functions are `testCopyHeredoc`, `testCopyHeredocSpecialSymbols`, `testRunBasicHeredoc`, `testRunFakeHeredoc`, `testRunShebangHeredoc`, `testRunComplexHeredoc`, `testHeredocIndent`, `testHeredocVarSubstitution`, and `testOnBuildHeredoc`.

## Control Flow and Assertions
Most tests build an inline Dockerfile in a temp directory, solve it through the selected frontend, export to a temp local directory, and assert exact file bytes. `testCopyHeredoc` checks inline file creation, multiple heredocs in one instruction, chmod/chown behavior, and stat output. `testCopyHeredocSpecialSymbols` distinguishes unquoted delimiters from quoted raw delimiters for quotes, backslashes, and dollar signs. RUN heredoc tests verify default shell execution, custom `SHELL`, shebang interpretation, pipes, multi-fd heredocs, indentation rules, and ARG expansion versus literal preservation. `testOnBuildHeredoc` pushes a base image with an ONBUILD heredoc trigger to a sandbox registry, then builds a child image from it and checks the trigger output.

## State, Persistence, and Dependencies
State is transient except for pushed test images in the sandbox registry and exported local files used for assertions. Build context and Dockerfile data are in temp directories. Dependencies include BuildKit client/frontend abstractions, containerd continuity `fstest`, filesystem reads, runtime platform checks, and direct-push feature gating.

## Integration Points
The file exercises Dockerfile parser heredoc tokenization, variable interpolation, frontend-to-LLB conversion, local and image exporters, ONBUILD trigger execution, platform-specific shell dispatch, and registry push/pull behavior. It integrates with the shared frontend matrix through `getFrontend`.

## Risks and Test Signals
High-value risks are delimiter quoting regressions, newline/indent preservation changes, Windows shell byte differences, heredocs accidentally interpreted by the wrong shell, and ONBUILD heredocs not surviving image export/import. Strong signals are exact exported byte comparisons, permission/stat checks, and feature-gated registry coverage. Some Linux shell paths are skipped on Windows by design.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/dockerfile_heredoc_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/dockerfile_lint_test.go -->
# sources/cloud-native/buildkit/frontend/dockerfile/dockerfile_lint_test.go

## Purpose
This file is the central integration suite for Dockerfile linter behavior. It validates warning generation, warning metadata, skip/error control through `#check` directives and `BUILDKIT_DOCKERFILE_CHECK`, progress-stream warnings, and JSON output from the `frontend.lint` subrequest. It covers rule families for casing, stage names, ignored files, secret-looking ARG/ENV names, undefined variables, malformed defaults in `FROM`, platform flags, duplicate instructions, legacy key/value syntax, EXPOSE formatting, and definition-description comments.

## Important APIs, Types, and Functions
The suite registers `lintTests` with `integration.TestFuncs`. Main test functions include `testDefinitionDescription`, `testCopyIgnoredFiles`, `testSecretsUsedInArgOrEnv`, `testAllTargetUnmarshal`, `testRuleCheckOption`, `testStageName`, `testNoEmptyContinuation`, `testConsistentInstructionCasing`, `testDuplicateStageName`, `testReservedStageName`, `testJSONArgsRecommended`, `testMaintainerDeprecated`, `testWarningsBeforeError`, `testUndeclaredArg`, `testWorkdirRelativePath`, `testUnmatchedVars`, `testMultipleInstructionsDisallowed`, `testLegacyKeyValueFormat`, `testRedundantTargetPlatform`, `testInvalidDefaultArgInFrom`, `testFromPlatformFlagConstDisallowed`, `testExposeProtoCasing`, and `testExposeInvalidFormat`. Shared helpers are `checkLinterWarnings`, `checkProgressStream`, `checkUnmarshal`, `checkVertexWarning`, `checkLintWarning`, and `unmarshalLintResults`. Data carriers are `expectedLintWarning` and `lintTestParams`.

## Control Flow and Assertions
Each rule-specific test builds a Dockerfile fixture and expected warning list, then calls `checkLinterWarnings`. That helper normalizes warning order, creates temp Dockerfile and optional `.dockerignore`, opens a BuildKit client, and runs two subtests: `warntype=progress`, which solves the Dockerfile and collects `client.VertexWarning` values from the status stream, and `warntype=unmarshal`, which invokes gateway subrequest `frontend.lint` and unmarshals `result.json` into `lint.LintResults`. Expected rule names, descriptions, URLs, detail text, levels, lines, and build-error locations are compared precisely.

## State, Persistence, and Dependencies
The file persists only temporary test inputs. State is carried through `lintTestParams`: client reuse, temp dir, Dockerfile bytes, dockerignore bytes, expected warnings, optional unmarshal-only warnings, expected build errors, and frontend attrs. Dependencies include Go `maps`, `slices`, `cmp`, sorting, regexes, BuildKit linter formatting, gateway subrequests, and platform-aware base image names.

## Integration Points
This file bridges Dockerfile parsing, linter rule implementations, frontend solve status output, gateway subrequest output, `.dockerignore` evaluation, frontend attrs, build-arg check controls, and multi-platform solve defaults. It ensures warnings are not just emitted internally but also transported through the two public observation channels.

## Risks and Test Signals
Risks include mismatched warning line numbers, divergent progress versus subrequest outputs, incorrect skip/error precedence, overzealous secret-name detection, wrong suggestions for similar variable names, ignored-file warnings conflicting with real build failures, and unreachable-target warnings being lost during lint unmarshalling. The strongest signals are duplicate validation through both progress and JSON paths, exact metadata checks, and targeted negative fixtures with no warnings.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/dockerfile_lint_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/dockerfile_mount_test.go -->
# sources/cloud-native/buildkit/frontend/dockerfile/dockerfile_mount_test.go

## Purpose
This file validates Dockerfile `RUN --mount` behavior across bind/context mounts, tmpfs mounts, cache mounts, writable stage mounts, parser typo suggestions, variable interpolation, mount IDs, user/mode settings, duplicate context mounts, and nested cache mount parallelism. It registers `mountTests` into the global `allTests` matrix.

## Important APIs, Types, and Functions
The major tests are `testMountContext`, `testMountTmpfs`, `testMountInvalid`, `testMountRWCache`, `testCacheMountUser`, `testCacheMountDefaultID`, `testMountEnvVar`, `testMountArg`, `testMountEnvAcrossStages`, `testMountMetaArg`, `testMountFromError`, `testMountTmpfsSize`, `testMountDuplicate`, and `testCacheMountParallel`. They use `getFrontend`, `client.New`, `f.Solve`, local mounts, local exporter outputs, `integration.UnixOrWindows`, `integration.SkipOnPlatform`, and `fstest` fixtures.

## Control Flow and Assertions
Positive tests build small Dockerfiles and assert successful solves or exported file content. `testMountContext` reads a context file through a default mount. `testMountTmpfs` confirms tmpfs contents do not persist between RUN instructions. `testMountRWCache` solves twice with a changed cachebust file and expects identical output from a cached writable mount. Cache ID tests prove default IDs isolate by target and explicit IDs share across targets/stages. Variable tests verify `ENV`, `ARG`, and global meta-ARG expansion in mount attributes. Negative tests check typo diagnostics (`--mont`, `typ`, `tmp`) and reject variable expansion in `from=`.

## State, Persistence, and Dependencies
Cache mounts intentionally persist between RUN instructions and solves according to BuildKit cache semantics; tmpfs and secret-like temporary mounts must not persist. Most other state is temp-directory Dockerfile/context data and optional local exporter output. Dependencies include shell commands inside Linux/Windows base images and BuildKit cache/mount implementations.

## Integration Points
The tests cover parser flag handling, frontend mount option conversion, solver cache keys, local context mounting, stage-to-stage mounts, cache sharing across stages, environment interpolation in mount specs, and exporter output validation. `testCacheMountParallel` loops 20 no-cache solves to catch race conditions in nested cache mount setup.

## Risks and Test Signals
Key risks are stale cache reuse, mount option typo suggestions breaking, unsupported variable expansion becoming ambiguous, tmpfs persistence leaks, duplicate context source mounts failing to refresh after context changes, and parallel nested cache mounts deadlocking or colliding. Test signals include exact error substrings, repeated solve comparisons, stat checks, file existence checks, and stress-looped parallel solves.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/dockerfile_mount_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/dockerfile_outline_test.go -->
# sources/cloud-native/buildkit/frontend/dockerfile/dockerfile_outline_test.go

## Purpose
This file tests the Dockerfile frontend's `frontend.outline` subrequest. Outline metadata describes a selected target, its source Dockerfile, ARGs with computed values and descriptions, secrets, SSH mounts, and request availability through `subrequests.Describe`. It is intentionally limited to the client frontend when required.

## Important APIs, Types, and Functions
Registered tests are `testOutlineArgs`, `testOutlineSecrets`, `testOutlineRecursiveArgs`, and `testOutlineDescribeDefinition`; `unmarshalOutline` decodes `result.json` into `outline.Outline`. The suite uses `workers.CheckFeatureCompat(workers.FeatureFrontendOutline)`, `client.Build`, gateway `c.Solve`, `FrontendOpt` values `frontend.caps`, `requestid=frontend.outline`, build args, target selection, `subrequests.Describe`, and `outline` model types.

## Control Flow and Assertions
The tests construct Dockerfiles with commented ARGs and stages, invoke a gateway callback through `client.Build`, and inside the callback solve `dockerfile.v0` with the outline request. `testOutlineArgs` verifies target name/description extraction, source preservation, inherited/global ARGs, target-local ARGs, build-arg overrides, skipped secret-looking ARG descriptions, and exact source line locations. `testOutlineSecrets` checks only reachable target dependencies are represented, with computed secret IDs and required flags plus SSH IDs. `testOutlineRecursiveArgs` verifies recursive ARG expansion and deduped output values. `testOutlineDescribeDefinition` confirms `frontend.outline` appears as an RPC subrequest with a version.

## State, Persistence, and Dependencies
State is transient: Dockerfile bytes are kept in temp local mounts and decoded outline metadata is held in memory. Dependencies include frontend subrequest capability support, source-location tracking, comment parsing, ARG expansion, and platform-specific Dockerfile variants.

## Integration Points
The file integrates Dockerfile parsing with frontend subrequest RPCs, target graph reachability, secrets/SSH mount analysis, build-arg substitution, source attachment, and source location serialization. It verifies the metadata contract without exporting images.

## Risks and Test Signals
Risks include outline leaking unreachable stages, losing source bytes, reporting wrong lines after parser changes, mishandling recursive ARGs, including skipped secret-like ARG descriptions incorrectly, and subrequest discovery drifting. Signals are exact equality on names, values, descriptions, source bytes, required flags, and line numbers.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/dockerfile_outline_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/dockerfile_parents_test.go -->
# sources/cloud-native/buildkit/frontend/dockerfile/dockerfile_parents_test.go

## Purpose
This file validates `COPY --parents` behavior in Dockerfile builds. It covers preserving parent paths from local context and from previous stages, pivot markers with `./`, wildcard expansion, multiple inputs, and missing-source behavior. It is registered as `parentsTests` in `allTests`.

## Important APIs, Types, and Functions
The core tests are `testCopyParents`, `testCopyRelativeParents`, and `testCopyParentsMissingDirectory`. They use local export validation, `FrontendAttrs{"target": ...}` to solve multiple stages from a single Dockerfile, `integration.UnixOrWindows` for Linux/Windows fixtures, `fstest` context construction, `client.New`, and `f.Solve`.

## Control Flow and Assertions
`testCopyParents` exports a scratch result and reads files from the output directory, proving direct and globbed local `COPY --parents` preserve expected `foo1/foo2` paths under root and `WORKDIR /test`. `testCopyRelativeParents` builds a source tree in a base stage, then solves targets named `middle`, `end`, `start`, `double`, `wildcard`, `doublewildcard`, and `doubleinputs`; each target asserts whether path prefixes before/after pivot markers are preserved. `testCopyParentsMissingDirectory` solves positive targets plus negative and wildcard-nonexistent cases, checking an exact missing file regex only for a literal nonexistent file while wildcard misses produce empty output directories.

## State, Persistence, and Dependencies
All filesystem state is produced in temporary build stages or local contexts. The tests depend on Dockerfile frontend path normalization, wildcard matching, stage filesystem snapshots, and platform-specific shell commands for assertions.

## Integration Points
The file exercises the parser and copier logic for `--parents`, local context transfer, stage-to-stage copy, target-specific solves, wildcard resolution, platform path separators, and local exporter validation.

## Risks and Test Signals
Risks include incorrect pivot trimming, accidental inclusion of too much path prefix, wildcard misses becoming hard errors, literal missing files not erroring, Windows path behavior diverging from Linux, or multi-input globs collapsing incorrectly. Test signals are per-target solve results, exported byte checks, in-build file/directory assertions, and a regex for the expected checksum/missing-path error.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/dockerfile_parents_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/dockerfile_provenance_test.go -->
# sources/cloud-native/buildkit/frontend/dockerfile/dockerfile_provenance_test.go

## Purpose
This large integration suite validates BuildKit Dockerfile provenance and attestation behavior. It covers SLSA v1 and v0.2 predicate shapes, min/max/full provenance modes, direct image push attestations, git contexts with SHA-1 and SHA-256 repositories, multi-platform builds, client and gateway frontend differences, LLB and Dockerfile inputs, nested input request provenance, secrets and SSH metadata, OCI layout base images, nil/local/tar exporters, duplicate platform and duplicate layer regressions, `.dockerignore` disappearance, source mapping, source deduplication, and local exporter provenance files.

## Important APIs, Types, and Functions
The suite registers `provenanceTests` into `allTests`. Major tests include `testProvenanceAttestation`, `testGitProvenanceAttestationSHA1`, `testGitProvenanceAttestationSHA256`, `testMultiPlatformProvenance`, `testClientFrontendProvenance`, `testGatewayBuiltinSyntaxSourceProvenance`, `testClientLLBProvenance`, `testGatewayProvenanceRootRequest`, input-producer tests, `testSecretSSHProvenance`, `testOCILayoutProvenance`, `testNilProvenance`, `testDuplicatePlatformProvenance`, `testDockerIgnoreMissingProvenance`, `testCommandSourceMapping`, `testFrontendDeduplicateSources`, `testDuplicateLayersProvenance`, and local export tests. Helpers include `daemonDockerfileVersion`, `provenanceInputDockerfile`, `solveProvenanceInputProducer`, `solveProvenanceNamedTarget`, `solveProvenanceInputProducerWithInner`, `solveProvenanceInputConsumer`, `assertProvenanceInputRequest`, `assertMinProvenanceInputRequest`, `assertFrontendRequest`, and `readNativeProvenancePredicate`.

## Control Flow and Assertions
Most tests build Dockerfiles through `f.Solve` or `client.Build`, push images to a sandbox registry, reload image indexes with `contentutil.ProviderFromRef` and `testutil.ReadImages`, find image and attestation manifests, unmarshal in-toto statements, and assert predicate fields. The code distinguishes builtin, gateway, and client frontends: client frontend solves often omit frontend request details, gateway adds source/buildkit test material, and builtin dockerfile records `dockerfile.v0` plus daemon Dockerfile version. Git tests create real repositories, serve them over HTTP with masked credentials, and assert resolved dependency URIs and digest formats. Input-producer tests marshal frontend result refs to LLB states plus `containerimage.config` metadata, then consume them through named `input:` contexts and assert request nesting.

## State, Persistence, and Dependencies
Persistent test state includes temporary git repositories, HTTP test servers, local OCI stores, pushed registry images, BuildKit build-history records, local exporter directories, and in-memory content stores. Provenance custom environment config is supplied by `provenanceEnvSimple`, which writes JSON files and injects `provenanceEnvDir` into integration config. Dependencies include containerd content APIs, OCI descriptors, in-toto/SLSA types, BuildKit control/history APIs, LLB builders, gateway frontend APIs, platform normalization, registry support, and feature gates for direct push, provenance, and multi-platform builds.

## Integration Points
The file is a cross-cutting integration point for the Dockerfile frontend, gateway frontend, client frontend callbacks, solver provenance capture, exporter attestation attachment, registry/image loading, source maps, source/layer deduplication, secret/SSH declaration capture, OCI layout material resolution, git source material tracking, and local exporter provenance writing. It also validates provenance behavior for both image and non-image exporters.

## Risks and Test Signals
Risks are high because provenance is an external supply-chain contract. Possible regressions include credential leakage, missing Dockerfile versions, wrong SLSA predicate type, incomplete request/material completeness flags, lost local source bytes in max mode, incorrect per-platform materials, duplicate layers/sources, lost nested input request metadata, nil provenance panics for local/tar exporters, and local exporter file naming drift. Strong signals include exact predicate field assertions, masked URL checks, digest presence and algorithm checks, platform-specific attestation lookup, exported output validation, build-history attestation reads, and regression tests tied to known issues.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/dockerfile_provenance_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/dockerfile_rundevice_test.go -->
# sources/cloud-native/buildkit/frontend/dockerfile/dockerfile_rundevice_test.go

## Purpose
This build-tagged file (`//go:build dfrundevice`) tests experimental Dockerfile `RUN --device` support with CDI device specs. It verifies that a CDI device selected in a Dockerfile RUN instruction can inject environment variables into the build container.

## Important APIs, Types, and Functions
The file registers only `testDeviceRunEnv` into `allTests`. It uses `sb.CDISpecDir()` to write a CDI YAML spec, `client.New`, `f.Solve`, local mounts, local exporter output, `integration.SkipOnPlatform`, rootless detection, and `fstest.CreateFile`.

## Control Flow and Assertions
`testDeviceRunEnv` skips rootless and Windows environments. It writes `vendor1-device.yaml` with `cdiVersion: 0.6.0`, kind `vendor1.com/device`, device `foo`, a `containerEdits.env` entry `FOO=injected`, and BuildKit autoallow annotation. The Dockerfile runs BusyBox with `--device=vendor1.com/device=foo,required` plus an optional missing `vendor2.com/device=bar`, captures sorted environment to `foo.env`, exports it, and asserts the output contains `FOO=injected`.

## State, Persistence, and Dependencies
State persists only in the sandbox CDI spec directory for the test lifetime and exported local output. Dependencies include CDI support in the worker, non-rootless execution, Linux devices, Dockerfile frontend device parsing, and local export.

## Integration Points
This file integrates the Dockerfile frontend's `--device` option with worker CDI spec discovery, BuildKit device entitlement/autoallow behavior, environment injection, and exporter validation.

## Risks and Test Signals
Risks include CDI spec discovery failure, required device lookup regressions, optional missing devices incorrectly failing, environment edits not being applied, rootless/Windows unsupported paths accidentally running, and build tag coverage being omitted from default test runs. The signal is simple but strong: successful solve and exported environment containing the injected variable.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/dockerfile_rundevice_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/dockerfile_runnetwork_test.go -->
# sources/cloud-native/buildkit/frontend/dockerfile/dockerfile_runnetwork_test.go

## Purpose
This file validates Dockerfile `RUN --network` modes and global network forcing. It registers `runNetworkTests` into `networkTests` and uses an environment variable gate for tests that require host networking behavior.

## Important APIs, Types, and Functions
Tests are `testRunDefaultNetwork`, `testRunNoNetwork`, `testRunHostNetwork`, and `testRunGlobalNetwork`. They use `echoserver.NewTestServer`, `entitlements.EntitlementNetworkHost`, `AllowedEntitlements`, `FrontendAttrs{"force-network-mode": "host"}`, sandbox values such as `network.host`, `workers.IsTestDockerd`, and rootless/platform skips.

## Control Flow and Assertions
Default/no-network tests build BusyBox Dockerfiles that inspect `eth0`, with rootless conditions handled specially. Host-network tests start a local echo server, run `nc 127.0.0.1 <port>` in a `RUN --network=host` step, and optionally assert a normal RUN cannot reach it. The solve includes network-host entitlement and then branches on sandbox policy: granted must succeed, denied must fail with an entitlement error except in dockerd-specific behavior. The global network test forces host mode through frontend attrs, then checks explicit `--network=none` still blocks the connection.

## State, Persistence, and Dependencies
State is transient: temp Dockerfiles and a local echo server. Tests depend on Linux networking, sandbox network policy labels, worker entitlement enforcement, BusyBox `ip`/`nc`, and an opt-in environment variable for some network integration cases.

## Integration Points
The file tests frontend parsing of `--network`, frontend attr forced network mode, solver entitlement checks, worker network namespace behavior, rootless differences, and dockerd integration differences.

## Risks and Test Signals
Risks include host entitlement bypass, `--network=none` not isolating, forced network mode overriding explicit none, rootless behavior drifting, and test flakiness from local port reachability. Signals are solve success/failure, exact entitlement error text, and real TCP echo-server reachability.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/dockerfile_runnetwork_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/dockerfile_runsecurity_test.go -->
# sources/cloud-native/buildkit/frontend/dockerfile/dockerfile_runsecurity_test.go

## Purpose
This file validates Dockerfile `RUN --security` modes, security entitlements, and insecure device whitelist behavior. It registers `runSecurityTests` into `securityTests` and configures mirrored images for `alpine` and `tonistiigi/hellofs`.

## Important APIs, Types, and Functions
Tests are `testInsecureDevicesWhitelist`, `testRunSecurityInsecure`, `testRunSecuritySandbox`, and `testRunSecurityDefault`. They use `entitlements.EntitlementSecurityInsecure`, sandbox value `security.insecure`, `integration.WithMirroredImages`, `client.New`, `f.Solve`, and local Dockerfile/context mounts.

## Control Flow and Assertions
`testInsecureDevicesWhitelist` skips rootless, installs packages in Alpine, confirms `/dev/fuse` and loop-control are absent without insecure mode, then uses `RUN --security=insecure` to check device nodes, run `dmesg`, mount a FUSE hellofs filesystem, and mount an ext4 loopback image. `testRunSecurityInsecure` compares capability bounding sets under insecure and default RUNs. `testRunSecuritySandbox` checks explicit sandbox mode has the normal capability set. `testRunSecurityDefault` checks default behavior while passing the insecure entitlement, then branches on sandbox policy.

## State, Persistence, and Dependencies
State lives in temp Dockerfiles and image layers. Dependencies include Linux capabilities, `/proc/self/status`, FUSE, loop devices, mirrored external images, and sandbox entitlement configuration. Windows is not explicitly skipped in all tests, but the Dockerfiles use Linux images and proc/device semantics, so matrix selection likely handles platform suitability elsewhere.

## Integration Points
The file integrates Dockerfile `--security` parsing, worker capability/device setup, entitlement authorization, mirrored-image resolution, and privileged filesystem operations.

## Risks and Test Signals
Risks include insecure mode gaining too many or too few devices, entitlement denial not being enforced, default/sandbox capabilities changing unintentionally, rootless unsupported paths running, and external image/tool availability. Signals include capability string equality, successful/failed entitlement branches, and real FUSE/loopback operations under insecure mode.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/dockerfile_runsecurity_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/dockerfile_secrets_test.go -->
# sources/cloud-native/buildkit/frontend/dockerfile/dockerfile_secrets_test.go

## Purpose
This file tests Dockerfile secret mounts in RUN instructions, including file parameters, required-secret failure, environment-variable injection, status redaction, and combined env/file mounting. It registers `secretsTests` into `allTests`.

## Important APIs, Types, and Functions
Tests are `testSecretFileParams`, `testSecretRequiredWithoutValue`, `testSecretAsEnviron`, and `testSecretAsEnvironWithFileMount`. They use BuildKit sessions, `secretsprovider.FromMap`, `client.SolveStatus`, status channels, `assert` and `require`, platform skips, and local mounts.

## Control Flow and Assertions
`testSecretFileParams` supplies `mysecret` and verifies a mounted secret file has expected uid/gid/mode bits, then a later RUN confirms no stub remains. `testSecretRequiredWithoutValue` does not attach a secret provider and expects `secret mysecret: not found`. `testSecretAsEnviron` mounts a secret with `env=SECRET_ENV`, verifies the value is visible in the command environment and no default secret file exists, then reads solve status vertex names to ensure secret values are masked. `testSecretAsEnvironWithFileMount` confirms `env=` and `target=` can both be used for the same secret.

## State, Persistence, and Dependencies
Secret values are session-scoped attachables and should not persist into layers unless explicitly written by the command. The file depends on BuildKit session secret plumbing, Dockerfile mount parsing, status stream redaction, and POSIX tmpfs-backed file mounts for file-mode tests.

## Integration Points
The tests integrate Dockerfile frontend secret mount options with session providers, executor mount setup, frontend status naming/redaction, platform path differences, and layer persistence boundaries.

## Risks and Test Signals
Critical risks are secret leakage in status names, secret files persisting after RUN, required secrets silently becoming optional, file mode/ownership regressions, and Windows unsupported tmpfs paths accidentally running. Signals include exact error text, stat output, file absence checks, status-channel inspection, and env/file dual-access assertions.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/dockerfile_secrets_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/dockerfile_ssh_test.go -->
# sources/cloud-native/buildkit/frontend/dockerfile/dockerfile_ssh_test.go

## Purpose
This file tests Dockerfile SSH mounts. It verifies socket ownership/mode parameters and guards against leaking file descriptors to repeated SSH client invocations. It registers `sshTests` into `allTests` and is Linux-only.

## Important APIs, Types, and Functions
Tests are `testSSHSocketParams` and `testSSHFileDescriptorsClosed`. Dependencies include `sshprovider.NewSSHAgentProvider`, BuildKit sessions, generated RSA keys, `ssh-agent`, `os/exec`, socket path management, `client.New`, and `f.Solve`.

## Control Flow and Assertions
`testSSHSocketParams` generates an RSA private key, writes it to a short temp path, constructs an SSH agent provider from that key, and builds a BusyBox Dockerfile that stats `$SSH_AUTH_SOCK` under `RUN --mount=type=ssh,mode=741,uid=100,gid=102`. `testSSHFileDescriptorsClosed` starts a real `ssh-agent` in debug mode on a controlled socket, waits for the socket to appear, mounts it into an Alpine build that installs OpenSSH and calls `ssh -T git@github.com` three times, then checks agent debug output contains socket 1 but not socket 2 or 3.

## State, Persistence, and Dependencies
State includes temporary private keys, ssh-agent socket files, and debug output buffers. The tests depend on Linux Unix sockets, external package install/network access to GitHub in the build step, and BuildKit SSH session forwarding.

## Integration Points
The file exercises Dockerfile SSH mount parsing, session attachable forwarding, executor socket creation with requested metadata, and cleanup of forwarded connections/file descriptors across repeated command invocations.

## Risks and Test Signals
Risks include wrong socket ownership/mode, socket path length failures, fd leaks in SSH forwarding, external network/package flakiness, and Windows unsupported paths. Signals are stat equality and ssh-agent debug-output checks that detect repeated socket descriptors.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/dockerfile_ssh_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/dockerfile_targets_test.go -->
# sources/cloud-native/buildkit/frontend/dockerfile/dockerfile_targets_test.go

## Purpose
This file tests the Dockerfile frontend's `frontend.targets` subrequest. Target metadata lists stages, base images, default target status, descriptions derived from comments, sources, and location data. It also checks subrequest discovery metadata.

## Important APIs, Types, and Functions
Registered tests are `testTargetsList` and `testTargetsDescribeDefinition`; `unmarshalTargets` decodes `result.json` into `targets.List`. The file uses `workers.CheckFeatureCompat(workers.FeatureFrontendTargets)`, client frontend gating, `client.Build`, gateway `c.Solve`, `FrontendOpt{"frontend.caps", "requestid": "frontend.targets"}`, `subrequests.Describe`, and platform-specific base image selection.

## Control Flow and Assertions
`testTargetsList` creates a Dockerfile with named and unnamed stages plus comments before two stages. The gateway callback invokes `frontend.targets`, unmarshals the list, and asserts source bytes, four target entries, names, base image values, descriptions, default flag only on the final named target, and exact source line numbers. `testTargetsDescribeDefinition` invokes `subrequests.Describe` and verifies `frontend.targets` appears as an RPC request with a non-empty version.

## State, Persistence, and Dependencies
The tests are metadata-only and keep state in temp Dockerfile mounts and decoded result JSON. They depend on client frontend support, subrequest capability negotiation, parser source-location tracking, and comment-to-description extraction.

## Integration Points
This file integrates Dockerfile stage parsing with gateway subrequest output, target default selection, source inclusion, and frontend capability discovery. It does not run/export target stages; it validates metadata extraction before actual build execution.

## Risks and Test Signals
Risks include incorrect default target marking, lost unnamed stages, wrong base image reporting, stale line numbers after parser changes, descriptions attaching to the wrong stage, and subrequest discovery drift. Signals are exact list length, exact per-target fields, source equality, and `Describe` metadata checks.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/dockerfile_targets_test.go -->
