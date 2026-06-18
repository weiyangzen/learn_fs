## sources/distributed-fs/ceph-client/mm/kasan/Makefile

Purpose: defines how the KASAN runtime and KASAN KUnit tests are built while preventing instrumentation recursion.

Important build rules: disables KASAN, UBSAN, and KCOV for the runtime directory; removes ftrace from runtime objects; defines `CC_FLAGS_KASAN_RUNTIME` with `-fno-conserve-stack`, `-fno-stack-protector`, and `-DDISABLE_BRANCH_PROFILING`; applies KASAN test compiler flags separately to `kasan_test_c.o`; and passes Rust KASAN flags to `kasan_test_rust.o`.

Control flow: object selection is config-driven. `common.o` and `report.o` are always built under KASAN. Generic mode adds `init.o`, `generic.o`, generic report, shadow, and quarantine. HW tags mode adds hardware tag files and tag reports. SW tags mode adds init, software tag, shadow, tags, and reports. KUnit test composition includes the Rust helper only when `CONFIG_RUST` is enabled.

State and persistence: no runtime state; this file controls build-time composition and instrumentation boundaries.

Dependencies and integration: integrates with Kbuild, compiler feature detection for KASAN memintrinsic prefixing, C and Rust sanitizer flags, and KUnit object aggregation.

Risks and test signals: incorrect flags can instrument the sanitizer runtime itself, causing recursion, stack protector dependency loops, or tracing recursion. Test signals are successful builds across generic, SW_TAGS, HW_TAGS, VMALLOC, KUnit, Rust, and compiler configurations, plus absence of recursive KASAN reports during boot.
