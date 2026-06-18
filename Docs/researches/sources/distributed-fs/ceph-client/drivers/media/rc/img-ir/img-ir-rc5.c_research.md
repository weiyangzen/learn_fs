# sources/distributed-fs/ceph-client/drivers/media/rc/img-ir/img-ir-rc5.c

Purpose: provides the ImgTec hardware descriptor for Philips RC-5. It compensates for hardware bit shifting and emits rc-core RC5 scancodes with toggle state.

Important APIs, types, and functions: `img_ir_rc5_scancode()` shifts raw data right by two due to a hardware quirk, validates the start bit, extracts toggle, address, and six-bit command, extends the command with the RC5 field bit, sets `RC_PROTO_RC5`, and returns `IMG_IR_SCANCODE`. `img_ir_rc5_filter()` returns `-EINVAL` because this hardware path cannot support RC5 scancode filters. The exported `img_ir_rc5` descriptor uses biphase code type, secondary decoder (`decodend2`), MSB-first secondary bit orientation, 888.888 us units, 14-bit length, and 16 percent tolerance.

Control flow: the hardware layer selects this descriptor when RC5 is requested and compatible. Decoded frames are passed to the scancode callback; filters and wake filters are rejected because the descriptor's filter hook always fails.

State and persistence behavior: no local mutable state. Toggle handling is per-frame and repeat behavior is left to rc-core key repeat logic rather than a descriptor repeat frame.

Dependencies and integration points: depends on `img-ir-hw.h` and rc-core RC5 protocol constants. It is sensitive to the parent hardware's biphase interrupt quirk handling.

Risks and edge cases: hardware shift compensation is mandatory; removing it breaks every scancode. Filtering is unsupported, so wakeup protocol availability is suppressed by the parent when this decoder is active. Only standard RC5 is supported here, not RC5X or StreamZap variants handled by the software raw decoder.

Test signals: test known RC5 remotes, toggle-bit alternation, protocol selection rejection for wake filters, and biphase quirk recovery under partial/incomplete messages.
