# sources/distributed-fs/beegfs-go/ctl/internal/config/config.go

Purpose: defines and binds CTL global CLI flags, environment variables, and cleanup hooks for the command front-end.

Important APIs/types/functions: `InitGlobalFlags`; `Cleanup`. The initializer registers flags for debug/raw/output/columns/page-size, management and BeeRemote addresses, mount handling, TLS/auth, worker count, logging, pprof, proxy use, alerts, and environment binding.

Control flow: flags are registered on the root persistent flag set, hidden developer/proxy/pprof flags are marked hidden, Viper is configured with `BEEGFS_` prefix and hyphen-to-underscore replacement, `BEEGFS_BINARY_NAME` is set, and every persistent flag is bound to both environment and pflag.

State and persistence: mutates process environment and Viper global configuration. `Cleanup` delegates to backend config cleanup to release global resources.

Dependencies and integration points: front-end bridge to `ctl/pkg/config`; uses Cobra, pflag, Viper, runtime CPU count, and internal util validated-string flag for output modes.

Risks: Viper is global, so tests and library consumers must isolate/reset state. Defaults such as management auto-detection, auth file, TLS cert file, and worker count strongly affect backend behavior. Some `MarkHidden` errors are ignored.

Test signals: no direct tests. Useful tests would validate env binding names, defaults, hidden flags, output value validation, and cleanup forwarding.
