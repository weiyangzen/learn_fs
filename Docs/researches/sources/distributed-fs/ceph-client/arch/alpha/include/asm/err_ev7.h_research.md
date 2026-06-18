# Research: sources/distributed-fs/ceph-client/arch/alpha/include/asm/err_ev7.h

This header defines EV7 PAL logout-frame subpacket layouts. It includes structures for logout, processor, ZBOX, RBOX, IO, IO port, environmental subpackets, a union `ev7_pal_subpacket`, and `ev7_lf_subpackets` for collected pointers.

The only inline control-flow helper is `ev7_lf_env_index`, which validates environmental packet type with `BUG_ON` and converts PAL environmental type ids into a zero-based array index. Dependencies include common error-log type constants and `BUG_ON`.

State is decoded firmware/PAL logout data, including CPU, memory, routing, IO ASIC, environmental, and hot-plug condition fields. Integration is EV7/Marvel machine-check handling. Risks are binary layout fidelity, validating environmental type ranges before indexing, and interpreting multiple subpacket revisions. Tests are synthetic EV7 logout parsing and build coverage for machine-check handlers.
