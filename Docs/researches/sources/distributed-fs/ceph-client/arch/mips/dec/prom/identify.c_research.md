# sources/distributed-fs/ceph-client/arch/mips/dec/prom/identify.c

Purpose: identifies the DECstation model from PROM data and initializes essential per-model physical base addresses before broader platform setup.

Important APIs: `get_system_type()` returns a cached `"Digital ..."` string; `prom_identify_arch(u32 magic)` reads PROM `systype` or REX `sysid`, decodes fields, selects `mips_machtype`, and calls inline initializers. It exports `dec_rtc_base`.

Control flow: model-specific helpers set `dec_kn_slot_base`, `dec_kn_slot_size`, `dec_tc_bus`, `ioasic_base`, and `dec_rtc_base` for KN01, KN230, KN02, KN02XA, and KN03 families. DS5000/2x0 may be refined to DS5900 by inspecting IOASIC status.

State and integration: the selected machine type and base pointers are global platform state used by setup, RTC, TurboChannel, IRQ, and bus-error code.

Risks and test signals: bad PROM sysid or wrong IOASIC probe results cascade into wrong interrupt maps and resources. Boot logs should print the expected DEC model, and RTC/IOASIC/TurboChannel resources should match hardware.
