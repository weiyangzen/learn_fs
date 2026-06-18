## sources/cloud-native/buildkit/util/progress/progressui/colors.go

Purpose: parses `BUILDKIT_COLORS` customization for progress UI semantic colors.

Important functions: `setUserDefinedTermColors`, `readBuildkitColorsEnv`, `readRGB`, `parseKeys`, `isValidRGB`, `isValidRGBValue`. `termColorMap` maps named colors to `aec` ANSI values.

Control flow: environment string is parsed as colon-separated CSV fields; each field must be `key=value` with no extra equals. Values are matched against named colors or parsed as comma-separated RGB triplets. Keys update `colorRun`, `colorCancel`, `colorError`, or `colorWarning`; unknown keys/values log warnings and are ignored.

State/persistence: mutates package-level color variables in progress UI; no persistence. Dependencies: BuildKit logger, `morikuni/aec`, `tonistiigi/go-csvvalue`.

Integration points: terminal progress display configuration. Risks: invalid config only warns; RGB parsing depends on CSV escaping; package-level mutation affects subsequent displays globally. Test signals: no color tests in this subset.
