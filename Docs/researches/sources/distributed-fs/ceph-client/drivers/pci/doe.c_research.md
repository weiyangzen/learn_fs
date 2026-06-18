# sources/distributed-fs/ceph-client/drivers/pci/doe.c

## Purpose
Implements PCIe Data Object Exchange mailbox support. It discovers DOE extended capabilities, creates ordered mailbox workers, caches supported protocols, exposes supported features via sysfs, and provides synchronous request/response exchange through `pci_doe()`.

## Important APIs, Types, And Functions
Main types are opaque `struct pci_doe_mb`, `struct pci_doe_feature`, and internal stack-allocated `struct pci_doe_task`. Public functions are `pci_doe()`, `pci_find_doe_mailbox()`, `pci_doe_init()`, `pci_doe_destroy()`, `pci_doe_disconnected()`, plus sysfs init/teardown helpers. Important internals include `pci_doe_abort()`, `pci_doe_send_req()`, `pci_doe_recv_resp()`, `doe_statemachine_work()`, and `pci_doe_cache_features()`.

## Control Flow
`pci_doe_init()` scans PCI extended capabilities and creates a mailbox for each DOE capability. Creation allocates an ordered workqueue, aborts to reset the mailbox, and runs DOE discovery to populate an xarray of supported features. `pci_doe()` builds a stack task, queues it, waits for completion, and returns response length or errno. The worker sends headers/payload, starts GO, polls for ready/error/timeout, reads the response while acknowledging dwords, and aborts on failures.

## State And Persistence
Per-device mailboxes live in `pdev->doe_mbs`. Each mailbox persists its capability offset, feature xarray, waitqueue, ordered workqueue, cancel/dead flags, and optional sysfs attributes. Task state is per call and destroyed after completion.

## Dependencies And Integration Points
Depends on PCI config-space accessors, PCI DOE register definitions, xarray, workqueues, waitqueues, sysfs, and consumers such as CXL/SPDM protocols that locate mailboxes with `pci_find_doe_mailbox()`.

## Risks
The mailbox has no hardware interrupt path and relies on polling. Firmware/OS contention is only detected indirectly through busy/error status. Partial payload dword handling requires caller endian discipline. Abort failure marks a mailbox dead. Destroy/disconnect must cancel queued work before device removal.

## Test Signals
Exercise DOE discovery sysfs entries, `pci_find_doe_mailbox()` for discovery and vendor protocols, successful and short responses, oversized payload rejection, busy/error/timeout abort paths, hot-remove cancellation, and concurrent callers serialized by the ordered workqueue.
