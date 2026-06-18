# sources/distributed-fs/juicefs/pkg/object/eos.go


Purpose: implements an EOS S3-compatible backend behind `!nos3`, registering `eos`.

Important APIs and flow: `eos` embeds `s3client`, overriding `String` and `Limits`. `newEos` normalizes endpoints to HTTPS, derives the bucket from the first host label, strips the bucket from the service endpoint, sets region to `us-east-1`, loads `EOS_ACCESS_KEY`, `EOS_SECRET_KEY`, and `EOS_TOKEN` fallbacks, and creates an AWS SDK v2 S3 client with custom endpoint, path-style policy, shared HTTP client, unsigned payload middleware, and one retry attempt.

State and persistence: all object, listing, and multipart persistence is delegated to `s3client` and the remote EOS-compatible service. Local state is the S3 client, bucket, and region.

Dependencies and integration: depends on AWS SDK v2, shared `defaultPathStyle`, `httpClient`, and the package's generic S3 implementation in files outside this subset.

Risks: endpoint parsing assumes bucket-as-first-label host format. Region is hard-coded. All core operation behavior is inherited from `s3client`, so provider-specific quirks must be handled there or through endpoint configuration. Build is disabled by `nos3`.

Test signals: `TestEOS` is environment-gated on `EOS_ENDPOINT` and then runs the shared object-storage contract.
