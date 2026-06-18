## sources/distributed-fs/ceph-client/arch/arm64/boot/Makefile

### Purpose
Builds ARM64 bootable kernel image formats from `vmlinux`, including raw `Image`, compressed variants, FIT image, and EFI zboot support.

### Important APIs, Types, And Functions
Defines `OBJCOPYFLAGS_Image`, `targets`, rules for `Image`, `Image.bz2`, `Image.gz`, `Image.lz4`, `Image.lzma`, `Image.lzo`, `Image.zst`, `Image.xz`, `image.fit`, and EFI zboot variables.

### Control Flow
`Image` is produced by objcopy from `vmlinux`; compression targets depend on `Image` and call standard Kbuild compression commands. `image.fit` depends on `Image` plus the DTB list. EFI zboot includes the EFI libstub zboot makefile and forwards BTI CFI settings.

### State, Persistence, And Dependencies
Persistent artifacts are boot images under `arch/arm64/boot`. Dependencies include `vmlinux`, compression tools, DTB lists, `NM`, objcopy, and EFI libstub machinery.

### Integration Points
Receives recursive calls from `arch/arm64/Makefile` and produces images consumed by bootloaders, installers, and EFI stub flows.

### Risks
Compression tool absence or stale DTB lists breaks specific targets. Objcopy flags intentionally strip notes/comments; changing them affects boot image contents. EFI zboot symbol injection depends on `_kernel_codesize`.

### Test Signals
Build all boot targets, inspect image sizes and `file` output, boot `Image.gz` and `vmlinuz.efi`, and validate FIT includes expected DTBs.
