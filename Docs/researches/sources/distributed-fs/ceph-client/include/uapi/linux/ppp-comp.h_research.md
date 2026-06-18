<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/ppp-comp.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/ppp-comp.h

Purpose: defines PPP Compression Control Protocol constants and option helpers for BSD-Compress, Deflate, MPPE, and legacy predictor options.

Important APIs and types: CCP packet macros read code, id, length, option code, and option length. BSD helpers encode version and code size (`BSD_NBITS`, `BSD_VERSION`, `BSD_MAKE_OPT`). Deflate helpers encode window size and method (`DEFLATE_SIZE`, `DEFLATE_METHOD`, `DEFLATE_MAKE_OPT`). Constants define option IDs and minimum/maximum bit/window sizes.

Control flow: PPP negotiation code parses CCP packets, validates option lengths, negotiates compression methods, and resets compression state using these codes. The header itself is macro-only.

State and persistence: compression state lives in PPP channel/session compressors and decompressors; negotiated options persist only for the link lifetime.

Dependencies and integration points: integrates with PPP core, pppd, kernel compression modules, MPPE support, and RFC CCP negotiation.

Risks and test signals: risks include accepting malformed CCP lengths, compression parameter mismatch between peers, unsupported MPPE expectations, and reset handling. Test PPP CCP negotiation for BSD/Deflate, invalid option lengths, reset request/ack, and pppd interoperability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/ppp-comp.h -->
