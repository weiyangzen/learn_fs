# sources/distributed-fs/ceph-client/arch/s390/kernel/kexec_image.c

Purpose: fallback/raw image loader for `kexec_file_load` on s390 when no reliable image format probe is possible.

Important APIs: `s390_kexec_image_ops` always probes successfully, loads through `s390_image_load()`, and optionally uses `s390_verify_sig`. `kexec_file_add_kernel_image()` adds the entire kernel buffer as one kexec buffer.

Control flow and state: normal images are loaded at physical 0; crash images are offset by `crashk_res.start`. The function sets `data->kernel_buf`, `data->kernel_mem`, `data->parm` at `PARMAREA`, and increases `data->memsz` by image length. The loaded image is added to the IPL report as signed and verified.

Dependencies and integration: this is the second loader in `kexec_file_loaders[]` after ELF. It relies on `kexec_file_add_components()` for command line, initrd, purgatory, and IPL report assembly.

Risks and test signals: because probe always succeeds, validation is deferred to later boot/purgatory behavior. Test loader ordering, raw image kexec, crash image offsetting, too-small parm area rejection in the common component path, and secure signature behavior.
