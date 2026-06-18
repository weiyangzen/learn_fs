<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/pdb.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/caam/pdb.h

Purpose: defines CAAM Protocol Data Block layouts and option bits for hardware protocol descriptors, including IPsec ESP, WiFi, WiMAX, MACsec, TLS/DTLS/SSL, SRTP, DSA/ECDSA, and RSA.

Important APIs and control flow: the header is layout-only. It defines PDB option masks for ESP header manipulation, anti-replay, IV source, ESN, checksum, tunnel/header handling, protocol-specific structs for encapsulation/decapsulation variants, DECO override layout, TLS/DTLS sequence/IV structures, SRTP salt/ROC/anti-replay fields, DSA/ECDSA scatter-gather and length bits, RSA public/private key form selectors, RSA PDB structs, and `SIZEOF_RSA_*_PDB` macros that depend on runtime `caam_ptr_sz`.

State and persistence behavior: none directly; these structures are copied into descriptors or used to append descriptor PDB fields. Some PDBs contain DECO writeback regions such as sequence numbers or anti-replay scorecards, so caller-owned buffers may be modified by hardware.

Dependencies and integration points: consumed by protocol crypto modules and `pkc_desc.c`; depends on DMA address sizes and CAAM descriptor pointer width. RSA size macros integrate with descriptor PDB initialization helpers.

Risks and test signals: risks include C structure padding/endian mismatches with hardware PDB format, flexible IP header sizing mistakes, runtime pointer-size-dependent PDB length errors, typo/documentation drift in RSA CRT comments, and caller responsibility for DMA-safe/writeback buffers. Test signals include IPsec/TLS/SRTP/MACsec/WiFi protocol known-answer tests, RSA public/private form descriptors accepted by hardware, anti-replay/writeback state updates, and descriptor length checks in 32-bit and 64-bit pointer modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/pdb.h -->
