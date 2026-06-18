# sources/distributed-fs/ceph-client/drivers/hsi/clients/Kconfig

## Purpose
This Kconfig file declares HSI client driver options for Nokia modem support, CMT speech, SSI protocol, and a generic HSI/SSI character interface.

## Important Symbols
- `NOKIA_MODEM`: tristate, depends on `HSI && SSI_PROTOCOL && CMT_SPEECH`; supports the modem on Nokia N900/RX-51 hardware.
- `CMT_SPEECH`: tristate, depends on `HSI && SSI_PROTOCOL`; provides Nokia CMT speech protocol support and can build as `cmt_speech`.
- `SSI_PROTOCOL`: tristate, depends on `HSI && PHONET && OMAP_SSI`; enables the SSI protocol, also described as McSAAB.
- `HSI_CHAR`: tristate, depends on `HSI`; provides a generic character device interface for modem serial communication over HSI/SSI.

## Control Flow and Build Flow
Selections in this file drive `drivers/hsi/clients/Makefile`. The dependency chain requires the OMAP SSI controller and Phonet for `SSI_PROTOCOL`, then speech depends on SSI protocol, and Nokia modem depends on both protocol and speech. `HSI_CHAR` is independent of that Nokia stack beyond needing HSI.

## State and Persistence
No runtime state exists. User choices persist in kernel configuration and decide which modules are compiled.

## Dependencies and Integration Points
This file ties protocol/client layering together: the Nokia modem composition driver is not available unless both `ssi_protocol` and `cmt_speech` are buildable. It also exposes `hsi_char` as a simpler diagnostic or general HSI client interface.

## Risks and Edge Cases
- The `NOKIA_MODEM` dependency on `CMT_SPEECH` means probe-time child creation is matched by build-time availability; changing that relationship could cause `device_attach()` deferrals or missing child drivers.
- `SSI_PROTOCOL` is tied to `OMAP_SSI`, so non-OMAP HSI deployments will only get `HSI_CHAR` unless they add compatible protocol support.

## Test Signals
- Kconfig dependency tests should verify `NOKIA_MODEM` is hidden until `SSI_PROTOCOL` and `CMT_SPEECH` are enabled.
- Module builds should produce `nokia-modem.ko`, `cmt_speech.ko`, `ssi_protocol.ko`, and `hsi_char.ko` according to selected tristates.
