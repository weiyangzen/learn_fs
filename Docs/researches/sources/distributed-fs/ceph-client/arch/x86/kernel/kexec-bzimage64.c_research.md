# sources/distributed-fs/ceph-client/arch/x86/kernel/kexec-bzimage64.c

Purpose: Implements the file-based kexec loader for 64-bit x86 bzImage kernels. It validates bzImage protocol requirements, allocates kexec segments for purgatory, boot parameters, kernel, initrd, and optional metadata, then prepares purgatory registers for entering the new kernel.

Important APIs/types/functions: exposes `kexec_bzImage64_ops` with `.probe`, `.load`, `.cleanup`, and optional `.verify_sig`. Key helpers are `bzImage64_probe()`, `bzImage64_load()`, `bzImage64_cleanup()`, `setup_boot_parameters()`, `setup_cmdline()`, `setup_initrd()`, `setup_e820_entries()`, `setup_rng_seed()`, EFI setup helpers, `setup_dtb()`, `setup_ima_state()`, and `setup_kho()`. Loader-private state is `struct bzimage64_data`.

Control flow: probe checks file length, boot signature, `HdrS`, protocol >= 2.12, high-load bzImage flags, 64-bit support, above-4G loading, EFI bitness, and 5-level paging compatibility. Load computes setup-sector size, validates command-line length including crash additions, optionally loads crash backup and dm-crypt key segments, loads purgatory, allocates a combined bootparams/cmdline/EFI/setup-data buffer, adds it as a segment, adds the protected-mode kernel payload, optionally adds initrd, writes command line pointers, sets loader type, patches purgatory `entry64_regs`, and fills boot parameters from current boot state.

State and persistence: data persists only in the staged `kimage` until execution or cleanup. The bootparams buffer is stored in `bzimage64_data` so cleanup can free it after the kexec core copies segments. Setup-data chain entries may carry RNG seed, EFI, DTB, IMA, and KHO handover metadata to the next kernel.

Dependencies and integration points: integrates with generic kexec file load APIs, x86 boot protocol structures, e820/crash memory setup, EFI runtime map copying, FDT, IMA kexec buffer, kexec handover, random subsystem, sysfb screen info, purgatory symbol patching, and optional PE signature verification.

Risks: command-line sizing must include crash `elfcorehdr=` and `dmcryptkeys=` additions. EFI and setup-data offsets must remain aligned and non-overlapping. Carrying runtime maps, DTB, IMA, and KHO data requires correct setup-data chaining. Loading kernels incompatible with current 5-level paging or 32-bit EFI is explicitly rejected.

Test signals: kexec-file tests should cover normal and crash kernels, initrd/no-initrd, long command lines near protocol limits, EFI runtime services, forced DTB carryover, IMA buffer handoff, KHO enabled and disabled, RNG initialized and uninitialized, 5-level paging incompatibility, and signature verification when configured.
