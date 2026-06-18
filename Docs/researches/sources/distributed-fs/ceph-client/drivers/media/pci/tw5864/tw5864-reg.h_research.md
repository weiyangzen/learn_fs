
# sources/distributed-fs/ceph-client/drivers/media/pci/tw5864/tw5864-reg.h

## Purpose
This header is the TW5864 hardware register contract. It maps direct MMIO offsets, indirect decoder/audio/motion-detection registers, and bit fields for the H.264 encoder, sensor interface, DDR, VLC/MV buffers, PCI interrupt bridge, video input decoder, and motion detection blocks.

## Important APIs, Types, And Functions
It is a macro-only file. Major symbol families include `TW5864_EMU`, `TW5864_DSP*`, `TW5864_SLICE`, `TW5864_ENC_BUF_PTR_REC*`, `TW5864_SENIF_ORG_FRM_PTR*`, `TW5864_INTERLACING`, `TW5864_MOTION_SEARCH_ETC`, `TW5864_QUAN_TAB`, `TW5864_FRAME_*`, `TW5864_VLC*`, `TW5864_INTR_*`, `TW5864_H264EN_*`, `TW5864_DDR_*`, `TW5864_PCI_*`, `TW5864_MV*`, and `TW5864_INDIR_*`. Function-like macros compute per-channel register addresses for frame buses, rate controls, video input decoder bytes, picture size, and detection controls.

## Control Flow
There is no executable control flow, but the macros drive all register programming in `tw5864-core.c`, `tw5864-video.c`, and `tw5864-util.c`. Direct registers are accessed through `tw_readl`/`tw_writel`; indirect registers are accessed through `TW5864_IND_CTL`/`TW5864_IND_DATA` helper functions.

## State And Persistence
The file describes hardware state rather than owning state. Persistent effects are writes into TW5864 registers: encoder configuration, DMA base addresses, interrupt masks/status, input standard selection, crop/size settings, DDR behavior, and motion-detection thresholds/masks.

## Dependencies And Integration Points
The header assumes Linux `BIT()` is visible through includers. It is included by `tw5864.h` and directly by implementation files. Its constants are tightly coupled to datasheet behavior and to inferred/undocumented bits noted in comments, such as `TW5864_DSP_INTER_ST`.

## Risks
Many definitions represent reverse-engineered or poorly documented hardware behavior. A wrong shift/mask can corrupt unrelated channels because registers pack per-channel fields. Some address ranges are large and sparse, making debug-register bounds important. Maintaining this file requires checking every user of a field before renaming or changing bit semantics.

## Test Signals
Signals are indirect: successful hardware initialization, valid H.264 output, correct interrupt delivery, stable frame-rate controls, accurate input status reporting, and no register-debug access outside documented direct/indirect ranges. Hardware regression tests should cover all four channel indices to catch packed-field errors.
