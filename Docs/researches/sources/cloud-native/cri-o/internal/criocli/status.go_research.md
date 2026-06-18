# sources/cloud-native/cri-o/internal/criocli/status.go

Purpose: implements `crio status` and subcommands for querying a running CRI-O daemon.

Important APIs/types/functions: constants `defaultCrioSocketPath` and `crioSocketPath`; `StatusCommand`; helpers `crioClient`, `configSubCommand`, `containers`, `info`, `goroutines`, and `heap`.

Control flow: `StatusCommand` requires subcommands and exposes `config`, `containers`, `info`, `goroutines`, and `heap`. `crioClient` builds a client from `--socket`. `configSubCommand` prints daemon config info. `containers` optionally filters by ID and supports verbose output. `info` prints version/config/storage/runtime details. `goroutines` and `heap` request runtime diagnostics and write them to stdout.

State and persistence behavior: reads daemon state over the CRI-O client socket and writes output to stdout. Does not mutate daemon state.

Dependencies/integration points: urfave/cli and `github.com/cri-o/cri-o/pkg/client`. Integrates with the CRI-O status API served by the daemon.

Risks: command success depends on daemon socket availability and permissions. Output is plain text and tightly coupled to client response structures. Filtering and verbose modes are implemented client-side.

Test signals: no direct tests for status commands in this subset.
