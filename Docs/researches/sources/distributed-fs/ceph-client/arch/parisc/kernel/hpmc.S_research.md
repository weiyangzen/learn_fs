# sources/distributed-fs/ceph-client/arch/parisc/kernel/hpmc.S

## Purpose

`hpmc.S` implements the PA-RISC High Priority Machine Check handler. It tries to collect firmware PIM data, reset I/O, reinitialize enough console IODC state, and return into the normal trap-save path with an HPMC code so C code can dump registers and memory.

## Important APIs, Types, And Labels

The file allocates `hpmc_iodc_buf`, `hpmc_raddr`, and exported `hpmc_pim_data`. `os_hpmc` is the handler entry point. Labels `os_hpmc_1` through `os_hpmc_6` sequence PDC calls and failure reset handling.

It imports `toc_stack` as the emergency stack and `intr_save` as the normal low-level trap-save path. It uses PDC constants for `PDC_PIM`, `PDC_IO`, `PDC_IODC`, IODC `ENTRY_INIT_MOD_DEV`, and `PDC_BROADCAST_RESET`.

## Control Flow

On entry, `os_hpmc` saves the PDCE_PROC address from `arg0`, invalidates the handler checksum by incrementing a word under IVA to prevent nested HPMCs, switches to the TOC stack, and uses `rfi` to turn on the Q bit and turn off the M bit as required by many PDC calls.

The handler calls `PDC_PIM_HPMC` to copy HPMC PIM data into `hpmc_pim_data`, then calls `PDC_IO` to reset I/O. It loads console IODC into `hpmc_iodc_buf` with `PDC_IODC_READ`, calls the IODC init entry for the boot console using page-zero HPA/SPA/path fields, restores kernel page table root pointers, clears space registers, converts the stack to virtual, clears Q, sets trap code 1, and branches to `intr_save`.

If a required PDC or IODC step fails, the handler calls `PDC_BROADCAST_RESET`; if that returns, it writes a reset command to the broadcast I/O address and loops.

## State And Persistence Behavior

The handler writes the global PIM buffer and modifies low-level processor state: PSW bits, root pointers, space registers, stack pointer, and trap code. It deliberately invalidates the HPMC checksum to avoid reentry. No filesystem persistence is involved.

## Dependencies And Integration Points

It depends on firmware PDCE_PROC entry semantics, page-zero console fields, the TOC stack, `swapper_pg_dir`, and the trap entry code in `intr_save`. The C trap handler later consumes the saved state and `hpmc_pim_data`.

## Risks

The handler runs when hardware or firmware state may already be compromised. It has no normal C stack, uses physical addresses for early operations, and cannot rely on most kernel services. Multiprocessor synchronization is explicitly marked as missing. Failure in PDC_PIM or console IODC paths falls back to reset, so changes must preserve minimalism and firmware calling conventions.

## Test Signals

Signals are difficult to automate. Useful evidence includes successful HPMC injection or emulator-assisted machine-check tests that reach the C trap dump, valid PIM data in `hpmc_pim_data`, console output after HPMC, and reset fallback when forced PDC/IODC failures occur.
