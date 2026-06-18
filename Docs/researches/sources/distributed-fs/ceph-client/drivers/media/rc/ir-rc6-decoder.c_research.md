# sources/distributed-fs/ceph-client/drivers/media/rc/ir-rc6-decoder.c

Purpose: generic raw decoder and encoder for RC6 mode 0 and RC6-6A variants, including MCE, Zotac, and Kathrein customer-code handling.

Important APIs, types, and functions: constants define RC6 units, header/body lengths, prefix, toggle, suffix, mode masks, and customer-code masks. `rc6_mode()` classifies header mode. `ir_rc6_decode()` parses prefix, header, double-width toggle, variable body, and suffix; it emits `RC_PROTO_RC6_0`, `RC_PROTO_RC6_6A_20`, `RC_PROTO_RC6_6A_24`, `RC_PROTO_RC6_6A_32`, or `RC_PROTO_RC6_MCE`. MCE-style 32-bit customer codes clear the body toggle bit from the scancode and emit it as toggle. `ir_rc6_encode()` generates Manchester segments for mode 0 or mode 6A variants. `rc6_handler` registers all supported protocol bits.

Control flow: after prefix pulse/space, the decoder reads four header bits, a double-width toggle bit, chooses wanted body length (`16` for mode 0 or up to 128 for 6A), reads body bits until fixed length or suffix space, then validates and emits according to mode and body bit count. Encoding writes header, trailer/toggle bit, and body through timing descriptor segments.

State and persistence behavior: per-device state stores decode state, header, body, count, wanted bits, and toggle. The 32-bit body is bounded by `sizeof data->body`; longer 6A captures are rejected.

Dependencies and integration points: depends on rc-core raw helpers, Manchester generator, enabled protocol handling by rc-core, and input event consumers for MCE remotes. It is the primary software path for RC6 variants beyond the ImgTec hardware's limited RC6-0 descriptor.

Risks and edge cases: variable-length 6A support stops on suffix space and rejects bodies too large for `u32`. Customer-code classification changes protocol and toggle semantics for certain 32-bit values. First-pulse margin is wider than later units to tolerate receiver settling. Encoder does not synthesize MCE body toggle logic beyond using the provided scancode.

Test signals: decode/encode RC6-0, 6A-20/24/32, MCE customer codes, toggle extraction, unknown mode rejection, long 6A body rejection, and suffix timing variations.
