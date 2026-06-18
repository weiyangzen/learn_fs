# sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/bna/bfa_ioc_ct.c

## Purpose
`bfa_ioc_ct.c` provides the CT and CT2 ASIC-specific implementation behind the common `struct bfa_ioc_hwif` interface used by the BNA network IOC layer. It maps BAR0 register offsets, initializes PLLs and memory blocks, handles firmware ownership/reference counting, synchronizes failure recovery across PCI functions, chooses port mappings, and exposes CT/CT2 hardware operation tables through `bfa_nw_ioc_set_ct_hwif()` and `bfa_nw_ioc_set_ct2_hwif()`.

## Important APIs, Types, and Functions
- `bfa_nw_ioc_set_ct_hwif()` and `bfa_nw_ioc_set_ct2_hwif()` install static `bfa_ioc_hwif` tables into `ioc->ioc_hwif`.
- `bfa_ioc_ct_firmware_lock()` and `bfa_ioc_ct_firmware_unlock()` serialize firmware image ownership with hardware semaphores and the MMIO use-count register.
- `bfa_ioc_ct_reg_init()` and `bfa_ioc_ct2_reg_init()` populate `ioc->ioc_regs` for mailbox, heartbeat, state, semaphores, SRAM, PLL, and error/halt registers.
- `bfa_ioc_ct_map_port()` and `bfa_ioc_ct2_map_port()` read personality registers to assign `ioc->port_id`.
- `bfa_ioc_ct_sync_start()`, `sync_join()`, `sync_leave()`, `sync_ack()`, and `sync_complete()` coordinate multi-function IOC failure recovery using `ioc_fail_sync`.
- `bfa_ioc_ct_pll_init()` performs CT clock, reset, MAC, LMEM, and EDRAM BIST initialization.
- `bfa_ioc_ct2_pll_init()` supports CT2/NFC-assisted and fallback PLL/MAC/memory initialization paths.

## Control Flow and State
The common IOC layer first selects a hardware interface, maps the port, initializes register pointers, then uses these callbacks for firmware locking, PLL initialization, state register updates, mailbox interrupt mode, and recovery. Firmware lock flow returns early for flash/BIOS boot images, otherwise acquires `ioc_usage_sem_reg`, checks `ioc_usage_reg`, verifies the running firmware header with `bfa_nw_ioc_fwver_cmp()`, increments use count, and clears fail sync on first owner.

Failure synchronization stores requested PCI functions in high bits of `ioc_fail_sync` and acknowledgements in low bits. On first startup after an unclean exit, `sync_start()` clears fail sync, sets use count to one, and resets both IOC state registers to `BFI_IOC_UNINIT`. During recovery, `sync_complete()` waits until all required functions have acknowledged, then clears ack bits and writes both current and alternate IOC state registers to `BFI_IOC_FAIL`.

CT and CT2 register setup diverges mainly in function indexing. CT uses function-specific arrays for four PCI functions and port-specific LPU command/status registers. CT2 uses two port entries with changed semaphore/state offsets and includes `lpu_read_stat`.

## State and Persistence Behavior
All meaningful persistence is MMIO-backed hardware state rather than filesystem state. The file reads and writes IOC use counts, firmware states, heartbeat locations, fail-sync bits, semaphore locks, interrupt masks/status, PLL controls, NFC control registers, mailbox command/status registers, and halt bits. These survive long enough to coordinate multiple functions and driver reloads, and wrong values can affect other PCI functions sharing the ASIC.

## Dependencies and Integration Points
The implementation depends on `bfa_ioc.h` for IOC structure/callback contracts, `bfi.h` for firmware state values, `bfi_reg.h` for ASIC offsets and bit masks, and Linux MMIO primitives (`readl`, `writel`, `udelay`). It integrates upward with the common IOC state machine and downward with CT/CT2 register layouts. `bna_enet.c` indirectly relies on these callbacks through `bfa_nw_ioc_enable()`, mailbox interrupts, and IOC ready/failure notifications.

## Risks
- `BUG_ON()` is used for invalid use counts, impossible PLL/NFC states, and semaphore assumptions; hardware or firmware anomalies can panic the kernel.
- The firmware use-count and fail-sync protocol is shared across PCI functions, so missed semaphore handling or stale bits can wedge recovery or reset another function unexpectedly.
- PLL paths rely on fixed delays and polling loops; hardware timing changes or emulation can expose races.
- `bfa_ioc_ct_isr_mode_set()` mutates function personality bits and assumes the CT layout; CT2 has no equivalent callback.

## Test Signals
Useful validation signals include successful IOC enable/disable cycles on CT and CT2 hardware, firmware reload with multiple active PCI functions, forced heartbeat failure recovery, driver reload after unclean exit, MSI-X/INTx mode changes on CT, CT2 NFC-assisted and fallback PLL paths, and absence of stuck `BFI_IOC_FAIL`/`BFI_IOC_UNINIT` states after recovery.
