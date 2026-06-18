# File Research: sources/block-storage/parted/libparted/fs/linux_swap/linux_swap.c

Linux swap and swsusp probe module. It treats swap as a `PedFileSystem` for libparted registration purposes and supports old swap signature `SWAP-SPACE`, new signature `SWAPSPACE2`, and suspend signature `S1SUSPEND`.

`swap_alloc()` creates a temporary filesystem object with `SwapSpecific` state, page-sized header buffer, large working buffer, duplicate geometry, and default v1 type. `swap_init()` derives page-sector size from `getpagesize()` and device sector size, computes page count, and reads the first page. `_swap_v0_open()`, `_swap_v1_open()`, and `_swap_swsusp_open()` validate signatures at the end of the first memory page. v0 page count is bounded by the old bitmap capacity; v1 uses `last_page`; swsusp is identified separately.

`_generic_swap_probe()` opens the requested kind and returns a geometry sized by swap page count for v1 or by input length for v0. Init registers three types and aliases: deprecated `linux-swap(old)`, deprecated `linux-swap(new)`, and canonical `linux-swap` pointing to v1. Risks include dependence on host page size matching swap metadata expectations.
