# sources/distributed-fs/ceph-client/drivers/scsi/smartpqi/smartpqi_sis.h

Purpose: this header exposes the SmartPQI SIS interface functions implemented in `smartpqi_sis.c` to the rest of the SmartPQI driver.

Important APIs, types, and functions: it declares readiness checks, firmware-running and kernel-up queries, controller property and PQI capability discovery, base-structure initialization, interrupt mode selection, shutdown/reset/quiesce operations, scratch register access, product-id readout, firmware triage wait, controller logging support/wait, kdump notification, and `sis_verify_structures()`. It also declares the tunable `sis_ctrl_ready_timeout_secs`.

Control flow: consumers include this header after `struct pqi_ctrl_info` and `enum pqi_ctrl_shutdown_reason` are visible from `smartpqi.h`. Calls normally occur in controller initialization order: wait ready, get properties, get capabilities, initialize base structure, enable interrupt mode, then proceed to PQI setup. Reset and crash paths call the doorbell helpers later in the lifecycle.

State and persistence: this header owns no state. It exposes functions that mutate or observe MMIO state through `pqi_ctrl_info` and a single exported timeout variable.

Dependencies and integration: it is tightly coupled to SmartPQI internal controller types and to the SIS register layout in `smartpqi.h`. It has include guards and no standalone Linux includes, relying on including translation units for type visibility.

Risks: because it exposes low-level controller lifecycle operations, mismatched ordering by callers can leave firmware in the wrong mode. The external timeout variable is global across controllers, so module parameter or debug modification affects all adapters.

Test signals: build coverage should catch prototype drift with `smartpqi_sis.c`; runtime testing should verify each declared operation is called in expected probe, resume, shutdown, kdump, and reset paths.
