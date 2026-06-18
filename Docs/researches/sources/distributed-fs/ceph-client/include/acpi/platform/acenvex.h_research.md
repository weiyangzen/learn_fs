# sources/distributed-fs/ceph-client/include/acpi/platform/acenvex.h

Purpose: Adds second-stage host/compiler extensions after ACPICA headers have been included, letting OS and compiler backends override or clean up definitions that depend on earlier declarations.

Important APIs, types, and functions: Includes `aclinuxex.h` for Linux, optional DragonFly/EFI extension headers, and `acgccex.h` or MSVC equivalents for compiler-specific cleanup.

Control flow: Compile-time dispatch chooses OS extension first and compiler extension second. There is no runtime behavior.

State and persistence: No state; it mutates the preprocessor environment.

Dependencies and integration points: Depends on the platform macros established by `acenv.h`. Integrates with ACPICA OSL declarations and compiler quirks.

Risks and test signals: Risks are missing late overrides for alternate prototypes or compiler builtins, and inclusion-order regressions. Test Linux kernel/userspace ACPICA builds and builds that exercise GCC extension cleanup.
