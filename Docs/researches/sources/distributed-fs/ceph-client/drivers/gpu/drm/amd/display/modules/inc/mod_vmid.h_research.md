# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/modules/inc/mod_vmid.h

Purpose: declares the virtual memory ID helper module used to map page table bases to limited VMID slots for display use.

Important APIs/types: `MAX_VMID` is 16. `struct mod_vmid` is opaque. Public functions are `mod_vmid_get_for_ptb(struct mod_vmid *, uint64_t ptb)`, `mod_vmid_reset`, `mod_vmid_create`, and `mod_vmid_destroy`.

Control flow role: callers create the module with `struct dc`, number of VMIDs, and virtual-address-space config, request a VMID for a PTB, and reset/destroy when address-space state changes or the device is torn down.

State and persistence: implementation owns the mapping cache between PTB values and VMID identifiers. Reset clears that mapping.

Dependencies and integration: includes `dc.h` and references `dc_virtual_addr_space_config`, tying it to core display virtual memory setup.

Risks: VMID exhaustion, stale PTB mappings after reset-sensitive events, and incorrect `num_vmid` bounds can affect GPU memory addressing. Header does not expose error signaling beyond an 8-bit return value.

Test signals: PTB reuse returns stable VMIDs, reset clears mappings, `num_vmid` boundary behavior including `MAX_VMID`, and destroy after partial create failures.
