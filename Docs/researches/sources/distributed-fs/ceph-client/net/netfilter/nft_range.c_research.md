
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_range.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nft_range.c

## Purpose

`nft_range.c` implements the nftables `range` expression. It compares register data against an inclusive byte range and either accepts values inside the range (`NFT_RANGE_EQ`) or outside the range (`NFT_RANGE_NEQ`) by breaking evaluation on mismatch.

## Important APIs, Types, and Functions

`struct nft_range_expr` stores `data_from`, `data_to`, source register, data length, and operation. `nft_range_eval()` performs two `memcmp()` comparisons against the register bytes. `nft_range_init()` parses nested nft data values, validates matching lengths, validates register load size, and accepts only EQ/NEQ operations. `nft_range_dump()` serializes the expression.

## Control Flow

Initialization requires all range attributes. It initializes the lower bound first, then the upper bound, releases already-initialized data on later errors, and stores the common length. Evaluation compares register bytes to both endpoints. EQ breaks when the register value is below `from` or above `to`; NEQ breaks when the value is inside the inclusive range.

## State and Persistence Behavior

All persistent state is immutable expression configuration after rule creation. There is no dynamic per-packet state except reads from registers and possible `NFT_BREAK` in the verdict register.

## Dependencies and Integration Points

The file depends on nf_tables core data parsing, register validation, and netlink nested data attributes. It is a generic expression module independent of protocol families; callers normally pair it with payload/meta/rt/socket expressions that populate registers.

## Risks and Test Signals

Risks are mostly semantic: `memcmp()` gives network-byte-order lexicographic comparison, so producers must load values in the intended byte order and length. Bounds with mismatched lengths are rejected. Test exact lower/upper boundary matches, one-byte and multi-register ranges, NEQ inversion, missing attributes, and register length validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_range.c -->
