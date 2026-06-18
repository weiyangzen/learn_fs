<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/bootparam.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/bootparam.h

Purpose: Defines the x86 boot protocol's main zeropage structures, setup header, load flags, e820 zeropage capacity, EFI/APM/EDD/screen/IST embeddings, and hardware subarchitecture enum.

Important APIs/types/functions: `RAMDISK_*`, `LOADED_HIGH`, `KASLR_FLAG`, `QUIET_FLAG`, `CAN_USE_HEAP`, `XLF_*`, `struct setup_header`, `struct sys_desc_table`, `struct olpc_ofw_header`, `struct efi_info`, `E820_MAX_ENTRIES_ZEROPAGE`, `JAILHOUSE_SETUP_REQUIRED_VERSION`, `struct boot_params`, and `enum x86_hardware_subarch`.

Control flow: Bootloaders populate `boot_params` and `setup_header`; early kernel code reads flags and addresses to decide relocation, command line, initrd, KASLR, 5-level paging, EFI handoff, memory encryption, setup-data chain traversal, e820 import, and subarchitecture dispatch.

State and persistence behavior: The zeropage is the persistent handoff state from bootloader/firmware to kernel entry. Some fields are obsolete but preserved; `sentinel` protects against bootloaders copying too much stale data.

Dependencies and integration points: Depends on setup-data, screen, APM, EDD, IST, and EDID UAPI structures. Integrates with boot/compressed kernel, EFI, BIOS E820, OLPC OFW, tboot, confidential-computing blobs, Jailhouse, Xen PV subarch, and early platform quirks.

Risks and test signals: Risks include packed-layout drift, offset changes, bootloader incompatibility, incorrect xloadflags interpretation, and e820 truncation. Test BIOS and EFI boots, 32-bit and 64-bit boot protocol versions, initrd above 4G, KASLR, 5-level paging, memory encryption, setup_data extensions, and struct offset assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/bootparam.h -->
