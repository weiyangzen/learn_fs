# sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/lsdc_probe.h

Purpose: declares the Loongson CPU PRID helper.

Important APIs/types/functions: `loongson_cpu_get_prid(u8 *impl, u8 *rev)`.

Control flow: no executable flow; debugfs calls the helper.

State and persistence: no state.

Dependencies and integration points: included by debugfs and implemented by `lsdc_probe.c`.

Risks and test signals: declaration requires `u8` type visibility from includers. Test compile on LoongArch, MIPS, and compile-test architectures.
