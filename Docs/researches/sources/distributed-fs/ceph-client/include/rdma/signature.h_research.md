# sources/distributed-fs/ceph-client/include/rdma/signature.h

Purpose: Provides RDMA signature/T10-DIF capability and attribute types for protection information handover between memory and wire domains.

Important APIs/types/functions: Capability enums advertise T10 DIF types and guard algorithms. `struct ib_t10_dif_domain` describes DIF interval, guard seed/type, application tag, reference tag, remap and escape behavior, and check mask. `struct ib_sig_domain` wraps the signature type, `struct ib_sig_attrs` describes memory and wire domains plus check mask and metadata length, and `struct ib_sig_err` reports guard/ref/app tag failures.

Control flow and state: This header carries configuration only; providers consume attributes when building registered MRs or signature RDMA operations. Error records identify the failed field, expected/actual values, offset, and key.

Dependencies and integration: Used by RDMA verbs providers and `rdma_rw_ctx_signature_init()`. It aligns with T10 PI/DIF and storage transports that need end-to-end data protection.

Risks and test signals: Main risks are mismatched memory/wire domains, incorrect interval or tag remap semantics, and incomplete check masks. Test signals include guard CRC and checksum cases, type 1/2/3 DIF, reference tag rollover/remap, escape tag behavior, and injected signature errors.
