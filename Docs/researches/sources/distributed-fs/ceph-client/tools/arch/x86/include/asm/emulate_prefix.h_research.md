# sources/distributed-fs/ceph-client/tools/arch/x86/include/asm/emulate_prefix.h

## Purpose
Defines special byte sequences used by hypervisors to force instruction emulation. These prefixes are recognized by the x86 instruction decoder before normal prefix/opcode parsing.

## APIs, Types, and Functions
The file exports only `__XEN_EMULATE_PREFIX` and `__KVM_EMULATE_PREFIX`, each encoding `ud2` followed by ASCII vendor bytes.

## Control Flow, State, and Persistence
There is no state. `lib/insn.c` peeks for these byte sequences in `insn_get_emulate_prefix()`, records `insn->emulate_prefix_size`, and advances the decoder cursor so the real instruction follows the synthetic escape.

## Dependencies and Integration
Included by `tools/arch/x86/lib/insn.c`. It ties instruction decoding to Xen and KVM paravirtual emulation conventions without requiring callers to special-case those streams.

## Risks and Test Signals
Risks include accidental mismatch with kernel/hypervisor byte sequences and decode failures when the input buffer is shorter than the prefix. Test signals are decoder tests for Xen/KVM-prefixed instruction buffers and boundary tests where the prefix is truncated or followed by invalid opcodes.
