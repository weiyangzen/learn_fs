## sources/distributed-fs/ceph-client/tools/testing/selftests/mseal_system_mappings/sysmap_is_sealed.c

**Purpose:** Kselftest coverage for `CONFIG_MSEAL_SYSTEM_MAPPINGS=y`. It verifies selected special process mappings expose the `sl` sealed flag in `/proc/self/smaps`, while `[stack]` remains unsealed.

**Important APIs and flow:** `has_mapping()` scans the already opened smaps stream for a variant mapping name. `mapping_is_sealed()` continues scanning to the next `VmFlags:` line and checks for `sl`. A `basic` fixture owns `FILE *maps` from `/proc/self/smaps`; fixture variants cover `[vdso]`, `[vvar]`, `[vvar_vclock]`, `[sigpage]`, `[vectors]`, `[uprobes]`, and `[stack]`. `TEST_F(basic, check_sealed)` skips unavailable mappings and compares the expected seal boolean with parsed flags.

**State, dependencies, integration:** The only persistent state is the procfs smaps stream inside the fixture. It depends on `kselftest_harness.h`, procfs smaps formatting, and architecture-specific mapping names. It integrates with the mseal selftest directory as a runtime check of kernel VMA flag reporting rather than calling `mseal()` directly.

**Risks and test signals:** The parser is stream-order sensitive: after `has_mapping()` consumes through a mapping line, `mapping_is_sealed()` assumes the following `VmFlags:` belongs to that mapping. Missing architecture mappings are skipped. A pass signals system mappings are tagged sealed in smaps and ordinary stack mappings are not falsely tagged.
