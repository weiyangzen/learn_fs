## sources/cloud-native/buildkit/util/gitutil/git_cli_test.go

Purpose: verifies Git CLI environment and SSH helper behavior.

Important tests: `TestGetGitSSHCommandUsesConfigPath` checks default strict-host-key disabling and known-hosts override. `TestGitCLIConfigEnv` uses `WithExec` to inspect `cmd.Env`, confirming default isolation from host config and explicit `WithHostGitConfig` forwarding of HOME/XDG/Windows/global/system config variables.

Control flow/state: environment variables are set with `t.Setenv`; no actual git command is run because `WithExec` returns nil.

Risks covered: accidental host config leakage in daemon-side git operations and missing host config in client-side inspection. Gaps: no tests for depth/refspec retry, stream nil behavior, or context cancellation.
