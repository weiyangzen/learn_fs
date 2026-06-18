<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/progress/progressui/init.go -->
# sources/cloud-native/buildkit/util/progress/progressui/init.go

Purpose: initializes package-level color and terminal log-height defaults for progress UI rendering.

Important APIs and types: package globals `colorRun`, `colorCancel`, `colorWarning`, `colorError`, `termHeightInitial`, and `termHeight` are consumed by `display.go` and `printer.go`. The `init` function configures them at process startup.

Control flow: if `NO_COLOR` is set, color globals remain nil so no ANSI color is applied. Windows defaults use cyan for completed/running rows; other platforms use blue. `BUILDKIT_COLORS` invokes `setUserDefinedTermColors` from the sibling color parser. `BUILDKIT_TTY_LOG_LINES` overrides the initial virtual terminal log pane height when it parses as a positive integer.

State and persistence: state is package-global and mutable. `termHeight` is later adjusted by TTY rendering as terminal dimensions change, so concurrent displays would share height state.

Dependencies and integration: depends on runtime GOOS, environment variables, and the package color map. It directly affects `ttyDisplay.print` color choices and vt100 sizing.

Risks: environment is read only once at package initialization. Invalid height input is silently ignored. Shared globals make behavior process-wide rather than display-instance-specific.

Test signals: no direct tests in this subset; behavior is exercised indirectly by display rendering.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/progress/progressui/init.go -->
