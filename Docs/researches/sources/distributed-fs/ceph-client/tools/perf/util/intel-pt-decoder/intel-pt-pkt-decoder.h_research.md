# sources/distributed-fs/ceph-client/tools/perf/util/intel-pt-decoder/intel-pt-pkt-decoder.h

Purpose: public packet-level Intel PT decoder interface and raw packet constants.

Important APIs and types: defines description and packet size limits, error return values `INTEL_PT_NEED_MORE_BYTES` and `INTEL_PT_BAD_PACKET`, PSB byte string/length, VMX NR flag, `enum intel_pt_pkt_type`, `struct intel_pt_pkt`, and `enum intel_pt_pkt_ctx`. Declares packet name, decode, context update, and description functions.

Control flow: callers maintain a packet context, pass a byte buffer to `intel_pt_get_packet()`, advance by the positive returned length, and feed the same context back for later packets. `intel_pt_upd_pkt_ctx()` is exposed for users that need to update context manually.

State and persistence: no global state. The packet context is the only cross-call state and exists to disambiguate BIP encodings while inside block payloads.

Dependencies and integration: consumed by `intel-pt-decoder.c` and `intel-pt-log.c`. It is deliberately independent of perf session structures.

Risks: enum values are used in large switch statements across the decoder and logger, so additions require exhaustive updates. Callers must treat negative returns as non-lengths and must not advance incorrectly on partial packets.

Test signals: header compile tests, exhaustive switch warnings when adding packet types, and packet stream tests that verify caller context is preserved across BBP/BIP/BEP sequences.
