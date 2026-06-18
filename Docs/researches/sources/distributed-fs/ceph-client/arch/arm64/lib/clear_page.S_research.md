# sources/distributed-fs/ceph-client/arch/arm64/lib/clear_page.S

Purpose: provides the page-aligned `clear_page` primitive for zeroing a full kernel page.

Important APIs/types/functions: `__pi_clear_page`, alias `clear_page`, MOPS alternatives, DC ZVA fallback, and store-pair fallback.

Control flow: when assembler and CPU MOPS support are available, the routine uses `setpn/setmn/seten` over `PAGE_SIZE`. Without MOPS it reads `dczid_el0`; if DC ZVA is permitted it zeros one ZVA block at a time until the page boundary, otherwise it writes 64 bytes per loop with paired zero stores.

State and persistence: mutates only the destination page contents. It has no persistent state and assumes the caller provides a page-aligned page-sized destination.

Dependencies/integration: exported to core MM and page allocation code; depends on alternative patching, assembler helpers, `PAGE_SIZE`, and CPU DC ZVA/MOPS feature reporting.

Risks: incorrect ZVA size handling or non-page-aligned inputs can overrun or leave data uncleared. MOPS alternatives must patch correctly for CPUs without FEAT_MOPS. Cache and memory ordering are left to callers.

Test signals: boot/page allocator tests, zero-page verification across page sizes, CPU feature matrix with and without MOPS and DC ZVA, and KASAN/KMSAN checks for full-page initialization.
