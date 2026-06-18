# sources/distributed-fs/ceph-client/sound/isa/msnd/msnd_classic.h

## Purpose
`msnd_classic.h` defines the hardware constants for Turtle Beach MultiSound Classic/Monterey/Tahiti cards. It supplies the register offsets, reset values, queue sizes, MIDI routing constants, SMA shared-memory offsets, firmware filenames, and long name used when `MSND_CLASSIC` builds the common board driver.

## Important APIs, Types, and Functions
Key constants include `DSP_NUMIO`, Classic-only host ports `HP_MEMM`, `HP_BITM`, `HP_WAIT`, `HP_DSPR`, `HP_PROR`, `HP_BLKS`, reset and bank-select values, `DSPQ_BUFF_SIZE`, `DSPQ_DATA_BUFF`, `MOP_*` and `MIP_*` MIDI routing masks, Classic `SMA_*` offsets, and firmware names `turtlebeach/msndinit.bin` and `turtlebeach/msndperm.bin`.

## Control Flow
The header provides compile-time configuration. The included `msnd_pinnacle.c` uses these definitions for Classic reset timing, memory bank selection, IRQ mask programming, SMA initialization, and firmware upload.

## State and Persistence
No direct state is stored here. The constants describe persistent hardware ABI positions in SRAM and volatile control register values.

## Dependencies and Integration Points
It is included only under `MSND_CLASSIC`. It pairs with `msnd.h` for common queue and command constants and with `msnd_classic.c` for build selection.

## Risks and Test Signals
The risk is hardware ABI drift: a wrong SMA offset or queue size would corrupt DSP-shared memory. Test signals include Classic firmware loading from the declared filenames, DSP reset success through Classic ports, correct IRQ mask mapping, and mixer/PCM operation against the Classic SMA layout.
