# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_lan_hmc.c

## Purpose
`i40e_lan_hmc.c` builds the LAN-specific HMC layer above the generic HMC allocator. It sizes LAN/FCoE context memory, creates and destroys direct or paged HMC backing store, programs LAN FPM registers, resolves queue-context virtual addresses, and packs Tx/Rx queue context structs into the hardware bit layout.

## Important APIs, types, and functions
- Sizing helpers: `i40e_align_l2obj_base()` and `i40e_calculate_l2fpm_size()`.
- Lifecycle APIs: `i40e_init_lan_hmc()`, `i40e_configure_lan_hmc()`, and `i40e_shutdown_lan_hmc()`.
- Object management: `i40e_create_lan_hmc_object()`, `i40e_delete_lan_hmc_object()`, and static wrappers around generic HMC remove helpers.
- Context description: `struct i40e_context_ele`, `I40E_HMC_STORE`, `i40e_hmc_txq_ce_info[]`, and `i40e_hmc_rxq_ce_info[]`.
- Bit packing helpers: `i40e_write_byte()`, `i40e_write_word()`, `i40e_write_dword()`, `i40e_write_qword()`, `i40e_set_hmc_context()`, and `i40e_clear_hmc_context()`.
- Queue-context APIs: `i40e_clear_lan_tx_queue_context()`, `i40e_set_lan_tx_queue_context()`, `i40e_clear_lan_rx_queue_context()`, and `i40e_set_lan_rx_queue_context()`.

## Control flow and behavior
Initialization sets the HMC signature and PF function id, allocates the LAN object-info array, reads maximum counts and object-size exponents from GLHMC registers, validates requested Tx/Rx/FCoE counts, lays object bases sequentially with 512-byte alignment, computes total L2 FPM size, and allocates the software SD table sized in 2 MiB units. The aggregate `I40E_HMC_LAN_FULL` object records the total FPM span for later SD creation.

Configuration chooses the backing model. Direct-preferred and direct-only attempt a single direct SD sized to the full LAN object; direct-preferred falls back to paged if direct allocation fails. Paged-only creates a paged SD and allocates PD/backing pages as needed. After backing store is ready, the function writes GLHMC base/count registers for Tx, Rx, FCoE DDP contexts, and FCoE filters, using 512-byte base units.

Object creation validates the HMC info, range, and signature; computes SD and PD index ranges; adds each required SD; adds PD backing pages for paged SDs; and writes PFHMC SD entries once software backing is initialized. Error paths unwind already-created PDs/SDs. Deletion walks PDs first for paged backing pages, then walks SDs and removes direct or paged SD resources.

Queue context APIs resolve an object VA from HMC metadata and either zero the context bytes or pack a caller-provided `struct i40e_hmc_obj_txq`/`rxq` into the hardware layout. The packing table stores each field's source offset/size, hardware width, and bit LSB; width-specific writers mask source values, shift them into place, update little-endian destination words, and preserve unrelated bits.

## State and persistence
The file initializes and tears down `hw->hmc`, including `hmc_obj`, `sd_table`, object bases/counts/sizes, DMA backing pages, and virtual bookkeeping memory. It writes persistent-in-device-register state in PFHMC SD registers and GLHMC LAN/FCoE base/count registers until reset or shutdown. Queue context memory is DMA-backed HMC state consumed by device hardware.

## Dependencies and integration points
It depends on generic HMC helpers from `i40e_hmc.c`, structures from `i40e_lan_hmc.h`, allocation helpers, register/MMIO accessors, and `i40e_hw` register/capability definitions. Queue setup elsewhere in the driver calls the set/clear context APIs when enabling or resetting rings.

## Risks and edge cases
- Object range calculations assume valid nonzero counts and correctly initialized object sizes.
- Direct-preferred fallback must leave no partially programmed direct resources before trying paged mode.
- The deletion path always frees top-level SD and object virtual memory in `i40e_shutdown_lan_hmc()` even if `i40e_delete_lan_hmc_object()` returns an error.
- Context packers rely on unaligned casts from struct fields; the explicit little-endian destination operations handle byte order, but source struct layout must match the tables exactly.
- `i40e_hmc_get_object_va()` does not explicitly test `sd_entry->valid` or `pd_entry->valid`; callers rely on prior HMC configuration.

## Test signals
Probe and remove cycles are the main integration test. Additional signals include direct and paged HMC model coverage, forced allocation failures to exercise unwinds, queue setup/teardown with Tx/Rx context set and clear, register traces for GLHMC/PFHMC writes, and traffic tests proving queue contexts point at valid descriptors.
