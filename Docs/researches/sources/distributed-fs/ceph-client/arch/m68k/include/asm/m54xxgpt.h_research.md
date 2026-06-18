<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/m54xxgpt.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/m54xxgpt.h

## Purpose
`m54xxgpt.h` defines MCF54xx general purpose timer register addresses and bitfields.

## Important APIs, Types, and Functions
It maps four GPT channels through `MCF_GPT_GMS*`, `GCIR*`, `GPWM*`, `GSR*`, plus indexed macros `MCF_GPT_GMS(x)` and siblings. It defines mode, GPIO, interrupt, watchdog, input/output capture, PWM, counter, prescaler, status, overflow, and capture-field macros.

## Control Flow, State, and Persistence
The file is macro-only. Timer state persists in GPT registers controlled by timer, PWM, or GPIO drivers.

## Dependencies and Integration Points
It depends on `MCF_MBAR`. M54xx timer/PWM/GPIO watchdog users program the GPT through these constants.

## Risks
Indexed macros assume four channels at 0x10 spacing. Bitfield macros do not validate width, so callers must pass values already in range. Clearing status bits may be write-one-to-clear depending on hardware behavior outside this header.

## Test Signals
Use all four channels in timer, capture, PWM, and GPIO modes. Verify prescaler/counter programming, interrupt status handling, and watchdog enable behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/m54xxgpt.h -->
