# sources/distributed-fs/juicefs/pkg/object/gs.go


Purpose: implements Google Cloud Storage behind `!nogs`, registering `gs`.

Important APIs and flow: `gs` maintains multiple `storage.Client` instances and selects them round-robin. `Create` probes list, discovers project ID from env, metadata, or default credentials, guesses region from metadata zone, and creates the bucket. `Head`, `Get`, `Put`, `Copy`, `Delete`, and `List` use the GCS client. `Put` sets storage class from active tier and a 5 MiB writer chunk size. `List` uses `iterator.Pager`, supports delimiter common prefixes, and returns page tokens.

State and persistence: persistent state is GCS bucket/object data. Local state includes clients, bucket, region, tier config, and atomic index.

Dependencies and integration: depends on `cloud.google.com/go/storage`, Google auth/metadata packages, shared `Tier`, `ResponseAttrs`, and `DefaultStorageClass`.

Risks: `newGS` returns a `gs` with zero-value tier map unless `InitTiers` is called; methods like `Create` and `Put` assume tier access. Credential discovery and bucket creation require environment or metadata availability. Restore is unsupported because GCS does not expose the same temporary restore operation. `ListAll` is inherited/default unsupported unless generic helpers use `List`.

Test signals: `TestGS` is environment-gated on `GOOGLE_APPLICATION_CREDENTIALS` and runs `testStorage`.
