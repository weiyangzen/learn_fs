# Research: sources/cloud-native/buildkit/cmd/buildctl/debug/info.go

Purpose: implements `buildctl debug info`, which displays BuildKit and Dockerfile frontend version information reported by the daemon.

Important APIs and flow: `info` resolves the client, calls `c.Info` with the command context, then either executes a template or prints a small tabwriter table with BuildKit package/version/revision and optional Dockerfile version.

State and dependencies: no persistence; reads daemon version state through the client info API. Dependencies are shared client resolution, template parsing, tabwriter, and standard output.

Risks and test signals: output depends on daemon capability and Dockerfile version availability. The command is simple and has no direct test in this subset; version response construction is covered on the daemon side by `Controller.Info`.
