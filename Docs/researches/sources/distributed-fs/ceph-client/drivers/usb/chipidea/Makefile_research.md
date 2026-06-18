# sources/distributed-fs/ceph-client/drivers/usb/chipidea/Makefile

Purpose: maps ChipIdea Kconfig symbols to core, role, trace, OTG FSM, and glue driver objects.

Important APIs/types/functions: builds `ci_hdrc.o` from `core.o otg.o debug.o ulpi.o`, conditionally adds `udc.o trace.o`, `host.o`, and `otg_fsm.o`, and emits glue modules `ci_hdrc_usb2.o`, `ci_hdrc_msm.o`, `ci_hdrc_npcm.o`, `ci_hdrc_pci.o`, `usbmisc_imx.o ci_hdrc_imx.o`, and `ci_hdrc_tegra.o`.

Control flow: no runtime flow; object inclusion controls available callbacks and tracepoint definitions. `CFLAGS_trace.o := -I$(src)` supports `define_trace.h` finding `trace.h`.

State and persistence: no runtime state; build artifact composition is determined by Kconfig.

Dependencies and integration: ties the central `ci_hdrc` module to role implementations and platform glue modules. The i.MX rule also includes `usbmisc_imx.o`, an important sidecar dependency for `ci_hdrc_imx.c`.

Risks: trace builds require exactly one `CREATE_TRACE_POINTS` translation unit. Missing conditional objects surface as `-ENXIO` stubs or link errors depending on header coverage.

Test signals: build matrix across UDC, host, OTG FSM, and each glue driver; tracepoint build validates the special include flag.
