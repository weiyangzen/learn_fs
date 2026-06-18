# sources/distributed-fs/ceph-client/security/ipe/Makefile

Purpose: Builds IPE objects and generates a built-in boot policy source when configured.

Important APIs/types/functions: Defines `quiet_cmd_polgen`/`cmd_polgen` to run `scripts/ipe/polgen/polgen security/ipe/boot_policy.c $(CONFIG_IPE_BOOT_POLICY)`. Builds `boot_policy.o`, digest/eval/hooks/fs/ipe/policy/policy_fs/policy_parser/audit objects when `CONFIG_SECURITY_IPE=y`, and `policy_tests.o` for KUnit.

Control flow: Kbuild regenerates `boot_policy.c` when the policy generator or configured policy changes, tracks it as a target, and removes it via `clean-files`.

State and persistence: Generated `boot_policy.c` is build output, not source-controlled runtime state.

Dependencies and integration: Depends on kernel scripts, Kbuild, config symbols, and IPE boot policy embedding consumed by `ipe.c`.

Risks and test signals: Risks are stale boot policy generation and missing dependency rebuilds. Build tests should check empty and non-empty `CONFIG_IPE_BOOT_POLICY` paths plus clean target behavior.
