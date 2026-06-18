## sources/distributed-fs/seaweedfs/weed/s3api/stats.go

Purpose: wraps S3 HTTP handlers with metrics, server header injection, bucket activity tracking, and audit fallback logging.

Important APIs: `track`, `TimeToFirstByte`, `BucketTrafficReceived`, and `BucketTrafficSent`.

Control flow: `track` increments an in-flight gauge by action, extracts bucket/object, sets `Server`, wraps the response writer to capture status, installs audit and identity holder context, invokes the handler, blanks bucket labels on forbidden responses, records latency/counter/bucket activity, and emits fallback `PostLog` if the handler did not already audit. TTFB and traffic helpers update histograms/counters and active bucket time.

State and dependencies: metrics are stored in global stats collectors. Request context carries audit tracking and identity holder state. Dependencies include `s3_constants`, `s3err`, SeaweedFS version, and stats package.

Risks: fallback auditing relies on the handler seeing the same request object and setting the tracking flag; status defaults come from the status recorder. Tests cover direct `WriteHeader` fallback and no double-log behavior.
