# sources/cloud-native/cri-o/internal/config/nri/nri.go

Purpose: models CRI-O configuration for NRI, converts it to containerd NRI adaptation options, and applies NRI timeout globals.

Important APIs/types/functions: `Config` holds enablement, socket path, plugin path/config path, registration/request timeouts, connection disabling, tracing flag, and `DefaultValidator`. `DefaultValidatorConfig` mirrors validator plugin policy. Public methods include `New`, `IsDefaultValidatorDefaultConfig`, `Validate`, `WithTracing`, `ToOptions`, `ConfigureTimeouts`, and `DefaultValidatorConfig.ToNRI`.

Control flow: `New` populates containerd NRI defaults and an empty validator config. `defaultValidatorEqual` compares every validator field and compares `RequiredPlugins` after sorting, making ordering irrelevant. `ToOptions` appends options only for non-empty/non-nil settings, adds disabled external connections when requested, maps the default validator, and injects OpenTelemetry ttrpc interceptors when tracing is enabled. `ConfigureTimeouts` sets global NRI timeouts only when durations are nonzero.

State and persistence behavior: config state is in memory. `ConfigureTimeouts` mutates package-level NRI adaptation timeouts. No files are read or written.

Dependencies/integration points: integrates `github.com/containerd/nri/pkg/adaptation`, `github.com/containerd/nri/plugins/default-validator`, ttrpc, and otel ttrpc. CLI merge code writes these fields from flags; server startup consumes `ToOptions` and timeout configuration.

Risks: `Validate` currently returns nil, so bad paths or policy combinations are not checked here. `ToOptions` dereferences `c.withTracing` after nil-guarded blocks; because it uses `if c.withTracing`, callers must not call `ToOptions` on nil if tracing path might be evaluated. Global timeout mutation affects the process.

Test signals: no direct tests in this subset; CLI tests touch only selected NRI flag merging indirectly through config metadata shape.
