
# sources/distributed-fs/beegfs-go/ctl/internal/cmd/health/utils.go

- Purpose: shared formatting helpers for health command headings and client headers.
- Important APIs: `printHeader`, `sPrintHeader`, and `printClientHeader`.
- Control flow/state: builds repeated-character headers sized to the longest line, prints them, and formats client ID plus management/mount mapping.
- Dependencies/integration: uses `cmdfmt` for output and `procfs.Client` data from health network/check flows.
- Risks/tests: output-only helpers; multi-line header sizing is custom and not directly tested.
