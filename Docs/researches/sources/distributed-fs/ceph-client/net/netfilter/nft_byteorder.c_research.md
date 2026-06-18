# sources/distributed-fs/ceph-client/net/netfilter/nft_byteorder.c

## Purpose
`nft_byteorder.c` implements the nftables `byteorder` expression, converting register data between network byte order and host byte order for arrays of 16-bit, 32-bit, or 64-bit values.

## Important APIs, Types, and Functions
Private state is `struct nft_byteorder`, containing source/destination registers, operation (`NFT_BYTEORDER_NTOH` or `NFT_BYTEORDER_HTON`), total byte length, and element size. The evaluator is `nft_byteorder_eval()`. Netlink setup and dump are `nft_byteorder_init()` and `nft_byteorder_dump()`. Registration is through `struct nft_expr_type nft_byteorder_type`.

## Control Flow, State, and Persistence
Initialization requires all attributes: source register, destination register, operation, length, and element size. It accepts only NTOH/HTON operations and element sizes of 2, 4, or 8 bytes. Register validation uses `nft_parse_register_load()` and `nft_parse_register_store()` for the full requested length.

Evaluation casts the selected register window to u16/u32/u64 views depending on element size. For 64-bit elements it uses `nft_reg_load64()` and `nft_reg_store64()` so nft register layout is respected. For 32-bit and 16-bit elements it loops over `len / size` elements and applies `ntohl`/`htonl` or `ntohs`/`htons`. There is no offload support in this file.

State is entirely expression-private and immutable after rule creation. Dump emits the original register ids, operation, length, and element size.

## Dependencies and Integration Points
The expression depends on nftables register parsing/dumping and Linux byteorder helpers. It is called from the generic interpreter, including direct retpoline-bypass dispatch in `nf_tables_core.c`.

## Risks and Test Signals
Risks include lengths that are not multiples of element size silently leaving tail bytes untouched, register overlap between source and destination, 64-bit register layout correctness, and invalid netlink attributes. Tests should cover 16/32/64-bit NTOH and HTON arrays, in-place conversion, non-multiple lengths if userspace can create them, invalid size/op rejection, dump round-trip, and mixed endian hosts.
