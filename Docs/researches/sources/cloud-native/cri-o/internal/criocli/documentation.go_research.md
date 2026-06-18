# sources/cloud-native/cri-o/internal/criocli/documentation.go

Purpose: provides CLI subcommands that generate man-page and markdown documentation for the app.

Important APIs/types/functions: `markdownDocTemplate`, `man()`, and `markdown()`.

Control flow: `man` returns a command that writes `c.App.ToMan()` output. `markdown` returns a command that temporarily overrides `cli.MarkdownDocTemplate` with CRI-O’s custom template, writes `c.App.ToMarkdown()`, and restores the original template with a deferred assignment.

State and persistence behavior: writes generated documentation to the app writer. Temporarily mutates the global urfave/cli markdown template during markdown generation.

Dependencies/integration points: urfave/cli documentation generation. `DefaultCommands` includes these commands.

Risks: global template mutation must be restored even on errors; the defer handles normal control flow. Concurrent documentation generation in the same process could observe the temporary template.

Test signals: no direct tests in this subset.
