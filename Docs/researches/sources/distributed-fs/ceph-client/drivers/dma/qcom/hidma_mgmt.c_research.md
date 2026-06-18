# sources/distributed-fs/ceph-client/drivers/dma/qcom/hidma_mgmt.c

Purpose: platform management driver for Qualcomm HIDMA common hardware registers. It validates and programs global DMA QoS, max burst, max transaction, reset-timeout, hardware-version, and channel arbitration settings before per-channel HIDMA engines operate.

Important APIs/types/functions: `struct hidma_mgmt_dev` is defined in `hidma_mgmt.h`. `hidma_mgmt_setup` is exported and re-applies all validated settings. `hidma_mgmt_probe` reads ACPI/device properties and module-param overrides, maps the management register block, starts hardware, initializes sysfs via `hidma_mgmt_init_sys`, and enables runtime PM. Module parameters allow overriding max write/read request sizes and max write/read transactions.

Control flow: probe enables runtime PM, maps resource 0, obtains IRQ presence, allocates management state, reads `dma-channels`, `channel-reset-timeout-cycles`, `max-write-burst-bytes`, `max-read-burst-bytes`, `max-write-transactions`, and `max-read-transactions`, allocates per-channel priority/weight arrays, calls `hidma_mgmt_setup`, sets `HIDMA_CFG_OFFSET` bit 0 to start hardware, creates sysfs knobs, and stores drvdata. `hidma_mgmt_setup` validates power-of-two 128..1024 burst sizes, transaction masks, priority values, and weight range, then writes max bus request length, transaction limits, QoS registers per channel, reset timeout, and reads hardware revision.

State/persistence: management values are kept in `hidma_mgmt_dev` and programmed to MMIO registers. Sysfs setters update the in-memory value, call setup, and roll back on validation/programming failure.

Dependencies/integration: uses platform property APIs, runtime PM, MMIO, module parameters, `hidma_mgmt_sys.c` for sysfs, and ACPI ID `QCOM8060`. Per-channel `hidma.c` devices depend on this global management block being configured on systems that expose it.

Risks: probe obtains an IRQ but does not request it in this file, so the IRQ resource acts as a presence/firmware contract. Priority/weight arrays are zero-initialized, and setup converts zero weight to one. Read-only-looking sysfs attributes are still wired with store callbacks internally, but modes mostly restrict writes except per-channel knobs.

Test signals: invalid DT/ACPI properties reject probe; module parameter overrides program expected registers; sysfs changes update registers and roll back on invalid values; runtime PM balances on setup; hardware revision appears in logs.
