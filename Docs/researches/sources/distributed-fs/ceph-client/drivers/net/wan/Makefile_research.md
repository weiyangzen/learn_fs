<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wan/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/wan/Makefile

## Purpose
`drivers/net/wan/Makefile` maps WAN Kconfig symbols to object files and defines the optional wanXL firmware build pipeline. It is the build-system counterpart to `drivers/net/wan/Kconfig`.

## Important APIs, Types, and Functions
- Object mappings: `obj-$(CONFIG_HDLC) += hdlc.o`, protocol modules (`hdlc_raw.o`, `hdlc_cisco.o`, etc.), card drivers (`c101.o`, `n2.o`, `farsync.o`, `wanxl.o`, `pci200syn.o`, `pc300too.o`, `ixp4xx_hss.o`, `fsl_qmc_hdlc.o`, `fsl_ucc_hdlc.o`, `slic_ds26522.o`), and `obj-y += framer/`.
- Firmware artifacts: `clean-files := wanxlfw.inc`, `targets += wanxlfw.inc wanxlfw.bin wanxlfw.o`.
- `CROSS_COMPILE_M68K` and conditional `M68KCC`/`M68KLD` selection support building wanXL QUICC firmware on non-m68k hosts.
- Custom commands: `build_wanxlfw`, `m68kld_bin_o`, and `m68kas_o_S` transform `wanxlfw.S` to object, binary, then C include data when `CONFIG_WANXL_BUILD_FIRMWARE=y`.

## Control Flow
During kbuild, selected `CONFIG_*` values append object files to the directory build. The `framer/` subdirectory is always descended through `obj-y`. When `WANXL_BUILD_FIRMWARE` is enabled, kbuild compiles `wanxlfw.S` with an m68k assembler/compiler, links a raw binary at text address `0x1000`, converts it to a C byte array include using `hexdump` and `sed`, and makes `wanxl.o` depend on that generated include.

## State and Persistence Behavior
The file creates build artifacts only in the object tree. Generated `wanxlfw.inc`, `.bin`, and `.o` are declared as targets/clean files so kbuild can track and remove them. There is no runtime state.

## Dependencies and Integration Points
This Makefile depends on Kconfig symbols from the same directory, kbuild `if_changed`/`if_changed_dep` infrastructure, the m68k toolchain for firmware rebuilding, and source files such as `c101.c`, `hdlc*.c`, `wanxl.c`, and `wanxlfw.S`. `CONFIG_C101` directly builds the C101 driver researched in this work item.

## Risks and Edge Cases
- Firmware rebuild depends on external m68k tools unless building on m68k; missing tools will fail builds only when `WANXL_BUILD_FIRMWARE=y`.
- Generated firmware include content is produced by shell text processing; changes to formatting commands can affect C syntax consumed by `wanxl.o`.
- `obj-y += framer/` means the subdirectory is visited regardless of top-level `WAN` object choices; its own Kconfig/Makefile must gate actual objects correctly.
- Object names must stay synchronized with Kconfig symbols and source filenames.

## Test Signals
- Build representative configs with `CONFIG_C101=m`, `CONFIG_HDLC=m`, and no WAN drivers to confirm object selection.
- Run `make clean` or inspect clean targets to verify generated wanXL firmware artifacts are removed.
- Test `CONFIG_WANXL_BUILD_FIRMWARE=y` on m68k and non-m68k toolchain environments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wan/Makefile -->
