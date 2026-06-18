# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-csid-gen2.h

## sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-csid-gen2.h

Purpose: Defines Gen2 CSID decode, encode, and plain-format constants used by Gen2, 340, and 680 CSID operation files.

Important APIs/types/functions: Includes uncompressed 6/8/10/12/14/16/20-bit decode constants, DPCM decode constants, user-defined and payload-only constants, RAW encode constants for TPG, and `PLAIN_FORMAT_PLAIN8/16/32`.

Control flow/state: No runtime state. Values are written into RDI and TPG configuration bitfields.

Dependencies/integration: Included by `camss-csid-gen2.c`, `camss-csid-340.c`, `camss-csid-680.c`, and format metadata in `camss-csid.c`.

Risks/test signals: Constant drift breaks data interpretation across SoCs. Test with RAW/YUV formats and TPG encode modes on Gen2-derived hardware.
