<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/filesystem/flags.go -->
# sources/distributed-fs/beegfs-go/common/filesystem/flags.go

Purpose: exposes the CLI/config flag name for file filtering.

Important APIs/types/functions: `FilterExprFlag = "filter-files"`.

Control flow: none.

State and persistence: none.

Dependencies and integration points: consumed by command/config packages that expose the filter DSL from `filter.go`.

Risks: changing the constant is a user-facing flag compatibility break.

Test signals: no direct tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/filesystem/flags.go -->
