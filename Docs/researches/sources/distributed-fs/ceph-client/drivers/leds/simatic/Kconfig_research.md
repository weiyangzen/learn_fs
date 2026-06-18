<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/simatic/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/leds/simatic/Kconfig

Purpose: This Kconfig file declares LED driver options for Siemens SIMATIC industrial PCs, covering a legacy I/O-port implementation and GPIO-backed variants for Intel Apollo Lake, Intel Elkhart Lake, and Nuvoton F7188x hardware.

Important entries: `LEDS_SIEMENS_SIMATIC_IPC` depends on `LEDS_CLASS` and `SIEMENS_SIMATIC_IPC` and defaults to `y`, building `simatic-ipc-leds`. `LEDS_SIEMENS_SIMATIC_IPC_APOLLOLAKE`, `LEDS_SIEMENS_SIMATIC_IPC_F7188X`, and `LEDS_SIEMENS_SIMATIC_IPC_ELKHARTLAKE` depend on `LEDS_GPIO`, the relevant pinctrl/GPIO controller option, and `SIEMENS_SIMATIC_IPC`; they default to the base SIMATIC LED option.

Control flow and integration: Kconfig selection constrains the Makefile objects so the common GPIO helper is compiled with each GPIO board wrapper. The dependencies ensure the platform base driver is present to instantiate platform devices with `struct simatic_ipc_platform` data, and that the LED/GPIO providers required by the drivers are enabled.

State and persistence: This file has no runtime state. It persists build-time policy and module names.

Risks and test signals: The default-to-base relationship can enable GPIO LED modules whenever the base option is enabled, but hard dependencies on pinctrl/GPIO providers keep impossible builds out. Build tests should cover each tristate as built-in and module, and negative dependency combinations should not expose unavailable options.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/simatic/Kconfig -->
