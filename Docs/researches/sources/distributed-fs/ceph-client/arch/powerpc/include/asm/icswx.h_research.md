# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/icswx.h

Purpose: Defines the PowerPC ICSWX coprocessor interface, request-block layout, status bits, and inline instruction wrappers.

Important APIs, types, and functions: Declares request/status flags, `struct coprocessor_request_block`, `struct coprocessor_status_block`, `struct vas_window`, and inline `icswx()`-style assembly helpers that execute the instruction and return condition/status information.

Control flow: Accelerator/VAS users prepare a request block and status block, issue the ICSWX instruction against a window/context, then inspect status/error bits for completion or fault handling.

State and persistence: Request and status blocks are caller-owned memory. Accelerator/window state is maintained by hardware and VAS/coproc subsystems.

Dependencies and integration points: Integrates with VAS/NX/coprocessor drivers, PowerPC inline assembly, and endian/alignment-sensitive hardware block formats.

Risks: Request block alignment and reserved fields must match hardware. Inline assembly clobbers and condition handling are ABI-sensitive. Fault/status interpretation must distinguish retryable and fatal accelerator errors.

Test signals: Successful ICSWX submission, invalid window/context faults, status-block error decoding, alignment failures, concurrent submissions, and accelerator reset/error recovery.
