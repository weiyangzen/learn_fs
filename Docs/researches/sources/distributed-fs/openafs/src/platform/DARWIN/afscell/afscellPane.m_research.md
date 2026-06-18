# Research: sources/distributed-fs/openafs/src/platform/DARWIN/afscell/afscellPane.m

Purpose: implements the installer pane that reads existing local cell settings and writes user-selected `ThisCell`/`CellAlias` values for the installer to consume.

Important APIs and control flow: helper methods validate word/cell/alias syntax, parse a `CellAlias` line for the current cell, append old or new alias lines, and show alert panels. `didEnterPane:` reads `/private/var/db/openafs/etc/ThisCell` and `CellAlias`, displays the first local cell line, and finds its alias. `shouldExitPane:` on forward navigation validates the cell, writes `/private/tmp/org.OpenAFS.Install.ThisCell.<username>`, optionally validates alias, rewrites or appends a matching alias line, and writes `/private/tmp/org.OpenAFS.Install.CellAlias.<username>`.

State and persistence: persistent existing config is read from `/private/var/db/openafs/etc`. New installer data is written to user-suffixed temp files under `/private/tmp`, not directly into final config.

Dependencies and integration: InstallerPane lifecycle, Cocoa scanners/alerts, and later installer scripts that consume the temp files.

Risks: username in temp filename is not sanitized. Alias parsing is scanner-based and may mishandle comments/whitespace. Alerts allow continuing after write failures, which can produce partial installer state. The validation only allows alphanumeric and hyphen labels, with dots for cells.

Test signals: no existing ThisCell, no CellAlias, valid and invalid domain-style cells, empty cell continue/cancel, alias replace/append/no-op, temp-file write failure, and usernames with unusual characters.
