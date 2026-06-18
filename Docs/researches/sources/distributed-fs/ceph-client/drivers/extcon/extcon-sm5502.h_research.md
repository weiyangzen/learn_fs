# sources/distributed-fs/ceph-client/drivers/extcon/extcon-sm5502.h

## Purpose
Private register, bitfield, timing, device-type, switch, reset, and interrupt definitions for the SM5502-family MUIC extcon driver. It supports both SM5502-style and SM5504-style interrupt/control layouts.

## Important APIs, Types, and Functions
`enum sm5502_reg` maps the device register space through `SM5502_REG_END`. Control masks define interrupt masking, wait, manual switch, raw data, switch-open, and SM5504 charger/ADC enable bits. INTM and IRQ masks define two-register IRQ layouts for SM5502 and SM5504 variants. Timing constants encode key press, ADC detect, switch wait, and long-key windows. DEV_TYPE masks classify audio, USB SDP, UART, car kit, charger, DCP, OTG, JIG, PPD, TTY, and AV cable states. Manual switch macros encode VBUSIN and DM/DP routing. `enum sm5502_irq` and `enum sm5504_irq` define logical regmap IRQ indices.

## Control Flow
The header has no executable control flow. Its enum ordering must match the C file's `regmap_irq` arrays and variant IRQ descriptor arrays. Its switch and device-type macros are consumed by cable classification and hardware path programming.

## State and Persistence
No state is stored here. The constants describe persistent hardware register state when the C driver writes reset/control/mask/manual-switch registers.

## Dependencies and Integration Points
Requires kernel bit macros from the including C file. It is coupled to SM5502/SM5504 datasheet layouts and the variant data in `extcon-sm5502.c`.

## Risks
`SM5502_REG_DEV_TYPE1_AUDIO_TYPE1__MASK` appears to be named as audio type1 but uses the audio type2 shift, which is likely a naming typo and could mislead future users. Raw macros do not enforce field width or register variant. Full-register initialization in the C file makes these definitions sensitive to reset-value assumptions.

## Test Signals
Compile coverage, regmap IRQ event ordering, hardware validation of DEV_TYPE classification, manual VBUS/DM/DP switch routing, SM5502 versus SM5504 interrupt masks, and timing register programming if future code uses timing constants.
