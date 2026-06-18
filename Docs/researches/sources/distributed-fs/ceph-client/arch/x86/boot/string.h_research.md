# sources/distributed-fs/ceph-client/arch/x86/boot/string.h

Purpose: declares boot-local string/memory helpers and controls builtin use for setup code.

Important APIs and state: declares memory functions, comparison/string functions, simple numeric conversion, and checked conversion functions. It undefines `memcpy`, `memset`, and `memcmp`, then maps them to compiler builtins by default for callers.

Control flow: none; compile-time macro behavior only.

Dependencies and integration: included throughout x86 boot code. `compressed/string.c` deliberately provides custom memory implementations for the decompressor environment.

Risks and test signals: builtin mapping must not be used in contexts where compiler-generated code is unsafe. Build and boot with GCC/Clang, KASAN compressed aliases, and calls requiring addressable memory function symbols.
