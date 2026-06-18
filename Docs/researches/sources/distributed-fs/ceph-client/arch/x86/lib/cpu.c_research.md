# sources/distributed-fs/ceph-client/arch/x86/lib/cpu.c

Purpose: provides small CPUID signature decoding helpers for x86 family, model, and stepping fields.

Important APIs/functions: exports GPL symbols `x86_family`, `x86_model`, and `x86_stepping`.

Control flow: `x86_family()` extracts base family bits `[11:8]` and adds extended family bits `[27:20]` for family `0xf`. `x86_model()` calls `x86_family()`, extracts base model bits `[7:4]`, and adds extended model bits `[19:16] << 4` for family `>= 0x6`. `x86_stepping()` returns signature bits `[3:0]`.

State and persistence behavior: pure functions; no state, no side effects.

Dependencies/integration points: uses Linux export infrastructure and `<asm/cpu.h>`. Consumed by CPU feature, quirk, driver, and module code that needs consistent CPUID signature decoding.

Risks: simple but architecture-defined bit positions must stay exact. Family/model handling differs before family 6/15; helpers encode those rules.

Test signals: unit checks with known Intel/AMD signatures, module link tests, and CPU identification paths during boot.
