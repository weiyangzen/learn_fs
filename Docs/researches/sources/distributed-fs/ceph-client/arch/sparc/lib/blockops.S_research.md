# sources/distributed-fs/ceph-client/arch/sparc/lib/blockops.S

Purpose: SPARC32 one-page zero and copy block helpers.

Important APIs/functions: Exports `bzero_1page` and `__copy_1page`.

Control flow: `bzero_1page` loops over `PAGE_SIZE` using a macro that writes a block of zeros at multiple offsets. `__copy_1page` loops over a page using a macro that loads source words and stores them to destination.

State and persistence: Mutates a single destination page; no persistent state.

Dependencies/integration: Includes `asm/page.h`; built for `CONFIG_SPARC32`.

Risks/test signals: Loop count and block offsets must cover exactly one page. Test full page clear/copy, page alignment, and comparison against generic page helpers.
