# sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/response_manager.h

Purpose: Defines LiquidIO response list structures, response ordering classes, and host/firmware request status codes.

Important APIs, types, and functions: `struct octeon_response_list` is a locked list with a pending counter. Response list IDs include ordered, unordered, ordered soft-command, done soft-command, and zombie soft-command lists. Response-order enum values describe ordered, unordered, and no-response requests. Driver and firmware status macros encode major/minor error namespaces, and `FIRMWARE_STATUS_CODE()` maps firmware 16-bit statuses into the host-visible status space. Public functions initialize/delete response lists and process the ordered list.

Control flow: Request-manager code moves fetched soft commands into `OCTEON_ORDERED_SC_LIST`; response-manager code moves them to done/zombie or invokes callbacks; callers interpret `OCTEON_REQUEST_*` values.

State and persistence: The header defines volatile list state only. Status values are protocol-level constants shared with firmware-facing logic.

Dependencies and integration: Requires Linux list, spinlock, atomic primitives, and `struct octeon_device`. It is included by request, response, NIC control, mailbox, and memory-operation files.

Risks: Adding/removing list types or changing status codes would affect cleanup and user-visible control command results. The processing cap protects CPU time but can delay large bursts.

Test signals: Initialization of all list heads/counters, status-code mapping, timeout and interrupted status propagation, and no leak between done/zombie/ordered lists.
