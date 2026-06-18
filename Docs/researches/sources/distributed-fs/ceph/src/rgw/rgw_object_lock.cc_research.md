## sources/distributed-fs/ceph/src/rgw/rgw_object_lock.cc

Purpose: implements JSON/XML parsing and formatting for S3 Object Lock configuration, object retention, and legal hold.

Important APIs/functions: `DefaultRetention::decode_json()/decode_xml()/dump()/dump_xml()` handles retention mode and days/years. `ObjectLockRule` wraps default retention. `RGWObjectLock` parses bucket-level lock configuration, dumps it, computes lock-until date from object mtime, and generates test instances. `RGWObjectRetention` parses/dumps per-object retention. `RGWObjectLegalHold` parses/dumps status and reports enabled state.

Control flow: XML parsing enforces valid modes (`GOVERNANCE`/`COMPLIANCE`), exactly one of Days/Years, `ObjectLockEnabled == Enabled`, ISO-8601 retain-until dates, and legal hold status `ON`/`OFF`. Lock-until calculation adds days or years to mtime when a rule exists.

State and persistence: object lock structures are encoded in bucket/object attrs elsewhere. Retention dates use `ceph::real_time`, with round-trip encode support in the header.

Dependencies/integration: uses RGW XML/JSON decoders, Ceph ISO-8601 time helpers, and Formatter encoders.

Risks and test signals: date arithmetic uses `std::chrono::days/years`; leap-year/year semantics should be validated. XML validation is stricter than JSON decode for default retention. Tests should cover invalid modes, both/neither Days/Years, disabled/missing lock values, retain date parse failure, legal hold status, dump round trips, and lock-until date calculations.
