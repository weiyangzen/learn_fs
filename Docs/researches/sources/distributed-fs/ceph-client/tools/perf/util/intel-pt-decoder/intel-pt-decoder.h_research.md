# sources/distributed-fs/ceph-client/tools/perf/util/intel-pt-decoder/intel-pt-decoder.h

Purpose: public contract for the Intel PT decoder. It defines sample types, error codes, parameter callbacks, decoded state layout, PT block item storage, VMCS timing metadata, and public decoder functions.

Important APIs and types: `enum intel_pt_sample_type`, `enum intel_pt_period_type`, error enums, `enum intel_pt_param_flags`, block type enums and `intel_pt_blk_type_pos()`, `struct intel_pt_blk_items`, `struct intel_pt_vmcs_info`, `struct intel_pt_evd`, `struct intel_pt_state`, `struct intel_pt_buffer`, `struct intel_pt_params`, and opaque `struct intel_pt_decoder`. Function declarations cover lifecycle, decode, fast-forward, overlap detection, error text, and first timestamp.

Control flow: callers fill `intel_pt_params` with `get_trace`, `walk_insn`, optional `pgd_ip`, `lookahead`, and `findnew_vmcs_info` callbacks plus configuration flags. They repeatedly call `intel_pt_decode()` and consume the returned stable pointer until an error/no-data state is reported.

State and persistence: `intel_pt_state` is the per-sample output and is owned by the decoder until the next decode call. `intel_pt_vmcs_info` nodes are stored by the caller, typically in an rb-tree, and carry learned VMCS TSC offsets.

Dependencies and integration: includes Linux rbtree and the PT instruction decoder. It is consumed by perf Intel PT auxtrace integration and, indirectly, by tooling that needs branch/instruction synthesis.

Risks: flags overlap intentionally (`INTEL_PT_IFLAG` and `INTEL_PT_ASYNC` both use bit 2 in different contexts), so consumers must interpret them by sample type. Struct layout is broad and easy to misuse if fields are read without checking `type` bits.

Test signals: compile/API tests, decode consumer tests that validate state fields for each sample type, VMCS info storage tests, and ABI review before changing enum values or struct semantics.
