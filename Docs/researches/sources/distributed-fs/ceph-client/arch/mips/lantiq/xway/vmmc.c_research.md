# sources/distributed-fs/ceph-client/arch/mips/lantiq/xway/vmmc.c

Purpose: reserves coherent memory for the Lantiq VMMC/CP1 voice processor and configures optional relay GPIOs.

Important APIs/functions: `ltq_get_cp1_base`, `vmmc_probe`, `vmmc_match`, and `vmmc_driver`.

Control flow: built-in platform driver probes `lantiq,vmmc-xway`, allocates 1 MiB coherent memory, stores its physical address as `cp1_base`, requests all unnamed GPIOs as output-high relays, names them `vmmc-relay`, and logs the reservation. Consumers call `ltq_get_cp1_base()` and panic if probe has not set the base.

State and persistence: static `cp1_base` persists after probe; coherent DMA allocation is kernel-lifetime.

Dependencies and integration: exports CP1 base to voice/firmware users; uses DMA coherent and GPIO descriptor APIs.

Risks: allocation failure is not checked before `CPHYSADDR`. Panicking accessor makes probe ordering important. GPIO failures are logged but not fatal.

Test signals: VMMC DT probe, non-null CP1 base export, relay GPIO state, and voice firmware users accessing the reserved region.
