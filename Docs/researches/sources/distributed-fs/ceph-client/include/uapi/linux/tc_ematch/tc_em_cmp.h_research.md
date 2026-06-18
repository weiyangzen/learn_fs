# sources/distributed-fs/ceph-client/include/uapi/linux/tc_ematch/tc_em_cmp.h

## Purpose
Defines the TC extended match compare ABI for matching packet bytes against masked values.

## Important APIs, Types, and Constants
`struct tcf_em_cmp` carries comparison `val`, `mask`, offset, alignment, flags, layer, and operand in bitfields. Alignment constants are `TCF_EM_ALIGN_U8`, `TCF_EM_ALIGN_U16`, and `TCF_EM_ALIGN_U32`; `TCF_EM_CMP_TRANS` flags transformed comparison.

## Control Flow, State, and Persistence
Userspace encodes match criteria in classifier netlink data. Runtime ematch reads packet data at the specified layer/offset, applies alignment/mask/operator logic, and returns match result.

## Dependencies and Integration Points
Depends on `<linux/types.h>` and `<linux/pkt_cls.h>`. Integrates with TC ematch/classifier framework.

## Risks and Test Signals
Risks include bitfield layout assumptions, out-of-bounds offsets, and endian/alignment confusion. Test u8/u16/u32 matches, transformed flag, layer offsets, and malformed packet handling.
