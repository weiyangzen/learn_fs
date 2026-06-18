# sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/xgbe/xgbe-smn.h

## Purpose
`xgbe-smn.h` abstracts access to AMD System Management Network reads/writes used by the PCI driver for XPCS v3 indirect window setup. It provides real AMD northbridge access when `CONFIG_AMD_NB` is enabled and safe stubs otherwise.

## Important APIs, Types, And Functions
- When `CONFIG_AMD_NB` is enabled, the header includes `<asm/amd/nb.h>` and exposes the platform `amd_smn_read`/`amd_smn_write` APIs.
- Otherwise, inline `amd_smn_write` and `amd_smn_read` return `-ENODEV`.

## Control Flow
`xgbe-pci.c` includes this header. During probe for v3 XPCS access, it computes an SMN address and calls `amd_smn_read` to read the XPCS window definition register. If the stub is active, probe fails for that path with `-ENODEV`.

## State And Persistence
The header owns no state. It only controls compile-time availability of SMN access.

## Dependencies And Integration Points
This file depends on the kernel AMD northbridge support configuration. Its sole integration in this subset is the PCI probe path for v3 hardware.

## Risks
Building without `CONFIG_AMD_NB` can make v3 PCI devices fail probe when SMN access is required. The stub behavior is explicit and safe, but it shifts the failure to runtime. Callers must check return codes, which `xgbe-pci.c` does.

## Test Signals
Build with and without `CONFIG_AMD_NB`. Probe v3 hardware and confirm successful SMN reads when enabled and clear probe failure logs when unavailable. Static analysis should confirm all SMN calls check return values.
