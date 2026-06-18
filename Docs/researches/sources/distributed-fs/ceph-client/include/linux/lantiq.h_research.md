# sources/distributed-fs/ceph-client/include/linux/lantiq.h

Purpose: abstracts Lantiq SoC support so generic drivers can compile whether or not `CONFIG_LANTIQ` is enabled.

Important APIs and types: when Lantiq support is enabled it includes `<lantiq_soc.h>`. Otherwise it defines fallback `LTQ_EARLY_ASC`, `CPHYSADDR(a)`, and `clk_get_fpi()` returning `NULL`.

Control flow: platform or serial/clock code can include this header and call Lantiq helpers; non-Lantiq builds collapse those hooks to inert defaults.

State and persistence: no state is owned here. In enabled builds state comes from SoC-specific clock and physical-address helpers.

Dependencies and integration points: integrates MIPS/Lantiq platform headers with generic include users. The fallback avoids broad `#ifdef CONFIG_LANTIQ` use in drivers.

Risks and test signals: risks include fallback semantics masking accidental use on non-Lantiq platforms and missing declarations when SoC headers change. Test Lantiq and non-Lantiq compile configurations plus early serial/clock initialization on affected boards.
