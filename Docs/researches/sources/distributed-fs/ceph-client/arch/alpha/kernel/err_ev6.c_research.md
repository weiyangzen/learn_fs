# sources/distributed-fs/ceph-client/arch/alpha/kernel/err_ev6.c

**Purpose:** Decodes and reports EV6 processor machine-check logout frames. It identifies Ibox, Mbox/Dcache, and Cbox/cache/memory error syndromes, decides whether an error is known/reportable, dumps additional frame data for non-dismissed events, and releases the PAL logout frame.

**Important APIs/types/functions:** Exposes `ev6_register_error_handlers()`, `ev6_process_logout_frame()`, and `ev6_machine_check()`. Key parsers are `ev6_parse_ibox()`, `ev6_parse_mbox()`, and `ev6_parse_cbox()`. It consumes `struct el_common_EV6_mcheck` from `<asm/err_ev6.h>` and disposition constants from the common error headers.

**Control flow:** `ev6_machine_check()` synchronizes the processor with `mb()` and `draina()`, first parses the frame with `print == 0`, and suppresses output only if disposition is dismissible. Otherwise it raises `err_print_prefix` to critical, prints correctable/uncorrectable vector context, reprocesses with printing enabled, dumps registers through `dik_show_regs()`, restores the prefix, then calls `wrmces(0x7)` to release the frame. `ev6_process_logout_frame()` ORs parser dispositions and, when printing, emits extra core registers and dumps the whole logout frame unless the disposition is dismissible.

**State and persistence behavior:** No persistent state. It reads a PAL logout frame pointed to by `la_ptr`, temporarily changes `err_print_prefix`, and clears machine-check state with `wrmces`.

**Dependencies and integration points:** Called by generic Alpha interrupt handling through `alpha_mv.machine_check` or delegated from TITAN/Privateer for processor-frame cases. Depends on `err_common.c` dump helpers, `get_irq_regs()`, SMP CPU id, and EV6 frame field definitions.

**Risks:** Parser status is built with bitwise OR over disposition values, so disposition constant design must make combinations meaningful. Print decoding is gated by compile-time verbose options for some surrounding handlers, and unknown errors fall back to full dumps. Incorrect bit definitions would misclassify hardware errors or suppress important logs.

**Test signals:** Use known EV6 logout-frame samples for Icache parity, Dcache tag/ECC, and Cbox memory/Bcache errors. Verify correctable versus uncorrectable vectors, no output for intentionally dismissible cases if any are added, register dump presence on reportable errors, and `wrmces` release. Compile with and without verbose machine-check support.
