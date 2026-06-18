# sources/distributed-fs/ceph-client/drivers/crypto/bcm/spu2.h

Purpose: SPU2-specific hardware message definition header. It defines SPU2 cipher/hash numeric encodings, FMD layout, FMD control-word masks, response status constants, and public prototypes for the SPU2 backend.

Important APIs and types: `enum spu2_cipher_type`, `spu2_cipher_mode`, `spu2_hash_type`, `spu2_hash_mode`, and `spu2_ret_md_opts`; `struct SPU2_FMD` with four little-endian 64-bit control words; constants `FMD_SIZE`, `SPU2_REQ_FIXED_LEN`, `SPU2_HEADER_ALLOC_LEN`, `SPU2_MAX_PAYLOAD`, `SPU2_INVALID_ICV`; masks for ctrl0 cipher/hash/protocol/order, ctrl1 key/IV/tag/return fields, ctrl2 AAD/payload offsets, and ctrl3 payload/TLS length.

Control flow: `spu2.c` writes these masks into FMD ctrl words, appends OMD after the FMD, and later decodes response FMD/status according to these definitions.

State and persistence: no runtime state. This file defines binary ABI expectations between driver memory and SPU2 hardware.

Dependencies and integration points: depends on common SPU enums and MAX key/IV sizes from surrounding Broadcom headers. It is included by SPU2 implementation and indirectly by the common driver dispatch code.

Risks: mask widths and shifts are hardware-contract critical; many fields exceed 32 bits and require 64-bit constants and casts; `SPU2_RET_IV_LEN` uses zero to mean 16 bytes; `SPU2_HEADER_ALLOC_LEN` references the generic request fixed length, so allocation assumptions must match both SPU families.

Test signals: compile tests for 64-bit mask use, request header dumps for FMD ctrl fields, invalid ICV mapping, and hardware/crypto selftests that exercise returned metadata, IV, AAD2, and payload flags.
