# sources/distributed-fs/ceph-client/drivers/acpi/apei/ghes.c

## Purpose
Implements ACPI Generic Hardware Error Source handling. GHES is the firmware-first runtime path for reading CPER error status blocks, reporting them, dispatching subsystem recovery, and registering notification mechanisms.

## Important APIs, Types, And Functions
Exports `ghes_estatus_pool_init()`, `ghes_estatus_pool_region_free()`, vendor notifier registration helpers, CXL CPER work registration helpers, `ghes_get_devices()`, and GHES report-chain registration. Core functions include `ghes_new()`, `ghes_read_estatus()`, `ghes_clear_estatus()`, `ghes_do_proc()`, `ghes_proc()`, `ghes_in_nmi_queue_one_entry()`, and `ghes_probe()`.

## Control Flow
HEST creates `GHES` platform devices, and this driver probes enabled generic error sources. Probe validates notification type, maps the error status address and optional GHESv2 ack register, installs the chosen notifier path, links the device for EDAC, and handles pending errors. Runtime handlers read a CPER status block, validate it, panic on fatal severity, rate-limit duplicate logs through an RCU cache, process each CPER section, clear firmware status, and acknowledge GHESv2 if needed. NMI-like paths copy records into a gen_pool-backed llist and defer processing to irq_work.

## State And Persistence
State includes per-source `struct ghes`, HED/SEA/NMI lists, EDAC device list, fixmap locks, gen_pool for atomic copies/work items, RCU error-status cache, CXL FIFOs, and vendor notifier chain. Errors are transient; persistence is only through downstream pstore or subsystem logging.

## Dependencies And Integration Points
Integrates ACPI HEST/GHES, APEI register helpers, CPER parsers, memory failure, AER, CXL event handling, vendor CPER notifiers, EDAC, SDEI, NMI, HED, IRQ, timers, RAS tracing/logging, and firmware-first `_OSC` setup.

## Risks
Important risks are atomic-context memory availability, fixmap serialization, duplicate/flooded CPER reports, malformed CPER lengths, fatal-error ordering, synchronous error SIGBUS behavior, FIFO overflow for CXL work, and RCU/list lifetime on notifier removal.

## Test Signals
Validate all notification types, CPER length/header rejection, fatal panic path, corrected/uncorrected ratelimiting, memory-failure queueing for sync and async errors, AER recovery queueing, CXL event FIFO overflow handling, vendor notifier dispatch, GHESv2 ack writes, and probe/remove cleanup.
