# sources/distributed-fs/juicefs/pkg/object/oos.go


Purpose: implements CTYun OOS/S3-compatible storage behind `!nos3`, registering `oos`.

Important APIs and flow: `oos` embeds `s3client`, overriding `String`, `Limits`, `Create`, and `List`. `Create` does not create buckets; it probes list and asks the user to create the bucket manually on failure. `List` caps limit at 1000, delegates to `s3client.List`, and removes the first object when it equals the `start` marker to handle provider-inclusive listing. `newOOS` parses bucket and region from endpoint host, derives service endpoint, chooses path-style except for `xstore.ctyun.cn`, and builds an AWS SDK v2 S3 client with static credentials and unsigned payload middleware.

State and persistence: persistent data is delegated to the remote OOS bucket via `s3client`.

Dependencies and integration: uses AWS SDK v2, shared S3 implementation, `httpClient`, and `defaultPathStyle`-style behavior.

Risks: endpoint parsing assumes host label shape where the second label starts with a region prefix sliced by `[4:]`. Bucket creation is unsupported operationally. Inclusive-marker adjustment is provider-specific and can affect pagination if the delegate behavior changes.

Test signals: `TestOOS` is environment-gated on `OOS_ACCESS_KEY` and runs the shared storage suite.
