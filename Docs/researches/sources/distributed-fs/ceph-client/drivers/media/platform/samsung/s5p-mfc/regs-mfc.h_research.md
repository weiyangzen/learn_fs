# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/regs-mfc.h

## Purpose
This is the legacy MFC v5.1 register, command, status, codec-id, shared-memory, alignment, and buffer-size contract. It is the base include used by common driver code and the v5 command/operation implementation.

## Important APIs, Types, and Constants
The file defines v5 MMIO ranges, reset and host/RISC argument registers, firmware status/version, two-bank DRAM base registers, decoder and encoder buffer address registers, stream interface registers, display/decode status fields, frame-type values, buffer alignment and size constants, encoder control/rate/H.264/MPEG4 registers, codec ids, channel command ids, host-to-RISC and RISC-to-host command ids, error masks, shared-memory offsets for crop/frame tags/rate-control/DPB sizes/SEI, `MFC_OFFSET_SHIFT`, firmware/context/descriptor/shared-buffer sizes, `MFC_VERSION`, and `MFC_NUM_PORTS`.

## Control Flow and State
This header enables the v5 command flow in `s5p_mfc_cmd_v5.c`, where arguments are written to `HOST2RISC_ARG1..4` before a command is posted. Runtime state is read from stream-interface and shared-memory offsets: consumed bytes, display/decode status, decoded/display addresses, frame type, DPB size, crop information, and interrupt return codes.

## Dependencies and Integration Points
It includes `linux/kernel.h` and `linux/sizes.h`, and is included by `s5p_mfc_common.h`. The common macros `mfc_read()` and `mfc_write()` use these offsets. `s5p_mfc.c` maps compatible `samsung,mfc-v5` to two memory ports, v5 firmware, v5 buffer sizes, and clock-gating behavior.

## Risks
The v5 ABI differs materially from v6+: command arguments are explicit registers, memory uses two ports, and addresses are offset-shifted. Accidentally using v6 register or address semantics on v5 can break firmware communication. Dummy compatibility definitions for v6-only features use `-1`, so unchecked use of those macros can produce invalid MMIO offsets.

## Test Signals
Signals include v5 firmware load/init, open/close instance command returns, H.264/MPEG4/H263/VC1/MPEG2 decode, H.264/MPEG4/H263 encode, two-bank DMA allocation, shared-memory crop reporting, and error handling for warning/error code ranges.
