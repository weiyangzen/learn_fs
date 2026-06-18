# sources/cloud-native/containerd/cmd/ctr/commands/leases/leases.go

Purpose: implements `ctr leases` list/create/delete commands for containerd leases.

Important APIs/functions: `Command`, `listCommand`, `createCommand`, and `deleteCommand`.

Control flow: list applies filters and prints quiet IDs or table with created time and sorted labels. Create parses label args, optional ID, optional expiration defaulting to 24h, creates a lease, and prints the ID. Delete validates at least one ID, deletes each lease, and applies synchronous delete only to the last ID when `--sync` is set.

State and persistence: reads, creates, and deletes lease metadata; synchronous delete can trigger cleanup of unreferenced resources.

Dependencies/integration: leases service, shared client helper, tabwriter.

Risks: create label parsing ignores whether `=` was present and stores empty values for bare keys. Quiet flag usage text says blob digest, likely copied from content commands.

Test signals: no local tests.
