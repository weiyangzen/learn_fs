# Research: sources/cloud-native/moby/daemon/command/cobra.go

## sources/cloud-native/moby/daemon/command/cobra.go

Purpose: configures root Cobra command presentation and flag error handling for dockerd.

Important APIs: `SetupRootCommand`, `FlagErrorFunc`, `wrappedFlagUsages`, plus `usageTemplate` and `helpTemplate`. Setup registers a template function, sets usage/help/version templates, installs a Docker CLI-like flag error function, adds persistent `--help/-h`, and marks the shorthand deprecated. `FlagErrorFunc` wraps parse errors in `StatusError` with status code 125 and a `See '<cmd> --help'` message, including usage for commands with subcommands.

State is Cobra command configuration. Dependencies are `github.com/spf13/cobra` and terminal width detection. Risks include terminal width errors falling back to 80 columns, template changes affecting UX and tests, and status-code compatibility with Docker CLI behavior. Tests are not in this subset.
