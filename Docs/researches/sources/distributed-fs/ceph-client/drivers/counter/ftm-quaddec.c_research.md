# sources/distributed-fs/ceph-client/drivers/counter/ftm-quaddec.c

Purpose: platform driver for the NXP/Freescale FlexTimer Module quadrature decoder, exposing one X4 quadrature count with two phase signals through the Generic Counter subsystem.

Important APIs/types/functions: private `struct ftm_quaddec` stores platform device, MMIO base, endian mode, and mutex. Register helpers `ftm_read()`, `ftm_write()`, and `FTM_FIELD_UPDATE()` abstract endian-aware MMIO. Hardware setup/cleanup is in `ftm_quaddec_init()` and `ftm_quaddec_disable()`. Counter callbacks include count read/write, fixed function/action reads, and prescaler enum read/write.

Control flow: probe allocates a managed counter, maps the memory resource, reads optional `big-endian`, fills one `counter_count`, two `counter_signal`s, two both-edge synapses, and a `prescaler` enum extension, initializes the hardware, registers a devm cleanup action to disable it, and calls `devm_counter_add()`. Writes to `count` only accept zero and reset CNT; prescaler writes unlock write protection, update `FTM_SC`, re-lock, and reset the counter.

State and persistence: hardware registers hold count, prescaler, modulo, and quadrature enable state. Driver state is only endian flag and mutex. Configuration is volatile and reset at probe; devm cleanup disables FTM mode and QDCTRL.

Dependencies and integration: uses `linux/fsl/ftm.h` register definitions, platform/MMIO APIs, OF matching compatible `fsl,ftm-quaddec`, and the Generic Counter API.

Risks: write-protection transitions must stay mutex-protected. Count write rejecting nonzero values may surprise generic tools. The driver uses `devm_ioremap()` rather than `devm_platform_ioremap_resource()`, so resource request semantics are limited. Endianness must match DT.

Test signals: boot/probe on compatible hardware, sysfs count/function/action/prescaler reads, writing prescaler values resets the count, writing count `0` resets, writing nonzero count returns `-EINVAL`, and removal disables quadrature mode.
