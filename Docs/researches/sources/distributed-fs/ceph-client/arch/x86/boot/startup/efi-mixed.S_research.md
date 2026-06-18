# sources/distributed-fs/ceph-client/arch/x86/boot/startup/efi-mixed.S

Purpose: supports invoking 32-bit EFI services and entering a 64-bit kernel from 32-bit EFI firmware in mixed-mode EFI boots.

Important APIs and state: defines `efi32_stub_entry`, local `efi_enter32`, `__efi64_thunk`, `efi32_enable_long_mode`, `efi32_startup`, `efi32_pe_entry`, optional `efi64_stub_entry`, data `efi32_call`, `efi_is64`, and a 6-page page-table buffer `pte`.

Control flow: 32-bit EFI entry clears BSS, extracts `boot_params`, and jumps to startup. `efi32_startup` saves/copies firmware GDT, appends a 64-bit code descriptor, builds identity page tables, enables PAE/LME/paging, records mixed mode, prepares a far-call gate back to 32-bit firmware, and long-jumps to `efi_stub_entry`. `__efi64_thunk` far-calls `efi_enter32`, which converts x86-64 ABI arguments to 32-bit stack arguments, disables paging/long mode, calls firmware, then re-enables long mode.

Dependencies and integration: tied to EFI stub, PE header entries in `header.S`, x86 GDT/MSR/page-table definitions, and identity mappings before virtual-address transition.

Risks and test signals: mode-switching and firmware GDT restoration are fragile; argument truncation is intentional because early identity mappings keep addresses under 4 GiB. Test 64-bit kernel on 32-bit EFI firmware, EFI handover protocol, EFI boot service calls through thunking, and unsupported CPU long-mode return path.
