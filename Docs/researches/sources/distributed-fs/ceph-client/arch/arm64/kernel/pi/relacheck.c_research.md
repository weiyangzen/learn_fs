# sources/distributed-fs/ceph-client/arch/arm64/kernel/pi/relacheck.c

Purpose: this host-side build utility validates relocation records in early position-independent ARM64 objects. It rejects unexpected absolute 64-bit relocations in allocatable non-executable data and converts allowed `.rodata.prel64` absolute relocations to `R_AARCH64_PREL64`.

Important APIs and state: the process-level globals `ehdr`, `shdr`, `strtab`, and `swap` hold the mapped ELF header, section headers, string table, and endian-conversion flag. `swab_elfxword()`, `swab_elfword()`, and `swab_elfhword()` abstract host/target byte order. `main()` opens the temporary object passed as `argv[1]`, mmaps it writable/shared, scans `SHT_RELA` sections, and reports errors using `argv[2]` as the display name.

Control flow: after argument and file setup, `main()` chooses `swap` by comparing ELF data encoding to host order. For each RELA section, it examines the target section via `sh_info`; only allocatable data sections, not executable sections, are guarded. If the target section name contains `.rodata.prel64`, ABS64 relocations are rewritten in-place by toggling the relocation type bits from `R_AARCH64_ABS64` to `R_AARCH64_PREL64`. Otherwise an ABS64 relocation is a fatal error: the tool prints a diagnostic, closes and unlinks the object, and exits failure.

Dependencies and integration: uses libc, POSIX file/mmap APIs, and ELF constants. It is intended for the kernel build pipeline around the `pi/` objects, pairing with `pi.h` and `__prel64_initconst` to enforce early relocation discipline.

Risks: the utility trusts basic ELF layout enough to mmap and index headers, so it is for controlled build inputs rather than hostile files. The `.rodata.prel64` match is substring based but scoped to the target section name. Unlinking the temporary output is intentional build hygiene but can obscure later inspection if logs are insufficient.

Test signals: build failure on new accidental absolute references is the primary signal. Positive tests include `.rodata.prel64` entries being converted and endian-swapped objects being handled correctly. Changes should be checked by inspecting relocations with `readelf -r` before and after the tool.
