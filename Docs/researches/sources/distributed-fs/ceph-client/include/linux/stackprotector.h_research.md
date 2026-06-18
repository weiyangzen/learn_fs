<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/stackprotector.h -->
# sources/distributed-fs/ceph-client/include/linux/stackprotector.h

Purpose: Defines stack canary generation policy and boot-time stack protector initialization hook.

Important APIs/types/functions: `CANARY_MASK`, `get_random_canary()`, and `boot_init_stack_canary()`.

Control flow: `get_random_canary()` masks `get_random_long()` so 64-bit canaries include a zero byte to limit unterminated string overflow attacks. If stack protector or ARM64 pointer authentication is enabled, architecture code supplies `boot_init_stack_canary()`; otherwise it is a no-op.

State and persistence behavior: Generated canaries seed per-task or per-CPU stack protector state in architecture code; this header only defines the random generation helper and mask.

Dependencies: Compiler definitions, scheduler, random number generation, endian/word-size config, and optional `asm/stackprotector.h`.

Integration points: Early boot, task stack protection, compiler-emitted stack-protector checks, and ARM64 pointer-auth support.

Risks: Incorrect endian mask would remove the wrong byte. Early boot must have enough randomness or architecture fallback behavior.

Test signals: Architecture boot tests with stack protector enabled/disabled, canary mask checks on endian/word-size variants, and compiler stack-protector fault tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/stackprotector.h -->
