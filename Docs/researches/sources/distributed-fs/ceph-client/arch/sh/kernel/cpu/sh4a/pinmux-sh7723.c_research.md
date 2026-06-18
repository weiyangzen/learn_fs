# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/pinmux-sh7723.c

Purpose: registers the SH7723 PFC MMIO block with the SuperH pin-control framework.

Important APIs, types, and functions: `plat_pinmux_setup()` registers `pfc-sh7723`; `sh7723_pfc_resources` describes `0xa4050100-0xa405016f`.

Control flow: an `arch_initcall` invokes the registration once during boot. The PFC core later binds the named driver and services GPIO/pin-function requests.

State and persistence: this file contains static immutable resource metadata only. Persistent pin state is maintained by the hardware and PFC core.

Dependencies and integration points: integrates with `<cpu/pfc.h>` and SH7723 board/platform setup, especially SCIF/SCIFA, I2C, USB, and multimedia pin assignments.

Risks: there is no runtime SoC detection; building or selecting this for the wrong CPU registers the wrong address range. Missing GPIO resource means all access is through the PFC range.

Test signals: `pfc-sh7723` should probe without MMIO conflicts, and platform devices requiring alternate pin functions should initialize correctly.
