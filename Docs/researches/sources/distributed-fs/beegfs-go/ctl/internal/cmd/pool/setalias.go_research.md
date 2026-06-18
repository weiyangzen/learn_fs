
# sources/distributed-fs/beegfs-go/ctl/internal/cmd/pool/setalias.go

- Purpose: implements `pool set-alias <storage-pool> <alias>`.
- Important APIs: `newSetAliasCmd` and `runSetAliasCmd`.
- Control flow/state: parses storage pool entity ID, validates alias, calls `backend.SetAlias`, and prints confirmation.
- Dependencies/integration: uses BeeGFS parsers and pool backend alias persistence.
- Risks/tests: no local duplicate/existence checks; backend owns validation. No direct tests found.
