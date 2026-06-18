# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/pinmux-sh7722.c

Purpose: registers the SH7722 pin function controller resource window with the SuperH PFC core.

Important APIs, types, and functions: `plat_pinmux_setup()` calls `sh_pfc_register("pfc-sh7722", sh7722_pfc_resources, ARRAY_SIZE(...))` at `arch_initcall`. The resource array exposes MMIO `0xa4050100-0xa405018f`.

Control flow: the initcall runs during architecture initialization and creates the PFC platform registration before most device consumers request GPIO or function pins.

State and persistence: no local mutable state beyond the static resource table; hardware state is in PFC registers and owned by the PFC driver after registration.

Dependencies and integration points: depends on `<cpu/pfc.h>` and the SoC-specific PFC driver named `pfc-sh7722`. Board files and serial setup rely on this registration for pin modes.

Risks: the file only registers one MMIO range, so incorrect range size or base prevents PFC probing. No validation is performed locally.

Test signals: boot should register/probe `pfc-sh7722`; GPIO/function requests for SH7722 board devices should succeed; pinmux debug output should show the expected resource span.
