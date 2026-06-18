## sources/distributed-fs/ceph-client/include/linux/compiler_attributes.h

Purpose: This header provides compiler-agnostic names for common GNU/Clang attributes. It is deliberately sorted and mostly unconditional, with optional attributes guarded by `__has_attribute`.

Important APIs, types, and functions: It defines attribute wrappers such as `__alias`, `__aligned`, `__aligned_largest`, `__alloc_size__`, `__always_inline`, `__assume_aligned`, `__cleanup`, `__attribute_const__`, `__copy`, `__diagnose_as`, `__deprecated` as intentionally empty, `__designated_init`, `__compiletime_error`, `__visible`, `__printf`, `__scanf`, `__gnu_inline`, `__malloc`, `__mode`, `__no_caller_saved_registers`, `__noclone`, `fallthrough`, `__flatten`, `noinline`, `__nonstring`, `__no_profile`, `__noreturn`, `__no_stack_protector`, `__overloadable`, `__packed`, `__pass_dynamic_object_size`, `__pass_object_size`, `__pure`, `__section`, `__uninitialized`, `__always_unused`, `__maybe_unused`, `__used`, `__always_used`, `__must_check`, `__compiletime_warning`, `__disable_sanitizer_instrumentation`, `__weak`, and `__fix_address`.

Control flow: There is no runtime flow. Compile-time feature detection decides whether optional wrappers emit attributes or disappear. Later headers combine these primitives into config-sensitive attributes.

State and persistence: No state is stored. The persistent effects are ABI layout (`__packed`, `__aligned`), section placement, symbol retention, diagnostics, warning enforcement, call convention restrictions, and sanitizer instrumentation behavior.

Dependencies and integration points: It is included by `compiler_types.h` under `__KERNEL__`, then consumed throughout the kernel by subsystems declaring structures, callbacks, printf-like functions, allocation APIs, noinline paths, and linker-section objects.

Risks and test signals: Risks include applying attributes to the wrong entity, depending on attributes that are empty on one compiler, marking ERR_PTR-returning functions as aligned, or losing format/no-return diagnostics. Test signals include GCC and Clang builds, W=1/W=2 warning checks, sparse builds, ABI-sensitive struct layout tests, and negative tests for compile-time error/warning wrappers.
