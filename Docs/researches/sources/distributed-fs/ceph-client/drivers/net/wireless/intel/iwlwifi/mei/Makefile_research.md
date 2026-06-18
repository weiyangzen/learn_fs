# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mei/Makefile

Purpose: Builds the optional `iwlmei` companion module that mediates iwlwifi communication with Intel CSME firmware over MEI/SAP.

Important APIs and targets: `obj-$(CONFIG_IWLMEI) += iwlmei.o` gates module build. `iwlmei-y` includes `main.o` and `net.o`; `trace.o` is added for `CONFIG_IWLWIFI_DEVICE_TRACING`. `CFLAGS_trace.o` and `ccflags-y` add include paths for trace generation and parent iwlwifi headers.

Control flow: Kbuild composes `iwlmei.o` from the listed objects when enabled. There is no runtime flow in this file.

State and persistence: No runtime state. Build configuration determines whether real MEI APIs or stubs from `iwl-mei.h` are used by iwlwifi.

Dependencies and integration points: Integrates with kernel Kbuild, `CONFIG_IWLMEI`, tracing configuration, and headers in the parent iwlwifi directory.

Risks: Missing parent include path breaks shared-header inclusion. Trace include flags must match kernel tracing generation expectations. Disabled `CONFIG_IWLMEI` changes ownership/NVM behavior via stubs.

Test signals: Build with `CONFIG_IWLMEI=y/m/n`, build with device tracing enabled, and verify module object contains `main.o`, `net.o`, and optional `trace.o`.
