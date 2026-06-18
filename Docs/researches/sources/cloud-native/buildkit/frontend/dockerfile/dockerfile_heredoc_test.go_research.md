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
