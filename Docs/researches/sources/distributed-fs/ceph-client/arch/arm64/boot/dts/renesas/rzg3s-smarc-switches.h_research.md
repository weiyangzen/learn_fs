# sources/distributed-fs/ceph-client/arch/arm64/boot/dts/renesas/rzg3s-smarc-switches.h

## Purpose
This board-configuration header documents and encodes on-board switch settings for the Renesas RZ/G3S SMARC module and RZ SMARC Carrier II.

## APIs, Types, And Constants
The macro API defines `SW_OFF` and `SW_ON`, then sets board switch constants: `SW_CONFIG2` selects SD0 connected to eMMC, `SW_CONFIG3` selects SCIF1/SSI0/IRQ0/IRQ1 connected to the SoC, and `SW_OPT_MUX4` routes SMARC SER0 signals to PMOD1.

## Control Flow And State
There is no runtime control flow. These macros are a source-level representation of physical board switch state and are expanded into DTS conditional configuration.

## Dependencies And Integration
The header has no includes and is consumed by RZ/G3S SMARC DTS files. It integrates physical board assembly/switch positions with device-tree descriptions.

## Risks And Test Signals
The risk is documentation drift from actual switch positions, causing DTS to describe unavailable peripherals. Tests are DTB compilation plus board validation of SD/eMMC, serial, audio, IRQ, and PMOD routing under the documented switch settings.
