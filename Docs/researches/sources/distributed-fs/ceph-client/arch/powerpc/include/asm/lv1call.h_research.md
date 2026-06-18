# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/lv1call.h

Purpose: declares the PlayStation 3 LV1 hypervisor call interface and generates typed wrappers for many argument-count combinations.

Important APIs/types/functions: macro families `LV1_*_IN_ARG_DECL`, `LV1_*_OUT_ARG_DECL`, `LV1_*_IN_*_OUT_ARG_DECL`, and corresponding argument lists generate function signatures. `LV1_CALL(name, in, out, num)` creates a public wrapper and underscored low-level hypercall declaration, with optional instrumentation point. The file also declares numerous PS3 LV1 calls through those macros.

Control flow: callers invoke a typed `lv1_*` wrapper; it forwards fixed register-style arguments and output pointers to the low-level hypervisor call implementation. Return values are hypervisor status codes and outputs are written through pointer arguments.

State and persistence: this header stores no state. LV1 calls manipulate PS3 hypervisor state such as logical partitions, devices, repository entries, memory mappings, interrupts, and storage resources in implementation/hardware.

Dependencies and integration points: depends on `linux/types.h`, export support, and PS3 platform code. It is the ABI bridge between Linux PS3 drivers and the LV1 hypervisor.

Risks: generated signatures must match the hypervisor ABI exactly; argument count or ordering mistakes corrupt register convention. Output pointers must be valid and checked by callers. Hypercalls can have system-wide resource effects.

Test signals: build PS3 platform support, run PS3 device discovery and storage/network drivers, validate representative LV1 calls return expected status codes, and check wrapper symbol exports.
