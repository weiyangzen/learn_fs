# sources/distributed-fs/ceph-client/arch/parisc/kernel/jump_label.c

## Purpose

`jump_label.c` implements PA-RISC static-key patching. It transforms reserved NOP sites into PA1.1 `b,n` branches to static-key targets, or back into NOPs.

## Important APIs, Types, And Functions

`reassemble_17()` encodes a signed 17-bit branch displacement into PA-RISC instruction bit layout. `arch_jump_label_transform()` is the architecture hook called by generic jump-label code with a `struct jump_entry` and `enum jump_label_type`.

## Control Flow

The transform obtains the patch address from `jump_entry_code()`. For `JUMP_LABEL_JMP`, it computes `target - addr - 8`, verifies the signed 17-bit branch range, encodes a `b,n` instruction (`0xe8000002` plus the reassembled displacement), and calls `patch_text()`. For the non-jump state it patches `INSN_NOP`.

## State And Persistence Behavior

The only state mutation is kernel text patching at static-key sites. Patches persist until the static key toggles again. There is no separate data persistence.

## Dependencies And Integration Points

The file depends on generic jump labels, PA-RISC alternative/text patching, instruction constants, and the assumption that static-key branch targets are within the 17-bit displacement range.

## Risks

The range check is fatal through `BUG_ON()`. Code layout changes that put jump-label targets outside range will crash when transforming. The displacement subtracts 8 for PA-RISC branch semantics, so off-by-one-instruction errors would redirect control flow.

## Test Signals

Signals include toggling static keys under tracing or branch-heavy kernel features, verifying patched instruction bytes with ftrace/jump-label debug tooling, and booting kernels where jump-label sites are spread across sections without range failures.
