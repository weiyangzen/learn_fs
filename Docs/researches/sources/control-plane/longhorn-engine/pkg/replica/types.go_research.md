# sources/control-plane/longhorn-engine/pkg/replica/types.go

Purpose: defines shared progress state strings for backup, restore, purge, clone, rebuild, and hash status reporting inside replica/sync packages.

Important APIs/types/functions: `ProgressState` is a string alias with constants `ProgressStateInProgress`, `ProgressStateComplete`, and `ProgressStateError`.

Control flow: no executable control flow. Other files compare and serialize these constants.

State and persistence: values are persisted or returned as JSON/RPC strings by status objects in backup, restore, and sync-agent code.

Dependencies and integration points: consumed by `BackupStatus`, `RestoreStatus`, `SnapshotHashJob`, sync RPC list retention, and status responses.

Risks: string constants are part of external API contracts; changing them would break clients. There is no enum validation helper, so arbitrary strings can still be assigned to `ProgressState`.

Test signals: indirectly tested wherever status transitions assert these values.
