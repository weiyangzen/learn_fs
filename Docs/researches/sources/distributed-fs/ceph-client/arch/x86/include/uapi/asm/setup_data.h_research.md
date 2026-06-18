<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/setup_data.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/setup_data.h

Purpose: Defines extensible x86 boot setup-data node types and payload structures for firmware/device-tree/EFI/Jailhouse/confidential-computing/IMA/RNG seed/kexec handover data.

Important APIs/types/functions: `SETUP_*`, `SETUP_INDIRECT`, `SETUP_TYPE_MAX`, `struct setup_data`, `struct setup_indirect`, `struct boot_e820_entry`, `struct jailhouse_setup_data`, `struct ima_setup_data`, and `struct kho_data`.

Control flow: Early boot walks the linked `setup_data` list from `boot_params.hdr.setup_data`; indirect nodes reference payloads elsewhere; type-specific handlers import extra e820 entries, DTB, PCI, EFI, Apple properties, Jailhouse data, CC blobs, IMA buffers, RNG seeds, or kexec handover metadata.

State and persistence behavior: Setup-data nodes are bootloader-to-kernel handoff state. Kexec handover and IMA payloads can describe data preserved across kernel transitions.

Dependencies and integration points: Depends on Linux UAPI types. Integrates with boot protocol, EFI, device tree, confidential computing, Jailhouse guests, IMA across kexec, RNG seeding, and kexec handover objects.

Risks and test signals: Risks include unknown type handling, indirect pointer validation, length truncation, and packed layout drift. Test boot with extended e820, EFI setup data, CC blob, IMA kexec buffer, RNG seed, KHO metadata, and malformed setup_data chains.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/setup_data.h -->
