<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/fuloong-2e/Makefile -->
# sources/distributed-fs/ceph-client/arch/mips/loongson2ef/fuloong-2e/Makefile

Purpose: Builds the Fuloong 2E board support objects.

Important APIs/types/functions: Adds `irq.o`, `reset.o`, and `dma.o` to `obj-y`.

Control flow: Kernel build always includes these board files when the Fuloong 2E directory is selected.

State and persistence: No runtime state; controls object inclusion.

Dependencies and integration: Provides board hooks consumed by Loongson2EF common code.

Risks: Missing any object leaves weak/default hooks or DMA translation unsuitable for the board.

Test signals: A Fuloong 2E build should include board IRQ, reset, and DMA symbols with no unresolved references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/fuloong-2e/Makefile -->
