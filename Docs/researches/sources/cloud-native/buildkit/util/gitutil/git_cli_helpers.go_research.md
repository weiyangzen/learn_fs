## sources/cloud-native/buildkit/util/gitutil/git_cli_helpers.go

Purpose: supplies convenience methods for repository paths and cleaned git output.

Important APIs: `Dir()` returns explicit dir or work tree. `WorkTree(ctx)` returns configured `workTree` or runs `git rev-parse --show-toplevel`. `GitDir(ctx)` returns configured `gitDir` or appends `.git` to the work tree. `clean([]byte,error)` keeps first output line, strips single quotes, and trims error newlines.

Control flow/state: methods delegate to `GitCLI.Run`, so they inherit environment isolation and retry behavior. No persistence.

Dependencies/integration: used by Git source code needing stable repository directories. Risks: `GitDir` assumes standard non-bare `.git` directory when not configured; `clean` removes all single quotes, which is useful for shell-quoted git output but lossy for unusual paths. Test signals: no direct helper test in this subset.
