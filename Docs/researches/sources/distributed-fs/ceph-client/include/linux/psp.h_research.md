# sources/distributed-fs/ceph-client/include/linux/psp.h

Purpose: provides common AMD PSP mailbox bit definitions and physical-address conversion used by PSP-related subsystems.

Important APIs and types: `__psp_pa(x)` maps to `__sme_pa()` on x86 to account for SME memory encryption and to `__pa()` elsewhere. Bit masks define common command-response status, command, reserved, recovery, response, doorbell message, and ring bits, plus the TEE ring-busy status code.

Control flow: PSP clients construct mailbox command/response words using these masks and translate kernel virtual buffers to physical addresses with the correct encryption semantics before firmware access.

State and persistence: no state is stored. The definitions describe hardware register fields and address translation behavior.

Dependencies and integration points: depends on x86 memory encryption when applicable and generic physical address helpers. Used by PSP SEV, TEE, and platform-access code.

Risks and test signals: risks include using raw `__pa()` on encrypted x86 memory, interpreting command-response bits incorrectly for mailbox variants, and recovery bit mishandling. Test encrypted-memory platforms, mailbox command status decoding, and non-x86 builds.
