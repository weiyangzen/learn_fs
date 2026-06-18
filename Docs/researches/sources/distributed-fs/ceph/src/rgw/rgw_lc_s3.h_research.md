# sources/distributed-fs/ceph/src/rgw/rgw_lc_s3.h

Purpose: Declares S3 XML-specialized subclasses for lifecycle filters, expirations, transitions, rules, and whole lifecycle configurations.

Important APIs and types: `LCFilter_S3`, `LCExpiration_S3`, `LCNoncurExpiration_S3`, `LCMPExpiration_S3`, `LCTransition_S3`, `LCNoncurTransition_S3`, `LCRule_S3`, and `RGWLifecycleConfiguration_S3` each add `decode_xml()` and/or `dump_xml()` to their generic lifecycle base type. `RGWLifecycleConfiguration_S3::rebuild()` copies S3-parsed rules into a generic validated configuration.

Control flow: The header establishes a two-phase parse model: parse XML into S3 subclasses, then rebuild into the generic encoded lifecycle configuration consumed by `RGWLC`. Dump methods perform the reverse for GET lifecycle responses.

State and persistence: S3 subclasses mostly reuse base-class storage. `LCExpiration_S3` adds `dm_expiration` to represent `ExpiredObjectDeleteMarker` before it is copied into `LCRule::dm_expiration`.

Dependencies and integration points: Depends on `rgw_lc.h`, XML helpers, S3 tag XML handling, and Ceph include types. It is consumed by S3 REST lifecycle operation code and implemented by `rgw_lc_s3.cc`.

Risks: The subclasses rely on casts between generic and S3 lifecycle types in dump paths. That is safe only when objects actually originated from S3-specific classes or layout-compatible base state. The default constructor without `CephContext` cannot decode full configurations because id generation requires context.

Test signals: Compile and runtime tests should cover decode with and without context, XML dump casts, delete-marker expiration transfer, noncurrent version fields, and rebuild validation failures.
