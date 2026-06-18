## sources/distributed-fs/ceph-client/arch/x86/boot/compressed/efi.h

### Purpose
`compressed/efi.h` defines the compressed boot environment's private EFI types, GUIDs, memory descriptors, system table layouts, and soft-reserve helper declarations.

### Important APIs, Types, And Functions
It defines `efi_guid_t`, `EFI_GUID()`, ACPI and unaccepted-memory GUID constants, loader signatures, `efi_table_hdr_t`, memory types and attributes, `efi_memory_desc_t`, `efi_early_memdesc_ptr()`, 32-bit and 64-bit config/system table structures, `struct efi_unaccepted_memory`, `efi_guidcmp()`, and `efi_soft_reserve_enabled()`.

### Control Flow
This header has no runtime control flow beyond inline helpers. `efi_early_memdesc_ptr()` performs descriptor-size-indexed pointer arithmetic, `efi_guidcmp()` wraps `memcmp`, and `efi_soft_reserve_enabled()` gates the external soft-reserve query behind `CONFIG_EFI_SOFT_RESERVE`.

### State, Persistence, And Dependencies
No mutable state is owned here. It depends on basic integer types, `guid_t`, `memcmp`, and build-time `CONFIG_EFI`.

### Integration Points
Included by compressed `efi.c`, `acpi.c`, `kaslr.c`, `mem.c`, and `misc.h` so early code can inspect EFI data without pulling in kernel-proper EFI namespaces, which the header explicitly forbids.

### Risks
The private structure definitions must match UEFI layout exactly for both 32-bit and 64-bit firmware. Namespace guards prevent accidental inclusion conflicts with full kernel EFI headers.

### Test Signals
Compile EFI and non-EFI compressed boot, validate descriptor walking against known EFI memory maps, compare GUID matching for ACPI/unaccepted tables, and test soft-reserve filtering.
