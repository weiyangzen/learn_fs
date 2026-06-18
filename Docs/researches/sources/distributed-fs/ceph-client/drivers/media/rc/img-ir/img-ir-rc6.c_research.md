# sources/distributed-fs/ceph-client/drivers/media/rc/img-ir/img-ir-rc6.c

Purpose: provides a limited ImgTec hardware descriptor for RC6 mode 0. It reconstructs header/trailer information around known hardware decoder behavior and emits `RC_PROTO_RC6_0` scancodes.

Important APIs, types, and functions: `img_ir_rc6_scancode()` shifts raw data, extracts two trailer samples, mode, address, and command, validates that trailer samples differ, rejects nonzero modes, sets the scancode to `addr << 8 | cmd`, and uses `trl2` as toggle. `img_ir_rc6_filter()` returns `-EINVAL`. The exported `img_ir_rc6` descriptor uses biphase code type, active-high input, MSB-first orientation, explicit RTL-derived leader/bit timings, 20 percent tolerance, fixed 21-bit length, and no filter support.

Control flow: selected through the parent hardware decoder for `RC_PROTO_BIT_RC6_0`. The descriptor supplies custom timings because default RC6 header timings did not work with this hardware block. Decoded frames go through the scancode callback and then `rc_keydown()` in the parent.

State and persistence behavior: no mutable local state. Toggle is derived per message. Filter and wake state are not supported for RC6 on this hardware path.

Dependencies and integration points: depends on `img-ir-hw.h`; integrates with the parent hardware quirk that biphase decoding can produce interrupt storms after incomplete codes.

Risks and edge cases: only mode 0 is supported; RC6-6A/MCE variants are handled by the generic software decoder, not this hardware descriptor. Header recovery is explicitly a workaround for hardware side effects. Filters are unsupported, so userspace should not expect wake-filter matching.

Test signals: verify RC6-0 devices produce correct scancodes and toggles; verify RC6-MCE is not advertised by this hardware descriptor; test incomplete biphase frames for quirk timer recovery.
