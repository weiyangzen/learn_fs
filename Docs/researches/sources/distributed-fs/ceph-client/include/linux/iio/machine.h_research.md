<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/machine.h -->
# sources/distributed-fs/ceph-client/include/linux/iio/machine.h

Purpose: Defines static machine mapping entries that connect IIO provider channels to named consumer devices/channels.

Important APIs/types/functions: `struct iio_map` stores provider channel name, consumer device name, and consumer channel name. `IIO_MAP()` initializes one mapping entry.

Control flow: Board code or mapping tables declare arrays consumed by the IIO map/consumer infrastructure; no runtime behavior exists in the header.

State/persistence: Mapping entries are static configuration and persist as board data.

Dependencies/integration: Used by IIO consumer APIs to resolve provider channels without firmware descriptions.

Risks: String mismatches make consumers fail at runtime; stale maps can silently bind the wrong channel names.

Test signals: Consumer lookup by device/channel, missing-provider error handling, and board boot with expected IIO channel wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/machine.h -->
