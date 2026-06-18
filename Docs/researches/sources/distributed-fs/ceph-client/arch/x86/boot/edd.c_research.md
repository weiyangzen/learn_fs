# sources/distributed-fs/ceph-client/arch/x86/boot/edd.c

Purpose: queries BIOS Enhanced Disk Drive information and optional MBR signatures for handoff in `boot_params`.

Important APIs and state: under `CONFIG_EDD` or `CONFIG_EDD_MODULE`, exports `query_edd()`. Helpers `get_edd_info()`, `read_mbr()`, and `read_mbr_sig()` use INT 13h. State is persisted in `boot_params.eddbuf`, `eddbuf_entries`, `edd_mbr_sig_buffer`, and `edd_mbr_sig_buf_entries`.

Control flow: command-line `edd=off/on/skipmbr/skip` controls probing. For BIOS drives `0x80` through the MBR signature max, it checks extensions, stores EDD params up to `EDDMAXNR`, and optionally reads the first sector to collect valid MBR signatures using heap space.

Dependencies and integration: called by `main()` when configured. Depends on BIOS calls, heap availability for MBR buffers, early strings, and Linux EDD structures.

Risks and test signals: buggy BIOSes can hang EDD probing, hence the user-facing `edd=off` hint. Heap shortage disables MBR signature reads. Test with EDD on/off/skipmbr, BIOS disks with and without valid MBR magic, and quiet vs non-quiet output.
