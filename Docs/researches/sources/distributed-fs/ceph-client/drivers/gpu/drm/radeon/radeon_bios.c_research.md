# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_bios.c

Purpose: locates, copies, validates, and classifies the Radeon video BIOS image from ACPI, PCI ROM, VRAM, disabled-ROM hardware paths, or platform ROM resources.

Important APIs/functions: public `radeon_get_bios` orchestrates BIOS retrieval and validates the result. Retrieval helpers include `radeon_atrm_get_bios`, `radeon_acpi_vfct_bios`, `igp_read_bios_from_vram`, `radeon_read_bios`, `radeon_read_disabled_bios`, and `radeon_read_platform_bios`. ASIC-family-specific disabled-ROM readers include `ni_read_disabled_bios`, `r700_read_disabled_bios`, `r600_read_disabled_bios`, `avivo_read_disabled_bios`, and `legacy_read_disabled_bios`. `radeon_atrm_call` fetches ACPI ATRM chunks.

Control flow: `radeon_get_bios` tries ACPI ATRM first for discrete hybrid GPUs, then ACPI VFCT, IGP VRAM copy, normal PCI ROM mapping, disabled-ROM register sequences, and platform ROM. After a candidate image is copied into `rdev->bios`, it checks the `0x55 0xaa` signature, rejects non-x86 ROMs, records `bios_header_start`, and sets `rdev->is_atom_bios` based on the `ATOM`/`MOTA` marker. Disabled-ROM paths save relevant display, bus, ROM, GPIO, PLL, and power registers, temporarily enable ROM access and disable conflicting display/VGA paths, read via `radeon_read_bios`, then restore registers.

State and persistence: allocates and owns `rdev->bios` in kernel memory, sets `rdev->bios_header_start`, and marks `rdev->is_atom_bios`. Temporarily mutates GPU registers while reading disabled ROMs but restores saved values before returning. ACPI table references are released with `acpi_put_table`; PCI ROM mappings are unmapped after copy. No disk persistence exists.

Dependencies and integration: depends on Linux PCI ROM mapping/resource APIs, ACPI ATRM/VFCT table access, I/O remapping, Radeon register definitions/macros, `radeon_card_posted`, and BIOS access macros such as `RBIOS8/16`. It feeds all later COMBIOS/AtomBIOS parsing, clock discovery, display setup, and PM table parsing.

Risks: hardware register sequencing is ASIC-specific and can affect display or ROM access if not restored exactly. Several firmware sources copy up to fixed or firmware-declared sizes and rely on signature checks after allocation. ACPI ATRM scanning must manage PCI device references correctly. VFCT parsing validates offsets but still trusts firmware structure contents. Failure to find a BIOS prevents normal driver initialization paths that require firmware tables.

Test signals: boot logs showing `ATOMBIOS detected` or `COMBIOS detected`; hybrid GPU systems using ATRM/VFCT; IGP systems booted behind discrete primary GPUs; ASIC-family tests where ROM BAR is initially disabled; validation of register restoration after failed and successful reads; negative tests for bad signatures, non-x86 ROM markers, and truncated ACPI VFCT entries.
