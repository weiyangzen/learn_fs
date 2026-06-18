# sources/distributed-fs/ceph-client/drivers/clk/sifive/Kconfig

Purpose: Kconfig menu for SiFive clock support and the PRCI driver.

Important APIs/types/functions: `CLK_SIFIVE` menuconfig; `CLK_SIFIVE_PRCI` tristate; selects `RESET_CONTROLLER`, `RESET_SIMPLE`, and `CLK_ANALOGBITS_WRPLL_CLN28HPC`.

Control flow: configuration controls whether `sifive-prci.o` is built and whether it is built-in or modular.

State and persistence behavior: no runtime state; selected symbols control compiled feature availability.

Dependencies/integration points: defaults to `ARCH_SIFIVE`, supports `COMPILE_TEST`, and pulls in reset and WRPLL dependencies required by `sifive-prci.c`.

Risks: dependency/select drift can produce build or link failures; defaulting to `ARCH_SIFIVE` makes this driver part of typical SiFive kernels.

Test signals: Kconfig resolution for `y`, `m`, and disabled builds, including non-SiFive `COMPILE_TEST`.
