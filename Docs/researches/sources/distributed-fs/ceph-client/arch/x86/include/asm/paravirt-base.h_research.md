# sources/distributed-fs/ceph-client/arch/x86/include/asm/paravirt-base.h

Purpose: defines the small base layer shared by x86 paravirtualization headers: metadata about the active paravirt environment, the callee-save wrapper type used by paravirt call sites, and common stubs/capability hooks.

Important APIs, types, and functions: `struct paravirt_callee_save` wraps non-standard calling-convention functions. `struct pv_info` records `name`, `io_delay`, and, under `CONFIG_PARAVIRT_XXL`, `extra_user_64bit_cs`. It declares `default_banner()`, global `pv_info`, `paravirt_ret0()`, optional `_paravirt_ident_64()`, `paravirt_nop`, `call_io_delay()`, and `paravirt_set_cap()`.

Control flow: this header is mostly declarations and compile-time selection. When paravirt spinlocks are disabled, `paravirt_set_cap()` becomes an inline no-op; when `CONFIG_PARAVIRT` is enabled, `call_io_delay()` reads `pv_info.io_delay`.

State and persistence: `pv_info` is runtime global metadata selected during boot by native or hypervisor setup. There is no persistence.

Dependencies and integration points: consumed by `paravirt_types.h`, `paravirt.h`, and `paravirt-spinlock.h`; implemented by native, Xen PV, and other paravirt setup code. `paravirt_nop` points to `nop_func` for alternative patching.

Risks: `struct paravirt_callee_save` is part of the low-level calling convention contract used from inline assembly. Incorrect `pv_info` setup affects boot banners, I/O delay behavior, and segment assumptions under paravirt XXL.

Test signals: native and Xen PV boot logs, paravirt alternative patching, `io_delay` behavior, spinlock capability setup, and build coverage across `CONFIG_PARAVIRT`, `CONFIG_PARAVIRT_XXL`, and `CONFIG_PARAVIRT_SPINLOCKS`.
