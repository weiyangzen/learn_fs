# sources/distributed-fs/ceph-client/drivers/media/rc/img-ir/img-ir-nec.c

Purpose: provides the ImgTec hardware-decoder descriptor for NEC-family IR protocols: normal NEC, extended NEC, and NEC32. It maps hardware-decoded raw fields to rc-core protocol-specific scancodes and supports hardware scancode filtering for all NEC variants.

Important APIs, types, and functions: `img_ir_nec_scancode()` treats zero-length frames as repeat codes, requires 32 data bits otherwise, extracts raw `ddDDaaAA`, distinguishes NEC32 when the command inverse check fails, NECX when the address inverse check fails, and normal NEC when both inverse checks match. It uses `bitrev8()` for NEC32's transmitted-order scancode encoding. `img_ir_nec_filter()` chooses an exact protocol from the supplied protocol bitmap or infers one from the scancode/mask, then builds raw data/mask in the hardware order. The exported `img_ir_nec` descriptor declares pulse-distance timing, 562.5 us units, NEC leader and bit timings, fixed 32-bit normal length, 108 ms repeat interval, and repeat timing with zero data bits.

Control flow: the parent hardware layer preprocesses and converts the descriptor, then calls `img_ir_nec_scancode()` for decoded frames. A zero-length repeat frame returns `IMG_IR_REPEATCODE`, causing the hardware layer to call `rc_repeat()` only while it is already in repeating mode. Filter programming calls `img_ir_nec_filter()` from rc-core normal or wake filter callbacks.

State and persistence behavior: no mutable state is stored here. NEC repeat behavior is encoded in descriptor fields and managed by `img-ir-hw.c` timers.

Dependencies and integration points: uses `linux/bitrev.h`, `linux/log2.h` for `is_power_of_2()`, and `img-ir-hw.h`. Integrates with rc-core NEC protocol bitmaps and wake filtering through the hardware driver.

Risks and edge cases: protocol inference from scancode and mask matters for normal filters; wake filters should pass one exact protocol bit. Incorrect inverse handling would misclassify NECX versus NEC32. Zero-length repeat frames depend on the parent repeat-mode timer and may be ignored if received before a primary scancode.

Test signals: test normal NEC, NECX, and NEC32 scancodes, verify repeat frames generate rc repeats after an initial keydown, and verify scancode filters for each variant, especially NEC32 bit-reversal cases.
