# sources/cloud-native/cri-o/internal/config/ulimits/ulimits.go

Purpose: parses configured default ulimits into runtime-tools compatible resource limit entries.

Important APIs/types/functions: `Ulimit` with `Name`, `Hard`, and `Soft`; `Config` storing `[]Ulimit`; `New`, `LoadUlimits`, and `Ulimits`.

Control flow: `LoadUlimits` iterates strings such as `name=soft:hard`, parses with Docker `go-units.ParseUlimit`, converts to an rlimit with `GetRlimit`, and appends a `Ulimit` whose name is `RLIMIT_` plus the uppercased parsed name. Errors are wrapped with the original unrecognized string when parsing fails.

State and persistence behavior: parsed limits are stored in memory. No files are read or written.

Dependencies/integration points: depends on `github.com/docker/go-units`. The resulting names and values match runtime-tools expectations for OCI spec generation.

Risks: repeated `LoadUlimits` calls append rather than replace, so callers should load once on a fresh config. Error handling stops on the first invalid entry.

Test signals: `ulimits_test.go` covers empty defaults, invalid input, and a valid `locks=10:64` entry.
