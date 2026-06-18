<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/arm64/gic_v5.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/arm64/gic_v5.h

Purpose: this header provides GICv5 current-domain instruction encodings, bitfield helpers, barriers, and minimal CPU-interface initialization routines for arm64 KVM GICv5 selftests.

Important APIs, types, and functions: `GICV5_OP_GIC_*` and `GICV5_OP_GICR_*` define system instruction encodings for current-domain affinity, enable, priority, pending, acknowledge, deactivate, and EOI operations. Bit masks decode or build instruction operands such as `GICV5_GICR_CDIA_VALID_MASK`, `GICV5_GICR_CDIA_INTID`, and per-operation ID/type/priority fields. `gicr_insn()` reads GICR current-domain instruction results and `gic_insn()` writes GIC instructions. `gsb_ack()` and `gsb_sys()` emit GIC barrier instructions. `gicv5_ppi_priority_init()`, `gicv5_cpu_disable_interrupts()`, and `gicv5_cpu_enable_interrupts()` configure PPI priority registers, `ICC_PCR_EL1`, and `ICC_CR0_EL1`.

Control flow: initialization clears PPI enable registers, writes default priority to all PPI priority registers, sets the priority control register, and enables the CPU interface. Barrier and instruction helpers are inline macros. The header defines executable functions in the header, so every including translation unit receives definitions.

State, persistence, and dependencies: state is guest CPU interface sysreg state. Dependencies include `<asm/barrier.h>`, `<asm/sysreg.h>`, `linux/bitfield.h`, and `processor.h`. It is used by `vgic_v5.c`.

Risks and edge cases: GICv5 is optional and instruction encodings must match the architecture. Header-defined non-static functions can create multiple-definition risk if included by multiple C files in one link unit, though current use is narrow. Priority defaults use repeated 5-bit priority bytes and assume the tested KVM model implements these sysregs.

Test signals: `vgic_v5.c` validates these helpers by enabling PPIs, acknowledging CDIA results, applying barriers, and deactivating/EOIing software PPIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/arm64/gic_v5.h -->
