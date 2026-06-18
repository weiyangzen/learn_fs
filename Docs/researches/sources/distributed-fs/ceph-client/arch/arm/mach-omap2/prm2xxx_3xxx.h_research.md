# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prm2xxx_3xxx.h

## Purpose
Provides shared OMAP2/3 PRM register offsets, inline module register accessors, common hardreset/powerdomain/clockdomain prototypes, and shared PRM bit masks.

## APIs, Flow, And State
Inline APIs read, write, RMW, set, clear, and read-shift PRM module registers via `prm_base.va + module + idx`. Prototypes cover hardreset, memory state, logic retention, transition polling, and wake dependency operations. Shared register fields include event generator timings, clock setup/source fields, reset timing/control/status bits, wake dependency bits, and logic retention.

## Dependencies And Integration
Includes `prcm-common.h`, `prm.h`, Linux IO, and `powerdomain.h`. It is the common include for `prm2xxx.c`, `prm3xxx.c`, and many OMAP2/3 power/clock call sites.

## Risks And Test Signals
Inline relaxed MMIO helpers assume `prm_base.va` is initialized and callers provide locking where noted. `__ffs(mask)` requires nonzero masks. Test signals include successful OMAP2/3 PRM MMIO after DT base init, hardreset operations, and powerdomain memory-bank reads.
