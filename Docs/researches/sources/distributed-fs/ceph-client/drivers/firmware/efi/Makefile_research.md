# sources/distributed-fs/ceph-client/drivers/firmware/efi/Makefile

Purpose: wires EFI core, optional table/sysfs/runtime facilities, architecture runtime setup, capsule loading, CPER decoders, early console, and libstub into Kbuild.

Important APIs/types/functions: builds core `efi.o`, `vars.o`, `reboot.o`, `memattr.o`, `tpm.o`, and `memmap.o` for `CONFIG_EFI`; conditionally adds `efi-bgrt.o`, `capsule.o`, `capsule-loader.o`, `fdtparams.o`, `esrt.o`, `efi-pstore.o`, `cper*.o`, `runtime-wrappers.o`, `efibc.o`, `dev-path-parser.o`, `apple-properties.o`, `embedded-firmware.o`, `mokvar-table.o`, `ovmf-debug-log.o`, `sysfb_efi.o`, architecture runtime files, and `libstub`.

Control flow: no runtime flow. Kbuild selection determines which initcalls and exported symbols exist. The Makefile also disables KASAN instrumentation for `runtime-wrappers.o` on ARM64 because EFI runtime mappings lack KASAN shadow.

State and persistence behavior: none beyond build products.

Dependencies and integration points: mirrors the EFI Kconfig feature graph and architecture symbols. It connects generic EFI core code to ARM/ARM64/RISC-V runtime enablement and to the EFI boot stub subdirectory.

Risks and test signals: incorrect object gating can produce missing symbols or dead code under architecture-specific configs. Test signals are allmodconfig/defconfig builds across x86, ARM, ARM64, and RISC-V, plus link checks for capsule/CPER/pstore combinations.
