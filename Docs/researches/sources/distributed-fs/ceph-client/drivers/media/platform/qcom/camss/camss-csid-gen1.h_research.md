# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-csid-gen1.h

## sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-csid-gen1.h

Purpose: Defines CSID generation-1 decode and plain-format constants used by 4.1 and 4.7 hardware operation files.

Important APIs/types/functions: Provides `DECODE_FORMAT_*` constants for uncompressed and DPCM RAW encodings and `PLAIN_FORMAT_PLAIN8/PLAIN16`.

Control flow/state: No runtime state. Constants are compiled into CID configuration writes for legacy CSID hardware.

Dependencies/integration: Included by `camss-csid-4-1.c`, `camss-csid-4-7.c`, and common format tables in `camss-csid.c`.

Risks/test signals: Incorrect numeric constants cause hardware to decode CSI-2 payloads incorrectly. Test with RAW8/10/12/14 and YUV capture on Gen1 platforms, plus packed RAW10 source-code paths on 4.7.
