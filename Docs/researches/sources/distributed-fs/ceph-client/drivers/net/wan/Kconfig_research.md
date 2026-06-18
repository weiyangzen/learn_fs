<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wan/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/wan/Kconfig

## Purpose
`drivers/net/wan/Kconfig` defines the kernel configuration menu for WAN interface support and the protocol/card drivers in this directory. It gates the generic HDLC layer, HDLC protocol personalities, WAN card drivers, firmware build options, and related X.25/LAPB pseudo devices.

## Important APIs, Types, and Functions
This is Kconfig metadata rather than C code. Important symbols include:
- `WAN`: top-level boolean menu controlling WAN interface support.
- `HDLC`: generic HDLC layer, tristate, required by most synchronous WAN card drivers.
- `HDLC_RAW`, `HDLC_RAW_ETH`, `HDLC_CISCO`, `HDLC_FR`, `HDLC_PPP`, `HDLC_X25`: protocol modes layered on generic HDLC.
- `PCI200SYN`, `WANXL`, `PC300TOO`, `N2`, `C101`, `FARSYNC`, `FSL_QMC_HDLC`, `FSL_UCC_HDLC`, `SLIC_DS26522`, `IXP4XX_HSS`, `LAPBETHER`: device/driver feature symbols.
- `WANXL_BUILD_FIRMWARE`: optional firmware rebuild path for the wanXL driver.
- It also sources `drivers/net/wan/framer/Kconfig`.

## Control Flow
Kconfig is evaluated by the kernel configuration system. Enabling `WAN` reveals subordinate WAN options. Enabling `HDLC` makes the protocol-specific HDLC modules selectable. Individual card symbols declare dependencies such as `HDLC && ISA`, `HDLC && PCI`, `HAS_IOPORT`, platform controller symbols, or protocol dependencies. The selected symbols drive compilation through the directory `Makefile`.

## State and Persistence Behavior
Selected values persist in the kernel build `.config`. At runtime this file has no behavior. Tristate symbols determine whether drivers are built in, built as modules, or omitted.

## Dependencies and Integration Points
The file integrates with the kernel Kconfig system and `drivers/net/wan/Makefile`. `CONFIG_C101` specifically controls compilation of `c101.o` and depends on `HDLC && ISA`. `HDLC_X25` depends on compatible LAPB/HDLC tristate combinations. `SLIC_DS26522` selects `BITREVERSE` and is constrained to specific SoCs or `COMPILE_TEST`.

## Risks and Edge Cases
- Dependency expressions must keep module/built-in combinations valid; `HDLC_X25` has a more complex LAPB expression to avoid unusable link combinations.
- Legacy ISA drivers such as `C101` are only visible with ISA and HDLC enabled, which affects test coverage on modern configs.
- `WANXL_BUILD_FIRMWARE` invokes toolchain requirements and should stay optional and disabled by default for normal builds.
- Moving or renaming symbols requires matching `Makefile`, module alias, and user documentation updates.

## Test Signals
- Run `olddefconfig`/`menuconfig` combinations for `WAN`, `HDLC`, and each driver symbol.
- Build-test `CONFIG_C101=m`, `CONFIG_HDLC=m`, and representative PCI/platform WAN drivers.
- Check that invalid LAPB/HDLC tristate combinations hide or disable `HDLC_X25`.
- Verify `WANXL_BUILD_FIRMWARE=y` only builds when firmware build prevention is disabled and the expected tools are available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wan/Kconfig -->
