# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/regs-mfc-v6.h

## Purpose
This header is the primary register map for MFC v6 and the base for later v7/v8/v10/v12 definitions. It describes the v6+ host/RISC command interface, reset and firmware status registers, decoder and encoder programming windows, returned status registers, codec ids, alignment requirements, scratch/ME/TMV size formulas, and firmware/context/CPB sizes.

## Important APIs, Types, and Constants
Important groups include command registers (`S5P_FIMV_HOST2RISC_CMD_V6`, `S5P_FIMV_RISC2HOST_CMD_V6`, interrupt registers), command ids (`SYS_INIT`, `OPEN_INSTANCE`, `CH_SEQ_HEADER`, `CH_INIT_BUFS`, `CH_FRAME_START`, `CLOSE_INSTANCE`, `SLEEP`, `WAKEUP`, `FLUSH`, `NAL_ABORT`), return ids matching `s5p_mfc_irq`, context registers, error masks, decoder option/display/decode/DPB/CPB registers, encoder frame/rate-control/DPB/source/stream/H.264/MPEG4/MVC registers, codec ids for H.264 MVC, VP8, MPEG4, MPEG2, VC1, H263, and alignment/size macros.

## Control Flow and State
The constants back the v6 command flow in `s5p_mfc_cmd_v6.c`: program context/codec registers, write a host command, raise `HOST2RISC_INT`, and wait for a `RISC2HOST_CMD` return. Decoder state is represented by display and decoded status registers, DPB flags, stream size and CPB offset registers. Encoder state is represented by stream size, slice type, picture count, write pointer, and encoded source address registers.

## Dependencies and Integration Points
The file includes `linux/sizes.h` and is included by v7+ register headers. It is used by the hardware operation layer and by reset/init code in `s5p_mfc_ctrl.c`. The common header's `IS_MFCV6_PLUS()` selects this style of memory-control, reset, command, and buffer logic.

## Risks
Offsets are numerous and tightly coupled to firmware ABI. A wrong offset can corrupt adjacent hardware state rather than failing cleanly. Size formulas use dimensions in operation-specific units, so their callers must pass the expected macroblock or pixel values. The header contains FIXME comments for unknown codec slots, signaling incomplete hardware enumeration.

## Test Signals
Signals include SYS_INIT/OPEN/CLOSE/SLEEP/WAKEUP returns, header parse followed by correct `MIN_NUM_DPB` and frame dimensions, DPB allocation for all advertised decode codecs, frame done/status decoding, rate-control programming for encoders, and suspend/resume on v6+ devices.
