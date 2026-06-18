<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/alternative-macros.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/alternative-macros.h

## Purpose
Defines assembly and C inline-assembly macros for RISC-V runtime alternatives.

## Important APIs, Types, And Functions
Important macros include `ALT_ENTRY`, `ALT_NEW_CONTENT`, `ALTERNATIVE_CFG`, `ALTERNATIVE_CFG_2`, `__ALTERNATIVE_CFG`, `_ALTERNATIVE_CFG`, `ALTERNATIVE`, and `ALTERNATIVE_2`. When alternatives are disabled, they collapse to the old instruction content.

## Control Flow
When enabled, macros emit old code at labels 886/887, alternative metadata in `.alternative`, replacement code in subsection 1 at labels 888/889, disable RVC/relaxation around patchable content, and use `.org` checks to keep old and new content lengths compatible.

## State And Persistence
Persistent state is the `.alternative` metadata and replacement instruction sections linked into the kernel or module. Runtime patching code later consumes those entries.

## Dependencies And Integration Points
Integrated with `asm/alternative.h`, vendor errata patch functions, cpufeature alternatives, module loading, and text patching.

## Risks And Edge Cases
Length mismatches, relaxed instructions, or compressed encodings can make runtime patching unsafe, hence `norvc` and `norelax`. `ALTERNATIVE_2` must preserve ordering when multiple vendors patch the same site.

## Test Signals
Signals are objdump inspection of `.alternative`, successful builds with alternatives on/off, boot-time patch application, and module alternative patching.

Source read size: 161 lines, 5123 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/alternative-macros.h -->
