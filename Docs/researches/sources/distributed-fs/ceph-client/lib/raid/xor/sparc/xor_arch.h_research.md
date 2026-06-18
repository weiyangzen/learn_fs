# sources/distributed-fs/ceph-client/lib/raid/xor/sparc/xor_arch.h

Purpose: defines SPARC XOR registration and forced selection policy.

Important APIs and flow: on sparc64, `arch_xor_init()` forces `xor_block_niagara` for hypervisor Niagara chip types and otherwise forces `xor_block_VIS`. On 32-bit SPARC it registers generic `8regs`, `32regs`, and `xor_block_SPARC`.

State and persistence: forced-template state is stored in the XOR core during init.

Dependencies and integration: sparc64 path depends on `<asm/spitfire.h>` global CPU type data; 32-bit path depends on `xor-sparc32.c`.

Risks and test signals: forced selection relies on CPU-type detection and assembly requirements. Signals include boot logs, KUnit, and parity workloads on sun4v Niagara and non-Niagara SPARC64 systems.
