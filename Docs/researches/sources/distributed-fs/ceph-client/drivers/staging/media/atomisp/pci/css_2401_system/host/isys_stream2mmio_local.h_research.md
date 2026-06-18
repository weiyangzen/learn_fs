# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_2401_system/host/isys_stream2mmio_local.h

Purpose: defines Stream2MMIO state snapshot structures.

Important APIs/types/functions: `stream2mmio_sid_state_t` captures receive acknowledgements, pixel width, start/end addresses, stride, number of items, and block-when-no-command for one SID. `stream2mmio_state_t` stores an array of SID states.

Control flow: no direct logic; private helpers fill and print these snapshots.

State and persistence: snapshot-only and caller-owned.

Dependencies and integration: depends on `isys_stream2mmio_global.h` for ID/count types.

Risks and test signals: fixed array size must match the maximum SID enum. Tests should validate state capture for controllers with 8 and 4 active SIDs.
