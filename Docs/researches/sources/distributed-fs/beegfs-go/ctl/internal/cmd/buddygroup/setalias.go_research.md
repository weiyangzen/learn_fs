
# sources/distributed-fs/beegfs-go/ctl/internal/cmd/buddygroup/setalias.go

- Purpose: implements `mirror set-alias <buddygroup> <alias>`.
- Important APIs: `newSetAliasCmd` and `runSetAliasCmd`.
- Control flow/state: parses a meta/storage entity ID and validates alias, then calls `backend.SetAlias` and prints success.
- Dependencies/integration: integrates with management alias storage through `ctl/pkg/ctl/buddygroup`; uses common BeeGFS alias and entity parsers.
- Risks/tests: no confirmation or existence preflight here; backend must enforce uniqueness and validity. No direct tests observed.
