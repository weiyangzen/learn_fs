# sources/distributed-fs/ceph/src/rgw/rgw_cksum_pipe.h

Purpose: declares checksum-header discovery helpers and the put-object checksum data-processing pipe.

Important APIs/types/functions: `cksum_hdr_t`, `cksum_algorithm_hdr(Type)`, `cksum_algorithm_hdr(const RGWEnv&)`, `multipart_cksum_algo()`, `get_hdr_cksum()`, `find_hdr_cksum()`, `parse_cksum_flags()`, and class `RGWPutObj_Cksum`.

Control flow: header discovery honors AWS precedence: individual checksum algorithm header before SDK algorithm header, trailers, then concrete checksum value headers. `get_hdr_cksum()` uses the selected algorithm to read `HTTP_X_AMZ_CHECKSUM_<ALG>`. `find_hdr_cksum()` scans value headers for CompleteMultipartUpload-style requests without algorithm header. `parse_cksum_flags()` maps `x-amz-checksum-type` to full-object or composite, otherwise defaults by algorithm family.

State/persistence: helpers inspect request env only. `RGWPutObj_Cksum` state includes digest variant and finalized `Cksum`; persistence happens in object metadata outside this class.

Dependencies/integration: `rgw_putobj` pipe, `RGWEnv`, `rgw_cksum`, digest factory, Ceph split, and AWS checksum request semantics.

Risks: `get_hdr_cksum()` and `find_hdr_cksum()` declare `cksum_type` without initializing before no-header return paths. Trailer parsing returns the first recognized checksum type. The `xxh3` SDK header string is `"XX3"`, likely suspicious. Verify requires both header key and expected value.

Test signals: AWS precedence cases, trailer checksum algorithm detection, uninitialized no-header paths under sanitizers, CompleteMultipartUpload checksum scan including crc64nvme coverage, checksum-type defaults, and malformed header rejection.
