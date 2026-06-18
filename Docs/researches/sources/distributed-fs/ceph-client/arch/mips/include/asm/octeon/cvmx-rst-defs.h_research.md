# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-rst-defs.h

Purpose: defines OCTEON reset, boot, power, PCIe reset, and BIST-clear CSR addresses and packed register layouts.

Important APIs/types/functions: macros cover `CVMX_RST_BOOT`, `CVMX_RST_CFG`, `CVMX_RST_CKILL`, indexed `CVMX_RST_CTLX`, `CVMX_RST_DELAY`, `CVMX_RST_ECO`, `CVMX_RST_INT`, `CVMX_RST_OCX`, `CVMX_RST_POWER_DBG`, `CVMX_RST_PP_POWER`, indexed `CVMX_RST_SOFT_PRSTX`, and `CVMX_RST_SOFT_RST`. Unions include `cvmx_rst_boot`, `cvmx_rst_cfg`, `cvmx_rst_ckill`, `cvmx_rst_ctlx`, `cvmx_rst_delay`, `cvmx_rst_eco`, `cvmx_rst_int`, `cvmx_rst_ocx`, `cvmx_rst_power_dbg`, `cvmx_rst_pp_power`, `cvmx_rst_soft_prstx`, and `cvmx_rst_soft_rst`.

Control flow: the file is declarative. Platform reset code reads boot straps and PLL multipliers, writes BIST-clear policy and reset delays, controls per-link reset bits through `RST_CTLX`/`SOFT_PRSTX`, and can trigger a chip-wide software reset via `soft_rst`.

State and persistence: all state is hardware reset-domain state. Some fields reflect boot-time straps (`lboot`, `rboot`, multipliers, JTAG/EJTAG disable flags), while others control active reset and power-gating state. A software reset or processor power gate has system-wide effects and persists only until the next reset cycle reinitializes hardware.

Dependencies and integration points: depends on `CVMX_ADD_IO_SEG` and the OCTEON CSR access layer. It integrates with board boot, PCIe root-complex/endpoint setup, CPU power management, and reset interrupt handling.

Risks: mistaken writes can reset links, processors, or the full chip. Indexed macros mask offsets with `& 3`; out-of-range callers silently alias to one of four registers. CN70XX variants narrow some fields, so generic code can misinterpret gate or interrupt bit widths. BIST-clear fields must be coordinated with diagnostics to avoid losing failure evidence.

Test signals: hardware validation should verify boot strap decoding, reset interrupt bits, PCIe link reset sequencing, and soft-reset paths. Static tests should compile both endian layouts and chip-specific union views.
