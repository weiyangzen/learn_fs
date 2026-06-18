<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/nri/logshim.go -->
# sources/cloud-native/moby/daemon/internal/nri/logshim.go

Purpose: adapts containerd NRI framework logging to Docker's contextual logger.

Important APIs and types: `logShim` implements `nrilog.Logger` with `Debugf`, `Infof`, `Warnf`, and `Errorf`.

Control flow: each method prefixes messages with `NRI: ` and delegates to `log.G(ctx)`.

State and persistence: none.

Dependencies and integration: `nri.go` installs this logger with `nrilog.Set` when NRI starts.

Risks: format strings and arguments pass through directly; caller-controlled strings are logged as format strings by design.

Test signals: no direct tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/nri/logshim.go -->
