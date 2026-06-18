# sources/distributed-fs/ceph-client/drivers/acpi/acpica/evgpeblk.c

## Purpose
Creates, installs, initializes, and deletes GPE register blocks. It allocates per-register and per-GPE metadata, disables and clears hardware on creation, links blocks to interrupt descriptors, discovers matching `_Lxx`/`_Exx` methods, auto-enables eligible runtime GPEs, and frees block resources on deletion.

## Important APIs, Types, And Functions
- `acpi_ev_create_gpe_block` validates address space, allocates a `struct acpi_gpe_block_info`, creates substructures, installs the block, walks methods, and returns the block.
- `acpi_ev_create_gpe_info_blocks` allocates and initializes `acpi_gpe_register_info` and `acpi_gpe_event_info` arrays, computes status/enable register addresses, disables enable registers, and clears status registers.
- `acpi_ev_install_gpe_block` links a block into the proper `acpi_gpe_xrupt_info` list under the events mutex and GPE spin lock.
- `acpi_ev_initialize_gpe_block` marks all GPEs initialized and auto-enables non-wake GPEs with method dispatch.
- `acpi_ev_delete_gpe_block` disables a block, unlinks it, deletes the xrupt if needed, updates global count, and frees arrays.

## Control Flow
Creation validates nonzero register count and memory/IO address space, validates IO blocks, allocates the top-level block, builds metadata arrays, then installs into the interrupt list. Method discovery walks under the GPE device and calls `acpi_ev_match_gpe_method`. Initialization later iterates every event descriptor, ignores wake-only or methodless GPEs, adds a runtime reference to method-backed GPEs, marks them auto-enabled, and records whether polling is needed.

## State And Persistence
Persistent global GPE state includes xrupt block lists, GPE block linked lists, `acpi_current_gpe_count`, per-register addresses/masks, and per-event dispatch flags. Hardware enable/status registers are reset during block creation.

## Dependencies And Integration Points
Uses events mutex, GPE spin lock, xrupt allocation, hardware GPE writes, IO range validation, namespace method walking, GPE method matching, and reference-count enable helpers. It supplies data consumed by interrupt dispatch in `evgpe.c`.

## Risks And Edge Cases
Partial allocation or install failures must free both register and event arrays. Deleting a block must not remove the SCI interrupt descriptor itself, and the code delegates that distinction to xrupt deletion. Auto-enable failures are logged per GPE but do not abort the whole block. Unsupported address spaces and invalid IO ranges reject block creation.

## Test Signals
Exercise zero-register no-op blocks, memory and IO FADT blocks, unsupported space IDs, register address calculations for status versus enable halves, hardware disable/clear writes during creation, method discovery immediately after install, auto-enable counts, polling-needed propagation, and deletion of last versus non-last block on an interrupt.
