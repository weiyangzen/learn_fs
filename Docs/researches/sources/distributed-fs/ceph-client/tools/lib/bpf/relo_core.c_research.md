## sources/distributed-fs/ceph-client/tools/lib/bpf/relo_core.c

Purpose: Implements libbpf/kernel shared BPF CO-RE relocation logic. It parses `struct bpf_core_relo` access strings against local BTF, matches them against target BTF candidate types, computes relocation values, and patches BPF instructions.

Important APIs/functions: `bpf_core_parse_spec()` converts raw access strings into low-level and high-level `bpf_core_spec` forms. `bpf_core_calc_relo_insn()` is the main relocation resolver. `bpf_core_patch_insn()` mutates ALU, LDIMM64, LDX, ST, and STX instructions or poisons unreachable instructions. `__bpf_core_types_are_compat()` and `__bpf_core_types_match()` implement compatibility and exact-match relations. `bpf_core_format_spec()` creates diagnostic text.

Control flow: relocation starts by parsing the local spec, handling `TYPE_ID_LOCAL` specially, then iterating candidate target BTF types. Candidates are pruned to those matching by essential name and structural/accessor compatibility. Each matching candidate yields a candidate relocation result; all candidates must agree on offset and value to avoid ambiguity. Missing candidates may intentionally produce zero/existence false or poison-on-use depending on relocation kind.

State/persistence: No durable storage; it mutates candidate lists in memory and patches BPF instruction arrays. Scratch specs and result structs are caller-owned.

Dependencies/integration: Depends on BTF helpers, libbpf logging/error conventions, Linux BPF instruction encoding, CO-RE relocation enums, and endian behavior. Used by libbpf object loading and by kernel verifier-side code under `__KERNEL__`.

Risks: Candidate ambiguity, anonymous type rejection, too-deep access specs, bitfield layout uncertainty, unsafe memory-size adjustment, and poisoned instructions that only fail if reachable. A duplicated comment terminator is present before `bpf_core_patch_insn()` in this checkout and should be compile-tested.

Test signals: CO-RE selftests should cover field offsets/sizes, type existence/matches, enum64 values, anonymous types, flexible arrays, bitfields, 32-bit pointer-size adjustments, unsupported reloc kinds, and verifier rejection of reachable poisoned instructions.
