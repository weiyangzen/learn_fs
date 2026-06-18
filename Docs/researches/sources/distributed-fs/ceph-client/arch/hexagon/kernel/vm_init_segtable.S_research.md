# sources/distributed-fs/ceph-client/arch/hexagon/kernel/vm_init_segtable.S

## Purpose

`vm_init_segtable.S` defines and initializes the early Hexagon segment and device page tables. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

Important labels include `swapper_pg_dir`, `_K_init_segtable`, `_K_io_map`, `_K_init_devicetable`, and `UART_PTE_ENTRY`; macros create big-page, IO, and L2 pointer entries. Concrete declarations observed in the file: Includes: `asm/vm_mmu.h`. Macros: `BKP`, `BKPG_IO`, `FOURK_IO`, `L2_PTR`, `X`. Assembly entry labels: `swapper_pg_dir`, `UART_PTE_ENTRY`, `_K_init_segtable`, `_K_io_map`, `_K_init_devicetable`, `_K_io_kmap`.

## Control Flow, State, And Persistence

Control flow/data setup creates boot-time identity/virtual mappings, kernel text/data mappings, IO windows, and the initial device table consumed by early boot and MM initialization.

## Dependencies And Integration Points

It integrates with `head.S`, `mm/init.c`, HVM PTE definitions, and the linker script.

## Risks And Test Signals

Risks are invalid early mappings, wrong cache attributes, or device-window overlap. Test signals are early console, memory sizing logs, and boot through paging initialization.
 A local static signal for this file is that it has 430 lines and 12163 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
