<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/atariints.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/atariints.h

## Purpose
This header defines Atari interrupt source numbering and inline MFP interrupt register operations. It provides the mapping between vectors, source indexes, MFP/SCC/VME interrupt domains, and Linux IRQ control.

## Important APIs, Types, And Functions
- Source bases include `STMFP_SOURCE_BASE`, `TTMFP_SOURCE_BASE`, `SCC_SOURCE_BASE`, `VME_SOURCE_BASE`, and `NUM_ATARI_SOURCES`.
- `IRQ_VECTOR_TO_SOURCE()` and `IRQ_SOURCE_TO_VECTOR()` convert between vector numbers and source indexes.
- `IRQ_MFP_*`, `IRQ_TT_MFP_*`, `IRQ_SCC*`, and shared timer constants identify interrupt sources.
- `get_mfp_bit()`, `set_mfp_bit()`, and `clear_mfp_bit()` compute MFP register addresses and operate on enable, pending, service, or mask bits.
- `atari_enable_irq()`, `atari_disable_irq()`, `atari_turnon_irq()`, `atari_turnoff_irq()`, `atari_clear_pending_irq()`, and `atari_irq_pending()` are inline IRQ controls.
- `atari_register_vme_int()` and `atari_unregister_vme_int()` manage VME interrupt allocation.

## Control Flow
Interrupt setup uses source/vector macros to register handlers. Runtime IRQ enable/disable paths update MFP mask registers; turn-on/off paths update MFP enable and pending bits. Pending checks read MFP pending registers to decide dispatch or acknowledge behavior.

## State And Persistence Behavior
The state is in MFP hardware registers, plus VME allocation state in the implementation. The inline helpers mutate hardware directly and do not maintain separate software shadow state.

## Dependencies And Integration Points
It depends on `asm/irq.h` and `atarihw.h` for MFP register mappings. It integrates with Atari interrupt controller code, MFP timer, serial, storage, SCC, VME, and device drivers.

## Risks And Edge Cases
The MFP register address calculation is compact and relies on source numbering layout. `clear_mfp_bit()` has different semantics for pending/service versus enable/mask registers; using the wrong type can lose interrupts. Range checks exclude non-MFP domains from inline helpers.

## Test Signals
Interrupt vector/source conversion tests, MFP enable/mask/pending operations, timer A-D interrupts, serial RX/TX/error interrupts, storage IRQs, SCC interrupts, and VME allocation/free paths validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/atariints.h -->
