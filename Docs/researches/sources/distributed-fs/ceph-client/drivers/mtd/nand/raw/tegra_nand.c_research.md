## sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/tegra_nand.c

Purpose: this is the NVIDIA Tegra20 NAND controller driver. It provides parsed command execution, DMA page transfers, hardware RS or BCH ECC, timing setup from SDR timings, runtime clock PM, optional write-protect GPIO, and a single-child/single-CS raw NAND integration.

Important APIs, types, and functions: `struct tegra_nand_controller` stores the controller, MMIO base, IRQ, clock, command/DMA completions, last-read-error flag, current CS, and chip pointer. `struct tegra_nand_chip` embeds the NAND chip, WP GPIO, ECC OOB region, config templates, BCH config, and CS. Key functions are `tegra_nand_irq()`, `tegra_nand_cmd()`, `tegra_nand_page_xfer()`, raw and HWECC page/OOB callbacks, `tegra_nand_setup_timing()`, ECC strength selection helpers, `tegra_nand_attach_chip()`, child parsing, probe/remove, and runtime PM callbacks.

Control flow: probe maps registers, gets reset and clock, initializes Tegra OPP support, enables runtime PM/clock, resets hardware, programs status/IRQ defaults, requests IRQ, clears DMA done status, parses exactly one child NAND node with one CS, scans, and registers MTD. Small command operations use a NAND op parser to program command/address registers and optionally exchange up to four bytes through `RESP`. Page/OOB operations use `tegra_nand_page_xfer()`, which maps data and/or OOB buffers for DMA, programs DMA pointers and command bits, waits for command and DMA completions, and aborts/dumps registers on timeout. Hardware ECC wraps page DMA with ECC config and interprets decoder status.

State and persistence: persistent runtime state includes controller config templates for raw vs ECC mode, BCH config, current CS, selected ECC algorithm/strength, OOB ECC region, and `last_read_error` latched from IRQ status. Runtime PM only gates the clock; the driver keeps the device resumed while bound.

Dependencies and integration points: it depends on raw NAND op parsers, DMA mapping, Tegra common OPP setup, reset and clock frameworks, GPIO descriptors, MTD OOB layouts, runtime PM, and the `nvidia,tegra20-nand` compatible.

Risks: only one NAND chip and one CS are supported. ECC requires 512-byte steps; BCH is limited to 2K/4K pages, while RS/BCH boot-medium strength choices are restricted. Corrected-bit statistics are overestimated because hardware reports only the maximum correction count per page and corrected-sector bitmap. Erased-page handling rereads OOB when all sectors fail. DMA timeouts trigger a controller abort and IRQ disable/enable cycle. The OOB layout exposes no free regions.

Test signals: probe with a single child CS, OPP/runtime PM clock enable, small op parser READID/status behavior, DMA page/OOB transfers, command/DMA timeout register dumps absent during stress, RS and BCH ECC strength selection, erased-page false-failure handling, corrected/failed ECC stat updates, timing register programming, and runtime suspend/resume clock gating.
