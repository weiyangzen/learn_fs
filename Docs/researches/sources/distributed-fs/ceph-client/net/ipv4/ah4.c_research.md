# sources/distributed-fs/ceph-client/net/ipv4/ah4.c

## Purpose
`ah4.c` implements the IPv4 IPsec Authentication Header transform for XFRM. It authenticates immutable IPv4 header fields and payload, handles extended sequence numbers, registers AH as an IPv4 XFRM type/protocol, and processes ICMP errors relevant to AH state.

## Important APIs, types, and functions
Key internal helpers include `ah_alloc_tmp()`, `ah_tmp_auth()`, `ah_tmp_icv()`, `ah_tmp_req()`, `ah_req_sg()`, and `ip_clear_mutable_options()`. Transform entry points are `ah_output()`, `ah_output_done()`, `ah_input()`, `ah_input_done()`, `ah4_err()`, `ah_init_state()`, `ah_destroy()`, and `ah4_rcv_cb()`. Registration objects are `ah_type` and `ah4_protocol`, installed by `ah4_init()` and removed by `ah4_fini()`.

## Control flow
Outbound processing makes skb data writable, pushes to the network header, saves mutable header fields/options, clears fields excluded from AH ICV, fills AH header fields including SPI and sequence number, optionally appends ESN high bits to the scatterlist, computes the ahash digest, writes the truncated ICV, restores header fields, and resumes XFRM output. Inbound processing validates AH header length against full or truncated ICV size, unshares the skb, copies the original IP header and received auth data into temporary storage, clears mutable fields, includes ESN high bits when configured, computes and compares the ICV with `crypto_memneq()`, removes the AH header, restores the IP header, updates transport header placement, and returns the next header. Async crypto completions mirror the synchronous completion steps and resume XFRM input/output.

## State and persistence
Per-XFRM-state AH data is stored in `struct ah_data` attached to `x->data`, including the crypto ahash handle and ICV lengths. Temporary per-packet state is stored in `AH_SKB_CB(skb)->tmp`. No persistent storage exists beyond runtime XFRM state.

## Dependencies and integration points
The file depends on the crypto ahash API, XFRM state/type/protocol registration, IPv4 header and options helpers, scatterlist conversion from skbs, ICMP PMTU/redirect handling, PF_KEY algorithm descriptions, and module aliasing for `XFRM_PROTO_AH`.

## Risks and invariants
AH requires an auth algorithm and rejects encapsulation. Mutable IPv4 options must be zeroed exactly as AH expects while immutable options remain covered; mistakes break interoperability or authentication. Header length and alignment differ for `XFRM_STATE_ALIGN4` and default align8 modes. Temporary storage allocation uses `GFP_ATOMIC`, so packet processing can fail under pressure. ESN high bits must be hashed in the correct byte order and position.

## Test signals
Tests should create IPv4 AH XFRM states with supported auth algorithms, verify outbound AH packets and inbound validation, exercise truncated/full ICV lengths, tunnel and transport modes, ESN, IPv4 options including source route/CIPSO/router alert, async crypto completion, ICMP fragmentation-needed PMTU updates, redirect handling, and module load/unload registration paths.
