# sources/distributed-fs/ceph-client/drivers/remoteproc/imx_rproc.h

## Purpose

`imx_rproc.h` is the shared private configuration header for NXP i.MX remoteproc drivers. It defines the address translation table entry format, device-configuration flags, platform operation callbacks, and SoC configuration descriptor used by `imx_rproc.c` and reused by `imx_dsp_rproc.c`.

## Important APIs, types, and data

- `struct imx_rproc_att` maps a remote device address (`da`) to a system bus address (`sa`) and size, with driver-specific flags.
- `IMX_RPROC_NEED_SYSTEM_OFF` marks configurations needing reboot/power-off mailbox handling.
- `IMX_RPROC_NEED_CLKS` marks configurations where Linux should enable a clock when the remote core is under Linux control.
- `struct imx_rproc_plat_ops` contains optional `start`, `stop`, `detach`, `detect_mode`, and `prepare` hooks.
- `struct imx_rproc_dcfg` combines reset/source register fields, GPR wait fields, ATT table pointer and size, flags, platform ops, and System Manager `cpuid`/`lmid`.

## Control flow

The header has no executable flow. Runtime behavior is driven by consumers that choose an `imx_rproc_dcfg` from an OF match entry, call `detect_mode`, map ATT entries, and call `start`/`stop`/`prepare` through `imx_rproc_plat_ops`.

## State and persistence behavior

The types are static configuration contracts and hold no state by themselves. The fields describe persistent hardware state locations such as SRC/GPR reset registers and remote memory address windows. In consumers, `cpuid` and `lmid` are treated as firmware protocol identifiers rather than mutable state.

## Dependencies and integration points

The header assumes Linux integer types and `BIT()` are available from including C files. It is local to the remoteproc drivers and should stay synchronized with both generic M-core and DSP driver expectations. The ATT flags are interpreted differently by each C file, so new flag bits must not collide across users without auditing both consumers.

## Risks and edge cases

- `lmid` is commented as "Logcial Machine", a spelling issue only, but the field is a critical System Manager identifier.
- The header does not define ATT flag bits; each user defines its own high-bit meanings. This reduces coupling but makes shared-table reuse risky if flags are moved into the header later.
- Address and size fields are 32-bit. This matches current i.MX remote views but constrains future address maps above 4 GiB.

## Test signals

Header validation is mostly compile-time: every C file using it should build with all configured SoC tables, callbacks, and flag definitions. Adding fields should trigger review of both `imx_rproc.c` and `imx_dsp_rproc.c`, plus DT-compatible data initialization for all i.MX variants.
