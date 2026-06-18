# sources/distributed-fs/ceph-client/rust/kernel/generated_arch_static_branch_asm.rs.S

## Purpose
This generated template extracts the architecture-specific static branch assembly macro into Rust literal form for jump-label support.

## Important APIs, Types, and Functions
The file includes `<linux/jump_label.h>` and calls `::kernel::concat_literals!(ARCH_STATIC_BRANCH_ASM("{symb} + {off} + {branch}", "{l_yes}"))`. It has no runtime functions.

## Control Flow
During build, the C preprocessor expands `ARCH_STATIC_BRANCH_ASM` with placeholder operands. The Rust macro concatenates emitted string fragments so generated Rust code can embed the resulting assembly template.

## State and Persistence
No runtime state exists. The preprocessed generated literal is a build artifact consumed by Rust static branch support.

## Dependencies and Integration Points
It depends on architecture jump-label macro definitions and Rust build tooling that recognizes the marker and macro output.

## Risks
Placeholder argument changes, architecture macro changes, or include ordering can invalidate generated output. Cross-architecture differences must remain compatible with Rust-side consumers.

## Test Signals
Compile on architectures with static branch support and compare generated strings against C expectations for symbol, offset, branch, and label substitutions.
