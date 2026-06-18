# sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/renesas-nand-controller.c

Purpose: this is the Renesas R-Car Gen3 and RZ/N1 NAND controller driver for the Evatronix-derived controller. It implements generic `exec_op`, timing setup, DMA-backed full-page hardware ECC, FIFO-backed subpage ECC, OOB layout, optional IRQ or polling completion, and multi-CS child chip registration.

Important APIs, types, and functions: `struct rnandc` owns controller state, MMIO, clock rate, completion, polling flag, shared DMA buffer, and chip list. `struct rnand_chip` caches per-chip/die CS selection, control/ECC/timing registers, and selected die. `struct rnandc_op` packages command/address/data sequence registers. Key functions include `rnandc_select_target()`, `rnandc_trigger_op()`, `rnandc_wait_end_of_op()`, `rnandc_wait_end_of_io()`, `rnandc_read/write_page_hw_ecc()`, `rnandc_read/write_subpage_hw_ecc()`, `rnandc_exec_op()`, `rnandc_setup_interface()`, and `rnandc_attach_chip()`.

Control flow: probe maps MMIO, enables runtime PM, reads the `eclk` rate for timing calculations, configures IRQ or polling mode, sets a 32-bit DMA mask, clears FIFO, and initializes child NANDs. Attach rejects small-page devices, derives block-size control bits from memory organization, enables subpage reads, chooses/validates ECC, and forces later target reconfiguration. Page read/write uses DMA into a controller-owned buffer with ECC enabled, while subpage operations use FIFO accesses rounded to ECC chunks. Generic operations are translated directly into up to four command phases, two address phases, two delay phases, and one data phase.

State and persistence: per-chip cached timing/control/ECC registers are written on target selection. The shared DMA buffer is resized to the largest registered chip. On-media layout reserves two initial OOB bytes before ECC and free regions. Runtime PM is enabled during probe and released on remove, but there are no custom suspend hooks here.

Dependencies and integration points: the driver uses raw NAND controller ops, Linux DMA mapping, completions, optional IRQs, runtime PM, OF child nodes, and compatibles `renesas,rcar-gen3-nandc` and `renesas,rzn1-nandc`.

Risks: FIFO loops use busy waits with limited internal guarding; stuck FIFO state can spin until the later operation wait. ECC corrected-bit reporting is page-level approximation, not per chunk. Small pages and unsupported eraseblock page counts are rejected. Timing setup requires equal read/write pulse and hold times. Polling fallback changes completion behavior and should be tested separately from IRQ mode.

Test signals: probe with and without IRQ, multiple CS values and duplicate-CS rejection, SDR timing conversion, full-page DMA ECC read/write, subpage read/write, erased-page handling for uncorrectable reports, OOB layout offsets, runtime PM enable/put balance, and timeout logs from operation/IO waits.
