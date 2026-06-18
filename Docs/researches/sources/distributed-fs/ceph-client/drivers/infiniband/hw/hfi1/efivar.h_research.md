# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/efivar.h

Purpose: declaration header for HFI1 EFI variable access.

Important APIs/types: includes Linux EFI and HFI1 core definitions, and declares `read_hfi1_efi_var(struct hfi1_devdata *dd, const char *kind, unsigned long *size, void **return_data)`.

Control flow: callers use this function when they need per-adapter EFI-backed configuration data. The implementation allocates the returned buffer and reports the byte count.

State and persistence: no state is stored in the header. The API exposes firmware-persistent data as caller-owned kernel memory.

Dependencies and integration: integrated with platform configuration loading code and the HFI1 device data model.

Risks: caller must free returned data on success and treat failure outputs as empty. The header includes `hfi.h`, which may be heavier than a forward declaration but gives the implementation and callers a consistent `struct hfi1_devdata` view.

Test signals: compile coverage, EFI config read integration, and caller cleanup tests.
