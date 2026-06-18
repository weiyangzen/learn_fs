# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8195/mt8195-audsys-clk.h

## Purpose
Small private interface for registering MT8195 audiosys gate clocks from the AFE platform clock initialization path.

## Important APIs, Types, and Functions
Declares `int mt8195_audsys_clk_register(struct mtk_base_afe *afe);`. The declaration expects callers to include or already know `struct mtk_base_afe` from the MT8195/common AFE headers.

## Control Flow
The header has no runtime logic. It lets `mt8195-audsys-clk.c` expose one registration function to the broader MT8195 AFE clock setup code.

## State and Persistence
No state is defined here. State created by the declared function lives in `struct mt8195_afe_private`, the Linux clock framework, and hardware gate registers.

## Dependencies and Integration Points
Integrated by MT8195 AFE clock code and indirectly used by the AFE platform probe before sub-DAI registration. It forms the compile-time boundary between the audiosys gate table and the rest of the audio driver.

## Risks
Because the header does not include `mt8195-afe-common.h`, include order matters for users that do not already have `struct mtk_base_afe` visible. API drift is the main risk.

## Test Signals
Compile tests for MT8195 audio are the primary signal. Runtime validation comes from successful `mt8195_afe_init_clock()` and later stream use of audsys gates.
