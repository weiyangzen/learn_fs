# sources/distributed-fs/ceph-client/arch/x86/coco/sev/vc-shared.c

## Purpose
Shared SEV-ES #VC emulation code included by both normal kernel and early/compressed contexts. It validates intercepted opcode bytes, initializes/finishes emulation contexts, handles port I/O, verifies GHCB exception information, performs GHCB hypervisor calls, handles CPUID/RDTSC, registers GHCBs, and negotiates GHCB protocol.

## Important APIs, Types, And Functions
Key functions are `vc_check_opcode_bytes()`, `vc_init_em_ctxt()`, `vc_finish_insn()`, `vc_ioio_exitinfo()`, `vc_handle_ioio()`, `verify_exception_info()`, `sev_es_ghcb_hv_call()`, `vc_handle_cpuid()`, `vc_handle_rdtsc()`, `snp_register_ghcb_early()`, `sev_es_check_cpu_features()`, and `sev_es_negotiate_protocol()`. The file relies on includer-provided `vc_decode_insn()`, `vc_read_mem()`, `vc_write_mem()`, `vc_ioio_check()`, `sev_printk`, and feature macros.

## Control Flow And State
For decode-required exits, the shared code decodes the instruction and checks that opcode bytes match the hardware-reported exit code. Port I/O builds GHCB exit-info fields for scalar and string I/O, chunks repeated string operations through the GHCB shared buffer, updates RSI/RDI/RCX according to direction and REP, and returns `ES_RETRY` until complete. GHCB calls populate protocol metadata and exit fields, execute VMGEXIT, then interpret `sw_exit_info_1/2` as success, forwarded #GP/#UD, or VMM error. CPUID uses SNP CPUID tables first, falling back to GHCB CPUID with XCR0/XSS inputs; RDTSC/RDTSCP are rejected under Secure TSC.

## Dependencies And Integration
Included by `vc-handle.c` and boot/compressed SEV code. It depends on GHCB field accessors, SVM exit-code definitions, x86 instruction decoder, SNP CPUID validation, native MSR/VMGEXIT primitives, and exception metadata formats.

## Risks And Test Signals
Risks include opcode/exit mismatches, IOIO bitfield errors, off-by-one REP string state, trusting invalid GHCB output-valid bits, CPUID hypervisor fallback bypassing SNP policy, and GHCB protocol version negotiation failures. Signals include SEV-ES early and runtime boot, port I/O console tests, CPUID conformance, GHCB registration under SNP, Secure TSC intercept tests, and negative VMM response tests.
