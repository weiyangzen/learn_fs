# sources/distributed-fs/ceph-client/lib/raid/xor/alpha/xor_arch.h

Purpose: supplies Alpha-specific XOR implementation registration for the common XOR core.

Important APIs and flow: declares `xor_block_alpha` and `xor_block_alpha_prefetch`. `arch_xor_init()` tests `implver()`: EV6 forces `xor_block_alpha_prefetch` because cold-cache behavior is expected to be better, while other Alpha variants register generic `8regs`, `32regs`, and both Alpha templates for calibration.

State and persistence: no runtime persistence beyond `xor-core.c`'s forced-template or registered-template list.

Dependencies and integration: depends on `<asm/special_insns.h>` for `implver()` and `IMPLVER_EV6`, and is included by `xor-core.c` when `CONFIG_XOR_BLOCKS_ARCH` is enabled.

Risks and test signals: forced selection bypasses calibration, so a CPU identification mistake could lock in a slower or broken path. Signals are boot logs showing forced or measured template choice and KUnit XOR correctness on Alpha builds.
