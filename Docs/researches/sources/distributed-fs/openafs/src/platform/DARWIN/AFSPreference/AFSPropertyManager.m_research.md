# Research: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/AFSPropertyManager.m

Purpose: implements the preference pane's OpenAFS configuration engine. It parses local AFS configuration from `/var/db/openafs`, exposes cache and cell state to the UI, writes changed config through the privileged helper, starts/stops the client, and shells out for tokens.

Important APIs and control flow: `loadConfiguration` checks the install path, clears current state, determines whether to use `afs.conf` or `afsd.options` from `fs -version`, reads `ThisCell`, `TheseCells`, `CellServDB`, `cacheinfo`, and afsd options. `readCellDB` scans `CellServDB` into `DBCellElement` and `CellIp` objects. `readAFSDParamLineContent` decodes `-afsdb`, `-verbose`, `-stat`, `-dcache`, `-daemons`, `-volumes`, and `-dynroot`. `saveConfigurationFiles:` writes `ThisCell`, `CellServDB`, and `TheseCells`; `saveCacheConfigurationFiles:` writes `cacheinfo` plus old or new afsd config. `getTokens:` iterates token-default cells and calls klog or aklog.

State and persistence: persistent state lives in OpenAFS config files under `/var/db/openafs/etc` and `/var/db/openafs/etc/config`, but callers pass logical names like `/etc/CellServDB` to `TaskUtil`; the privileged helper prefixes them with `/var/db/openafs`. Backups use `.afscommander_bk`. AFS status is inferred from mounted volume resource descriptions containing `(afs)`.

Dependencies and integration: uses `TaskUtil` for `fs`, `tokens`, `klog`, `aklog`, `unlog`, privileged backup/write, `afsd_start`, and `afsd_stop`. Uses `Krb5Util` to acquire tickets before `aklog`. Exposes mutable `cellList` directly to `AFSCommanderPref` and `IpConfiguratorCommander`.

Risks: parsers are scanner-based and fragile around comments, quoted values, empty files, malformed lines, hostnames without IPs, and missing `TheseCells` because `readTheseCell` assumes a nonnil file handle. Version parsing shells out to `fs` multiple times. `klog` compares strings with `== @""`, not content equality. `checkAfsStatus` ignores the configured mount point. Privileged writes accept only the helper allowlist; adding new files requires updating both sides.

Test signals: fixtures for `ThisCell`, empty/missing `TheseCells`, CellServDB entries with no servers, comments and whitespace, old and new afsd configs, malformed `fs -version`, cacheinfo validation, backup/write failures, start/stop status codes, token parsing, multi-cell token acquisition, and mounted-volume detection.
