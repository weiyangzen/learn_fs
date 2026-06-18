# sources/distributed-fs/ceph-client/drivers/media/rc/img-ir/img-ir-jvc.c

Purpose: provides the ImgTec hardware-decoder descriptor for the JVC pulse-distance IR protocol. It translates 16-bit hardware-decoded raw frames into rc-core JVC scancodes and converts rc-core scancode filters into ImgTec hardware data/mask filters.

Important APIs, types, and functions: `img_ir_jvc_scancode()` validates `len == 16`, extracts customer and data bytes from raw `cust | data << 8`, sets `RC_PROTO_JVC`, and returns `IMG_IR_SCANCODE`. `img_ir_jvc_filter()` maps scancode `cust:data` into the hardware raw order and mask. The exported `struct img_ir_decoder img_ir_jvc` declares `RC_PROTO_BIT_JVC`, pulse-distance code type, 527.5 us units, leader/zero/one timings, fixed 16-bit length, and the two callbacks.

Control flow: `img-ir-hw.c` includes this descriptor in its decoder list when `CONFIG_IR_IMG_JVC` is enabled. During protocol selection, the hardware layer writes the descriptor's timings and control fields. At interrupt time the raw frame is routed to `img_ir_jvc_scancode()`, which emits a scancode through the generic hardware handler.

State and persistence behavior: the file has no mutable persistent state. The descriptor is static module data; runtime state is held in the parent hardware decoder.

Dependencies and integration points: depends on `img-ir-hw.h` for descriptor types and rc-core protocol constants. It integrates with rc-core only indirectly through the hardware driver. It mirrors the software JVC decoder's bit layout but avoids raw pulse parsing because the ImgTec hardware already classified symbols.

Risks and edge cases: only exact 16-bit frames are accepted. Filter translation assumes the JVC scancode layout used by rc-core and the raw byte order expected by the hardware; regressions here would cause wake/filter mismatches while unfiltered receive still works. Repeat semantics are not modeled in this descriptor, so JVC repeat behavior depends on hardware-visible data frames rather than a dedicated no-data repeat path.

Test signals: enable the hardware decoder, select JVC with `ir-keytable`, verify a known JVC remote produces `RC_PROTO_JVC` scancodes, and set normal/wakeup scancode filters to confirm data/mask order.
