# sources/cloud-native/containerd/core/metadata/migrations.go

Purpose: declares ordered metadata database migrations and implements schema transitions for snapshot child links, ingest bucket restructuring, a historical no-op, and sandbox bucket relocation.

Important APIs and types: `migration` holds schema, version, and function. `migrations` is the ordered migration list. Migration functions are `addChildLinks`, `migrateIngests`, `migrateSandboxes`, and `noOpMigration`.

Control flow: `addChildLinks` iterates every namespace and snapshotter, finds snapshots with a `parent`, and adds each child key under the parent's `children` bucket when the parent exists. `migrateIngests` moves deprecated flat ingest entries from `content/ingest` into structured `content/ingests/<ref>/ref`, then deletes the deprecated bucket. `migrateSandboxes` creates the version bucket, iterates root-level namespace buckets other than `v1`, copies sandbox buckets and subbuckets into `v1/<namespace>/sandboxes`, then deletes the old root namespace buckets. `noOpMigration` intentionally returns nil for the old bolt-to-bbolt transition.

State and persistence: all migrations mutate bbolt schema in place. `migrateSandboxes` copies key/value entries and one nested subbucket level for each sandbox, and treats unexpected deeper buckets as errors. `addChildLinks` deliberately skips inconsistent parent references rather than failing the migration.

Dependencies and integration: used by metadata DB open/upgrade paths elsewhere in the package. It depends on bbolt and bucket key constants shared by stores and GC.

Risks: migration order is contractually important and comments require a migration test for each new entry. `migrateSandboxes` deletes all non-`v1` root buckets after attempting sandbox migration; if unexpected root buckets existed, they would be removed by design in this schema transition. `addChildLinks` can leave inconsistent child state if parent buckets are missing.

Test signals: this file itself has no tests in the subset, but related snapshot remove behavior depends on child links, and sandbox tests depend on post-migration bucket layout assumptions.
