# sources/distributed-fs/ceph-client/tools/perf/util/intel-pt-decoder/intel-pt-pkt-decoder.c

Purpose: low-level Intel PT packet decoder. It parses raw bytes into `struct intel_pt_pkt` records, maintains minimal block-packet context, and formats packet descriptions for logs.

Important APIs and types: exports `intel_pt_pkt_name()`, `intel_pt_get_packet()`, `intel_pt_upd_pkt_ctx()`, and `intel_pt_pkt_desc()`. Static helpers parse long/short TNT, IP packets, CYC, PIP, TSC, TMA, MODE, MTC, VMCS, PSB/PSBEND, CBR, OVF, MNT, PTWRITE, EXSTOP, MWAIT/PWRE/PWRX, BBP/BIP/BEP, CFE, and EVD packets.

Control flow: `intel_pt_get_packet()` calls `intel_pt_do_get_packet()` using the current context. If a packet is decoded, it absorbs trailing PAD bytes up to eight bytes, then updates context. In block context, byte patterns with low bits matching BIP are decoded as 4- or 8-byte BIP instead of TNT. Description formatting switches by packet type to produce human-readable payload details.

State and persistence: the decoder itself is stateless except for the caller-owned `enum intel_pt_pkt_ctx`, which tracks whether BIP packets are valid between BBP and BEP. Parsed packet data is returned in caller-owned storage.

Dependencies and integration: uses Linux unaligned helpers, endian conversion, compiler fallthrough, and constants from the header. The main PT decoder uses it for every packet and the log layer uses descriptions.

Risks: packet length/count handling is security-sensitive because input is trace data. Need-more-bytes and bad-packet distinctions drive resync behavior. Context mistakes can misclassify BIP as TNT. Some payload extraction uses partial little-endian copies, so big-endian behavior depends on helper correctness.

Test signals: byte fixtures for every packet type, boundary lengths returning `INTEL_PT_NEED_MORE_BYTES`, malformed encodings returning `INTEL_PT_BAD_PACKET`, BBP/BIP/BEP context transitions, trailing PAD absorption, and description string checks.
