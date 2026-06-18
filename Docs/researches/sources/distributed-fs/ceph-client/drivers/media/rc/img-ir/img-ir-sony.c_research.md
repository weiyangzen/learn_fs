# sources/distributed-fs/ceph-client/drivers/media/rc/img-ir/img-ir-sony.c

Purpose: provides the ImgTec hardware descriptor for Sony SIRC 12-, 15-, and 20-bit variants. It converts variable-length hardware data into rc-core Sony scancodes and builds length-constrained hardware filters.

Important APIs, types, and functions: `img_ir_sony_scancode()` switches on decoded bit length, checks the enabled protocol bitmap, extracts function, device, and optional subdevice fields, sets the appropriate `RC_PROTO_SONY12`, `RC_PROTO_SONY15`, or `RC_PROTO_SONY20`, and emits `dev << 16 | subdev << 8 | func`. `img_ir_sony_filter()` extracts scancode fields and masks, chooses or infers a Sony variant, validates 20-bit device limits, handles the hardware ambiguity between high device bits and low extended bits, writes raw data/mask, and optionally sets `out->minlen/maxlen`. The descriptor uses pulse-length code type, 600 us units, Sony leader and pulse-length bit timings, and 12-20 bit length range.

Control flow: the parent hardware decoder may enable a subset of Sony variants. When raw frames arrive, the scancode callback rejects lengths not included in the currently enabled protocol bitmap. Filter conversion either honors one exact protocol bit or infers a length from masked scancode fields.

State and persistence behavior: no mutable local state. Length restrictions for filters are returned through `struct img_ir_filter` and then tightened into the free-time register by the parent.

Dependencies and integration points: depends on `img-ir-hw.h` and rc-core Sony protocol bitmaps. The parent has a pulse-length bit-count increment quirk for this code type.

Risks and edge cases: filter inference can be ambiguous for Sony12 high device bits versus Sony20 subdevice bits, and the code explicitly ANDs masks to represent hardware limitations. The pulse-length quirk in the parent affects reported lengths. Userspace wake filters should pass an exact protocol to avoid inference surprises.

Test signals: test all Sony12/15/20 variants, enabled-protocol subsets, filter length restriction, high device-bit ambiguity, and wake filters for each exact variant.
