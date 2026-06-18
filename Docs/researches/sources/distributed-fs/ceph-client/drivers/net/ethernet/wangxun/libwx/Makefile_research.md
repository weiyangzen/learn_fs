# sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/libwx/Makefile

## Purpose
This Makefile builds the Wangxun common support library object used by the Wangxun Ethernet drivers.

## Important APIs, types, and functions
The rule `obj-$(CONFIG_LIBWX) += libwx.o` creates the composite library object. `libwx-objs` is composed from `wx_hw.o`, `wx_lib.o`, `wx_ethtool.o`, `wx_ptp.o`, `wx_mbx.o`, `wx_sriov.o`, `wx_vf.o`, `wx_vf_lib.o`, and `wx_vf_common.o`.

## Control flow and integration
When `CONFIG_LIBWX` is enabled directly or selected by a Wangxun driver, kbuild compiles the listed objects and links them into `libwx.o`. Higher-level PF/VF drivers link against or depend on this common code through the directory-level build.

## State and persistence behavior
No runtime state is declared in the Makefile. The listed object files likely provide shared hardware, ethtool, PTP, mailbox, SR-IOV, and VF support state at runtime, but this file only controls composition.

## Dependencies and integration points
The file depends on the `LIBWX` Kconfig symbol and the presence of all listed source files in the `libwx` directory. Kconfig ensures supporting facilities such as PTP, page-pool, DIM, and PHYLINK are available.

## Risks and edge cases
Adding or removing common library source files requires updating `libwx-objs`; otherwise code may be omitted or stale object names may break builds. Because multiple drivers share this library, build failures here affect all Wangxun PF/VF drivers.

## Test signals
Build any driver that selects `LIBWX`, verify `libwx.o` is composed from all listed objects, and run module dependency checks for PF and VF drivers that consume common Wangxun functionality.
