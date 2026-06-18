# Research: sources/cloud-native/buildkit/cmd/buildctl/debug/cli.go

Purpose: supplies a small adapter that converts debug package functions of shape `func(*cli.Command) error` into urfave/cli v3 `ActionFunc`.

Important APIs and flow: `commandAction` ignores the context argument supplied by cli v3 and passes the command object to the package command function. This keeps debug command implementations consistent with the main package command style.

State and dependencies: no state or persistence. It depends only on `context` and `github.com/urfave/cli/v3`.

Risks and test signals: because it discards the passed action context, debug commands rely on app-level context storage via common helpers or `appcontext.Context()`. There are no direct tests; errors surface when debug commands are executed through the CLI.
