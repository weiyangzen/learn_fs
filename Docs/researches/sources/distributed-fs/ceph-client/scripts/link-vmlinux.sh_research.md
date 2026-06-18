# sources/distributed-fs/ceph-client/scripts/link-vmlinux.sh

## Purpose
`link-vmlinux.sh` performs final kernel image linking. It links `vmlinux`, handles kallsyms multi-pass generation, optional BTF generation and BTF ID patching, System.map generation, optional built-time table sorting, map-file generation, and cleanup.

## Important APIs, Types, and Functions
Inputs are `LD`, `KBUILD_LDFLAGS`, `LDFLAGS_vmlinux`, and output `VMLINUX`. Functions include `is_enabled()`, `info()`, `vmlinux_link()`, `kallsyms()`, `sysmap_and_kallsyms()`, `mksysmap()`, `sorttable()`, and `cleanup()`.

Important variables include `arch_vmlinux_o`, `btf_vmlinux_bin_o`, `btfids_vmlinux`, `kallsymso`, `strip_debug`, and `generate_map`. It checks many configs: `CONFIG_LTO_CLANG`, `CONFIG_X86_KERNEL_IBT`, `CONFIG_KLP_BUILD`, `CONFIG_GENERIC_BUILTIN_DTB`, `CONFIG_ARCH_WANTS_PRE_LINK_VMLINUX`, `CONFIG_KALLSYMS`, `CONFIG_DEBUG_INFO_BTF`, `CONFIG_KALLSYMS_ALL`, `CONFIG_64BIT`, `CONFIG_RELOCATABLE`, `CONFIG_VMLINUX_MAP`, and `CONFIG_BUILDTIME_TABLE_SORT`.

## Control Flow
After optional `clean`, it builds `init/version-timestamp.o`, selects architecture and BTF/kallsyms setup, optionally runs tracepoint update, creates a dummy kallsyms object, links temporary vmlinux images for kallsyms and/or BTF, runs `gen-btf.sh`, performs kallsyms passes until size stabilizes or an extra pass is requested, links final `vmlinux`, patches BTF IDs, writes `System.map`, sorts tables if configured, verifies final System.map against kallsyms, and writes a dependency file for fixdep.

## State and Persistence
It creates and removes temporary `.tmp_vmlinux*`, `.btf.*`, `vmlinux.map`, `System.map`, and `.${VMLINUX}.d` files in the object tree. Final persistent outputs are `vmlinux`, `System.map`, optional `vmlinux.map`, and dependency metadata.

## Dependencies and Integration Points
Called by Kbuild. Depends on linker/compiler variables, `${MAKE}`, `${CC}`, `${NM}`, `${RESOLVE_BTFIDS}`, `scripts/kallsyms`, `scripts/mksysmap`, `scripts/file-size.sh`, `scripts/gen-btf.sh`, `scripts/sorttable`, architecture pre-link objects, linker script `${KBUILD_LDS}`, and `include/config/auto.conf`.

## Risks and Edge Cases
Final link behavior is configuration-sensitive. Kallsyms convergence may need `KALLSYMS_EXTRA_PASS=1`; mismatch is a hard error. BTF failure suggests disabling `CONFIG_DEBUG_INFO_BTF`. User-mode Linux uses `CC` as linker with different flags/libs. Temporary files must be cleaned when switching configs. Any quoting mistake around flags/libs can affect unusual paths or flags.

## Test Signals
Kernel build configurations with and without KALLSYMS, BTF, LTO, KLP, built-in DTBs, UML, map generation, and table sorting validate this script. `clean` mode should remove its generated artifacts.
