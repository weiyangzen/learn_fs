# sources/distributed-fs/seaweedfs/weed/s3api/s3bucket/s3api_bucket.go

Purpose: central S3 bucket name validator for SeaweedFS S3 API. It enforces AWS-like bucket naming constraints plus a SeaweedFS-specific reservation for `filemeta`, which collides with filer metadata storage on SQL backends.

Important APIs/types: `VerifyS3BucketName(name string) error` is the exported validator. `reservedBucketName` is the package constant for `filemeta`.

Control flow: validation checks length, reserved name, allowed runes, adjacent periods, starting and ending characters, reserved `xn--` prefix, reserved `-s3alias` suffix, and IP-address-like names via `net.ParseIP`. It returns the first validation error encountered.

State and persistence behavior: no state is persisted here, but the `filemeta` rejection protects persistent filer metadata tables/collections from bucket-name collisions that can make buckets undeletable and interfere with fsck.

Dependencies and integration points: uses `net`, `strings`, `unicode`, and `fmt`. Called by bucket creation paths before creating filer entries or bucket metadata.

Risks: AWS bucket naming rules evolve; this file implements a subset and has a TODO for transfer acceleration dot restrictions. Unicode number categories are accepted through `unicode.IsNumber`, not just ASCII digits, which may be broader than AWS DNS-style rules. Error messages are user-visible and may be asserted by clients only loosely.

Test signals: `s3api_bucket_test.go` covers invalid uppercase, IP address, adjacent dots, too short, leading dot, trailing hyphen, all hyphens, invalid character, and `filemeta`, plus several valid names.
