# sources/distributed-fs/ceph-client/arch/parisc/include/asm/special_insns.h

Purpose: wraps PA-RISC privileged and special instructions for address probing, physical address lookup, control registers, and space registers.

Important APIs/types/functions: defines `lpa`, `lpa_user`, `prober_user`, control-register IDs `CR_EIEM`, `CR_CR16`, `CR_EIRR`, plus `mfctl`, `mtctl`, `get_eiem`, `set_eiem`, `mfsp`, and `mtsp`.

Control flow: low-level code invokes these inline assembly helpers to read/write CPU control state, test user addresses, and translate virtual addresses to physical addresses.

State and persistence: control and space register writes persist in CPU state until changed. Dependencies and integration: used by IRQ flags, TLB/cache management, uaccess, timers, and MMU context switching.

Risks and test signals: operand constraints and privilege assumptions are critical. Test syscall/uaccess probing, timer reads, interrupt mask changes, and context-switch space-register state.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
