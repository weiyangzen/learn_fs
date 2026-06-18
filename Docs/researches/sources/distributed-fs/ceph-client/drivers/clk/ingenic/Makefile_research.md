# sources/distributed-fs/ceph-client/drivers/clk/ingenic/Makefile Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ingenic/Makefile -->
## sources/distributed-fs/ceph-client/drivers/clk/ingenic/Makefile

### Purpose
The Ingenic Makefile maps Kconfig symbols to the CGU common objects, SoC-specific CGU tables, and TCU clock driver.

### Important APIs, Types, And Functions
It builds `cgu.o pm.o` when `CONFIG_INGENIC_CGU_COMMON` is enabled, one `*-cgu.o` file per SoC symbol, and `tcu.o` for `CONFIG_INGENIC_TCU_CLK`.

### Control Flow, State, And Persistence
Build composition is direct: SoC CGU options depend on and select the common implementation, so table files link against `ingenic_cgu_new()`, `ingenic_cgu_register_clocks()`, and `ingenic_cgu_register_syscore()`. There is no runtime state in this file, but the object list determines which OF_DECLARE registrations are present at boot.

### Dependencies, Integration Points, Risks, And Test Signals
The Makefile must stay aligned with Kconfig names, source filenames, and dt-binding compatible coverage. Risks are missing common objects for a selected SoC, stale object names after file renames, or absent TCU support in platform builds. Test signals are kernel build matrix coverage for each `CONFIG_INGENIC_*` symbol and successful link of each OF clock declaration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ingenic/Makefile -->
