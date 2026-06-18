## sources/cloud-native/buildkit/util/gitutil/git_cli.go

Purpose: wraps `git` CLI execution with BuildKit-specific isolation, environment control, retry fallbacks, and configurable command execution/streams.

Important APIs/types: `GitCLI` stores binary, exec hook, extra args, working tree/git dir, SSH settings, stream factory, and host config opt-in. Options include `WithGitBinary`, `WithExec`, `WithArgs`, `WithDir`, `WithWorkTree`, `WithGitDir`, `WithSSHAuthSock`, `WithSSHKnownHosts`, `WithHostGitConfig`, and `WithStreams`. `Run(ctx,args...)` executes a git command and returns stdout bytes.

Control flow: `Run` builds `exec.Cmd`, adds `-c protocol.file.allow=user`, optional work-tree/git-dir and args, captures stdout/stderr, optionally tees streams, and constructs a restricted environment. By default it disables system/global/user git config via `GIT_CONFIG_NOSYSTEM`, `HOME=os.DevNull`, and `GIT_CONFIG_GLOBAL=os.DevNull`; host config variables are copied only with `WithHostGitConfig`. Proxy variables and SSH auth socket are forwarded. On errors it wraps stderr, handles context cause specially, retries without `--depth=1` for shallow/depth complaints, and retries `fetch` without a commit refspec for "not our ref" or unadvertised-object failures.

State/persistence: immutable-ish client config; `New` shallow-copies and clones args. No repository state is changed except whatever git command performs. Dependencies: `os/exec`, BuildKit git helpers, `pkg/errors`.

Integration points: used by BuildKit Git source resolver. Risks: stream setup defers `stdout.Close()`/`stderr.Close()` without nil checks if a custom stream factory returns nil; retry string matching depends on git stderr wording; `WithExec` uses `context.TODO()` in `CommandContext` and relies entirely on the hook for cancellation. Test signals: `git_cli_test.go` covers SSH command construction and git config environment isolation/opt-in.
