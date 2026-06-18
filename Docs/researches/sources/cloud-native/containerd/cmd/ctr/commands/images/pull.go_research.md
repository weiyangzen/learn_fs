# sources/cloud-native/containerd/cmd/ctr/commands/images/pull.go

Purpose: implements `ctr images pull`, fetching, registering, and unpacking images from remote registries.

Important APIs/types/functions: `pullCommand`, transfer-mode setup, local fetch/unpack path, `progressNode`, `ProgressHandler()`, `DisplayHierarchy()`, `displayNode()`, `prefixes()`, `displayName()`, `shortenName()`, and `Display()`.

Control flow: validates ref, creates client/context, then defaults to transfer-service mode unless `--local`. Transfer mode rejects local-only flags, creates static credentials and registry source, resolves platforms with default Linux substitution on Darwin, configures unpack/store metadata/labels, and runs `client.Transfer()` with hierarchical progress. Local mode creates a lease, uses content fetch config, fetches content, resolves platforms, unpacks each selected platform, optionally prints chain ID, and prints elapsed time.

State and persistence: writes content, image metadata, snapshots, and leases. Progress state is in-memory.

Dependencies/integration: transfer registry/image APIs, content fetch helpers, containerd image APIs, diff sync-fs, platform helpers, progress writer, identity chain IDs.

Risks: transfer mode and local mode support different flags, enforced by runtime validation. All-platform unpack support in transfer mode is noted as TODO. Progress tree parent attachment can display roots before parents arrive, though update logic later re-parents known nodes.

Test signals: no local tests for pull paths or progress rendering.
