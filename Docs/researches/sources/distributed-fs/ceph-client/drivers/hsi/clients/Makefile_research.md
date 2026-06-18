# sources/distributed-fs/ceph-client/drivers/hsi/clients/Makefile

## Purpose
This Makefile maps HSI client Kconfig symbols to the corresponding object files.

## Important Build Rules
- `obj-$(CONFIG_NOKIA_MODEM) += nokia-modem.o`
- `obj-$(CONFIG_SSI_PROTOCOL) += ssi_protocol.o`
- `obj-$(CONFIG_CMT_SPEECH) += cmt_speech.o`
- `obj-$(CONFIG_HSI_CHAR) += hsi_char.o`

## Control Flow and Build Flow
Kbuild compiles each client object as built-in or module based on its tristate symbol. There are no aggregate objects or subdirectories in this file.

## State and Persistence
No runtime state exists. Build output follows `.config`.

## Dependencies and Integration Points
The rules consume symbols defined in `drivers/hsi/clients/Kconfig`. The resulting modules register `hsi_client_driver` instances that bind to HSI child devices by name/alias.

## Risks and Edge Cases
- Kconfig expresses dependencies, not the Makefile; forcing object builds outside Kconfig could break due to missing protocol/controller dependencies.
- Object names must match module aliases and child device names used by `nokia-modem.c` (`ssi-protocol`, `cmt-speech`) and by HSI board/device declarations.

## Test Signals
- Build each client as `y` and `m` to confirm module naming and link dependencies.
- Confirm `modinfo` aliases for generated modules align with HSI client names.
