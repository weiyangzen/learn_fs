# sources/distributed-fs/ceph-client/tools/perf/arch/x86/util/cpuid.h

Purpose: This header provides a small x86 CPUID wrapper for perf's user-space arch code. It preserves the ABI-sensitive EBX/RBX register while exposing CPUID leaf/subleaf results through output pointers.

Important APIs, types, and functions: `cpuid(unsigned int op, unsigned int op2, unsigned int *a, unsigned int *b, unsigned int *c, unsigned int *d)` is a static inline helper. It declares output constraints for EAX, EDI-as-saved-EBX, ECX, and EDX, with inputs in EAX and ECX. `get_cpuid_0(char *vendor, unsigned int *lvl)` is declared for the implementation in `header.c`.

Control flow: On x86-64, inline assembly moves `%rbx` to `%rdi`, executes `cpuid`, then exchanges `%rdi` and `%rbx` so the CPUID EBX result is captured through the `=D` output while RBX is restored. On 32-bit, it pushes `%ebx`, executes `cpuid`, moves `%ebx` into `%edi`, then pops the saved `%ebx`.

State and persistence: The helper has no persistent state. Its state contract is register preservation, especially for PIC/GOT usage and dynamic alloca cases where RBX may be important to the compiler.

Dependencies and integration points: It is included by x86 perf utility and test code such as `header.c`, `intel-pt-test.c`, and TSC-related utilities. The wrapper supports `get_cpuid()`, PMU event matching, Intel PT capability checks, and CPU vendor/family/model extraction.

Risks: Inline assembly constraints are delicate. Breaking RBX preservation can corrupt position-independent code or compiler-generated stack addressing. The helper assumes x86 CPUID availability and is only suitable for x86 arch builds.

Test signals: CPUID-dependent tests and features should produce stable vendor, family, model, and feature data. Failures in PMU event matching, Intel PT hybrid checks, or crashes under PIC builds can indicate wrapper regressions.
