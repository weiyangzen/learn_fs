# sources/distributed-fs/ceph-client/sound/soc/atmel/Kconfig

## Purpose
This Kconfig fragment describes Atmel/Microchip ASoC platform, PCM transport, and machine-driver options.

## Important APIs, Types, And Functions
Transport symbols include `SND_ATMEL_SOC_PDC`, `SND_ATMEL_SOC_DMA`, `SND_ATMEL_SOC_SSC`, `SND_ATMEL_SOC_SSC_PDC`, and `SND_ATMEL_SOC_SSC_DMA`. Platform/machine symbols include `SND_ATMEL_SOC_CLASSD`, `SND_ATMEL_SOC_PDMIC`, `SND_ATMEL_SOC_I2S`, `SND_ATMEL_SOC_WM8904`, legacy WM8731 boards, TSE850, Mikroe PROTO, and Microchip I2S MCC/SPDIF/PDMC drivers.

## Control Flow
Build-time only. The symbols select lower-level PCM transports and codec dependencies so machine drivers build with their CPU DAI and codec support.

## State And Persistence
No runtime state. It determines which drivers are compiled.

## Dependencies And Integration Points
It depends on `HAS_IOMEM`, `ARCH_AT91 || COMPILE_TEST`, `OF`, `ATMEL_SSC`, `I2C`, `COMMON_CLK`, and codec symbols. It integrates with the Atmel Makefile for object selection.

## Risks And Test Signals
Risks are missing selects that lead to link failures or runtime absent components. Test signals are allmodconfig/COMPILE_TEST coverage, DT board configs selecting the expected transport, and no duplicate/unsatisfied symbol dependency warnings.
