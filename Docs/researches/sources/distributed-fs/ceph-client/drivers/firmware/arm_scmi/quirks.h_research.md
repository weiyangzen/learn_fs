# sources/distributed-fs/ceph-client/drivers/firmware/arm_scmi/quirks.h

Purpose: This header exposes the SCMI quirk static-key API to the rest of the SCMI stack while compiling to no-op helpers when `CONFIG_ARM_SCMI_QUIRKS` is disabled.

Important APIs/types/functions: `DECLARE_SCMI_QUIRK()` declares global static keys. `SCMI_QUIRK(_qn, _blk)` executes the provided block only when the named static branch is enabled; in disabled builds the block is compiled but never executed through an `if (0)` construct. `scmi_quirks_initialize()` and `scmi_quirks_enable()` are real functions under the config and inline no-ops otherwise. Declared quirks are `clock_rates_triplet_out_of_spec` and `perf_level_get_fc_force`.

Control flow: SCMI core calls initialization and enablement hooks unconditionally. The header hides build-time configuration by making those hooks no-op without quirk support. Workaround sites invoke `SCMI_QUIRK()` around small code blocks and rely on static branch patching for low overhead.

State and persistence: The header itself holds no state. With quirks enabled, state lives in `quirks.c` static keys and descriptors; with quirks disabled, no state is retained.

Dependencies and integration points: It includes Linux static-key and type headers. It must stay synchronized with quirk definitions in `quirks.c`: each defined quirk needs a declaration here so code snippets can reference its static key.

Risks and edge cases: The comment says "delarations", a harmless typo. More importantly, missing declarations cause compile failures at use sites, while stale declarations without a descriptor would leave an unreachable static key. The disabled-build macro still type-checks the block, which is useful but means referenced symbols must exist even when runtime support is off.

Test signals: Compile both `CONFIG_ARM_SCMI_QUIRKS=y` and disabled configurations. Runtime test signals are static branch enablement for matching platforms and absence of quirk side effects when config is off.
