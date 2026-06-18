
# sources/distributed-fs/beegfs-go/ctl/internal/cmd/pool/list.go

- Purpose: implements `pool list` and exported `RunListCmd` used by quota defaults listing.
- Important APIs: `newListCmd` and `RunListCmd`.
- Control flow/state: rejects page size 0, fetches pools, conditionally includes default quota limit columns, formats limits raw or human-readable, formats targets/mirrors differently in debug mode, and prints a table.
- Dependencies/integration: uses pool backend `GetStoragePools`, Viper raw/debug/page-size config, `cmdfmt`, and quota formatting utilities.
- Risks/tests: multi-line cells require paging constraints; target/group string assembly has separate debug and non-debug paths. No direct tests found.
