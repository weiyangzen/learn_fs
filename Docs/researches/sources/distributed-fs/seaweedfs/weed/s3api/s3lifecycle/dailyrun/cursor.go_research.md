# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/dailyrun/cursor.go

Purpose: persistent cursor model for the daily lifecycle replay worker. It records per-shard meta-log progress and rule-set partition hashes so workers can resume, detect rule changes, and throttle full-bucket walker runs.

Important APIs/types: `CursorDir` is `/etc/s3/lifecycle/daily-cursors`. `Cursor` stores `TsNs`, `RuleSetHash`, `PromotedHash`, and `LastWalkedNs`. `CursorPersister` abstracts load/save. `FilerCursorPersister` stores JSON cursor files through `dispatcher.FilerStore`. `cursorFileName`, `Load`, and `Save` implement the file contract.

Control flow: `Load` rejects nil store, reads `shard-%02d.json`, treats `filer_pb.ErrNotFound` as cold start, rejects empty files, decodes JSON, validates version, shard id, and exact 32-byte hashes, copies hashes into arrays, and returns found. `Save` builds an indented JSON `cursorFile` and writes it to the filer store.

State and persistence behavior: durable per-shard cursor files live under the filer. Strict validation is intentional to avoid silently converting corrupt/truncated state into plausible zero-padded hashes. `LastWalkedNs` is omitempty/backward-compatible; missing value means never walked.

Dependencies and integration points: uses `filer_pb.ErrNotFound` and `dispatcher.FilerStore`. `run.go` loads/saves cursors, publishes cursor gauges, and uses hashes to decide recovery.

Risks: save atomicity depends on `FilerStore.Save` implementation; this file detects empty/corrupt reads but cannot prevent partial writes. Hash length validation is critical; relaxing it risks masking corruption. Cursor filename format assumes shard counts below 100 for zero-padding readability but still formats larger values.

Test signals: `cursor_test.go` covers not-found, round trip, shard isolation, corrupt/empty/wrong-version/shard-mismatch/hash-length errors, and nil store errors.
