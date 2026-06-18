# sources/distributed-fs/ceph-client/arch/s390/kernel/machine_kexec_file.c

Purpose: s390 `kexec_file_load` common component assembly, signature verification, purgatory symbol patching, initrd placement, IPL report placement, and purgatory relocation handling.

Important APIs and state: exports `kexec_file_loaders[]`, optional `s390_verify_sig()`, `kexec_file_add_components()`, `arch_kexec_apply_relocations_add()`, and `arch_kimage_file_post_load_cleanup()`. `struct s390_load_data` carries kernel buffer, parm area, memory size, and report during load.

Control flow: signature verification is enforced only when secure IPL is active, requiring module-signature marker, PKCS#7 signature metadata, and secondary or platform keyring success. Component assembly initializes an IPL report, delegates kernel loading, validates parm area and command line capacity, copies command line and crash oldmem data, adds initrd and purgatory, patches purgatory symbols such as `kernel_entry`, `kernel_type`, `crash_start`, and `crash_size`, handles the restart PSW special case for memory 0, then writes the IPL report as another kexec buffer and stores its lowcore pointer.

Dependencies and integration: depends on loader ops from ELF/raw image files, generic kexec buffers/purgatory, verification keyrings, boot data, lowcore offsets, crash resources, and IPL report/certificate helpers in `ipl.c`.

Risks and test signals: secure IPL signature parsing, command-line bounds, certificate list walking, crash offset arithmetic, and purgatory relocations are key. Test signed/unsigned secure boot, platform keyring fallback, initrd placement, malformed signature trailers, relocation types, cleanup freeing `image->arch.ipl_buf`, and normal/crash kexec-file boots.
