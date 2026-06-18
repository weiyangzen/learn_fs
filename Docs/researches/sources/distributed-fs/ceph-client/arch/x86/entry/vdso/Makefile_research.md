## sources/distributed-fs/ceph-client/arch/x86/entry/vdso/Makefile

Purpose: top-level Kbuild file for x86 vDSO support. It builds kernel-side vDSO mapping/fixup objects and descends into architecture-width-specific vDSO image directories.

Important build objects: always builds `vma.o` and `extable.o`; conditionally builds `vdso32-setup.o` for `CONFIG_COMPAT_32`, `vdso64/` for `CONFIG_X86_64`, and `vdso32/` for `CONFIG_COMPAT_32`.

Control flow: Kbuild aggregates regular kernel objects separately from the image-producing subdirectories. The per-ABI Makefiles handle actual vDSO shared-object linkage.

State/persistence: produces kernel objects and vDSO image artifacts consumed by `vma.c` and process exec setup. No runtime state is defined in the Makefile.

Integration points: Kbuild, compat settings, vDSO image linker scripts, vDSO exception handling, and process additional-page setup.

Risks: missing subdirectory inclusion removes user-visible ABI symbols or mapping support. Test signals include x86_64, x32, and IA32 compat builds, boot with vDSO enabled/disabled, and ABI symbol checks with readelf.
