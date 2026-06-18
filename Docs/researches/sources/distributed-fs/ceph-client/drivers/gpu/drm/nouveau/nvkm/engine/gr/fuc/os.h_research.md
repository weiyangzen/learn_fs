
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/fuc/os.h

## Purpose
Defines the small error-code ABI shared between Nouveau graphics Falcon microcode headers and the host-side GR interrupt/debug code.

## Important APIs, types, and functions
- Include guard `__NVKM_GRAPH_OS_H__`.
- `E_BAD_COMMAND` is error code `0x00000001`.
- `E_CMD_OVERFLOW` is error code `0x00000002`.
- `E_BAD_FWMTHD` is error code `0x00000003`.

## Control flow
The header is declarative. Host C code includes it so FECS status values can be decoded consistently. In `gf100_gr_ctxctl_isr()`, `E_BAD_FWMTHD` causes the driver to print the FECS-submitted class, subchannel, method, and data instead of only reporting a generic ucode error.

## State and persistence
No state is stored. These constants form a persistent ABI with compiled Falcon firmware images.

## Dependencies and integration points
Included by `gf100.c` and paired with `fuc/*.h` microcode arrays. The constants integrate FECS firmware status reporting with NVKM logging and interrupt handling.

## Risks
The numeric values must stay synchronized with firmware. If a code is changed independently of the microcode, interrupt diagnostics will become misleading and bad firmware-method events may be misclassified.

## Test signals
Build coverage catches missing include guards or macro names. Runtime validation comes from FECS error interrupt logs matching expected decoded paths, especially `FECS MTHD ...` messages for `E_BAD_FWMTHD`.
