<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_sosapi.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_sosapi.go

Purpose: implements Smart Object Storage API virtual objects for backup software discovery. It synthesizes `.system-.../system.xml` and `.system-.../capacity.xml` inside buckets without requiring physical objects.

Important APIs/types/functions: constants define the SOSAPI system folder, XML object names, client user-agent marker, protocol version, and recommended block size. `SystemInfo`, `APIEndpoints`, `SystemRecommendations`, and `CapacityInfo` model XML payloads. `isSOSAPIObject`, `generateSystemXML`, `generateCapacityXML`, `getCapacityInfo`, `collectBucketUsageFromTopology`, `calculateClusterCapacity`, `handleSOSAPIGetObject`, `handleSOSAPIHeadObject`, and `generateSOSAPIContent` implement discovery and response generation.

Control flow: GET/HEAD handlers first check whether the object path is one of the SOSAPI virtual objects. Content generation verifies bucket existence through `getBucketConfig`, then either emits static system capability XML or asks masters for topology and quota-derived capacity. GET responses compute MD5 ETags, set XML content type, and use `http.ServeContent` for range/content metadata; HEAD emits headers and status without a body.

State and persistence behavior: virtual XML is generated on demand and not persisted. Capacity uses bucket quota from filer entry metadata when available, otherwise master topology disk/volume information. Bucket usage is approximated by summing unique volume sizes in the bucket collection.

Dependencies and integration: depends on S3 bucket config/entry helpers, filer errors, master `VolumeList`, SeaweedFS version metadata, S3 error writers, and protobuf topology structures. It is intended to be called from object HEAD/GET handlers before normal object lookup.

Risks: capacity is only as accurate as master topology and volume collection mapping; shared volumes, stale topology, or missing masters produce zero/default capacity. `time.Now()` is used for Last-Modified/ServeContent, so caches may see changing validators for identical XML. `ModelName` and protocol version include quoted string values, which appears spec-driven but is easy to regress. The user-agent constant is defined here but detection is not in this file.

Test signals: valuable tests would cover virtual path detection, XML schema fields, bucket-not-found mapping to `NoSuchBucket`, quota-vs-cluster capacity choice, duplicate volume ID suppression, HEAD header correctness, and GET range behavior through `ServeContent`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_sosapi.go -->
