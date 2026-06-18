# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-devtrace-io.h

## Purpose
Declares trace events for iwlwifi MMIO/PRPH IO, IRQ, MSI-X, and ICT reads.

## Important APIs, Types, and Functions
Events include `iwlwifi_dev_ioread32`, `iwlwifi_dev_iowrite8`, `iwlwifi_dev_iowrite32`, `iwlwifi_dev_iowrite64`, `iwlwifi_dev_iowrite_prph32`, `iwlwifi_dev_iowrite_prph64`, `iwlwifi_dev_ioread_prph32`, `iwlwifi_dev_irq`, `iwlwifi_dev_irq_msix`, and `iwlwifi_dev_ict_read`.

## Control Flow
The header is declarative tracepoint code. IO wrappers and interrupt handlers call these tracepoints when device tracing is enabled.

## State and Persistence Behavior
No driver state is changed; register offsets, values, IRQ vector metadata, and interrupt cause snapshots are recorded in tracing buffers.

## Dependencies and Integration Points
Depends on Linux tracepoints and PCI `msix_entry`. Included through `iwl-devtrace.h`.

## Risks
High-volume IO tracing can be expensive. Format strings must match field widths, and interrupt tracepoints must not add heavy work in hot paths.

## Test Signals
MMIO read/write traces, PRPH read/write traces, legacy IRQ trace, MSI-X cause trace, ICT read trace, and disabled-tracing no-op builds are relevant.
