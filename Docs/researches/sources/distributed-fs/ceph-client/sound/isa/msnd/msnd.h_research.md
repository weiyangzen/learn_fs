# sources/distributed-fs/ceph-client/sound/isa/msnd/msnd.h

## Purpose
`msnd.h` is the shared contract for Turtle Beach MultiSound support. It defines default audio parameters, SRAM layout, host-port registers, DSP command/message constants, queue descriptor offsets, the `struct snd_msnd` device state, and function prototypes exported from common and mixer code.

## Important APIs, Types, and Functions
- Constants map DSP SRAM regions: `SRAM_CNTL_START`, `SMA_STRUCT_START`, `DAPQ_DATA_BUFF`, `DARQ_DATA_BUFF`, `DSPQ_OFFSET`, and queue sizes.
- Host-port constants define control/status registers and bits such as `HP_ICR`, `HP_CVR`, `HP_ISR`, `HPICR_RREQ`, `HPISR_TXDE`, and `HPCVR_HC`.
- DSP message and command constants include `HIMT_PLAY_DONE`, `HIMT_RECORD_DONE`, `HDEX_PLAY_START`, `HDEX_RECORD_START`, and `HDEX_AUX_REQ`.
- `struct snd_msnd` carries mapped memory, queue pointers, card/rawmidi handles, resource identifiers, flags, mixer levels, PCM runtime parameters, and active substreams.

## Control Flow
The header itself has no executable control flow, but it shapes all common paths: board code initializes `struct snd_msnd`, common PCM code updates queue and format fields, interrupt code reads `HIMT_*` messages, and mixer code writes SMA offsets through macros defined here and board-specific headers.

## State and Persistence
All state is in memory and hardware. `struct snd_msnd` keeps volatile driver state; the `SMA_*` offsets defined by board headers identify DSP-shared memory that is rewritten on reset/resume.

## Dependencies and Integration Points
It includes `<sound/pcm.h>` and is included by `msnd.c`, `msnd_pinnacle.c`, `msnd_classic.c`, and `msnd_pinnacle_mixer.c`. Board-specific headers extend the generic register map with Classic or Pinnacle SMA layouts.

## Risks and Test Signals
The main risk is that many offsets are hard-coded hardware ABI values. Any change needs hardware or emulation validation. Test signals include successful compilation of both Classic and Pinnacle variants, correct queue address conversion by `PCTODSP_*`, no struct-field mismatch across users, and stable period/capture positions when queue constants change.
