# sources/distributed-fs/ceph-client/drivers/media/rc/img-ir/img-ir-sanyo.c

Purpose: provides the ImgTec hardware-decoder descriptor for Sanyo/Aiwa/Chinon style IR, a NEC-timed protocol with 13-bit address and inverted address plus 8-bit command and inverted command.

Important APIs, types, and functions: `img_ir_sanyo_scancode()` treats zero-length frames as repeat codes, requires 42 data bits, extracts address, inverted address, command, and inverted command, validates both inversion checks, and emits `RC_PROTO_SANYO` with `addr << 8 | data`. `img_ir_sanyo_filter()` rejects out-of-range scancodes, constructs raw data/mask including inverted fields, and supports hardware filtering. The exported `img_ir_sanyo` descriptor uses pulse-distance timings matching NEC, 562.5 us units, 42-bit fixed length, 108 ms repeat interval, and zero-length repeat timings.

Control flow: the parent hardware decoder writes Sanyo timing registers and calls the scancode function for data frames. Repeat frames are routed as `IMG_IR_REPEATCODE` and handled by the parent's repeat state. Filters are converted to raw data/mask by `img_ir_sanyo_filter()`.

State and persistence behavior: no local mutable state. Repeat-mode state is descriptor-driven and stored in `img-ir-hw.c`.

Dependencies and integration points: depends on `img-ir-hw.h` and rc-core Sanyo protocol constants. It shares NEC-like timing expectations with both the software Sanyo decoder and NEC descriptor.

Risks and edge cases: address and command inverse validation must match the protocol; otherwise noise could become key events. Filter masks duplicate data masks across inverted command fields and address masks across inverted address fields, so partial filters need careful validation. Out-of-range high address bits are rejected.

Test signals: test full 42-bit Sanyo frames, invalid inverse fields, repeat frames after keydown, and wake/normal filters for address-only and address+command masks.
