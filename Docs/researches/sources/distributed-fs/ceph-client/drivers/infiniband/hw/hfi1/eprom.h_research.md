# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/eprom.h

Purpose: declaration header for HFI1 EPROM support.

Important APIs/types: forward-declares `struct hfi1_devdata` and declares `eprom_init()` plus `eprom_read_platform_config()`.

Control flow: probe or chip init calls `eprom_init()` before attempting EPROM-backed platform configuration. Configuration loading calls `eprom_read_platform_config()` and receives allocated data plus size.

State and persistence: no header-local state. The implementation records EPROM availability in `struct hfi1_devdata` and returns caller-owned buffers.

Dependencies and integration: lightweight interface used by platform configuration and chip initialization code.

Risks: callers must handle `-ENXIO` for unavailable EPROM and must free the returned buffer on success. The header has no include guard in this snapshot, so repeated direct inclusion relies on normal include ordering not to cause declaration conflicts; the declarations themselves are idempotent but a guard would be safer.

Test signals: compile coverage for multiple inclusion paths, EPROM absent/present probe, and successful platform config read/cleanup.
