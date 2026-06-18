# sources/distributed-fs/ceph-client/arch/arm64/lib/copy_to_user.S

Purpose: implements `__arch_copy_to_user`, copying bytes from kernel memory into a user destination and returning bytes not copied.

Important APIs/types/functions: `__arch_copy_to_user`, kernel load macros, user store macros, MOPS `cpyfpwt/cpyfmwt/cpyfewt`, included `copy_template.S`, and exception fixup labels.

Control flow: initializes end and original source, runs the shared copy template with kernel loads and user stores, and returns zero on success. Fault handlers adjust `dst` from MOPS residual state, retry a first-byte store when no progress occurred, then return `end - dst`.

State and persistence: writes copied bytes to user memory. It does not persist kernel state and may leave a partial user write on fault.

Dependencies/integration: used by raw copy-to-user; depends on exception-table uaccess annotations, `copy_template.S`, and ARM64 MOPS alternatives.

Risks: residual accounting and fault-side discrimination are critical because user-visible copy APIs depend on exact remaining bytes. The final retry must not mask kernel-source faults. Store-side faults must be represented as uaccess write faults in extable metadata.

Test signals: valid and faulting user destinations, page-boundary residual counts, no-progress first-byte fault, all alignments/tail sizes, MOPS vs generic path, and hardened usercopy coverage.
