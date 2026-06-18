
# sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/efistub.h

Purpose: private EFI stub ABI header defining mixed-mode-safe protocol unions, boot/runtime service call wrappers, EFI protocol structures, helper macros, global flags, and cross-file prototypes for stub memory, graphics, FDT, initrd, random, secure boot, SMBIOS, KASLR, unaccepted memory, and zboot code.

Important APIs/types/functions: key macros are `efi_table_attr()`, `efi_fn_call()`, `efi_call_proto()`, `efi_bs_call()`, `efi_rt_call()`, `efi_dxe_call()`, logging wrappers, FDT property setters, EFI variable wrappers, and mixed-mode handle/event helpers. It defines EFI boot services, DXE services, memory attribute protocol, text/graphics/file/PCI/Apple/TCG2/CC/SMBIOS/RISC-V boot/LoadFile protocol layouts plus prototypes for all major helper files.

Control flow: the header has no executable top-level flow, but it defines how all stub C files call firmware through native or mixed-mode tables, how output logging is gated, how config-table and file-protocol data is represented, and which functions each architecture must supply.

State and persistence behavior: declares global boot-stub flags and global EFI system/DXE table pointers. Structures mirror firmware tables or configuration-table payloads and are live only during boot or passed to the kernel by pointer.

Dependencies and integration points: depends on Linux EFI definitions, compiler cleanup helpers, architecture EFI wrappers, FDT APIs, sysfb, and arch-specific image alignment/cache/entry functions. It is the integration hub among libstub files and between common code and x86/RISC-V/LoongArch/ARM-specific implementations.

Risks and test signals: ABI risk is high because field order and pointer width in protocol unions must match UEFI native and mixed-mode layouts. Prototype drift breaks cross-arch builds. Test signals are all EFI-stub build matrices, mixed-mode x86 boot, GOP/file/PCI protocol calls, TCG2/CC measurement calls, and compile-time coverage for optional config combinations.
