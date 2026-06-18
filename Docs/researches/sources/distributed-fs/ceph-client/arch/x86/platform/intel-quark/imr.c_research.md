<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/intel-quark/imr.c -->
# sources/distributed-fs/ceph-client/arch/x86/platform/intel-quark/imr.c

## Purpose
Provides Intel Quark X1000 Isolated Memory Region management, protecting selected physical ranges from non-CPU system-agent access.

## Important APIs, Types, And Functions
`struct imr_device` stores init state, lock, register base, and count. `struct imr_regs` mirrors address/mask registers. Exported APIs are `imr_add_range()` and `imr_remove_range()`. Internal helpers read/write IOSF MBI registers, validate 1 KiB alignment, detect overlaps, clear entries, expose debugfs state, and build a kernel text/rodata IMR at init.

## Control Flow
`device_initcall` matches Quark and IOSF availability, initializes the device, registers debugfs, clears unlocked firmware/grub IMRs, and protects kernel `.text` through `__end_rodata`. Adding a range validates alignment/nonzero size, converts size to IMR raw encoding, rejects disabled all-access zero ranges and overlaps, chooses a free register, then writes address and masks. Removal finds by index or exact address range and writes the disabled encoding.

## State And Persistence
IMR state is persistent hardware register state until firmware reset or later writes. The driver keeps only lock/init metadata in RAM. Debugfs reads live hardware state.

## Dependencies And Integration Points
Requires `iosf_mbi_read/write()`, Quark CPU matching, `asm/imr.h` mask constants, kernel section boundaries, and debugfs.

## Risks And Edge Cases
Failed IOSF writes can leave partial IMR state and cause system resets on later memory access. Overlap detection checks base/end inside existing ranges but not all possible containment forms. Locked firmware IMRs cannot be removed. Alignment and raw-size handling must preserve the hardware's inclusive high-address encoding.

## Test Signals
Debugfs `imr_state`, boot log showing kernel text protection, selftest pass/fail output, and absence of random resets under DMA-heavy IO are primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/intel-quark/imr.c -->
