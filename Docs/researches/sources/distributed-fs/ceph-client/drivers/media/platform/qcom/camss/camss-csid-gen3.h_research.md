# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-csid-gen3.h

## sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-csid-gen3.h

Purpose: Defines decode and plain-format constants for Titan Gen3 CSID hardware.

Important APIs/types/functions: Provides `DECODE_FORMAT_UNCOMPRESSED_8/10/12/14/16/20/24_BIT`, `DECODE_FORMAT_PAYLOAD_ONLY`, and plain-format constants.

Control flow/state: No runtime state. Gen3 stream programming uses these values in RDI decode-format fields.

Dependencies/integration: Included by `camss-csid-gen3.c`; values must match hardware documentation and common CSID format tables.

Risks/test signals: Wrong constants produce corrupted frame payload interpretation. Test RAW8 through RAW24-capable paths and payload-only RDI streaming.
