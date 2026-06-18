# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/disasm.h

Purpose: public interface for BPF instruction disassembly.

Important APIs and types: exports `bpf_alu_string`, `bpf_class_string`, `func_id_name()`, callback typedefs `bpf_insn_print_t`, `bpf_insn_revmap_call_t`, `bpf_insn_print_imm_t`, `struct bpf_insn_cbs`, and `print_bpf_insn()`.

Control flow: header only.

State and persistence: no state in the header.

Dependencies and integration points: includes BPF UAPI and kernel/stringify helpers; also includes stdio/string outside kernel builds.

Risks: callbacks must be valid for the duration of printing; `allow_ptr_leaks` policy is enforced by implementation, not type system.

Test signals: consumers compile against the callbacks and can capture disassembly output.
