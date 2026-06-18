# sources/distributed-fs/ceph-client/arch/x86/boot/header.S

Purpose: defines the x86 boot sector/setup header, optional EFI PE headers, boot protocol fields, decompression size calculations, and real-mode setup entry that reaches C `main()`.

Important APIs and state: exports labels such as `sentinel`, `hdr`, `_start`, `realmode_swtch`, `kernel_version`, `start_of_setup`, and `die`. Header fields include load flags, command-line pointer, ramdisk fields, setup_data, preferred address, xloadflags, payload offset/length, init size, and handover offset. EFI builds emit DOS/PE/COFF optional headers and `.setup`, `.compat`, `.text`, optional `.sbat`, and `.data` section records.

Control flow: execution begins in 16-bit setup code, normalizes segments/stack, handles ancient loader stack quirks, far-returns to normalize `%cs`, verifies setup signature, clears BSS, calls C `main()`, and halts on corruption. Build-time macros compute safe in-place decompression offsets for supported compressors and choose `INIT_SIZE`.

Dependencies and integration: central to Linux x86 boot protocol compatibility and EFI stub entry. Depends on generated zoffset/voffset symbols, `boot.h`, kernel config flags, compressed linker symbols, and the C setup code.

Risks and test signals: changing offsets can break bootloaders that expect exact protocol field positions. PE metadata must match compressed linker layout. Test BIOS and EFI boots, mixed EFI, handover protocol, SBAT builds, legacy command-line loaders, and `tools/build` validation of bzImage headers.
